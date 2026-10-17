"""后验复算每臂已记录辅助候选中最低缺口反例，区分真实误差转移与Q24保守拒绝。"""
import argparse
import hashlib
import math
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "python"))
import numpy as np
from lutlab import io,interp,tail_repair as tr
from diagnose_quantile_compensation import affected
from diagnose_quantile_bounds import frequency,trimmed
from diagnose_three_node import replace_hist
from report_tail_grid_study import digest,write_json
from report_quantile_tail_study import load


def reductions(hist):
    low = high = sse = 0
    for d in np.flatnonzero(hist):
        count = int(hist[d])
        root = math.isqrt(int(d) << 48)
        low += count*root
        high += count*(root+int(root*root != int(d) << 48))
        sse += count*int(d)
    return low,high,sse


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--guard",type=Path,required=True)
    parser.add_argument("--aware",type=Path,required=True)
    parser.add_argument("--warm",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    if args.output.exists():raise ValueError("不覆盖已冻结反例")
    records,inputs = [],{}
    warm_full = load(args.warm / "velvia-vivid/full-domain.json")
    for arm,source in (("guard",args.guard),("aware",args.aware)):
        case = load(source / "results.json")["cases"][0]
        search = case["selection"]["search"]
        if search["new_accepted_steps"]:raise ValueError("该反例归因仅适用于零接受且全部候选同一冻结初态")
        trials = [t for r in search["compensation_rounds"] for t in r["trials"]+r.get("block_search",{}).get("trials",[])]
        chosen = min(trials,key=lambda t:(t["loss"],len(t["photo_failed"]),len(t["moves"]),str(t["moves"])))
        model_path = source / "velvia-vivid/warm-replayed.slut"
        model = io.load_sparse(model_path)
        if digest(model_path) != case["selection"]["model_sha256"]:raise ValueError("当前模型不是冻结起点")
        points = affected(model,[m["node"] for m in chosen["moves"]])
        keys = tr.encode(points)
        plan = ROOT / f"experiments/stable-tail-{arm}-v1.json" if arm == "guard" else ROOT / "experiments/stable-tail-aware-v1.json"
        inventory,partition = [load(source / n) for n in ("photo-inventory.json","photo-partition.json")]
        rows = {r["id"]:r for r in load(ROOT / "assets/photos/manifest.json")["images"]}
        weights = frequency(keys,inventory,partition,load(plan),rows)
        table_path = ROOT / case["sources"][0]["path"]
        if digest(table_path) != case["sources"][0]["table_sha256"]:raise ValueError("完整参考表不同")
        truth = io.load_full(table_path,mmap=True).reshape(-1,3)[keys]
        pred = interp.apply_tetra_q16(model,points)
        stream = args.warm / "velvia-vivid/repaired.rgb"
        if digest(stream) != warm_full["prediction_sha256"] or not np.array_equal(pred,np.memmap(stream,np.uint8,mode="r",shape=(256**3,3))[keys]):raise ValueError("冻结局部输出不同")
        old = np.sum((pred.astype(np.int32)-truth)**2,axis=1)
        candidate = tr.clone([model])[0]
        for m in chosen["moves"]:candidate.nodes.reshape(-1,3)[m["node"]] = m["value"]
        pred = interp.apply_tetra_q16(candidate,points)
        new = np.sum((pred.astype(np.int32)-truth)**2,axis=1)
        ref = load(source / "velvia-vivid/stability-reference.json")
        groups = load(args.warm / "velvia-vivid/final-groups.json")["groups"]
        loss,failed,details = 0,[],[]
        for g,base in enumerate(groups):
            hist = replace_hist(base["histogram"],old,new,weights[g])
            before = replace_hist(base["histogram"],old,old,weights[g])
            lo,hi,sse = reductions(hist)
            old_lo,old_hi,old_sse = reductions(before)
            loss += sum(trimmed(hist,c)[0] for c in base["constraints"])
            mean_bound = hi > old_lo and not np.array_equal(np.pad(hist,(0,max(0,len(before)-len(hist)))),np.pad(before,(0,max(0,len(hist)-len(before)))))
            if sse > old_sse:failed.append(f"stability.group{g}.rms")
            if mean_bound:failed.append(f"stability.group{g}.mean_bound")
            tails = []
            for j,(t,b) in enumerate(zip(ref["thresholds"][g],ref["budgets"][g])):
                if b < 0:continue
                count = int(hist[t+1:].sum())
                if count > b:failed.append(f"stability.group{g}.tail{j}")
                tails.append({"threshold_squared":t,"excess":max(0,count-b)})
            if sse > old_sse or mean_bound or any(t["excess"] for t in tails):
                details.append({"group":g,"image":inventory["groups"][g]["image"],"kind":inventory["groups"][g]["kind"],
                    "sse_delta":str(sse-old_sse),"mean_bound_failed":mean_bound,
                    "mean_increase_proved":lo > old_hi,"mean_delta_lower_q24":str(lo-old_hi),"mean_delta_upper_q24":str(hi-old_lo),"tails":tails})
        if loss != chosen["loss"] or set(failed) != {s for s in chosen["photo_failed"] if s.startswith("stability.")}:raise AssertionError("独立局部复算与搜索回执不同")
        records.append({"arm":arm,"chosen":chosen,"union_colours":len(points),"loss":loss,"violating_groups":details,
            "mean_bound_failures":sum(d["mean_bound_failed"] for d in details),
            "proved_mean_increases":sum(d["mean_bound_failed"] and d["mean_increase_proved"] for d in details),
            "rms_increases":sum(int(d["sse_delta"]) > 0 for d in details),
            "keys_sha256":hashlib.sha256(keys.astype("<u4").tobytes()).hexdigest(),"frequency_sha256":hashlib.sha256(memoryview(weights).cast("B")).hexdigest()})
        for p in (source / "results.json",source / "velvia-vivid/stability-reference.json",plan,model_path):inputs[str(p)] = digest(p)
    for p in (args.warm / "velvia-vivid/final-groups.json",args.warm / "velvia-vivid/full-domain.json"):inputs[str(p)] = digest(p)
    result = {"records":records,"inputs_sha256":inputs,"source_sha256":{n:digest(ROOT / "scripts" / n) for n in
        ("diagnose_stable_tail.py","diagnose_three_node.py","diagnose_quantile_compensation.py","diagnose_quantile_bounds.py")},
        "python":sys.version,"numpy":np.__version__,"scope":"每臂只复算已保存辅助候选中最低缺口一例，非新搜索/调参；Q24双向区间证明真实mean上升，不把充分条件失败均当成真实退化"}
    write_json(args.output,result)
    print([{k:r[k] for k in ("arm","union_colours","loss","mean_bound_failures","proved_mean_increases","rms_increases")} for r in records])


if __name__ == "__main__":main()
