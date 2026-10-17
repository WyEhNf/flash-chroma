"""标准库独立核坐标提议、同中心双箱和最终选择；各箱复用独立完整覆盖验证。"""
import hashlib
import itertools
import json
from pathlib import Path
import runpy


def verify(folder,plan,model,source,points,frequencies,photos,domain,records):
    def load(name):return json.loads((folder / name).read_text(encoding="utf-8"))
    def digest(name):return hashlib.sha256((folder / name).read_bytes()).hexdigest()
    trace,warm,run = load("working-set.json"),load("warm-results.json"),load("run.json")
    parents = {k.replace("\\","/"):v for k,v in run["identity"]["parent_files"].items()}
    for name,h in plan["parent_evidence_sha256"].items():
        if parents[plan["warm_run"]+"/"+name] != h:raise ValueError("父证据未绑定发布SHA")
    if (digest("warm-results.json") != parents[plan["warm_run"]+"/results.json"] or not warm["selection"]["selected"] or warm["final"]["reused"]):
        raise ValueError("工作集没有绑定已测新终态")
    last = next(r for r in warm["records"] if r["name"] == warm["selection"]["selected"])
    if last["model_sha256"] != hashlib.sha256(model.data).hexdigest() or not last["assessment"]["accepted"]:raise ValueError("父实际工作集模型不同")
    control = load("parent-search.json")["nodes"]
    changed = {m["node"] for m in last["moves"]}
    if len(changed) != len(last["moves"]) or not changed <= set(control):raise ValueError("父实际变更集合错误")
    for move in last["moves"]:
        offset = model.node_offset+3*move["node"]
        if list(model.data[offset:offset+3]) != move["after"]:raise ValueError("父实际节点终值不同")
    keep,drop = [n for n in control if n in changed],[n for n in control if n not in changed]
    fresh = sorted(set(load("support.json")["nodes"])-set(control))
    if len(drop) != 1 or not keep or not fresh or len(fresh) > plan["max_fresh_nodes"]:raise ValueError("本阶段工作集范围不同")
    expected = {"control_nodes":control,"kept_nodes":keep,"dropped_nodes":drop,"fresh_nodes":fresh}
    if any(trace.get(k) != v for k,v in expected.items()):raise ValueError("坐标保留/替换来源不同")
    signature = hashlib.sha256(model.m.to_bytes(4,"little"))
    signature.update(model.data[model.node_offset:]);signature.update(model.data[16+12*model.m:model.node_offset])
    if trace["baseline_signature"] != signature.hexdigest():raise ValueError("坐标提议起点签名不同")
    deltas = plan["proposal_deltas"]
    if not deltas or len(set(deltas)) != len(deltas) or any(type(d) is not int or not 1 <= abs(d) <= 4 for d in deltas):raise ValueError("提议幅度域错误")
    legal = {(n,plan["channel"],d) for n,d in itertools.product(fresh,deltas) if 0 <= model.data[model.node_offset+3*n+plan["channel"]]+d <= 255}
    actual = []
    for item in trace["proposals"]:
        h,s = item["helper"],item["score"]
        key = [s["primary_loss"],len(s["fixed_failed"]),s["max_squared"],int(s["full_sse_delta"]),h["node"],h["channel"],h["delta"]]
        if key != item["rank_key"]:raise ValueError("坐标优先级没有使用冻结的历史缺口口径")
        actual.append((h["node"],h["channel"],h["delta"]))
    if len(set(actual)) != len(actual) or set(actual) != legal or trace["proposals"] != sorted(trace["proposals"],key=lambda p:tuple(p["rank_key"])):
        raise ValueError("合法坐标探针集合或确定性排名错误")
    replacement = keep+[trace["proposals"][0]["helper"]["node"]]
    if trace["replacement_nodes"] != replacement:raise ValueError("新联合箱没有采用第一提议的坐标")
    receipt = run["reused_source_audit"]
    if (receipt["path"].replace("\\","/") != plan["warm_run"]+"/source-audit.json" or
            receipt["sha256"] != parents[plan["warm_run"]+"/source-audit.json"] or digest("source-audit.json") != receipt["sha256"]):
        raise ValueError("源审计复用没有保留旧回执及SHA")
    helper = Path(__file__).with_name("verify_joint_interval.py")
    checker = runpy.run_path(str(helper))["verify"]
    checks = {}
    referenced = {"baseline"}
    for label,nodes in (("control",control),("replacement",replacement)):
        names = trace["box_records"][label]
        if len(set(names)) != len(names) or any(n in referenced or n not in records or records[n]["solver"]["box"] != label for n in names):raise ValueError("双箱回执归属/唯一性错误")
        referenced.update(names)
        subset = {n:records[n] for n in ["baseline"]+names}
        checks[label] = checker(folder,plan,model,source,points,frequencies,photos,domain,subset,search_name=label+"-search.json",expected_nodes=nodes,
            proposal_trace=trace if label == "control" else None)
    if referenced != set(records):raise ValueError("双箱模型清单遗漏或多出")
    trees = {label:load(label+"-search.json") for label in checks}
    winner = min(trees,key=lambda label:(tuple(trees[label]["incumbent"]["objective"]),label))
    comparison = {"control":trees["control"]["incumbent"]["objective"],"replacement":trees["replacement"]["incumbent"]["objective"],"winner":winner,
        "quality_improved_vs_control":tuple(trees["replacement"]["incumbent"]["objective"][:3]) < tuple(trees["control"]["incumbent"]["objective"][:3]),"before_photos":True}
    if trace["comparison"] != comparison or load("joint-search.json") != trees[winner]:raise ValueError("双箱比较及选中覆盖证书不同")
    return {"verified":True,"proposals":len(actual),"checks":checks,"comparison":comparison,"helper_verifier_sha256":hashlib.sha256(helper.read_bytes()).hexdigest(),
        "scope":"独立核全部有限坐标探针和同起点双箱完整覆盖；没有遍历所有替换工作集，不作全局最优或性能声明"}
