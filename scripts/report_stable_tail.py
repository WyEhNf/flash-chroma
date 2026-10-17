"""归档固定参照两臂实验、完整误差分布、拒绝原因及源码/模型绑定。"""
import argparse
from collections import Counter
import hashlib
import itertools
import math
from pathlib import Path
import shutil
import zipfile
from report_quantile_tail_study import check_epoch,model_check,constraints,load
from report_tail_grid_study import digest,write_csv,write_json,compare

ROOT = Path(__file__).resolve().parents[1]


def batch_audit(global_info,m):
    batch = global_info["batch_search"]
    singles = [t for t in global_info["trials"] if len(t["moves"]) == 1 and t.get("seed_eligible",t["accepted"])]
    expected = [{"node":t["moves"][0]["node"],"value":t["moves"][0]["value"],"loss":t["loss"],"lower_bound_delta":t["lower_bound_delta"],
        **({"commit_eligible":t["commit_eligible"]} if "commit_eligible" in t else {})} for t in singles]
    if expected != batch["feasible_singles"] or len(expected) > batch["feasible_limit"]:raise ValueError("批次可行单改清单与真实回执不同")
    before = global_info["anchor_loss"]
    if any(t["before_loss"] != before for t in global_info["trials"]+batch["trials"]+batch["confirmation"]):
        raise ValueError("批次试探没有保持同一冻结状态")
    def key(moves):return tuple(sorted((part["node"],tuple(part["value"])) for part in moves))
    offers = [(t["loss"],1,key(t["moves"])) for t in singles if t["accepted"]]
    blocks,overlap = [],0
    for size in range(2,batch["max_order"]+1):
        for subset in itertools.combinations(singles,size):
            moves = tuple(sorted(part for t in subset for part in key(t["moves"])))
            coords = [(node//(m*m),(node//m)%m,node%m) for node,value in moves]
            if not all(any(abs(x-y) > 1 for x,y in zip(a,b)) for a,b in itertools.combinations(coords,2)):
                overlap += 1
                continue
            blocks.append((sum(t["loss"]-before for t in subset),size,moves))
    blocks.sort()
    if len(blocks) != batch["generated_blocks"] or overlap != batch["overlapping_blocks_skipped"] or len(blocks) != len(batch["trials"]):
        raise ValueError("批次组合遗漏、重复或不相交过滤不同")
    for expected,t in zip(blocks,batch["trials"]):
        if (t["sum_single_loss_delta"],len(t["moves"]),key(t["moves"])) != expected or t["lower_bound_delta"] is not None:
            raise ValueError("批次排序或下界标签不同")
        if t["accepted"]:offers.append((t["loss"],len(t["moves"]),key(t["moves"])))
    if offers:
        chosen = min(offers)
        if len(batch["confirmation"]) != 1:raise ValueError("批次未重新确认")
        t = batch["confirmation"][0]
        if not t["accepted"] or (t["loss"],len(t["moves"]),key(t["moves"])) != chosen:raise ValueError("批次没有选择真实损失最优可行项")
        if (batch["selected_loss"],batch["selected_node_count"],batch["selected_nodes"]) != (chosen[0],chosen[1],[node for node,value in chosen[2]]):
            raise ValueError("批次提交摘要不同")
    elif batch["confirmation"] or batch["selected_node_count"]:raise ValueError("空批次却有选择")
    return {**{k:v for k,v in batch.items() if k not in ("trials","confirmation")},
        "observed_block_decisions":dict(Counter(t["decision"] for t in batch["trials"])),"selection_audited":True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--guard",type=Path,required=True)
    parser.add_argument("--aware",type=Path,required=True)
    parser.add_argument("--warm",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--study",choices=("stable","primary","batch","cvar"),default="stable")
    parser.add_argument("--diagnosis",type=Path)
    parser.add_argument("--tail-risk",type=Path)
    args = parser.parse_args()
    if args.output.exists():raise ValueError("不覆盖旧归档")
    if args.study in ("primary","batch","cvar") and args.diagnosis is None:raise ValueError("主提案归档必须给出冻结独立归因目录")
    if args.study in ("batch","cvar") and args.tail_risk is None:raise ValueError("批次归档必须给出最坏1%独立复算")
    names = {"stable":("guard","aware"),"primary":("tail","constraints"),"batch":("first","joint"),"cvar":("unprotected","guarded")}[args.study]
    sources = dict(zip(names,(args.guard,args.aware)))
    prefix = {"stable":"stable-tail","primary":"primary-budget","batch":"primary-batch","cvar":"cvar-commit"}[args.study]
    plans = {arm:ROOT / f"experiments/{prefix}-{arm}-v1.json" for arm in sources} if args.study != "cvar" else {
        "unprotected":ROOT / "experiments/primary-batch-joint-v1.json","guarded":ROOT / "experiments/cvar-commit-v1.json"}
    checked = {arm:check_epoch(path,plans[arm]) for arm,path in sources.items()}
    if checked[names[0]][0]["identity"]["environment"] != checked[names[1]][0]["identity"]["environment"]:raise ValueError("两臂环境不同")
    a,b = [load(plans[arm]) for arm in sources]
    for field in ("parent","warm_start","cases","threads","pixels_per_image","pixel_seed","steps","focus_count","trial_limit","pair_nodes","compensation","full_domain_guard","memory_array_budget_bytes"):
        if a[field] != b[field]:raise ValueError("目标排序之外的实验配置不同")
    if args.study in ("primary","batch","cvar"):
        varying = "ordering" if args.study == "primary" else "batch"
        if a["stability"] != b["stability"] or {k:v for k,v in a["global_search"].items() if k != varying} != {k:v for k,v in b["global_search"].items() if k != varying}:
            raise ValueError("主提案排序之外的保护或全局配置不同")
        first = [checked[arm][1]["cases"][0]["selection"]["search"]["global_rounds"][0] for arm in names]
        for key in ("anchor_loss","negative_score_proposals","model_signature","score_sha256","statistics_sha256","hist_changes_sha256","raw_top_proposals"):
            if first[0][key] != first[1][key]:raise ValueError("两臂首轮主提案库或统计不同")
    warm = load(args.warm / "results.json")
    inventory,partition = [load(args.guard / n) for n in ("photo-inventory.json","photo-partition.json")]
    if load(args.aware / "photo-inventory.json") != inventory:raise ValueError("两臂颜色倒排输入不同")
    if args.study == "cvar":
        from run_quantile_tail_study import check_cohort
        old_case,new_case = [checked[arm][1]["cases"][0] for arm in names]
        cohort = check_cohort(new_case["selection"]["search"],old_case)
        if cohort != load(args.aware / new_case["case"]["id"] / "cohort-replay.json"):raise ValueError("CVaR固定队列复核不同")
        certificate = load(args.aware / "cvar-verification.json")
        if not certificate["verified"] or certificate["external_dependencies_loaded"]:raise ValueError("CVaR独立复核失败")
        for name,h in certificate["input_sha256"].items():
            if digest(args.aware / name) != h:raise ValueError("CVaR复核输入变化")
        for name,h in certificate["reference_sha256"].items():
            if digest(args.warm / name) != h:raise ValueError("CVaR复核参照变化")
        if certificate["verifier_sha256"] != digest(ROOT / "scripts/verify_cvar_guard.py"):raise ValueError("CVaR复核源码变化")
    out = args.output
    out.mkdir(parents=True)
    diagnostic = None
    risk = None
    if args.tail_risk is not None:
        risk = load(args.tail_risk)
        if risk["external_dependencies_loaded"]:raise ValueError("最坏1%复算不应载入外部数值依赖")
        for name,h in risk["inputs_sha256"].items():
            if digest(Path(name)) != h:raise ValueError("最坏1%复算输入变化")
        for name,h in risk["sources_sha256"].items():
            if digest(ROOT / "scripts" / name) != h:raise ValueError("最坏1%复算源码变化")
        shutil.copyfile(args.tail_risk,out / "tail-risk.json")
        shutil.copyfile(args.tail_risk.with_suffix(".log"),out / "tail-risk.log")
    if args.study == "stable":
        counterexamples = ROOT / "artifacts/stable-tail-counterexamples-v1.json"
        diagnostic = load(counterexamples)
        for name,h in diagnostic["inputs_sha256"].items():
            if digest(Path(name)) != h:raise ValueError("独立反例复算输入变化")
        for name,h in diagnostic["source_sha256"].items():
            if digest(ROOT / "scripts" / name) != h:raise ValueError("独立反例复算源码变化")
        shutil.copyfile(counterexamples,out / "counterexamples.json")
        shutil.copyfile(counterexamples.with_suffix(".log"),out / "counterexamples.log")
    else:
        diagnostic = load(args.diagnosis / "analysis.json")
        for name,h in diagnostic["inputs_sha256"].items():
            if digest(Path(name)) != h:raise ValueError("独立主提案归因输入变化")
        for name,h in diagnostic["sources_sha256"].items():
            if digest(ROOT / "scripts" / name) != h:raise ValueError("独立主提案归因源码变化")
        destination = out / "independent-diagnosis"
        destination.mkdir()
        for path in args.diagnosis.glob("*"):
            if path.is_file():shutil.copyfile(path,destination / path.name)
        shutil.copyfile(args.diagnosis.with_suffix(".log"),out / "diagnosis.log")
    for name in ("photo-inventory.json","photo-partition.json"):shutil.copyfile(args.guard / name,out / name)
    contract_log = {"stable":"stable-tail-contracts-v1.log","primary":"primary-budget-contracts-v1.log","batch":"primary-batch-contracts-v1.log","cvar":"cvar-commit-contracts-v1.log"}[args.study]
    shutil.copyfile(ROOT / "artifacts" / contract_log,out / "contract-tests.log")
    if args.study == "cvar":
        shutil.copyfile(ROOT / "report/data/primary-batch-v1/contract-tests.log",out / "reused-control-contract-tests.log")
    summary,photo_rows,regressions,diagnosis,provenance,parity = [],[],[],[],[],[]
    split_rows = []
    splits = {"training":[r["id"] for r in partition["training"]["images"]],
        "selection":[r["id"] for r in partition["guard"]["images"]],"audit":partition["audit_ids"]}
    primary_rows = []
    for arm,(run,result,expected) in checked.items():
        source = sources[arm]
        verify = load(source / "stability-verification.json")
        if not verify["verified"] or verify["external_dependencies_loaded"]:raise ValueError("稳定性独立复核失败")
        for name,h in verify["input_sha256"].items():
            if digest(source / name) != h:raise ValueError("稳定性复核输入变化")
        for name,h in verify["reference_input_sha256"].items():
            if digest(args.warm / name) != h:raise ValueError("稳定性参照变化")
        if verify["verifier_sha256"] != digest(ROOT / "scripts/verify_stability.py"):raise ValueError("稳定性复核源码变化")
        for name,h in run["identity"]["warm_files"].items():
            if digest(args.warm / name) != h:raise ValueError("热启动来源变化")
        folder = out / arm
        folder.mkdir()
        for name in ("verification.json","stability-verification.json"):shutil.copyfile(source / name,folder / name)
        shutil.copyfile(source / "run.json",folder / "environment.json")
        shutil.copyfile(source.with_suffix(".log"),folder / "experiment.log")
        shutil.copyfile(plans[arm],folder / "plan.json")
        members = ["run.json","results.json","verification.json","stability-verification.json","photo-inventory.json","photo-partition.json","measured-source.zip"]
        if args.study == "cvar" and arm == "guarded":
            members.append("cvar-verification.json")
            shutil.copyfile(source / "cvar-verification.json",folder / "cvar-verification.json")
        for case in result["cases"]:
            cid = case["case"]["id"]
            old = next(c for c in warm["cases"] if c["case"]["id"] == cid)
            model_check(source,case)
            if case["warm_loss"] != old["final_loss"]:raise ValueError("起始缺口不同")
            final = load(source / cid / "final-groups.json")
            full = load(source / cid / "full-domain.json")
            search = case["selection"]["search"]
            trials = []
            rounds = []
            for round_info in search["compensation_rounds"]:
                for label,entries in (("pair",round_info["trials"]),("triple",round_info.get("block_search",{}).get("trials",[]))):
                    trials.extend({"family":label,**t} for t in entries)
                rounds.append({k:v for k,v in round_info.items() if k not in ("trials","block_search")})
            globals_summary = []
            for round_index,global_info in enumerate(search["global_rounds"]):
                entries = global_info["trials"]
                item = {**{k:v for k,v in global_info.items() if k not in ("trials","batch_search")},
                    "trial_count":len(entries),"observed_decisions":dict(Counter(t["decision"] for t in entries))}
                extra = []
                if "batch_search" in global_info:
                    from lutlab import io
                    item["batch_search"] = batch_audit(global_info,io.load_sparse(source / cid / "warm-replayed.slut").m)
                    extra = [("batch",t) for t in global_info["batch_search"]["trials"]]+[("confirmation",t) for t in global_info["batch_search"]["confirmation"]]
                globals_summary.append(item)
                for rank,(family,t) in enumerate([("primary",t) for t in entries]+extra):
                    primary_rows.append({"arm":arm,"round":round_index,"trial":rank+1,"family":family,"node_count":len(t["moves"]),
                        "nodes":" ".join(str(m["node"]) for m in t["moves"]),"loss":t["loss"],"lower_bound_delta":t["lower_bound_delta"],
                        "decision":t["decision"],"stability_rms_failed_count":sum(k.startswith("stability.") and k.endswith(".rms") for k in t["photo_failed"]),
                        "stability_mean_failed_count":sum(k.startswith("stability.") and k.endswith(".mean_bound") for k in t["photo_failed"]),
                        "stability_tail_failed_count":sum(k.startswith("stability.") and ".tail" in k for k in t["photo_failed"])})
            rejection = Counter(key for t in trials for key in t["photo_failed"]+t["full_failed"]+t.get("stability_full_failed",[]))
            breakdown = {}
            for family in ("pair","triple"):
                entries = [t for t in trials if t["family"] == family]
                breakdown[family] = {"trials":len(entries),"decisions":dict(Counter(t["decision"] for t in entries)),
                    "with_stability_rms_failure":sum(any(k.startswith("stability.") and k.endswith(".rms") for k in t["photo_failed"]) for t in entries),
                    "with_stability_mean_failure":sum(any(k.startswith("stability.") and k.endswith(".mean_bound") for k in t["photo_failed"]) for t in entries),
                    "with_stability_tail_failure":sum(any(k.startswith("stability.") and ".tail" in k for k in t["photo_failed"]) for t in entries),
                    "with_stability_but_no_old_photo_failure":sum(any(k.startswith("stability.") for k in t["photo_failed"]) and not any(not k.startswith("stability.") for k in t["photo_failed"]) for t in entries)}
            diagnosis.append({"arm":arm,"case":cid,"warm_loss":case["warm_loss"],"final_loss":case["final_loss"],
                "constraints":constraints(final,inventory),"new_steps":[s for s in search["accepted"] if not s.get("replayed")],
                "search_counts":{k:v for k,v in search.items() if k not in ("accepted","compensation_rounds","global_rounds")},
                "rounds":rounds,"global_rounds":globals_summary,"helper_decisions":dict(Counter(t["decision"] for t in trials)),"helper_breakdown":breakdown,
                "helper_failed_conditions":dict(rejection.most_common()),"host_memory":full["host_memory"],
                "persistent_array_bytes":full["combined_cache_array_bytes"]})
            profiles = [("historical",case["historical"],True),("warm",old["final"],True)] if arm == names[0] else []
            reused_final = case["final"]["reused"] or (args.study == "cvar" and arm == "unprotected")
            profiles += [(arm,case["final"],reused_final)]
            for name,value,reused in profiles:
                summary.append({"case":cid,"profile":name,"reused_metrics":reused,
                    **{f"cube_{k}":value["cube"][k] for k in ("mean","rms","p99","max","cvar_1pct","fraction_ge_1","fraction_ge_2","fraction_ge_3","fraction_ge_5")},
                    **{f"photos_{k}":value["photos"][k] for k in ("mean","rms","worst_image_p99","max")}})
                photo_rows.extend({"profile":name,"reused_metrics":reused,**r} for r in value["photos"]["per_image"])
                for split,ids in splits.items():
                    images = [r for r in value["photos"]["per_image"] if r["image"] in ids]
                    if len(images) != len(ids):raise ValueError("逐图分组数据缺失")
                    split_rows.append({"profile":name,"split":split,"n_images":len(images),"reused_metrics":reused,
                        "mean":math.fsum(r["mean"] for r in images)/len(images),
                        "rms":math.sqrt(math.fsum(r["rms"]**2 for r in images)/len(images)),
                        "worst_image_p99":max(r["p99"] for r in images),"max":max(r["max"] for r in images)})
                regressions.append({"profile":name,"vs_warm":compare(old["final"]["photos"],value["photos"]),
                    "vs_historical":compare(case["historical"]["photos"],value["photos"])})
            parity.extend({"arm":arm,"reused":reused_final,**p} for p in case["final"]["native"])
            members.extend(p.relative_to(source).as_posix() for p in sorted((source / cid).glob("*")) if p.suffix in (".json",".slut") and p.name != "selected-stage1.slut")
        index = {}
        with zipfile.ZipFile(folder / "evidence.zip","w",zipfile.ZIP_DEFLATED) as z:
            for name in sorted(set(members)):
                z.write(source / name,name)
                index[name] = digest(source / name)
            z.write(plans[arm],"plan.json")
            index["plan.json"] = digest(plans[arm])
            with zipfile.ZipFile(ROOT / "report/data/fractional-fit-v1/models-and-selection.zip") as parent:
                name = "velvia-vivid/historical-grid.npy"
                data = parent.read(name)
                z.writestr(name,data)
                index[name] = hashlib.sha256(data).hexdigest()
        with zipfile.ZipFile(folder / "evidence.zip") as z:
            if set(index) != set(z.namelist()) or any(hashlib.sha256(z.read(n)).hexdigest() != h for n,h in index.items()):raise ValueError("归档成员或SHA不一致")
        write_json(folder / "archive-index.json",index)
        provenance.append({"arm":arm,"git_commit":run["git_commit"],"source_sha256":expected,
            "current_source_same":{name:(ROOT / name).exists() and digest(ROOT / name) == h for name,h in expected.items()}})
    with zipfile.ZipFile(out / "verification-sources.zip","w",zipfile.ZIP_DEFLATED) as z:
        for name in ("verify_stability.py","verify_quantile_constraints.py","verify_full_domain_guard.py")+(("verify_cvar_guard.py",) if args.study == "cvar" else ()):z.write(ROOT / "scripts" / name,name)
    if diagnostic is not None:
        with zipfile.ZipFile(out / "diagnostic-sources.zip","w",zipfile.ZIP_DEFLATED) as z:
            diagnostic_sources = {**diagnostic["source_sha256" if args.study == "stable" else "sources_sha256"],**(risk["sources_sha256"] if risk else {})}
            for name in diagnostic_sources:z.write(ROOT / "scripts" / name,name)
    if primary_rows:write_csv(out / "primary-trials.csv",primary_rows)
    write_csv(out / "case-summary.csv",summary)
    write_csv(out / "photos-per-image.csv",photo_rows)
    write_csv(out / "photo-splits.csv",split_rows)
    write_json(out / "photo-regressions.json",regressions)
    write_json(out / "native-parity.json",parity)
    write_json(out / "constraint-diagnosis.json",diagnosis)
    write_json(out / "source-provenance.json",provenance)
    write_json(out / "archive-summary.json",{"profiles":len(summary),"photo_rows":len(photo_rows),"native_receipts":len(parity),
        "bytes":sum(p.stat().st_size for p in out.rglob("*") if p.is_file()),"archiver_sha256":digest(Path(__file__)),
        "scope":"仅Velvia固定两臂研究，额外统计及试探成本单列，复用数据显式标记；无默认升级、官方评分或性能声明"})
    print("两臂误差与候选拒绝证据归档完成")


if __name__ == "__main__":main()
