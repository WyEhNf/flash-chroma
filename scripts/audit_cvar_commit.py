"""校验CVaR阶段归档、复用标记及实测源码，解压后用标准库复核证书。"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def load(path):return json.loads(path.read_text(encoding="utf-8"))
def digest(data):return hashlib.sha256(data).hexdigest()


def extract(archive,index,destination):
    destination.mkdir(parents=True)
    with zipfile.ZipFile(archive) as z:
        if set(z.namelist()) != set(index) or len(z.namelist()) != len(index):raise ValueError("归档成员不完整或重复")
        for name,h in index.items():
            data = z.read(name)
            if digest(data) != h:raise ValueError("归档成员哈希不符")
            path = (destination / name).resolve()
            if not path.is_relative_to(destination.resolve()):raise ValueError("归档成员越出目标目录")
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,default=ROOT / "report/data/cvar-commit-v1")
    parser.add_argument("--output",type=Path,default=ROOT / "artifacts/cvar-commit-roundtrip-v1")
    args = parser.parse_args()
    if args.output.exists() or (args.input / "archive-audit.json").exists():raise ValueError("不覆盖已有归档复核")
    args.output.mkdir(parents=True)
    reference = args.output / "warm"
    old = ROOT / "report/data/primary-budget-v1/constraints"
    extract(old / "evidence.zip",load(old / "archive-index.json"),reference)
    with zipfile.ZipFile(args.input / "verification-sources.zip") as z:
        for name in z.namelist():
            if Path(name).name != name:raise ValueError("验证器归档名称不合法")
            if z.read(name) != (ROOT / "scripts" / name).read_bytes():raise ValueError("验证器源不同")
        z.extractall(args.output / "verifiers")
    records,source_maps = [],{}
    legacy = ["python/lutlab/interp.py","python/lutlab/io.py"]
    for arm in ("unprotected","guarded"):
        source = args.input / arm
        index = load(source / "archive-index.json")
        folder = args.output / arm
        extract(source / "evidence.zip",index,folder)
        run,result = [load(folder / n) for n in ("run.json","results.json")]
        expected = {n.replace("\\","/"):h for n,h in {**run["identity"]["source_sha256"],**run["identity"]["stage_source_sha256"]}.items()}
        line_only = []
        with zipfile.ZipFile(folder / "measured-source.zip") as z:
            if set(expected) != set(z.namelist()):raise ValueError("实测源码集合不同")
            for name,h in expected.items():
                data = z.read(name)
                if digest(data) != h:raise ValueError("实测源码快照哈希不符")
                frozen = subprocess.run(["git","show",run["git_commit"]+":"+name],cwd=ROOT,check=True,capture_output=True).stdout
                if frozen != data:
                    if name not in legacy or frozen.replace(b"\r\n",b"\n") != data.replace(b"\r\n",b"\n"):
                        raise ValueError("实测源码不属于记录的Git提交")
                    line_only.append(name)
                if arm == "guarded" and (ROOT / name).read_bytes() != data:raise ValueError("当前数值源码与实测字节不同")
        source_maps[arm] = expected
        for verifier in ("verify_quantile_constraints.py","verify_stability.py")+(("verify_cvar_guard.py",) if arm == "guarded" else ()):
            command = [sys.executable,"-I","-S",str(args.output / "verifiers" / verifier),"--input",str(folder),"--output",str(folder / ("roundtrip-"+verifier.replace(".py",".json")))]
            if verifier != "verify_quantile_constraints.py":command += ["--reference-run",str(reference)]
            completed = subprocess.run(command,cwd=ROOT,capture_output=True)
            (args.output / (arm+"-"+verifier+".log")).write_bytes(completed.stdout+completed.stderr)
            if completed.returncode:raise ValueError("归档解压后的标准库证书复核失败："+verifier)
            receipt = json.loads(completed.stdout.decode("ascii"))
            if not receipt["verified"] or receipt["external_dependencies_loaded"]:raise ValueError("解压复核未隔离外部数值依赖")
        case = result["cases"][0]
        model = folder / case["case"]["id"] / "repaired.slut"
        if digest(model.read_bytes()) != case["selection"]["model_sha256"]:raise ValueError("归档模型SHA不符")
        records.append({"arm":arm,"members":len(index),"git_commit":run["git_commit"],"roundtrip_original":True,"roundtrip_stability":True,
            "roundtrip_cvar":arm == "guarded","model_sha256":case["selection"]["model_sha256"],"legacy_line_ending_only_differences":line_only})
    old_map,new_map = source_maps["unprotected"],source_maps["guarded"]
    changed = [n for n in old_map.keys() & new_map.keys() if old_map[n] != new_map[n]]
    if set(changed) != {"python/lutlab/primary_batch.py","python/lutlab/quantile_repair.py","scripts/run_quantile_tail_study.py"}:
        raise ValueError("旧对照与新保护的数值源差异超出声明")
    if set(new_map)-set(old_map) != {"python/lutlab/cvar_guard.py"} or set(old_map)-set(new_map):raise ValueError("额外实测数值模块不同")
    with (args.input / "photos-per-image.csv").open(encoding="utf-8",newline="") as f:rows = list(csv.DictReader(f))
    if len(rows) != 400 or sum(r["reused_metrics"] == "False" for r in rows) != 100:raise ValueError("逐图新测与复用数量不符")
    parity = load(args.input / "native-parity.json")
    if len(parity) != 4 or sum(not p["reused"] for p in parity) != 2 or any(p["byte_mismatches"] for p in parity):raise ValueError("原生回执新旧数量或差分不符")
    diagnostic = load(args.input / "independent-diagnosis/analysis.json")
    final_sha = records[1]["model_sha256"]
    if digest((args.input / "independent-diagnosis/selected-block.slut").read_bytes()) != final_sha or len(diagnostic["subsets"]) != 7:
        raise ValueError("独立七子集最终模型不同")
    risk = load(args.input / "tail-risk.json")
    old_risk = load(ROOT / "report/data/primary-batch-v1/tail-risk.json")
    def normalized(records):
        return sorted((tuple(r["nodes"]),tuple(map(tuple,r["values"])),r["loss"],r["candidate_histogram_sha256"],r["tail_delta_lower_q24"],r["tail_delta_upper_q24"]) for r in records)
    if normalized(risk["candidates"]) != normalized(old_risk["candidates"]) or risk["candidate_count"] != 72:
        raise ValueError("新旧72候选的完整域尾部频数或缺口不同")
    selected = risk["selected"]
    if not selected["nonincrease_proved"] or selected["loss"] != 1585 or selected["nodes"] != sorted(m["node"] for m in diagnostic["moves"]):
        raise ValueError("所选候选尾部或缺口不符")
    subprocess.run(["git","diff","--exit-code","2b92cee","--","AGENTS.md"],cwd=ROOT,check=True,capture_output=True)
    output = {"verified":True,"records":records,"changed_common_numerical_sources":sorted(changed),"guarded_extra_source":"python/lutlab/cvar_guard.py",
        "current_guarded_numerical_sources_match_measured_bytes":True,"same_72_candidate_histograms_and_losses":True,
        "independent_seven_subsets_and_selected_model_match":True,"new_photo_rows":100,"reused_photo_rows":300,"new_native_receipts":2,"reused_native_receipts":2,
        "agents_unchanged":True,"auditor_sha256":digest(Path(__file__).read_bytes()),"python":sys.version,
        "scope":"成员/实测源/Git来源/旧证据复用及解压隔离证书复核，不重拟合、不重复完整数值终验；历史interp/io换行差异逐项披露"}
    (args.input / "archive-audit.json").write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(output,ensure_ascii=True))


if __name__ == "__main__":main()
