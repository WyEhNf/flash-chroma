"""归档单节点失败与双节点成功两个冻结时期；不重新优化或展开性能扫描。"""
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
from lutlab import error_analysis as ea, interp, io, study_provenance, tail_repair as tr


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8",newline="\n")


def write_csv(path,rows):
    with path.open("w",encoding="utf-8",newline="") as stream:
        writer = csv.DictWriter(stream,list(rows[0]),lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def archive_epoch(source,destination,plan_path,verification):
    destination.mkdir(parents=True,exist_ok=True)
    run = json.loads((source / "run.json").read_text(encoding="utf-8"))
    if run["identity_sha256"] != study_provenance.identity_digest(run["identity"]):
        raise ValueError("时期运行身份无效")
    expected = {k.replace("\\","/"):v for k,v in {**run["identity"]["source_sha256"],**run["identity"]["stage_source_sha256"]}.items()}
    with zipfile.ZipFile(source / "measured-source.zip") as archive:
        if set(archive.namelist()) != set(expected) or any(hashlib.sha256(archive.read(k)).hexdigest() != v for k,v in expected.items()):
            raise ValueError("实测源码快照不符")
    if digest(plan_path) != run["identity"]["plan_sha256"]:
        raise ValueError("冻结计划不符")
    proof = json.loads((source / verification).read_text(encoding="utf-8"))
    if not proof["verified"] or proof["external_dependencies_loaded"] or any(digest(source / k) != v for k,v in proof["input_sha256"].items()):
        raise ValueError("独立标准库复核未通过或输入不同")
    files = [source/name for name in ("run.json","results.json","selection.json","full-domain.json","negative-control.json",
        "inventory.json","fixed-guards.json","measured-source.zip")] + sorted(source.glob("round*.json"))
    if (source / "warm-start.json").exists():
        files.append(source / "warm-start.json")
    for path in files:
        shutil.copyfile(path,destination / path.name)
    shutil.copyfile(plan_path,destination / "plan.json")
    shutil.copyfile(source / verification,destination / "certificate-verification.json")
    write_json(destination / "source-provenance.json",{"measured_git_commit":run["git_commit"],"source_sha256":expected,
        "current_files_different_from_measurement":[k for k,v in expected.items() if digest(ROOT / k) != v],
        "scope":"实测快照逐文件核对原始run身份；当前源的后续扩展/日志修补不冒充旧测量"})
    return json.loads((source / "results.json").read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--single",type=Path,required=True)
    parser.add_argument("--joint",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True,exist_ok=True)
    single = archive_epoch(args.single,out / "single",ROOT / "experiments/full-domain-guard-v1.json","certificate-verification-portable.json")
    joint = archive_epoch(args.joint,out / "joint",ROOT / "experiments/full-domain-joint-v2.json","certificate-verification.json")
    if single["training_feasible"] or not joint["training_feasible"] or joint["final"] is None:
        raise ValueError("两个时期的训练可行状态与声明不同")
    for name,path in (("single/experiment.log",ROOT / "artifacts/full-domain-guard-v1.log"),
        ("joint/experiment.log",ROOT / "artifacts/full-domain-joint-v2.log"),
        ("single/contract.log",ROOT / "artifacts/full-domain-guard-contract.log"),
        ("joint/contract.log",ROOT / "artifacts/full-domain-joint-contract.log"),
        ("single/certificate.log",ROOT / "artifacts/full-domain-certificate-v1-portable.log"),
        ("joint/certificate.log",ROOT / "artifacts/full-domain-certificate-v2.log"),
        ("certificate-verifier.py",ROOT / "scripts/verify_full_domain_guard.py")):
        shutil.copyfile(path,out / name)
    old = json.loads((ROOT / "report/data/tail-repair-v1/results.json").read_text(encoding="utf-8"))
    variants = {"baseline":joint["previous"]["baseline"],"pr14":joint["previous"]["selected"],"pr15":old["final"],"full_joint":joint["final"]}
    partition = json.loads((ROOT / "report/data/joint-box-v1/photo-partition.json").read_text(encoding="utf-8"))
    splits = {"training":[r["id"] for r in partition["training"]["images"]],"guard":[r["id"] for r in partition["guard"]["images"]],"audit":partition["audit_ids"]}
    rows,photos,groups = [],[],[]
    for name,value in variants.items():
        rows.append({"variant":name,**{"cube_"+k:value["cube"][k] for k in ("mean","rms","p99","max")},
            **{"photos_"+k:value["photos"][k] for k in ("mean","rms","worst_image_p99","max")},
            "provenance":"本轮新执行" if name == "full_joint" else "同输入/模型历史复用"})
        for row in value["photos"]["per_image"]:
            photos.append({"variant":name,"split":next(k for k,ids in splits.items() if row["image"] in ids),**row})
        for split,ids in splits.items():
            values = [r for r in value["photos"]["per_image"] if r["image"] in ids]
            groups.append({"variant":name,"split":split,"n":len(values),"mean":float(np.mean([r["mean"] for r in values])),
                "rms":float(np.sqrt(np.mean([r["rms"]**2 for r in values]))),"worst_image_mean":max(r["mean"] for r in values),
                "worst_image_p99":max(r["p99"] for r in values),"max":max(r["max"] for r in values)})
    comparisons,regressions = {},[]
    for reference in ("baseline","pr14","pr15"):
        a,b = variants[reference]["photos"]["per_image"],variants["full_joint"]["photos"]["per_image"]
        if [r["image"] for r in a] != [r["image"] for r in b]:
            raise ValueError("逐图比较的图片顺序/身份不同")
        comparisons[reference] = {k:{"better":sum(x[k]>y[k]+1e-12 for x,y in zip(a,b)),
            "equal":sum(abs(x[k]-y[k])<=1e-12 for x,y in zip(a,b)),"worse":sum(x[k]<y[k]-1e-12 for x,y in zip(a,b))} for k in ("mean","rms","p99","max")}
        for x,y in zip(a,b):
            for metric in ("mean","rms","p99","max"):
                if y[metric] > x[metric]+1e-12:
                    regressions.append({"reference":reference,"image":x["image"],"metric":metric,
                        "before":x[metric],"after":y[metric],"split":next(k for k,ids in splits.items() if x["image"] in ids)})
    domain = json.loads((args.joint / "full-domain.json").read_text(encoding="utf-8"))
    if (domain["prediction_sha256"] != joint["final"]["cube"]["prediction_sha256"]
            or domain["reference_sha256"] != joint["final"]["cube"]["reference_sha256"]
            or any(r["sha256"] != domain["prediction_sha256"] for r in joint["final"]["native_parity"])):
        raise ValueError("完整域缓存、重建与原生后端的字节绑定不同")
    comparisons["strict_full_domain_mean_decrease_proved"] = int(domain["final"]["sum_upper_q24"]) < int(domain["reference"]["sum_lower_q24"])
    for key,variant in (("reference","pr14"),("final","full_joint")):
        hist = np.zeros(len(ea.ROOT_DISTANCE),np.int64)
        for d,n in domain[key]["histogram"]:
            hist[d] = n
        derived = ea.hist_metrics(hist)
        if any(abs(derived[k]-variants[variant]["cube"][k]) > 1e-12 for k in ("mean","rms","p99","max")):
            raise ValueError("证书直方图与完整色域重建指标不一致")
    comparisons["mean_ratio_vs_pr14"] = variants["full_joint"]["cube"]["mean"]/variants["pr14"]["cube"]["mean"]
    write_json(out / "comparisons.json",comparisons)
    write_csv(out / "case-summary.csv",rows)
    write_csv(out / "photos-per-image.csv",photos)
    write_csv(out / "image-regressions.csv",regressions)
    write_csv(out / "photo-split-summary.csv",groups)
    write_json(out / "native-parity.json",joint["final"]["native_parity"])
    # 对唯一剩余RGB重放主节点/帮手/联合反事实；完整域主节点证据来自冻结v1。
    models = [io.load_sparse(args.single / f"repaired-stage{k+1}.slut") for k in range(4)]
    paired = joint["rounds"][0]["paired_search"]
    moves = [tr.Move(m["stage"]-1,m["node"],tuple(m["after"])) for m in paired["moves"]]
    point = np.asarray(json.loads((args.single / "selection.json").read_text(encoding="utf-8"))["remaining_training_rgb"],np.uint8)
    if point.shape != (1,3):
        raise ValueError("本期报告要求冻结检查点恰好剩余一个颜色")
    tables = [io.load_full(ROOT / r["path"].replace("\\","/"),mmap=True) for r in joint["references"]]
    target = ea.exact_chain(tables,point)
    cap = next(r["cap_squared"] for r in json.loads((ROOT / "report/data/tail-repair-v1/training-violations.json").read_text(encoding="utf-8"))["records"] if r["rgb"] == point[0].tolist())
    counterfactual = []
    for name,updates in (("warm",[]),("primary",moves[:1]),("helper",moves[1:]),("pair",moves)):
        changed = tr.clone(models)
        for move in updates:
            changed[move.stage].nodes.reshape(-1,3)[move.node] = move.value
        prediction = point.copy()
        for model in changed:
            prediction = interp.apply_tetra_q16(model,prediction)
        delta = prediction.astype(np.int32)-target.astype(np.int32)
        counterfactual.append({"variant":name,"rgb":point[0].tolist(),"reference":target[0].tolist(),
            "output":prediction[0].tolist(),"squared_error":int(np.sum(delta*delta)),"cap_squared":cap})
    write_json(out / "joint-counterfactual.json",{"records":counterfactual,"scope":"一个已知剩余颜色的独立整数重放；帮手的单独完整域收益未测，不假定可加性"})
    final_models = [io.load_sparse(args.joint / f"repaired-stage{k+1}.slut") for k in range(4)]
    initial_models = [io.load_sparse(args.joint / "input-models" / f"selected-stage{k+1}.slut") for k in range(4)]
    write_json(out / "model-provenance.json",{"joint_model_sha256":{f"repaired-stage{k+1}.slut":digest(args.joint / f"repaired-stage{k+1}.slut") for k in range(4)},
        "changed_nodes":[int(np.count_nonzero(np.any(a.nodes != b.nodes,axis=3))) for a,b in zip(initial_models,final_models)],
        "changed_components":[int(np.count_nonzero(a.nodes != b.nodes)) for a,b in zip(initial_models,final_models)],
        "axis_tables_unchanged":all(all(np.array_equal(x,y) for x,y in zip(a.tables(),b.tables())) for a,b in zip(initial_models,final_models))})
    plt.rcParams.update({"font.family":"Microsoft YaHei","axes.unicode_minus":False,"font.size":10})
    fig,axes = plt.subplots(1,2,figsize=(12.5,4.8),constrained_layout=True)
    names = ["PR14联合","单节点停滞（不可行）","PR15旧修复","双节点全域保护"]
    means = [variants["pr14"]["cube"]["mean"],json.loads((args.single / "full-domain.json").read_text())["final"]["mean_lower"],
             variants["pr15"]["cube"]["mean"],variants["full_joint"]["cube"]["mean"]]
    axes[0].scatter(means,np.arange(4),s=65,color=["#3977aa","#999999","#c35d4f","#23826b"])
    axes[0].axvline(means[0]*1.005,color="#c35d4f",linestyle="--",label="PR14×1.005预算")
    axes[0].set(yticks=np.arange(4),yticklabels=names,xlabel="完整256³ mean RGB距离",title="预算不放宽，保留单节点失败结果")
    axes[0].legend(fontsize=8)
    for name,label,offset in (("pr14","PR14",(5,8)),("pr15","PR15",(-10,8)),("full_joint","本轮双节点",(5,8))):
        x,y = variants[name]["cube"]["mean"],variants[name]["cube"]["max"]
        axes[1].scatter([x],[y],s=70)
        axes[1].annotate(label,(x,y),xytext=offset,textcoords="offset points")
    axes[1].set(xlabel="完整256³ mean",ylabel="完整256³ max",title="固定链全域指标改善；逐图仍有权衡")
    fig.savefig(out / "full-domain-joint.png",dpi=160)
    plt.close(fig)
    members = [(source / f"repaired-stage{k+1}.slut",label+f"/repaired-stage{k+1}.slut") for label,source in (("single",args.single),("joint",args.joint)) for k in range(4)]
    members += [(args.single/name,"single/"+name) for name in ("run.json","selection.json","full-domain.json")]
    index = {name:digest(path) for path,name in members}
    with zipfile.ZipFile(out / "models-and-checkpoints.zip","w",zipfile.ZIP_DEFLATED) as archive:
        for path,name in members:
            archive.write(path,name)
    with zipfile.ZipFile(out / "models-and-checkpoints.zip") as archive:
        if set(archive.namelist()) != set(index) or any(hashlib.sha256(archive.read(name)).hexdigest() != h for name,h in index.items()):
            raise AssertionError("模型/检查点归档哈希不同")
    write_json(out / "archive-index.json",index)
    write_json(out / "integrity.json",{"epochs":2,"new_photo_records":100,"reused_photo_records":300,"archive_members":len(index),
        "measured_source_snapshots_verified":True,"files":{str(p.relative_to(out)).replace("\\","/"):digest(p) for p in out.rglob("*") if p.is_file() and p.name != "integrity.json"},
        "scope":"两个时期来源/原始证据/独立代数证书/ZIP字节；不把单节点失败登记为完整验收"})
    print(json.dumps({"epochs":2,"photo_rows":len(photos),"archive_members":len(index),"joint_feasible":joint["training_feasible"]},ensure_ascii=False))


if __name__ == "__main__":
    main()
