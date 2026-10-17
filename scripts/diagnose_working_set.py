"""对已选新坐标的各合法值计算补偿区间必要界，不增加模型/搜索。"""
import csv
import hashlib
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]


def diagnose(folder):
    def load(name):return json.loads((folder / name).read_text(encoding="utf-8"))
    def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
    verification = load("verification.json")
    if not verification["working_set"]["verified"] or verification["input_result_sha256"] != digest(folder / "results.json"):
        raise ValueError("支撑诊断必须使用已独立核对的冻结结果")
    plan,trace = load("plan.json"),load("working-set.json")
    Model = runpy.run_path(str(ROOT / "scripts/verify_extreme_cell.py"))["Model"]
    model = Model(folder / "reference" / plan["case"] / "repaired.slut")
    parent = next(c for c in load("reference/results.json")["cases"] if c["case"]["id"] == plan["case"])
    table_path = ROOT / parent["sources"][0]["path"]
    source = table_path.read_bytes()
    if digest(table_path) != parent["sources"][0]["table_sha256"]:raise ValueError("支撑诊断参考SHA不同")
    points = load("support.json")["points"]
    keys = [(p[0]*256+p[1])*256+p[2] for p in points]
    position = {k:i for i,k in enumerate(keys)}
    rows = {}
    with (folder / "frequencies.csv").open(encoding="utf-8",newline="") as f:
        for row in csv.DictReader(f):rows.setdefault(int(row["group"]),[]).append((position[int(row["key"])],int(row["count"])))
    inventory = load("reference/photo-inventory.json")["groups"]
    channel = plan["channel"]
    keep = trace["kept_nodes"]
    chosen = trace["proposals"][0]["helper"]
    fresh = chosen["node"]
    lower,upper = [],[]
    for n in keep:
        value = model.data[model.node_offset+3*n+channel]
        lower.append(max(-plan["max_delta"],-value));upper.append(min(plan["max_delta"],255-value))
    records,old,targets,other,counts = [],[],[],[],[]
    for p,key in zip(points,keys):
        ids,weights = model.weights(p)
        old_rgb = model.apply(p)
        truth = source[3*key:3*key+3]
        old.append(sum((a-b)**2 for a,b in zip(old_rgb,truth)))
        targets.append(truth[channel])
        other.append(sum((old_rgb[c]-truth[c])**2 for c in range(3) if c != channel))
        sums = sum(w*model.data[model.node_offset+3*n+channel] for n,w in zip(ids,weights))
        kept_weights = [sum(w for n,w in zip(ids,weights) if n == chosen_node) for chosen_node in keep]
        new_weight = sum(w for n,w in zip(ids,weights) if n == fresh)
        counts.append((any(kept_weights),bool(new_weight)))
        records.append((sums,kept_weights,new_weight))
    incidence = [{"group":g,"image":inventory[g]["image"],"retained_support_pixels":sum(n for i,n in row if counts[i][0]),
        "new_support_pixels":sum(n for i,n in row if counts[i][1]),"retained_baseline_sse":str(sum(n*old[i] for i,n in row if counts[i][0]))} for g,row in sorted(rows.items())]
    rows["full"] = list(enumerate([1]*len(points)))
    current = model.data[model.node_offset+3*fresh+channel]
    bounds = []
    for delta in range(max(-plan["max_delta"],-current),min(plan["max_delta"],255-current)+1):
        optimistic = []
        for i,(total,weights,new_weight) in enumerate(records):
            lo = (total+delta*new_weight+sum(w*d for w,d in zip(weights,lower))+32768)//65536
            hi = (total+delta*new_weight+sum(w*d for w,d in zip(weights,upper))+32768)//65536
            difference = max(0,lo-targets[i],targets[i]-hi)
            optimistic.append(other[i]+difference*difference)
        violations = []
        for g,row in rows.items():
            value = sum(n*(optimistic[i]-old[i]) for i,n in row)
            if value > 0:violations.append({"group":g,"sse_delta_lower":str(value)})
        bounds.append({"new_node_delta":delta,"rms_impossible_for_all_retained_completions":bool(violations),"violations":violations})
    selected = next(b for b in bounds if b["new_node_delta"] == chosen["delta"])
    return {"verified_input":True,"result_sha256":digest(folder / "results.json"),"trace_sha256":digest(folder / "working-set.json"),
        "source_sha256":digest(Path(__file__)),"new_model_evaluations":0,"retained_nodes":keep,"new_node":fresh,"selected_proposal":chosen,
        "incidence":incidence,"conditional_bounds":bounds,"selected_proposal_bound":selected,
        "scope":"仅对已选节点的合法值复算既有支撑的区间必要SSE界；保留节点仍自由±4，正下界证明无法补偿，非正不代表可行。未生成新模型、解码图片或新增拟合/搜索"}
