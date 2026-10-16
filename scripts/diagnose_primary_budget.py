"""局部独立重放唯一新接受主改，绑定原128提案截断、误差来源与固定保护。"""
import argparse
from pathlib import Path
from diagnose_quantile_bounds import process
from report_quantile_tail_study import load
from report_tail_grid_study import digest,write_json

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tail",type=Path,required=True)
    parser.add_argument("--constraints",type=Path,required=True)
    parser.add_argument("--warm",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    if args.output.exists():raise ValueError("不覆盖独立主提案归因")
    old,case = [load(p / "results.json")["cases"][0] for p in (args.tail,args.constraints)]
    warm = load(args.warm / "results.json")["cases"][0]
    cid = case["case"]["id"]
    search = case["selection"]["search"]
    records = [r for r in search["accepted"] if not r.get("replayed")]
    if len(records) != 1 or len(records[0]["moves"]) != 1 or records[0]["proposal_source"] != "global_single":
        raise ValueError("该独立归因冻结为本轮唯一全局单节点反例")
    if old["selection"]["search"]["new_accepted_steps"]:raise ValueError("对照不是原冻结状态")
    a,b = [c["selection"]["search"]["global_rounds"][0] for c in (old,case)]
    for key in ("model_signature","score_sha256","negative_score_proposals","statistics_sha256","hist_changes_sha256"):
        if a[key] != b[key]:raise ValueError("两臂不是同一主提案库及统计")
    plan_path = ROOT / "experiments/primary-budget-constraints-v1.json"
    run = load(args.constraints / "run.json")
    if digest(plan_path) != run["identity"]["plan_sha256"]:raise ValueError("独立归因计划不同")
    for n,h in run["identity"]["warm_files"].items():
        if digest(args.warm / n) != h:raise ValueError("热启动来源不同")
    inventory,partition = [load(args.constraints / n) for n in ("photo-inventory.json","photo-partition.json")]
    rows = {r["id"]:r for r in load(ROOT / "assets/photos/manifest.json")["images"]}
    args.output.mkdir()
    replay = process(case,warm,args.constraints,args.warm,inventory,partition,load(plan_path),rows,args.output)
    result = replay["global_steps"][0]
    prefix = [t for t in a["trials"] if len(t["moves"]) == 1]
    if len(prefix) != 128:raise ValueError("原主试探前缀不是冻结128项")
    move = records[0]["moves"][0]
    last = prefix[-1]
    last_move = last["moves"][0]
    candidate_key = (result["proxy_delta"],move["node"],tuple(move["after"]))
    last_key = (last["lower_bound_delta"],last_move["node"],tuple(last_move["value"]))
    if not candidate_key > last_key or any(t["moves"][0] == {"node":move["node"],"value":move["after"]} for t in prefix):
        raise ValueError("不能证明新主改位于原128项之后")
    before,after = [load(p / cid / "final-groups.json") for p in (args.warm,args.constraints)]
    changed = []
    for g,(start,end) in enumerate(zip(before["groups"],after["groups"])):
        if start["histogram"] == end["histogram"]:continue
        sse_delta = int(end["sse"])-int(start["sse"])
        mean_upper = int(end["mean_sum_upper_q24"])-int(start["mean_sum_lower_q24"])
        if sse_delta > 0 or mean_upper > 0:raise ValueError("有变化组没有通过固定参照整数非退化证明")
        changed.append({"group":g,"image":inventory["groups"][g]["image"],"kind":inventory["groups"][g]["kind"],
            "sse_delta":str(sse_delta),"mean_delta_upper_q24":str(mean_upper),"cost_before":sum(start["costs"]),"cost_after":sum(end["costs"])})
    old_full,new_full = [load(p / cid / "full-domain.json")["final"] for p in (args.warm,args.constraints)]
    output = {"case":cid,"replay":replay,"outside_original_single_prefix":True,"original_prefix_last":last,
        "accepted_constraint_rank":1,"global_negative_proposals":a["negative_score_proposals"],"changed_groups":changed,
        "full_sse_delta":str(int(new_full["sum_squared_error"])-int(old_full["sum_squared_error"])),
        "full_mean_delta_upper_q24":str(int(new_full["sum_upper_q24"])-int(old_full["sum_lower_q24"])),
        "inputs_sha256":{str(p):digest(p) for p in (args.tail / "results.json",args.constraints / "results.json",args.warm / "results.json",plan_path)},
        "sources_sha256":{name:digest(ROOT / "scripts" / name) for name in ("diagnose_primary_budget.py","diagnose_quantile_bounds.py","diagnose_quantile_compensation.py")},
        "scope":"独立NumPy局部映射/101组完整直方图重建及整数预算；证明位于原128前缀后，不声称精确原名次；无新拟合/搜索或审计反馈"}
    write_json(args.output / "analysis.json",output)
    print({"changed_groups":len(changed),"full_sse_delta":output["full_sse_delta"],"outside_prefix":True,"conditions":result["conditions"]})


if __name__ == "__main__":main()
