"""Compute the predeclared complete training search before native validation.

All 1458 configurations use exact, fully proven full-RGB histogram counts. The
54 uniform configurations must match existing native whole-cube results. This
analysis does not run new native pixels, fit models, freeze rules or read heldout.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
import numpy as np
from lutlab import casebook, corpus, curve_search, io, reportio, validation


def main():
    output = ROOT / "artifacts/r47-mixed-capacity"
    output.mkdir(exist_ok=True)
    target = output / "training.json"
    if target.exists():
        raise RuntimeError("preserve this declared analysis epoch before rerunning")
    plan_path = ROOT / "datasets/problem16-v1/mixed-capacity-plan-r47.json"
    plan = reportio.read_json(plan_path)
    source_names = ["scripts/r47_mixed_capacity_study.py", "scripts/r47_mixed_capacity_plan.py",
                    "python/lutlab/curve_search.py", "python/lutlab/stage_bundle.py", "python/lutlab/io.py",
                    "python/lutlab/interp.py", "python/lutlab/validation.py", "python/lutlab/cache.py"]
    hashes = {name: corpus.digest_file(ROOT / name) for name in source_names}
    states = {}
    phase_evidence = {}
    for phase in ("development", "calibration"):
        path = ROOT / "artifacts/r36-extension" / (phase + ".json")
        state = reportio.read_json(path)
        if not state["phase_complete"] or len(state["observations"]) != 720:
            raise RuntimeError("complete parent training phases required")
        states[phase] = state
        phase_evidence[phase] = {"path": str(path), "sha256": corpus.digest_file(path)}
    cases = [case for case in plan["cases"] if case["split"] in states]
    if len(cases) != 18 or len(plan["configurations"]) != 81 or plan["original_matrix_candidates_unchanged"] != 7917:
        raise RuntimeError("predeclared universe changed")
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__, "source_sha256": hashes,
              "plan_sha256": corpus.digest_file(plan_path), "parent_training_reports": phase_evidence,
              "cases": [], "analytic_configurations": 0, "uniform_native_statistics_matched": 0,
              "analysis_pass": False, "native_gate_complete": False, "new_fits": 0, "new_native_pixel_executions": 0,
              "holdout_outputs_read": False, "class_sweet_zone_proven": False, "official": False}
    reportio.write_report(target, report)
    try:
        for case in cases:
            case_id = case["id"]
            folder = output / "cases" / case_id
            folder.mkdir(parents=True)
            manifest_path = ROOT / "data/corpus-v1/cases" / case_id / "manifest.json"
            source_manifest = reportio.read_json(manifest_path)
            truth_path = manifest_path.parent / "composite.lut256"
            if corpus.digest_file(truth_path) != source_manifest["composite"]["sha256"]:
                raise RuntimeError("full source-chain truth changed")
            with validation._mapped_full(truth_path) as truth:
                target_curves = curve_search.target_curves(truth)
            observations = {}
            models = {stage: {} for stage in range(4)}
            curves = {stage: {} for stage in range(4)}
            proofs = []
            for m in plan["stage_sizes"]:
                item = states[case["split"]]["observations"][f"{case_id}/adaptive_bins/m{m}"]
                path = casebook._path(item["path"])
                if item["status"] != "screened" or corpus.digest_file(path) != item["sha256"]:
                    raise RuntimeError("parent observation changed or failed")
                value = reportio.read_json(path)
                if (value["source_sha256"] != [row["sha256"] for row in source_manifest["stages"]]
                        or value["m"] != [m] * 4 or value["profile"] != "adaptive_bins"):
                    raise RuntimeError("parent source/profile/budget differs")
                for proof in value["evidence"]:
                    if corpus.digest_file(casebook._path(proof["path"])) != proof["sha256"]:
                        raise RuntimeError("parent whole-cube numerical receipt changed")
                observations[m] = value
                for stage, (name, expected) in enumerate(zip(value["models"], value["model_sha256"])):
                    model_path = casebook._path(name)
                    if corpus.digest_file(model_path) != expected:
                        raise RuntimeError("parent model bytes changed")
                    model = io.load_sparse(model_path, competition=True)
                    models[stage][m] = model_path
                    curves[stage][m] = curve_search.model_curves(model)
                    proofs.append({"stage": stage + 1, "m": m, "path": str(model_path), "sha256": expected,
                                   "complete_node_count": m ** 3, "integer_curve_sha256": hashlib.sha256(curves[stage][m].tobytes()).hexdigest()})
            rows = []
            for configuration in plan["configurations"]:
                selected = [curves[stage][m] for stage, m in enumerate(configuration)]
                predicted = curve_search.compose(selected)
                hist = curve_search.error_histogram(predicted, target_curves)
                stats = curve_search.statistics(hist)
                if len(set(configuration)) == 1:
                    parent = observations[configuration[0]]["cube"]
                    if any(stats[name] != parent[name] for name in stats):
                        raise RuntimeError("exact factorized uniform statistics differ from existing native full cube: " + case_id)
                    report["uniform_native_statistics_matched"] += 1
                rows.append({"m": configuration, **stats, "node_payload_bytes": sum(3 * m ** 3 for m in configuration),
                             "serialized_model_bytes": sum(models[stage][m].stat().st_size for stage, m in enumerate(configuration)),
                             "error_histogram_sha256": hashlib.sha256(hist.tobytes()).hexdigest()})
            mean = min(rows, key=lambda row: (row["mean"], row["node_payload_bytes"], row["m"]))
            tail = min(rows, key=lambda row: (row["max"], row["p99"], row["node_payload_bytes"], row["m"]))
            uniform = [row for row in rows if len(set(row["m"])) == 1]
            uniform_mean = min(uniform, key=lambda row: (row["mean"], row["node_payload_bytes"], row["m"]))
            record = {"case": case, "source_manifest_sha256": corpus.digest_file(manifest_path),
                      "reference_sha256": source_manifest["composite"]["sha256"],
                      "target_complete_color_proof": 256 ** 3, "target_integer_curves": target_curves.tolist(),
                      "parent_models": proofs, "configurations": rows, "pareto": curve_search.pareto(rows),
                      "best_mean": mean, "best_max": tail, "best_uniform_mean": uniform_mean,
                      "mean_improvement_vs_best_uniform": uniform_mean["mean"] - mean["mean"],
                      "scope": "exact full-RGB analytical histogram; new mixed native execution pending"}
            case_path = folder / "analysis.json"
            reportio.write_report(case_path, record)
            report["cases"].append({"id": case_id, "analysis": str(case_path), "sha256": corpus.digest_file(case_path),
                                    "best_mean": mean, "best_max": tail, "best_uniform_mean": uniform_mean})
            report["analytic_configurations"] += len(rows)
            reportio.write_report(target, report)
            print(f"[capacity] {len(report['cases'])}/18 {case_id}: uniform_mean={uniform_mean['mean']:.9f}, mixed_mean={mean['mean']:.9f}, m={mean['m']}", flush=True)
            if corpus.digest_file(truth_path) != source_manifest["composite"]["sha256"]:
                raise RuntimeError("truth changed during complete diagonal proof/search")
        for name, digest in hashes.items():
            if corpus.digest_file(ROOT / name) != digest:
                raise RuntimeError("analysis source changed")
        for row in phase_evidence.values():
            if corpus.digest_file(Path(row["path"])) != row["sha256"]:
                raise RuntimeError("complete parent training changed")
        if report["analytic_configurations"] != 1458 or report["uniform_native_statistics_matched"] != 54:
            raise RuntimeError("declared training search incomplete")
        report.update(analysis_pass=True, finished_utc=datetime.now(timezone.utc).isoformat())
        reportio.write_report(target, report)
        print(json.dumps({"analysis_pass": True, "analytic_configurations": 1458, "existing_native_uniforms_matched": 54,
                          "sources_improved_mean": sum(row["best_mean"]["mean"] < row["best_uniform_mean"]["mean"] for row in report["cases"]),
                          "new_native_pixel_executions": 0}))
    except BaseException as error:
        report.update(error={"type": type(error).__name__, "message": str(error)}, finished_utc=datetime.now(timezone.utc).isoformat())
        reportio.write_report(target, report)
        raise


if __name__ == "__main__":
    main()
