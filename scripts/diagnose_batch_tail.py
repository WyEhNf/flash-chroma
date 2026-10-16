"""仅用标准库从已保存完整域证书分解最坏1%均值，暴露四指标保护之外的代价。"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import runpy


def load(path):return json.loads(path.read_text(encoding="utf-8"))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def key(moves):return tuple(sorted((m["node"],tuple(m["value"])) for m in moves))


def tail(summary):
    count = (summary["n"]+99)//100
    remaining,low,high = count,0,0
    cutoff = None
    for d,n in reversed(summary["histogram"]):
        take = min(remaining,n)
        root = math.isqrt(d << 48)
        low += take*root
        high += take*(root+int(root*root != d << 48))
        remaining -= take
        cutoff = d
        if not remaining:break
    if remaining:raise ValueError("最坏1%像素数不足")
    return {"count":count,"lower_q24":low,"upper_q24":high,"cutoff_squared":cutoff}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--warm",type=Path,required=True)
    parser.add_argument("--diagnosis",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    if args.output.exists():raise ValueError("不覆盖最坏1%复算")
    result = load(args.input / "results.json")["cases"][0]
    cid = result["case"]["id"]
    domain = load(args.input / cid / "full-domain.json")
    warm = load(args.warm / cid / "full-domain.json")
    diagnosis = load(args.diagnosis / "analysis.json")
    if not diagnosis["selected_batch"]:raise ValueError("本归因需要已有选定批次")
    verifier_path = Path(__file__).with_name("verify_full_domain_guard.py")
    verifier = runpy.run_path(str(verifier_path))
    verifier["checked_summary"](warm["final"])
    ref = tail(warm["final"])
    info = result["selection"]["search"]["global_rounds"][0]
    batch = info["batch_search"]
    candidates = [t for t in info["trials"]+batch["trials"] if t["accepted"]]
    proofs = {}
    for proof in domain["checks"]:
        moves = proof.get("moves",[{"node":proof.get("node"),"value":proof.get("value")}])
        if any(m["node"] is None for m in moves):continue
        proofs.setdefault(key(moves),[]).append(proof)
    subset_by_nodes = {tuple(sorted(r["nodes"])):r for r in diagnosis["subsets"]}
    records = []
    for candidate in candidates:
        proposal_key = key(candidate["moves"])
        matches = proofs.get(proposal_key,[])
        subset = subset_by_nodes.get(tuple(n for n,v in proposal_key))
        if subset is not None:
            target_sse = int(warm["final"]["sum_squared_error"])+int(subset["full_sse_delta"])
            target_upper = int(warm["final"]["sum_lower_q24"])+int(subset["full_mean_delta_upper_q24"])
            matches = [p for p in matches if int(p["candidate"]["sum_squared_error"]) == target_sse and int(p["candidate"]["sum_upper_q24"]) == target_upper]
        if not matches:raise ValueError("找不到候选的已验证完整域证书")
        histograms = {json.dumps(p["candidate"]["histogram"]) for p in matches}
        if len(histograms) != 1:raise ValueError("候选跨状态证书有歧义，不能任意选择")
        proof = matches[0]
        verifier["verify"](domain["reference"],proof)
        current = tail(proof["candidate"])
        lower,upper = current["lower_q24"]-ref["upper_q24"],current["upper_q24"]-ref["lower_q24"]
        equal = proof["candidate"]["histogram"] == warm["final"]["histogram"]
        records.append({"nodes":[n for n,v in proposal_key],"values":[list(v) for n,v in proposal_key],"loss":candidate["loss"],
            "tail_delta_lower_q24":str(lower),"tail_delta_upper_q24":str(upper),
            "tail_mean_delta_lower":lower/((1 << 24)*current["count"]),"tail_mean_delta_upper":upper/((1 << 24)*current["count"]),
            "cutoff_squared":current["cutoff_squared"],"increase_proved":lower > 0,"nonincrease_proved":upper <= 0 or equal,
            "candidate_histogram_sha256":hashlib.sha256(json.dumps(proof["candidate"]["histogram"],separators=(",",":")).encode()).hexdigest()})
    chosen_nodes = sorted(m["node"] for m in diagnosis["moves"])
    chosen = next(r for r in records if r["nodes"] == chosen_nodes)
    eligible = [r for r in records if r["nonincrease_proved"]]
    best = min(eligible,key=lambda r:(r["loss"],len(r["nodes"]),r["nodes"])) if eligible else None
    inputs = [args.input / "results.json",args.input / cid / "full-domain.json",args.warm / cid / "full-domain.json",args.diagnosis / "analysis.json"]
    output = {"selected":chosen,"reference":ref,"candidate_count":len(records),"proved_increases":sum(r["increase_proved"] for r in records),
        "best_saved_candidate_with_nonincrease_proof":best,"candidates":records,"inputs_sha256":{str(p):digest(p) for p in inputs},
        "sources_sha256":{Path(__file__).name:digest(Path(__file__)),verifier_path.name:digest(verifier_path)},
        "external_dependencies_loaded":any(n in __import__("sys").modules for n in ("numpy","scipy","numba")),
        "scope":"仅对已试探且原四指标可行的候选，独立整数复算完整域最坏ceil(N/100)像素的距离和区间；后验比较不构成新搜索/拟合，不提升默认，CVaR不是历史主阈值"}
    args.output.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:output[k] for k in ("selected","candidate_count","proved_increases","best_saved_candidate_with_nonincrease_proof")},ensure_ascii=False))


if __name__ == "__main__":main()
