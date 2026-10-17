"""限制已验证覆盖树到新坐标各值，解释筛查未排除后的联合冲突；不新增模型。"""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path


def diagnose(folder):
    def load(name):return json.loads((folder / name).read_text(encoding="utf-8"))
    def digest(name):return hashlib.sha256((folder / name).read_bytes()).hexdigest()
    verification,trace = load("verification.json"),load("working-set.json")
    if (not verification["working_set"]["verified"] or not verification["working_set"]["screening"]["verified"] or
            verification["input_result_sha256"] != digest("results.json")):raise ValueError("条件解释必须消费已独立验证结果")
    selected = trace["selected_proposal"]
    if selected is None:return {"new_model_evaluations":0,"selected_proposal":None,"scope":"全部探针已被必要界排除，没有新增替换箱"}
    tree = load("replacement-search.json")
    if verification["working_set"]["checks"]["replacement"]["covered_assignments"] != tree["assignments"]:raise ValueError("完整覆盖回执不同")
    j = tree["nodes"].index(selected["node"])
    inventory = load("reference/photo-inventory.json")["groups"]
    expected = math.prod(len(d) for i,d in enumerate(tree["domains"]) if i != j)
    slices = []
    necessary_kinds = {"outside_max","rgb_max","rms","mean","tail"}
    for delta in tree["domains"][j]:
        categories,groups = Counter(),Counter()
        for item in tree["terminals"]:
            prefix = item["deltas"]
            if len(prefix) > j and prefix[j] != delta:continue
            count = math.prod(len(d) for i,d in enumerate(tree["domains"]) if i >= len(prefix) and i != j)
            categories[item["kind"]] += count
            if "group" in item:groups[(item["kind"],str(item["group"]))] += count
        if sum(categories.values()) != expected:raise ValueError("固定新坐标后的覆盖不完整")
        slices.append({"new_node_delta":delta,"retained_assignments":expected,"covered_assignments":sum(categories.values()),
            "necessary_rejected_assignments":sum(v for k,v in categories.items() if k in necessary_kinds),"by_kind":dict(categories),
            "all_retained_completions_infeasible":sum(v for k,v in categories.items() if k in necessary_kinds) == expected,
            "group_rejections":[{"kind":kind,"group":g if g == "full" else int(g),"image":None if g == "full" else inventory[int(g)]["image"],"assignments":n}
                for (kind,g),n in sorted(groups.items())]})
    chosen = next(v for v in slices if v["new_node_delta"] == selected["delta"])
    return {"verified_input":True,"new_model_evaluations":0,"result_sha256":digest("results.json"),"tree_sha256":digest("replacement-search.json"),
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"selected_proposal":selected,"selected_slice":chosen,"conditional_slices":slices,
        "scope":"将已有互斥完整覆盖限制到每个新坐标值，不生成候选或重新映射。必要界拒绝表示保护不可能满足；quality剪枝只表示不能优于当前目标，不能算不可行。各组归因依遍历首个见证，不是唯一原因或最小冲突集"}
