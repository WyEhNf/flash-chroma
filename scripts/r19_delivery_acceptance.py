"""One frozen public-entry acceptance batch: three scenes, m17/m18, 100 frames."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import cache, metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu", type=Path, required=True)
    parser.add_argument("--cuda", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/r19-delivery")
    args = parser.parse_args()
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment.update(OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", OMP_NUM_THREADS="1")
    environment["PYTHONPATH"] = os.pathsep.join([str(ROOT / "python"), str(ROOT / "artifacts/r18-tools/python")])
    report = {"started_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "one fixed fit + verified cache + CPU/CUDA full-cube + 100-image batch",
        "threshold_note": "mean < 2 is illustrative; max and p99 diagnostics retained; official threshold unknown",
        "commands": [], "cases": []}
    for scenario in ("isp-0", "clip-7", "warp-7"):
        for m in (17, 18):
            source = ROOT / "artifacts/r17-algorithm" / scenario
            inputs = [source / f"lut{k}.lut256" for k in range(1, 5)]
            namespace = args.output / "models" / scenario / f"dp_jitter_m{m}"
            command = [sys.executable, "-m", "lutlab", "fit", "--scenario", scenario, "--m", str(m),
                "--method", "ls_tetra_jitter", "--grid", "dp", "--model-dir", str(namespace),
                "--inputs", *map(str, inputs)]
            started = time.perf_counter()
            process = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True,
                text=True, encoding="utf-8", errors="replace")
            log = args.output / f"fit-{scenario}-m{m}.log"
            log.write_text(process.stdout + process.stderr, encoding="utf-8")
            report["commands"].append({"command": command, "returncode": process.returncode,
                "external_wall_seconds": time.perf_counter() - started, "log": str(log)})
            process.check_returncode()
            entries = []
            for manifest in namespace.glob("*/*/manifest.json"):
                value = json.loads(manifest.read_text(encoding="utf-8"))
                entry = cache.inspect_entry(manifest.parent, value["identity"])
                if entry is not None and value["identity"]["source_sha256"] == cache.source_fingerprint():
                    entries.append(entry)
            if len(entries) != 1:
                raise RuntimeError(f"expected one current verified batch in {namespace}, got {len(entries)}")
            entry = entries[0]
            study = ROOT / f"artifacts/r18-algorithm/{scenario}/dp_jitter_m{m}"
            if any(path.read_bytes() != (study / path.name).read_bytes() for path in entry.paths):
                raise RuntimeError("public entry changed frozen R18 model bytes")
            target = args.output / f"acceptance-{scenario}-m{m}.json"
            command = [sys.executable, "-m", "lutlab", "accept", "--models", *map(str, entry.paths),
                "--full-luts", *map(str, inputs), "--reference", str(source / "composite.lut256"),
                "--images", str(ROOT / "artifacts/r17-acceptance/bench.txt"),
                "--cpu-executable", str(args.cpu.resolve()), "--cuda-executable", str(args.cuda.resolve()),
                "--threshold", "2", "--metric", "mean", "--output", str(target)]
            started = time.perf_counter()
            process = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True,
                text=True, encoding="utf-8", errors="replace")
            log = args.output / f"acceptance-{scenario}-m{m}.log"
            log.write_text(process.stdout + process.stderr, encoding="utf-8")
            report["commands"].append({"command": command, "returncode": process.returncode,
                "external_wall_seconds": time.perf_counter() - started, "log": str(log)})
            if process.returncode not in (0, 2) or not target.exists():
                process.check_returncode()
                raise RuntimeError("acceptance did not write a result")
            value = json.loads(target.read_text(encoding="utf-8"))
            if not value["structural_contract_pass"] or not value["backend_cube_sha256_equal"]:
                raise RuntimeError("structural contract or CPU/CUDA parity failed")
            report["cases"].append({"scenario": scenario, "m": m, "models": list(map(str, entry.paths)),
                "acceptance": str(target), "acceptance_sha256": metrics.file_sha256(target),
                "public_models_match_study": True, "local_mean_gate_pass": value["pass"]})
            (args.output / "acceptance-suite.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print(f"[delivery] {scenario}/m{m}: structural+parity pass; local mean gate={value['pass']}", flush=True)
    report["finished_utc"] = datetime.now(timezone.utc).isoformat()
    report["structural_and_parity_pass"] = True
    (args.output / "acceptance-suite.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
