"""Run frozen extension phases in isolated ordinary processes, never subagents.

Canonical publication belongs to r38_parallel_phases --extra-matrix. Each child
maintains its own case winners and immutable receipts. This controller only
owns child lifetimes/logs and declares its result independently of the baseline.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import corpus, reportio


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--phases", nargs="+", choices=["development", "calibration", "regression", "holdout"],
                        default=["development", "calibration", "regression"])
    parser.add_argument("--max-new-per-phase", type=int, default=0)
    parser.add_argument("--combined-class-rule", type=Path)
    args = parser.parse_args()
    if args.max_new_per_phase < 0 or len(set(args.phases)) != len(args.phases):
        parser.error("invalid work limit or duplicate phase")
    if "holdout" in args.phases and args.combined_class_rule is None:
        parser.error("holdout requires the combined frozen rule")
    source_root = args.source_root.resolve()
    marker = reportio.read_json(source_root / "frozen-source.json")
    if not marker["pass"]:
        raise RuntimeError("extension source image is unverified")
    for name, digest in marker["source_sha256"].items():
        if corpus.digest_file(source_root / name) != digest:
            raise RuntimeError("source image changed")
    output = ROOT / "artifacts/r36-extension"
    folder = output / "controllers" / uuid.uuid4().hex[:12]
    folder.mkdir(parents=True)
    result = folder / "controller.json"
    hashes = {name: corpus.digest_file(ROOT / name) for name in
              ("scripts/r36_run_phases.py", "python/lutlab/reportio.py")}
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__, "controller_pid": os.getpid(),
              "source_sha256": hashes, "frozen_source_epoch_sha256": marker["epoch_sha256"],
              "source_root": str(source_root), "children": {}, "pass": False, "timing_is_benchmark": False,
              "extension_candidates": 2517, "canonical_writer": "external R38 controller or collect-only import"}
    reportio.write_report(result, report)
    children = {}
    logs = []
    try:
        for phase in args.phases:
            matrix = output / (phase + ".json")
            if matrix.exists() and reportio.read_json(matrix)["phase_complete"]:
                report["children"][phase] = {"status": "already_complete", "returncode": 0}
                continue
            if (output / (phase + ".lock")).exists():
                raise RuntimeError("a phase lease already exists; inspect its actual owner before resuming")
            command = [sys.executable, str(source_root / "scripts/r36_strategy_extension.py"),
                       "--workspace", str(ROOT), "--phase", phase, "--output", str(output),
                       "--max-candidates", str(args.max_new_per_phase)]
            if args.combined_class_rule:
                command += ["--combined-class-rule", str(args.combined_class_rule)]
            log = folder / (phase + ".log")
            handle = log.open("wb")
            logs.append(handle)
            environment = {**os.environ, "PYTHONPATH": str(source_root / "python"), "GIT_CEILING_DIRECTORIES": str(ROOT),
                "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OMP_NUM_THREADS": "1",
                "JSHC_FULL_FIT_LIB": str(ROOT / "build-fit/libjshc_full_fit.dll"),
                "JSHC_LOG_DIR": str(output / "runlogs" / phase)}
            child = subprocess.Popen(command, cwd=source_root, env=environment, stdout=handle, stderr=subprocess.STDOUT,
                                     start_new_session=os.name != "nt")
            children[phase] = child
            report["children"][phase] = {"pid": child.pid, "command": command, "log": str(log), "status": "running"}
        reportio.write_report(result, report)
        previous = None
        while any(child.poll() is None for child in children.values()):
            counts = {}
            for phase, child in children.items():
                matrix = output / (phase + ".json")
                if matrix.exists():
                    state = reportio.read_json(matrix)
                    counts[phase] = len(state["observations"])
                if child.poll() is not None:
                    report["children"][phase].update(status="terminal", returncode=child.returncode)
            if counts != previous:
                report["phase_observations"] = counts
                print("[extension/phases] " + json.dumps(counts) + "; full extension 2517", flush=True)
                previous = counts
            reportio.write_report(result, report)
            time.sleep(3)
        counts = {}
        for phase, child in children.items():
            report["children"][phase].update(status="terminal", returncode=child.returncode)
            matrix = output / (phase + ".json")
            if matrix.exists(): counts[phase] = len(reportio.read_json(matrix)["observations"])
        for name, digest in hashes.items():
            if corpus.digest_file(ROOT / name) != digest:
                raise RuntimeError("extension controller/publisher changed")
        report.update(phase_observations=counts, finished_utc=datetime.now(timezone.utc).isoformat(),
                      pass_=all(row["returncode"] == 0 for row in report["children"].values()))
        report["pass"] = report.pop("pass_")
        reportio.write_report(result, report)
        if not report["pass"]:
            raise RuntimeError("an extension worker stopped; preserve its receipts and inspect its terminal log")
    finally:
        for child in children.values():
            if child.poll() is None:
                if os.name == "nt":
                    subprocess.run(["taskkill", "/PID", str(child.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    os.killpg(child.pid, signal.SIGTERM)
                child.wait()
        for handle in logs: handle.close()


if __name__ == "__main__":
    main()
