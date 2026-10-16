"""归档固定参照两臂实验、完整误差分布、拒绝原因及源码/模型绑定。"""
import argparse
from collections import Counter
import hashlib
from pathlib import Path
import shutil
import zipfile
from report_quantile_tail_study import check_epoch,model_check,constraints,load
from report_tail_grid_study import digest,write_csv,write_json,compare

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--guard",type=Path,required=True)
    parser.add_argument("--aware",type=Path,required=True)
    parser.add_argument("--warm",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    if args.output.exists():raise ValueError("不覆盖旧归档")
    sources = {"guard":args.guard,"aware":args.aware}
    plans = {arm:ROOT / f"experiments/stable-tail-{name}-v1.json" for arm,name in (("guard","guard"),("aware","aware"))}
    checked = {arm:check_epoch(path,plans[arm]) for arm,path in sources.items()}
    if checked["guard"][0]["identity"]["environment"] != checked["aware"][0]["identity"]["environment"]:raise ValueError("两臂环境不同")
    a,b = [load(plans[arm]) for arm in sources]
    for field in ("parent","warm_start","cases","threads","pixels_per_image","pixel_seed","steps","focus_count","trial_limit","pair_nodes","compensation","full_domain_guard","memory_array_budget_bytes"):
        if a[field] != b[field]:raise ValueError("尾部排序之外的实验配置不同")
    warm = load(args.warm / "results.json")
    inventory,partition = [load(args.guard / n) for n in ("photo-inventory.json","photo-partition.json")]
    if load(args.aware / "photo-inventory.json") != inventory:raise ValueError("两臂颜色倒排输入不同")
    out = args.output
    out.mkdir(parents=True)
    counterexamples = ROOT / "artifacts/stable-tail-counterexamples-v1.json"
    diagnostic = load(counterexamples)
    for name,h in diagnostic["inputs_sha256"].items():
        if digest(Path(name)) != h:raise ValueError("独立反例复算输入变化")
    for name,h in diagnostic["source_sha256"].items():
        if digest(ROOT / "scripts" / name) != h:raise ValueError("独立反例复算源码变化")
    shutil.copyfile(counterexamples,out / "counterexamples.json")
    shutil.copyfile(counterexamples.with_suffix(".log"),out / "counterexamples.log")
    for name in ("photo-inventory.json","photo-partition.json"):shutil.copyfile(args.guard / name,out / name)
    shutil.copyfile(ROOT / "artifacts/stable-tail-contracts-v1.log",out / "contract-tests.log")
    summary,photo_rows,regressions,diagnosis,provenance,parity = [],[],[],[],[],[]
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
                "rounds":rounds,"helper_decisions":dict(Counter(t["decision"] for t in trials)),"helper_breakdown":breakdown,
                "helper_failed_conditions":dict(rejection.most_common()),"helper_trials":trials,"host_memory":full["host_memory"],
                "persistent_array_bytes":full["combined_cache_array_bytes"]})
            profiles = [("historical",case["historical"],True),("warm",old["final"],True)] if arm == "guard" else []
            profiles += [(arm,case["final"],case["final"]["reused"])]
            for name,value,reused in profiles:
                summary.append({"case":cid,"profile":name,"reused_metrics":reused,
                    **{f"cube_{k}":value["cube"][k] for k in ("mean","rms","p99","max","cvar_1pct","fraction_ge_1","fraction_ge_2","fraction_ge_3","fraction_ge_5")},
                    **{f"photos_{k}":value["photos"][k] for k in ("mean","rms","worst_image_p99","max")}})
                photo_rows.extend({"profile":name,"reused_metrics":reused,**r} for r in value["photos"]["per_image"])
                regressions.append({"profile":name,"vs_warm":compare(old["final"]["photos"],value["photos"]),
                    "vs_historical":compare(case["historical"]["photos"],value["photos"])})
            parity.extend({"arm":arm,"reused":case["final"]["reused"],**p} for p in case["final"]["native"])
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
        for name in ("verify_stability.py","verify_quantile_constraints.py","verify_full_domain_guard.py"):z.write(ROOT / "scripts" / name,name)
    with zipfile.ZipFile(out / "diagnostic-sources.zip","w",zipfile.ZIP_DEFLATED) as z:
        for name in diagnostic["source_sha256"]:z.write(ROOT / "scripts" / name,name)
    write_csv(out / "case-summary.csv",summary)
    write_csv(out / "photos-per-image.csv",photo_rows)
    write_json(out / "photo-regressions.json",regressions)
    write_json(out / "native-parity.json",parity)
    write_json(out / "constraint-diagnosis.json",diagnosis)
    write_json(out / "source-provenance.json",provenance)
    write_json(out / "archive-summary.json",{"profiles":len(summary),"photo_rows":len(photo_rows),"native_receipts":len(parity),
        "bytes":sum(p.stat().st_size for p in out.rglob("*") if p.is_file()),"archiver_sha256":digest(Path(__file__)),
        "scope":"仅Velvia固定两臂研究，新增尾部统计成本单列，复用数据显式标记；无默认升级、官方评分或性能声明"})
    print("两臂误差与候选拒绝证据归档完成")


if __name__ == "__main__":main()
