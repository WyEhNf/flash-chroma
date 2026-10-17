"""Bind completed R39 mapping timings to per-case quality/runtime choices.

The six new-kernel cube executions are reused from R35. Three ordinary gather
cubes run once because that particular build/kernel/model combination lacks a
prior case-specific cube receipt. All output hashes must match the frozen
quality proof; no fitting or new speed measurements occur in this stage.
"""
from __future__ import annotations

from datetime import datetime, timezone
import copy
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import casebook, corpus, reportio, runtime, timingbook


def main():
    output = ROOT / "artifacts/r40-runtime-registry"
    output.mkdir(exist_ok=True)
    target = output / "stage.json"
    if target.exists():
        raise RuntimeError("preserve this registration epoch before rerunning")
    lease = ROOT / "artifacts/r29-matrix/phase-controller.lock"
    with lease.open("x", encoding="utf-8") as stream:
        json.dump({"pid": os.getpid(), "owner": "R40 runtime/canonical registry writer"}, stream)
    try:
        run(output, target)
    finally:
        lease.unlink()


def run(output, target):
    timing_path = ROOT / "artifacts/r39-structured-performance/comparison.json"
    native_path = ROOT / "artifacts/r35-structured-runtime/stage.json"
    timed = reportio.read_json(timing_path)
    native = reportio.read_json(native_path)
    if not timed["pass"] or not native["pass"]:
        raise RuntimeError("requires completed quality and performance stages")
    binary = ROOT / "build-r35-structured/jshc.exe"
    if corpus.digest_file(binary) != native["builds"]["simd"]["binary_sha256"]:
        raise RuntimeError("validated binary changed")
    sources = ["scripts/r40_register_runtimes.py", "python/lutlab/casebook.py", "python/lutlab/timingbook.py",
               "python/lutlab/runtime.py", "python/lutlab/reportio.py"]
    hashes = {name: corpus.digest_file(ROOT / name) for name in sources}
    book = casebook.Casebook(ROOT / "datasets/problem16-v1/casebook")
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__, "pass": False,
              "source_sha256": hashes, "timing_evidence_sha256": corpus.digest_file(timing_path),
              "quality_evidence_sha256": corpus.digest_file(native_path), "timing_is_benchmark": False,
              "new_speed_measurements": 0, "new_gather_cubes": [], "registered": [], "negative_metadata_controls": []}
    reportio.write_report(target, report)
    with tempfile.TemporaryDirectory(prefix="r40-gather-") as temporary:
        for case_label in ("historical-clip-m17", "new-stress-m33", "new-bins17-m17"):
            model = next(row for row in native["cases"] if row["name"] == case_label)
            paths = [casebook._path(path) for path in model["models"]]
            proof_path = casebook._path(model["evidence"])
            if corpus.digest_file(proof_path) != model["evidence_sha256"]:
                raise RuntimeError("frozen quality evidence changed")
            proof = reportio.read_json(proof_path)
            source_hashes = [row["sha256"] for row in proof["sources"]] if "backends" in proof else proof["source_sha256"]
            quality = proof["backends"]["cpu"]["cube"] if "backends" in proof else proof["cube"]
            reference = proof["reference_sha256"]
            cube_hash = proof["backends"]["cpu"]["mapped_cube_sha256"] if "backends" in proof else proof["output_sha256"]
            if cube_hash != model["cube_sha256"] or [corpus.digest_file(path) for path in paths] != model["model_sha256"]:
                raise RuntimeError("cube/model source binding differs")
            matches = []
            for case_id, case in book.index["cases"].items():
                if case["source_sha256"] != source_hashes: continue
                for identifier in case["observations"]:
                    row = reportio.read_json(book.root / "observations" / (identifier + ".json"))
                    if row["model_sha256"] == model["model_sha256"]:
                        exact_path = [casebook._path(path) for path in row["models"]] == paths
                        matches.append((not exact_path, case_id, row))
            if not matches:
                raise RuntimeError("no quality-bound existing case/model observation")
            _, case_id, template = sorted(matches, key=lambda value: (value[0], value[1], value[2]["observation_id"]))[0]
            gathered = Path(temporary) / "cube.rgb"
            gather_execution = runtime.cube(paths, gathered, executable=binary, kernel="tetra_avx2_scalar_gather", threads=16, competition=True)
            if corpus.digest_file(gathered) != cube_hash:
                raise RuntimeError("new gather case-specific cube differs from frozen quality")
            report["new_gather_cubes"].append({"case_label": case_label, "runtime": gather_execution, "cube_sha256": cube_hash})
            for configuration, kernel in timed["configurations"].items():
                execution = gather_execution if configuration == "gather16" else model["backends"][kernel]["cube"]
                folder = output / case_label / configuration
                folder.mkdir(parents=True)
                primary = {"kind": "casebook_native_cube_screen_v1", "case_id": case_id,
                    "source_sha256": source_hashes, "reference_sha256": reference, "runtime": execution,
                    "cube": quality, "output_sha256": cube_hash, "inputs_unchanged": True,
                    "quality_reuse": {"path": str(proof_path), "sha256": corpus.digest_file(proof_path),
                        "reason": "identical complete output SHA256 and bound source/reference/model bytes"},
                    "native_execution_reused_from_r35": configuration != "gather16", "timing_is_benchmark": False}
                primary_path = folder / "quality.json"
                reportio.write_report(primary_path, primary)
                value = {key: copy.deepcopy(data) for key, data in template.items() if key not in
                         ("observation_id", "record_source", "images", "performance")}
                value.update(kernel=kernel, cube=quality, models=list(map(str, paths)),
                    performance=timingbook.normalize(timing_path, case_label, configuration),
                    evidence=[{"path": str(primary_path), "sha256": corpus.digest_file(primary_path)},
                              {"path": str(timing_path), "sha256": report["timing_evidence_sha256"]},
                              {"path": str(native_path), "sha256": report["quality_evidence_sha256"]},
                              {"path": str(proof_path), "sha256": corpus.digest_file(proof_path)}])
                # These metadata controls exercise real evidence validation,
                # without repeating pixel or timing measurements.
                if not report["negative_metadata_controls"]:
                    for field, bad in (("kernel", "tri_float"), ("median_set_ms", 0.), ("resource_group", "unbound")):
                        wrong = copy.deepcopy(value)
                        if field == "kernel": wrong["kernel"] = bad
                        else: wrong["performance"][field] = bad
                        try: timingbook.validate(wrong)
                        except ValueError: report["negative_metadata_controls"].append(field)
                        else: raise RuntimeError("unbound timing metadata was accepted")
                destination = folder / "observation.json"
                reportio.write_report(destination, value)
                identifier = book.record(destination)
                report["registered"].append({"case_id": case_id, "case_label": case_label, "configuration": configuration,
                    "observation_id": identifier, "path": str(destination), "sha256": corpus.digest_file(destination)})
                reportio.write_report(target, report)
            print("[runtime registry] " + case_id + ": three kernels bound to exact quality and paired resources", flush=True)
    for name, digest in hashes.items():
        if corpus.digest_file(ROOT / name) != digest: raise RuntimeError("registration source changed")
    if corpus.digest_file(timing_path) != report["timing_evidence_sha256"] or corpus.digest_file(native_path) != report["quality_evidence_sha256"]:
        raise RuntimeError("completed stage changed")
    report["case_runtime_policies"] = {case: book.index["cases"][case]["champions"]["speed"] for case in
                                      sorted({row["case_id"] for row in report["registered"]})}
    reportio.write_report(book.root / "summary.json", book.summary())
    report.update(pass_=True, finished_utc=datetime.now(timezone.utc).isoformat(), new_pixel_cube_executions=3)
    report["pass"] = report.pop("pass_")
    reportio.write_report(target, report)
    print(json.dumps({"pass": True, "runtime_observations": len(report["registered"]), "new_speed_measurements": 0,
                      "case_ids": list(report["case_runtime_policies"])}), flush=True)


if __name__ == "__main__":
    main()
