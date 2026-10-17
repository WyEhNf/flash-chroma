"""Concentrated image-path qualification for selected training models.

Two native full-cube streams and two actual 100-image executions per case qualify
structured CPU/CUDA paths. Five known photos per case also compare the portable
C99 optimized/generic paths. No timing benchmark, new fitting or holdout is run.
The live canonical ledger is untouched; verified records queue for later import.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
sys.path.insert(0, str(ROOT))
import numpy as np
from lutlab import casebook, corpus, io, reportio, runtime, validation
from scripts.r30_portable_stage import Prepared, load_library


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--append-case", nargs=3, action="append", default=[], metavar=("CASE", "PROFILE", "M"),
                        help="append a distinct development/calibration case without rerunning committed cases")
    args = parser.parse_args()
    output = ROOT / "artifacts/r45-representative-images"
    output.mkdir(exist_ok=True)
    target = output / "stage.json"
    if target.exists() and not args.append_case:
        raise RuntimeError("preserve this qualification epoch before rerunning")
    names = ["scripts/r45_representative_images.py", "scripts/r30_portable_stage.py", "python/lutlab/validation.py",
             "python/lutlab/runtime.py", "python/lutlab/casebook.py", "portable/src/jshc_portable.c", "portable/include/jshc_portable.h"]
    source_hashes = {name: corpus.digest_file(ROOT / name) for name in names}
    phase_path = ROOT / "artifacts/r36-extension/development.json"
    phase_hash = corpus.digest_file(phase_path)
    phase = reportio.read_json(phase_path)
    if not phase["phase_complete"] or len(phase["observations"]) != 720:
        raise RuntimeError("requires completed extension development results")
    calibration_path = ROOT / "artifacts/r36-extension/calibration.json"
    calibration_hash = corpus.digest_file(calibration_path)
    calibration = reportio.read_json(calibration_path)
    if not calibration["phase_complete"] or len(calibration["observations"]) != 720:
        raise RuntimeError("requires completed extension calibration results")
    cpu = ROOT / "build-r35-structured/jshc.exe"
    cuda = ROOT / "build-r32-format-gpu/jshc_gpu.exe"
    portable = ROOT / "build-r30-portable/libjshc_portable.dll"
    listing = ROOT / "data/corpus-v1/benchmark100.txt"
    photos_path = ROOT / "datasets/problem16-photos-v1/catalog.json"
    photos = reportio.read_json(photos_path)
    photo_paths = [ROOT / row["path"] for row in photos["images"]]
    frames = [Path(line) for line in listing.read_text(encoding="utf-8").splitlines() if line]
    hashes = {str(path): corpus.digest_file(path) for path in [cpu, cuda, portable, listing, photos_path, *frames, *photo_paths]}
    if len(frames) != 100 or len({hashes[str(path)] for path in frames}) != 100:
        raise RuntimeError("requires all 100 distinct registered images")
    for row, path in zip(photos["images"], photo_paths):
        if hashes[str(path)] != row["file_sha256"]:
            raise RuntimeError("registered photo changed")
    selected = [(case_id, profile, int(m)) for case_id, profile, m in args.append_case] if args.append_case else [
        ("quantize_early-strong-s0-50f0ff15", "reachable_bins", 25),
        ("axis_posterize-medium-s0-1aecbc86", "lookahead_bins", 25),
    ]
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__, "pass": False,
              "source_sha256": source_hashes, "completed_development_sha256": phase_hash,
              "input_and_binary_sha256": hashes, "cases": [], "pending_canonical_import": [],
              "new_fits": 0, "timing_is_benchmark": False, "holdout_outputs_read": False,
              "local_quality_gate": {"threshold": 2., "metric": "mean", "scope": "all 100 images and whole cube", "official": False},
              "image_cohort_scope": "fixed corpus-v1 throughput/format cohort; not an independent transform holdout",
              "photo_scope": "five known Kodak images; not a new-family blind test", "official": False}
    if args.append_case:
        previous_path = output / "completed-before-append/stage.json"
        previous_driver = output / "completed-before-append/driver.py"
        previous = reportio.read_json(previous_path)
        if (not previous["pass"] or corpus.digest_file(target) != corpus.digest_file(previous_path)
                or previous["completed_development_sha256"] != phase_hash
                or corpus.digest_file(previous_driver) != previous["source_sha256"]["scripts/r45_representative_images.py"]):
            raise RuntimeError("append requires the preserved successful two-case epoch")
        for name, digest in previous["source_sha256"].items():
            if name != "scripts/r45_representative_images.py" and corpus.digest_file(ROOT / name) != digest:
                raise RuntimeError("previously qualified implementation changed")
        for name, digest in previous["input_and_binary_sha256"].items():
            if corpus.digest_file(Path(name)) != digest:
                raise RuntimeError("previously qualified input/executable changed")
        for row in previous["cases"]:
            if corpus.digest_file(casebook._path(row["acceptance"])) != row["acceptance_sha256"]:
                raise RuntimeError("committed qualification receipt changed")
        for row in previous["pending_canonical_import"]:
            if corpus.digest_file(casebook._path(row["path"])) != row["sha256"]:
                raise RuntimeError("committed normalized qualification changed")
        existing = {(row["case_id"], row["profile"], row["m"]) for row in previous["cases"]}
        if existing.intersection(selected) or len(set(selected)) != len(selected):
            raise RuntimeError("append would rerun an already committed case")
        hashes.update(previous["input_and_binary_sha256"])
        report.update(previous)
        report.pop("finished_utc", None)
        report.update(source_sha256=source_hashes, input_and_binary_sha256=hashes, scope=__doc__)
        report["pass"] = False
        report["append_epoch"] = {"previous_stage_sha256": corpus.digest_file(previous_path),
                                  "previous_stage": str(previous_path), "previous_source_sha256": corpus.digest_file(previous_driver),
                                  "reused_qualified_cases": len(previous["cases"]), "new_selected_cases": selected,
                                  "started_utc": datetime.now(timezone.utc).isoformat()}
    report["completed_calibration_sha256"] = calibration_hash
    reportio.write_report(target, report)
    definition = reportio.read_json(ROOT / "datasets/problem16-v1/catalog.json")
    lookup = {row["id"]: row for row in definition["cases"]}
    book = casebook.Casebook(output / "qualified-casebook")
    library = load_library(portable.resolve())
    try:
        for case_id, profile, m in selected:
            if lookup[case_id]["split"] not in ("development", "calibration"):
                raise RuntimeError("this qualification stage cannot read holdout model outputs")
            selected_phase = phase if lookup[case_id]["split"] == "development" else calibration
            item = selected_phase["observations"][f"{case_id}/{profile}/m{m}"]
            observation_path = casebook._path(item["path"])
            if corpus.digest_file(observation_path) != item["sha256"]:
                raise RuntimeError("selected completed observation changed")
            observation = reportio.read_json(observation_path)
            original_proof = casebook._path(observation["evidence"][0]["path"])
            if corpus.digest_file(original_proof) != observation["evidence"][0]["sha256"]:
                raise RuntimeError("prior whole-cube execution changed")
            primary = reportio.read_json(original_proof)
            models = [casebook._path(path) for path in observation["models"]]
            sources = [ROOT / "data/corpus-v1/cases" / case_id / f"lut{s}.lut256" for s in range(1, 5)]
            truth = sources[0].parent / "composite.lut256"
            for path in [*sources, truth, *models]:
                hashes[str(path)] = corpus.digest_file(path)
            if ([hashes[str(path)] for path in sources] != observation["source_sha256"]
                    or [hashes[str(path)] for path in models] != observation["model_sha256"]
                    or hashes[str(truth)] != primary["reference_sha256"]):
                raise RuntimeError("selected source/model/reference bytes changed")
            folder = output / case_id
            folder.mkdir()
            acceptance = {"sources": [{"path": str(path), "sha256": hashes[str(path)]} for path in sources],
                          "reference_sha256": hashes[str(truth)], "structural_contract_pass": True, "official": False,
                          "prior_screen_sha256": observation["evidence"][0]["sha256"], "backends": {}}
            for backend, binary, kernel, threads in (("cpu", cpu, "tetra_structured_avx2", 4),
                                                      ("cuda", cuda, "cuda_q16_fused4", 0)):
                value = validation.validate(models, truth, listing, kernel=kernel, threads=threads, threshold=2.,
                    full_cube=True, executable=binary, constraint_scope="both", competition=True, backend=backend)
                if (not value["submission_contract_pass"] or not value["image_execution_verified"]
                        or value["mapped_cube_sha256"] != primary["output_sha256"]
                        or any(value["cube"][metric] != observation["cube"][metric] for metric in ("n_colors", "mean", "rms", "p99", "max"))):
                    raise RuntimeError("new native backend differs from the completed cube or image/format contract")
                acceptance["backends"][backend] = value
                reportio.write_report(folder / "acceptance.json", acceptance)
                print(f"[representative] {case_id} {backend}: actual100 worst_mean={value['worst_image_metric']:.9f}", flush=True)
            acceptance["backend_cube_sha256_equal"] = len({value["mapped_cube_sha256"] for value in acceptance["backends"].values()}) == 1
            acceptance["backend_images_sha256_equal"] = len({value["mapped_images_sha256"] for value in acceptance["backends"].values()}) == 1
            if not acceptance["backend_cube_sha256_equal"] or not acceptance["backend_images_sha256_equal"]:
                raise RuntimeError("CPU/CUDA output bytes disagree")
            acceptance_path = folder / "acceptance.json"
            reportio.write_report(acceptance_path, acceptance)
            prepared = Prepared(library, models)
            photo_records = []
            with validation._mapped_full(truth) as reference, tempfile.TemporaryDirectory(prefix="r45-photo-") as temporary:
                for photo, path in zip(photos["images"], photo_paths):
                    image = io.load_image(path)
                    expected = prepared.apply(image)
                    if not np.array_equal(expected, prepared.apply(image, generic=True)):
                        raise RuntimeError("portable optimized/generic photo outputs differ")
                    record = {"id": photo["id"], "input_sha256": hashes[str(path)],
                              "quality": validation._stats(expected, io.apply_full(reference, image))[0],
                              "portable_optimized_equals_generic": True, "backends": {}}
                    for backend, binary, kernel, threads in (("cpu", cpu, "tetra_structured_avx2", 4),
                                                              ("cuda", cuda, "cuda_q16_fused4", 0)):
                        destination = Path(temporary) / (backend + ".png")
                        execution = runtime.apply(models, path, destination, backend=backend, executable=binary,
                                                   kernel=kernel, threads=threads, competition=True)
                        if not np.array_equal(io.load_image(destination), expected):
                            raise RuntimeError("portable/CPU/CUDA photo outputs disagree")
                        record["backends"][backend] = execution
                    photo_records.append(record)
            # Only this isolated qualification book is mutated while R38 owns
            # the canonical writer lease. The pending receipts retain exact IDs.
            case = lookup[case_id]
            book.add_case(case_id, {key: case[key] for key in ("family", "intensity", "seed", "split", "tags", "expected")}, observation["source_sha256"])
            value = acceptance["backends"]["cpu"]
            normalized = {**observation, "kernel": value["kernel"], "cube": value["cube"],
                "images": {"count": 100, "native_verified": True, "list_sha256": value["image_list_sha256"],
                           "worst_mean": max(row["mean"] for row in value["per_image"]),
                           "illustrative_mean_pass": all(row["mean"] < 2 for row in value["per_image"]) and value["cube"]["mean"] < 2,
                           "cpu_cuda_byte_equal": True},
                "evidence": [{"path": str(acceptance_path), "sha256": corpus.digest_file(acceptance_path)}]}
            normalized_path = folder / "observation.json"
            reportio.write_report(normalized_path, normalized)
            identifier = book.record(normalized_path)
            receipt = {"case_id": case_id, "observation_id": identifier, "path": str(normalized_path), "sha256": corpus.digest_file(normalized_path)}
            report["pending_canonical_import"].append(receipt)
            report["cases"].append({"case_id": case_id, "profile": profile, "m": m,
                                    "acceptance": str(acceptance_path), "acceptance_sha256": corpus.digest_file(acceptance_path),
                                    "cube": observation["cube"], "worst_image_mean": normalized["images"]["worst_mean"],
                                    "illustrative_mean_pass": normalized["images"]["illustrative_mean_pass"],
                                    "photos5": photo_records})
            reportio.write_report(target, report)
        for name, digest in source_hashes.items():
            if corpus.digest_file(ROOT / name) != digest:
                raise RuntimeError("qualification source changed during stage")
        for name, digest in hashes.items():
            if corpus.digest_file(Path(name)) != digest:
                raise RuntimeError("qualification input/executable changed during stage")
        if corpus.digest_file(phase_path) != phase_hash or corpus.digest_file(calibration_path) != calibration_hash:
            raise RuntimeError("completed training phase changed")
        report.update(pass_=True, finished_utc=datetime.now(timezone.utc).isoformat(), inputs_unchanged=True)
        report["pass"] = report.pop("pass_")
        reportio.write_report(target, report)
        reportio.write_report(output / "pending-canonical-import.json", {"observations": report["pending_canonical_import"],
            "required_writer_lease": "artifacts/r29-matrix/phase-controller.lock", "imported_to_canonical": False})
        count = len(report["cases"])
        print(json.dumps({"pass": True, "qualified_cases": count, "native_full_cubes": 2 * count,
                          "actual_standard_image_executions": 200 * count, "known_photo_executions_cpu_cuda_c99": 20 * count,
                          "new_fits": 0, "new_benchmarks": 0, "canonical_import_pending": count}))
    except BaseException as error:
        report.update(error={"type": type(error).__name__, "message": str(error)}, finished_utc=datetime.now(timezone.utc).isoformat())
        reportio.write_report(target, report)
        raise


if __name__ == "__main__":
    main()
