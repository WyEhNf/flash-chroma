"""仅用标准库复核完整RGB直方图的整数预算证书，不执行拟合或模型。"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys


def checked_summary(record):
    if record["n"] != 256**3 or record["precision_bits"] != 24:
        raise ValueError("证书必须覆盖完整256³且使用Q24根号界")
    bins = record["histogram"]
    if (not bins or any(type(d) is not int or type(n) is not int or not 0 <= d <= 3*255**2 or n <= 0 for d,n in bins)
            or [d for d,n in bins] != sorted(set(d for d,n in bins)) or sum(n for d,n in bins) != 256**3):
        raise ValueError("误差直方图计数、顺序或完整性无效")
    lower, upper, squared = 0, 0, 0
    for d,n in bins:
        root = math.isqrt(d*(1 << 48))
        if not root*root <= d*(1 << 48) < (root+1)*(root+1):
            raise ArithmeticError("整数平方根性质不成立")
        lower += n*root
        upper += n*(root+int(root*root != d*(1 << 48)))
        squared += n*d
    rank, t = divmod(99*(256**3-1),100)
    endpoints = []
    for position in (rank,rank+int(t > 0)):
        count = 0
        for d,n in bins:
            count += n
            if count > position:
                endpoints.append(d)
                break
    expected = {"sum_lower_q24":str(lower), "sum_upper_q24":str(upper), "sum_squared_error":str(squared),
                "p99_squared_endpoints":endpoints, "p99_high_weight_percent":t, "max_squared_error":bins[-1][0]}
    if any(record[key] != value for key,value in expected.items()):
        raise ValueError("保存的证书数值不等于独立整数复算")
    return expected


def verify(reference, proof):
    candidate = checked_summary(proof["candidate"])
    if proof["mean_ratio"] != [1005,1000]:
        raise ValueError("该版本仅接受预先冻结的0.5%完整域预算")
    failed = []
    if int(candidate["sum_upper_q24"])*1000 > int(reference["sum_lower_q24"])*1005:
        failed.append("mean")
    if int(candidate["sum_squared_error"]) > int(reference["sum_squared_error"]):
        failed.append("rms")
    new,old = candidate["p99_squared_endpoints"],reference["p99_squared_endpoints"]
    if not all(a <= b for a,b in zip(new,old)):
        t = reference["p99_high_weight_percent"]
        def lo(d): return math.isqrt(d*(1 << 48))
        def hi(d):
            x = lo(d)
            return x+int(x*x != d*(1 << 48))
        if (100-t)*hi(new[0])+t*hi(new[1]) > (100-t)*lo(old[0])+t*lo(old[1]):
            failed.append("p99")
    if candidate["max_squared_error"] > reference["max_squared_error"]:
        failed.append("max")
    if failed != proof["failed"] or proof["accepted"] != (not failed):
        raise ValueError("保存的接受/拒绝结论与独立整数复算不一致")
    return not failed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path)
    args = parser.parse_args()
    paths = [args.input/name for name in ("full-domain.json","negative-control.json")]
    domain,negative = [json.loads(p.read_text(encoding="utf-8")) for p in paths]
    reference = checked_summary(domain["reference"])
    if domain["final"] != domain["certificate"]["candidate"]:
        raise ValueError("最终摘要与最终证书不对应")
    proofs = [*domain["checks"],domain["certificate"],negative]
    outcomes = [verify(reference,proof) for proof in proofs]
    if not outcomes[-2] or outcomes[-1] or "mean" not in negative["failed"]:
        raise ValueError("最终候选或已知超预算负对照未达到声明的验收口径")
    result = {"verified":True,"checked_certificates":len(proofs),"accepted_certificates":sum(outcomes),
        "rejected_certificates":len(outcomes)-sum(outcomes),"n":256**3,"python":sys.version,
        "external_dependencies_loaded":any(name in sys.modules for name in ("numpy","scipy","numba")),
        "verifier_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "input_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        "scope":"仅证明保存的全域直方图与整数预算结论一致；实际输入覆盖、模型和参考绑定须另核全域输出"}
    if args.output:
        if args.output.exists():
            raise ValueError("不覆盖已有证书复核记录")
        args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    # 隔离模式会忽略UTF8环境变量；标准输出用JSON转义保证跨Windows代码页可读。
    print(json.dumps(result,ensure_ascii=True))


if __name__ == "__main__":
    main()
