"""归档有限局部实验及历史对照，解压后独立重放，不重新拟合。"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile
ROOT = Path(__file__).resolve().parents[1]


def load(path):return json.loads(path.read_text(encoding="utf-8"))
def digest(data):return hashlib.sha256(data).hexdigest()
def write(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def pack(source,target):
    index = {}
    with zipfile.ZipFile(target,"x",zipfile.ZIP_DEFLATED) as z:
        for path in sorted(source.rglob("*")):
            if path.is_file() and path.suffix != ".rgb":
                name = path.relative_to(source).as_posix()
                z.write(path,name)
                index[name] = digest(path.read_bytes())
    return index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--first-failure",type=Path)
    parser.add_argument("--study",choices=("extreme","compensation","automatic","joint"),default="extreme")
    parser.add_argument("--prior-run",type=Path)
    parser.add_argument("--additional-contract-log",type=Path)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--roundtrip",type=Path,required=True)
    args = parser.parse_args()
    if args.study == "extreme" and args.first_failure is None:raise ValueError("原单元阶段必须保存首次失败")
    if args.output.exists() or args.roundtrip.exists():raise ValueError("不覆盖归档或解压复核")
    run,result,verification = [load(args.input / n) for n in ("run.json","results.json","verification.json")]
    identity = run["identity"]
    if digest(json.dumps(identity,sort_keys=True,allow_nan=False).encode()) != run["identity_sha256"] or result["run_identity"] != run["identity_sha256"]:
        raise ValueError("数值来源身份不符")
    if not verification["verified"] or verification["external_dependencies_loaded"] or verification["input_result_sha256"] != digest((args.input / "results.json").read_bytes()):
        raise ValueError("独立复核或输入绑定不符")
    if verification["verifier_sha256"] != digest((ROOT / "scripts/verify_extreme_cell.py").read_bytes()):raise ValueError("独立验证器已变化")
    for path,h in identity["parent_files"].items():
        if digest((ROOT / path).read_bytes()) != h:raise ValueError("已测父输入变化")
    for path,h in identity.get("frequency_cache",{}).items():
        if digest((ROOT / path).read_bytes()) != h:raise ValueError("复用频数的来源变化")
    for path,h in identity.get("local_reference_files",{}).items():
        if digest((ROOT / path).read_bytes()) != h:raise ValueError("冻结主改及复用证书的来源变化")
    line_only = []
    with zipfile.ZipFile(args.input / "measured-source.zip") as z:
        if set(z.namelist()) != set(identity["source_sha256"]):raise ValueError("实测数值源码集合不同")
        for name,h in identity["source_sha256"].items():
            data = z.read(name)
            if digest(data) != h or (ROOT / name).read_bytes() != data:raise ValueError("当前数值源码与实测字节不同")
            frozen = subprocess.run(["git","show",run["git_commit"]+":"+name],cwd=ROOT,check=True,capture_output=True).stdout
            if data != frozen:
                if name not in ("python/lutlab/interp.py","python/lutlab/io.py") or data.replace(b"\r\n",b"\n") != frozen.replace(b"\r\n",b"\n"):
                    raise ValueError("数值源不属于记录的Git提交")
                line_only.append(name)
    out = args.output
    out.mkdir(parents=True)
    index = pack(args.input,out / "evidence.zip")
    write(out / "archive-index.json",index)
    first_index = {}
    if args.first_failure is not None:
        first_index = pack(args.first_failure,out / "first-failure-evidence.zip")
        write(out / "first-failure-index.json",first_index)
    prior_index = {}
    same_prior_candidates = None
    if args.prior_run is not None:
        prior_result = load(args.prior_run / "results.json")
        prior_verification = load(args.prior_run / "verification.json")
        if not prior_verification["verified"] or prior_verification["external_dependencies_loaded"] or prior_verification["input_result_sha256"] != digest((args.prior_run / "results.json").read_bytes()):
            raise ValueError("首轮实验的独立复核或结果绑定不符")
        with zipfile.ZipFile(args.prior_run / "measured-source.zip") as prior_sources:
            if digest(prior_sources.read("scripts/verify_extreme_cell.py")) != prior_verification["verifier_sha256"]:raise ValueError("首轮复核没有对应原始验证源")
        current_by_name = {r["name"]:r for r in result["records"]}
        if set(current_by_name) != {r["name"] for r in prior_result["records"]}:raise ValueError("证书改进前后改变了候选队列")
        for old in prior_result["records"]:
            new = current_by_name[old["name"]]
            if (old["model_sha256"] != new["model_sha256"] or old["support_sha256"] != new["support_sha256"] or old["assessment"]["groups"] != new["assessment"]["groups"]
                    or old["assessment"]["full_domain"] != new["assessment"]["full_domain"] or old["assessment"]["cvar"] != new["assessment"]["cvar"]
                    or old["assessment"]["primary_loss"] != new["assessment"]["primary_loss"]):raise ValueError("证书改进却改变了模型或精确频数/指标")
        same_prior_candidates = True
        prior_index = pack(args.prior_run,out / "prior-run-evidence.zip")
        write(out / "prior-run-index.json",prior_index)
        shutil.copyfile(args.prior_run.with_suffix(".log"),out / "prior-experiment.log")
        shutil.copyfile(ROOT / "artifacts/local-compensation-initial-verify-v1.log",out / "prior-verification.log")
    if args.additional_contract_log is not None:shutil.copyfile(args.additional_contract_log,out / "contracts-signed-mean.log")
    for name in ("run.json","plan.json","certificate.json","verification.json","selection-before-photos.json"):
        shutil.copyfile(args.input / name,out / name)
    logs = [(args.input.with_suffix(".log"),"experiment.log")]
    if args.study == "extreme":logs += [(args.first_failure.with_suffix(".log"),"first-failure.log"),
        (ROOT / "artifacts/extreme-cell-contracts-v1.log","contracts-initial.log"),(ROOT / "artifacts/extreme-cell-contracts-fix-v1.log","contracts-fix.log"),
        (ROOT / "artifacts/extreme-cell-verify-v2.log","verification.log")]
    elif args.study == "compensation":logs += [(ROOT / "artifacts/local-compensation-contracts-v1.log","contracts.log"),(ROOT / "artifacts/local-compensation-verify-v1.log","verification.log")]
    elif args.study == "automatic":logs += [(ROOT / "artifacts/automatic-compensation-contracts-v1.log","contracts.log"),(ROOT / "artifacts/automatic-compensation-verify-v1.log","verification.log")]
    else:logs += [(ROOT / "artifacts/joint-interval-contracts-v1.log","contracts.log"),(ROOT / "artifacts/joint-interval-verify-v1.log","verification.log")]
    for path,target in logs:
        shutil.copyfile(path,out / target)
    with zipfile.ZipFile(out / "contracts-and-report-sources.zip","x",zipfile.ZIP_DEFLATED) as z:
        for commit,label in ((("bc5568b","initial"),("a86dba0","fix")) if args.study == "extreme" else ()):
            data = subprocess.run(["git","show",commit+":tests/test_local_minimax.py"],cwd=ROOT,check=True,capture_output=True).stdout
            z.writestr(label+"/test_local_minimax.py",data)
        for name in (("tests/test_joint_interval.py","tests/test_automatic_compensation.py","scripts/report_extreme_cell.py") if args.study == "joint" else
                ("tests/test_automatic_compensation.py","tests/test_local_minimax.py","tests/test_histogram_delta.py","scripts/report_extreme_cell.py") if args.study == "automatic" else
                ("tests/test_error_analysis.py","tests/test_local_minimax.py","scripts/report_extreme_cell.py") if args.study == "extreme" else
                ("tests/test_local_compensation.py","tests/test_local_minimax.py","tests/test_cvar_guard.py","tests/test_histogram_delta.py","tests/test_stability.py","scripts/report_extreme_cell.py")):
            z.write(ROOT / name,"current/"+name)
        if args.prior_run is not None:
            old_commit = load(args.prior_run / "run.json")["git_commit"]
            for name in ("tests/test_local_compensation.py","tests/test_local_minimax.py","tests/test_cvar_guard.py","python/lutlab/stability.py"):
                z.writestr("initial/"+name,subprocess.run(["git","show",old_commit+":"+name],cwd=ROOT,check=True,capture_output=True).stdout)
    before = load(args.input / "reference" / load(args.input / "plan.json")["case"] / "final-groups.json")
    inventory = load(args.input / "reference/photo-inventory.json")
    summaries,conflicts = [],[]
    for record in result["records"]:
        if not record["generated"]:continue
        a = record["assessment"]
        summaries.append({"name":record["name"],"changed_nodes":len(record["moves"]),"local_cell_max":record["cell_metrics"]["max"],
            **{k:a["cube_metrics"][k] for k in ("mean","rms","p99","max","cvar_1pct")},"primary_loss":a["primary_loss"],
            "full_sse_delta":a["full_sse_delta"],"guards_accepted":a["accepted"],"failed_conditions":len(a["failed"]),
            "metrics_scope":"完整非零支撑更新已验证完整频数；不是新增256³执行"})
        for g,after in enumerate(a["groups"]):
            if after["histogram"] == before["groups"][g]["histogram"]:continue
            old = before["groups"][g]
            conflicts.append({"name":record["name"],"group":g,"image":inventory["groups"][g]["image"],"kind":inventory["groups"][g]["kind"],
                "mean_before":old["metrics"]["mean"],"mean_after":after["metrics"]["mean"],"rms_before":old["metrics"]["rms"],"rms_after":after["metrics"]["rms"],
                "sse_delta":str(sum(d*n for d,n in after["histogram"])-sum(d*n for d,n in old["histogram"])),
                "primary_loss_before":sum(old["costs"]),"primary_loss_after":after["loss"]})
    for name,rows in (("candidate-summary.csv",summaries),("changed-groups.csv",conflicts)):
        with (out / name).open("w",encoding="utf-8",newline="") as f:
            fields = list(rows[0]) if rows else ["name","group","image","kind","mean_before","mean_after","rms_before","rms_after","sse_delta","primary_loss_before","primary_loss_after"]
            writer = csv.DictWriter(f,fields,lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    if args.study == "automatic":
        if (not verification["automatic"]["tree_complete"] or verification["automatic_verifier_sha256"] != digest((ROOT / "scripts/verify_automatic_compensation.py").read_bytes())):
            raise ValueError("自动完整候选树没有绑定独立复核源")
        shutil.copyfile(args.input / "automatic.json",out / "automatic.json")
    if args.study == "joint":
        if (not verification["joint_interval"]["verified"] or verification["joint_verifier_sha256"] != digest((ROOT / "scripts/verify_joint_interval.py").read_bytes())):
            raise ValueError("联合完整覆盖没有绑定独立复核源")
        shutil.copyfile(args.input / "joint-search.json",out / "joint-search.json")
        shutil.copyfile(args.input / "node-evidence.json",out / "node-evidence.json")
    if args.study in ("compensation","automatic","joint"):
        if not verification.get("selection_checked") or verification["interactions_checked"] != len(result["interactions"]):raise ValueError("补偿阶段未独立复核选择与交互")
        if args.study == "compensation":shutil.copyfile(args.input / "interactions.json",out / "interactions.json")
        write(out / "signed-mean-rechecks.json",[{"candidate":r["name"],**p} for r in result["records"] for p in r.get("signed_mean_rechecks",[])])
        if result["selection"]["selected"] is not None and not verification.get("full_stream_checked"):raise ValueError("新终态归档前未核对实际完整流")
        parent_case = next(c for c in load(args.input / "reference/results.json")["cases"] if c["case"]["id"] == load(args.input / "plan.json")["case"])
        profiles = [("baseline",parent_case["final"],True)]
        if result["selection"]["selected"] is not None:profiles += [("selected",result["final"],False)]
        photo_rows,split_rows,regressions,native = [],[],[],[]
        partition = load(args.input / "reference/photo-partition.json")
        splits = {"training":[v["id"] for v in partition["training"]["images"]],"selection":[v["id"] for v in partition["guard"]["images"]],"audit":partition["audit_ids"]}
        previous = {v["image"]:v for v in parent_case["final"]["photos"]["per_image"]}
        for name,value,reused in profiles:
            photo_rows += [{"profile":name,"reused":reused,**v} for v in value["photos"]["per_image"]]
            native += [{"profile":name,"reused":reused,**v} for v in value["native"]]
            for split,ids in splits.items():
                rows = [v for v in value["photos"]["per_image"] if v["image"] in ids]
                if len(rows) != len(ids):raise ValueError("完整照片分组清单不符")
                split_rows.append({"profile":name,"split":split,"reused":reused,"n_images":len(rows),"mean":math.fsum(v["mean"] for v in rows)/len(rows),
                    "rms":math.sqrt(math.fsum(v["rms"]**2 for v in rows)/len(rows)),"worst_image_p99":max(v["p99"] for v in rows),"max":max(v["max"] for v in rows)})
            regressions.append({"profile":name,"vs_baseline":{k:{"improved":sum(v[k] < previous[v["image"]][k]-1e-12 for v in value["photos"]["per_image"]),
                "worse":sum(v[k] > previous[v["image"]][k]+1e-12 for v in value["photos"]["per_image"]),
                "equal":sum(abs(v[k]-previous[v["image"]][k]) <= 1e-12 for v in value["photos"]["per_image"])} for k in ("mean","rms","p99","max")}})
        for name,rows in (("photos-per-image.csv",photo_rows),("photo-splits.csv",split_rows)):
            with (out / name).open("w",encoding="utf-8",newline="") as f:
                writer = csv.DictWriter(f,list(rows[0]),lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
        write(out / "photo-regressions.json",regressions)
        write(out / "native-parity.json",native)
    args.roundtrip.mkdir(parents=True)
    with zipfile.ZipFile(out / "evidence.zip") as z:
        if set(z.namelist()) != set(index) or len(z.namelist()) != len(index):raise ValueError("归档成员重复或遗漏")
        for name,h in index.items():
            data = z.read(name)
            if digest(data) != h:raise ValueError("归档成员字节不同")
            path = (args.roundtrip / name).resolve()
            if not path.is_relative_to(args.roundtrip.resolve()):raise ValueError("归档成员越界")
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(data)
    completed = subprocess.run([sys.executable,"-I","-S",str(ROOT / "scripts/verify_extreme_cell.py"),"--input",str(args.roundtrip),"--output",str(args.roundtrip / "roundtrip-verification.json")],cwd=ROOT,capture_output=True)
    (out / "roundtrip-verification.log").write_bytes(completed.stdout+completed.stderr)
    if completed.returncode:raise ValueError("解压后独立证书或局部重放失败")
    receipt = load(args.roundtrip / "roundtrip-verification.json")
    if not receipt["verified"] or receipt["external_dependencies_loaded"]:raise ValueError("解压后独立复核依赖外部数值库")
    shutil.copyfile(args.roundtrip / "roundtrip-verification.json",out / "roundtrip-verification.json")
    subprocess.run(["git","diff","--exit-code","876e15b","--","AGENTS.md"],cwd=ROOT,check=True,capture_output=True)
    write(out / "archive-audit.json",{"verified":True,"members":len(index),"first_failure_members":len(first_index),"prior_run_members":len(prior_index),"source_git_commit":run["git_commit"],
        "same_models_outputs_histograms_and_metrics_as_prior":same_prior_candidates,
        "current_numerical_sources_same":True,"legacy_line_ending_only_differences":line_only,"roundtrip_verified":True,
        "no_new_full_domain_execution":result["final"]["reused"],"selected":result["selection"]["selected"],"agents_unchanged":True,
        "archiver_sha256":digest(Path(__file__).read_bytes()),"scope":"归档来源/成员、首次失败和频数缓存保留；解压用已核同字节独立验证器及本机同字节完整源表重放；无新搜索/拟合"})
    write(out / "file-index.json",{p.relative_to(out).as_posix():digest(p.read_bytes()) for p in sorted(out.rglob("*")) if p.is_file()})
    print(json.dumps({"archived_members":len(index),"first_failure_members":len(first_index),"bytes":sum(p.stat().st_size for p in out.rglob("*") if p.is_file()),"roundtrip_verified":True},ensure_ascii=True))


if __name__ == "__main__":main()
