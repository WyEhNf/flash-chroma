"""Execute every predeclared R36 cell with immutable, resumable evidence.

This process owns an isolated phase ledger. The canonical controller may import
its immutable observations while this phase continues. Identical mappings reuse
only a hash-bound complete cube and the exact same probe cohort. No image
qualification, performance ranking or class sweet-zone claim is inferred here.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import traceback
import uuid

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE / "python"))
sys.path.insert(1, str(SOURCE))
os.environ.update(OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", OMP_NUM_THREADS="1")
import numpy as np
from lutlab import axisbins, cache, casebook, corpus, fullfit, io, reportio, selection, validation, runtime
from scripts.r33_axis_bins_study import new_entry
from scripts.r29_strategy_matrix import probe_stats


def baseline_entry(paths, name, m, profile, definition, output, baseline_root):
    _, method, grid, _ = definition
    destination = output / "baseline-models" / name / f"{profile}-m{m}"
    params = dict(scenario=name, mode="seq", method=method, m=m, grid=grid, adaptive=False,
                  inputs=list(map(str, paths)), model_dir=str(destination), allow_composite=False, allow_residual=False)
    code = ("from pathlib import Path;from types import SimpleNamespace;import sys,json;from lutlab import cli;"
            "v=json.loads(sys.argv[1]);v['inputs']=[Path(x) for x in v['inputs']];"
            "e=cli.model_entry(SimpleNamespace(**v));print('R36_ENTRY='+str(e.directory))")
    environment = {**os.environ, "PYTHONPATH": str(baseline_root / "python"),
                   "GIT_CEILING_DIRECTORIES": str(output.parents[1]), "JSHC_LOG_DIR": str(output / "baseline-runlogs")}
    command = [sys.executable, "-c", code, json.dumps(params)]
    process = subprocess.run(command, cwd=baseline_root, env=environment, capture_output=True,
                             text=True, encoding="utf-8", errors="replace")
    log = output / "baseline-logs" / name / f"{profile}-m{m}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(process.stdout + process.stderr, encoding="utf-8")
    if process.returncode:
        raise RuntimeError("frozen baseline fit failed: " + str(log))
    line = next(line for line in reversed(process.stdout.splitlines()) if line.startswith("R36_ENTRY="))
    directory = Path(line[len("R36_ENTRY="):])
    manifest = reportio.read_json(directory / "manifest.json")
    entry = cache.inspect_entry(directory, manifest["identity"])
    if entry is None:
        raise RuntimeError("baseline did not publish a verifiable batch")
    for name, digest in manifest["identity"]["source_sha256"].items():
        path = baseline_root / name if name == "pixi.lock" else baseline_root / "python/lutlab" / name
        if corpus.digest_file(path) != digest:
            raise RuntimeError("baseline numerical source differs")
    return entry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--phase", choices=["development", "calibration", "regression", "holdout"], required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--max-candidates", type=int, default=0)
    parser.add_argument("--combined-class-rule", type=Path)
    args = parser.parse_args()
    if args.max_candidates < 0:
        parser.error("negative work limit")
    workspace = args.workspace.resolve()
    output = (args.output or workspace / "artifacts/r36-extension").resolve()
    output.mkdir(parents=True, exist_ok=True)
    lock = output / (args.phase + ".lock")
    with lock.open("x", encoding="utf-8") as stream:
        json.dump({"pid": os.getpid(), "phase": args.phase, "source_root": str(SOURCE)}, stream)
    try:
        run(args, workspace, output)
    finally:
        lock.unlink()


def run(args, workspace, output):
    image_marker = reportio.read_json(SOURCE / "frozen-source.json")
    if not image_marker["pass"]:
        raise RuntimeError("extension must execute from its verified source image")
    baseline_root = Path(reportio.read_json(workspace / "artifacts/r29-matrix/frozen-source.json")["source_root"])
    baseline_marker = reportio.read_json(baseline_root / "frozen-source.json")
    plan_path = workspace / "datasets/problem16-v1/strategy-extension-r36.json"
    plan = reportio.read_json(plan_path)
    original_plan = workspace / "datasets/problem16-v1/strategy-plan.json"
    if corpus.digest_file(original_plan) != plan["baseline_plan_sha256"]:
        raise RuntimeError("baseline plan changed")
    if set(plan["new_profiles"]) != set(axisbins.PROFILES):
        raise RuntimeError("new profile set differs from the declaration")
    for name, parameters in plan["profiles"].items():
        if list(selection.PROFILES[name]) != parameters:
            raise RuntimeError("profile parameters changed")
    definitions = []
    inspections = []
    datasets = [workspace / "data/corpus-v1", workspace / "data/corpus-axis-bins-v1"]
    for descriptor, dataset in zip(plan["catalogs"], datasets):
        path = workspace / descriptor["path"]
        if corpus.digest_file(path) != descriptor["sha256"]:
            raise RuntimeError("catalog changed")
        definition = reportio.read_json(path)
        if definition["generator"] != corpus.generator_fingerprint():
            raise RuntimeError("source generator differs from the inspected corpus")
        inspection = dataset / "inspection.json"
        if not reportio.read_json(inspection)["pass"]:
            raise RuntimeError("source corpus was not inspected")
        definitions.append({case["id"]: case for case in definition["cases"]})
        inspections.append(corpus.digest_file(inspection))
    keys = sorted(f"{case['id']}/{profile}/m{m}" for case in plan["cases"] for m in plan["sizes"] for profile in case["profiles"])
    if len(keys) != plan["extension_candidates"] or hashlib.sha256(corpus.canonical(keys)).hexdigest() != plan["expected_keyset_sha256"]:
        raise RuntimeError("extension cell set differs")
    phase_cases = [case for case in plan["cases"] if case["split"] == args.phase]
    ranks = {"mild": 0, "medium": 1, "strong": 2}
    phase_cases.sort(key=lambda case: (0 if case["catalog"] else 1, ranks.get(case["intensity"], 3), case["family"], case["id"]))
    expected = {f"{case['id']}/{profile}/m{m}" for case in phase_cases for m in plan["sizes"] for profile in case["profiles"]}
    if len(expected) != plan["phase_expected_candidates"][args.phase]:
        raise RuntimeError("phase coverage differs")
    if args.phase == "holdout":
        if args.combined_class_rule is None:
            raise RuntimeError("extension holdout needs the combined frozen rule")
        rule = reportio.read_json(args.combined_class_rule)
        if (not rule["frozen_before_holdout"] or rule["extension_plan_sha256"] != corpus.digest_file(plan_path)
                or rule["baseline_plan_sha256"] != plan["baseline_plan_sha256"]):
            raise RuntimeError("combined rule belongs to another experiment")
        for role in ("baseline_development", "baseline_calibration", "extension_development", "extension_calibration"):
            item = rule["training_reports"][role]
            path = casebook._path(item["path"])
            if corpus.digest_file(path) != item["sha256"] or not reportio.read_json(path)["phase_complete"]:
                raise RuntimeError("combined rule did not freeze complete training reports")
    cpu = workspace / "build-r18-cpu/jshc.exe"
    os.environ.update(JSHC_FULL_FIT_LIB=str(workspace / "build-fit/libjshc_full_fit.dll"),
                      OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", OMP_NUM_THREADS="1", OMP_DYNAMIC="FALSE")
    probe_path = datasets[0] / "probes.json"
    probe_definition = reportio.read_json(probe_path)
    points = {}
    for name, descriptor in probe_definition.items():
        path = datasets[0] / "probes" / (name + ".npy")
        array = np.load(path, mmap_mode="r", allow_pickle=False)
        if array.shape != (descriptor["count"], 3) or array.dtype != np.uint8 or corpus.digest_file(path) != descriptor["sha256"]:
            raise RuntimeError("probe bytes differ from the inspected cohort")
        points[name] = array
    frozen = {"plan_sha256": corpus.digest_file(plan_path), "inspection_sha256": inspections,
              "probe_definition_sha256": corpus.digest_file(probe_path), "new_fitting_source_sha256": cache.source_fingerprint(),
              "evaluation_source_sha256": {name: corpus.digest_file(SOURCE / name) for name in
                  ("python/lutlab/runtime.py", "python/lutlab/validation.py", "scripts/r29_strategy_matrix.py")},
              "baseline_source_image_sha256": baseline_marker["archive_sha256"],
              "native_sha256": corpus.digest_file(cpu), "trainer": fullfit.trainer_fingerprint(), "phase": args.phase,
              "combined_class_rule_sha256": corpus.digest_file(args.combined_class_rule) if args.combined_class_rule else None}
    def source_guard():
        for name, digest in image_marker["source_sha256"].items():
            if corpus.digest_file(SOURCE / name) != digest:
                raise RuntimeError("frozen extension source changed")
        for name, digest in baseline_marker["source_sha256"].items():
            if corpus.digest_file(baseline_root / name) != digest:
                raise RuntimeError("frozen baseline source changed")
        if corpus.digest_file(cpu) != frozen["native_sha256"] or fullfit.trainer_fingerprint() != frozen["trainer"]:
            raise RuntimeError("native runtime/trainer changed")
    source_guard()
    state_path = output / (args.phase + ".json")
    if state_path.exists():
        state = reportio.read_json(state_path)
        if state["frozen"] != frozen:
            raise RuntimeError("resume epoch differs; preserve existing evidence")
    else:
        state = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__, "frozen": frozen,
                 "observations": {}, "phase_complete": False, "phase_expected_candidates": len(expected),
                 "extension_candidates": 2517, "combined_declared_candidates": 7917,
                 "timing_is_benchmark": False, "image_qualification": False, "official": False}
    if set(state["observations"]) - expected:
        raise RuntimeError("saved observations outside the predeclared phase")
    state.setdefault("execution_epochs", {})[image_marker["epoch_sha256"]] = {
        "root": str(SOURCE), "archive_sha256": image_marker["archive_sha256"], "source_sha256": image_marker["source_sha256"]}
    book = casebook.Casebook(output / "worker-casebooks" / args.phase)
    for descriptor, dataset in zip(plan["catalogs"], datasets):
        book.attach_catalog(workspace / descriptor["path"], dataset)
    for item in state["observations"].values():
        path = casebook._path(item["path"])
        if corpus.digest_file(path) != item["sha256"]:
            raise RuntimeError("completed evidence changed")
        if item["status"] == "screened":
            if book.record(path) != item["observation_id"]:
                raise RuntimeError("completed observation identity changed")
        else:
            book.record_failure(path)
    # A crash after committing an immutable observation but before publishing
    # the phase index must not cause it to be overwritten or mapped again.
    recovered = []
    for item in phase_cases:
        for m in plan["sizes"]:
            for profile in item["profiles"]:
                key = f"{item['id']}/{profile}/m{m}"
                if key in state["observations"]: continue
                directory = output / "cases" / item["id"] / f"{profile}-m{m}"
                candidates = sorted(directory.glob("attempt-*/observation.json"))
                if not candidates:
                    failures = sorted(directory.glob("attempt-*/failure.json"))
                    if not failures: continue
                    path = failures[0]
                    failure = reportio.read_json(path)
                    if (failure["case_id"] != item["id"] or failure["strategy"] != profile or failure["m"] != [m]*4
                            or failure["frozen"] != frozen):
                        raise RuntimeError("unindexed failure belongs to a different cell/epoch")
                    book.record_failure(path)
                    state["observations"][key] = {"status": failure["status"], "path": str(path),
                        "sha256": corpus.digest_file(path), "recovered_completed_before_resume": True}
                    recovered.append(key)
                    continue
                path = candidates[0]
                value = reportio.read_json(path)
                primary = reportio.read_json(casebook._path(value["evidence"][0]["path"]))
                if (value["case_id"] != item["id"] or value["profile"] != profile or value["m"] != [m]*4
                        or primary["frozen"] != frozen):
                    raise RuntimeError("unindexed receipt belongs to a different cell/epoch")
                folder = datasets[item["catalog"]] / "cases" / item["id"]
                manifest = reportio.read_json(folder / "manifest.json")
                if ([corpus.digest_file(folder / f"lut{k}.lut256") for k in range(1, 5)] != value["source_sha256"]
                        or corpus.digest_file(folder / "composite.lut256") != manifest["composite"]["sha256"]
                        or primary["reference_sha256"] != manifest["composite"]["sha256"]):
                    raise RuntimeError("unindexed receipt no longer binds the current data")
                identifier = book.record(path)
                state["observations"][key] = {"status": "screened", "observation_id": identifier,
                    "path": str(path), "sha256": corpus.digest_file(path), "cube_mean": value["cube"]["mean"],
                    "cube_max": value["cube"]["max"], "numerical_evidence_reused": "reuse" in primary,
                    "recovered_completed_before_resume": True}
                recovered.append(key)
    if recovered:
        state.setdefault("recovery_events", []).append({"utc": datetime.now(timezone.utc).isoformat(), "keys": recovered,
                                                        "pixel_reexecutions": 0})
    reportio.write_report(state_path, state)
    reuse_index = {}
    def register_primary(value, primary_path):
        if corpus.digest_file(primary_path) != value["evidence"][0]["sha256"]:
            raise RuntimeError("reuse primary proof changed")
        primary = reportio.read_json(primary_path)
        if (primary.get("kind") != "casebook_native_cube_screen_v1" or not primary["inputs_unchanged"]
                or primary["runtime"]["returncode"] != 0 or primary["cube"] != value["cube"]
                or primary["source_sha256"] != value["source_sha256"]
                or list(primary["runtime"]["models_sha256"].values()) != value["model_sha256"]):
            raise RuntimeError("reuse source is not a complete bound native screen")
        prior = primary.get("frozen", {})
        same_probes = (prior.get("inspection_sha256") == inspections[0]
                       or prior.get("probe_definition_sha256") == frozen["probe_definition_sha256"])
        if not same_probes or set(primary["probes"]) != set(points):
            return
        key = (tuple(value["source_sha256"]), primary["reference_sha256"], tuple(value["model_sha256"]),
               value["kernel"], primary["runtime"]["executable_sha256"])
        reuse_index.setdefault(key, (primary_path, corpus.digest_file(primary_path), primary))
    for item in state["observations"].values():
        if item["status"] == "screened":
            value = reportio.read_json(casebook._path(item["path"]))
            register_primary(value, casebook._path(value["evidence"][0]["path"]))
    loaded_receipts = {}
    def refresh_baseline_reuse():
        path = workspace / "artifacts/r29-matrix" / (args.phase + ".json")
        if not path.exists(): return
        prior = reportio.read_json(path)
        if prior["frozen"]["inspection_sha256"] != inspections[0]:
            raise RuntimeError("baseline probe inspection differs")
        for item in prior["observations"].values():
            if item["status"] != "screened": continue
            if item["path"] in loaded_receipts:
                if loaded_receipts[item["path"]] != item["sha256"]:
                    raise RuntimeError("previously indexed baseline receipt changed")
                continue
            value_path = casebook._path(item["path"])
            if corpus.digest_file(value_path) != item["sha256"]:
                raise RuntimeError("baseline observation changed")
            value = reportio.read_json(value_path)
            register_primary(value, casebook._path(value["evidence"][0]["path"]))
            loaded_receipts[item["path"]] = item["sha256"]
    refresh_baseline_reuse()
    memo = {}
    performed = 0
    for item in phase_cases:
        case = definitions[item["catalog"]][item["id"]]
        folder = datasets[item["catalog"]] / "cases" / case["id"]
        manifest = reportio.read_json(folder / "manifest.json")
        if manifest["spec_sha256"] != hashlib.sha256(corpus.canonical(case)).hexdigest():
            raise RuntimeError("source recipe differs from the declared case")
        paths = [folder / f"lut{k}.lut256" for k in range(1, 5)]
        source_hashes = [record["sha256"] for record in manifest["stages"]]
        truth_path = folder / "composite.lut256"
        truth_hash = manifest["composite"]["sha256"]
        def input_guard():
            if [corpus.digest_file(path) for path in paths] != source_hashes or corpus.digest_file(truth_path) != truth_hash:
                raise RuntimeError("source/reference bytes changed")
        input_guard()
        for m in plan["sizes"]:
            for profile in item["profiles"]:
                key = f"{case['id']}/{profile}/m{m}"
                if key in state["observations"]: continue
                if args.max_candidates and performed >= args.max_candidates:
                    state["last_chunk_finished_utc"] = datetime.now(timezone.utc).isoformat()
                    reportio.write_report(state_path, state)
                    return
                performed += 1
                source_guard()
                destination = output / "cases" / case["id"] / f"{profile}-m{m}" / ("attempt-" + uuid.uuid4().hex[:16])
                destination.mkdir(parents=True, exist_ok=True)
                failure = {"case_id": case["id"], "source_sha256": source_hashes, "strategy": profile,
                           "m": [m]*4, "frozen": frozen}
                def publish_failure(status, detail):
                    path = destination / "failure.json"
                    reportio.write_report(path, {**failure, "status": status, "detail": detail})
                    book.record_failure(path)
                    state["observations"][key] = {"status": status, "path": str(path), "sha256": corpus.digest_file(path)}
                    reportio.write_report(state_path, state)
                started = time.perf_counter()
                try:
                    if profile in axisbins.PROFILES:
                        entry = new_entry(paths, case["id"], m, profile, output, memo)
                    else:
                        entry = baseline_entry(paths, case["id"], m, profile, plan["profiles"][profile], output, baseline_root)
                except Exception:
                    source_guard(); input_guard()
                    publish_failure("fit_failure", traceback.format_exc().encode("ascii", "backslashreplace").decode("ascii"))
                    print("[extension] " + key + ": fit_failure", flush=True)
                    continue
                fit_elapsed = time.perf_counter() - started
                parameters = entry.manifest["identity"]["parameters"]
                if parameters["method"] != plan["profiles"][profile][1] or parameters["m"] != m:
                    raise RuntimeError("published batch belongs to another declared method/budget")
                model_hashes = [corpus.digest_file(path) for path in entry.paths]
                kernel = plan["profiles"][profile][3]
                kernel = "tetra_avx2" if kernel == "auto" else kernel
                mapping_key = (tuple(source_hashes), truth_hash, tuple(model_hashes), kernel, frozen["native_sha256"])
                reused = reuse_index.get(mapping_key)
                if reused:
                    prior_path, prior_hash, prior = reused
                    if corpus.digest_file(prior_path) != prior_hash:
                        raise RuntimeError("reuse proof changed")
                    quality = prior["cube"]
                    primary = {"kind": "casebook_native_cube_screen_v1", "case_id": case["id"],
                        "source_sha256": source_hashes, "reference_sha256": truth_hash, "runtime": prior["runtime"],
                        "output_sha256": prior["output_sha256"], "cube": quality, "probes": prior["probes"],
                        "reuse": {"path": str(prior_path), "sha256": prior_hash,
                            "reason": "identical ordered sources/model bytes, truth, executable, kernel and probe cohort"}}
                else:
                    with tempfile.TemporaryDirectory(prefix="r36-cube-") as temporary:
                        raw = Path(temporary) / "cube.rgb"
                        try:
                            execution = runtime.cube(entry.paths, raw, executable=cpu, kernel=kernel, threads=4, competition=True)
                        except runtime.BackendError as error:
                            source_guard(); input_guard()
                            publish_failure("execution_failure", error.record)
                            continue
                        with validation._mapped_full(raw) as prediction, validation._mapped_full(truth_path) as truth:
                            quality = validation._cube_stats(prediction, truth, 8, 2.)
                            per_probe = {name: probe_stats(prediction, truth, array) for name, array in points.items()}
                        primary = {"kind": "casebook_native_cube_screen_v1", "case_id": case["id"],
                            "source_sha256": source_hashes, "reference_sha256": truth_hash, "runtime": execution,
                            "output_sha256": corpus.digest_file(raw), "cube": quality, "probes": per_probe}
                source_guard(); input_guard()
                primary.update(frozen=frozen, inputs_unchanged=True, image_path_qualification=False,
                               timing_is_benchmark=False, fit_wall_seconds_not_benchmark=fit_elapsed,
                               fit_info=entry.manifest["fit"], execution_source_epoch_sha256=image_marker["epoch_sha256"])
                primary_path = destination / "screen.json"
                reportio.write_report(primary_path, primary)
                version = hashlib.sha256(corpus.canonical({name: value for name, value in entry.manifest["identity"].items() if name != "inputs"})).hexdigest()[:12]
                value = {"case_id": case["id"], "source_sha256": source_hashes, "semantics": "independent", "correctness_pass": True,
                    "strategy": profile + "@" + version, "profile": profile, "model_identity_sha256": entry.manifest["identity_sha256"],
                    "m": [m]*4, "models": list(map(str, entry.paths)), "model_sha256": model_hashes, "kernel": kernel,
                    "node_payload_bytes": sum(io.load_sparse(path).nodes.nbytes for path in entry.paths), "cube": quality,
                    "evidence": [{"path": str(primary_path), "sha256": corpus.digest_file(primary_path)}], "official": False}
                observation = destination / "observation.json"
                reportio.write_report(observation, value)
                identifier = book.record(observation)
                state["observations"][key] = {"status": "screened", "observation_id": identifier,
                    "path": str(observation), "sha256": corpus.digest_file(observation),
                    "cube_mean": quality["mean"], "cube_max": quality["max"], "numerical_evidence_reused": bool(reused)}
                reportio.write_report(state_path, state)
                register_primary(value, primary_path)
                reportio.write_report(book.root / "summary.json", book.summary())
                print(f"[extension] {len(state['observations'])}/{len(expected)} {key}: mean={quality['mean']:.8f}, max={quality['max']:.8f}, reused={bool(reused)}", flush=True)
        refresh_baseline_reuse()
    source_guard()
    state.update(phase_complete=set(state["observations"]) == expected, finished_utc=datetime.now(timezone.utc).isoformat())
    reportio.write_report(state_path, state)


if __name__ == "__main__":
    main()
