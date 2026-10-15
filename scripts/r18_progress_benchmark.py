"""One fixed R18 progress batch; exploratory timings, not official scores."""
from __future__ import annotations

import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "python"), str(ROOT / "artifacts/r18-tools/python")]
from lutlab import metrics
from phase_acceptance import verify_inputs


def main():
    out = ROOT / "artifacts/r18-progress"
    out.mkdir(parents=True, exist_ok=True)
    binary = ROOT / "build-r18-cpu/jshc.exe"
    inputs = ROOT / "artifacts/r17-acceptance"
    verify_inputs(inputs)
    models = [ROOT / f"artifacts/r17-algorithm/isp-0/baseline_m18/stage{k}.slut" for k in range(1, 5)]
    files = [binary, inputs / "input-manifest.json", *models]
    hashes = {str(path): metrics.file_sha256(path) for path in files}
    report = {"scope": "single fixed 100-frame exploratory batch, 4 requested CPU workers, five whole-set repetitions per configuration",
              "note": "configuration medians are not paired speedup evidence; fitting/loading/decode/encoding excluded from set time",
              "sha256": hashes, "environment": {key: os.environ.get(key) for key in
                  ("OMP_NUM_THREADS", "OMP_DYNAMIC", "OMP_PROC_BIND", "OMP_SCHEDULE", "JSHC_BLOCK_PIXELS")},
              "source_sha256": {str(path.relative_to(ROOT)): metrics.file_sha256(path)
                  for path in (ROOT / "cpp/src/main.cpp", ROOT / "cpp/src/lut.cpp", ROOT / "cpp/src/lut_simd_avx2.cpp")},
              "runs": []}
    configurations = [("tetra_avx2", False), ("tetra_avx2", True),
                      ("tetra_avx2_madd", True), ("tetra_avx2_scalar_gather", True),
                      ("tetra_avx2_exact_float", True)]
    for kernel, batch in configurations:
        command = [str(binary), "bench", "--competition", "-l", str(inputs / "bench.txt"),
                   "-k", kernel, "-t", "4", "-r", "5", *map(str, models)]
        if batch:
            command.insert(2, "--batch")
        started = time.perf_counter()
        process = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
        row = {"command": command, "returncode": process.returncode, "stdout": process.stdout,
               "stderr": process.stderr, "process_wall_seconds": time.perf_counter() - started}
        report["runs"].append(row)
        if process.returncode:
            (out / "cpu-benchmark.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            raise RuntimeError(process.stderr)
        row["result"] = value = json.loads(process.stdout)
        if value["images"] != 100 or len(value["set_ms_reps"]) != 5:
            raise RuntimeError("incomplete whole-set benchmark")
        print(kernel, "batch=" + str(batch), "set_ms=" + str(statistics.median(value["set_ms_reps"])), flush=True)
    verify_inputs(inputs)
    if any(metrics.file_sha256(path) != expected for path, expected in hashes.items()):
        raise RuntimeError("benchmark input or binary changed")
    report["inputs_unchanged"] = True
    (out / "cpu-benchmark.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
