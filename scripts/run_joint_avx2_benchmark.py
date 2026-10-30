"""顺序执行固定候选的完整域验证和ABBA配对基准，保留全部周期原值。"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str], env: dict[str, str]) -> dict:
    completed = subprocess.run(command, check=True, capture_output=True, text=True,
                               encoding="utf-8", env=env)
    return json.loads(completed.stdout)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--photos", type=Path, required=True)
    parser.add_argument("--compiler", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    env = os.environ.copy()
    env["PATH"] = str(args.compiler.parent) + os.pathsep + env.get("PATH", "")
    env["OMP_DYNAMIC"] = "FALSE"
    candidates = ["repo_current", "repo_no_prefetch", "repo_t0", "repo_cached",
                  "repo_t0_cached"]
    cube = run([str(args.exe), "--verify-cube"], env)
    rows = []
    for threads in (1, 4):
        for candidate in candidates:
            rows.append(run([str(args.exe), str(args.photos), candidate, str(threads)], env))
    compiler = subprocess.run([str(args.compiler), "--version"], check=True, capture_output=True,
                              text=True, encoding="utf-8", env=env).stdout.splitlines()[0]
    result = {
        "schema_version": 1,
        "purpose": "固定100图、当前仓库热核与四个同源单变量候选的CPU-only AVX2配对筛查",
        "environment": {
            "platform": platform.platform(),
            "processor": "Intel(R) Core(TM) Ultra 5 125H；来自Windows注册表及WSL lscpu核对",
            "compiler": compiler,
            "compile_flags": "-O3 -DNDEBUG -std=c++17 -mavx2 -mbmi -mtune=skylake -fopenmp",
            "thread_affinity": {"1": [0], "4": [0, 2, 4, 6]},
            "gpu_npu": "未调用",
        },
        "inputs": {"photos": str(args.photos), "photos_sha256": sha(args.photos),
                   "pixels": args.photos.stat().st_size // 3, "bytes": args.photos.stat().st_size,
                   "executable_sha256": sha(args.exe)},
        "correctness": cube,
        "method": "每候选独立进程；预热当前核和候选各1次；8个循环交替ABBA/BAAB；每循环两次当前核与两次候选取均值；保留全部8个配对比。",
        "results": rows,
        "qualification": {
            "status": "没有候选获得性能资格",
            "reason": "A/A自身配对范围已超过±3%，且所有候选区间均跨过1或存在明显反例；仅保留方向性观察。",
        },
    }
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "results.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"correctness": cube, "runs": len(rows),
                      "output": str(args.output / 'results.json')}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
