"""归档全颜色分位候选的来源、下界松弛和最终精度，不重新搜索。"""
import argparse
from collections import Counter
import hashlib
import json
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


def diagnostics(case,inventory,initial,final):
    search = case["selection"]["search"]
    new = search["accepted"][search["replayed_steps"]:]
    changes = Counter()
    steps = []
    for record in new:
        source = record["proposal_source"]
        changes[source] += record["before_loss"]-record["after_loss"]
        steps.append({k:record[k] for k in ("step","before_loss","after_loss","proposal_source","moves")})
    rounds = []
    for record in search["global_rounds"]:
        base = record["anchor_loss"]
        errors = []
        classified = Counter()
        for trial in record["trials"]:
            if trial["lower_bound_delta"] is not None:
                gap = trial["loss"]-base-trial["lower_bound_delta"]
                if gap < 0:raise ValueError("保存的单提案下界超过真实缺口")
                errors.append(gap)
            if trial["loss"] >= base:classified["tail_loss"] += 1
            elif trial["photo_failed"]:classified["photo_guard"] += 1
            elif trial["full_failed"]:classified["full_guard"] += 1
            elif trial["accepted"]:classified["accepted"] += 1
            else:raise ValueError("全局试探没有明确判定")
        rounds.append({**{k:v for k,v in record.items() if k != "trials"},"trial_classification":dict(classified),
            "single_lower_bound_gaps":{"n":len(errors),"zero":errors.count(0),"min":min(errors,default=None),"max":max(errors,default=None),
                "sum":sum(errors)},"trials":record["trials"]})
    return {"case":case["case"]["id"],"initial":constraints(initial,inventory),"final":constraints(final,inventory),
        "warm_loss":case["warm_loss"],"final_loss":case["final_loss"],"new_steps":steps,"loss_reduction_by_source":dict(changes),
        "new_step_count_by_source":dict(Counter(r["proposal_source"] for r in new)),"global_rounds":rounds,
        "compensation_rounds":search["compensation_rounds"],"rejections":search["rejections"],"stop":search["stop"],
        "attribution_scope":"按直接接受步骤记录缺口变化，不作因果收益分摊；全局修改也可能使后续热点修改可行"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--warm",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    if args.output.exists():raise ValueError("不覆盖已归档结果")
    plan = ROOT / "experiments/quantile-tail-v3.json"
    run,result,expected = check_epoch(args.input,plan)
    for name,sha in run["identity"]["warm_files"].items():
        if digest(args.warm / name) != sha:raise ValueError("热启动来源不同")
    warm = load(args.warm / "results.json")
    inventory,partition = [load(args.input / n) for n in ("photo-inventory.json","photo-partition.json")]
    out = args.output
    out.mkdir(parents=True)
    for a,b in (("run.json","environment.json"),("verification.json","verification.json"),("photo-inventory.json","photo-inventory.json"),
                ("photo-partition.json","photo-partition.json")):
        shutil.copyfile(args.input / a,out / b)
    shutil.copyfile(plan,out / "plan.json")
    shutil.copyfile(args.input.with_suffix(".log"),out / "experiment.log")
    shutil.copyfile(ROOT / "artifacts/quantile-global-contracts.log",out / "contract-tests.log")
    summary,photos,splits,regressions,native,diagnosis = [],[],[],[],[],[]
    split_ids = {"training":[r["id"] for r in partition["training"]["images"]],
        "selection":[r["id"] for r in partition["guard"]["images"]],"audit":partition["audit_ids"]}
    members = ["run.json","results.json","verification.json","photo-inventory.json","photo-partition.json","measured-source.zip"]
    plt.rcParams.update({"font.family":"Microsoft YaHei","axes.unicode_minus":False,"font.size":10})
    fig,axes = plt.subplots(2,2,figsize=(13,8),constrained_layout=True)
    for ci,case in enumerate(result["cases"]):
        cid = case["case"]["id"]
        previous = next(c for c in warm["cases"] if c["case"]["id"] == cid)
        if case["warm_loss"] != previous["final_loss"]:raise ValueError("热启动缺口不同")
        replayed = load(args.input / cid / "warm-start.json")
        if replayed["model_sha256"] != previous["selection"]["model_sha256"]:raise ValueError("热启动模型不同")
        model_check(args.input,case)
        initial,final = [load(args.input / cid / n) for n in ("initial-groups.json","final-groups.json")]
        item = diagnostics(case,inventory,initial,final)
        used = len(case["selection"]["search"]["global_rounds"])
        item["global_round_budget"] = {"used":used,"limit":load(plan)["global_search"]["rounds"],
            "exhausted":used >= load(plan)["global_search"]["rounds"],
            "interpretation":"原stop为有限库停止；已耗尽全局轮数时不能据此断言最终模型全局邻域停滞"}
        diagnosis.append(item)
        variants = [("historical",case["historical"],True),("mixed_initial",case["initial"],True),
            ("repair_v2",previous["final"],True),("global_v3",case["final"],case["final"]["reused"])]
        for name,value,reused in variants:
            summary.append({"case":cid,"profile":name,"reused_metrics":reused,
                **{f"cube_{k}":value["cube"][k] for k in ("mean","rms","p99","max","cvar_1pct","fraction_ge_1","fraction_ge_2","fraction_ge_3","fraction_ge_5")},
                **{f"photos_{k}":value["photos"][k] for k in ("mean","rms","worst_image_p99","max")}})
            photos.extend({"case":cid,"profile":name,"reused_metrics":reused,**r} for r in value["photos"]["per_image"])
            regressions.append({"case":cid,"profile":name,"vs_historical":compare(case["historical"]["photos"],value["photos"]),
                "vs_warm_v2":compare(previous["final"]["photos"],value["photos"])})
            for split,ids in split_ids.items():
                records = [r for r in value["photos"]["per_image"] if r["image"] in ids]
                if len(records) != len(ids):raise ValueError("逐图分组缺失")
                splits.append({"case":cid,"profile":name,"split":split,"n_images":len(records),
                    "mean":float(np.mean([r["mean"] for r in records])),"rms":float(np.sqrt(np.mean([r["rms"]**2 for r in records]))),
                    "worst_image_p99":max(r["p99"] for r in records),"max":max(r["max"] for r in records)})
        native.extend({"case":cid,"reused":case["final"]["reused"],**r} for r in case["final"]["native"])
        members.extend(p.relative_to(args.input).as_posix() for p in sorted((args.input / cid).glob("*"))
            if p.suffix in (".json",".slut") and p.name not in ("results.json","selected-stage1.slut"))
        search = case["selection"]["search"]
        records = search["accepted"][search["replayed_steps"]:]
        xs = list(range(len(records)+1))
        ys = [case["warm_loss"]]+[r["after_loss"] for r in records]
        axes[ci,0].step(xs,ys,where="post",marker=".")
        global_steps = [i+1 for i,r in enumerate(records) if r["proposal_source"].startswith("global")]
        axes[ci,0].scatter(global_steps,[ys[i] for i in global_steps],color="red",s=40,label="全局提案接受")
        axes[ci,0].set(title=cid+"：从v2继续的缺口",xlabel="本轮接受步骤",ylabel="整数缺口，非色差单位")
        axes[ci,0].legend()
        x = np.arange(3)
        before,after = previous["final"]["photos"],case["final"]["photos"]
        keys = ("mean","worst_image_p99","max")
        axes[ci,1].bar(x-.18,[1]*3,.36,label="v2")
        axes[ci,1].bar(x+.18,[after[k]/before[k] for k in keys],.36,label="v3")
        axes[ci,1].axhline(1,color="grey",linestyle="--")
        axes[ci,1].set(title=cid+"：100图相对v2",xticks=x,xticklabels=["mean","最差单图p99","max"],ylabel="相对值，越低越好")
        axes[ci,1].legend()
    index = {}
    with zipfile.ZipFile(out / "evidence.zip","w",zipfile.ZIP_DEFLATED) as z:
        for name in sorted(set(members)):
            z.write(args.input / name,name)
            index[name] = digest(args.input / name)
        with zipfile.ZipFile(ROOT / "report/data/fractional-fit-v1/models-and-selection.zip") as parent:
            for case in result["cases"]:
                name = case["case"]["id"]+"/historical-grid.npy"
                data = parent.read(name)
                z.writestr(name,data)
                index[name] = hashlib.sha256(data).hexdigest()
    with zipfile.ZipFile(out / "evidence.zip") as z:
        if set(index) != set(z.namelist()) or any(hashlib.sha256(z.read(n)).hexdigest() != h for n,h in index.items()):raise ValueError("归档不同")
    write_json(out / "archive-index.json",index)
    with zipfile.ZipFile(out / "verification-sources.zip","w",zipfile.ZIP_DEFLATED) as z:
        for name in ("verify_quantile_constraints.py","verify_full_domain_guard.py"):z.write(ROOT / "scripts" / name,name)
    write_csv(out / "case-summary.csv",summary)
    write_csv(out / "photos-per-image.csv",photos)
    write_csv(out / "photo-groups.csv",splits)
    write_json(out / "photo-regressions.json",regressions)
    write_json(out / "global-diagnostics.json",diagnosis)
    write_json(out / "native-parity.json",native)
    write_json(out / "source-provenance.json",{"git_commit":run["git_commit"],"executed_source_sha256":expected,
        "current_source_same":{n:(ROOT / n).exists() and digest(ROOT / n) == h for n,h in expected.items()},
        "report_sources_sha256":{p:digest(ROOT / "scripts" / p) for p in ("report_quantile_global.py","report_quantile_tail_study.py","report_tail_grid_study.py")}})
    fig.savefig(out / "global-quantile-comparison.png",dpi=150)
    plt.close(fig)
    write_json(out / "integrity.json",{"files":{p.relative_to(out).as_posix():digest(p) for p in out.rglob("*") if p.is_file()},
        "summary_rows":len(summary),"photo_rows":len(photos),"new_photo_rows":sum(not r["reused_metrics"] for r in photos),
        "split_rows":len(splits),"native_receipts":len(native),"new_native_receipts":sum(not r["reused"] for r in native),
        "scope":"原执行源/模型/直方图和接受日志归档，派生表不重新执行模型；不包括随后README和阶段说明"})
    print(json.dumps({"archive":str(out),"members":len(index),"photo_rows":len(photos),"archive_bytes":sum(p.stat().st_size for p in out.rglob("*") if p.is_file())},ensure_ascii=False))


if __name__ == "__main__":main()
