"""Classify the completed solver study, retain case champions and package ROM.

Metadata/model validation only. The running canonical writer is not touched.
The failed original candidate stays in its original denominator. The recovered
model is compared against all 38 successful original alternatives on this case.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import casebook, corpus, reportio


def main():
    folder = ROOT / "artifacts/r51-solver-recovery"
    stage_path = folder / "stage.json"
    output = folder / "completed-stage.json"
    annotation_path = ROOT / "datasets/problem16-v1/annotations/r51-solver-boundaries.json"
    if output.exists() or annotation_path.exists():
        raise RuntimeError("preserve the existing completed classification epoch")
    study = reportio.read_json(stage_path)
    if not study["pass"] or not study["inputs_unchanged"] or not study["original_failure_preserved"] or not study.get("finished_utc"):
        raise RuntimeError("numerical qualification is incomplete")
    hashes = dict(study["source_sha256"])
    hashes[Path(__file__).relative_to(ROOT).as_posix()] = corpus.digest_file(Path(__file__))
    for name, digest in hashes.items():
        if corpus.digest_file(ROOT / name) != digest:
            raise RuntimeError("completed numerical source changed")
    for name, digest in study["binary_sha256"].items():
        if corpus.digest_file(Path(name)) != digest:
            raise RuntimeError("numerical executable changed")
    catalog_path = ROOT / "datasets/problem16-v1/catalog.json"
    catalog = {row["id"]: row for row in reportio.read_json(catalog_path)["cases"]}
    cid = study["pending_canonical_import"][0]["case_id"]
    source_manifest = reportio.read_json(ROOT / "data/corpus-v1/cases" / cid / "manifest.json")
    source_hashes = [row["sha256"] for row in source_manifest["stages"]]
    case = catalog[cid]
    book = casebook.Casebook(folder / "comparison-casebook")
    book.add_case(cid, {key: case[key] for key in ("family", "intensity", "seed", "split", "tags", "expected")}, source_hashes)
    references = []
    for name in ("r29-matrix", "r36-extension"):
        path = ROOT / "artifacts" / name / "regression.json"
        payload = path.read_bytes()
        state = json.loads(payload)
        if not state["phase_complete"]:
            raise RuntimeError("full regression reference changed")
        (folder / (name + "-regression-snapshot.json")).write_bytes(payload)
        for key, item in state["observations"].items():
            if key.split("/")[0] != cid:
                continue
            source = casebook._path(item["path"])
            if corpus.digest_file(source) != item["sha256"]:
                raise RuntimeError("immutable reference receipt changed")
            value = reportio.read_json(source)
            target = folder / "references" / key.replace("/", "--")
            target.mkdir(parents=True)
            shutil.copyfile(source, target / source.name)
            if item["status"] == "screened":
                if book.record(source) != item["observation_id"]:
                    raise RuntimeError("reference canonical ID differs")
                for proof in value["evidence"]:
                    p = casebook._path(proof["path"])
                    if corpus.digest_file(p) != proof["sha256"]:
                        raise RuntimeError("reference primary proof changed")
                    shutil.copyfile(p, target / p.name)
                for name in value["models"]:
                    model = casebook._path(name)
                    shutil.copyfile(model, target / model.name)
                shutil.copyfile(casebook._path(value["models"][0]).parent / "manifest.json", target / "manifest.json")
            else:
                book.record_failure(source)
                shutil.copyfile(source.parent / "fit.log", target / "fit.log")
            references.append({"key": key, "sha256": item["sha256"], "status": item["status"]})
    if len(references) != 39:
        raise RuntimeError("13-profile/three-size reference universe changed")
    for item in study["pending_canonical_import"]:
        source = casebook._path(item["path"])
        if corpus.digest_file(source) != item["sha256"] or book.record(source) != item["observation_id"]:
            raise RuntimeError("recovered observation differs")
    champions = book.index["cases"][cid]["champions"]
    mean = reportio.read_json(book.root / "observations" / (champions["best_measured_mean"] + ".json"))
    tail = reportio.read_json(book.root / "observations" / (champions["best_measured_max"] + ".json"))
    if (mean["cube"]["mean"] != study["reference_comparison"]["best_old_mean"]
            or tail["cube"]["max"] != study["reference_comparison"]["best_old_max"]):
        raise RuntimeError("expected observed quality scores changed")
    case_metadata = reportio.read_json(ROOT / "datasets/problem16-v1/casebook/index.json")["cases"][cid]
    if (case_metadata["champions"]["best_measured_mean"] != mean["observation_id"]
            or case_metadata["champions"]["best_measured_max"] != tail["observation_id"]):
        raise RuntimeError("running canonical quality champion differs from this complete comparison")
    reportio.write_report(book.root / "summary.json", book.summary())
    annotations = []
    for row in study["fits"]:
        metadata = catalog[row["case_id"]]
        fit = reportio.read_json(Path(row["manifest"]))
        recovery = []
        for stage, info in enumerate(fit["fit"]["stage_info"], 1):
            for channel in info["solver"]["channels"]:
                if len(channel["attempts"]) > 1:
                    recovery.append({"stage": stage, "channel": channel["channel"], "iterations": channel["iterations"],
                        "first_relative_residual": channel["attempts"][0]["relative_residual"],
                        "final_relative_residual": channel["attempts"][-1]["relative_residual"]})
        tags = ["bounded_cg_policy", "all_twelve_systems_converged"]
        tags += ["first_pass_only", "legacy_model_bytes_preserved"] if not recovery else ["cg_iteration_budget_boundary", "recovered_by_continuation", "hash_noise_accuracy_boundary"]
        annotations.append({"case_id": row["case_id"], "family": metadata["family"], "intensity": metadata["intensity"],
            "split": metadata["split"], "original_case_tags": metadata["tags"], "m": [row["m"]] * 4,
            "strategy": "dp_jitter_continued", "tags": tags, "source_sha256": [x["sha256"] for x in fit["identity"]["inputs"]],
            "model_identity_sha256": row["identity_sha256"], "manifest_sha256": row["manifest_sha256"], "recovered_channels": recovery})
    annotation = {"schema": 1, "kind": "supplemental_method_boundary_annotations_v1", "catalog_sha256": corpus.digest_file(catalog_path),
        "source_stage": {"path": casebook._portable(stage_path), "sha256": corpus.digest_file(stage_path)},
        "records": annotations, "original_case_ids_and_metadata_unchanged": True, "holdout_outputs_read": False,
        "scope": "five measured configurations; numerical solver residual is distinct from RGB prediction error",
        "recovered_case_quality_champions": {"case_id": cid,
            "mean_policy": {"cube": mean["cube"], "profile": mean["profile"], "m": mean["m"], "observation_id": mean["observation_id"]},
            "max_then_p99_policy": {"cube": tail["cube"], "profile": tail["profile"], "m": tail["m"], "observation_id": tail["observation_id"]},
            "new_solver_replaces_quality_champion": False}}
    reportio.write_report(annotation_path, annotation)
    # Preserve the integration shape failure and the metadata-stage assumption,
    # including the exact driver/solver sources for both failed attempts.
    shutil.copytree(ROOT / "artifacts/r51-solver-recovery-first-failure", folder / "failed-initial-shape-attempt")
    export = folder / "recovered-rom"
    package_dir = folder / "packages"
    package_dir.mkdir()
    package = package_dir / "recovered-adversarial-m33.zip"
    entries = {}
    with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED) as archive:
        def add(name, payload):
            archive.writestr(name, payload)
            entries[name] = {"sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)}
        for path in sorted(export.iterdir()):
            if path.is_file():
                add(path.name, path.read_bytes())
        for source, name in [("portable/include/jshc_portable.h", "include/jshc_portable.h"),
                             ("portable/src/jshc_portable.c", "src/jshc_portable.c"),
                             ("portable/tools/verify_exported_rom.c", "host/verify_exported_rom.c")]:
            add(name, (ROOT / source).read_bytes())
        readme = ("Recovered random/adversarial m33 model; not an accuracy-qualified model.\n"
            "CPU, CUDA and this compiled C99 ROM produce the same full RGB8 cube.\n"
            "Mean RGB distance: 128.83916568095952; max: 413.07868499839105.\n"
            f"The observed mean champion remains {mean['profile']}/m{mean['m'][0]}; the max/p99 champion remains {tail['profile']}/m{tail['m'][0]}.\n"
            "Host check: cc -std=c99 -O2 -Iinclude -I. flash_chroma.c src/jshc_portable.c host/verify_exported_rom.c -o verify\n"
            "Run: ./verify cube output.rgb\n"
            "Firmware uses const ROM arrays plus caller-owned workspace; host/ is only a verification example.\n"
            "The 64-bit host measured 12560 workspace bytes; this is not a phone memory/performance measurement.\n")
        add("README.txt", readme.encode())
    with zipfile.ZipFile(package) as archive:
        for name, expected in entries.items():
            if hashlib.sha256(archive.read(name)).hexdigest() != expected["sha256"]:
                raise RuntimeError("ROM package readback failed")
    for name, digest in hashes.items():
        if corpus.digest_file(ROOT / name) != digest:
            raise RuntimeError("finalization source changed")
    result = {"started_utc": study["started_utc"], "finished_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__,
        "pass": True, "source_sha256": hashes, "inputs_unchanged": True,
        "numerical_stage": {"path": str(stage_path), "sha256": corpus.digest_file(stage_path)},
        "fit_configurations": 5, "legacy_byte_equal_configurations": 4, "recovered_failed_configurations": 1,
        "new_native_full_cube_streams": 3, "new_pixel_executions_in_finalizer": 0,
        "reference_configurations": 39, "reference_valid": 38, "reference_failed_preserved": 1,
        "comparison_casebook_valid_observations": len(book.index["cases"][cid]["observations"]),
        "accuracy_champion_unchanged": True,
        "mean_champion": {"profile": mean["profile"], "m": mean["m"], "cube": mean["cube"]},
        "max_then_p99_champion": {"profile": tail["profile"], "m": tail["m"], "cube": tail["cube"]},
        "annotations": {"path": str(annotation_path), "sha256": corpus.digest_file(annotation_path)},
        "rom_package": {"path": str(package), "sha256": corpus.digest_file(package), "bytes": package.stat().st_size,
                        "readback_verified": True, "files": entries},
        "pending_canonical_import": study["pending_canonical_import"], "canonical_mutations": 0,
        "scope_boundary": "solver recovery established; hash-noise accuracy remains poor; no class/population guarantee",
        "previous_goal_turn_classification": "progress", "current_goal_turn_classification": "progress",
        "holdout_outputs_read": False, "timing_is_benchmark": False, "full_user_goal_complete": False, "official": False}
    reportio.write_report(output, result)
    print(json.dumps({"pass": True, "annotated_configurations": len(annotations),
        "case_comparison_valid_observations": result["comparison_casebook_valid_observations"],
        "mean_champion": mean["profile"] + "/m" + str(mean["m"][0]),
        "max_then_p99_champion": tail["profile"] + "/m" + str(tail["m"][0]),
        "new_solver_does_not_replace_accuracy_champion": True,
        "rom_package_bytes": package.stat().st_size, "canonical_import_pending": len(study["pending_canonical_import"])}))


if __name__ == "__main__":
    main()
