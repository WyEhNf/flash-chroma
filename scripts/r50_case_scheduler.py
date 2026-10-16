"""Schedule whole-case R29 jobs with one canonical writer and bounded processes.

Only work placement changes. The original 5400 keys, source image, destination
model/cache paths, four native threads and all numerical calculations remain.
At most --jobs ordinary subprocesses run; no subagents or performance claims.
"""
from __future__ import annotations

import argparse
from collections import deque
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import casebook, corpus, reportio
from r38_parallel_phases import committed_receipt


def stamp():
    return datetime.now(timezone.utc).isoformat()


def make_job(folder, *, source, matrix, phase, ids, seed, plan, catalog, data, cpu, class_rule=None):
    folder.mkdir(parents=True)
    worker = ROOT / "scripts/r50_case_worker.py"
    publisher = ROOT / "python/lutlab/reportio.py"
    marker = reportio.read_json(source / "frozen-source.json")
    index = folder / "index.json"
    selected = {key: item for key, item in seed["observations"].items() if key.split("/")[0] in ids}
    # The old driver verifies this seed, including all normalized records, before
    # computing only missing cells. It owns a private Casebook, never the global.
    value = {key: item for key, item in seed.items() if key not in (
        "finished_utc", "finished_candidates", "execution_io_overlays", "scheduling_overlays")}
    value.update(observations=selected, phase_complete=False)
    reportio.write_report(index, value)
    job = {"schema": 1, "source_root": str(source), "numerical_source_image_sha256": marker["archive_sha256"],
           "worker_sha256": corpus.digest_file(worker), "reportio": str(publisher), "reportio_sha256": corpus.digest_file(publisher),
           "phase": phase, "case_ids": ids, "matrix": str(matrix), "index_path": str(index),
           "casebook": str(folder / "casebook"), "plan": str(plan), "catalog": str(catalog),
           "data": str(data), "cpu": str(cpu), "class_rule": str(class_rule) if class_rule else None}
    path = folder / "job.json"
    reportio.write_report(path, job)
    return path


def environment(source, folder):
    return {**os.environ, "PYTHONPATH": str(source / "python"), "GIT_CEILING_DIRECTORIES": str(ROOT),
            "JSHC_LOG_DIR": str(folder / "runlogs"), "JSHC_FULL_FIT_LIB": str(ROOT / "build-fit/libjshc_full_fit.dll"),
            "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OMP_NUM_THREADS": "1"}


