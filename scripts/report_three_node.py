"""归档旧两节点前缀与新增三节点块，区分候选成本及真子集证据。"""
import argparse
from collections import Counter
import hashlib
from pathlib import Path
import shutil
import sys
import zipfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "python"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
from report_quantile_tail_study import check_epoch,model_check,constraints,load
from report_rounded_budget import budgets
from report_tail_grid_study import digest,write_csv,write_json,compare


def subset_audit(search):
    result = []
    for round_info in search["compensation_rounds"]:
        block = round_info.get("block_search")
        if block is None:continue
        accepted = [t for t in block["trials"] if t["accepted"]]
        if accepted:
            if len(accepted) != 1 or len(block["subset_trials"]) != 6 or len(block["confirmation"]) != 1:
                raise ValueError("可行三节点块没有完整六真子集及确认")
            full = accepted[0]
            chosen = block["confirmation"][0]
            allowed = {(m["node"],tuple(m["value"])) for m in full["moves"]}
            subsets = []
            for t in block["subset_trials"]:
                key = frozenset((m["node"],tuple(m["value"])) for m in t["moves"])
                if not 0 < len(key) < 3 or not key < allowed:raise ValueError("真子集不是原节点值子集")
                subsets.append(key)
            if len(set(subsets)) != 6:raise ValueError("真子集重复或遗漏")
            feasible = [full]+[t for t in block["subset_trials"] if t["accepted"]]
            expected = min(feasible,key=lambda t:(t["loss"],len(t["moves"]),tuple((m["node"],tuple(m["value"])) for m in t["moves"])))
            if not chosen["accepted"] or chosen["moves"] != expected["moves"] or chosen["loss"] != expected["loss"]:
                raise ValueError("确认提交没有选择真实缺口最好的可行项")
            if block["selected"]["all_proper_subsets_rejected"] != all(not t["accepted"] for t in block["subset_trials"]):
                raise ValueError("真子集必要性标记不同")
        result.append({**block,"observed_decisions":dict(Counter(t["decision"] for t in block["trials"]))})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control",type=Path,required=True)
    parser.add_argument("--optimized",type=Path,required=True)
    parser.add_argument("--warm",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    if args.output.exists():raise ValueError("不覆盖旧阶段归档")
    sources = {"two_node":args.control,"three_node":args.optimized}
    plans = {"two_node":ROOT / "experiments/velvia-candidate-trace-v1.json","three_node":ROOT / "experiments/velvia-three-node-v1.json"}
    checked = {arm:check_epoch(source,plans[arm]) for arm,source in sources.items()}
    if checked["two_node"][0]["identity"]["environment"] != checked["three_node"][0]["identity"]["environment"]:
        raise ValueError("诊断与优化环境不同")
    a,b = [load(plans[k]) for k in sources]
    for field in ("parent","warm_start","cases","threads","pixels_per_image","pixel_seed","steps","focus_count","trial_limit","pair_nodes","full_domain_guard","memory_array_budget_bytes"):
        if a[field] != b[field]:raise ValueError("节点块扩展之外的冻结参数不同")
    out = args.output
    out.mkdir(parents=True)
    inventory,partition = [load(args.control / n) for n in ("photo-inventory.json","photo-partition.json")]
    for n in ("photo-inventory.json","photo-partition.json"):shutil.copyfile(args.control / n,out / n)
    shutil.copyfile(ROOT / "artifacts/three-node-contracts.log",out / "contract-tests.log")
    warm = load(args.warm / "results.json")
    summary,photos,splits,regressions,parity,diagnostics,provenance = [],[],[],[],[],[],[]
    splits_ids = {"training":[r["id"] for r in partition["training"]["images"]],
        "selection":[r["id"] for r in partition["guard"]["images"]],"audit":partition["audit_ids"]}
    baseline_case = checked["two_node"][1]["cases"][0]
    optimized_case = checked["three_node"][1]["cases"][0]
    old_prefix = baseline_case["selection"]["search"]["compensation_rounds"][0]
    new_prefix = optimized_case["selection"]["search"]["compensation_rounds"][0]
    if old_prefix["trials"] != new_prefix["trials"] or old_prefix["statistics_sha256"] != new_prefix["statistics_sha256"]:
        raise ValueError("原128对前缀不一致")
    for arm,(run,result,expected) in checked.items():
        for n,h in run["identity"]["warm_files"].items():
            if digest(args.warm / n) != h:raise ValueError("warm来源变化")
        if load(sources[arm] / "photo-inventory.json") != inventory:raise ValueError("颜色频数不同")
        folder = out / arm
        folder.mkdir()
        for a,b in (("run.json","environment.json"),("verification.json","verification.json")):
            shutil.copyfile(sources[arm] / a,folder / b)
        shutil.copyfile(plans[arm],folder / "plan.json")
        shutil.copyfile(sources[arm].with_suffix(".log"),folder / "experiment.log")
        members = ["run.json","results.json","verification.json","photo-inventory.json","photo-partition.json","measured-source.zip"]
        for case in result["cases"]:
            cid = case["case"]["id"]
            previous = next(c for c in warm["cases"] if c["case"]["id"] == cid)
            if case["warm_loss"] != previous["final_loss"] or load(sources[arm] / cid / "warm-start.json")["model_sha256"] != previous["selection"]["model_sha256"]:
                raise ValueError("初态模型或缺口不同")
            model_check(sources[arm],case)
            initial,final = [load(sources[arm] / cid / n) for n in ("initial-groups.json","final-groups.json")]
            full = load(sources[arm] / cid / "full-domain.json")
            block_info = subset_audit(case["selection"]["search"])
            diagnostics.append({"arm":arm,"case":cid,"initial":constraints(initial,inventory),"final":constraints(final,inventory),
                "budget_steps":budgets(case,load(args.warm / cid / "full-domain.json")["final"]),"blocks":block_info,
                "search":{k:v for k,v in case["selection"]["search"].items() if k != "accepted"},"host_memory":full["host_memory"]})
            variants = [("historical",case["historical"],True),("warm_v3",previous["final"],True)] if arm == "two_node" else []
            variants += [(arm,case["final"],case["final"]["reused"])]
            for name,value,reused in variants:
                summary.append({"case":cid,"profile":name,"reused_metrics":reused,
                    **{f"cube_{k}":value["cube"][k] for k in ("mean","rms","p99","max","cvar_1pct","fraction_ge_1","fraction_ge_2","fraction_ge_3","fraction_ge_5")},
                    **{f"photos_{k}":value["photos"][k] for k in ("mean","rms","worst_image_p99","max")}})
                photos.extend({"case":cid,"profile":name,"reused_metrics":reused,**r} for r in value["photos"]["per_image"])
                regressions.append({"profile":name,"vs_historical":compare(case["historical"]["photos"],value["photos"]),"vs_warm_v3":compare(previous["final"]["photos"],value["photos"])})
                for split,ids in splits_ids.items():
                    records = [r for r in value["photos"]["per_image"] if r["image"] in ids]
                    if len(records) != len(ids):raise ValueError("逐图分组缺失")
                    splits.append({"profile":name,"split":split,"n_images":len(records),"mean":float(np.mean([r["mean"] for r in records])),
                        "rms":float(np.sqrt(np.mean([r["rms"]**2 for r in records]))),"worst_image_p99":max(r["p99"] for r in records),"max":max(r["max"] for r in records)})
            parity.extend({"arm":arm,"reused":case["final"]["reused"],**r} for r in case["final"]["native"])
            members.extend(p.relative_to(sources[arm]).as_posix() for p in sorted((sources[arm] / cid).glob("*"))
                if p.suffix in (".json",".slut") and p.name not in ("results.json","selected-stage1.slut"))
        index = {}
        with zipfile.ZipFile(folder / "evidence.zip","w",zipfile.ZIP_DEFLATED) as z:
            for name in sorted(set(members)):
                z.write(sources[arm] / name,name)
                index[name] = digest(sources[arm] / name)
            z.write(plans[arm],"plan.json")
            index["plan.json"] = digest(plans[arm])
            with zipfile.ZipFile(ROOT / "report/data/fractional-fit-v1/models-and-selection.zip") as parent:
                name = "velvia-vivid/historical-grid.npy"
                data = parent.read(name)
                z.writestr(name,data)
                index[name] = hashlib.sha256(data).hexdigest()
        with zipfile.ZipFile(folder / "evidence.zip") as z:
            if set(index) != set(z.namelist()) or any(hashlib.sha256(z.read(n)).hexdigest() != h for n,h in index.items()):raise ValueError("归档SHA不同")
        write_json(folder / "archive-index.json",index)
        provenance.append({"arm":arm,"git_commit":run["git_commit"],"source_sha256":expected,
            "current_source_same":{n:(ROOT / n).exists() and digest(ROOT / n) == h for n,h in expected.items()}})
    with zipfile.ZipFile(out / "verification-sources.zip","w",zipfile.ZIP_DEFLATED) as z:
        for n in ("verify_quantile_constraints.py","verify_full_domain_guard.py"):z.write(ROOT / "scripts" / n,n)
    write_csv(out / "case-summary.csv",summary)
    write_csv(out / "photos-per-image.csv",photos)
    write_csv(out / "photo-groups.csv",splits)
    write_json(out / "photo-regressions.json",regressions)
    write_json(out / "native-parity.json",parity)
    write_json(out / "block-diagnostics.json",diagnostics)
    write_json(out / "source-provenance.json",provenance)
    plt.rcParams.update({"font.family":"Microsoft YaHei","axes.unicode_minus":False,"font.size":10})
    fig,axes = plt.subplots(1,2,figsize=(13,5),constrained_layout=True)
    records = diagnostics[1]["budget_steps"]["new_steps"]
    axes[0].axhline(optimized_case["warm_loss"],color="grey",linestyle="--",label="原128对停止基线")
    axes[0].step(range(len(records)+1),[optimized_case["warm_loss"]]+[s["after_loss"] for s in records],where="post",marker=".",label="三节点扩展")
    axes[0].set(title="Velvia冻结尾部整数缺口",xlabel="新增接受步骤",ylabel="整数缺口，非色差单位",xlim=(0,max(1,len(records))))
    axes[0].xaxis.set_major_locator(MaxNLocator(integer=True))
    axes[0].legend()
    groups = [old_prefix["trials"],*[b["trials"] for b in diagnostics[1]["blocks"]]]
    labels = ["原128辅助对"]+[f"第{k+1}轮三节点" for k in range(len(groups)-1)]
    bottom = np.zeros(len(groups))
    for decision,label in (("tail_loss","未下降"),("photo_guard","照片保护"),("full_guard","全域保护"),("accepted","接受")):
        values = [sum(t["decision"] == decision for t in group) for group in groups]
        axes[1].bar(range(len(groups)),values,bottom=bottom,label=label)
        bottom += values
    axes[1].set(title="实际试探判定（追加成本，非等成本比较）",xticks=range(len(groups)),xticklabels=labels,ylabel="试探次数")
    axes[1].legend()
    fig.savefig(out / "three-node-comparison.png",dpi=150)
    plt.close(fig)
    write_json(out / "integrity.json",{"files":{p.relative_to(out).as_posix():digest(p) for p in out.rglob("*") if p.is_file()},
        "summary_rows":len(summary),"photo_rows":len(photos),"new_photo_rows":sum(not r["reused_metrics"] for r in photos),"split_rows":len(splits),
        "native_receipts":len(parity),"new_native_receipts":sum(not r["reused"] for r in parity),"pair_prefix_identical":True,
        "report_source_sha256":digest(__file__),"scope":"按冻结方案归档诊断与扩展，核对真子集选择/证书；不重新搜索或执行模型，不含后加README/阶段说明"})
    print({"archive":str(out),"photo_rows":len(photos),"archive_bytes":sum(p.stat().st_size for p in out.rglob("*") if p.is_file())})


if __name__ == "__main__":main()
