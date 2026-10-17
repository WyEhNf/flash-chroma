"""独立局部重放首个三节点块的全部七个非空子集，复算尾部与预算。"""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "python"))
import numpy as np
from lutlab import full_domain_guard as fg,interp,io,tail_repair as tr
from diagnose_quantile_compensation import affected
from diagnose_quantile_bounds import frequency,trimmed
from report_tail_grid_study import digest,write_json


def load(path):return json.loads(path.read_text(encoding="utf-8"))


def replace_hist(pairs,old,new,counts,full=False):
    size = max(max(d for d,n in pairs),int(old.max()),int(new.max()))+1
    hist = np.zeros(3*255**2+1 if full else size,np.int64)
    for d,n in pairs:hist[d] = n
    np.add.at(hist,old,-counts)
    np.add.at(hist,new,counts)
    if np.any(hist < 0):raise AssertionError("局部直方图频数不守恒")
    return hist


def reductions(hist):
    sse = high = 0
    for d in np.flatnonzero(hist):
        root = math.isqrt(int(d) << 48)
        high += int(hist[d])*(root+int(root*root != int(d) << 48))
        sse += int(hist[d])*int(d)
    return sse,high


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--warm",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    if args.output.exists():raise ValueError("不覆盖旧子集归因")
    result,run = [load(args.input / n) for n in ("results.json","run.json")]
    case = result["cases"][0]
    cid = case["case"]["id"]
    search = case["selection"]["search"]
    record = search["accepted"][search["replayed_steps"]]
    if len(record["moves"]) != 3:raise ValueError("本次归因要求首个新增修改就是三节点块")
    block = search["compensation_rounds"][0]["block_search"]
    expected = [t for t in block["trials"] if t["accepted"]]+block["subset_trials"]
    model = io.load_sparse(args.input / cid / "warm-replayed.slut")
    nodes = [m["node"] for m in record["moves"]]
    points = affected(model,nodes)
    keys = tr.encode(points)
    plan_path = ROOT / "experiments/velvia-three-node-v1.json"
    if digest(plan_path) != run["identity"]["plan_sha256"]:raise ValueError("计划不同")
    for n,h in run["identity"]["warm_files"].items():
        if digest(args.warm / n) != h:raise ValueError("warm来源不同")
    inventory,partition = [load(args.input / n) for n in ("photo-inventory.json","photo-partition.json")]
    rows = {r["id"]:r for r in load(ROOT / "assets/photos/manifest.json")["images"]}
    weights = frequency(keys,inventory,partition,load(plan_path),rows)
    table = ROOT / case["sources"][0]["path"]
    if digest(table) != case["sources"][0]["table_sha256"]:raise ValueError("完整参考不同")
    truth = io.load_full(table,mmap=True).reshape(-1,3)[keys]
    prediction = interp.apply_tetra_q16(model,points)
    stream = args.warm / cid / "repaired.rgb"
    if digest(stream) != load(args.input / cid / "warm-start.json")["full_prediction_sha256"] or not np.array_equal(prediction,np.memmap(stream,np.uint8,mode="r",shape=(256**3,3))[keys]):
        raise AssertionError("局部初态不同")
    old = np.sum((prediction.astype(np.int32)-truth)**2,axis=1)
    groups = load(args.warm / cid / "final-groups.json")
    full = load(args.warm / cid / "full-domain.json")
    records = []
    for size in (1,2,3):
        for subset in itertools.combinations(record["moves"],size):
            candidate = tr.clone([model])[0]
            for m in subset:candidate.nodes.reshape(-1,3)[m["node"]] = m["after"]
            mapped = interp.apply_tetra_q16(candidate,points)
            new = np.sum((mapped.astype(np.int32)-truth)**2,axis=1)
            failed,stats,loss = [],[],0
            for g,base in enumerate(groups["groups"]):
                hist = replace_hist(base["histogram"],old,new,weights[g])
                sse,high = reductions(hist)
                loss += sum(trimmed(hist,c)[0] for c in base["constraints"])
                if sse > int(base["sse_limit"]):failed.append(f"group{g}.rms")
                sparse = [[int(d),int(hist[d])] for d in np.flatnonzero(hist)]
                if high > int(base["mean_limit_lower_q24"]) and sparse not in (base["original_histogram"],base["initial_histogram"]):
                    failed.append(f"group{g}.mean")
                stats.append((sse,high))
            for k,a in enumerate(groups["aggregates"]):
                if sum(stats[g][0] for g in a["groups"]) > int(a["initial_sse"]):failed.append(f"aggregate{k}.rms")
                if sum(stats[g][1] for g in a["groups"])*1000 > int(a["initial_sum_lower_q24"])*1005:failed.append(f"aggregate{k}.mean")
            full_hist = replace_hist(full["final"]["histogram"],old,new,np.ones(len(points),np.int64),True)
            summary = fg.summary(full_hist)
            proof = fg.certify(full["reference"],summary)
            decision = "tail_loss" if loss >= record["before_loss"] else "photo_guard" if failed else "full_guard" if not proof["accepted"] else "accepted"
            chosen_nodes = sorted(m["node"] for m in subset)
            original = next(t for t in expected if sorted(m["node"] for m in t["moves"]) == chosen_nodes)
            if original["loss"] != loss or original["decision"] != decision:raise AssertionError("独立子集判定与冻结回执不同")
            aggregate = groups["aggregates"][0]
            records.append({"nodes":chosen_nodes,"loss":loss,"decision":decision,"photo_failed":failed,"full_failed":proof["failed"],
                "aggregate0_sse_delta":str(sum(stats[g][0]-int(groups["groups"][g]["sse"]) for g in aggregate["groups"])),
                "aggregate0_room":str(int(aggregate["initial_sse"])-sum(stats[g][0] for g in aggregate["groups"])),
                "full_sse_delta":str(int(summary["sum_squared_error"])-int(full["final"]["sum_squared_error"])),
                "full_room":str(int(full["reference"]["sum_squared_error"])-int(summary["sum_squared_error"]))})
    value = {"case":cid,"step":record["step"],"union_colours":len(points),"keys_sha256":hashlib.sha256(keys.astype("<u4").tobytes()).hexdigest(),
        "frequency_sha256":hashlib.sha256(memoryview(weights).cast("B")).hexdigest(),"subsets":records,"python":sys.version,"numpy":np.__version__,
        "sources_sha256":{n:digest(ROOT / "scripts" / n) for n in ("diagnose_three_node.py","diagnose_quantile_bounds.py","diagnose_quantile_compensation.py")},
        "inputs_sha256":{str(p):digest(p) for p in (args.input / "results.json",args.warm / "results.json",plan_path)},
        "scope":"局部七非空子集，独立整数根/频数/尾部复算；完整域判定由更新后的完整直方图复核，无新搜索、拟合或审计反馈"}
    write_json(args.output,value)
    print([(r["nodes"],r["loss"],r["decision"],r["aggregate0_room"],r["full_room"]) for r in records])


if __name__ == "__main__":main()
