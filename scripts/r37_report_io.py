"""Reproduce the Windows report-sharing failure and recover a completed row.

The recovery requires a controller-confirmed failed phase writer whose actual
OS process is terminal. A temporary verification ledger checks immutable model,
source and execution evidence; the canonical controller remains its sole writer.
No fitting, native RGB mapping, or performance measurements are executed.
"""
from __future__ import annotations

import argparse
import ctypes as ct
from ctypes import wintypes as wt
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import threading
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import casebook, corpus, reportio


def process_alive(pid):
    kernel = ct.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
    kernel.OpenProcess.restype = wt.HANDLE
    kernel.GetExitCodeProcess.argtypes = [wt.HANDLE, ct.POINTER(wt.DWORD)]
    kernel.GetExitCodeProcess.restype = wt.BOOL
    kernel.CloseHandle.argtypes = [wt.HANDLE]
    kernel.CloseHandle.restype = wt.BOOL
    handle = kernel.OpenProcess(0x1000, False, pid)
    if not handle:
        error = ct.get_last_error()
        if error == 87:
            return False
        raise ct.WinError(error)
    try:
        code = wt.DWORD()
        if not kernel.GetExitCodeProcess(handle, ct.byref(code)):
            raise ct.WinError(ct.get_last_error())
        return code.value == 259
    finally:
        kernel.CloseHandle(handle)


def windows_gate(output):
    if os.name != "nt":
        raise RuntimeError("this stage needs actual Windows sharing semantics")
    path = output / "sharing-control.json"
    reportio.write_report(path, {"version": 0})
    kernel = ct.WinDLL("kernel32", use_last_error=True)
    kernel.CreateFileW.argtypes = [wt.LPCWSTR, wt.DWORD, wt.DWORD, ct.c_void_p, wt.DWORD, wt.DWORD, wt.HANDLE]
    kernel.CreateFileW.restype = wt.HANDLE
    kernel.CloseHandle.argtypes = [wt.HANDLE]
    kernel.CloseHandle.restype = wt.BOOL
    handle = kernel.CreateFileW(str(path), 0x80000000, 3, None, 3, 0x80, None)
    if handle == ct.c_void_p(-1).value:
        raise ct.WinError(ct.get_last_error())
    attempts = []
    errors = []
    finished = threading.Event()
    def writer():
        try:
            reportio.write_report(path, {"version": 1}, retry_events=attempts)
        except BaseException as error:
            errors.append(repr(error))
        finally:
            finished.set()
    thread = None
    try:
        replacement = output / "legacy-replacement.tmp"
        replacement.write_text('{"version":99}', encoding="utf-8")
        try:
            os.replace(replacement, path)
        except PermissionError as error:
            old_error = {"type": type(error).__name__, "winerror": getattr(error, "winerror", None)}
        else:
            raise RuntimeError("did not reproduce the real denied-replace condition")
        finally:
            replacement.unlink(missing_ok=True)
        thread = threading.Thread(target=writer)
        thread.start()
        time.sleep(.12)
        if finished.is_set():
            raise RuntimeError("writer failed or published while deletion was denied")
    finally:
        kernel.CloseHandle(handle)
        if thread is not None:
            thread.join(6.)
    if errors or not finished.is_set() or not attempts or reportio.read_json(path) != {"version": 1}:
        raise RuntimeError("bounded retry did not complete after release: " + repr(errors))
    snapshot = reportio.read_text(path)
    reportio.write_report(path, {"version": 2})
    if json.loads(snapshot) != {"version": 1}:
        raise RuntimeError("completed reader did not retain its copied snapshot")
    if reportio.read_json(path) != {"version": 2}:
        raise RuntimeError("new name did not reference the new complete JSON")
    try:
        reportio.write_report(output / "invalid-json.json", {"not_finite": float("nan")})
    except ValueError:
        pass
    else:
        raise RuntimeError("invalid JSON unexpectedly published")
    if (output / "invalid-json.json").exists() or list(output.glob("*.tmp")):
        raise RuntimeError("failed publication left an output or temporary file")
    return {"pass": True, "real_denied_replace": old_error, "bounded_retry_events": attempts,
            "reader_closes_before_parse": True, "copied_reader_keeps_old_snapshot": True,
            "invalid_json_rejected_and_temporary_cleaned": True}


