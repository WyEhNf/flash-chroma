"""Stage-qualify bounded CG continuation without changing the original matrix.

Five declared fits: four successful legacy configurations must reproduce all
model bytes, while the recorded random/adversarial m33 failure must complete.
Only the new m33 model executes three full RGB8 streams (CPU, CUDA, compiled
C99 ROM). No mapping/fit speed claim and no held-out source is evaluated.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import cache, casebook, corpus, io, portable_export, reportio, runtime, validation
from r29_strategy_matrix import probe_stats

CONFIGURATIONS = [("hashed_random-adversarial-s0-c986b485", 17, True),
                  ("hashed_random-adversarial-s0-c986b485", 25, True),
                  ("gamma-mild-s0-677a6f0f", 33, True),
                  ("hard_clip-mild-s0-dbb95391", 33, True),
                  ("hashed_random-adversarial-s0-c986b485", 33, False)]


def execute(command):
    result = runtime._execute(list(map(str, command)))
    if result["returncode"]:
        raise runtime.BackendError("solver recovery stage command failed", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resume", action="store_true", help="reuse already published model batches after a metadata-only driver repair")
    args = parser.parse_args()
    folder = ROOT / "artifacts/r51-solver-recovery"
    target = folder / "stage.json"
    previous = reportio.read_json(target) if target.exists() else None
    if folder.exists() and not args.resume:
        raise RuntimeError("preserve the previous qualification epoch")
    if args.resume and (previous is None or previous["pass"] or not previous.get("finished_utc")
                        or previous["new_native_full_cube_streams"]):
        raise RuntimeError("resume only the explicit pre-deployment failed attempt; never repeat completed pixel streams")
    folder.mkdir(exist_ok=True)
    names = ["scripts/r51_solver_recovery.py", "scripts/r29_strategy_matrix.py",
             "python/lutlab/robust_solver.py", "python/lutlab/robust_fit.py", "python/lutlab/fit.py",
             "python/lutlab/cascade.py", "python/lutlab/cache.py", "python/lutlab/io.py", "python/lutlab/interp.py",
             "python/lutlab/portable_export.py", "python/lutlab/casebook.py", "python/lutlab/runtime.py",
             "python/lutlab/reportio.py", "python/lutlab/validation.py", "portable/include/jshc_portable.h",
             "portable/src/jshc_portable.c", "portable/tools/verify_exported_rom.c"]
    hashes = {name: corpus.digest_file(ROOT / name) for name in names}
    if previous:
        for name, digest in previous["source_sha256"].items():
            if name != Path(__file__).relative_to(ROOT).as_posix() and hashes[name] != digest:
                raise RuntimeError("numerical/validation code changed; do not alias existing fit batches")
    frozen = ROOT / "artifacts/r29-frozen-source/19c69a6a7554b9920301"
    def functions(path):
        return {node.name: node for node in ast.parse(path.read_bytes()).body if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
    old_functions = functions(frozen / "python/lutlab/fit.py")
    current_functions = functions(ROOT / "python/lutlab/fit.py")
    todo = ["stratified_points", "_stratified_system", "fit_ls_sep", "int_refine", "quantize", "adaptive_dp_grid"]
    checked = set()
    while todo:
        name = todo.pop()
        if name in checked:
            continue
        checked.add(name)
        if ast.dump(old_functions[name], include_attributes=False) != ast.dump(current_functions[name], include_attributes=False):
            raise RuntimeError("legacy arithmetic helper changed: " + name)
        todo.extend(node.id for node in ast.walk(current_functions[name])
                    if isinstance(node, ast.Name) and node.id in current_functions and node.id not in checked)
    cpu = ROOT / "build-r18-cpu/jshc.exe"
    cuda = ROOT / "build-r32-format-gpu/jshc_gpu.exe"
    binaries = {str(path): corpus.digest_file(path) for path in (cpu, cuda, ROOT / "build-fit/libjshc_full_fit.dll")}
    base_regression_path = ROOT / "artifacts/r29-matrix/regression.json"
    extension_regression_path = ROOT / "artifacts/r36-extension/regression.json"
    base_regression = reportio.read_json(base_regression_path)
    extension_regression = reportio.read_json(extension_regression_path)
    if not base_regression["phase_complete"] or not extension_regression["phase_complete"]:
        raise RuntimeError("complete regression reference matrices are required")
    reference_states = {"regression": base_regression}
    catalog = {row["id"]: row for row in reportio.read_json(ROOT / "datasets/problem16-v1/catalog.json")["cases"]}
    plan = {"schema": 1, "declared_before_executing_candidate_fits": True,
            "configurations": [{"case_id": cid, "m": m, "expect_legacy_bytes_equal": equal} for cid, m, equal in CONFIGURATIONS],
            "new_native_full_cube_streams": 3, "legacy_model_checks": 4,
            "holdout_sources": 0, "original_matrix_candidates": 7917}
    reportio.write_report(folder / "plan.json", plan)
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__, "pass": False,
              "source_sha256": hashes, "binary_sha256": binaries, "plan_sha256": corpus.digest_file(folder / "plan.json"),
              "legacy_jitter_arithmetic_helpers_ast_equal": sorted(checked), "fits": [], "pending_canonical_import": [],
              "new_native_full_cube_streams": 0, "holdout_outputs_read": False, "timing_is_benchmark": False,
              "original_failure_preserved": False, "canonical_mutations": 0, "official": False}
    if previous:
        report["metadata_only_resume"] = {"previous_failed_stage": str(folder / "failed-metadata-attempt/stage.json"),
            "previous_failed_stage_sha256": corpus.digest_file(folder / "failed-metadata-attempt/stage.json"),
            "reason": "old log did not name a stage; compare the first exhausted channel across all four stages, not stage one",
            "numerical_sources_unchanged": True, "completed_pixel_streams_repeated": 0}
        report["resumed_model_batches"] = 0
    reportio.write_report(target, report)
    try:
        chosen = None
        original_failure = None
        for cid, m, expect_equal in CONFIGURATIONS:
            case = catalog[cid]
            if case["split"] not in reference_states:
                reference_states[case["split"]] = reportio.read_json(ROOT / "artifacts/r29-matrix" / (case["split"] + ".json"))
            old_item = reference_states[case["split"]]["observations"][f"{cid}/dp_jitter/m{m}"]
            old_path = casebook._path(old_item["path"])
            if corpus.digest_file(old_path) != old_item["sha256"]:
                raise RuntimeError("original candidate receipt changed")
            old = reportio.read_json(old_path)
            if (old_item["status"] == "screened") != expect_equal:
                raise RuntimeError("legacy expectation differs from recorded candidate outcome")
            location = folder / f"{cid}-m{m}"
            location.mkdir(exist_ok=True)
            source = ROOT / "data/corpus-v1/cases" / cid
            inputs = [source / f"lut{k}.lut256" for k in range(1, 5)]
            manifest = reportio.read_json(source / "manifest.json")
            expected_hashes = [stage["sha256"] for stage in manifest["stages"]]
            if ([corpus.digest_file(path) for path in inputs] != expected_hashes or old["source_sha256"] != expected_hashes
                    or corpus.digest_file(source / "composite.lut256") != manifest["composite"]["sha256"]):
                raise RuntimeError("original case sources or truth changed")
            command = [sys.executable, "-m", "lutlab.robust_fit", "--inputs", *inputs,
                       "--m", m, "--grid", "dp", "--model-dir", location / "models"]
            execution = execute(command)
            (location / ("fit-resume.log" if args.resume else "fit.log")).write_text(execution["stdout"] + execution["stderr"], encoding="utf-8")
            value = json.loads(execution["stdout"].splitlines()[-1])
            if args.resume:
                if not value["cache_hit"]:
                    raise RuntimeError("metadata-only resume unexpectedly repeated a fit")
                report["resumed_model_batches"] += 1
            models = [Path(path) for path in value["models"]]
            model_hashes = [corpus.digest_file(path) for path in models]
            model_manifest = reportio.read_json(models[0].parent / "manifest.json")
            contract = io.inspect_submission_contract(models, semantics="independent")
            if not contract["pass"] or contract["grid_sizes"] != [m] * 4:
                raise RuntimeError("candidate does not satisfy the four-own-source model contract")
            attempts = [channel for stage in value["fit"]["stage_info"] for channel in stage["solver"]["channels"]]
            if len(attempts) != 12 or any(not row["converged"] for row in attempts):
                raise RuntimeError("not all twelve stage/channel systems converged")
            row = {"case_id": cid, "m": m, "models": list(map(str, models)), "model_sha256": model_hashes,
                   "manifest": value["manifest"], "manifest_sha256": corpus.digest_file(Path(value["manifest"])),
                   "identity_sha256": value["identity_sha256"], "fit_execution": {k: v for k, v in execution.items() if k not in ("stdout", "stderr")},
                   "continuation_channels": sum(len(channel["attempts"]) > 1 for channel in attempts),
                   "all_channels_converged": True, "legacy_status": old_item["status"], "legacy_receipt": old_item}
            if expect_equal:
                if model_hashes != old["model_sha256"] or value["identity_sha256"] == old["model_identity_sha256"]:
                    raise RuntimeError("successful old model changed bytes or new solver aliased its old cache identity")
                if any(len(channel["attempts"]) != 1 for channel in attempts):
                    raise RuntimeError("an originally successful case unexpectedly required continuation")
                row.update(all_legacy_model_bytes_equal=True, previous_native_output_reused_by_byte_identity=True,
                           previous_cube=old["cube"])
            else:
                original_failure = (old_path, old_item["sha256"])
                old_run = reportio.read_json(ROOT / "artifacts/r29-matrix/frozen-runlogs/regression/runs/20261015T224312Z-fit-ad61843f/run.json")
                expected = old_run["metrics"]["solver_failure"]["channels"][0]
                exhausted = [(stage_index + 1, channel) for stage_index, stage in enumerate(value["fit"]["stage_info"])
                             for channel in stage["solver"]["channels"] if not channel["attempts"][0]["converged"]]
                if not exhausted:
                    raise RuntimeError("no first exhausted legacy channel was recorded")
                failure_stage, failure_channel = exhausted[0]
                initial = failure_channel["attempts"][0]
                for field in ("info", "iterations", "residual_l2", "relative_residual", "finite", "converged"):
                    if initial[field] != expected[field]:
                        raise RuntimeError("first failed solve did not exactly reproduce the recorded failure: " + field)
                if row["continuation_channels"] == 0:
                    raise RuntimeError("the failed configuration did not exercise the proposed recovery")
                chosen = (cid, models, model_hashes, model_manifest, source, expected_hashes, manifest, location)
                row.update(recorded_first_failure_exactly_reproduced=True, recorded_first_failure_stage=failure_stage,
                           recorded_first_failure_channel=failure_channel["channel"])
            report["fits"].append(row)
            reportio.write_report(target, report)
            print(f"[solver] {cid}/m{m}: all channels converged; continuations={row['continuation_channels']}; old-byte-check={expect_equal}", flush=True)
        if chosen is None:
            raise RuntimeError("no recovered configuration available")
        cid, models, model_hashes, model_manifest, source, source_hashes, source_manifest, location = chosen
        probes = reportio.read_json(ROOT / "data/corpus-v1/probes.json")
        import numpy as np
        with tempfile.TemporaryDirectory(prefix="r51-native-") as temporary:
            raw = Path(temporary) / "cpu.rgb"
            execution = runtime.cube(models, raw, executable=cpu, kernel="tetra_avx2", threads=4, competition=True)
            report["new_native_full_cube_streams"] += 1
            truth_path = source / "composite.lut256"
            with validation._mapped_full(raw) as predicted, validation._mapped_full(truth_path) as truth:
                quality = validation._cube_stats(predicted, truth, 8, 2.)
                probe_quality = {name: probe_stats(predicted, truth, np.load(ROOT / "data/corpus-v1/probes" / (name + ".npy"), mmap_mode="r", allow_pickle=False)) for name in probes}
            output_hash = corpus.digest_file(raw)
            primary = {"kind": "casebook_native_cube_screen_v1", "case_id": cid, "source_sha256": source_hashes,
                       "reference_sha256": source_manifest["composite"]["sha256"], "runtime": execution,
                       "output_sha256": output_hash, "cube": quality, "probes": probe_quality,
                       "inputs_unchanged": True, "image_path_qualification": False, "timing_is_benchmark": False}
            primary_path = location / "screen.json"
            reportio.write_report(primary_path, primary)
            observation = {"case_id": cid, "source_sha256": source_hashes, "semantics": "independent", "correctness_pass": True,
                           "strategy": "dp_jitter_continued@" + model_manifest["identity_sha256"][:12], "profile": "dp_jitter_continued",
                           "m": [33] * 4, "models": list(map(str, models)), "model_sha256": model_hashes,
                           "model_identity_sha256": model_manifest["identity_sha256"], "kernel": "tetra_avx2",
                           "node_payload_bytes": 4 * 3 * 33 ** 3, "cube": quality,
                           "evidence": [{"path": str(primary_path), "sha256": corpus.digest_file(primary_path)}], "official": False}
            observation_path = location / "observation.json"
            reportio.write_report(observation_path, observation)
            book = casebook.Casebook(folder / "native-casebook")
            case = catalog[cid]
            book.add_case(cid, {key: case[key] for key in ("family", "intensity", "seed", "split", "tags", "expected")}, source_hashes)
            identifier = book.record(observation_path)
            report["pending_canonical_import"].append({"case_id": cid, "path": str(observation_path),
                "sha256": corpus.digest_file(observation_path), "observation_id": identifier})
            gpu_raw = Path(temporary) / "cuda.rgb"
            gpu = runtime.cube(models, gpu_raw, backend="cuda", executable=cuda, kernel="cuda_q16_fused4", competition=True)
            report["new_native_full_cube_streams"] += 1
            if corpus.digest_file(gpu_raw) != output_hash:
                raise RuntimeError("recovered model CPU/CUDA differs")
            export = folder / "recovered-rom"
            metadata = portable_export.export_models(models, export)
            executable = folder / "verify-recovered-rom.exe"
            build = execute(["E:/mingw64/bin/gcc.exe", "-std=c99", "-O2", "-Wall", "-Wextra", "-Wpedantic", "-Wconversion", "-Werror",
                             "-I", ROOT / "portable/include", "-I", export, export / "flash_chroma.c",
                             ROOT / "portable/src/jshc_portable.c", ROOT / "portable/tools/verify_exported_rom.c", "-o", executable])
            rom_raw = Path(temporary) / "rom.rgb"
            rom = execute([executable, "cube", rom_raw])
            report["new_native_full_cube_streams"] += 1
            if corpus.digest_file(rom_raw) != output_hash:
                raise RuntimeError("recovered compiled C99 ROM differs")
            report["deployment"] = {"cpu_cube": primary, "cuda_execution": gpu, "rom_metadata": metadata,
                "rom_build": build, "rom_execution": rom, "rom_plan": json.loads(rom["stderr"]),
                "all_full_cube_sha256_equal": True, "output_sha256": output_hash, "cube": quality,
                "actual_images_executed": 0, "physical_mobile_measured": False}
        # Compare against every original candidate at every declared capacity;
        # retain the failed original cell and do not retroactively replace it.
        references = []
        for state in (base_regression, extension_regression):
            for key, item in state["observations"].items():
                if key.split("/")[0] == cid:
                    value = reportio.read_json(casebook._path(item["path"]))
                    if corpus.digest_file(casebook._path(item["path"])) != item["sha256"]:
                        raise RuntimeError("reference regression candidate changed")
                    references.append({"key": key, "status": item["status"], "cube": value.get("cube")})
        if len(references) != 39:
            raise RuntimeError("original 13-profile by 3-size comparison incomplete")
        valid = [row for row in references if row["status"] == "screened"]
        report["reference_comparison"] = {"declared": len(references), "valid": len(valid), "failures": len(references) - len(valid),
            "best_old_mean": min(row["cube"]["mean"] for row in valid), "best_old_max": min(row["cube"]["max"] for row in valid),
            "candidate_mean": quality["mean"], "candidate_max": quality["max"], "reference_rows": references}
        from lutlab.robust_fit import fit_batch
        hit, reused = fit_batch([source / f"lut{k}.lut256" for k in range(1, 5)], 33, "dp", location / "models")
        if not reused or hit.manifest["identity_sha256"] != model_manifest["identity_sha256"]:
            raise RuntimeError("public robust cache identity did not resume the published batch")
        for name, expected in hashes.items():
            if corpus.digest_file(ROOT / name) != expected:
                raise RuntimeError("candidate numerical or validation source changed")
        for name, expected in binaries.items():
            if corpus.digest_file(Path(name)) != expected:
                raise RuntimeError("native binary changed")
        if original_failure is None or corpus.digest_file(original_failure[0]) != original_failure[1]:
            raise RuntimeError("original recorded failure changed")
        if ([corpus.digest_file(source / f"lut{k}.lut256") for k in range(1, 5)] != source_hashes
                or corpus.digest_file(source / "composite.lut256") != source_manifest["composite"]["sha256"]):
            raise RuntimeError("recovered original source/truth changed during validation")
        report.update(pass_=True, inputs_unchanged=True, original_failure_preserved=True,
                      finished_utc=datetime.now(timezone.utc).isoformat(), public_cache_hit_verified=True,
                      full_original_matrix_complete=False, full_user_goal_complete=False)
        report["pass"] = report.pop("pass_")
        reportio.write_report(target, report)
        print(json.dumps({"pass": True, "fit_configurations": len(report["fits"]), "legacy_byte_equal_configurations": 4,
            "recovered_failed_configuration": True, "native_full_streams": report["new_native_full_cube_streams"], "quality": quality,
            "canonical_import_pending": 1}))
    except BaseException as error:
        if isinstance(error, runtime.BackendError):
            report["failed_execution"] = error.record
        report.update(error={"type": type(error).__name__, "message": str(error)}, finished_utc=datetime.now(timezone.utc).isoformat())
        reportio.write_report(target, report)
        raise


if __name__ == "__main__":
    main()
