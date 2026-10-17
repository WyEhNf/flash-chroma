"""仅用标准库，从完整平方误差频数独立复核固定最坏1%提交门禁。"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys


def tail_summary(pairs):
    if (not pairs or any(type(d) is not int or type(n) is not int or not 0 <= d <= 3*255**2 or n <= 0 for d,n in pairs)
            or [d for d,n in pairs] != sorted(set(d for d,n in pairs))):
        raise ValueError("CVaR频数必须有序、唯一、非负且属于RGB8平方误差范围")
    n = sum(count for d,count in pairs)
    if not 1 <= n <= 256**3:raise ValueError("CVaR像素数超出完整RGB8域范围")
    count = (n+99)//100
    remaining,lower,upper,selected = count,0,0,[]
    for d,frequency in reversed(pairs):
        take = min(remaining,frequency)
        scaled = d*(1 << 48)
        root = math.isqrt(scaled)
        lower += root*take
        upper += (root+int(root*root != scaled))*take
        selected.append([d,take])
        remaining -= take
        if not remaining:break
    return {"n":n,"tail_count":count,"precision_bits":24,"sum_lower_q24":str(lower),"sum_upper_q24":str(upper),
        "cutoff_squared":selected[-1][0],"tail_histogram":list(reversed(selected))}


def summary_sha256(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def verify_certificate(reference,pairs,proof):
    current = tail_summary(pairs)
    if reference["n"] != current["n"]:raise ValueError("候选与参照像素数不同")
    same = current["tail_histogram"] == reference["tail_histogram"]
    accepted = same or int(current["sum_upper_q24"]) <= int(reference["sum_lower_q24"])
    expected = {"reference_sha256":summary_sha256(reference),"candidate":current,"same_tail_histogram":same,
        "accepted":accepted,"failed":[] if accepted else ["cvar.mean_bound"]}
    if any(proof.get(key) != value for key,value in expected.items()):
        raise ValueError("CVaR提交证书与独立整数复算不同")
    return accepted


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--reference-run",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    if args.output.exists():raise ValueError("不覆盖CVaR独立复核记录")
    def load(path):return json.loads(path.read_text(encoding="utf-8"))
    def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
    results = load(args.input / "results.json")
    old_results = load(args.reference_run / "results.json")
    inputs = {"results.json":digest(args.input / "results.json")}
    old_inputs = {"results.json":digest(args.reference_run / "results.json")}
    counts = {"committed_steps":0,"final_models":0,"trial_certificates":0,"rejected_trials":0}
    for case in results["cases"]:
        cid = case["case"]["id"]
        folder,old_folder = args.input / cid,args.reference_run / cid
        source = next(c for c in old_results["cases"] if c["case"]["id"] == cid)
        old_domain = load(old_folder / "full-domain.json")
        reference_record = load(folder / "cvar-reference.json")
        reference = tail_summary(old_domain["final"]["histogram"])
        if reference["n"] != 256**3 or reference_record["reference"] != reference:
            raise ValueError("CVaR参照不是已测热启动完整域")
        if reference_record["reference_sha256"] != summary_sha256(reference):raise ValueError("CVaR参照摘要SHA不符")
        if reference_record["model_signature"] != old_domain["model_signature"]:raise ValueError("CVaR参照模型签名不同")
        if not (reference_record["model_sha256"] == source["selection"]["model_sha256"] == digest(folder / "warm-replayed.slut") == digest(old_folder / "repaired.slut")):
            raise ValueError("CVaR参照未绑定同字节热启动模型")
        final = load(folder / "cvar-final.json")
        domain = load(folder / "full-domain.json")
        if final["model_sha256"] != case["selection"]["model_sha256"] or digest(folder / "repaired.slut") != final["model_sha256"]:
            raise ValueError("CVaR终态未绑定同字节实测模型")
        if not verify_certificate(reference,domain["final"]["histogram"],final):raise ValueError("终态未通过CVaR保护")
        counts["final_models"] += 1
        search = case["selection"]["search"]
        for step in search["accepted"]:
            if step.get("replayed"):continue
            if not verify_certificate(reference,step["full_domain"]["candidate"]["histogram"],step["cvar"]):
                raise ValueError("存在越过CVaR门禁的实际提交")
            counts["committed_steps"] += 1
        # 四指标可行但CVaR失败的材料允许入池；这里只验证其拒绝单独提交的证书。
        proofs = []
        for round_ in search["global_rounds"]:
            proofs.extend(round_["trials"])
            batch = round_.get("batch_search",{})
            proofs.extend(batch.get("trials",[])+batch.get("confirmation",[]))
        for trial in proofs:
            if "cvar" not in trial:continue
            proof = trial["cvar"]
            # 候选保存的最坏K频数已足够独立复算其尾部整数和；全域绑定由阶段归因另证。
            candidate = proof["candidate"]
            tail = tail_summary(candidate["tail_histogram"])
            low = sum(n*math.isqrt(d*(1 << 48)) for d,n in candidate["tail_histogram"])
            high = sum(n*(math.isqrt(d*(1 << 48))+int(math.isqrt(d*(1 << 48))**2 != d*(1 << 48))) for d,n in candidate["tail_histogram"])
            if (candidate["n"] != reference["n"] or candidate["tail_count"] != reference["tail_count"] or tail["n"] != reference["tail_count"]
                    or candidate["sum_lower_q24"] != str(low) or candidate["sum_upper_q24"] != str(high)
                    or candidate["cutoff_squared"] != candidate["tail_histogram"][0][0] or candidate["precision_bits"] != 24):
                raise ValueError("候选尾部计数或Q24和不一致")
            same = candidate["tail_histogram"] == reference["tail_histogram"]
            eligible = same or high <= int(reference["sum_lower_q24"])
            if (proof["reference_sha256"] != summary_sha256(reference) or proof["accepted"] != eligible or proof["same_tail_histogram"] != same
                    or proof["failed"] != ([] if eligible else ["cvar.mean_bound"]) or trial["commit_eligible"] != eligible or trial["accepted"] != eligible):
                raise ValueError("候选尾部判定或提交资格不符")
            counts["trial_certificates"] += 1
            counts["rejected_trials"] += int(not eligible)
        for name in ("full-domain.json","cvar-reference.json","cvar-final.json","repaired.slut","warm-replayed.slut"):
            inputs[cid+"/"+name] = digest(folder / name)
        for name in ("full-domain.json","repaired.slut"):
            old_inputs[cid+"/"+name] = digest(old_folder / name)
    result = {"verified":True,**counts,"input_sha256":inputs,"reference_sha256":old_inputs,
        "verifier_sha256":digest(Path(__file__)),"python":sys.version,
        "external_dependencies_loaded":any(n in sys.modules for n in ("numpy","scipy","numba")),
        "scope":"标准库独立复核每个新提交及最终完整域CVaR；候选尾部摘要另核整数和；模型执行、100图和候选全域绑定由阶段证据负责"}
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=True))


if __name__ == "__main__":main()
