"""One native gate after the completed, materially useful joint-capacity search.

Execute the distinct mean/max selections per declared training source, verify
every output colour against the factored curves and bind native receipts to an
isolated casebook. Two mixed CUDA streams and one compiled C99 ROM stream are
separate deployment checks. No fitting, timing or holdout is performed.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
import numpy as np
from lutlab import casebook, cache, corpus, curve_search, io, portable_export, reportio, runtime, stage_bundle, validation


def execute(command):
    value = runtime._execute(list(map(str, command)))
    if value["returncode"]:
        raise RuntimeError("deployment verification failed: " + json.dumps(value, ensure_ascii=True))
    return value


def main():
    output = ROOT / "artifacts/r47-mixed-capacity"
    target = output / "native-gate.json"
    if target.exists():
        raise RuntimeError("preserve this native verification epoch before rerunning")
    training_path = output / "training.json"
    training_hash = corpus.digest_file(training_path)
    training = reportio.read_json(training_path)
    if not training["analysis_pass"] or training["analytic_configurations"] != 1458 or training["uniform_native_statistics_matched"] != 54:
        raise RuntimeError("complete exact training search required")
    for name, digest in training["source_sha256"].items():
        if corpus.digest_file(ROOT / name) != digest:
            raise RuntimeError("analytical proof implementation changed")
    source_names = ["scripts/r47_mixed_native_gate.py", "python/lutlab/stage_bundle.py", "python/lutlab/curve_search.py",
                    "python/lutlab/io.py", "python/lutlab/cache.py", "python/lutlab/casebook.py", "python/lutlab/runtime.py",
                    "python/lutlab/portable_export.py", "portable/src/jshc_portable.c", "portable/include/jshc_portable.h",
                    "portable/tools/verify_exported_rom.c", "python/lutlab/validation.py"]
    source_hashes = {name: corpus.digest_file(ROOT / name) for name in source_names}
    cpu = ROOT / "build-r35-structured/jshc.exe"
    cuda = ROOT / "build-r32-format-gpu/jshc_gpu.exe"
    binary_hashes = {str(path): corpus.digest_file(path) for path in (cpu, cuda)}
    lookup = {case["id"]: case for case in reportio.read_json(ROOT / "datasets/problem16-v1/catalog.json")["cases"]}
    book = casebook.Casebook(output / "native-casebook")
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__, "pass": False,
              "source_sha256": source_hashes, "training_sha256": training_hash, "binaries_sha256": binary_hashes,
              "observations": [], "pending_canonical_import": [], "cuda_checks": [], "rom_check": None,
              "new_fits": 0, "timing_is_benchmark": False, "holdout_outputs_read": False,
              "new_native_full_cube_streams": 0, "official": False}
    reportio.write_report(target, report)
    try:
        with tempfile.TemporaryDirectory(prefix="r47-native-") as temporary:
            temporary = Path(temporary)
            for entry in training["cases"]:
                analysis_path = casebook._path(entry["analysis"])
                if corpus.digest_file(analysis_path) != entry["sha256"]:
                    raise RuntimeError("completed per-source analysis changed")
                analysis = reportio.read_json(analysis_path)
                case_id = entry["id"]
                source_dir = ROOT / "data/corpus-v1/cases" / case_id
                source_manifest = reportio.read_json(source_dir / "manifest.json")
                sources = [source_dir / f"lut{stage}.lut256" for stage in range(1, 5)]
                source_hashes_before = [corpus.digest_file(path) for path in sources]
                truth_path = source_dir / "composite.lut256"
                if (source_hashes_before != [stage["sha256"] for stage in source_manifest["stages"]]
                        or corpus.digest_file(truth_path) != analysis["reference_sha256"]):
                    raise RuntimeError("original source/truth differs from the analytical proof")
                metadata = lookup[case_id]
                book.add_case(case_id, {key: metadata[key] for key in ("family", "intensity", "seed", "split", "tags", "expected")}, source_hashes_before)
                parents = {(row["stage"] - 1, row["m"]): row for row in analysis["parent_models"]}
                selected = {tuple(analysis["best_mean"]["m"]), tuple(analysis["best_max"]["m"])}
                for configuration in sorted(selected):
                    row = next(value for value in analysis["configurations"] if tuple(value["m"]) == configuration)
                    folder = output / "cases" / case_id / ("native-" + "-".join(map(str, configuration)))
                    folder.mkdir()
                    paths = [casebook._path(parents[stage, m]["path"]) for stage, m in enumerate(configuration)]
                    bundle = stage_bundle.assemble(paths, folder / "models")
                    contract = io.inspect_submission_contract(bundle.paths, semantics="independent")
                    if not contract["pass"] or contract["semantics_evidence"] != "verified_model_manifest" or contract["grid_sizes"] != list(configuration):
                        raise RuntimeError("mixed model bundle failed the public provenance/size contract")
                    raw = temporary / "cube.rgb"
                    execution = runtime.cube(bundle.paths, raw, executable=cpu, kernel="tetra_structured_avx2", threads=4, competition=True)
                    report["new_native_full_cube_streams"] += 1
                    expected_curves = curve_search.compose([curve_search.model_curves(io.load_sparse(path, competition=True)) for path in bundle.paths])
                    with validation._mapped_full(raw) as mapped, validation._mapped_full(truth_path) as truth:
                        if not np.array_equal(curve_search.target_curves(mapped), expected_curves):
                            raise RuntimeError("a native RGB output differs from the complete predicted curve mapping")
                        quality = validation._cube_stats(mapped, truth, top_k=8, threshold=2.)
                    names = ("n_colors", "mean", "rms", "p99", "max", "pixels_at_or_above_threshold")
                    if any(quality[name] != row[name] for name in names):
                        raise RuntimeError("native full-cube metrics differ from exact histogram search")
                    screen = {"kind": "casebook_native_cube_screen_v1", "case_id": case_id,
                              "source_sha256": source_hashes_before, "reference_sha256": analysis["reference_sha256"],
                              "runtime": execution, "output_sha256": corpus.digest_file(raw), "cube": quality,
                              "inputs_unchanged": True, "analytical_proof": {"path": str(analysis_path), "sha256": entry["sha256"]},
                              "all_native_colors_equal_predicted_curves": True, "image_path_qualification": False,
                              "timing_is_benchmark": False}
                    screen_path = folder / "screen.json"
                    reportio.write_report(screen_path, screen)
                    normalized = {"case_id": case_id, "source_sha256": source_hashes_before, "semantics": "independent",
                                  "correctness_pass": True, "strategy": "mixed_capacity/" + "-".join(map(str, configuration)),
                                  "profile": "mixed_capacity", "m": list(configuration), "models": list(map(str, bundle.paths)),
                                  "model_sha256": [corpus.digest_file(path) for path in bundle.paths],
                                  "model_identity_sha256": bundle.manifest["identity_sha256"], "kernel": "tetra_structured_avx2",
                                  "node_payload_bytes": row["node_payload_bytes"], "cube": quality,
                                  "evidence": [{"path": str(screen_path), "sha256": corpus.digest_file(screen_path)}], "official": False}
                    observation_path = folder / "observation.json"
                    reportio.write_report(observation_path, normalized)
                    identifier = book.record(observation_path)
                    record = {"case_id": case_id, "m": list(configuration), "observation_id": identifier,
                              "path": str(observation_path), "sha256": corpus.digest_file(observation_path),
                              "output_sha256": screen["output_sha256"], "node_payload_bytes": row["node_payload_bytes"]}
                    report["observations"].append(record)
                    report["pending_canonical_import"].append(record)
                    reportio.write_report(target, report)
                if [corpus.digest_file(path) for path in sources] != source_hashes_before or corpus.digest_file(truth_path) != analysis["reference_sha256"]:
                    raise RuntimeError("source/truth changed during native mapping")
                print(f"[mixed-native] {case_id}: {len(selected)} selected configurations match all RGB colours", flush=True)
            mixed = [row for row in report["observations"] if len(set(row["m"])) > 1]
            if not mixed:
                raise RuntimeError("declared search did not yield a mixed configuration for deployment checks")
            for selected in mixed[:2]:
                value = reportio.read_json(Path(selected["path"]))
                raw = temporary / "cuda.rgb"
                execution = runtime.cube([Path(path) for path in value["models"]], raw, backend="cuda", executable=cuda,
                                         kernel="cuda_q16_fused4", competition=True)
                report["new_native_full_cube_streams"] += 1
                if corpus.digest_file(raw) != selected["output_sha256"]:
                    raise RuntimeError("mixed stage sizes differ on CUDA")
                report["cuda_checks"].append({"observation_id": selected["observation_id"], "runtime": execution,
                                               "output_sha256": selected["output_sha256"]})
            selected = mixed[0]
            value = reportio.read_json(Path(selected["path"]))
            export = output / "mixed-rom"
            metadata = portable_export.export_models([Path(path) for path in value["models"]], export)
            compiled = output / "verify-mixed-rom.exe"
            build = execute(["E:/mingw64/bin/gcc.exe", "-std=c99", "-O2", "-Wall", "-Wextra", "-Wpedantic", "-Wconversion", "-Werror",
                             "-I", ROOT / "portable/include", "-I", export, export / "flash_chroma.c",
                             ROOT / "portable/src/jshc_portable.c", ROOT / "portable/tools/verify_exported_rom.c", "-o", compiled])
            raw = temporary / "rom.rgb"
            execution = execute([compiled, "cube", raw])
            report["new_native_full_cube_streams"] += 1
            if corpus.digest_file(raw) != selected["output_sha256"]:
                raise RuntimeError("compiled mixed C99 ROM differs from native CPU output")
            report["rom_check"] = {"observation_id": selected["observation_id"], "metadata": metadata,
                                   "build": build, "execution": execution, "output_sha256": selected["output_sha256"],
                                   "native_plan": json.loads(execution["stderr"])}
            source_bundle = Path(value["models"][0]).parent
            invalid = temporary / "invalid-bundle"
            shutil.copytree(source_bundle, invalid)
            bad_manifest = reportio.read_json(invalid / "manifest.json")
            bad_manifest["identity"]["parents"][1]["stage"] = 1
            bad_manifest["identity_sha256"] = cache.identity_key(bad_manifest["identity"])
            reportio.write_report(invalid / "manifest.json", bad_manifest)
            rejection = io.inspect_submission_contract([invalid / f"stage{s}.slut" for s in range(1, 5)], semantics="independent")
            if rejection["pass"]:
                raise RuntimeError("self-consistently hashed but misordered parent provenance was accepted")
            report["misordered_parent_rejected"] = rejection
        for name, digest in source_hashes.items():
            if corpus.digest_file(ROOT / name) != digest:
                raise RuntimeError("native/provenance verification source changed")
        for name, digest in binary_hashes.items():
            if corpus.digest_file(Path(name)) != digest:
                raise RuntimeError("native executable changed")
        if corpus.digest_file(training_path) != training_hash:
            raise RuntimeError("training analysis changed")
        report.update(pass_=True, finished_utc=datetime.now(timezone.utc).isoformat(), inputs_unchanged=True,
                      native_gate_complete=True, canonical_import_pending=len(report["observations"]))
        report["pass"] = report.pop("pass_")
        reportio.write_report(target, report)
        print(json.dumps({"pass": True, "selected_cpu_configurations": len(report["observations"]),
                          "full_native_streams": report["new_native_full_cube_streams"], "cuda_mixed_checks": len(report["cuda_checks"]),
                          "compiled_rom": True, "misordered_parent_rejected": True}))
    except BaseException as error:
        report.update(error={"type": type(error).__name__, "message": str(error)}, finished_utc=datetime.now(timezone.utc).isoformat())
        reportio.write_report(target, report)
        raise


if __name__ == "__main__":
    main()
