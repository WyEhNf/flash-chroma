"""Evaluate frozen nine/thirteen-profile guides on all declared unseen seeds.

Requires complete original training, both immutable guides and complete original
holdout phases. No fit, pixel or timing execution occurs. Failed selections stay
failed; oracle regret never silently substitutes a successful alternative. One
unseen source seed per class is descriptive evidence, not a population guarantee.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import casebook, corpus, io, reportio
from r41_freeze_combined_rules import expected_keys, runtime_kernel
from r42_training_comparison import write_csv

METRICS = ("mean", "rms", "p99", "max")


def read_bound(path, expected):
    payload = Path(path).read_bytes()
    if hashlib.sha256(payload).hexdigest() != expected:
        raise RuntimeError("immutable input changed: " + str(path))
    return json.loads(payload)


def numerical(frozen):
    return {key: value for key, value in frozen.items()
            if key not in ("phase", "class_rule_sha256", "combined_class_rule_sha256")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inspect-only", action="store_true", help="prerequisite existence only; never read holdout contents")
    args = parser.parse_args()
    rule_path = ROOT / "datasets/problem16-v1/class-rules-combined-r41.json"
    old_rule_path = ROOT / "datasets/problem16-v1/class-rules.json"
    indices = {kind: ROOT / "artifacts" / folder / "holdout.json"
               for kind, folder in (("baseline", "r29-matrix"), ("extension", "r36-extension"))}
    prerequisites = {"combined_rule": rule_path.exists(), "baseline_rule": old_rule_path.exists(),
                     **{kind + "_holdout": path.exists() for kind, path in indices.items()}}
    if args.inspect_only:
        print(json.dumps({"prerequisite_files_present": prerequisites, "holdout_outputs_read": False,
                          "completion_not_checked": True, "evaluation_executed": False}))
        return
    if not all(prerequisites.values()):
        raise RuntimeError("all training/freeze/holdout prerequisites are required")
    rules = reportio.read_json(rule_path)
    old_rules = reportio.read_json(old_rule_path)
    plan_path = ROOT / "datasets/problem16-v1/strategy-plan.json"
    new_path = ROOT / "datasets/problem16-v1/strategy-extension-r36.json"
    catalog_path = ROOT / "datasets/problem16-v1/catalog.json"
    old_plan = reportio.read_json(plan_path)
    plan = reportio.read_json(new_path)
    catalog = reportio.read_json(catalog_path)
    if (not rules["frozen_before_holdout"] or not old_rules["frozen_before_holdout"]
            or rules["baseline_plan_sha256"] != corpus.digest_file(plan_path)
            or old_rules["plan_sha256"] != rules["baseline_plan_sha256"]
            or rules["extension_plan_sha256"] != corpus.digest_file(new_path)
            or rules["catalog_sha256"] != corpus.digest_file(catalog_path)
            or plan["combined_declared_candidates"] != 7917):
        raise RuntimeError("guides do not bind the original declared studies")
    train = {}
    for role in ("baseline_development", "baseline_calibration", "extension_development", "extension_calibration"):
        item = rules["training_reports"][role]
        value = read_bound(casebook._path(item["path"]), item["sha256"])
        if not value["phase_complete"] or not value.get("finished_utc"):
            raise RuntimeError("original training is incomplete")
        train[role] = value
    for name, digest in old_rules["training_reports_sha256"].items():
        read_bound(casebook._path(name), digest)
    held = {case["id"]: case for case in catalog["cases"] if case["split"] == "holdout"}
    if len(held) != 60 or len(rules["rules"]) != 180 or len(old_rules["rules"]) != 180:
        raise RuntimeError("original class/source universe changed")
    captures = {}
    frozen_at = max(datetime.fromisoformat(rules["frozen_utc"]), datetime.fromisoformat(old_rules["frozen_utc"]))
    for kind, path in indices.items():
        payload = path.read_bytes()
        value = json.loads(payload)
        cases = catalog["cases"] if kind == "baseline" else plan["cases"]
        profiles = (lambda case: old_plan["profiles"]) if kind == "baseline" else (lambda case: case["profiles"])
        keys = expected_keys(cases, profiles, plan["sizes"], "holdout")
        rule_field = "class_rule_sha256" if kind == "baseline" else "combined_class_rule_sha256"
        if (not value["phase_complete"] or not value.get("finished_utc")
                or value["observations"].keys() != keys or value["phase_expected_candidates"] != len(keys)
                or value["frozen"]["phase"] != "holdout"
                or value["frozen"][rule_field] != corpus.digest_file(old_rule_path if kind == "baseline" else rule_path)
                or numerical(value["frozen"]) != numerical(train[kind + "_development"]["frozen"])
                or frozen_at >= datetime.fromisoformat(value["started_utc"])):
            raise RuntimeError("holdout incomplete, used another numerical epoch or preceded both freezes")
        captures[kind] = {"value": value, "payload": payload, "sha256": hashlib.sha256(payload).hexdigest()}
    folder = ROOT / "artifacts/r49-holdout-comparison"
    if folder.exists():
        raise RuntimeError("preserve the prior holdout-analysis epoch")
    folder.mkdir()
    result_path = folder / "stage.json"
    names = ["scripts/r49_holdout_comparison.py", "scripts/r41_freeze_combined_rules.py",
             "scripts/r42_training_comparison.py", "python/lutlab/io.py", "python/lutlab/casebook.py",
             "python/lutlab/corpus.py", "python/lutlab/reportio.py"]
    hashes = {name: corpus.digest_file(ROOT / name) for name in names}
    inputs = {str(path): corpus.digest_file(path) for path in (rule_path, old_rule_path, plan_path, new_path, catalog_path, *indices.values())}
    result = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__, "source_sha256": hashes,
              "inputs_sha256": inputs, "pass": False, "declared_full_matrix_cells": 7917,
              "declared_heldout_cells": 2340, "new_pixel_executions": 0, "official": False,
              "unknown_population_guarantee": False, "guide_modified_after_holdout": False}
    reportio.write_report(result_path, result)
    try:
        cells = {}
        primary_receipts = set()
        manifests = {}
        flat = []
        verified_models = set()
        for kind, capture in captures.items():
            (folder / (kind + "-holdout.json")).write_bytes(capture["payload"])
            phase = capture["value"]
            for key, item in phase["observations"].items():
                if key in cells:
                    raise RuntimeError("duplicate key between the two declared matrices")
                case_id, profile, budget = key.split("/")
                case = held[case_id]
                value = read_bound(casebook._path(item["path"]), item["sha256"])
                if case_id not in manifests:
                    manifests[case_id] = reportio.read_json(ROOT / "data/corpus-v1/cases" / case_id / "manifest.json")
                manifest = manifests[case_id]
                sources = [stage["sha256"] for stage in manifest["stages"]]
                if value["case_id"] != case_id or value["m"] != [int(budget[1:])] * 4 or value["source_sha256"] != sources:
                    raise RuntimeError("held-out receipt belongs to another source/budget")
                if item["status"] == "screened":
                    if (hashlib.sha256(corpus.canonical(value)).hexdigest() != item["observation_id"]
                            or value["profile"] != profile or not value["correctness_pass"] or value["semantics"] != "independent"):
                        raise RuntimeError("held-out normalized identity or semantics differ")
                    casebook.validate_quality(value["cube"])
                    for evidence in value["evidence"]:
                        read_bound(casebook._path(evidence["path"]), evidence["sha256"])
                        primary_receipts.add(evidence["sha256"])
                    primary = reportio.read_json(casebook._path(value["evidence"][0]["path"]))
                    execution = primary["runtime"]
                    if (primary["kind"] != "casebook_native_cube_screen_v1" or not primary["inputs_unchanged"]
                            or primary["frozen"] != phase["frozen"] or primary["source_sha256"] != sources
                            or primary["cube"] != value["cube"] or primary["reference_sha256"] != manifest["composite"]["sha256"]
                            or execution["returncode"] or runtime_kernel(execution) != value["kernel"]
                            or value["kernel"] != ("tri_float" if profile == "trilinear" else "tetra_avx2")
                            or execution["executable_sha256"] != rules["frozen_training_environments"]["baseline"]["executable_sha256"]
                            or list(execution["models_sha256"].values()) != value["model_sha256"]):
                        raise RuntimeError("held-out primary execution binding changed")
                    paths = [casebook._path(name) for name in value["models"]]
                    identity = (tuple(map(str, paths)), tuple(value["model_sha256"]))
                    if identity not in verified_models:
                        contract = io.inspect_submission_contract(paths, semantics="independent")
                        parent = reportio.read_json(paths[0].parent / "manifest.json")
                        if ([corpus.digest_file(path) for path in paths] != value["model_sha256"]
                                or not contract["pass"] or contract["grid_sizes"] != value["m"]
                                or [row["sha256"] for row in parent["identity"]["inputs"]] != sources):
                            raise RuntimeError("held-out model bytes or original-source provenance changed")
                        verified_models.add(identity)
                elif (item["status"] not in ("fit_failure", "execution_failure", "correctness_failure")
                        or value["status"] != item["status"] or value["strategy"] != profile):
                    raise RuntimeError("undeclared failure status")
                cells[key] = {"value": value, "item": item}
                flat.append({"case_id": case_id, "family": case["family"], "intensity": case["intensity"],
                             "profile": profile, "m": int(budget[1:]), "status": item["status"],
                             **{metric: value["cube"][metric] if item["status"] == "screened" else None for metric in METRICS}})
        if len(cells) != 2340:
            raise RuntimeError("holdout denominator changed")
        decisions = []
        guide_comparison = []
        classes = []
        probe_rows = []
        for case_id, case in held.items():
            for m in plan["sizes"]:
                class_key = f"{case['family']}/{case['intensity']}/m{m}"
                rule = rules["rules"][class_key]
                old_rule = old_rules["rules"][class_key]
                candidates = {profile: cells[f"{case_id}/{profile}/m{m}"] for profile in plan["profiles"]}
                valid = {profile: row["value"] for profile, row in candidates.items() if row["item"]["status"] == "screened"}
                failed = sorted(set(candidates) - valid.keys())
                class_row = {"class": class_key, "heldout_case_id": case_id, "family": case["family"],
                             "intensity": case["intensity"], "m": m, "valid_profiles": len(valid), "failed_profiles": failed}
                for metric in METRICS:
                    selected_profile = rule[metric + "_profile"]
                    selected = valid.get(selected_profile)
                    oracle = min((value["cube"][metric] for value in valid.values()), default=None)
                    winners = sorted(profile for profile, value in valid.items() if value["cube"][metric] == oracle)
                    selected_value = selected["cube"][metric] if selected else None
                    regret = selected_value - oracle if selected and oracle is not None else None
                    if regret is not None and regret < 0:
                        raise RuntimeError("negative exact oracle regret")
                    row = {"case_id": case_id, "family": case["family"], "intensity": case["intensity"], "m": m,
                           "metric": metric, "frozen_profile": selected_profile, "selected_status": candidates[selected_profile]["item"]["status"],
                           "selected_value": selected_value, "oracle_value_among_valid": oracle, "regret": regret,
                           "ratio": selected_value / oracle if selected and oracle else None,
                           "oracle_zero": oracle == 0 if oracle is not None else None,
                           "frozen_selection_is_co_winner": selected_profile in winners,
                           "valid_profiles": len(valid), "failed_profiles": ";".join(failed), "co_winners": ";".join(winners)}
                    decisions.append(row)
                    class_row[metric + "_guide"] = selected_profile
                    class_row[metric + "_regret"] = regret
                    class_row[metric + "_co_winners"] = winners
                    if metric in ("mean", "max"):
                        old_profile = old_rule[metric + "_profile"]
                        old = valid.get(old_profile)
                        guide_comparison.append({"case_id": case_id, "family": case["family"], "intensity": case["intensity"],
                            "m": m, "metric": metric, "baseline_frozen_profile": old_profile, "combined_frozen_profile": selected_profile,
                            "baseline_selected_status": candidates[old_profile]["item"]["status"], "combined_selected_status": row["selected_status"],
                            "baseline_value": old["cube"][metric] if old else None, "combined_value": selected_value,
                            "combined_minus_baseline": selected_value - old["cube"][metric] if selected and old else None})
                classes.append(class_row)
                for profile in {rule["mean_profile"], rule["max_profile"]}:
                    value = valid.get(profile)
                    if value is None:
                        continue
                    primary = reportio.read_json(casebook._path(value["evidence"][0]["path"]))
                    for probe, score in primary["probes"].items():
                        probe_rows.append({"case_id": case_id, "family": case["family"], "intensity": case["intensity"],
                                           "m": m, "profile": profile, "probe": probe, **score})
        summary = {}
        for metric in METRICS:
            rows = [row for row in decisions if row["metric"] == metric]
            scored = [row for row in rows if row["regret"] is not None]
            summary[metric] = {"decisions": len(rows), "valid_selected": len(scored),
                "failed_selected": len(rows) - len(scored), "co_winner_selections": sum(row["frozen_selection_is_co_winner"] for row in rows),
                "mean_regret": math.fsum(row["regret"] for row in scored) / len(scored) if scored else None,
                "worst_regret": max((row["regret"] for row in scored), default=None),
                "all_declared_profiles_valid_decisions": sum(row["valid_profiles"] == 13 for row in rows)}
        if len(classes) != 180 or len(decisions) != 720 or len(guide_comparison) != 360:
            raise RuntimeError("class/budget/policy evaluation incomplete")
        write_csv(folder / "heldout-candidates.csv", flat)
        write_csv(folder / "frozen-guide-regret.csv", decisions)
        write_csv(folder / "nine-vs-thirteen-guide.csv", guide_comparison)
        write_csv(folder / "selected-boundary-probes.csv", probe_rows)
        for name, digest in hashes.items():
            if corpus.digest_file(ROOT / name) != digest:
                raise RuntimeError("analysis source changed")
        for name, digest in inputs.items():
            if corpus.digest_file(Path(name)) != digest:
                raise RuntimeError("frozen rule or phase index changed")
        result.update(pass_=True, finished_utc=datetime.now(timezone.utc).isoformat(), inputs_unchanged=True,
                      observed_heldout_cells=len(cells), status_counts=dict(Counter(row["status"] for row in flat)),
                      class_budget_groups=len(classes), classes=classes, policy_summary=summary,
                      policy_decisions=len(decisions), guide_comparison_decisions=len(guide_comparison),
                      checked_primary_receipts=len(primary_receipts), checked_model_chains=len(verified_models),
                      interpretation="one unseen source seed per family/intensity; observed boundaries only; failed candidates kept in denominator")
        result["pass"] = result.pop("pass_")
        reportio.write_report(result_path, result)
        print(json.dumps({"pass": True, "heldout_cells": len(cells), "class_budget_groups": len(classes), "policy_decisions": len(decisions)}))
    except BaseException as error:
        result.update(error={"type": type(error).__name__, "message": str(error)}, finished_utc=datetime.now(timezone.utc).isoformat())
        reportio.write_report(result_path, result)
        raise


if __name__ == "__main__":
    main()
