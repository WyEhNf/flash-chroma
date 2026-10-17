"""只复算冻结实验的残余冲突颜色和排序摘要，不生成新候选或拟合。"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]


def load(path):return json.loads(path.read_text(encoding="utf-8"))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    if args.output.exists():raise ValueError("不覆盖冲突归因")
    result,trace,verification = [load(args.input / name) for name in ("results.json","automatic.json","verification.json")]
    if not verification["verified"] or not verification["automatic"]["tree_complete"] or verification["input_result_sha256"] != digest(args.input / "results.json"):
        raise ValueError("归因必须基于已独立复核的冻结结果")
    Model = runpy.run_path(str(ROOT / "scripts/verify_extreme_cell.py"))["Model"]
    signed = runpy.run_path(str(ROOT / "scripts/verify_stability.py"))["signed_mean_upper"]
    cid = load(args.input / "plan.json")["case"]
    parent = next(c for c in load(args.input / "reference/results.json")["cases"] if c["case"]["id"] == cid)
    photos = load(args.input / "reference" / cid / "final-groups.json")
    inventory = load(args.input / "reference/photo-inventory.json")
    baseline = Model(args.input / "reference" / cid / "repaired.slut")
    table_path = ROOT / parent["sources"][0]["path"]
    source = table_path.read_bytes()
    if hashlib.sha256(source).hexdigest() != parent["sources"][0]["table_sha256"]:raise ValueError("完整参考SHA不同")
    records = {r["name"]:r for r in result["records"]}
    # 取最少失败且名称最小的已记录三节点反例，只解释，不作新模型选择。
    names = [r["name"] for r in result["records"] if r["solver"]["role"] == "triple"]
    closest = min(names,key=lambda n:(len(records[n]["assessment"]["failed"]),n))
    focus = records[closest]
    groups = sorted({int(v.split(".")[1][5:]) for v in focus["assessment"]["failed"] if v.startswith("fixed.group")})
    ranking_summary = []
    for prefix,ranking in [("primary",trace["first"])]+[(s["prefix"],s["proposals"]) for s in trace["second"]]:
        item = {"prefix":prefix,"proposals":len(ranking),"minimum_fixed_failures":min(len(r["score"]["fixed_failed"]) for r in ranking),"residual_groups":[]}
        for g in groups:
            def delta(r):return int(next((x["sse_delta"] for x in r["score"]["group_sse_deltas"] if x["group"] == g),"0"))
            best = min(ranking,key=lambda r:(delta(r),r["rank_key"]))
            item["residual_groups"].append({"group":g,"image":inventory["groups"][g]["image"],"minimum_sse_delta":str(delta(best)),
                "sse_nonincrease_proposals":sum(delta(r) <= 0 for r in ranking),"minimum_helper":best["helper"],"minimum_helper_fixed_failed":best["score"]["fixed_failed"]})
        ranking_summary.append(item)
    frequencies = {}
    with (args.input / "frequencies.csv").open(encoding="utf-8",newline="") as f:
        for row in csv.DictReader(f):
            if int(row["group"]) in groups:frequencies[int(row["group"]),int(row["key"])] = int(row["count"])
    conflict_rows = []
    for name in ("primary","pair_001",closest):
        candidate = Model(args.input / name / "model.slut")
        for g in groups:
            examples,delta_sse,changed,mean_changes = [],0,0,[]
            for (group,key),count in frequencies.items():
                if group != g:continue
                point = [key//65536,key//256%256,key%256]
                truth = list(source[3*key:3*key+3])
                old,new = baseline.apply(point),candidate.apply(point)
                if old == new:continue
                a,b = [sum((x-y)**2 for x,y in zip(rgb,truth)) for rgb in (old,new)]
                difference = count*(b-a)
                delta_sse += difference;changed += count
                mean_changes.append(count*(math.sqrt(b)-math.sqrt(a)))
                if difference > 0:examples.append({"rgb":point,"count":count,"truth":truth,"baseline":old,"candidate":new,
                    "squared_before":a,"squared_after":b,"weighted_sse_delta":str(difference),
                    "nodes_weights_q16":[[n,w] for n,w in zip(*baseline.weights(point)) if w]})
            before = photos["groups"][g]["histogram"]
            after = records[name]["assessment"]["groups"][g]["histogram"]
            if sum(d*n for d,n in after)-sum(d*n for d,n in before) != delta_sse:raise ValueError("颜色加权SSE不等于完整照片差值")
            n = sum(count for d,count in before)
            mean_delta = math.fsum(mean_changes)/n
            before_metrics,after_metrics = photos["groups"][g]["metrics"],records[name]["assessment"]["groups"][g]["metrics"]
            if abs(mean_delta-(after_metrics["mean"]-before_metrics["mean"])) > 1e-12:raise ValueError("颜色mean不等于完整照片差值")
            low,high = -signed(after,before),signed(before,after)
            conflict_rows.append({"candidate":name,"group":g,"image":inventory["groups"][g]["image"],"changed_pixels":changed,
                "sse_delta":str(delta_sse),"mean_delta":mean_delta,"mean_sum_delta_lower_q24":str(low),"mean_sum_delta_upper_q24":str(high),
                "mean_strictly_worse_proven":low > 0,"before":before_metrics,"after":after_metrics,
                "top_regressions":sorted(examples,key=lambda r:(-int(r["weighted_sse_delta"]),r["rgb"]))[:5]})
    output = {"verified":True,"result_sha256":digest(args.input / "results.json"),"verification_sha256":digest(args.input / "verification.json"),
        "trace_sha256":digest(args.input / "automatic.json"),"source_sha256":digest(Path(__file__)),"closest_record":closest,"residual_groups":groups,
        "ranking_summary":ranking_summary,"conflicts":conflict_rows,
        "scope":"只复算已冻结候选/频数/排名并定位最少失败三节点反例；未新增候选、搜索、PNG解码或全域执行。正整数SSE与正mean差下界证明真实退化，不是区间误拒。有限前缀树不证明全局不可行"}
    args.output.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"verified":True,"closest":closest,"groups":groups,"ranking_proposals":sum(r["proposals"] for r in ranking_summary)},ensure_ascii=True))


if __name__ == "__main__":main()