def check_holdout(args):
    if "holdout" not in args.phases:
        return
    if not args.class_rule or not args.combined_class_rule:
        raise RuntimeError("both original frozen rules required before any held-out numerical job")
    combined = reportio.read_json(args.combined_class_rule)
    if (not combined["frozen_before_holdout"]
            or combined["baseline_plan_sha256"] != corpus.digest_file(args.plan)
            or combined["extension_plan_sha256"] != corpus.digest_file(ROOT / "datasets/problem16-v1/strategy-extension-r36.json")):
        raise RuntimeError("combined rule differs from the declared experiment")
    for role in ("baseline_development", "baseline_calibration", "extension_development", "extension_calibration"):
        item = combined["training_reports"][role]
        path = casebook._path(item["path"])
        if corpus.digest_file(path) != item["sha256"] or not reportio.read_json(path)["phase_complete"]:
            raise RuntimeError("full training is incomplete or changed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--matrix", type=Path, default=ROOT / "artifacts/r29-matrix")
    parser.add_argument("--casebook", type=Path, default=ROOT / "datasets/problem16-v1/casebook")
    parser.add_argument("--phases", nargs="+", default=["development", "calibration", "regression"],
                        choices=["development", "calibration", "regression", "holdout"])
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--plan", type=Path, default=ROOT / "datasets/problem16-v1/strategy-plan.json")
    parser.add_argument("--catalog", type=Path, default=ROOT / "datasets/problem16-v1/catalog.json")
    parser.add_argument("--data", type=Path, default=ROOT / "data/corpus-v1")
    parser.add_argument("--cpu", type=Path, default=ROOT / "build-r18-cpu/jshc.exe")
    parser.add_argument("--class-rule", type=Path)
    parser.add_argument("--combined-class-rule", type=Path)
    args = parser.parse_args()
    if args.jobs < 1 or args.jobs > 8 or len(set(args.phases)) != len(args.phases):
        parser.error("use one to eight jobs and unique phases")
    for name in ("source_root", "matrix", "casebook", "plan", "catalog", "data", "cpu"):
        setattr(args, name, getattr(args, name).resolve())
    check_holdout(args)
    marker = reportio.read_json(args.source_root / "frozen-source.json")
    for name, expected in marker["source_sha256"].items():
        if not marker["pass"] or corpus.digest_file(args.source_root / name) != expected:
            raise RuntimeError("numerical source image changed")
    plan = reportio.read_json(args.plan)
    catalog = reportio.read_json(args.catalog)
    if plan["total_candidates"] != 5400 or len(plan["profiles"]) != 9:
        raise RuntimeError("preserve the original declared baseline universe")
    folder = args.matrix / "case-controllers" / uuid.uuid4().hex[:12]
    folder.mkdir(parents=True)
    path = folder / "controller.json"
    files = [Path(__file__), ROOT / "scripts/r50_case_worker.py", ROOT / "scripts/r38_parallel_phases.py",
             ROOT / "python/lutlab/reportio.py", ROOT / "python/lutlab/casebook.py", ROOT / "python/lutlab/timingbook.py",
             ROOT / "python/lutlab/io.py", ROOT / "python/lutlab/entry.py"]
    hashes = {p.relative_to(ROOT).as_posix(): corpus.digest_file(p) for p in files}
    report = {"started_utc": stamp(), "scope": __doc__, "controller_pid": os.getpid(), "pass": False,
              "source_sha256": hashes, "numerical_source_image_sha256": marker["archive_sha256"],
              "full_plan_candidates": 5400, "combined_declared_candidates": 7917, "jobs_limit": args.jobs,
              "jobs": {}, "imported_observations": 0, "timing_is_benchmark": False, "full_user_goal_complete": False}
    reportio.write_report(path, report)
    lease = args.matrix / "phase-controller.lock"
    with lease.open("x", encoding="utf-8") as stream:
        json.dump({"pid": os.getpid(), "owner": "R50 case-sharded original baseline", "controller": str(path)}, stream)
    running = {}
    seen = {}
    states = {}
    try:
        book = casebook.Casebook(args.casebook)
        book.attach_catalog(args.catalog, args.data)
        expected = {}
        pending = deque()
        for phase in args.phases:
            state_path = args.matrix / (phase + ".json")
            if not state_path.exists():
                raise RuntimeError("bootstrap a phase with the unchanged driver before sharding")
            state = reportio.read_json(state_path)
            if (state["frozen"]["phase"] != phase or state["frozen"]["plan_sha256"] != corpus.digest_file(args.plan)
                    or state["frozen"]["catalog_sha256"] != corpus.digest_file(args.catalog)):
                raise RuntimeError("saved phase differs from the declared plan")
            for name, digest in state["frozen"]["source_sha256"].items():
                if corpus.digest_file(args.source_root / name) != digest:
                    raise RuntimeError("saved phase belongs to another numerical source")
            if (state["frozen"]["executable_sha256"] != corpus.digest_file(args.cpu)
                    or state["frozen"]["inspection_sha256"] != corpus.digest_file(args.data / "inspection.json")):
                raise RuntimeError("saved native/data epoch changed")
            ids = [c["id"] for c in catalog["cases"] if c["split"] == phase]
            keys = {f"{case}/{profile}/m{m}" for case in ids for profile in plan["profiles"] for m in plan["sizes"]}
            if not set(state["observations"]) <= keys or state["phase_expected_candidates"] != len(keys):
                raise RuntimeError("saved phase scope changed")
            if state["phase_complete"] != (set(state["observations"]) == keys):
                raise RuntimeError("saved completeness flag contradicts exact coverage")
            states[phase] = state
            expected[phase] = keys
            for case_id in ids:
                case_keys = {key for key in keys if key.split("/")[0] == case_id}
                if not case_keys <= state["observations"].keys():
                    pending.append((phase, case_id))

        def commit(phase, key, item):
            identity = (phase, key)
            if identity in seen:
                if seen[identity] != item["sha256"]:
                    raise RuntimeError("completed candidate changed")
                return
            evidence = casebook._path(item["path"])
            if corpus.digest_file(evidence) != item["sha256"]:
                raise RuntimeError("candidate receipt changed")
            value = reportio.read_json(evidence)
            case_id, profile, budget = key.split("/")
            if (value["case_id"] != case_id or value["m"] != [int(budget[1:])] * 4
                    or value.get("profile", value.get("strategy")) != profile):
                raise RuntimeError("candidate receipt does not match its exact key")
            if not committed_receipt(book, item, evidence):
                if item["status"] == "screened":
                    if book.record(evidence) != item["observation_id"]:
                        raise RuntimeError("candidate observation identity changed")
                else:
                    book.record_failure(evidence)
            seen[identity] = item["sha256"]

        for phase, state in states.items():
            for key, item in state["observations"].items():
                commit(phase, key, item)
        report["resumed_observations"] = len(seen)
        report["initial_pending_case_jobs"] = len(pending)
        reportio.write_report(path, report)

        def collect():
            changed = set()
            for job_id, (child, handle, job_path, phase, case_id) in running.items():
                index = job_path.parent / "index.json"
                state = reportio.read_json(index)
                if state["frozen"] != states[phase]["frozen"]:
                    raise RuntimeError("shard changed the original numerical fingerprint")
                allowed = {key for key in expected[phase] if key.split("/")[0] == case_id}
                if not state["observations"].keys() <= allowed:
                    raise RuntimeError("shard crossed case ownership")
                overlay = state.get("scheduling_overlay")
                if overlay and (overlay["worker_sha256"] != hashes["scripts/r50_case_worker.py"]
                                or overlay["job_sha256"] != corpus.digest_file(job_path)):
                    raise RuntimeError("shard scheduling provenance changed")
                for key, item in state["observations"].items():
                    saved = states[phase]["observations"].get(key)
                    if saved is not None and saved != item:
                        raise RuntimeError("shard attempted to replace an immutable candidate")
                    if saved is None:
                        commit(phase, key, item)
                        states[phase]["observations"][key] = item
                        report["imported_observations"] += 1
                        changed.add(phase)
                row = report["jobs"][job_id]
                row["observations"] = len(state["observations"])
                if child.poll() is not None:
                    row.update(status="terminal", returncode=child.returncode)
                    if child.returncode or not state.get("shard_complete") or state["observations"].keys() != allowed:
                        raise RuntimeError("case job stopped or did not cover its complete assigned keys: " + job_id)
            for phase in changed:
                state = states[phase]
                state["phase_complete"] = state["observations"].keys() == expected[phase]
                if state["phase_complete"]:
                    state.update(finished_utc=stamp(), finished_candidates=len(state["observations"]))
                state.setdefault("scheduling_overlays", {})[folder.name] = {
                    "controller": str(path), "worker_sha256": hashes["scripts/r50_case_worker.py"],
                    "scope": "case partition and phase-index path only; numerical frozen fingerprint retained"}
                reportio.write_report(args.matrix / (phase + ".json"), state)
            if changed:
                reportio.write_report(book.root / "summary.json", book.summary())
            report["phase_observations"] = {phase: len(state["observations"]) for phase, state in states.items()}
            reportio.write_report(path, report)

        while pending or running:
            collect()
            for job_id in [name for name, row in running.items() if row[0].poll() is not None]:
                running.pop(job_id)[1].close()
            while pending and len(running) < args.jobs:
                # A soft launch guard preserves 1.5 GiB for the host; it is not
                # an RSS limit or a claim that later allocations cannot grow.
                try:
                    import psutil
                    available = psutil.virtual_memory().available
                except ImportError:
                    raise RuntimeError("psutil is required for the memory-aware launch guard")
                if available < 1536 * 2 ** 20:
                    report["launch_wait"] = {"available_bytes": available, "reason": "host RAM reserve"}
                    break
                report.pop("launch_wait", None)
                phase, case_id = pending.popleft()
                job_id = phase + "--" + case_id
                job_path = make_job(folder / "jobs" / job_id, source=args.source_root, matrix=args.matrix,
                    phase=phase, ids=[case_id], seed=states[phase], plan=args.plan, catalog=args.catalog,
                    data=args.data, cpu=args.cpu, class_rule=args.class_rule)
                handle = (job_path.parent / "worker.log").open("wb")
                command = [sys.executable, str(ROOT / "scripts/r50_case_worker.py"), "--job", str(job_path)]
                child = subprocess.Popen(command, cwd=args.source_root, env=environment(args.source_root, job_path.parent),
                                         stdout=handle, stderr=subprocess.STDOUT)
                running[job_id] = (child, handle, job_path, phase, case_id)
                report["jobs"][job_id] = {"pid": child.pid, "command": command, "status": "running", "started_utc": stamp()}
                reportio.write_report(path, report)
            time.sleep(3)
        for name, expected_hash in hashes.items():
            if corpus.digest_file(ROOT / name) != expected_hash:
                raise RuntimeError("scheduler/validator source changed")
        if not all(states[phase]["phase_complete"] and states[phase]["observations"].keys() == expected[phase] for phase in args.phases):
            raise RuntimeError("not all original requested phase keys were completed")
        report.update(pass_=True, finished_utc=stamp(), completed_requested_phases=args.phases)
        report["pass"] = report.pop("pass_")
        reportio.write_report(path, report)
        print(json.dumps({"pass": True, "phase_observations": report["phase_observations"]}), flush=True)
    except BaseException as error:
        report.update(error={"type": type(error).__name__, "message": str(error)}, finished_utc=stamp())
        reportio.write_report(path, report)
        raise
    finally:
        for child, handle, *_ in running.values():
            if child.poll() is None:
                subprocess.run(["taskkill", "/PID", str(child.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                child.wait()
            handle.close()
        lease.unlink()


if __name__ == "__main__":
    main()
