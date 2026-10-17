"""用标准库从冻结/最终直方图独立复核四指标充分条件及模型绑定。"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import runpy
import sys


def load(path):return json.loads(path.read_text(encoding="utf-8"))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def signed_mean_upper(reference,current):
    # 与生产代码分开复算：先合并有符号频数，负系数使用根号下界求整体上界。
    old,new = dict(reference),dict(current)
    if sum(old.values()) != sum(new.values()):raise ValueError("mean差值频数不守恒")
    upper = 0
    for d in old.keys() | new.keys():
        count = new.get(d,0)-old.get(d,0)
        lower = math.isqrt(d*(1 << 48))
        root_upper = lower+int(lower*lower != d*(1 << 48))
        upper += count*(root_upper if count > 0 else lower)
    return upper


def checked(reference,current,summarize):
    a,b = summarize(reference),summarize(current)
    if a["n"] != b["n"]:raise ValueError("参照和最终频数不同")
    if b["sse"] > a["sse"]:raise ValueError("RMS相对固定参照退化")
    if b["upper"] > a["lower"] and signed_mean_upper(reference,current) > 0:raise ValueError("mean非退化充分条件失败")
    tails = [sum(n for d,n in current if d > t) for t,budget in a["constraints"]]
    if any(n > budget for n,(t,budget) in zip(tails,a["constraints"])):raise ValueError("p99端点或max退化")
    return {"sse":str(b["sse"]),"mean_upper_q24":str(b["upper"]),"same_histogram":current == reference,
        "tails":tails+[0]*(3-len(tails))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--reference-run",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    if args.output.exists():raise ValueError("不覆盖已有稳定性复核")
    group_source = Path(__file__).with_name("verify_quantile_constraints.py")
    full_source = Path(__file__).with_name("verify_full_domain_guard.py")
    summarize = runpy.run_path(str(group_source))["summary"]
    full_summary = runpy.run_path(str(full_source))["checked_summary"]
    results,warm = load(args.input / "results.json"),load(args.reference_run / "results.json")
    inputs,reference_inputs,records = {},{},[]
    def read(folder,name,hashes,root):
        path = folder / name
        hashes[path.relative_to(root).as_posix()] = digest(path)
        return load(path)
    for case in results["cases"]:
        cid = case["case"]["id"]
        folder,old = args.input / cid,args.reference_run / cid
        ref = read(folder,"stability-reference.json",inputs,args.input)
        cert = read(folder,"stability-final.json",inputs,args.input)
        final = read(folder,"final-groups.json",inputs,args.input)
        domain = read(folder,"full-domain.json",inputs,args.input)
        selection = read(folder,"selection-before-photos.json",inputs,args.input)
        old_groups = read(old,"final-groups.json",reference_inputs,args.reference_run)
        old_domain = read(old,"full-domain.json",reference_inputs,args.reference_run)
        old_case = next(c for c in warm["cases"] if c["case"]["id"] == cid)
        if ref["model_sha256"] != old_case["selection"]["model_sha256"] or digest(folder / "warm-replayed.slut") != ref["model_sha256"]:
            raise ValueError("稳定性参照未绑定已验证热启动模型")
        if ref["histograms"] != [g["histogram"] for g in old_groups["groups"]] or ref["full"] != old_domain["final"]:
            raise ValueError("冻结参照直方图不同于上一阶段")
        if ref["model_signature"] != old_domain["model_signature"]:raise ValueError("冻结参照节点签名不同")
        expected_sha = case["selection"]["model_sha256"]
        if digest(folder / "repaired.slut") != expected_sha or cert["model_sha256"] != expected_sha:raise ValueError("最终模型SHA绑定不同")
        expected = []
        all_histograms = ref["histograms"]+[ref["full"]["histogram"]]
        for g,hist in enumerate(all_histograms):
            constraints = summarize(hist)["constraints"]
            if ref["thresholds"][g] != [t for t,b in constraints]+[0]*(3-len(constraints)) or ref["budgets"][g] != [b for t,b in constraints]+[-1]*(3-len(constraints)):
                raise ValueError("冻结尾部阈值或预算与直方图不同")
        if len(final["groups"]) != 101 or len(cert["photos"]) != 101:raise ValueError("照片组不完整")
        for g,(before,after) in enumerate(zip(ref["histograms"],final["groups"])):
            expected.append({"group":g,**checked(before,after["histogram"],summarize)})
        if cert["photos"] != expected:raise ValueError("终态照片证书与独立重算不同")
        full_summary(ref["full"])
        full_summary(cert["full"])
        if cert["full"] != domain["final"]:raise ValueError("终态全域直方图不同")
        check = checked(ref["full"]["histogram"],cert["full"]["histogram"],summarize)
        if cert["full_tails"] != check["tails"] or not cert["accepted"] or cert["failed"]:raise ValueError("终态全域稳定性证书不同")
        new_steps = [s for s in selection["search"]["accepted"] if not s.get("replayed")]
        for step in new_steps:
            proof = step["stability"]
            if not proof["accepted"] or proof["failed"]:raise ValueError("中间步骤没有稳定性回执")
        for name in ("warm-replayed.slut","repaired.slut"):
            inputs[f"{cid}/{name}"] = digest(folder / name)
        records.append({"case":cid,"verified_photo_histograms":101,"verified_full_histograms":1,
            "new_steps_with_recorded_receipts":len(new_steps),"reference_model_sha256":ref["model_sha256"],"final_model_sha256":expected_sha})
    inputs["results.json"] = digest(args.input / "results.json")
    reference_inputs["results.json"] = digest(args.reference_run / "results.json")
    result = {"verified":True,"cases":records,"input_sha256":inputs,"reference_input_sha256":reference_inputs,
        "verifier_sha256":digest(Path(__file__)),"group_verifier_sha256":digest(group_source),"full_verifier_sha256":digest(full_source),
        "python":sys.version,"external_dependencies_loaded":any(n in sys.modules for n in ("numpy","scipy","numba")),
        "scope":"从终态完整直方图独立核对充分条件和固定参照绑定；中间步骤只核对存在回执，不声称独立重放；不含审计反馈或未知图片保证"}
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=True))


if __name__ == "__main__":main()
