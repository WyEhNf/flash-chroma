"""Summarize immutable snapshots of selected declared training profiles.

This reads no holdout outputs and executes no fits or pixels. Rankings distinguish
provisional per-case winners from classes with both training seeds and every
selected profile attempted. The default compares all 13 profiles; an explicit
extension-only view compares the four new profiles without replacing that study.
Failed and missing cells retain both selected-view and full-study denominators.
These are descriptive training comparisons, not held-out sweet-zone evidence.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import casebook, corpus, reportio

METRICS = ("mean", "rms", "p99", "max")


def write_csv(path, rows):
    if not rows:
        return
    with Path(path).open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def metrics(rows):
    values = [row["cube"] for row in rows]
    return {"mean": math.fsum(value["mean"] for value in values) / len(values),
            "rms": math.sqrt(math.fsum(value["rms"] ** 2 for value in values) / len(values)),
            "p99": max(value["p99"] for value in values), "max": max(value["max"] for value in values)}


def summarize(args):
    from r41_freeze_combined_rules import context, runtime_kernel
    state = context(args)
    _, new, catalog, old_hash, new_hash, catalog_hash, reports, _ = state
    profiles = list(new["profiles"]) if args.profile_set == "all" else list(new["new_profiles"])
    if args.profile_set == "extension":
        reports = {role: item for role, item in reports.items() if role.startswith("extension_")}
    folder = args.output / uuid.uuid4().hex[:12]
    folder.mkdir(parents=True)
    output = folder / "stage.json"
    started = datetime.now(timezone.utc).isoformat()
    sources = {name: corpus.digest_file(ROOT / name) for name in (
        "scripts/r42_training_comparison.py", "scripts/r41_freeze_combined_rules.py",
        "python/lutlab/casebook.py", "python/lutlab/corpus.py", "python/lutlab/reportio.py")}
    # Reports are captured independently by a short read. Writers may append after
    # capture; these copied snapshots, not their later live versions, are evidence.
    captures = {}
    for role, item in reports.items():
        payload = item["payload"]
        digest = hashlib.sha256(payload).hexdigest()
        value = json.loads(payload)
        if digest != item["sha256"]:
            raise RuntimeError("captured index bytes differ from their original digest")
        target = folder / (role + ".json")
        target.write_bytes(payload)
        captures[role] = {"live_path": item["path"], "original_snapshot_sha256": item["sha256"],
                          "snapshot_path": casebook._portable(target), "snapshot_sha256": digest,
                          "encoding": "byte-identical original snapshot", "value": value}
    lookup = {case["id"]: case for case in catalog["cases"] if case["split"] in ("development", "calibration")}
    sizes = new["sizes"]
    all_cells = {f"{case_id}/{profile}/m{m}" for case_id in lookup for profile in profiles for m in sizes}
    cells = {}
    flat_rows = []
    proof_hashes = set()
    source_manifests = {}
    for role, capture in captures.items():
        for key, item in capture["value"]["observations"].items():
            if key in cells or key not in all_cells:
                raise RuntimeError("duplicate or undeclared training candidate")
            case_id, profile, budget = key.split("/")
            case = lookup[case_id]
            if role.rsplit("_", 1)[1] != case["split"]:
                raise RuntimeError("training candidate belongs to another split")
            path = casebook._path(item["path"])
            if corpus.digest_file(path) != item["sha256"]:
                raise RuntimeError("immutable normalized receipt changed")
            value = reportio.read_json(path)
            if value["case_id"] != case_id or value["m"] != [int(budget[1:])] * 4:
                raise RuntimeError("candidate receipt belongs to another case/budget")
            if case_id not in source_manifests:
                source_manifests[case_id] = reportio.read_json(ROOT / "data/corpus-v1/cases" / case_id / "manifest.json")
            manifest = source_manifests[case_id]
            if value["source_sha256"] != [stage["sha256"] for stage in manifest["stages"]]:
                raise RuntimeError("candidate source chain differs from this case")
            row = {"key": key, "case_id": case_id, "family": case["family"], "intensity": case["intensity"],
                   "split": case["split"], "profile": profile, "m": int(budget[1:]), "status": item["status"],
                   "observation_id": None, "mean": None, "rms": None, "p99": None, "max": None}
            if item["status"] == "screened":
                if (hashlib.sha256(corpus.canonical(value)).hexdigest() != item["observation_id"]
                        or value["profile"] != profile or not value["correctness_pass"] or value["semantics"] != "independent"):
                    raise RuntimeError("invalid normalized observation identity or semantics")
                casebook.validate_quality(value["cube"])
                for proof in value["evidence"]:
                    if corpus.digest_file(casebook._path(proof["path"])) != proof["sha256"]:
                        raise RuntimeError("underlying execution receipt changed")
                    proof_hashes.add(proof["sha256"])
                primary = reportio.read_json(casebook._path(value["evidence"][0]["path"]))
                execution = primary["runtime"]
                if (primary["kind"] != "casebook_native_cube_screen_v1" or not primary["inputs_unchanged"]
                        or primary["cube"] != value["cube"] or primary["source_sha256"] != value["source_sha256"]
                        or primary["reference_sha256"] != manifest["composite"]["sha256"]
                        or execution["returncode"] or runtime_kernel(execution) != value["kernel"]
                        or value["kernel"] != ("tri_float" if profile == "trilinear" else "tetra_avx2")
                        or list(execution["models_sha256"].values()) != value["model_sha256"]):
                    raise RuntimeError("normalized quality differs from the primary cube execution")
                row.update(observation_id=item["observation_id"], **{metric: value["cube"][metric] for metric in METRICS})
            elif value["status"] != item["status"] or item["status"] not in (
                    "fit_failure", "execution_failure", "correctness_failure"):
                raise RuntimeError("unrecognized candidate failure")
            cells[key] = {**row, "cube": value.get("cube")}
            flat_rows.append(row)
    expected_training = 120 * len(profiles) * 3
    if len(all_cells) != expected_training:
        raise RuntimeError("full training denominator changed")
    case_budget = []
    for case_id, case in lookup.items():
        for m in sizes:
            keys = [f"{case_id}/{profile}/m{m}" for profile in profiles]
            attempted = [cells[key] for key in keys if key in cells]
            valid = [row for row in attempted if row["status"] == "screened"]
            winners = {metric: None for metric in METRICS}
            co_winners = {metric: [] for metric in METRICS}
            for metric in METRICS:
                if valid:
                    best = min(row[metric] for row in valid)
                    co_winners[metric] = sorted(row["profile"] for row in valid if row[metric] == best)
                    winners[metric] = {"profile": co_winners[metric][0], "value": best}
            case_budget.append({"case_id": case_id, "family": case["family"], "intensity": case["intensity"],
                                "split": case["split"], "m": m, "declared_profiles": len(profiles),
                                "attempted": len(attempted), "valid": len(valid),
                                "all_profiles_attempted": len(attempted) == len(profiles),
                                "missing_profiles": [profile for profile, key in zip(profiles, keys) if key not in cells],
                                "failed_profiles": [row["profile"] for row in attempted if row["status"] != "screened"],
                                "best_among_measured": winners, "co_winners": co_winners})
    expected_groups = defaultdict(list)
    for case in lookup.values():
        for m in sizes:
            expected_groups[(case["family"], case["intensity"], m)].append(case["id"])
    classes = {}
    ranked_rows = []
    win_counts = {metric: Counter() for metric in METRICS}
    tie_counts = {metric: 0 for metric in METRICS}
    for (family, intensity, m), case_ids in sorted(expected_groups.items()):
        if len(case_ids) != 2 or {lookup[key]["split"] for key in case_ids} != {"development", "calibration"}:
            raise RuntimeError("class does not contain exactly two independent training seeds")
        expected = [f"{case_id}/{profile}/m{m}" for case_id in case_ids for profile in profiles]
        complete = all(key in cells for key in expected)
        attempted = sum(key in cells for key in expected)
        eligible = {}
        failed = defaultdict(list)
        for profile in profiles:
            values = [cells.get(f"{case_id}/{profile}/m{m}") for case_id in case_ids]
            if all(row is not None and row["status"] == "screened" for row in values):
                eligible[profile] = metrics(values)
            for case_id, row in zip(case_ids, values):
                if row and row["status"] != "screened":
                    failed[profile].append({"case_id": case_id, "status": row["status"]})
        winners = {}
        # Incomplete classes expose coverage only, never an interim class ranking.
        if complete and eligible:
            for metric in METRICS:
                best = min(score[metric] for score in eligible.values())
                ties = sorted(profile for profile, score in eligible.items() if score[metric] == best)
                winners[metric] = {"value": best, "selected_profile": ties[0], "co_winners": ties}
                tie_counts[metric] += len(ties) > 1
                for profile in ties:
                    win_counts[metric][profile] += 1
            for profile, score in eligible.items():
                reference = eligible.get("adaptive_full")
                ranked_rows.append({"family": family, "intensity": intensity, "m": m, "profile": profile,
                                    **score, "mean_delta_vs_adaptive_full": score["mean"] - reference["mean"] if reference else None,
                                    "max_delta_vs_adaptive_full": score["max"] - reference["max"] if reference else None,
                                    **{metric + "_co_winner": profile in winners[metric]["co_winners"] for metric in METRICS}})
        classes[f"{family}/{intensity}/m{m}"] = {"case_ids": sorted(case_ids), "expected_cells": 2 * len(profiles),
            "attempted": attempted, "all_profiles_attempted_on_both_seeds": complete,
            "eligible_profiles": sorted(eligible), "failed_profiles": dict(failed),
            "scores": eligible if complete else {}, "winners": winners,
            "ranking_status": "descriptive training only" if complete else "not ranked: incomplete comparison"}
    if len(classes) != 180:
        raise RuntimeError("expected all 180 class/intensity/budget groups")
    write_csv(folder / "training-candidates.csv", flat_rows)
    write_csv(folder / "complete-class-profiles.csv", ranked_rows)
    for name, digest in sources.items():
        if corpus.digest_file(ROOT / name) != digest:
            raise RuntimeError("analysis source changed during capture")
    result = {"started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__,
              "source_sha256": sources, "baseline_plan_sha256": old_hash, "extension_plan_sha256": new_hash,
              "catalog_sha256": catalog_hash, "training_reports": {
                  role: {key: value for key, value in capture.items() if key != "value"} for role, capture in captures.items()},
              "combined_declared_candidates": 7917, "declared_training_cells": expected_training,
              "full_declared_training_cells": 4680, "profiles_compared": profiles, "profile_set": args.profile_set,
              "comparison_scope": "all 13 profiles" if args.profile_set == "all" else "four new profiles only; does not replace the full 13-profile study",
              "observed_training_cells": len(cells), "missing_training_cells": sorted(all_cells - cells.keys()),
              "status_counts": dict(Counter(row["status"] for row in cells.values())),
              "class_budget_groups": len(classes),
              "complete_class_budget_groups": sum(row["all_profiles_attempted_on_both_seeds"] for row in classes.values()),
              "complete_valid_class_budget_groups": sum(row["all_profiles_attempted_on_both_seeds"] and len(row["eligible_profiles"]) == len(profiles) for row in classes.values()),
              "classes": classes, "case_budget_winners": case_budget,
              "complete_class_co_winner_counts": {metric: dict(values) for metric, values in win_counts.items()},
              "complete_class_tie_counts": tie_counts, "distinct_primary_receipts_checked": len(proof_hashes),
              "aggregation": "equal-size full-cube mean and pooled RMS; p99/max are worst across the two cases; exact ties all retained",
              "integrity_scope": "normalized IDs and primary receipt SHA; no new numerical execution or final model audit",
              "capture_scope": "four separately captured immutable training-index snapshots; later appended records are excluded",
              "holdout_outputs_read": False, "class_sweet_zone_proven": False, "official": False,
              "full_user_goal_complete": False, "descriptive_snapshot_integrity_pass": True}
    reportio.write_report(output, result)
    print(json.dumps({key: result[key] for key in ("observed_training_cells", "declared_training_cells",
        "complete_class_budget_groups", "class_budget_groups", "complete_class_tie_counts", "holdout_outputs_read")}))
    print(str(output))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-matrix", type=Path, default=ROOT / "artifacts/r29-matrix")
    parser.add_argument("--extension-matrix", type=Path, default=ROOT / "artifacts/r36-extension")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/r42-training-comparison")
    parser.add_argument("--profile-set", choices=("all", "extension"), default="all",
                        help="all 13 profiles, or an explicitly separate four-new-profile training comparison")
    summarize(parser.parse_args())


if __name__ == "__main__":
    main()
