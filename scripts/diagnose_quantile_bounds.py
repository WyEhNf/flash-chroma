"""局部重放既有接受步骤，拆分冻结截断下界的乐观松弛，不重新搜索。"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "python"))
import numpy as np
from lutlab import full_domain_guard as fg,interp,io,tail_repair as tr
from diagnose_quantile_compensation import affected
from run_tail_repair import read_image
from report_tail_grid_study import digest,write_json


def load(path):return json.loads(path.read_text(encoding="utf-8"))


def frequency(keys,inventory,partition,plan,rows):
    result = np.zeros((101,len(keys)),np.int64)
    def accumulate(g,encoded):
        position = np.searchsorted(keys,encoded)
        found = position < len(keys)
        found[found] &= keys[position[found]] == encoded[found]
        result[g] = np.bincount(position[found],minlength=len(keys))
    for g,meta in enumerate(inventory["groups"][:80]):
        rgb = read_image(rows[meta["image"]])
        encoded = tr.encode(rgb)
        accumulate(g,encoded)
        if g >= 60:
            seed = int.from_bytes(hashlib.sha256((str(plan["pixel_seed"])+":"+meta["image"]).encode()).digest()[:8],"little")
            selected = np.random.default_rng(seed).choice(len(rgb),plan["pixels_per_image"],replace=False)
            if hashlib.sha256(selected.astype("<u4").tobytes()).hexdigest() != partition["guard"]["images"][g-60]["pixel_indices_sha256"]:
                raise ValueError("局部归因的样本索引不同")
            accumulate(g+20,encoded[selected])
    result[100] = result[80:100].sum(axis=0)
    return result


def trimmed(hist,condition):
    t,b = condition["threshold_squared"],condition["allowed_tail_pixels"]
    remaining = max(0,int(hist[t+1:].sum())-b)
    cost,cap = 0,0
    for d in np.flatnonzero(hist[t+1:])+t+1:
        if not remaining:break
        take = min(remaining,int(hist[d]))
        cost += take*(int(d)-t)
        remaining -= take
        cap = int(d)-t
    return cost,cap


def process(case,warm_case,source,warm,inventory,partition,plan,rows,out):
    cid = case["case"]["id"]
    search = case["selection"]["search"]
    records = search["accepted"][search["replayed_steps"]:]
    nodes = sorted({part["node"] for r in records for part in r["moves"]})
    model_path = source / cid / "warm-replayed.slut"
    model = io.load_sparse(model_path)
    points = affected(model,nodes)
    keys = tr.encode(points)
    weights = frequency(keys,inventory,partition,plan,rows)
    table_path = ROOT / case["sources"][0]["path"]
    if digest(table_path) != case["sources"][0]["table_sha256"]:raise ValueError("完整参考表不同")
    truth = io.load_full(table_path,mmap=True).reshape(-1,3)[keys]
    prediction = interp.apply_tetra_q16(model,points)
    stream_path = warm / cid / "repaired.rgb"
    if digest(stream_path) != warm_case["final"]["cube"]["prediction_sha256"]:raise ValueError("热启动流不同")
    if not np.array_equal(prediction,np.memmap(stream_path,np.uint8,mode="r",shape=(256**3,3))[keys]):
        raise AssertionError("局部初态与冻结流不同")
    current = load(warm / cid / "final-groups.json")
    final = load(source / cid / "final-groups.json")
    hist = np.zeros((101,3*255**2+1),np.int64)
    for g,group in enumerate(current["groups"]):
        for d,n in group["histogram"]:hist[g,d] = n
    old_squared = np.sum((prediction.astype(np.int32)-truth)**2,axis=1)
    global_records,global_index = [],0
    for record in records:
        source_name = record["proposal_source"]
        is_global = source_name.startswith("global")
        round_info = search["global_rounds"][global_index] if is_global else None
        if is_global and (source_name != "global_single" or fg.signature([model]) != round_info["model_signature"]):
            raise ValueError("本归因仅覆盖实际四个全局单通道接受，或前态签名不同")
        old_stats = [[trimmed(hist[g],condition) for condition in group["constraints"]] for g,group in enumerate(current["groups"])]
        if sum(c for group in old_stats for c,u in group) != record["before_loss"]:raise AssertionError("局部旧缺口不同")
        for part in record["moves"]:
            node = model.nodes.reshape(-1,3)[part["node"]]
            if node.tolist() != part["before"]:raise AssertionError("局部前值不同")
            node[:] = part["after"]
        new_prediction = interp.apply_tetra_q16(model,points)
        squared = np.sum((new_prediction.astype(np.int32)-truth)**2,axis=1)
        changed = old_squared != squared
        contributions = []
        total_new = total_proxy = total_gap = 0
        for g,group in enumerate(current["groups"]):
            np.add.at(hist[g],old_squared[changed],-weights[g,changed])
            np.add.at(hist[g],squared[changed],weights[g,changed])
            if np.any(hist[g] < 0):raise AssertionError("局部频数替换不守恒")
            for j,condition in enumerate(group["constraints"]):
                new_cost,_ = trimmed(hist[g],condition)
                total_new += new_cost
                if not is_global:continue
                old_cost,cap = old_stats[g][j]
                t = condition["threshold_squared"]
                change = np.minimum(np.maximum(squared[changed]-t,0),cap)-np.minimum(np.maximum(old_squared[changed]-t,0),cap)
                proxy_delta = int(weights[g,changed] @ change.astype(np.int64))
                gap = new_cost-old_cost-proxy_delta
                if gap < 0:raise AssertionError("单条件下界不成立")
                total_proxy += proxy_delta
                total_gap += gap
                if gap or new_cost != old_cost:
                    contributions.append({"group":g,"image":inventory["groups"][g]["image"],"kind":inventory["groups"][g]["kind"],
                        **{k:condition[k] for k in ("threshold_squared","allowed_tail_pixels")},"old_cost":old_cost,"new_cost":new_cost,
                        "proxy_delta":proxy_delta,"gap":gap,"category":"new_constraint_activation" if old_cost == 0 else "active_trim_shift"})
        if total_new != record["after_loss"]:raise AssertionError("局部新缺口不同")
        checkpoint = out / f"{cid}-step{record['step']:03d}.slut"
        io.save_sparse(checkpoint,model)
        if digest(checkpoint) != load(source / cid / f"checkpoint{record['step']:03d}.json")["model_sha256"]:
            raise AssertionError("局部重放模型与冻结检查点不同")
        if is_global:
            trial = next(t for t in round_info["trials"] if t["accepted"])
            if total_proxy != trial["lower_bound_delta"] or total_new != trial["loss"]:raise AssertionError("全局下界与冻结试探不同")
            global_records.append({"step":record["step"],"moves":record["moves"],"before_loss":record["before_loss"],"after_loss":total_new,
                "proxy_delta":total_proxy,"actual_delta":total_new-record["before_loss"],"gap":total_gap,
                "gap_by_category":{k:sum(r["gap"] for r in contributions if r["category"] == k) for k in ("new_constraint_activation","active_trim_shift")},
                "conditions":contributions})
            global_index += 1
        old_squared = squared
    for g,group in enumerate(final["groups"]):
        if [[int(d),int(hist[g,d])] for d in np.flatnonzero(hist[g])] != group["histogram"]:
            raise AssertionError("局部所有步骤重放与最终完整图片直方图不同")
    return {"case":cid,"replayed_new_steps":len(records),"affected_union_colours":len(keys),
        "keys_sha256":hashlib.sha256(keys.astype("<u4").tobytes()).hexdigest(),"frequency_sha256":hashlib.sha256(memoryview(weights).cast("B")).hexdigest(),
        "initial_model_sha256":digest(model_path),"reference_sha256":digest(table_path),"warm_stream_sha256":digest(stream_path),
        "global_steps":global_records,"final_101_histograms_match":True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--warm",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    if args.output.exists():raise ValueError("不覆盖旧归因")
    run,result = [load(args.input / n) for n in ("run.json","results.json")]
    warm = load(args.warm / "results.json")
    plan_path = ROOT / "experiments/quantile-tail-v3.json"
    if digest(plan_path) != run["identity"]["plan_sha256"]:raise ValueError("计划不同")
    plan = load(plan_path)
    for n,h in run["identity"]["warm_files"].items():
        if digest(args.warm / n) != h:raise ValueError("热启动输入不同")
    inventory,partition = [load(args.input / n) for n in ("photo-inventory.json","photo-partition.json")]
    rows = {r["id"]:r for r in load(ROOT / "assets/photos/manifest.json")["images"]}
    args.output.mkdir(parents=True)
    records = [process(c,next(w for w in warm["cases"] if w["case"]["id"] == c["case"]["id"]),args.input,args.warm,inventory,partition,plan,rows,args.output) for c in result["cases"]]
    write_json(args.output / "results.json",{"cases":records,"python":sys.version,"numpy":np.__version__,
        "sources_sha256":{n:digest(ROOT / "scripts" / n) for n in ("diagnose_quantile_bounds.py","diagnose_quantile_compensation.py","run_tail_repair.py")},
        "input_sha256":{str(p):digest(p) for p in (args.input / "results.json",args.warm / "results.json",plan_path)},
        "scope":"只局部重放16个既有接受步骤，四个全局单节点的下界松弛分解；80完整图及固定选择样本，未使用20审计反馈，无新搜索/拟合/性能计时"})
    for c in records:print(c["case"],[(s["step"],s["proxy_delta"],s["actual_delta"],s["gap_by_category"]) for s in c["global_steps"]])


if __name__ == "__main__":main()
