"""Verify capacity-priority max ties in addition to legacy p99-priority ties.

The analytical table retains all configurations. The first native gate follows
the casebook's max/p99/payload order; the declared capacity policy uses
max/payload/lexicographic order. Validate only the eight additional distinct
selections, keeping all previously executed streams and their receipts intact.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
import numpy as np
from lutlab import casebook, corpus, curve_search, io, reportio, runtime, stage_bundle, validation


def main():
    output = ROOT / "artifacts/r47-mixed-capacity"
    target = output / "payload-tie-gate.json"
    if target.exists():
        raise RuntimeError("preserve the completed tie-policy epoch")
    parent_path = output / "native-gate.json"
    parent = reportio.read_json(parent_path)
    training_path = output / "training.json"
    training = reportio.read_json(training_path)
    if not parent["pass"] or not training["analysis_pass"]:
        raise RuntimeError("completed search and first native gate required")
    names = ["scripts/r47_payload_tie_gate.py", "python/lutlab/stage_bundle.py", "python/lutlab/curve_search.py",
             "python/lutlab/io.py", "python/lutlab/cache.py", "python/lutlab/casebook.py",
             "python/lutlab/runtime.py", "python/lutlab/validation.py"]
    hashes = {name: corpus.digest_file(ROOT / name) for name in names}
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__, "source_sha256": hashes,
              "first_native_gate_sha256": corpus.digest_file(parent_path), "training_sha256": corpus.digest_file(training_path),
              "pass": False, "selections": [], "pending_canonical_import": [], "new_native_full_cube_streams": 0,
              "previously_verified_streams_reexecuted": 0, "holdout_outputs_read": False, "new_fits": 0, "official": False}
    known = {(row["case_id"], tuple(row["m"])): row for row in parent["observations"]}
    book = casebook.Casebook(output / "native-casebook")
    cpu = ROOT / "build-r35-structured/jshc.exe"
    cpu_hash = corpus.digest_file(cpu)
    try:
        with tempfile.TemporaryDirectory(prefix="r47-payload-") as temporary:
            for entry in training["cases"]:
                path = casebook._path(entry["analysis"])
                if corpus.digest_file(path) != entry["sha256"]:
                    raise RuntimeError("analytical configuration table changed")
                analysis = reportio.read_json(path)
                selected = min(analysis["configurations"], key=lambda row: (row["max"], row["node_payload_bytes"], row["m"]))
                configuration = tuple(selected["m"])
                case_id = entry["id"]
                if (case_id, configuration) in known:
                    report["selections"].append({"case_id": case_id, "m": list(configuration),
                                                "reused_observation_id": known[case_id, configuration]["observation_id"]})
                    continue
                parents = {(row["stage"] - 1, row["m"]): row for row in analysis["parent_models"]}
                parent_paths = [casebook._path(parents[stage, m]["path"]) for stage, m in enumerate(configuration)]
                folder = output / "cases" / case_id / ("payload-max-" + "-".join(map(str, configuration)))
                folder.mkdir()
                bundle = stage_bundle.assemble(parent_paths, folder / "models")
                raw = Path(temporary) / "cube.rgb"
                execution = runtime.cube(bundle.paths, raw, executable=cpu, kernel="tetra_structured_avx2", threads=4, competition=True)
                report["new_native_full_cube_streams"] += 1
                truth_path = ROOT / "data/corpus-v1/cases" / case_id / "composite.lut256"
                if corpus.digest_file(truth_path) != analysis["reference_sha256"]:
                    raise RuntimeError("source truth changed")
                expected = curve_search.compose([curve_search.model_curves(io.load_sparse(model, competition=True)) for model in bundle.paths])
                with validation._mapped_full(raw) as mapped, validation._mapped_full(truth_path) as truth:
                    if not np.array_equal(curve_search.target_curves(mapped), expected):
                        raise RuntimeError("native payload-priority selection differs on some RGB input")
                    quality = validation._cube_stats(mapped, truth, top_k=8, threshold=2.)
                if any(quality[name] != selected[name] for name in ("n_colors", "mean", "rms", "p99", "max", "pixels_at_or_above_threshold")):
                    raise RuntimeError("payload-priority full-cube quality differs from exact histogram")
                source_hashes = book.index["cases"][case_id]["source_sha256"]
                screen = {"kind": "casebook_native_cube_screen_v1", "case_id": case_id,
                          "source_sha256": source_hashes, "reference_sha256": analysis["reference_sha256"],
                          "runtime": execution, "output_sha256": corpus.digest_file(raw), "cube": quality,
                          "inputs_unchanged": corpus.digest_file(truth_path) == analysis["reference_sha256"],
                          "all_native_colors_equal_predicted_curves": True, "timing_is_benchmark": False}
                screen_path = folder / "screen.json"
                reportio.write_report(screen_path, screen)
                value = {"case_id": case_id, "source_sha256": source_hashes, "semantics": "independent", "correctness_pass": True,
                         "strategy": "mixed_capacity/" + "-".join(map(str, configuration)), "profile": "mixed_capacity", "m": list(configuration),
                         "models": list(map(str, bundle.paths)), "model_sha256": [corpus.digest_file(model) for model in bundle.paths],
                         "model_identity_sha256": bundle.manifest["identity_sha256"], "kernel": "tetra_structured_avx2",
                         "node_payload_bytes": selected["node_payload_bytes"], "cube": quality,
                         "evidence": [{"path": str(screen_path), "sha256": corpus.digest_file(screen_path)}], "official": False}
                evidence = folder / "observation.json"
                reportio.write_report(evidence, value)
                identifier = book.record(evidence)
                row = {"case_id": case_id, "m": list(configuration), "observation_id": identifier,
                       "path": str(evidence), "sha256": corpus.digest_file(evidence)}
                report["pending_canonical_import"].append(row)
                report["selections"].append(row)
                reportio.write_report(target, report)
                print("[payload-max] " + case_id + " " + str(configuration), flush=True)
        if len(report["selections"]) != 18 or report["new_native_full_cube_streams"] != 8:
            raise RuntimeError("declared pure-max tie selection coverage differs")
        for name, digest in hashes.items():
            if corpus.digest_file(ROOT / name) != digest:
                raise RuntimeError("verification source changed")
        if corpus.digest_file(cpu) != cpu_hash or corpus.digest_file(parent_path) != report["first_native_gate_sha256"]:
            raise RuntimeError("prior native proof/executable changed")
        report.update(pass_=True, inputs_unchanged=True, finished_utc=datetime.now(timezone.utc).isoformat())
        report["pass"] = report.pop("pass_")
        reportio.write_report(target, report)
        print(json.dumps({"pass": True, "payload_max_sources": 18, "reused_selections": 10, "new_native_full_cubes": 8}))
    except BaseException as error:
        report.update(error={"type": type(error).__name__, "message": str(error)}, finished_utc=datetime.now(timezone.utc).isoformat())
        reportio.write_report(target, report)
        raise


if __name__ == "__main__":
    main()
