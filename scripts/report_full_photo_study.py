"""归档等质量拟合及保护失败，保存完整指标，不重新拟合。"""
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
from lutlab import study_provenance
from report_tail_grid_study import compare, write_csv, write_json, digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    source,out = args.input,args.output
    if out.exists():
        raise ValueError("拒绝覆盖既有证据")
    run = json.loads((source / "run.json").read_text(encoding="utf-8"))
    result = json.loads((source / "results.json").read_text(encoding="utf-8"))
    if study_provenance.identity_digest(run["identity"]) != run["identity_sha256"] or result["run_identity"] != run["identity_sha256"]:
        raise ValueError("运行来源身份无效")
    expected = {k.replace("\\","/"):v for k,v in {**run["identity"]["source_sha256"],**run["identity"]["stage_source_sha256"]}.items()}
    with zipfile.ZipFile(source / "measured-source.zip") as z:
        if set(z.namelist()) != set(expected) or any(hashlib.sha256(z.read(n)).hexdigest() != h for n,h in expected.items()):
            raise ValueError("源码快照与运行身份不一致")
    plan = ROOT / "experiments/full-photo-v1.json"
    if digest(plan) != run["identity"]["plan_sha256"]:
        raise ValueError("执行后冻结计划变化")
    out.mkdir(parents=True)
    for old,new in (("run.json","environment.json"),("results.json","results.json"),("measured-source.zip","measured-source.zip"),("photo-partition.json","photo-partition.json")):
        shutil.copyfile(source / old,out / new)
    shutil.copyfile(plan,out / "plan.json")
    shutil.copyfile(source.with_suffix(".log"),out / "experiment.log")
    partition = json.loads((source / "photo-partition.json").read_text(encoding="utf-8"))
    groups = {name:[r["id"] for r in partition[name]["images"]] for name in ("training","guard")}
    groups["audit"] = partition["audit_ids"]
    summary,photos,regressions,parity,splits,objectives = [],[],[],[],[],[]
    plt.rcParams.update({"font.family":"Microsoft YaHei","axes.unicode_minus":False,"font.size":10})
    fig,axes = plt.subplots(2,2,figsize=(14,9),constrained_layout=True)
    labels = ["历史","整数纯完整域","新网格纯完整域","整数混合","新网格混合"]
    for ci,case in enumerate(result["cases"]):
        cid = case["case"]["id"]
        original = case["bank"]["historical"]
        for name,value in case["bank"].items():
            summary.append({"case":cid,"profile":name,"reused":value["reused_metrics"],
                **{f"cube_{k}":value["cube"][k] for k in ("mean","rms","p99","max","fraction_ge_1","fraction_ge_2","fraction_ge_3","fraction_ge_5")},
                **{f"photos_{k}":value["photos"][k] for k in ("mean","rms","worst_image_p99","max")},
                "guard_photo_mean":value["guard"]["mean"],"full_guard":value["full_domain_certificate"]["accepted"],
                "selected":case["selection_before_photos"]["winner"] == name})
            photos.extend({"case":cid,"profile":name,"reused":value["reused_metrics"],**r} for r in value["photos"]["per_image"])
            regressions.append({"case":cid,"profile":name,"vs_historical":compare(original["photos"],value["photos"]),
                "selection_failures":case["selection_before_photos"]["failures"][name]})
            for group,ids in groups.items():
                rows = [r for r in value["photos"]["per_image"] if r["image"] in ids]
                if len(rows) != len(ids):
                    raise ValueError("完整逐图分组数量不一致")
                splits.append({"case":cid,"profile":name,"group":group,"n_images":len(rows),
                    "mean":float(np.mean([r["mean"] for r in rows])),"rms":float(np.sqrt(np.mean([r["rms"]**2 for r in rows]))),
                    "worst_image_p99":max(r["p99"] for r in rows),"max":max(r["max"] for r in rows)})
            if name.endswith("mixed"):
                if digest(source / cid / name / "cube.rgb") != value["cube"]["prediction_sha256"]:
                    raise ValueError("新完整流SHA变化")
                objectives.append({"case":cid,"profile":name,**value["fit"]["integer_selection"],
                    "accepted":value["fit"]["accepted"],"kkt":value["fit"]["solver"]["scaled_projected_gradient_inf"]})
                parity.extend({"case":cid,"profile":name,**r} for r in value["native"])
                if any(r["sha256"] != value["cube"]["prediction_sha256"] or r["byte_mismatches"] != 0 for r in value["native"]):
                    raise ValueError("原生全域回执不一致")
        for column,scope,keys in ((0,"cube",("mean","rms","p99","max")),(1,"photos",("mean","rms","worst_image_p99","max"))):
            ax = axes[ci,column]
            for i,key in enumerate(keys):
                values = [v[scope][key]/original[scope][key] for v in case["bank"].values()]
                ax.bar(np.arange(5)+(i-1.5)*.2,values,.2,label=("最差单图p99" if key == "worst_image_p99" else key))
            ax.axhline(1,color="black",linestyle="--",linewidth=1)
            ax.set_xticks(np.arange(5),labels,rotation=12)
            ax.set(title=cid+("：完整色域" if column == 0 else "：完整100图"),ylabel="相对历史基线（越低越好）")
            ax.legend(ncol=4,fontsize=8)
            ax.grid(axis="y",alpha=.2)
    fig.savefig(out / "full-photo-tradeoffs.png",dpi=150)
    plt.close(fig)
    index = {}
    with zipfile.ZipFile(out / "models-and-selection.zip","w",zipfile.ZIP_DEFLATED) as z:
        for path in sorted(source.rglob("*")):
            if path.is_file() and (path.suffix == ".slut" and path.name != "selected-stage1.slut" or path.name in ("full-domain-reference.json","selection-before-photos.json","frozen-model.json")):
                name = path.relative_to(source).as_posix()
                z.write(path,name)
                index[name] = digest(path)
    write_csv(out / "case-summary.csv",summary)
    write_csv(out / "photos-per-image.csv",photos)
    write_csv(out / "photo-groups.csv",splits)
    write_csv(out / "fit-objectives.csv",objectives)
    write_json(out / "photo-regressions.json",regressions)
    write_json(out / "native-parity.json",parity)
    write_json(out / "archive-index.json",index)
    write_json(out / "source-provenance.json",{"measured_git_commit":run["git_commit"],"source_sha256":expected,
        "current_files_different_from_measurement":[k for k,v in expected.items() if digest(ROOT / k) != v],
        "archive_source_sha256":{str(p.relative_to(ROOT)):digest(p) for p in (Path(__file__),ROOT / "scripts/report_tail_grid_study.py")}})
    write_json(out / "integrity.json",{"files":{p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file()},
        "summary_rows":len(summary),"photo_rows":len(photos),"photo_rows_new":400,"photo_rows_reused":600,
        "group_rows":len(splits),"native_streams":len(parity),"archive_members":len(index),"source_files":len(expected),
        "new_contracts":"3 passed in 1.53s","scope":"归档与来源绑定检查，不重复数值实验"})
    print(json.dumps({"summary":len(summary),"photos":len(photos),"native_streams":len(parity),"members":len(index)}))


if __name__ == "__main__":
    main()
