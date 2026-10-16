"""核对同初态两臂并归档真实舍入预算补偿，不再搜索或选择模型。"""
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
import numpy as np
from report_quantile_tail_study import check_epoch,model_check,constraints,load
from report_tail_grid_study import digest,write_csv,write_json,compare


def budgets(case,previous_full):
    search = case["selection"]["search"]
    records,by_source = [],Counter()
    for step in search["accepted"][search["replayed_steps"]:]:
        after = step["full_domain"]["candidate"]
        actual_sse = int(after["sum_squared_error"])-int(previous_full["sum_squared_error"])
        actual_mean = int(after["sum_upper_q24"])-int(previous_full["sum_upper_q24"])
        roles = step.get("compensation",{})
        item = {"step":step["step"],"before_loss":step["before_loss"],"after_loss":step["after_loss"],
            "proposal_source":step["proposal_source"],"moves":step["moves"],"compensation":roles,
            "actual_full_sse_delta":str(actual_sse),"actual_full_mean_upper_q24_delta":str(actual_mean)}
        if "predicted_full_sse_delta" in roles:
            item["sse_additive_gap"] = str(actual_sse-int(roles["predicted_full_sse_delta"]))
            item["mean_additive_gap"] = str(actual_mean-int(roles["predicted_full_mean_upper_q24_delta"]))
            if roles["disjoint_cell_support_certificate"] and (int(item["sse_additive_gap"]) or int(item["mean_additive_gap"])):
                raise ValueError("不相交支撑的预算可加证书与实际全流不同")
        records.append(item)
        by_source[step["proposal_source"]] += step["before_loss"]-step["after_loss"]
        previous_full = after
    return {"new_steps":records,"direct_loss_reduction_by_source":dict(by_source),
        "scope":"按接受步骤直接记账，不作因果收益拆分；未获支撑证书的组合仍以实际重放为准"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control",type=Path,required=True)
    parser.add_argument("--rounded",type=Path,required=True)
    parser.add_argument("--warm",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    if args.output.exists():raise ValueError("不覆盖已有归档")
    sources = {"control":args.control,"rounded":args.rounded}
    plans = {arm:ROOT / f"experiments/rounded-budget-{'control' if arm == 'control' else 'exact'}-v1.json" for arm in sources}
    checked = {arm:check_epoch(source,plans[arm]) for arm,source in sources.items()}
    a,b = [load(plans[arm]) for arm in sources]
    excluded = {"purpose","comparison","limits","compensation"}
    if {k:v for k,v in a.items() if k not in excluded} != {k:v for k,v in b.items() if k not in excluded}:
        raise ValueError("两臂参数不同")
    if {k:v for k,v in a["compensation"].items() if k != "method"} != {k:v for k,v in b["compensation"].items() if k != "method"}:
        raise ValueError("两臂辅助搜索上限不同")
    for arm,(run,result,expected) in checked.items():
        for name,sha in run["identity"]["warm_files"].items():
            if digest(args.warm / name) != sha:raise ValueError("热启动来源变化")
        if run["identity"]["environment"] != checked["control"][0]["identity"]["environment"]:
            raise ValueError("两臂数值环境不同")
    inventory,partition = [load(args.control / n) for n in ("photo-inventory.json","photo-partition.json")]
    if inventory != load(args.rounded / "photo-inventory.json") or partition != load(args.rounded / "photo-partition.json"):
        raise ValueError("两臂颜色频数或划分不同")
    warm = load(args.warm / "results.json")
    out = args.output
    out.mkdir(parents=True)
    for name in ("photo-inventory.json","photo-partition.json"):shutil.copyfile(args.control / name,out / name)
    shutil.copyfile(ROOT / "artifacts/rounded-budget-contracts.log",out / "contract-tests.log")
    with zipfile.ZipFile(out / "verification-sources.zip","w",zipfile.ZIP_DEFLATED) as z:
        for n in ("verify_quantile_constraints.py","verify_full_domain_guard.py"):z.write(ROOT / "scripts" / n,n)
    summary,photos,splits,regression,parity,analysis,provenance = [],[],[],[],[],[],[]
    split_ids = {"training":[r["id"] for r in partition["training"]["images"]],
        "selection":[r["id"] for r in partition["guard"]["images"]],"audit":partition["audit_ids"]}
    for arm,(run,result,expected) in checked.items():
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
            replayed = load(sources[arm] / cid / "warm-start.json")
            if case["warm_loss"] != previous["final_loss"] or replayed["model_sha256"] != previous["selection"]["model_sha256"]:
                raise ValueError("两臂没有使用同字节初态")
            model_check(sources[arm],case)
            initial,final = [load(sources[arm] / cid / n) for n in ("initial-groups.json","final-groups.json")]
            full = load(sources[arm] / cid / "full-domain.json")
            previous_full = load(args.warm / cid / "full-domain.json")["final"]
            analysis.append({"arm":arm,"case":cid,"warm_loss":case["warm_loss"],"final_loss":case["final_loss"],
                "initial":constraints(initial,inventory),"final":constraints(final,inventory),"budget_steps":budgets(case,previous_full),
                "search":{k:v for k,v in case["selection"]["search"].items() if k != "accepted"},
                "host_memory":full["host_memory"],"persistent_array_bytes":full["combined_cache_array_bytes"]})
            variants = [("historical",case["historical"],True),("warm_v3",previous["final"],True)] if arm == "control" else []
            variants += [(arm,case["final"],case["final"]["reused"])]
            for name,value,reused in variants:
                summary.append({"case":cid,"profile":name,"reused_metrics":reused,
                    **{f"cube_{k}":value["cube"][k] for k in ("mean","rms","p99","max","cvar_1pct","fraction_ge_1","fraction_ge_2","fraction_ge_3","fraction_ge_5")},
                    **{f"photos_{k}":value["photos"][k] for k in ("mean","rms","worst_image_p99","max")}})
                photos.extend({"case":cid,"profile":name,"reused_metrics":reused,**r} for r in value["photos"]["per_image"])
                regression.append({"case":cid,"profile":name,"vs_historical":compare(case["historical"]["photos"],value["photos"]),
                    "vs_warm_v3":compare(previous["final"]["photos"],value["photos"])})
                for split,ids in split_ids.items():
                    records = [r for r in value["photos"]["per_image"] if r["image"] in ids]
                    if len(records) != len(ids):raise ValueError("逐图分组缺失")
                    splits.append({"case":cid,"profile":name,"split":split,"n_images":len(records),
                        "mean":float(np.mean([r["mean"] for r in records])),"rms":float(np.sqrt(np.mean([r["rms"]**2 for r in records]))),
                        "worst_image_p99":max(r["p99"] for r in records),"max":max(r["max"] for r in records)})
            parity.extend({"arm":arm,"case":cid,"reused":case["final"]["reused"],**r} for r in case["final"]["native"])
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
                for case in result["cases"]:
                    name = case["case"]["id"]+"/historical-grid.npy"
                    data = parent.read(name)
                    z.writestr(name,data)
                    index[name] = hashlib.sha256(data).hexdigest()
        with zipfile.ZipFile(folder / "evidence.zip") as z:
            if set(index) != set(z.namelist()) or any(hashlib.sha256(z.read(n)).hexdigest() != h for n,h in index.items()):raise ValueError("归档变化")
        write_json(folder / "archive-index.json",index)
        provenance.append({"arm":arm,"git_commit":run["git_commit"],"source_sha256":expected,
            "current_source_same":{n:(ROOT / n).exists() and digest(ROOT / n) == h for n,h in expected.items()}})
    write_csv(out / "case-summary.csv",summary)
    write_csv(out / "photos-per-image.csv",photos)
    write_csv(out / "photo-groups.csv",splits)
    write_json(out / "photo-regressions.json",regression)
    write_json(out / "native-parity.json",parity)
    write_json(out / "budget-diagnostics.json",analysis)
    write_json(out / "source-provenance.json",provenance)
    plt.rcParams.update({"font.family":"Microsoft YaHei","axes.unicode_minus":False,"font.size":10})
    fig,axes = plt.subplots(2,2,figsize=(13,8),constrained_layout=True)
    for ci,cid in enumerate([c["case"]["id"] for c in warm["cases"]]):
        for arm in sources:
            item = next(a for a in analysis if a["arm"] == arm and a["case"] == cid)
            records = item["budget_steps"]["new_steps"]
            xs = list(range(len(records)+1))
            ys = [item["warm_loss"]]+[s["after_loss"] for s in records]
            axes[ci,0].step(xs,ys,where="post",marker=".",label="连续对照" if arm == "control" else "舍入预算")
        axes[ci,0].set(title=cid+"：同初态两臂缺口",xlabel="本轮接受步骤",ylabel="整数缺口，非色差单位")
        axes[ci,0].legend()
        records = [p for p in photos if p["case"] == cid and p["profile"] == "rounded"]
        previous = {p["image"]:p for p in photos if p["case"] == cid and p["profile"] == "warm_v3"}
        differences = np.array([r["mean"]-previous[r["image"]]["mean"] for r in records])
        axes[ci,1].bar(np.arange(len(records)),differences,color=np.where(differences > 0,"#d26b4d","#368b89"))
        axes[ci,1].axhline(0,color="grey",linewidth=.8)
        axes[ci,1].set(title=cid+"：舍入方案每图mean代价",xlabel="固定100图顺序",ylabel="相对v3的mean变化，越低越好")
    fig.savefig(out / "rounded-budget-comparison.png",dpi=150)
    plt.close(fig)
    write_json(out / "integrity.json",{"files":{p.relative_to(out).as_posix():digest(p) for p in out.rglob("*") if p.is_file()},
        "summary_rows":len(summary),"photo_rows":len(photos),"new_photo_rows":sum(not r["reused_metrics"] for r in photos),
        "split_rows":len(splits),"native_receipts":len(parity),"new_native_receipts":sum(not r["reused"] for r in parity),
        "report_source_sha256":digest(__file__),"scope":"两臂参数/环境/输入匹配后归档，不重新执行模型；不包括后加README/诊断/阶段说明"})
    print({"summary_rows":len(summary),"photo_rows":len(photos),"archive_bytes":sum(p.stat().st_size for p in out.rglob("*") if p.is_file())})


if __name__ == "__main__":main()
