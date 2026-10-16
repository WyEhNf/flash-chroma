"""归档两次冻结搜索、独立复核及局部反事实；不重新拟合或选择模型。"""
import argparse
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
from lutlab import io,study_provenance
from report_tail_grid_study import compare,digest,write_csv,write_json


def load(path):return json.loads(path.read_text(encoding="utf-8"))


def check_epoch(source,plan):
    run,result,verification = [load(source / n) for n in ("run.json","results.json","verification.json")]
    if run["identity_sha256"] != study_provenance.identity_digest(run["identity"]) or result["run_identity"] != run["identity_sha256"]:
        raise ValueError("运行身份不同")
    if digest(plan) != run["identity"]["plan_sha256"]:raise ValueError("冻结计划变化")
    for name,expected in verification["input_sha256"].items():
        if digest(source / name) != expected:raise ValueError("独立复核输入变化")
    if not verification["verified"] or verification["external_dependencies_loaded"]:raise ValueError("独立复核未通过")
    for name,key in (("verify_quantile_constraints.py","verifier_sha256"),("verify_full_domain_guard.py","full_verifier_sha256")):
        if digest(ROOT / "scripts" / name) != verification[key]:raise ValueError("复核源码变化")
    expected = {n.replace("\\","/"):h for n,h in {**run["identity"]["source_sha256"],**run["identity"]["stage_source_sha256"]}.items()}
    with zipfile.ZipFile(source / "measured-source.zip") as z:
        if set(z.namelist()) != set(expected) or any(hashlib.sha256(z.read(n)).hexdigest() != h for n,h in expected.items()):
            raise ValueError("实测源码快照不同")
    return run,result,expected


def model_check(source,case):
    cid = case["case"]["id"]
    model_path = source / cid / "repaired.slut"
    model,old = io.load_sparse(model_path),io.load_sparse(source / cid / "historical.slut")
    if digest(model_path) != case["selection"]["model_sha256"] or not all(np.array_equal(a,b) for a,b in zip(model.tables(),old.tables())):
        raise ValueError("最终模型或权威轴表不同")
    if not case["final"]["reused"]:
        if digest(source / cid / "repaired.rgb") != case["final"]["cube"]["prediction_sha256"]:raise ValueError("完整新流不同")
    if len(case["final"]["native"]) != 2 or any(r["byte_mismatches"] or r["sha256"] != case["final"]["cube"]["prediction_sha256"] for r in case["final"]["native"]):
        raise ValueError("原生回执不同")


