"""Describe completed four-policy training differences and capacity controls.

Reuses numerical execution receipts; no new fits, pixels, timing or holdout.
Constant final chains are labelled explicitly. This does not replace the full
13-profile comparison or freeze rules using incomplete baseline training.
"""
from __future__ import annotations

from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import casebook, corpus, reportio
from r42_training_comparison import METRICS, metrics, write_csv


def receipt(item):
    path = casebook._path(item["path"])
    if corpus.digest_file(path) != item["sha256"] or item["status"] != "screened":
        raise RuntimeError("requires unchanged valid completed numerical receipts")
    value = reportio.read_json(path)
    if hashlib.sha256(corpus.canonical(value)).hexdigest() != item["observation_id"]:
        raise RuntimeError("normalized numerical observation identity changed")
    casebook.validate_quality(value["cube"])
    return value


def main():
    output = ROOT / "artifacts/r44-new-policy-comparison"
    target = output / "analysis.json"
    if target.exists():
        raise RuntimeError("preserve this completed-policy analysis before rerunning")
    source_names = ["scripts/r44_policy_analysis.py", "scripts/r42_training_comparison.py",
                    "scripts/r41_freeze_combined_rules.py", "python/lutlab/corpus.py", "python/lutlab/casebook.py"]
    source_hashes = {name: corpus.digest_file(ROOT / name) for name in source_names}
    comparison_path = output / "5d60c69aaabd/stage.json"
    comparison = reportio.read_json(comparison_path)
    if (not comparison["descriptive_snapshot_integrity_pass"] or comparison["profile_set"] != "extension"
            or comparison["observed_training_cells"] != 1440 or comparison["declared_training_cells"] != 1440
            or comparison["complete_valid_class_budget_groups"] != 180 or comparison["holdout_outputs_read"]):
        raise RuntimeError("requires the complete, explicitly four-profile training comparison")
    inventory_path = ROOT / "artifacts/r28-corpus/case-inventory.csv"
    index = reportio.read_json(ROOT / "report/data/r28/evidence-index.json")
    if corpus.digest_file(inventory_path) != index["files"]["artifacts/r28-corpus/case-inventory.csv"]["sha256"]:
        raise RuntimeError("complete source characterization differs from the frozen R28 inventory")
    with inventory_path.open(encoding="utf-8-sig", newline="") as stream:
        labels = {row["case_id"]: row for row in csv.DictReader(stream)}
    profiles = comparison["profiles_compared"]
    observations = {}
    for item in comparison["training_reports"].values():
        path = casebook._path(item["snapshot_path"])
        if corpus.digest_file(path) != item["snapshot_sha256"]:
            raise RuntimeError("training snapshot changed")
        phase = reportio.read_json(path)
        if not phase["phase_complete"]:
            raise RuntimeError("extension training was incomplete")
        for key, row in phase["observations"].items():
            value = receipt(row)
            if labels[value["case_id"]]["source_sha256"].split("|") != value["source_sha256"]:
                raise RuntimeError("source characterization is bound to another original chain")
            if key in observations:
                raise RuntimeError("duplicate training key")
            observations[key] = value
    if len(observations) != 1440:
        raise RuntimeError("incomplete four-policy candidate universe")
    class_counts = {metric: {profile: Counter() for profile in profiles if profile != "adaptive_bins"} for metric in METRICS}
    case_counts = {metric: {profile: Counter() for profile in profiles if profile != "adaptive_bins"} for metric in METRICS}
    changes = []
    class_rows = []
    for key, group in comparison["classes"].items():
        family, intensity, budget = key.split("/")
        constant = [case_id for case_id in group["case_ids"] if labels[case_id]["chain_output_constant"] == "True"]
        scores = {}
        for profile in profiles:
            values = [observations[f"{case_id}/{profile}/{budget}"] for case_id in group["case_ids"]]
            scores[profile] = metrics(values)
            if scores[profile] != group["scores"][profile]:
                raise RuntimeError("aggregated class quality differs from exact captured observations")
        for metric in METRICS:
            reference = scores["adaptive_bins"][metric]
            for profile, counts in class_counts[metric].items():
                candidate = scores[profile][metric]
                counts["better" if candidate < reference else "worse" if candidate > reference else "equal"] += 1
        changed = any(score != scores["adaptive_bins"] for score in scores.values())
        row = {"class": key, "case_ids": group["case_ids"], "constant_final_cases": constant,
               "output_palette_sizes": {case_id: int(labels[case_id]["output_palette_size"]) for case_id in group["case_ids"]},
               "scores": scores, "changed_aggregate_metrics": changed}
        if changed:
            changes.append(row)
        for profile, score in scores.items():
            class_rows.append({"family": family, "intensity": intensity, "m": int(budget[1:]), "profile": profile,
                               "constant_training_cases": len(constant), "training_cases": 2, **score,
                               **{metric + "_delta_vs_adaptive_bins": score[metric] - scores["adaptive_bins"][metric] for metric in METRICS}})
    for case_id in {value["case_id"] for value in observations.values()}:
        for m in (17, 25, 33):
            reference = observations[f"{case_id}/adaptive_bins/m{m}"]["cube"]
            for profile in profiles:
                if profile == "adaptive_bins":
                    continue
                candidate = observations[f"{case_id}/{profile}/m{m}"]["cube"]
                for metric in METRICS:
                    a, b = reference[metric], candidate[metric]
                    case_counts[metric][profile]["better" if b < a else "worse" if b > a else "equal"] += 1
    regression_path = ROOT / "artifacts/r36-extension/regression.json"
    regression_payload = regression_path.read_bytes()
    regression = json.loads(regression_payload)
    if not regression["phase_complete"] or len(regression["observations"]) != 357:
        raise RuntimeError("extension regression is incomplete")
    (output / "regression.json").write_bytes(regression_payload)
    old_profiles = set(reportio.read_json(ROOT / "datasets/problem16-v1/strategy-plan.json")["profiles"])
    control_rows = []
    control_groups = {}
    for key, item in regression["observations"].items():
        if not key.startswith("axis_bin_capacity-"):
            continue
        value = receipt(item)
        case_id, profile, budget = key.split("/")
        row = {"case_id": case_id, "profile": profile, "m": int(budget[1:]), **{metric: value["cube"][metric] for metric in METRICS}}
        control_rows.append(row)
        control_groups.setdefault((case_id, budget), []).append(row)
    controls = {}
    for (case_id, budget), rows in control_groups.items():
        if len(rows) != 13 or len({row["profile"] for row in rows}) != 13:
            raise RuntimeError("capacity control lacks a full thirteen-profile comparison")
        old = [row for row in rows if row["profile"] in old_profiles]
        new = [row for row in rows if row["profile"] in profiles]
        controls[f"{case_id}/{budget}"] = {"all_13": {metric: min(row[metric] for row in rows) for metric in METRICS},
            "old_9": {metric: min(row[metric] for row in old) for metric in METRICS},
            "new_4": {metric: min(row[metric] for row in new) for metric in METRICS},
            "old_mean_co_winners": [row["profile"] for row in old if row["mean"] == min(other["mean"] for other in old)],
            "new_mean_co_winners": [row["profile"] for row in new if row["mean"] == min(other["mean"] for other in new)]}
    if len(control_rows) != 117 or len(controls) != 9:
        raise RuntimeError("capacity control denominator changed")
    write_csv(output / "new-policy-class-comparison.csv", class_rows)
    write_csv(output / "capacity-controls.csv", control_rows)
    shutil.copyfile(inventory_path, output / "source-case-characterization.csv")
    controller_path = ROOT / "artifacts/r36-extension/controllers/459d1fe72535/controller.json"
    controller = reportio.read_json(controller_path)
    if not controller["pass"] or not controller.get("finished_utc"):
        raise RuntimeError("extension controller has not completed")
    shutil.copyfile(controller_path, output / "completed-extension-controller.json")
    for name, digest in source_hashes.items():
        if corpus.digest_file(ROOT / name) != digest:
            raise RuntimeError("policy analysis source changed")
    report = {"finished_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__, "source_sha256": source_hashes,
              "comparison_sha256": corpus.digest_file(comparison_path), "source_characterization_sha256": corpus.digest_file(inventory_path),
              "completed_extension_controller_sha256": corpus.digest_file(controller_path),
              "regression_sha256": hashlib.sha256(regression_payload).hexdigest(),
              "training_cells": 1440, "class_budget_groups": 180, "case_budget_groups": 360,
              "profiles_compared": profiles, "full_study_profiles": 13, "full_declared_training_cells": 4680,
              "combined_declared_candidates": 7917, "class_counts_relative_to_adaptive_bins": class_counts,
              "case_counts_relative_to_adaptive_bins": case_counts, "changed_class_aggregate_metrics": changes,
              "unchanged_class_aggregate_metric_groups": 180 - len(changes),
              "capacity_control_cells": 117, "capacity_control_best": controls,
              "constant_chain_scope": "source full-cube characterization from R28; constant final targets are not complex-output generalisation evidence",
              "new_fits": 0, "new_pixel_executions": 0, "holdout_outputs_read": False,
              "class_sweet_zone_proven": False, "full_user_goal_complete": False, "official": False,
              "completed_analysis_contract_pass": True}
    reportio.write_report(target, report)
    print(json.dumps({"completed_analysis_contract_pass": True, "training_cells": 1440, "changed_class_groups": len(changes),
                      "unchanged_class_groups": 180 - len(changes), "capacity_control_cells": 117,
                      "case_mean_counts": case_counts["mean"]}))


if __name__ == "__main__":
    main()
