"""标准库独立复核逐图频数/分位预算、冻结保护与完整域证书，不执行模型。"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import runpy
import sys


def summary(pairs):
    if (not pairs or any(type(d) is not int or type(n) is not int or not 0 <= d <= 3*255**2 or n <= 0 for d,n in pairs)
            or [d for d,n in pairs] != sorted(set(d for d,n in pairs))):
        raise ValueError("图片直方图无效")
    n = sum(c for d,c in pairs)
    lower = upper = squared = 0
    for d,c in pairs:
        root = math.isqrt(d << 48)
        lower += c*root
        upper += c*(root+int(root*root != d << 48))
        squared += c*d
    rank,rem = divmod(99*(n-1),100)
    endpoints = []
    for r in (rank,rank+int(rem > 0)):
        count = 0
        for d,c in pairs:
            count += c
            if count > r:
                endpoints.append(d)
                break
    thresholds = {pairs[-1][0]:0}
    for r,d in zip((rank,rank+int(rem > 0)),endpoints):
        thresholds[d] = min(thresholds.get(d,n),n-r-1)
    return {"n":n,"lower":lower,"upper":upper,"sse":squared,"constraints":sorted(thresholds.items())}


def verify_groups(report,initial=None):
    records = report["groups"]
    if len(records) != 101 or [r["group"] for r in records] != list(range(101)) or report["aggregate_mean_ratio"] != [1005,1000]:
        raise ValueError("图片组或固定预算不同")
    loss = 0
    guards_ok = True
    current_summaries,initial_summaries = [],[]
    for g,record in enumerate(records):
        cur,old,start = [summary(record[k]) for k in ("histogram","original_histogram","initial_histogram")]
        expected_n = 1024*768 if g < 80 else 4096 if g < 100 else 81920
        if any(s["n"] != expected_n for s in (cur,old,start)):raise ValueError("图片像素频数不符")
        if initial is not None:
            first = initial["groups"][g]
            if record["original_histogram"] != first["original_histogram"] or record["initial_histogram"] != first["histogram"]:
                raise ValueError("原/初态图片阈值被更换")
        constraints,costs = [],[]
        for threshold,budget in old["constraints"]:
            tail = sum(c for d,c in record["histogram"] if d > threshold)
            remaining = max(0,tail-budget)
            cost = 0
            for d,c in record["histogram"]:
                if d <= threshold:continue
                take = min(remaining,c)
                cost += take*(d-threshold)
                remaining -= take
                if not remaining:break
            constraints.append({"threshold_squared":threshold,"allowed_tail_pixels":budget,"actual_tail_pixels":tail})
            costs.append(cost)
        if constraints != record["constraints"] or costs+[0]*(3-len(costs)) != record["costs"]:
            raise ValueError("计数预算或最小超额代价复算不同")
        loss += sum(costs)
        mean_limit,sse_limit = max(old["lower"],start["lower"]),max(old["sse"],start["sse"])
        expected = {"mean_sum_lower_q24":str(cur["lower"]),"mean_sum_upper_q24":str(cur["upper"]),
            "mean_limit_lower_q24":str(mean_limit),"sse":str(cur["sse"]),"sse_limit":str(sse_limit)}
        if any(record[k] != v for k,v in expected.items()):raise ValueError("保存的图片整数归约与复算不同")
        equal = record["histogram"] in (record["original_histogram"],record["initial_histogram"])
        guards_ok &= (cur["upper"] <= mean_limit or equal) and cur["sse"] <= sse_limit
        current_summaries.append(cur)
        initial_summaries.append(start)
    for field in ("histogram","original_histogram","initial_histogram"):
        merged = Counter()
        for r in records[80:100]:merged.update(dict(r[field]))
        if sorted(merged.items()) != [tuple(p) for p in records[100][field]]:
            raise ValueError("合并选择样本没有保留各图片像素频率")
    expected_groups = [list(range(80)),[100]]
    if [a["groups"] for a in report["aggregates"]] != expected_groups:raise ValueError("聚合保护范围改变")
    for indices,a in zip(expected_groups,report["aggregates"]):
        initial_lower = sum(initial_summaries[g]["lower"] for g in indices)
        initial_sse = sum(initial_summaries[g]["sse"] for g in indices)
        final_upper = sum(current_summaries[g]["upper"] for g in indices)
        final_sse = sum(current_summaries[g]["sse"] for g in indices)
        if a != {"groups":indices,"initial_sum_lower_q24":str(initial_lower),"initial_sse":str(initial_sse),
                  "final_sum_upper_q24":str(final_upper),"final_sse":str(final_sse)}:
            raise ValueError("聚合预算整数值不同")
        guards_ok &= final_upper*1000 <= initial_lower*1005 and final_sse <= initial_sse
    if report["loss"] != loss or report["feasible"] != (loss == 0) or report["guards_accepted"] != bool(guards_ok):
        raise ValueError("图片可行性或保护结论不同")
    return {"loss":loss,"feasible":loss == 0,"guards_accepted":bool(guards_ok)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--full-verifier",type=Path,default=Path(__file__).with_name("verify_full_domain_guard.py"))
    args = parser.parse_args()
    if args.output.exists():raise ValueError("不覆盖已有复核记录")
    full_verifier = runpy.run_path(str(args.full_verifier))
    results = json.loads((args.input / "results.json").read_text(encoding="utf-8"))
    records,inputs = [],{}
    for case in results["cases"]:
        cid = case["case"]["id"]
        folder = args.input / cid
        files = [folder / n for n in ("initial-groups.json","final-groups.json","full-domain.json","selection-before-photos.json")]
        initial,final,domain,selection = [json.loads(p.read_text(encoding="utf-8")) for p in files]
        a,b = verify_groups(initial),verify_groups(final,initial)
        if not b["guards_accepted"] or b["loss"] != case["final_loss"] or a["loss"] != case["initial_loss"]:
            raise ValueError("结果与图片保护不一致")
        previous = a["loss"]
        for step in selection["search"]["accepted"]:
            if step["before_loss"] != previous or not 0 <= step["after_loss"] < previous:
                raise ValueError("优化步骤没有严格减少固定整数缺口")
            previous = step["after_loss"]
        if previous != b["loss"] or selection["tail_feasible"] != b["feasible"]:
            raise ValueError("最终缺口与冻结选择记录不同")
        reference = full_verifier["checked_summary"](domain["reference"])
        if domain["final"] != domain["certificate"]["candidate"]:raise ValueError("完整域最终摘要不同")
        outcomes = [full_verifier["verify"](reference,p) for p in domain["checks"]+[domain["certificate"]]]
        if not outcomes[-1] or domain["prediction_sha256"] != case["final"]["cube"]["prediction_sha256"]:
            raise ValueError("完整域保护或最终输出SHA绑定不同")
        records.append({"case":cid,"initial":a,"final":b,"verified_group_summaries":202,
            "full_certificates":len(outcomes),"accepted_full_certificates":sum(outcomes)})
        inputs.update({p.relative_to(args.input).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    inputs["results.json"] = hashlib.sha256((args.input / "results.json").read_bytes()).hexdigest()
    result = {"verified":True,"cases":records,"input_sha256":inputs,"python":sys.version,
        "verifier_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "full_verifier_sha256":hashlib.sha256(args.full_verifier.read_bytes()).hexdigest(),
        "external_dependencies_loaded":any(n in sys.modules for n in ("numpy","scipy","numba")),
        "scope":"只复核保存直方图/计数/预算/单调性；未证明输入覆盖或未知图像泛化；verified不等于尾部可行"}
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=True))


if __name__ == "__main__":main()
