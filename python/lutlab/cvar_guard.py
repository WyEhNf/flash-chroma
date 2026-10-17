"""固定完整域最坏ceil(N/100)像素的RGB距离均值，以Q24整数界保护提交。"""
import hashlib
import json
import numpy as np
from . import full_domain_guard as fg


def tail_summary(hist):
    hist = np.asarray(hist)
    if (hist.ndim != 1 or not 1 <= len(hist) <= 3*255**2+1 or hist.dtype.kind not in "iu"
            or np.any(hist < 0) or np.any(hist > 256**3)):
        raise ValueError("CVaR直方图必须是RGB8平方误差的非负整数频数")
    n = int(hist.sum(dtype=np.int64))
    if not 1 <= n <= 256**3:raise ValueError("CVaR像素数必须在RGB8完整域范围内")
    count = (n+99)//100
    remaining,low,high = count,0,0
    roots_low,roots_high = fg.root_bounds()
    selected = []
    for d in np.flatnonzero(hist)[::-1]:
        take = min(remaining,int(hist[d]))
        low += take*int(roots_low[d])
        high += take*int(roots_high[d])
        selected.append([int(d),take])
        remaining -= take
        if not remaining:break
    selected.reverse()
    return {"n":n,"tail_count":count,"precision_bits":24,"sum_lower_q24":str(low),"sum_upper_q24":str(high),
        "cutoff_squared":selected[0][0],"tail_histogram":selected}


def summary_sha256(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":")).encode()).hexdigest()


class CvarGuard:
    def __init__(self,hist,model_signature):
        self.reference = tail_summary(hist)
        self.reference_sha256 = summary_sha256(self.reference)
        self.model_signature = model_signature

    def certify(self,hist):
        current = tail_summary(hist)
        if current["n"] != self.reference["n"]:raise ValueError("CVaR参照的完整域像素数不能改变")
        same = current["tail_histogram"] == self.reference["tail_histogram"]
        accepted = int(current["sum_upper_q24"]) <= int(self.reference["sum_lower_q24"]) or same
        return {"reference_sha256":self.reference_sha256,"candidate":current,"same_tail_histogram":same,
            "accepted":accepted,"failed":[] if accepted else ["cvar.mean_bound"],
            "scope":"固定完整域最坏1%RGB均值的充分非退化证书；同一尾部直方图允许相等，否则Q24可能保守"}

    def reference_report(self,model_sha256):
        return {"model_sha256":model_sha256,"model_signature":self.model_signature,"reference":self.reference,
            "reference_sha256":self.reference_sha256,"scope":"阶段起点一次冻结；不改变历史RGB阈值、p99/max或其他四指标保护"}
