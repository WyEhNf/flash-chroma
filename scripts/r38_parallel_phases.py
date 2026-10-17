"""Resume R29 with declared I/O repair, one canonical writer and no subagents.

The 5400 baseline cells, byte-preserved fitter, native binary and cache identities
remain unchanged. A metadata-only overlay retries Windows atomic publication.
R36 declares an additive matrix; any holdout now also needs its combined frozen
rule, so an early baseline-only rule cannot expose the shared holdout source.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import traceback
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import casebook, corpus, reportio


def committed_receipt(book, item, evidence):
    """Resume a previously validated canonical commit without refitting/rescanning.

    Check both normalized records and the canonical ID, not just file existence.
    Underlying model/execution integrity remains subject to the final book audit;
    this is the durable equivalent of this controller's in-memory `seen` set.
    """
    if item["status"] != "screened":
        return False
    identifier = item["observation_id"]
    target = book.root / "observations" / (identifier + ".json")
    if not target.exists():
        return False
    value = reportio.read_json(evidence)
    stored = reportio.read_json(target)
    normalized = {key: value for key, value in stored.items() if key not in ("observation_id", "record_source")}
    if (normalized != value or hashlib.sha256(corpus.canonical(value)).hexdigest() != identifier
            or stored.get("observation_id") != identifier
            or stored.get("record_source") != {"path": casebook._portable(evidence), "sha256": item["sha256"]}):
        raise RuntimeError("previous canonical receipt differs from immutable worker evidence")
    case = book.index["cases"][value["case_id"]]
    return identifier in case["observations"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--matrix", type=Path, default=ROOT / "artifacts/r29-matrix")
    parser.add_argument("--casebook", type=Path, default=ROOT / "datasets/problem16-v1/casebook")
    parser.add_argument("--phases", nargs="+", choices=["development", "calibration", "regression", "holdout"],
                        default=["development", "calibration", "regression"])
    parser.add_argument("--max-new-per-phase", type=int, default=270)
    parser.add_argument("--class-rule", type=Path)
    parser.add_argument("--combined-class-rule", type=Path)
    parser.add_argument("--extra-matrix", type=Path, action="append", default=[],
                        help="R36 phase index to import through the same sole canonical writer; may not exist yet")
    parser.add_argument("--collect-only", action="store_true", help="import current immutable receipts without starting fitting children")
    args = parser.parse_args()
    if args.max_new_per_phase < 0 or len(set(args.phases)) != len(args.phases):
        parser.error("invalid work limit or duplicate phase")
    if "holdout" in args.phases:
        if args.class_rule is None or args.combined_class_rule is None:
            parser.error("holdout needs both baseline and combined baseline+extension frozen class rules")
        combined = reportio.read_json(args.combined_class_rule)
        if (not combined["frozen_before_holdout"]
                or combined["baseline_plan_sha256"] != corpus.digest_file(ROOT / "datasets/problem16-v1/strategy-plan.json")
                or combined["extension_plan_sha256"] != corpus.digest_file(ROOT / "datasets/problem16-v1/strategy-extension-r36.json")):
            raise RuntimeError("combined rule is not bound to both declared plans")
        for role in ("baseline_development", "baseline_calibration", "extension_development", "extension_calibration"):
            evidence = combined["training_reports"][role]
            path = casebook._path(evidence["path"])
            if corpus.digest_file(path) != evidence["sha256"] or not reportio.read_json(path)["phase_complete"]:
                raise RuntimeError("combined rule lacks a complete immutable training phase")
    source_root = args.source_root.resolve()
    marker = reportio.read_json(source_root / "frozen-source.json")
    if not marker["pass"]:
        raise RuntimeError("unverified numerical source image")
    for name, digest in marker["source_sha256"].items():
        if corpus.digest_file(source_root / name) != digest:
            raise RuntimeError("numerical source image changed")
    args.matrix.mkdir(parents=True, exist_ok=True)
    lock = args.matrix / "phase-controller.lock"
    folder = args.matrix / "controllers" / uuid.uuid4().hex[:12]
    folder.mkdir(parents=True)
    files = [Path(__file__).resolve(), ROOT / "scripts/r38_frozen_worker.py", ROOT / "python/lutlab/reportio.py",
             ROOT / "python/lutlab/casebook.py", ROOT / "python/lutlab/timingbook.py", ROOT / "python/lutlab/entry.py"]
    hashes = {path.relative_to(ROOT).as_posix(): corpus.digest_file(path) for path in files}
    io_path = ROOT / "python/lutlab/reportio.py"
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__, "controller_pid": os.getpid(),
              "source_sha256": hashes, "full_plan_candidates": 5400, "max_new_per_phase": args.max_new_per_phase,
              "frozen_source_image": {"root": str(source_root), "archive_sha256": marker["archive_sha256"],
                  "public_cache_identity_probe": marker["public_cache_identity_probe"]},
              "children": {}, "merged_observations": 0, "pass": False, "full_user_goal_complete": False,
              "timing_is_benchmark": False, "io_overlay_is_numerical_change": False}
    report["resumed_committed_receipts"] = 0
    report["resume_integrity_scope"] = "canonical ID, normalized bytes and source receipt SHA; final underlying model/execution audit remains required"
    report.update(collect_only=args.collect_only, extra_matrix_paths=list(map(str, args.extra_matrix)),
                  extension_plan_candidates=2517 if args.extra_matrix else 0)
    if args.combined_class_rule:
        report["combined_class_rule_sha256"] = corpus.digest_file(args.combined_class_rule)
    path = folder / "controller.json"
    reportio.write_report(path, report)
    children = {}
    logs = []
    seen = {}
    with lock.open("x", encoding="utf-8") as stream:
        json.dump({"pid": os.getpid(), "started_utc": report["started_utc"], "owner": "R38 I/O-repaired baseline controller"}, stream)
    try:
        book = casebook.Casebook(args.casebook)
        book.attach_catalog(ROOT / "datasets/problem16-v1/catalog.json", ROOT / "data/corpus-v1")
        if args.extra_matrix:
            book.attach_catalog(ROOT / "datasets/problem16-axis-bins-v1/catalog.json", ROOT / "data/corpus-axis-bins-v1")
        def collect():
            counts = {}
            extras = {}
            added = False
            inputs = [(phase, args.matrix / (phase + ".json"), False) for phase in args.phases]
            inputs += [(str(path.resolve()), path.resolve(), True) for path in args.extra_matrix]
            for phase, matrix, extra in inputs:
                if not matrix.exists():
                    continue
                state = reportio.read_json(matrix)
                if extra:
                    if (state["extension_candidates"] != 2517
                            or state["frozen"]["plan_sha256"] != corpus.digest_file(ROOT / "datasets/problem16-v1/strategy-extension-r36.json")):
                        raise RuntimeError("extra matrix is not the declared extension")
                    if state["frozen"]["phase"] == "holdout" and args.combined_class_rule is None:
                        raise RuntimeError("cannot import holdout before the combined rule is supplied")
                    extras[phase] = len(state["observations"])
                else:
                    counts[phase] = len(state["observations"])
                for key, item in state["observations"].items():
                    identity = (phase, key)
                    if identity in seen:
                        if seen[identity] != item["sha256"]:
                            raise RuntimeError("completed observation changed")
                        continue
                    evidence = casebook._path(item["path"])
                    if corpus.digest_file(evidence) != item["sha256"]:
                        raise RuntimeError("immutable worker evidence changed")
                    if committed_receipt(book, item, evidence):
                        report["resumed_committed_receipts"] += 1
                    elif item["status"] == "screened":
                        if book.record(evidence) != item["observation_id"]:
                            raise RuntimeError("observation identity changed")
                    else:
                        book.record_failure(evidence)
                    seen[identity] = item["sha256"]
                    added = True
            if added:
                report.update(merged_observations=len(seen), phase_observations=counts, extra_matrix_observations=extras)
                reportio.write_report(book.root / "summary.json", book.summary())
                reportio.write_report(path, report)
                print("[phases/io] verified/imported " + json.dumps(counts) + "; full plan 5400", flush=True)
        for phase in ([] if args.collect_only else args.phases):
            matrix = args.matrix / (phase + ".json")
            if matrix.exists() and reportio.read_json(matrix)["phase_complete"]:
                report["children"][phase] = {"status": "already_complete", "returncode": 0}
                continue
            worker = args.matrix / "worker-casebooks" / marker["archive_sha256"][:16] / phase
            command = [sys.executable, str(ROOT / "scripts/r38_frozen_worker.py"), "--source-root", str(source_root),
                       "--reportio", str(io_path), "--reportio-sha256", hashes["python/lutlab/reportio.py"],
                       "--phase", phase, "--output", str(args.matrix), "--casebook", str(worker),
                       "--max-candidates", str(args.max_new_per_phase),
                       "--plan", str(ROOT / "datasets/problem16-v1/strategy-plan.json"),
                       "--catalog", str(ROOT / "datasets/problem16-v1/catalog.json"),
                       "--data", str(ROOT / "data/corpus-v1"), "--cpu", str(ROOT / "build-r18-cpu/jshc.exe")]
            if args.class_rule:
                command += ["--class-rule", str(args.class_rule)]
            log = folder / (phase + ".log")
            handle = log.open("wb")
            logs.append(handle)
            environment = {**os.environ, "PYTHONPATH": str(source_root / "python"), "GIT_CEILING_DIRECTORIES": str(ROOT),
                "JSHC_LOG_DIR": str(args.matrix / "frozen-runlogs" / phase),
                "JSHC_FULL_FIT_LIB": str(ROOT / "build-fit/libjshc_full_fit.dll"),
                "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OMP_NUM_THREADS": "1"}
            child = subprocess.Popen(command, cwd=source_root, env=environment, stdout=handle, stderr=subprocess.STDOUT,
                                     start_new_session=os.name != "nt")
            children[phase] = child
            report["children"][phase] = {"pid": child.pid, "command": command, "log": str(log), "status": "running"}
        reportio.write_report(path, report)
        collect()
        while any(child.poll() is None for child in children.values()):
            collect()
            for phase, child in children.items():
                if child.poll() is not None:
                    report["children"][phase].update(status="terminal", returncode=child.returncode)
            reportio.write_report(path, report)
            time.sleep(3)
        collect()
        for phase, child in children.items():
            report["children"][phase].update(status="terminal", returncode=child.returncode)
        for name, digest in hashes.items():
            if corpus.digest_file(ROOT / name) != digest:
                raise RuntimeError("controller/overlay source changed")
        report.update(finished_utc=datetime.now(timezone.utc).isoformat(), pass_=all(row["returncode"] == 0 for row in report["children"].values()))
        report["pass"] = report.pop("pass_")
        reportio.write_report(path, report)
        if not report["pass"]:
            raise RuntimeError("a worker stopped; preserve completed data and inspect its terminal log")
        print(json.dumps({"controller_chunk_pass": True, "phase_observations": report.get("phase_observations"), "full_plan_candidates": 5400}), flush=True)
    except BaseException as error:
        report.update(pass_=False, interrupted_utc=datetime.now(timezone.utc).isoformat(),
                      terminal_error={"type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc()})
        report["pass"] = report.pop("pass_")
        reportio.write_report(path, report)
        raise
    finally:
        for child in children.values():
            if child.poll() is None:
                if os.name == "nt":
                    subprocess.run(["taskkill", "/PID", str(child.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    os.killpg(child.pid, signal.SIGTERM)
                child.wait()
        for handle in logs:
            handle.close()
        lock.unlink()


if __name__ == "__main__":
    main()
