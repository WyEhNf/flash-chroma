"""把已完整验收的局部阶段终态转换成同一照片/全域状态视图；不生成测量。"""
import copy
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "python"))
from lutlab import automatic_compensation as ac,full_domain_guard as fg,io
from verify_quantile_constraints import summary


def load(path):return json.loads(path.read_text(encoding="utf-8"))


def manifest_hash(source,run):
    identity = run["identity"]
    found = identity.get("image_manifest_sha256",identity.get("image_manifest"))
    if found:return found
    identity = load(source / "reference/run.json")["identity"]
    found = identity.get("image_manifest_sha256",identity.get("image_manifest"))
    if not found:raise ValueError("父研究缺少可追溯的图片清单SHA")
    return found


def snapshot(source,cid):
    result = load(source / "results.json")
    if "cases" in result:
        case = next(c for c in result["cases"] if c["case"]["id"] == cid)
        run = load(source / "run.json")
        return {"case":case,"photos":load(source / cid / "final-groups.json"),"domain":load(source / cid / "full-domain.json"),
            "inventory":load(source / "photo-inventory.json"),"partition":load(source / "photo-partition.json"),
            "model_path":source / cid / "repaired.slut","stream_path":source / cid / "repaired.rgb","run":run,"manifest_sha256":manifest_hash(source,run)}
    if result["case"]["id"] != cid or not result["selection"]["selected"] or result["final"]["reused"]:
        raise ValueError("自动阶段只接收已选中并完成完整终验的新终态")
    selected = result["selection"]["selected"]
    row = next(r for r in result["records"] if r["name"] == selected)
    if not row["assessment"]["accepted"]:raise ValueError("父阶段选中模型没有通过全部保护")
    before = next(c for c in load(source / "reference/results.json")["cases"] if c["case"]["id"] == cid)
    photos = copy.deepcopy(load(source / "reference" / cid / "final-groups.json"))
    for g,after in enumerate(row["assessment"]["groups"]):
        target = photos["groups"][g]
        hist = after["histogram"]
        s = summary(hist)
        target.update(histogram=hist,metrics=after["metrics"],sse=str(s["sse"]),mean_sum_lower_q24=str(s["lower"]),mean_sum_upper_q24=str(s["upper"]))
        for condition in target["constraints"]:condition["actual_tail_pixels"] = sum(n for d,n in hist if d > condition["threshold_squared"])
        target["costs"] = [ac.cost(hist,[c]) for c in target["constraints"]]
        target["costs"] += [0]*(3-len(target["costs"]))
        if sum(target["costs"]) != after["loss"]:raise ValueError("父终态的历史缺口不匹配")
    photos.update(loss=row["assessment"]["primary_loss"],feasible=row["assessment"]["primary_loss"] == 0,generation=photos["generation"]+1,guards_accepted=True,
        scope="从父阶段完整验收终态重建状态视图；原历史阈值/混合预算保留，不重新拟合或冒称新测量")
    for aggregate in photos["aggregates"]:
        aggregate["final_sse"] = str(sum(int(photos["groups"][g]["sse"]) for g in aggregate["groups"]))
        aggregate["final_sum_upper_q24"] = str(sum(int(photos["groups"][g]["mean_sum_upper_q24"]) for g in aggregate["groups"]))
    model_path = source / selected / "model.slut"
    model = io.load_sparse(model_path)
    domain = {"reference":load(source / "reference" / cid / "full-domain.json")["reference"],
        "final":row["assessment"]["full_domain"]["candidate"],"certificate":row["assessment"]["full_domain"],
        "model_signature":fg.signature([model]),"prediction_sha256":result["final"]["cube"]["prediction_sha256"],
        "reference_sha256":result["final"]["cube"]["reference_sha256"],"scope":"父终态的已验证全域频数；不重算或重标旧时间"}
    case = {"case":before["case"],"sources":before["sources"],"selection":{"model_sha256":row["model_sha256"],"scope":"已测父终态的状态视图"},
        "final_loss":row["assessment"]["primary_loss"],"final":result["final"]}
    run = load(source / "run.json")
    return {"case":case,"photos":photos,"domain":domain,"inventory":load(source / "reference/photo-inventory.json"),"partition":load(source / "reference/photo-partition.json"),
        "model_path":model_path,"stream_path":source / selected / "cube.rgb","run":run,"manifest_sha256":manifest_hash(source,run)}
