"""One staged scheduling qualification: 52 reused receipts and two full cubes.

No canonical matrix or book is written. Compare byte-preserved fitter identities,
model bytes, all full-cube metrics and all boundary probes against existing R29
results on two independent non-held-out source cases, using two ordinary jobs.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import casebook, corpus, io, reportio
from r50_case_scheduler import environment, make_job
from r50_case_worker import projection


def main():
    folder = ROOT / "artifacts/r50-case-shard-qualification"
    result_path = folder / "stage.json"
    if folder.exists():
        raise RuntimeError("preserve the existing qualification epoch")
    folder.mkdir()
    source = ROOT / "artifacts/r29-frozen-source/19c69a6a7554b9920301"
    source_marker = reportio.read_json(source / "frozen-source.json")
    driver = source / "scripts/r29_strategy_matrix.py"
    _, ast_hash = projection(driver)
    names = ["scripts/r50_case_worker.py", "scripts/r50_case_scheduler.py", "scripts/r50_validate_case_shards.py",
             "scripts/r38_parallel_phases.py", "python/lutlab/reportio.py", "python/lutlab/casebook.py"]
    hashes = {name: corpus.digest_file(ROOT / name) for name in names}
    binary_paths = [ROOT / "build-fit/libjshc_full_fit.dll", ROOT / "build-r18-cpu/jshc.exe"]
    binaries = {str(path): corpus.digest_file(path) for path in binary_paths}
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__, "pass": False,
              "source_sha256": hashes, "binary_sha256": binaries, "original_driver_sha256": corpus.digest_file(driver),
              "original_ast_sha256": ast_hash, "numerical_source_image_sha256": source_marker["archive_sha256"],
              "full_plan_candidates": 5400, "combined_declared_candidates": 7917,
              "fresh_native_full_cubes": 0, "reused_receipts": 0, "cases": [],
              "holdout_outputs_read": False, "canonical_mutations": 0, "timing_is_benchmark": False}
    reportio.write_report(result_path, report)
    jobs = []
    try:
        for phase, case_id in [("development", "gamma-mild-s0-677a6f0f"), ("calibration", "gamma-mild-s1-7fc3b60c")]:
            seed_path = ROOT / "artifacts/r29-matrix" / (phase + ".json")
            payload = seed_path.read_bytes()
            (folder / (phase + "-snapshot.json")).write_bytes(payload)
            seed = json.loads(payload)
            selected = {key: item for key, item in seed["observations"].items() if key.split("/")[0] == case_id}
            if len(selected) != 27 or any(item["status"] != "screened" for item in selected.values()):
                raise RuntimeError("the selected qualification case was not previously completed")
            missing_key = f"{case_id}/sample/m17"
            expected = selected.pop(missing_key)
            seed = {**seed, "observations": selected, "phase_complete": False}
            job_path = make_job(folder / phase, source=source, matrix=folder / "private-matrix", phase=phase,
                ids=[case_id], seed=seed, plan=ROOT / "datasets/problem16-v1/strategy-plan.json",
                catalog=ROOT / "datasets/problem16-v1/catalog.json", data=ROOT / "data/corpus-v1", cpu=binary_paths[1])
            log = (job_path.parent / "worker.log").open("wb")
            child = subprocess.Popen([sys.executable, str(ROOT / "scripts/r50_case_worker.py"), "--job", str(job_path)],
                cwd=source, env=environment(source, job_path.parent), stdout=log, stderr=subprocess.STDOUT)
            jobs.append((child, log, job_path, expected, missing_key, selected))
        while any(child.poll() is None for child, *_ in jobs):
            time.sleep(2)
        for child, handle, job_path, expected, missing_key, selected in jobs:
            handle.close()
            if child.returncode:
                raise RuntimeError("scheduling qualification child failed: " + str(job_path))
            state = reportio.read_json(job_path.parent / "index.json")
            if (state["phase_complete"] or not state["shard_complete"] or state["phase_expected_candidates"] != 1620
                    or state["shard_expected_candidates"] != 27 or len(state["observations"]) != 27
                    or state["scheduling_overlay"]["original_ast_sha256"] != ast_hash):
                raise RuntimeError("shard misrepresented global/local coverage or AST scope")
            if any(state["observations"][key] != item for key, item in selected.items()):
                raise RuntimeError("reused receipt changed")
            actual_item = state["observations"][missing_key]
            old = reportio.read_json(casebook._path(expected["path"]))
            actual = reportio.read_json(casebook._path(actual_item["path"]))
            for field in ("source_sha256", "model_sha256", "model_identity_sha256", "cube", "kernel", "m", "node_payload_bytes", "strategy"):
                if actual[field] != old[field]:
                    raise RuntimeError("shard differs from the original driver: " + field)
            for value in (actual, old):
                if [corpus.digest_file(casebook._path(path)) for path in value["models"]] != value["model_sha256"]:
                    raise RuntimeError("model bytes changed")
            old_primary = reportio.read_json(casebook._path(old["evidence"][0]["path"]))
            new_primary = reportio.read_json(casebook._path(actual["evidence"][0]["path"]))
            for field in ("frozen", "cube", "probes", "source_sha256", "reference_sha256", "output_sha256", "inputs_unchanged"):
                if new_primary[field] != old_primary[field]:
                    raise RuntimeError("native/probe receipt differs: " + field)
            if (corpus.digest_file(casebook._path(actual_item["path"])) != actual_item["sha256"]
                    or actual["cube"]["n_colors"] != 256 ** 3
                    or not io.inspect_submission_contract([casebook._path(p) for p in actual["models"]], semantics="independent")["pass"]):
                raise RuntimeError("new full-cube receipt or contract is invalid")
            report["cases"].append({"key": missing_key, "job": str(job_path), "job_sha256": corpus.digest_file(job_path),
                "reference_observation": expected, "new_observation": actual_item,
                "all_model_bytes_equal": True, "cube_output_sha256_equal": True, "all_metrics_and_probes_equal": True,
                "probe_count": len(new_primary["probes"]), "reused_receipts": len(selected)})
            report["fresh_native_full_cubes"] += 1
            report["reused_receipts"] += len(selected)
        for name, expected in hashes.items():
            if corpus.digest_file(ROOT / name) != expected:
                raise RuntimeError("qualification source changed")
        for name, expected in source_marker["source_sha256"].items():
            if corpus.digest_file(source / name) != expected:
                raise RuntimeError("frozen numerical source changed")
        if any(corpus.digest_file(Path(name)) != expected for name, expected in binaries.items()):
            raise RuntimeError("fitting/runtime binaries changed")
        if report["fresh_native_full_cubes"] != 2 or report["reused_receipts"] != 52:
            raise RuntimeError("qualification scope incomplete")
        report.update(pass_=True, inputs_unchanged=True, finished_utc=datetime.now(timezone.utc).isoformat())
        report["pass"] = report.pop("pass_")
        reportio.write_report(result_path, report)
        print(json.dumps({"pass": True, "fresh_full_cubes": 2, "reused_receipts": 52,
                          "exact_model_output_metric_probe_match": True, "global_phase_claimed_complete": False}))
    except BaseException as error:
        report.update(error={"type": type(error).__name__, "message": str(error)}, finished_utc=datetime.now(timezone.utc).isoformat())
        reportio.write_report(result_path, report)
        raise
    finally:
        for child, handle, *_ in jobs:
            if child.poll() is None:
                subprocess.run(["taskkill", "/PID", str(child.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                child.wait()
            handle.close()


if __name__ == "__main__":
    main()
