"""Evaluate the frozen mixed-capacity guide on all nine declared held-out sources.

Requires both original full-training rules and complete R36 holdout parents.
Regret is selected error minus the feasible per-source oracle at the same node
budget. Nothing here tunes or rewrites the guide after seeing held-out results.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
import numpy as np
from lutlab import casebook, corpus, curve_search, io, reportio, runtime, stage_bundle, validation
from r42_training_comparison import write_csv


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--combined-rule", type=Path, default=ROOT / "datasets/problem16-v1/class-rules-combined-r41.json")
    parser.add_argument("--inspect-only", action="store_true", help="check prerequisite file presence only; do not read holdout output contents")
    args = parser.parse_args()
    plan_path = ROOT / "datasets/problem16-v1/mixed-capacity-plan-r47.json"
    rule_path = ROOT / "datasets/problem16-v1/mixed-capacity-rules-r47.json"
    parent_path = ROOT / "artifacts/r36-extension/holdout.json"
    prerequisites = {"original_combined_rule": args.combined_rule.exists(), "mixed_rule": rule_path.exists(),
                     "parent_holdout_index": parent_path.exists()}
    if args.inspect_only:
        print(json.dumps({"prerequisite_files_present": prerequisites, "holdout_outputs_read": False,
                          "parent_completion_not_checked": True, "evaluation_executed": False}))
        return
    if not all(prerequisites.values()):
        raise RuntimeError("holdout prerequisites missing; do not generate or inspect strategy outputs")
    combined = reportio.read_json(args.combined_rule)
    rule = reportio.read_json(rule_path)
    plan = reportio.read_json(plan_path)
    if (not combined["frozen_before_holdout"] or not rule["frozen_before_any_holdout_strategy_outputs"]
            or rule["plan_sha256"] != corpus.digest_file(plan_path)
            or combined["extension_plan_sha256"] != plan["parent_extension_plan_sha256"]):
        raise RuntimeError("rules do not bind the declared studies")
    for role in ("baseline_development", "baseline_calibration", "extension_development", "extension_calibration"):
        item = combined["training_reports"][role]
        path = casebook._path(item["path"])
        if corpus.digest_file(path) != item["sha256"] or not reportio.read_json(path)["phase_complete"]:
            raise RuntimeError("original training/freeze contract is incomplete")
    for item in rule["training_evidence"]:
        if corpus.digest_file(casebook._path(item["path"])) != item["sha256"]:
            raise RuntimeError("frozen mixed training evidence changed")
    parent = reportio.read_json(parent_path)
    if (not parent["phase_complete"] or len(parent["observations"]) != 720
            or parent["frozen"]["phase"] != "holdout"
            or parent["frozen"]["combined_class_rule_sha256"] != corpus.digest_file(args.combined_rule)):
        raise RuntimeError("complete holdout parents bound to the original frozen guide required")
    training = reportio.read_json(ROOT / "artifacts/r47-mixed-capacity/training.json")
    old_parent = reportio.read_json(casebook._path(training["parent_training_reports"]["development"]["path"]))
    def numerical(value):
        return {key: item for key, item in value.items() if key not in ("phase", "combined_class_rule_sha256")}
    if numerical(parent["frozen"]) != numerical(old_parent["frozen"]):
        raise RuntimeError("parent numerical method changed between training and holdout")
    frozen_time = datetime.fromisoformat(rule["frozen_utc"])
    if frozen_time >= datetime.fromisoformat(parent["started_utc"]):
        raise RuntimeError("mixed guide was not frozen before holdout started")
    for folder in (ROOT / "artifacts/r29-matrix",):
        path = folder / "holdout.json"
        if path.exists() and frozen_time >= datetime.fromisoformat(reportio.read_json(path)["started_utc"]):
            raise RuntimeError("another holdout phase predates the mixed guide")
    for name, digest in training["source_sha256"].items():
        if corpus.digest_file(ROOT / name) != digest:
            raise RuntimeError("the mixed analytical implementation differs from its frozen training version")
    output = ROOT / "artifacts/r48-mixed-holdout"
    output.mkdir(exist_ok=True)
    result_path = output / "stage.json"
    if result_path.exists():
        raise RuntimeError("preserve the previous held-out evaluation epoch")
    names = ["scripts/r48_mixed_holdout.py", "python/lutlab/curve_search.py", "python/lutlab/stage_bundle.py",
             "python/lutlab/io.py", "python/lutlab/cache.py", "python/lutlab/runtime.py", "python/lutlab/casebook.py",
             "python/lutlab/validation.py"]
    hashes = {name: corpus.digest_file(ROOT / name) for name in names}
    input_hashes = {str(path): corpus.digest_file(path) for path in (rule_path, args.combined_rule, plan_path, parent_path)}
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__, "source_sha256": hashes,
              "frozen_inputs_sha256": input_hashes, "pass": False, "heldout_cases": [], "regret": [],
              "analytic_configurations": 0, "uniform_native_statistics_matched": 0, "native_checks": [],
              "pending_canonical_import": [], "new_fits": 0, "timing_is_benchmark": False, "official": False}
    reportio.write_report(result_path, report)
    book = casebook.Casebook(output / "native-casebook")
    cpu = ROOT / "build-r35-structured/jshc.exe"
    cpu_hash = corpus.digest_file(cpu)
    catalog = {row["id"]: row for row in reportio.read_json(ROOT / "datasets/problem16-v1/catalog.json")["cases"]}
    try:
        with tempfile.TemporaryDirectory(prefix="r48-native-") as temporary:
            for case in (row for row in plan["cases"] if row["split"] == "holdout"):
                case_id = case["id"]
                folder = output / case_id
                folder.mkdir()
                source_dir = ROOT / "data/corpus-v1/cases" / case_id
                source_manifest = reportio.read_json(source_dir / "manifest.json")
                truth_path = source_dir / "composite.lut256"
                source_paths = [source_dir / f"lut{stage}.lut256" for stage in range(1, 5)]
                source_hashes = [corpus.digest_file(path) for path in source_paths]
                if (source_hashes != [row["sha256"] for row in source_manifest["stages"]]
                        or corpus.digest_file(truth_path) != source_manifest["composite"]["sha256"]):
                    raise RuntimeError("held-out original source/truth changed")
                with validation._mapped_full(truth_path) as truth:
                    target = curve_search.target_curves(truth)
                curves = {stage: {} for stage in range(4)}
                models = {stage: {} for stage in range(4)}
                parents = {}
                for m in plan["stage_sizes"]:
                    item = parent["observations"][f"{case_id}/adaptive_bins/m{m}"]
                    path = casebook._path(item["path"])
                    if item["status"] != "screened" or corpus.digest_file(path) != item["sha256"]:
                        raise RuntimeError("held-out parent failed or changed")
                    value = reportio.read_json(path)
                    if value["source_sha256"] != source_hashes:
                        raise RuntimeError("held-out parent source differs")
                    parents[m] = value
                    for proof in value["evidence"]:
                        if corpus.digest_file(casebook._path(proof["path"])) != proof["sha256"]:
                            raise RuntimeError("held-out primary receipt changed")
                    for stage, (name, digest) in enumerate(zip(value["models"], value["model_sha256"])):
                        model = casebook._path(name)
                        if corpus.digest_file(model) != digest:
                            raise RuntimeError("held-out model changed")
                        models[stage][m] = model
                        curves[stage][m] = curve_search.model_curves(io.load_sparse(model, competition=True))
                rows = []
                for config in plan["configurations"]:
                    histogram = curve_search.error_histogram(curve_search.compose([curves[stage][m] for stage, m in enumerate(config)]), target)
                    stats = curve_search.statistics(histogram)
                    if len(set(config)) == 1:
                        if any(stats[name] != parents[config[0]]["cube"][name] for name in stats):
                            raise RuntimeError("held-out uniform full-cube statistics differ")
                        report["uniform_native_statistics_matched"] += 1
                    rows.append({"m": config, **stats, "node_payload_bytes": sum(3 * m ** 3 for m in config),
                                 "serialized_model_bytes": sum(models[stage][m].stat().st_size for stage, m in enumerate(config)),
                                 "error_histogram_sha256": hashlib.sha256(histogram.tobytes()).hexdigest()})
                row_map = {tuple(row["m"]): row for row in rows}
                case_regret = []
                for budget in plan["node_payload_budgets"]:
                    frozen = rule["rules"][f"{case['family']}/{case['intensity']}/b{budget}"]
                    feasible = [row for row in rows if row["node_payload_bytes"] <= budget]
                    for policy, metric in (("mean", "mean"), ("max", "max")):
                        selected = row_map[tuple(frozen[policy + "_m"])]
                        oracle = min(feasible, key=lambda row: (row[metric], row["node_payload_bytes"], row["m"]))
                        if selected["node_payload_bytes"] > budget or selected[metric] < oracle[metric]:
                            raise RuntimeError("invalid frozen selection/budget regret")
                        record = {"case_id": case_id, "family": case["family"], "intensity": case["intensity"],
                                  "budget": budget, "policy": policy, "selected_m": "-".join(map(str, selected["m"])),
                                  "selected_metric": selected[metric], "oracle_metric": oracle[metric],
                                  "regret": selected[metric] - oracle[metric], "oracle_is_zero": oracle[metric] == 0,
                                  "ratio": selected[metric] / oracle[metric] if oracle[metric] else None,
                                  "selected_node_payload_bytes": selected["node_payload_bytes"],
                                  "selected_p99": selected["p99"], "selected_rms": selected["rms"]}
                        case_regret.append(record)
                analysis_path = folder / "analysis.json"
                reportio.write_report(analysis_path, {"case": case, "configurations": rows, "regret": case_regret,
                    "target_complete_color_proof": 256 ** 3, "reference_sha256": source_manifest["composite"]["sha256"]})
                metadata = catalog[case_id]
                book.add_case(case_id, {key: metadata[key] for key in ("family", "intensity", "seed", "split", "tags", "expected")}, source_hashes)
                largest = rule["rules"][f"{case['family']}/{case['intensity']}/b{max(plan['node_payload_budgets'])}"]
                selected_configs = {tuple(largest["mean_m"]), tuple(largest["max_m"])}
                for config in sorted(selected_configs):
                    location = folder / ("native-" + "-".join(map(str, config)))
                    location.mkdir()
                    bundle = stage_bundle.assemble([models[stage][m] for stage, m in enumerate(config)], location / "models")
                    raw = Path(temporary) / "cube.rgb"
                    execution = runtime.cube(bundle.paths, raw, executable=cpu, kernel="tetra_structured_avx2", threads=4, competition=True)
                    expected = curve_search.compose([curves[stage][m] for stage, m in enumerate(config)])
                    with validation._mapped_full(raw) as mapped, validation._mapped_full(truth_path) as truth:
                        if not np.array_equal(curve_search.target_curves(mapped), expected):
                            raise RuntimeError("frozen held-out deployment differs on some RGB colour")
                        quality = validation._cube_stats(mapped, truth, top_k=8, threshold=2.)
                    if any(quality[name] != row_map[config][name] for name in ("n_colors", "mean", "rms", "p99", "max", "pixels_at_or_above_threshold")):
                        raise RuntimeError("native frozen selection metrics differ")
                    screen = {"kind": "casebook_native_cube_screen_v1", "case_id": case_id, "source_sha256": source_hashes,
                              "reference_sha256": source_manifest["composite"]["sha256"], "runtime": execution,
                              "output_sha256": corpus.digest_file(raw), "cube": quality, "inputs_unchanged": True,
                              "all_native_colors_equal_predicted_curves": True, "timing_is_benchmark": False}
                    primary_path = location / "screen.json"
                    reportio.write_report(primary_path, screen)
                    value = {"case_id": case_id, "source_sha256": source_hashes, "semantics": "independent", "correctness_pass": True,
                             "strategy": "mixed_capacity/" + "-".join(map(str, config)), "profile": "mixed_capacity", "m": list(config),
                             "models": list(map(str, bundle.paths)), "model_sha256": [corpus.digest_file(path) for path in bundle.paths],
                             "model_identity_sha256": bundle.manifest["identity_sha256"], "kernel": "tetra_structured_avx2",
                             "node_payload_bytes": row_map[config]["node_payload_bytes"], "cube": quality,
                             "evidence": [{"path": str(primary_path), "sha256": corpus.digest_file(primary_path)}], "official": False}
                    normalized_path = location / "observation.json"
                    reportio.write_report(normalized_path, value)
                    identifier = book.record(normalized_path)
                    receipt = {"case_id": case_id, "m": list(config), "path": str(normalized_path),
                               "sha256": corpus.digest_file(normalized_path), "observation_id": identifier}
                    report["native_checks"].append(receipt)
                    report["pending_canonical_import"].append(receipt)
                if ([corpus.digest_file(path) for path in source_paths] != source_hashes
                        or corpus.digest_file(truth_path) != source_manifest["composite"]["sha256"]):
                    raise RuntimeError("held-out original inputs changed during evaluation")
                report["analytic_configurations"] += len(rows)
                report["heldout_cases"].append({"id": case_id, "analysis": str(analysis_path), "sha256": corpus.digest_file(analysis_path)})
                report["regret"].extend(case_regret)
                reportio.write_report(result_path, report)
        if len(report["heldout_cases"]) != 9 or report["analytic_configurations"] != 729 or report["uniform_native_statistics_matched"] != 27 or len(report["regret"]) != 270:
            raise RuntimeError("declared held-out evaluation incomplete")
        for name, digest in hashes.items():
            if corpus.digest_file(ROOT / name) != digest:
                raise RuntimeError("held-out evaluation code changed")
        for name, digest in input_hashes.items():
            if corpus.digest_file(Path(name)) != digest:
                raise RuntimeError("frozen guide or parent phase changed during evaluation")
        if corpus.digest_file(cpu) != cpu_hash:
            raise RuntimeError("deployment executable changed")
        write_csv(output / "regret.csv", report["regret"])
        report.update(pass_=True, inputs_unchanged=True, finished_utc=datetime.now(timezone.utc).isoformat(),
                      heldout_evaluation_complete=True, unknown_population_guarantee=False)
        report["pass"] = report.pop("pass_")
        reportio.write_report(result_path, report)
        print(json.dumps({"pass": True, "heldout_cases": 9, "configurations": 729, "budget_policy_regrets": 270,
                          "native_selected_configurations": len(report["native_checks"])}))
    except BaseException as error:
        report.update(error={"type": type(error).__name__, "message": str(error)}, finished_utc=datetime.now(timezone.utc).isoformat())
        reportio.write_report(result_path, report)
        raise


if __name__ == "__main__":
    main()
