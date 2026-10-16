"""Checkpoint and quiesce a verified live R38 controller before R50 takes over.

Workers are stopped before their fitting descendants, so termination is not
published as a candidate fit failure. All already-indexed receipts are retained.
Complete orphan receipts are recovered by metadata/model validation, no pixels.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "python"), str(ROOT / "artifacts/r18-tools/python")]
import psutil
from lutlab import casebook, corpus, reportio
from r41_freeze_combined_rules import runtime_kernel


def now():
    return datetime.now(timezone.utc).isoformat()


def alive(row):
    try:
        p = psutil.Process(row["pid"])
        return p.create_time() == row["create_time"] and p.is_running()
    except psutil.NoSuchProcess:
        return False


def describe(p):
    return {"pid": p.pid, "create_time": p.create_time(), "name": p.name(), "cmdline": p.cmdline()}


def contains_script(command, target):
    return any(Path(arg).resolve() == target.resolve() for arg in command if arg.lower().endswith(".py"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--controller", type=Path, required=True)
    args = parser.parse_args()
    matrix = ROOT / "artifacts/r29-matrix"
    lease = matrix / "phase-controller.lock"
    qualification_path = ROOT / "artifacts/r50-case-shard-qualification/stage.json"
    qualification = reportio.read_json(qualification_path)
    if not qualification["pass"] or qualification["fresh_native_full_cubes"] != 2 or qualification["reused_receipts"] != 52:
        raise RuntimeError("case sharding has not passed its declared qualification")
    for name, digest in qualification["source_sha256"].items():
        if corpus.digest_file(ROOT / name) != digest:
            raise RuntimeError("qualified scheduling source changed")
    for name, digest in qualification["binary_sha256"].items():
        if corpus.digest_file(Path(name)) != digest:
            raise RuntimeError("qualified native binary changed")
    old = reportio.read_json(args.controller)
    parent = psutil.Process(old["controller_pid"])
    parent_row = describe(parent)
    if (not contains_script(parent_row["cmdline"], ROOT / "scripts/r38_parallel_phases.py")
            or reportio.read_json(lease)["pid"] != parent.pid):
        raise RuntimeError("the live process is not the expected sole writer")
    roots = []
    descendants = {}
    for phase, item in old["children"].items():
        if item.get("status") != "running":
            continue
        try:
            p = psutil.Process(item["pid"])
        except psutil.NoSuchProcess:
            continue
        row = describe(p)
        if (p.ppid() != parent.pid or not contains_script(row["cmdline"], ROOT / "scripts/r38_frozen_worker.py")
                or row["cmdline"] != item["command"]):
            raise RuntimeError("worker identity/tree does not match the verified controller")
        roots.append({**row, "phase": phase})
        for child in p.children(recursive=True):
            try:
                child_row = describe(child)
                descendants[child.pid] = child_row
            except psutil.NoSuchProcess:
                pass
    if not roots:
        raise RuntimeError("no live owned workers to migrate; inspect the terminal controller instead")
    folder = ROOT / "artifacts/r50-case-migration" / uuid.uuid4().hex[:12]
    folder.mkdir(parents=True)
    path = folder / "stage.json"
    report = {"started_utc": now(), "scope": __doc__, "pass": False, "old_controller": str(args.controller.resolve()),
              "qualification_sha256": corpus.digest_file(qualification_path), "parent": parent_row, "worker_roots": roots,
              "owned_descendants": list(descendants.values()), "snapshots": {}, "recovered": [],
              "new_pixel_executions": 0, "source_sha256": {Path(__file__).relative_to(ROOT).as_posix(): corpus.digest_file(Path(__file__))}}
    before = {}
    def capture(source, name):
        payload = source.read_bytes()
        target = folder / name
        target.write_bytes(payload)
        report["snapshots"][name] = {"path": str(target), "sha256": hashlib.sha256(payload).hexdigest()}
        return json.loads(payload)
    for phase in ("development", "calibration", "regression"):
        before[phase] = capture(matrix / (phase + ".json"), "before-" + phase + ".json")
    capture(ROOT / "datasets/problem16-v1/casebook/index.json", "before-canonical-index.json")
    capture(args.controller, "before-old-controller.json")
    reportio.write_report(path, report)
    try:
        # Stop all publication roots first. Any reparented fit process is then
        # killed only if the captured PID AND creation time still match.
        for row in roots:
            if alive(row):
                psutil.Process(row["pid"]).terminate()
        for row in reversed(list(descendants.values())):
            if alive(row):
                psutil.Process(row["pid"]).terminate()
        deadline = time.monotonic() + 90
        owned = [parent_row, *roots, *descendants.values()]
        while any(alive(row) for row in owned):
            if time.monotonic() > deadline:
                raise RuntimeError("captured owned process still live; do not start another writer")
            time.sleep(1)
        if lease.exists():
            raise RuntimeError("old controller stopped without releasing its lease; preserve and inspect")
        old_terminal = capture(args.controller, "terminal-old-controller.json")
        if old_terminal.get("pass") or not old_terminal.get("terminal_error"):
            raise RuntimeError("old controller has no expected explicit interruption outcome")
        report.update(all_captured_processes_confirmed_terminal=True, old_lease_released=True,
                      old_terminal_reason=old_terminal["terminal_error"])
        with lease.open("x", encoding="utf-8") as stream:
            json.dump({"pid": os.getpid(), "owner": "R50 checkpoint orphan-receipt recovery"}, stream)
        try:
            catalog = {row["id"]: row for row in reportio.read_json(ROOT / "datasets/problem16-v1/catalog.json")["cases"]}
            plan = reportio.read_json(ROOT / "datasets/problem16-v1/strategy-plan.json")
            book = casebook.Casebook(folder / "recovered-casebook")
            book.attach_catalog(ROOT / "datasets/problem16-v1/catalog.json", ROOT / "data/corpus-v1")
            states = {}
            for phase in before:
                state = capture(matrix / (phase + ".json"), "quiescent-" + phase + ".json")
                if any(state["observations"].get(key) != item for key, item in before[phase]["observations"].items()):
                    raise RuntimeError("an indexed completed candidate changed during stop")
                states[phase] = state
            for observation in (matrix / "cases").glob("*/*/observation.json"):
                case_id = observation.parent.parent.name
                case = catalog[case_id]
                phase = case["split"]
                if phase not in states:
                    continue
                profile, _, budget = observation.parent.name.rpartition("-m")
                if profile not in plan["profiles"] or int(budget) not in plan["sizes"]:
                    raise RuntimeError("undeclared output folder")
                key = f"{case_id}/{profile}/m{budget}"
                if key in states[phase]["observations"]:
                    continue
                value = reportio.read_json(observation)
                primary_path = casebook._path(value["evidence"][0]["path"])
                primary = reportio.read_json(primary_path)
                manifest_path = ROOT / "data/corpus-v1/cases" / case_id / "manifest.json"
                manifest = reportio.read_json(manifest_path)
                sources = [row["sha256"] for row in manifest["stages"]]
                if (value["case_id"] != case_id or value["profile"] != profile or value["m"] != [int(budget)] * 4
                        or value["source_sha256"] != sources or not value["correctness_pass"] or value["semantics"] != "independent"
                        or primary["frozen"] != states[phase]["frozen"] or primary["cube"] != value["cube"]
                        or primary["source_sha256"] != sources or not primary["inputs_unchanged"]
                        or primary["reference_sha256"] != manifest["composite"]["sha256"]
                        or primary["kind"] != "casebook_native_cube_screen_v1"
                        or runtime_kernel(primary["runtime"]) != value["kernel"]
                        or value["kernel"] != ("tri_float" if profile == "trilinear" else "tetra_avx2")
                        or primary["runtime"]["returncode"] or primary["runtime"]["executable_sha256"] != states[phase]["frozen"]["executable_sha256"]
                        or list(primary["runtime"]["models_sha256"].values()) != value["model_sha256"]):
                    raise RuntimeError("orphan is not a complete unchanged R29 native full-cube observation")
                source_dir = manifest_path.parent
                if ([corpus.digest_file(source_dir / f"lut{k}.lut256") for k in range(1, 5)] != sources
                        or corpus.digest_file(source_dir / "composite.lut256") != primary["reference_sha256"]):
                    raise RuntimeError("orphan original inputs changed")
                identifier = book.record(observation)
                item = {"status": "screened", "observation_id": identifier, "path": str(observation),
                        "sha256": corpus.digest_file(observation), "cube_mean": value["cube"]["mean"], "cube_max": value["cube"]["max"]}
                states[phase]["observations"][key] = item
                report["recovered"].append({"phase": phase, "key": key, **item})
            for phase, state in states.items():
                if any(row["phase"] == phase for row in report["recovered"]):
                    state.setdefault("checkpoint_recoveries", []).append({"stage": str(path), "scope": "complete receipt recovered; no pixel rerun"})
                    reportio.write_report(matrix / (phase + ".json"), state)
                capture(matrix / (phase + ".json"), "after-" + phase + ".json")
            report["phase_observations"] = {phase: len(state["observations"]) for phase, state in states.items()}
        finally:
            lease.unlink()
        for name, digest in qualification["binary_sha256"].items():
            if corpus.digest_file(Path(name)) != digest:
                raise RuntimeError("native binary changed during checkpoint")
        report.update(pass_=True, inputs_unchanged=True, finished_utc=now(), ready_for_new_writer=True)
        report["pass"] = report.pop("pass_")
        reportio.write_report(path, report)
        print(json.dumps({"pass": True, "phase_observations": report["phase_observations"], "recovered_without_pixel_rerun": len(report["recovered"]), "stage": str(path)}))
    except BaseException as error:
        report.update(error={"type": type(error).__name__, "message": str(error)}, finished_utc=now())
        reportio.write_report(path, report)
        raise


if __name__ == "__main__":
    main()
