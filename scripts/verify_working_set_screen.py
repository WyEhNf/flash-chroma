"""标准库独立重建固定探针、保留坐标自由的必要界及确定性筛查。"""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import runpy


def verify(folder,plan,trace,model,source,points,frequencies,photos,domain):
    def load(name):return json.loads((folder / name).read_text(encoding="utf-8"))
    def digest(name):return hashlib.sha256((folder / name).read_bytes()).hexdigest()
    run = load("run.json")
    parents = {k.replace("\\","/"):v for k,v in run["identity"]["parent_files"].items()}
    for name,h in plan["control_evidence_sha256"].items():
        if digest("control-origin-"+name) != h or parents[plan["control_run"]+"/"+name] != h:raise ValueError("复用对照没有绑定原发布字节")
    if run["reused_control"]["path"] != plan["control_run"] or run["reused_control"]["files"] != plan["control_evidence_sha256"]:raise ValueError("复用对照声明不同")
    origin,proof,origin_run,origin_plan = [load("control-origin-"+n) for n in ("results.json","verification.json","run.json","plan.json")]
    if (not proof["verified"] or proof["input_result_sha256"] != digest("control-origin-results.json") or origin["run_identity"] != origin_run["identity_sha256"] or
            origin_run["identity"]["environment"] != run["identity"]["environment"] or origin["selection"]["selected"] is not None or not origin["final"]["reused"] or
            len(origin["records"]) != 1 or origin["records"][0]["model_sha256"] != hashlib.sha256(model.data).hexdigest() or
            any(origin_plan[k] != plan[k] for k in ("model_sha256","warm_run","max_delta","channel","objective","source_probes")) or
            digest("control-search.json") != digest("control-origin-control-search.json") or load("control-search.json")["incumbent"]["name"] != "baseline"):
        raise ValueError("原对照的基线/参数/环境/原证明不同")
    for n in ("joint_interval","joint_minimax"):
        path = "python/lutlab/"+n+".py"
        if origin_run["identity"]["source_sha256"][path] != run["identity"]["source_sha256"][path]:raise ValueError("复用对照的数值求解源变化")
    channel = plan["channel"]
    keys = [(p[0]*256+p[1])*256+p[2] for p in points]
    positions = {k:i for i,k in enumerate(keys)}
    targets = [source[3*k:3*k+3] for k in keys]
    old_rgb = [model.apply(p) for p in points]
    old = [sum((a-b)**2 for a,b in zip(v,t)) for v,t in zip(old_rgb,targets)]
    other = [sum((v[c]-t[c])**2 for c in range(3) if c != channel) for v,t in zip(old_rgb,targets)]
    weights = []
    for p in points:
        row = Counter()
        for n,w in zip(*model.weights(p)):row[n] += w
        weights.append(row)
    totals = [sum(w*model.data[model.node_offset+3*n+channel] for n,w in row.items()) for row in weights]
    # 权重中的零项保留不影响区间；各支撑节点互异，由原始Q16模型独立解析。
    kept = trace["kept_nodes"]
    bounds = [(max(-plan["max_delta"],-model.data[model.node_offset+3*n+channel]),
        min(plan["max_delta"],255-model.data[model.node_offset+3*n+channel])) for n in kept]
    low = [sum(row.get(n,0)*b[0] for n,b in zip(kept,bounds)) for row in weights]
    high = [sum(row.get(n,0)*b[1] for n,b in zip(kept,bounds)) for row in weights]
    rows = {g:[(positions[k],n) for (group,k),n in frequencies.items() if group == g] for g in sorted({g for g,k in frequencies})}
    rows["full"] = list(enumerate([1]*len(points)))
    histograms = {g:photos["groups"][g]["histogram"] for g in rows if g != "full"}
    histograms["full"] = domain["final"]["histogram"]
    outside = Counter(dict(histograms["full"]));outside.subtract(old)
    outside_max = max((d for d,n in outside.items() if n),default=0)
    maximum = math.ceil(math.sqrt(histograms["full"][-1][0]))
    summary = runpy.run_path(str(Path(__file__).with_name("verify_quantile_constraints.py")))["summary"]
    endpoints = {g:summary(hist)["constraints"] for g,hist in histograms.items()}
    roots = {}
    def root(d):
        if d not in roots:
            r = math.isqrt(d << 48);roots[d] = (r,r+int(r*r != d << 48))
        return roots[d]
    old_mean = {g:sum(n*root(old[i])[1] for i,n in row) for g,row in rows.items()}
    def certificate(h):
        lower = []
        for i,row in enumerate(weights):
            fixed = totals[i]+row.get(h["node"],0)*h["delta"]
            lo,hi = (fixed+low[i]+32768)//65536,(fixed+high[i]+32768)//65536
            d = max(0,lo-targets[i][channel],targets[i][channel]-hi)
            lower.append(other[i]+d*d)
        if outside_max > maximum**2:return {"kind":"outside_max","squared":outside_max}
        for i,d in enumerate(lower):
            if d > maximum**2:return {"kind":"rgb_max","point":i,"squared_lower":d}
        for g,row in rows.items():
            d = sum(n*(lower[i]-old[i]) for i,n in row)
            if d > 0:return {"kind":"rms","group":g,"sse_delta_lower":str(d)}
        for g,row in rows.items():
            d = sum(n*root(lower[i])[0] for i,n in row)-old_mean[g]
            if d > 0:return {"kind":"mean","group":g,"sum_delta_lower_q24":str(d)}
        for g,row in rows.items():
            for t,b in endpoints[g]:
                budget = b-sum(n for d,n in histograms[g] if d > t)+sum(n for i,n in row if old[i] > t)
                count = sum(n for i,n in row if lower[i] > t)
                if count > budget:return {"kind":"tail","group":g,"threshold_squared":t,"local_budget":budget,"local_count_lower":count}
        return None
    eligible = []
    for item in trace["proposals"]:
        h = item["helper"]
        if abs(h["delta"]) > plan["max_delta"]:raise ValueError("筛查探针越过联合域")
        proof = certificate(h)
        if item["necessary_screen"] != {"not_excluded":proof is None,"certificate":proof}:raise ValueError("探针必要界与独立整数复算不同")
        if proof is None:eligible.append(h)
    selected = eligible[0] if eligible else None
    if (trace["selected_proposal"] != selected or trace["screening"]["probes"] != len(trace["proposals"]) or
            trace["screening"]["not_excluded"] != len(eligible) or trace["screening"]["max_delta"] != plan["max_delta"] or trace["screening"]["rgb_max"] != maximum):
        raise ValueError("必要筛查计数或第一个未排除提议不同")
    return {"verified":True,"probes":len(trace["proposals"]),"excluded":len(trace["proposals"])-len(eligible),"not_excluded":len(eligible),
        "selected_proposal":selected,"control_reused":True,"scope":"独立重算每个固定探针的全部区间必要条件；未排除不是可行证明，原对照树另逐项重放"}
