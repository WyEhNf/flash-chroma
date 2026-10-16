"""本地三阶段工作流：隔离正确性检查→并行筛选→串行100图与四级复核。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, default=ROOT / "artifacts/local-lut-study/20261016")
parser.add_argument("--await-screen", action="store_true", help="等待已经启动的筛选进程，不重复启动")
args = parser.parse_args()
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, PYTHONPATH=str(ROOT / "python"), OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
           OMP_NUM_THREADS="4", NUMBA_NUM_THREADS="4", PYTHONIOENCODING="utf-8")
(ROOT / "tmp").mkdir(exist_ok=True)
test_dir = tempfile.mkdtemp(prefix="pipeline-tests-", dir=ROOT / "tmp")
with (out / "correctness-final.log").open("w", encoding="utf-8") as stream:
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", "--basetemp", test_dir,
        "tests/test_compatibility.py", "tests/test_chain_study.py"], cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
if result.returncode:
    raise SystemExit("正确性检查失败，详情见correctness-final.log")
print("格式/整数边界/统计正确性检查通过", flush=True)
workers, streams = [], []
if not args.await_screen:
    for shard in range(3):
        stream = (out / f"screen-{shard}.log").open("w", encoding="utf-8")
        streams.append(stream)
        workers.append(subprocess.Popen([sys.executable,"-u",str(ROOT / "scripts/study_worker.py"),"lutlab.compatibility","--phase","screen",
            "--shards","3","--shard",str(shard),"--extended","--output",str(out)], cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT))
started = time.monotonic()
last_count = -1
while True:
    reports = [json.loads(p.read_text(encoding="utf-8")) for p in (out / "luts").glob("*/result.json")]
    done = sum(r.get("screen_complete", False) for r in reports)
    if done != last_count:
        print(f"筛选进度：{done}/68 LUT，{sum(len(r['screen']) for r in reports)}条配置", flush=True)
        last_count = done
    if any(p.poll() not in (None, 0) for p in workers):
        raise SystemExit("筛选子进程失败，请查看对应日志")
    if done == 68 and all(p.poll() == 0 for p in workers):
        break
    if time.monotonic() - started > 7200:
        raise SystemExit("等待筛选超过两小时，保留检查点，不发布完成声明")
    time.sleep(10)
for stream in streams:
    stream.close()
# 串行计时前核对所有参考表与模型，拒绝损坏或被替换的检查点。
for report in reports:
    reference = out / "references" / (report["lut"]["sha256"][:12] + ".npy")
    expected = report["reference_sha256"]
    if hashlib.sha256(reference.read_bytes()).hexdigest() != expected:
        raise RuntimeError("参考表哈希不一致")
    checked = set()
    for row in report["screen"]:
        if row["status"] != "ok" or row["model"] in checked:
            continue
        checked.add(row["model"])
        if hashlib.sha256((out / row["model"]).read_bytes()).hexdigest() != row["model_sha256"]:
            raise RuntimeError("模型哈希不一致")
stages = [
    ("full", [str(ROOT / "scripts/study_worker.py"),"lutlab.compatibility","--phase","full","--extended","--output",str(out)]),
    ("chains", [str(ROOT / "scripts/study_worker.py"),"lutlab.study_chains","--input",str(out)]),
    ("cube", [str(ROOT / "scripts/check_full_cube_finalists.py"),"--input",str(out)]),
    ("screen-detail", [str(ROOT / "scripts/export_screen_per_image.py"),"--input",str(out)]),
    ("report", [str(ROOT / "scripts/report_local_lut_study.py"),"--input",str(out)]),
    ("audit", [str(ROOT / "scripts/audit_local_lut_study.py"),"--input",str(out)]),
]
for stage, command in stages:
    print(f"开始{stage}阶段；当前没有其他筛选进程运行", flush=True)
    with (out / f"{stage}.log").open("w", encoding="utf-8") as stream:
        subprocess.run([sys.executable,"-u",*command], cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT, check=True)
print("本地研究工作流已完成；未上传任何结果", flush=True)
