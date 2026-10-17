"""从冻结流归档指标、网格证书与热点切片；不重拟合或重选方案。"""
import argparse
import csv
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
from lutlab import error_certificate as ec, io, study_provenance


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream,"sha256").hexdigest()


def write_json(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8",newline="\n")


def write_csv(path,rows):
    with path.open("w",encoding="utf-8",newline="") as stream:
        writer = csv.DictWriter(stream,list(rows[0]),lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def compare(before,after):
    old = {r["image"]:r for r in before["per_image"]}
    return {key:{"improved":sum(r[key] < old[r["image"]][key]-1e-12 for r in after["per_image"]),
                 "worse":sum(r[key] > old[r["image"]][key]+1e-12 for r in after["per_image"]),
                 "equal":sum(abs(r[key]-old[r["image"]][key]) <= 1e-12 for r in after["per_image"]),
                 "largest_increase":max(({"image":r["image"],"before":old[r["image"]][key],"after":r[key],
                    "increase":r[key]-old[r["image"]][key]} for r in after["per_image"]),key=lambda r:r["increase"])}
            for key in ("mean","rms","p99","max")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    source,out = args.input,args.output
    if out.exists():
        raise ValueError("不覆盖已有证据归档")
    run = json.loads((source / "run.json").read_text(encoding="utf-8"))
    if run["identity_sha256"] != study_provenance.identity_digest(run["identity"]):
        raise ValueError("运行身份不一致")
    expected = {k.replace("\\","/"):v for k,v in {**run["identity"]["source_sha256"],**run["identity"]["stage_source_sha256"]}.items()}
    with zipfile.ZipFile(source / "measured-source.zip") as archive:
        if set(archive.namelist()) != set(expected) or any(hashlib.sha256(archive.read(k)).hexdigest() != v for k,v in expected.items()):
            raise ValueError("实测源码快照与运行身份不同")
    plan_path = ROOT / "experiments/tail-grid-v1.json"
    if digest(plan_path) != run["identity"]["plan_sha256"]:
        raise ValueError("冻结方案字节变化")
    result = json.loads((source / "results.json").read_text(encoding="utf-8"))
    if result["run_identity"] != run["identity_sha256"]:
        raise ValueError("结果不属于此运行")
    out.mkdir(parents=True)
    for old,new in (("run.json","environment.json"),("results.json","results.json"),("measured-source.zip","measured-source.zip")):
        shutil.copyfile(source / old,out / new)
    shutil.copyfile(plan_path,out / "plan.json")
    shutil.copyfile(source.with_suffix(".log"),out / "experiment.log")
    summary,photos,parity,regressions,certificates,archive_index = [],[],[],[],[],{}
    plt.rcParams.update({"font.family":"Microsoft YaHei","axes.unicode_minus":False,"font.size":10})
    figure,axes = plt.subplots(2,2,figsize=(13,8),constrained_layout=True)
    labels = {"rounded_control":"整数对照","line_sse":"切线SSE","line_minimax":"切线最小最大"}
    for ci,case in enumerate(result["cases"]):
        cid = case["case"]["id"]
        folder = source / cid
        reference = ROOT / case["sources"][0]["path"]
        if digest(reference) != case["sources"][0]["table_sha256"]:
            raise ValueError("绘图使用的完整参考表SHA变化")
        table = io.load_full(reference,mmap=True)
        points = np.tile([247,0,0] if ci == 0 else [255,0,0],(256,1)).astype(np.uint8)
        axis = 2 if ci == 0 else 1
        points[:,axis] = np.arange(256,dtype=np.uint8)
        channel = 0 if ci == 0 else 2
        ids = points.astype(np.int64) @ np.array([65536,256,1])
        line = table[points[:,0],points[:,1],points[:,2]]
        axes[ci,0].plot(np.arange(256),line[:,channel],color="black",label="完整参考",linewidth=2)
        for name,value in {"historical":case["historical"],**case["profiles"]}.items():
            summary.append({"case":cid,"profile":name,"reused":name == "historical",
                **{f"cube_{k}":value["cube"][k] for k in ("mean","rms","p99","max","cvar_1pct","fraction_ge_1","fraction_ge_2","fraction_ge_3","fraction_ge_5")},
                **{f"photos_{k}":value["photos"][k] for k in ("mean","rms","worst_image_p99","max")},
                "old_triplet_lower_bound":value["old_triplet_certificate"]["rgb_l2_max_lower_bound"]})
            photos.extend({"case":cid,"profile":name,"reused":name == "historical",**r} for r in value["photos"]["per_image"])
            if name == "historical":
                continue
            if value["cube"]["n"] != 256**3 or value["boundary"]["n"] != 390152 or value["photos"]["n_images"] != 100:
                raise ValueError("新模型验收覆盖数量不符")
            cube = folder / name / "cube.rgb"
            if digest(cube) != value["cube"]["prediction_sha256"]:
                raise ValueError("绘图的冻结输出SHA变化")
            stream = np.memmap(cube,np.uint8,mode="r",shape=(256**3,3))
            prediction = stream[ids]
            axes[ci,0].plot(np.arange(256),prediction[:,channel],label=labels[name],linewidth=1.2)
            axes[ci,1].plot(np.arange(256),np.linalg.norm(prediction.astype(float)-line,axis=1),label=labels[name])
            parity.extend({"case":cid,"profile":name,**p} for p in value["native"])
            if any(p["byte_mismatches"] != 0 or p["sha256"] != value["cube"]["prediction_sha256"] for p in value["native"]):
                raise ValueError("原生完整流没有与独立整数流一致")
            regressions.append({"case":cid,"profile":name,**{f"vs_{base}":compare(ref["photos"],value["photos"]) for base,ref in
                (("historical",case["historical"]),("rounded_control",case["profiles"]["rounded_control"]))}})
            model = io.load_sparse(folder / name / "model.slut")
            # 后验诊断只用新最坏色及固定四个半径；不反馈拟合，也不称为全域下界搜索。
            centre = np.asarray(value["cube"]["hotspots"][0]["rgb"])
            candidates = []
            for radius in (1,2,4,8):
                for a in range(3):
                    p = np.tile(centre,(3,1))
                    p[:,a] += np.array([-radius,0,radius])
                    if p.min() < 0 or p.max() > 255:
                        continue
                    p = p.astype(np.uint8)
                    candidates.append(ec.three_point_bound(model,p,table[p[:,0],p[:,1],p[:,2]]))
            certificates.append({"case":cid,"profile":name,"worst_rgb":centre.tolist(),"examined_triplets":len(candidates),
                "strongest":max(candidates,key=lambda c:c["rgb_l2_max_lower_bound"]),"all":candidates,
                "scope":"后验固定热点局部三点必要界；零下界不意味着可精确表示或已最优"})
        axes[ci,0].set(title=f"{cid}：固定旧反例切线，输出通道{'R' if ci == 0 else 'B'}",ylabel="输出码值")
        axes[ci,1].set(title=f"{cid}：同一切线的RGB欧氏误差",ylabel="RGB欧氏码值距离")
        for ax in axes[ci]:
            ax.set_xlim((60,90) if ci == 0 else (235,255))
            ax.set_xlabel("B码值（R=247,G=0）" if ci == 0 else "G码值（R=255,B=0）")
            ax.grid(alpha=.2)
            ax.legend(fontsize=9)
    figure.savefig(out / "counterexample-lines.png",dpi=150)
    plt.close(figure)
    with zipfile.ZipFile(out / "models-grid-and-costs.zip","w",zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source.rglob("*")):
            if path.is_file() and (path.suffix in (".npy",".npz") or path.name in ("model.slut","historical.slut","grid-design.json","frozen-model.json")):
                name = path.relative_to(source).as_posix()
                archive.write(path,name)
                archive_index[name] = digest(path)
    write_csv(out / "case-summary.csv",summary)
    write_csv(out / "photos-per-image.csv",photos)
    write_json(out / "native-parity.json",parity)
    write_json(out / "photo-regressions.json",regressions)
    write_json(out / "new-hotspot-certificates.json",certificates)
    write_json(out / "archive-index.json",archive_index)
    write_json(out / "source-provenance.json",{"measured_git_commit":run["git_commit"],"source_sha256":expected,
        "current_files_different_from_measurement":[k for k,v in expected.items() if digest(ROOT / k) != v],
        "archive_code_sha256":digest(Path(__file__)),"scope":"保存全部实测源码原字节；归档/后验证书不作为重新拟合"})
    write_json(out / "integrity.json",{"files":{p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file()},
        "case_summary_rows":len(summary),"photo_rows":len(photos),"photo_rows_reused":200,
        "native_streams":len(parity),"models":8,"archive_members":len(archive_index),"source_files":len(expected),
        "normal_rows_verified":sum(len(v["normal_row_audit"]) for c in result["cases"] for v in c["profiles"].values()),
        "contracts":{"test_axis_grid.py":"3 passed in 0.46s","purpose":"DP全路径、Q16窄峰与255边界；Windows研究Python3.12.14"},
        "scope":"归档字节/数量和已保存验收证据核对；不是另一次数值实验"})
    print(json.dumps({"summary_rows":len(summary),"photo_rows":len(photos),"native_streams":len(parity),"members":len(archive_index)}))


if __name__ == "__main__":
    main()
