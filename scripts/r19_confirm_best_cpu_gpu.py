"""Independent paired confirmation of the fastest declared CPU and CUDA arms."""
from __future__ import annotations

import json
import os
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "python"), str(ROOT / "artifacts/r18-tools/python")]
from lutlab import metrics, performance, runtime


def main():
    directory = ROOT / "artifacts/r19-delivery/paired"
    primary_file = directory / "comparison.json"
    primary = json.loads(primary_file.read_text(encoding="utf-8"))
    if not primary.get("inputs_unchanged") or not all(row["bit_exact"] for row in primary["preflight"]):
        raise RuntimeError("completed primary comparison and output parity are required")
    os.environ.update(primary["environment"])
    for name in primary["cleared_environment"]:
        os.environ.pop(name, None)
    for path, digest in primary["input_and_executable_sha256"].items():
        if metrics.file_sha256(path) != digest:
            raise RuntimeError("primary input or binary changed")
    configurations = {name: primary["configurations"][name] for name in ("gather_batch_t16", "cuda_batch100")}
    baseline_command = primary["preflight"][0]["runtime"]["command"]
    models = [Path(path) for path in baseline_command[-4:]]
    images = Path(baseline_command[baseline_command.index("-l") + 1])
    report = {"purpose": "separate seven-pair confirmation comparing the fastest CPU arm from the fixed matrix with host-to-host CUDA",
              "selection_evidence_sha256": metrics.file_sha256(primary_file),
              "timing_metric": primary["timing_metric"], "excluded": primary["excluded"],
              "reference": "gather_batch_t16", "candidate": "cuda_batch100", "runs": []}
    ratios = []
    for pair in range(7):
        order = list(configurations)
        if pair % 2:
            order.reverse()
        times = {}
        for name in order:
            result = runtime.bench(models, images, reps=1, competition=True, **configurations[name])
            elapsed = result["set_ms_p50_rep"] if name == "gather_batch_t16" else result["set_host_wall_ms_p50"]
            report["runs"].append({"pair": pair, "order": order, "configuration": name,
                                   "host_to_host_ms": elapsed, "runtime": result})
            times[name] = elapsed
        ratios.append(times["gather_batch_t16"] / times["cuda_batch100"])
        print(f"[confirm] pair={pair} CPU16={times['gather_batch_t16']:.3f} CUDA={times['cuda_batch100']:.3f} ms/100", flush=True)
    report.update(performance._paired_statistics(ratios, 2026101520))
    report["median_ms_per_100"] = {name: statistics.median(row["host_to_host_ms"] for row in report["runs"]
                                                          if row["configuration"] == name) for name in configurations}
    for path, digest in primary["input_and_executable_sha256"].items():
        if metrics.file_sha256(path) != digest:
            raise RuntimeError("input or binary changed during confirmation")
    report["inputs_unchanged"] = True
    performance._write(directory / "best-cpu-gpu-confirmation.json", report)
    print(json.dumps(report["median_ms_per_100"], indent=2))


if __name__ == "__main__":
    main()
