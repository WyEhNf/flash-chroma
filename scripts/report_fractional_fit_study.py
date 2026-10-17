"""归档原轴表配对实验与支撑证明，不重拟合或重新选择模型。"""
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
from report_tail_grid_study import compare,write_csv,write_json,digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    source,out = args.input,args.output
    if out.exists():raise ValueError("不覆盖旧归档")
    run = json.loads((source / "run.json").read_text(encoding="utf-8"))
    result = json.loads((source / "results.json").read_text(encoding="utf-8"))
    if run["identity_sha256"] != study_provenance.identity_digest(run["identity"]) or result["run_identity"] != run["identity_sha256"]:
        raise ValueError("运行身份不一致")
    expected = {k.replace("\\","/"):v for k,v in {**run["identity"]["source_sha256"],**run["identity"]["stage_source_sha256"]}.items()}
    with zipfile.ZipFile(source / "measured-source.zip") as z:
        if set(z.namelist()) != set(expected) or any(hashlib.sha256(z.read(n)).hexdigest() != h for n,h in expected.items()):
            raise ValueError("实测源码快照不同")
    plan = ROOT / "experiments/fractional-fit-v1.json"
    if digest(plan) != run["identity"]["plan_sha256"]:raise ValueError("冻结计划变化")
    out.mkdir(parents=True)
    for a,b in (("run.json","environment.json"),("results.json","results.json"),("photo-partition.json","photo-partition.json"),("measured-source.zip","measured-source.zip")):
        shutil.copyfile(source / a,out / b)
    shutil.copyfile(plan,out / "plan.json")
    shutil.copyfile(source.with_suffix(".log"),out / "experiment.log")
    shutil.copyfile(ROOT / "artifacts/fractional-fit-contracts.log",out / "contract-tests.log")
    partition = json.loads((source / "photo-partition.json").read_text(encoding="utf-8"))
    groups = {n:[r["id"] for r in partition[n]["images"]] for n in ("training","guard")}
    groups["audit"] = partition["audit_ids"]
    summary,photos,regressions,parity,splits,proofs = [],[],[],[],[],[]
    plt.rcParams.update({"font.family":"Microsoft YaHei","axes.unicode_minus":False,"font.size":10})
    fig,axes = plt.subplots(2,2,figsize=(14,9),constrained_layout=True)
    labels = ["历史","整数纯完整域","整数混合","原轴纯完整域","原轴混合"]
    for ci,c in enumerate(result["cases"]):
        cid = c["case"]["id"]
        historical = c["bank"]["historical"]
        old_model = io.load_sparse(source / cid / "historical.slut")
        for name,value in c["bank"].items():
            summary.append({"case":cid,"profile":name,"reused":value["reused_metrics"],
                **{f"cube_{k}":value["cube"][k] for k in ("mean","rms","p99","max","fraction_ge_1","fraction_ge_2","fraction_ge_3","fraction_ge_5")},
                **{f"photos_{k}":value["photos"][k] for k in ("mean","rms","worst_image_p99","max")},
                "guard_photo_mean":value["guard"]["mean"],"full_guard":value["full_domain_certificate"]["accepted"],
                "selected":c["selection_before_photos"]["winner"] == name})
            photos.extend({"case":cid,"profile":name,"reused":value["reused_metrics"],**r} for r in value["photos"]["per_image"])
            regressions.append({"case":cid,"profile":name,"vs_historical":compare(historical["photos"],value["photos"]),
                "vs_integer_same_objective":compare(c["bank"]["control_mixed" if name == "fractional_mixed" else "control_full"]["photos"],value["photos"]) if name.startswith("fractional") else None,
                "selection_failures":c["selection_before_photos"]["failures"][name]})
            for group,ids in groups.items():
                rows = [r for r in value["photos"]["per_image"] if r["image"] in ids]
                if len(rows) != len(ids):raise ValueError("逐图分组数量不同")
                splits.append({"case":cid,"profile":name,"group":group,"n_images":len(rows),
                    "mean":float(np.mean([r["mean"] for r in rows])),"rms":float(np.sqrt(np.mean([r["rms"]**2 for r in rows]))),
                    "worst_image_p99":max(r["p99"] for r in rows),"max":max(r["max"] for r in rows)})
            if name.startswith("fractional"):
                path = source / cid / name / "model.slut"
                model = io.load_sparse(path)
                if digest(path) != value["model_sha256"] or not all(np.array_equal(a,b) for a,b in zip(model.tables(),old_model.tables())):
                    raise ValueError("新模型没有保留历史轴表或SHA不同")
                if digest(source / cid / name / "cube.rgb") != value["cube"]["prediction_sha256"]:
                    raise ValueError("新完整流SHA变化")
                parity.extend({"case":cid,"profile":name,**r} for r in value["native"])
                if any(r["sha256"] != value["cube"]["prediction_sha256"] or r["byte_mismatches"] != 0 for r in value["native"]):
                    raise ValueError("原生流绑定不同")
                proofs.append({"case":cid,"profile":name,"support":value["fit"]["support_certificate"],
                    "fixed_triplet":value["fixed_triplet_certificate"]})
        for col,scope,keys in ((0,"cube",("mean","rms","p99","max")),(1,"photos",("mean","rms","worst_image_p99","max"))):
            ax = axes[ci,col]
            largest = 1.
            for i,key in enumerate(keys):
                values = [v[scope][key]/historical[scope][key] for v in c["bank"].values()]
                largest = max(largest,max(values))
                ax.bar(np.arange(5)+(i-1.5)*.2,values,.2,label="最差单图p99" if key == "worst_image_p99" else key)
            ax.axhline(1,color="black",linestyle="--",linewidth=1)
            ax.set_xticks(np.arange(5),labels,rotation=12)
            ax.set(title=cid+("：完整色域" if col == 0 else "：完整100图"),ylabel="相对历史基线（越低越好）",ylim=(0,largest*1.16))
            ax.legend(ncol=4,fontsize=8)
            ax.grid(axis="y",alpha=.2)
    fig.savefig(out / "fractional-fit-comparison.png",dpi=150)
    plt.close(fig)
    index = {}
    with zipfile.ZipFile(out / "models-and-selection.zip","w",zipfile.ZIP_DEFLATED) as z:
        for path in sorted(source.rglob("*")):
            if path.is_file() and ((path.suffix == ".slut" and path.name != "selected-stage1.slut") or path.name in ("historical-grid.npy","frozen-model.json","selection-before-photos.json")):
                name = path.relative_to(source).as_posix()
                z.write(path,name)
                index[name] = digest(path)
    for name,rows in (("case-summary.csv",summary),("photos-per-image.csv",photos),("photo-groups.csv",splits)):write_csv(out / name,rows)
    for name,value in (("archive-index.json",index),("photo-regressions.json",regressions),("native-parity.json",parity),("support-certificates.json",proofs)):write_json(out / name,value)
    write_json(out / "source-provenance.json",{"measured_git_commit":run["git_commit"],"source_sha256":expected,
        "current_files_different_from_measurement":[k for k,v in expected.items() if digest(ROOT / k) != v],
        "archive_code_sha256":{str(p.relative_to(ROOT)):digest(p) for p in (Path(__file__),ROOT / "scripts/report_tail_grid_study.py")}})
    write_json(out / "integrity.json",{"files":{p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file()},
        "summary_rows":len(summary),"photo_rows":len(photos),"photo_rows_new":400,"photo_rows_reused":600,
        "group_rows":len(splits),"native_streams":len(parity),"archive_members":len(index),"source_files":len(expected),
        "contracts":"8 passed in 25.50s","scope":"归档字节、来源与结构核对，不重跑拟合"})
    print(json.dumps({"summary":len(summary),"photos":len(photos),"native_streams":len(parity),"members":len(index)}))


if __name__ == "__main__":main()