def constraints(report,inventory):
    records = []
    for group,meta in zip(report["groups"],inventory["groups"]):
        for condition,cost in zip(group["constraints"],group["costs"]):
            records.append({"group":group["group"],"image":meta["image"],"kind":meta["kind"],
                **condition,"excess_pixels":max(0,condition["actual_tail_pixels"]-condition["allowed_tail_pixels"]),
                "loss":cost,"category":"max" if condition["allowed_tail_pixels"] == 0 else "p99_endpoint"})
    return {"violating_groups":sum(any(g["costs"]) for g in report["groups"]),
        "violating_constraints":sum(r["loss"] > 0 for r in records),"loss":report["loss"],
        "loss_by_category":{k:sum(r["loss"] for r in records if r["category"] == k) for k in ("max","p99_endpoint")},
        "conditions":records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v1",type=Path,required=True)
    parser.add_argument("--v2",type=Path,required=True)
    parser.add_argument("--diagnosis",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    if args.output.exists():raise ValueError("不覆盖旧归档")
    plans = [ROOT / f"experiments/quantile-tail-v{k}.json" for k in (1,2)]
    sources = [args.v1,args.v2]
    checked = [check_epoch(s,p) for s,p in zip(sources,plans)]
    if load(args.v1 / "photo-inventory.json") != load(args.v2 / "photo-inventory.json"):
        raise ValueError("两次图片约束输入不同")
    diagnosis = load(args.diagnosis)
    if diagnosis["source_sha256"] != digest(ROOT / "scripts/diagnose_quantile_compensation.py"):
        raise ValueError("反事实源码变化")
    for p,h in diagnosis["run_inputs"].items():
        if digest(ROOT / p) != h:raise ValueError("反事实输入变化")
    out = args.output
    out.mkdir(parents=True)
    inventory,partition = [load(args.v1 / n) for n in ("photo-inventory.json","photo-partition.json")]
    for n in ("photo-inventory.json","photo-partition.json"):shutil.copyfile(args.v1 / n,out / n)
    shutil.copyfile(args.diagnosis,out / "compensation-counterfactuals.json")
    shutil.copyfile(ROOT / "artifacts/quantile-compensation-diagnosis-v1.log",out / "diagnosis.log")
    for a,b in (("quantile-tail-contracts.log","contracts-v1.log"),("quantile-compensation-contracts.log","contracts-v2-first-failure.log"),
                ("quantile-compensation-contracts-fixed.log","contracts-v2-fixed.log")):
        shutil.copyfile(ROOT / "artifacts" / a,out / b)
    with zipfile.ZipFile(out / "verification-sources.zip","w",zipfile.ZIP_DEFLATED) as z:
        for name in ("verify_quantile_constraints.py","verify_full_domain_guard.py"):z.write(ROOT / "scripts" / name,name)
    summary,photo_rows,split_rows,regressions,native,details,source_changes = [],[],[],[],[],[],[]
    split_ids = {"training":[r["id"] for r in partition["training"]["images"]],
        "selection":[r["id"] for r in partition["guard"]["images"]],"audit":partition["audit_ids"]}
    for epoch,(source,plan,(run,result,expected)) in enumerate(zip(sources,plans,checked),1):
        folder = out / f"epoch-v{epoch}"
        folder.mkdir()
        for a,b in (("run.json","environment.json"),("verification.json","verification.json")):
            shutil.copyfile(source / a,folder / b)
        shutil.copyfile(plan,folder / "plan.json")
        shutil.copyfile(source.with_suffix(".log"),folder / "experiment.log")
        members = ["run.json","results.json","verification.json","photo-inventory.json","photo-partition.json","measured-source.zip"]
        for case in result["cases"]:
            cid = case["case"]["id"]
            model_check(source,case)
            members.extend(p.relative_to(source).as_posix() for p in sorted((source / cid).glob("*"))
                if p.suffix in (".json",".slut") and p.name not in ("results.json","selected-stage1.slut"))
            initial,final = [load(source / cid / n) for n in ("initial-groups.json","final-groups.json")]
            details.append({"epoch":epoch,"case":cid,"initial":constraints(initial,inventory),"final":constraints(final,inventory),
                "search":{k:v for k,v in case["selection"]["search"].items() if k != "accepted"}})
            variants = [("historical",case["historical"],True),("mixed_initial",case["initial"],True)] if epoch == 1 else []
            variants += [(f"repair_v{epoch}",case["final"],case["final"]["reused"])]
            for name,value,reused in variants:
                summary.append({"case":cid,"profile":name,"reused_metrics":reused,
                    **{f"cube_{k}":value["cube"][k] for k in ("mean","rms","p99","max","cvar_1pct","fraction_ge_1","fraction_ge_2","fraction_ge_3","fraction_ge_5")},
                    **{f"photos_{k}":value["photos"][k] for k in ("mean","rms","worst_image_p99","max")},
                    "tail_loss":initial["loss"] if name == "mixed_initial" else final["loss"] if name.startswith("repair") else 0,
                    "tail_constraint_scope":"原101组参考" if name == "historical" else "冻结101组充分条件"})
                photo_rows.extend({"case":cid,"profile":name,"reused_metrics":reused,**r} for r in value["photos"]["per_image"])
                regressions.append({"case":cid,"profile":name,"vs_historical":compare(case["historical"]["photos"],value["photos"]),
                    "vs_mixed_initial":compare(case["initial"]["photos"],value["photos"])})
                for split,ids in split_ids.items():
                    images = [r for r in value["photos"]["per_image"] if r["image"] in ids]
                    if len(images) != len(ids):raise ValueError("完整图片分组缺失")
                    split_rows.append({"case":cid,"profile":name,"split":split,"n_images":len(images),
                        "mean":float(np.mean([r["mean"] for r in images])),"rms":float(np.sqrt(np.mean([r["rms"]**2 for r in images]))),
                        "worst_image_p99":max(r["p99"] for r in images),"max":max(r["max"] for r in images)})
            native.extend({"epoch":epoch,"case":cid,"reused":case["final"]["reused"],**r} for r in case["final"]["native"])
        index = {}
        with zipfile.ZipFile(folder / "evidence.zip","w",zipfile.ZIP_DEFLATED) as z:
            for name in sorted(set(members)):
                z.write(source / name,name)
                index[name] = digest(source / name)
            with zipfile.ZipFile(ROOT / "report/data/fractional-fit-v1/models-and-selection.zip") as parent:
                for case in result["cases"]:
                    name = case["case"]["id"]+"/historical-grid.npy"
                    data = parent.read(name)
                    z.writestr(name,data)
                    index[name] = hashlib.sha256(data).hexdigest()
        write_json(folder / "archive-index.json",index)
        with zipfile.ZipFile(folder / "evidence.zip") as z:
            if set(index) != set(z.namelist()) or any(hashlib.sha256(z.read(n)).hexdigest() != h for n,h in index.items()):
                raise ValueError("归档成员变化")
        source_changes.append({"epoch":epoch,"git_commit":run["git_commit"],"executed_source_sha256":expected,
            "current_source_same":{name:(ROOT / name).exists() and digest(ROOT / name) == h for name,h in expected.items()}})
    write_csv(out / "case-summary.csv",summary)
    write_csv(out / "photos-per-image.csv",photo_rows)
    write_csv(out / "photo-groups.csv",split_rows)
    write_json(out / "photo-regressions.json",regressions)
    write_json(out / "native-parity.json",native)
    write_json(out / "constraint-diagnostics.json",details)
    write_json(out / "source-provenance.json",source_changes)
    plt.rcParams.update({"font.family":"Microsoft YaHei","axes.unicode_minus":False,"font.size":10})
    fig,axes = plt.subplots(2,2,figsize=(13,8),constrained_layout=True)
    for ci,cid in enumerate([c["case"]["id"] for c in checked[0][1]["cases"]]):
        first,second = [next(c for c in result["cases"] if c["case"]["id"] == cid) for run,result,expected in checked]
        accepted = second["selection"]["search"]["accepted"]
        xs = list(range(len(accepted)+1))
        ys = [second["initial_loss"]]+[r["after_loss"] for r in accepted]
        axes[ci,0].step(xs,ys,where="post",marker=".")
        axes[ci,0].axvline(len(first["selection"]["search"]["accepted"]),color="grey",linestyle="--",label="v1终点")
        axes[ci,0].set(title=cid+"：冻结尾部整数缺口",xlabel="累计接受步骤",ylabel="缺口（非色差单位）")
        axes[ci,0].legend()
        values = [r for r in summary if r["case"] == cid]
        x = np.arange(3)
        for i,value in enumerate(values):
            keylist = ("photos_mean","photos_worst_image_p99","photos_max")
            reference = values[0]
            axes[ci,1].bar(x+(i-1.5)*.19,[value[k]/reference[k] for k in keylist],.19,
                label=("历史","混合初态","修复v1","补偿v2")[i])
        axes[ci,1].axhline(1,color="grey",linestyle="--")
        axes[ci,1].set(title=cid+"：完整100图相对历史",xticks=x,xticklabels=["mean","最差单图p99","max"],ylabel="相对值，越低越好")
        axes[ci,1].legend(ncol=2)
    fig.savefig(out / "quantile-repair-comparison.png",dpi=150)
    plt.close(fig)
    files = {p.relative_to(out).as_posix():digest(p) for p in out.rglob("*") if p.is_file()}
    write_json(out / "integrity.json",{"files":files,"summary_rows":len(summary),"photo_rows":len(photo_rows),
        "new_photo_rows":sum(not r["reused_metrics"] for r in photo_rows),"split_rows":len(split_rows),"native_receipts":len(native),
        "new_native_receipts":sum(not r["reused"] for r in native),"report_source_sha256":digest(__file__),
        "scope":"不包括随后添加的README与阶段说明；原始流/完整表留在忽略缓存，模型和输出SHA在冻结证据中"})
    print(json.dumps({"archive":str(out),"summary_rows":len(summary),"photo_rows":len(photo_rows),"archive_bytes":sum(p.stat().st_size for p in out.rglob("*") if p.is_file())},ensure_ascii=False))


if __name__ == "__main__":main()
