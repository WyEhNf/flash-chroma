"""只重放已选节点的局部支撑，解释同样B加1为何产生相反尾部效果。"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "python"))
import numpy as np
from lutlab import interp,io,tail_repair as tr
from diagnose_quantile_compensation import affected
from diagnose_three_node import replace_hist
from verify_cvar_guard import tail_summary


def load(path):return json.loads(path.read_text(encoding="utf-8"))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,default=ROOT / "artifacts/cvar-commit-v1")
    parser.add_argument("--warm",type=Path,default=ROOT / "artifacts/primary-budget-constraints-v1")
    parser.add_argument("--risk",type=Path,default=ROOT / "report/data/cvar-commit-v1/tail-risk.json")
    parser.add_argument("--output",type=Path,default=ROOT / "report/data/cvar-commit-v1/error-directions.json")
    args = parser.parse_args()
    if args.output.exists():raise ValueError("不覆盖局部误差方向归因")
    case = load(args.input / "results.json")["cases"][0]
    cid = case["case"]["id"]
    changes = [s for s in case["selection"]["search"]["accepted"] if not s.get("replayed")][0]["moves"]
    warm_path = args.input / cid / "warm-replayed.slut"
    model = io.load_sparse(warm_path)
    table_path = ROOT / case["sources"][0]["path"]
    if digest(table_path) != case["sources"][0]["table_sha256"]:raise ValueError("局部参考LUT字节不同")
    warm_domain = load(args.warm / cid / "full-domain.json")
    reference = tail_summary(warm_domain["final"]["histogram"])
    risk = load(args.risk)
    stream_path = args.warm / cid / "repaired.rgb"
    stream = np.memmap(stream_path,np.uint8,mode="r",shape=(256**3,3))
    if digest(stream_path) != load(args.warm / "results.json")["cases"][0]["final"]["cube"]["prediction_sha256"]:
        raise ValueError("局部起点完整流不同")
    records = []
    for change in changes:
        points = affected(model,[change["node"]])
        keys = tr.encode(points)
        old_rgb = interp.apply_tetra_q16(model,points)
        if not np.array_equal(old_rgb,stream[keys]):raise ValueError("局部整数映射与已测完整起点流不同")
        truth = io.load_full(table_path,mmap=True).reshape(-1,3)[keys]
        candidate = tr.clone([model])[0]
        if candidate.nodes.reshape(-1,3)[change["node"]].tolist() != change["before"]:raise ValueError("局部节点前值不同")
        candidate.nodes.reshape(-1,3)[change["node"]] = change["after"]
        new_rgb = interp.apply_tetra_q16(candidate,points)
        if not np.array_equal(new_rgb[:,:2],old_rgb[:,:2]) or np.any(new_rgb[:,2].astype(int)-old_rgb[:,2] > 1) or np.any(new_rgb[:,2] < old_rgb[:,2]):
            raise ValueError("本归因只解释已选B加1节点")
        old = np.sum((old_rgb.astype(np.int32)-truth)**2,axis=1)
        new = np.sum((new_rgb.astype(np.int32)-truth)**2,axis=1)
        hist = replace_hist(warm_domain["final"]["histogram"],old,new,np.ones(len(points),np.int64),True)
        pairs = [[int(d),int(hist[d])] for d in np.flatnonzero(hist)]
        expected = next(r for r in risk["candidates"] if r["nodes"] == [change["node"]] and r["values"] == [change["after"]])
        if hashlib.sha256(json.dumps(pairs,separators=(",",":")).encode()).hexdigest() != expected["candidate_histogram_sha256"]:
            raise ValueError("独立局部平方误差变化与已测候选完整域频数不同")
        current = tail_summary(pairs)
        cutoff = reference["cutoff_squared"]
        if current["cutoff_squared"] != cutoff or math.isqrt(cutoff)**2 != cutoff:raise ValueError("截断值变化，本归因公式不适用")
        baseline = math.isqrt(cutoff) << 24
        def excess(d):
            if d <= cutoff:return 0,0
            root = math.isqrt(int(d) << 48)
            return root-baseline,root-baseline+int(root*root != int(d) << 48)
        bounds = [(excess(b)[0]-excess(a)[1],excess(b)[1]-excess(a)[0]) for a,b in zip(old,new)]
        low,high = [sum(b[i] for b in bounds) for i in (0,1)]
        changed = old != new
        better = (new < old) & ((old > cutoff) | (new > cutoff))
        worse = (new > old) & ((old > cutoff) | (new > cutoff))
        def examples(mask,descending):
            indices = np.flatnonzero(mask).tolist()
            indices.sort(key=lambda i:((-(bounds[i][0]+bounds[i][1]) if descending else bounds[i][0]+bounds[i][1]),tuple(points[i])))
            return [{"rgb":points[i].tolist(),"before":old_rgb[i].tolist(),"truth":truth[i].tolist(),"after":new_rgb[i].tolist(),
                "before_squared":int(old[i]),"after_squared":int(new[i])} for i in indices[:3]]
        records.append({"node":change["node"],"before":change["before"],"after":change["after"],"support_colours":len(points),
            "changed_output_colours":int(np.count_nonzero(changed)),"sse_improved_colours":int(np.count_nonzero(new < old)),"sse_worsened_colours":int(np.count_nonzero(new > old)),
            "sse_delta":str(int(np.sum(new-old,dtype=np.int64))),"tail_improved_colours":int(np.count_nonzero(better)),"tail_worsened_colours":int(np.count_nonzero(worse)),
            "tail_mean_delta_lower":low/((1 << 24)*reference["tail_count"]),"tail_mean_delta_upper":high/((1 << 24)*reference["tail_count"]),
            "tail_improvement_examples":examples(better,False),"tail_worsening_examples":examples(worse,True)})
    inputs = [args.input / "results.json",warm_path,args.warm / cid / "full-domain.json",args.warm / "results.json",args.risk,table_path,stream_path]
    output = {"records":records,"cutoff_squared":reference["cutoff_squared"],"tail_count":reference["tail_count"],
        "inputs_sha256":{str(p):digest(p) for p in inputs},"sources_sha256":{n:digest(ROOT / "scripts" / n) for n in ("explain_cvar_components.py","verify_cvar_guard.py","diagnose_three_node.py","diagnose_quantile_compensation.py")},
        "scope":"仅已选三个节点逐一局部整数重放，频数SHA与原完整候选绑定；截断49未变时CVaR变化等于超过7的距离余量变化除以K，非像素过阈值计数或SSE变化；无新搜索/拟合/完整域扫描"}
    args.output.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps([{k:r[k] for k in ("node","changed_output_colours","sse_improved_colours","sse_worsened_colours","sse_delta","tail_improved_colours","tail_worsened_colours","tail_mean_delta_lower","tail_mean_delta_upper")} for r in records],ensure_ascii=True))


if __name__ == "__main__":main()
