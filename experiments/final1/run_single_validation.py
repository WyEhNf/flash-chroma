"""在已有 P 核锁内验证单文件等价性，并记录一次百图分段诊断。"""
from pathlib import Path
import hashlib
import json
import os
import platform
import re
import subprocess
import time

root = Path(__file__).resolve().parent
os.chdir(root)
zmx = root.parent
previous = zmx / "final1"
fd = int(os.environ["PCORE_LOCK_FD"])
allocation = json.loads(os.environ["PCORE_ALLOCATION"])
assert len(os.sched_getaffinity(0)) == 1
assert os.fstat(fd).st_ino == os.stat(allocation["lock"]).st_ino


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


old_receipt = json.loads((previous / "evidence/validation-receipt.json").read_text())
data = zmx / "p16-framework-bench-20261030-1200/data"
inputs = {name: sha(data / name) for name in old_receipt["inputs"]}
assert inputs == old_receipt["inputs"]
source_names = ["main.cpp", "stage_timing.cpp", "run_single_validation.py"]
sources = {name: sha(root / name) for name in source_names}
record = dict(complete=False, allocation=allocation, affinity=sorted(os.sched_getaffinity(0)),
              system=platform.platform(), compiler=subprocess.check_output(["g++", "--version"], text=True).splitlines()[0],
              sources=sources, inputs=inputs, commands=[], started_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))


def update():
    (root / "validation.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")


def run(command, name):
    start = time.monotonic()
    with (root / name).open("w") as output:
        process = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT, pass_fds=(fd,))
    record["commands"].append(dict(command=command, log=name, exit=process.returncode, seconds=time.monotonic()-start))
    update()
    if process.returncode:
        raise RuntimeError(name)
    print("完成：" + name, flush=True)


update()
try:
    assert sha(previous / "main.cpp") == "979f71f9f27d55229dfa194fd9697ee5e5f81b6d84e9373eae2e909a9c867e65"
    assert sha(previous / "flash_chroma_framework.hpp") == "d8f8665aeb05f45d5302db64cf747118114a644528f7a0cd39bad277ec32aae4"
    run(["g++", "-O2", "-std=c++17", "main.cpp", "-o", "lut3d"], "compile-main.log")
    run(["g++", "-O2", "-std=c++17", "stage_timing.cpp", "-o", "stage_timing"], "compile-diagnostic.log")
    run(["g++", "-O2", "-std=c++17", "-E", "-P", "main.cpp", "-o", "single.ii"], "preprocess-single.log")
    run(["g++", "-O2", "-std=c++17", "-E", "-P", str(previous / "main.cpp"), "-o", "previous.ii"], "preprocess-previous.log")
    record["preprocessed_equal"] = (root / "single.ii").read_bytes() == (root / "previous.ii").read_bytes()
    assert record["preprocessed_equal"]
    record["preprocessed_sha256"] = sha(root / "single.ii")
    record["binary_sha256"] = sha(root / "lut3d")
    record["previous_binary_sha256"] = sha(previous / "lut3d")
    record["binary_equal_to_previous"] = (root / "lut3d").read_bytes() == (previous / "lut3d").read_bytes()
    update()
    run(["./stage_timing", str(previous / "data100"), "100", "stage-timing.json"], "stage-timing.log")
    timing = json.loads((root / "stage-timing.json").read_text())
    old_quality = json.loads((previous / "evidence/correctness.json").read_text())
    expected = [row["quality"]["mean"] for row in old_quality["images"] if row["dataset"] == "photos100"]
    assert len(timing["per_image"]) == len(expected) == 100
    deviations = [abs(row["mean"]-value) for row, value in zip(timing["per_image"], expected)]
    assert max(deviations) < 1e-9
    record["max_photo_mean_deviation"] = max(deviations)
    run(["./lut3d", str(previous / "data"), "4"], "official-main.log")
    old_deltas = re.findall(r"Delta: [0-9.]+ ([0-9.]+)", (previous / "evidence/official-main.log").read_text())
    new_deltas = re.findall(r"Delta: [0-9.]+ ([0-9.]+)", (root / "official-main.log").read_text())
    assert old_deltas == new_deltas and len(new_deltas) == 4
    assert all(sha(root / name) == value for name, value in sources.items())
    assert all(sha(data / name) == value for name, value in inputs.items())
    record.update(complete=True, sources_and_inputs_unchanged=True, official_four_deltas_equal=True)
except Exception as error:
    record["error"] = str(error)
record["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
update()
print(json.dumps({key: value for key, value in record.items() if key not in ("sources", "inputs", "commands")}, ensure_ascii=False), flush=True)
raise SystemExit(0 if record["complete"] else 1)
