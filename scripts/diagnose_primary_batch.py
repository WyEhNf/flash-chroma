"""独立重放选定批次的全部非空子集，核对真实缺口与尾部预算耦合。"""
import argparse
import hashlib
import itertools
from pathlib import Path
import runpy
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "python"))
import numpy as np
from lutlab import full_domain_guard as fg,interp,io,tail_repair as tr
from diagnose_quantile_compensation import affected
from diagnose_quantile_bounds import frequency,trimmed
from diagnose_three_node import replace_hist
from report_quantile_tail_study import load
from report_tail_grid_study import digest,write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--warm",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    if args.output.exists():raise ValueError("不覆盖批次独立归因")
    result,run = [load(args.input / n) for n in ("results.json","run.json")]
    case = result["cases"][0]
    cid = case["case"]["id"]
    search = case["selection"]["search"]
    records = [r for r in search["accepted"] if not r.get("replayed")]
    plan_path = ROOT / "experiments/primary-batch-joint-v1.json"
    if digest(plan_path) != run["identity"]["plan_sha256"]:raise ValueError("批次归因计划不同")
    for n,h in run["identity"]["warm_files"].items():
        if digest(args.warm / n) != h:raise ValueError("批次热启动来源不同")
    inputs = {str(p):digest(p) for p in (args.input / "results.json",args.warm / "results.json",plan_path)}
    sources = {n:digest(ROOT / "scripts" / n) for n in ("diagnose_primary_batch.py","diagnose_quantile_bounds.py","diagnose_quantile_compensation.py","diagnose_three_node.py","verify_quantile_constraints.py","verify_full_domain_guard.py")}
    args.output.mkdir()
    if not records or "primary_batch" not in records[0]:
        write_json(args.output / "analysis.json",{"selected_batch":False,"inputs_sha256":inputs,"sources_sha256":sources,
            "scope":"本次没有从冻结起点提交批次，不进行子集复算，不将普通回退收益冒称批次收益"})
        print("没有选定批次；只保留已记录候选证据")
        return
    record = records[0]
    model = io.load_sparse(args.input / cid / "warm-replayed.slut")
    points = affected(model,[m["node"] for m in record["moves"]])
    keys = tr.encode(points)
    inventory,partition = [load(args.input / n) for n in ("photo-inventory.json","photo-partition.json")]
    rows = {r["id"]:r for r in load(ROOT / "assets/photos/manifest.json")["images"]}
    weights = frequency(keys,inventory,partition,load(plan_path),rows)
    table_path = ROOT / case["sources"][0]["path"]
    if digest(table_path) != case["sources"][0]["table_sha256"]:raise ValueError("完整参考表不同")
    truth = io.load_full(table_path,mmap=True).reshape(-1,3)[keys]
    before = interp.apply_tetra_q16(model,points)
    stream = args.warm / cid / "repaired.rgb"
    warm_case = load(args.warm / "results.json")["cases"][0]
    if digest(stream) != warm_case["final"]["cube"]["prediction_sha256"] or not np.array_equal(before,np.memmap(stream,np.uint8,mode="r",shape=(256**3,3))[keys]):
        raise ValueError("局部初态与冻结完整流不同")
    old = np.sum((before.astype(np.int32)-truth)**2,axis=1)
    groups = load(args.warm / cid / "final-groups.json")
    full = load(args.warm / cid / "full-domain.json")
    summarize = runpy.run_path(str(ROOT / "scripts/verify_quantile_constraints.py"))["summary"]
    full_verify = runpy.run_path(str(ROOT / "scripts/verify_full_domain_guard.py"))["verify"]
    reference = [summarize(g["histogram"]) for g in groups["groups"]]
    full_reference = summarize(full["final"]["histogram"])
    info = search["global_rounds"][0]
    trace = info["trials"]+info["batch_search"]["trials"]
    def move_key(moves):return frozenset((m["node"],tuple(m.get("value",m.get("after")))) for m in moves)
    records_out = []
    for size in range(1,len(record["moves"])+1):
        for subset in itertools.combinations(record["moves"],size):
            candidate = tr.clone([model])[0]
            for m in subset:
                if candidate.nodes.reshape(-1,3)[m["node"]].tolist() != m["before"]:raise ValueError("局部节点前值不同")
                candidate.nodes.reshape(-1,3)[m["node"]] = m["after"]
            pred = interp.apply_tetra_q16(candidate,points)
            new = np.sum((pred.astype(np.int32)-truth)**2,axis=1)
            failed,stats,loss = [],[],0
            for g,base in enumerate(groups["groups"]):
                hist = replace_hist(base["histogram"],old,new,weights[g])
                pairs = [[int(d),int(hist[d])] for d in np.flatnonzero(hist)]
                s = summarize(pairs)
                stats.append(s)
                loss += sum(trimmed(hist,c)[0] for c in base["constraints"])
                same = pairs == base["histogram"]
                if s["sse"] > int(base["sse_limit"]):failed.append(f"group{g}.rms")
                if s["upper"] > int(base["mean_limit_lower_q24"]) and pairs not in (base["original_histogram"],base["initial_histogram"]):failed.append(f"group{g}.mean")
                if s["sse"] > reference[g]["sse"]:failed.append(f"stability.group{g}.rms")
                if s["upper"] > reference[g]["lower"] and not same:failed.append(f"stability.group{g}.mean_bound")
                for j,(t,b) in enumerate(reference[g]["constraints"]):
                    if sum(n for d,n in pairs if d > t) > b:failed.append(f"stability.group{g}.tail{j}")
            for k,a in enumerate(groups["aggregates"]):
                if sum(stats[g]["sse"] for g in a["groups"]) > int(a["initial_sse"]):failed.append(f"aggregate{k}.rms")
                if sum(stats[g]["upper"] for g in a["groups"])*1000 > int(a["initial_sum_lower_q24"])*1005:failed.append(f"aggregate{k}.mean")
            hist = replace_hist(full["final"]["histogram"],old,new,np.ones(len(points),np.int64),True)
            summary = fg.summary(hist)
            proof = fg.certify(full["reference"],summary)
            full_verify(full["reference"],proof)
            s = summarize(summary["histogram"])
            full_failed = []
            if s["sse"] > full_reference["sse"]:full_failed.append("stability.full.rms")
            if s["upper"] > full_reference["lower"] and summary["histogram"] != full["final"]["histogram"]:full_failed.append("stability.full.mean_bound")
            for j,(t,b) in enumerate(full_reference["constraints"]):
                if sum(n for d,n in summary["histogram"] if d > t) > b:full_failed.append(f"stability.full.tail{j}")
            decision = "tail_loss" if loss >= record["before_loss"] else "photo_guard" if failed else "full_guard" if not proof["accepted"] else "stability_full" if full_failed else "accepted"
            original = next(t for t in trace if move_key(t["moves"]) == move_key(subset))
            if loss != original["loss"] or decision != original["decision"] or set(failed) != set(original["photo_failed"]):
                raise AssertionError("独立子集缺口或保护与冻结试探不同")
            if size == len(record["moves"]):
                checkpoint = args.output / "selected-block.slut"
                io.save_sparse(checkpoint,candidate)
                if digest(checkpoint) != load(args.input / cid / f"checkpoint{record['step']:03d}.json")["model_sha256"]:raise AssertionError("局部选定块模型SHA不同")
            records_out.append({"nodes":[m["node"] for m in subset],"loss":loss,"decision":decision,"photo_failed":failed,
                "full_failed":proof["failed"],"stability_full_failed":full_failed,
                "sse_delta_80":str(sum(stats[g]["sse"]-reference[g]["sse"] for g in range(80))),
                "full_sse_delta":str(s["sse"]-full_reference["sse"]),"full_mean_delta_upper_q24":str(s["upper"]-full_reference["lower"])})
    output = {"selected_batch":True,"case":cid,"step":record["step"],"moves":record["moves"],"union_colours":len(points),
        "keys_sha256":hashlib.sha256(keys.astype("<u4").tobytes()).hexdigest(),"frequency_sha256":hashlib.sha256(memoryview(weights).cast("B")).hexdigest(),
        "subsets":records_out,"batch_summary":record["primary_batch"],"inputs_sha256":inputs,"sources_sha256":sources,
        "scope":"仅独立重放已选定块的全部非空子集，标准库整数根/直方图/原及新增保护复算；不重新搜索，不证明其他块最优或表达能力上限"}
    write_json(args.output / "analysis.json",output)
    print([{k:r[k] for k in ("nodes","loss","decision","sse_delta_80","full_sse_delta")} for r in records_out])


if __name__ == "__main__":main()