def recover(output, controller_path, phase):
    controller = reportio.read_json(controller_path)
    worker = controller["children"][phase]
    if worker.get("status") != "terminal" or worker.get("returncode") in (None, 0) or process_alive(worker["pid"]):
        raise RuntimeError("phase writer is not authoritatively failed and terminal")
    if not process_alive(controller["controller_pid"]):
        raise RuntimeError("this recovery protocol requires the original live canonical controller")
    log = Path(worker["log"])
    diagnostic = reportio.read_text(log, encoding="utf-8", errors="replace")
    if "PermissionError" not in diagnostic or "WinError 5" not in diagnostic:
        raise RuntimeError("phase did not stop at the observed report-sharing failure")
    matrix = controller_path.parents[2] / (phase + ".json")
    before_text = reportio.read_text(matrix)
    report = json.loads(before_text)
    source_root = Path(controller["frozen_source_image"]["root"])
    for name, digest in report["frozen"]["source_sha256"].items():
        if corpus.digest_file(source_root / name) != digest:
            raise RuntimeError("frozen numerical source image changed")
    plan = reportio.read_json(ROOT / "datasets/problem16-v1/strategy-plan.json")
    catalog = reportio.read_json(ROOT / "datasets/problem16-v1/catalog.json")
    command = worker["command"]
    worker_book = Path(command[command.index("--casebook") + 1])
    worker_index = reportio.read_json(worker_book / "index.json")
    verifier = casebook.Casebook(output / "verification-book")
    recovered = []
    for case in catalog["cases"]:
        if case["split"] != phase:
            continue
        folder = ROOT / "data/corpus-v1/cases" / case["id"]
        manifest = reportio.read_json(folder / "manifest.json")
        sources = [row["sha256"] for row in manifest["stages"]]
        for m in plan["sizes"]:
            for profile in plan["profiles"]:
                key = f"{case['id']}/{profile}/m{m}"
                evidence = matrix.parent / "cases" / case["id"] / f"{profile}-m{m}" / "observation.json"
                if key in report["observations"] or not evidence.exists():
                    continue
                value = reportio.read_json(evidence)
                if (value["case_id"] != case["id"] or value["profile"] != profile or value["m"] != [m]*4
                        or value["source_sha256"] != sources):
                    raise RuntimeError("unindexed observation is bound to another candidate")
                primary_path = casebook._path(value["evidence"][0]["path"])
                primary = reportio.read_json(primary_path)
                if (primary["frozen"] != report["frozen"] or not primary["inputs_unchanged"]
                        or primary["reference_sha256"] != manifest["composite"]["sha256"]):
                    raise RuntimeError("unindexed observation lacks the exact completed epoch")
                if corpus.digest_file(Path(primary["runtime"]["executable"])) != primary["runtime"]["executable_sha256"]:
                    raise RuntimeError("frozen native binary changed")
                for path, digest in [(folder / f"lut{k}.lut256", digest) for k, digest in enumerate(sources, 1)]:
                    if corpus.digest_file(path) != digest:
                        raise RuntimeError("case source changed")
                if corpus.digest_file(folder / "composite.lut256") != primary["reference_sha256"]:
                    raise RuntimeError("reference bytes changed")
                verifier.add_case(case["id"], {name: case[name] for name in ("family","intensity","seed","split","tags","expected")}, sources)
                identifier = verifier.record(evidence)
                if identifier not in worker_index["cases"][case["id"]]["observations"]:
                    raise RuntimeError("worker did not commit this row before its report failure")
                stored = reportio.read_json(worker_book / "observations" / (identifier + ".json"))
                if stored["record_source"]["sha256"] != corpus.digest_file(evidence):
                    raise RuntimeError("worker observation was changed")
                report["observations"][key] = {"status": "screened", "observation_id": identifier,
                    "path": str(evidence), "sha256": corpus.digest_file(evidence),
                    "cube_mean": value["cube"]["mean"], "cube_max": value["cube"]["max"]}
                recovered.append({"key": key, **report["observations"][key]})
    if not recovered:
        raise RuntimeError("no completed unindexed rows were found")
    if process_alive(worker["pid"]) or reportio.read_text(matrix) != before_text:
        raise RuntimeError("a writer resumed during recovery; no phase index was changed")
    backup = output / (phase + "-before.json")
    backup.write_text(before_text, encoding="utf-8", newline="")
    record = {"controller_sha256_at_check": corpus.digest_file(controller_path), "failed_worker_pid": worker["pid"],
              "failed_worker_actually_terminal": True, "error_log_sha256": corpus.digest_file(log),
              "before_matrix_sha256": hashlib.sha256(before_text.encode("utf-8")).hexdigest(),
              "recovery_script_sha256": corpus.digest_file(Path(__file__)), "rows": recovered,
              "pixel_reexecutions": 0, "failed_worker_restarted": False}
    report.setdefault("metadata_recoveries", []).append(record)
    reportio.write_report(matrix, report)
    return {**record, "after_matrix_sha256": corpus.digest_file(matrix)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--controller", type=Path, required=True)
    parser.add_argument("--phase", choices=["development", "calibration", "regression"], required=True)
    args = parser.parse_args()
    output = ROOT / "artifacts/r37-report-io" / uuid.uuid4().hex[:12]
    output.mkdir(parents=True)
    source_names = ["python/lutlab/reportio.py", "python/lutlab/entry.py", "scripts/r37_report_io.py"]
    hashes = {name: corpus.digest_file(ROOT / name) for name in source_names}
    result = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__, "pass": False,
              "source_sha256": hashes, "timing_is_benchmark": False}
    reportio.write_report(output / "stage.json", result)
    result["windows_sharing_gate"] = windows_gate(output)
    reportio.write_report(output / "stage.json", result)
    result["recovery"] = recover(output, args.controller.resolve(), args.phase)
    for name, digest in hashes.items():
        if corpus.digest_file(ROOT / name) != digest:
            raise RuntimeError("recovery source changed")
    result.update(pass_=True, finished_utc=datetime.now(timezone.utc).isoformat())
    result["pass"] = result.pop("pass_")
    reportio.write_report(output / "stage.json", result)
    print(json.dumps({"pass": True, "result": str(output / "stage.json"),
                      "recovered_rows": len(result["recovery"]["rows"]), "pixel_reexecutions": 0}), flush=True)


if __name__ == "__main__":
    main()
