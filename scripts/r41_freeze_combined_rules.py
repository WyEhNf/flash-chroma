"""Freeze all 13-profile family rules after four complete training phases.

No pixels or fits run here. Exact declared key sets, normalized observations,
source chains, model contracts and primary receipt hashes are checked before
publishing. Regression controls do not train family rules. The unseen seed is
reserved for a later regret evaluation; two training seeds prove no population
confidence claim. An incomplete matrix cannot publish a frozen rule.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import casebook, corpus, io, reportio


def snapshot(path, *, keep_bytes=False):
    payload = Path(path).read_bytes()
    result = (json.loads(payload), hashlib.sha256(payload).hexdigest())
    return (*result, payload) if keep_bytes else result


def expected_keys(cases, profiles, sizes, phase):
    return {f"{case['id']}/{profile}/m{m}" for case in cases if case["split"] == phase
            for profile in profiles(case) for m in sizes}


def runtime_kernel(execution):
    """A cube command emits raw bytes, so its wrapper has no kernel JSON field."""
    command = execution["command"]
    if (execution["backend"] != "cpu" or len(command) < 2 or command[1] != "cube"
            or command.count("-k") != 1 or command.count("-t") != 1 or "--competition" not in command
            or command[command.index("-t") + 1] != "4"):
        raise RuntimeError("cube execution does not have the declared CPU/4-thread competition contract")
    return command[command.index("-k") + 1]


def context(args):
    old_path = ROOT / "datasets/problem16-v1/strategy-plan.json"
    new_path = ROOT / "datasets/problem16-v1/strategy-extension-r36.json"
    catalog_path = ROOT / "datasets/problem16-v1/catalog.json"
    old, old_hash = snapshot(old_path)
    new, new_hash = snapshot(new_path)
    catalog, catalog_hash = snapshot(catalog_path)
    if (old["total_candidates"] != 5400 or new["extension_candidates"] != 2517
            or new["combined_declared_candidates"] != 7917
            or new["baseline_plan_sha256"] != old_hash
            or old["catalog_sha256"] != catalog_hash
            or old["sizes"] != [17, 25, 33] or new["sizes"] != old["sizes"]
            or len(old["profiles"]) != 9 or len(new["profiles"]) != 13
            or set(old["case_ids"]) != {case["id"] for case in catalog["cases"]}):
        raise RuntimeError("declared experiment universe changed")
    for descriptor in new["catalogs"]:
        if corpus.digest_file(ROOT / descriptor["path"]) != descriptor["sha256"]:
            raise RuntimeError("extension catalog changed")
    extension_keys = expected_keys(new["cases"], lambda case: case["profiles"], new["sizes"], "development")
    extension_all = {f"{case['id']}/{profile}/m{m}" for case in new["cases"]
                     for profile in case["profiles"] for m in new["sizes"]}
    if (len(extension_all) != 2517 or hashlib.sha256(corpus.canonical(sorted(extension_all))).hexdigest()
            != new["expected_keyset_sha256"] or len(extension_keys) != 720):
        raise RuntimeError("extension does not describe the complete fixed key universe")
    reports = {}
    pending = {}
    for kind, folder, cases, profiles, plan_hash in (
            ("baseline", args.baseline_matrix, catalog["cases"], lambda case: old["profiles"], old_hash),
            ("extension", args.extension_matrix, new["cases"], lambda case: case["profiles"], new_hash)):
        for phase in ("development", "calibration"):
            role = f"{kind}_{phase}"
            path = folder / (phase + ".json")
            keys = expected_keys(cases, profiles, old["sizes"], phase)
            if not path.exists():
                pending[role] = {"completed": 0, "expected": len(keys), "missing": len(keys)}
                continue
            value, digest, payload = snapshot(path, keep_bytes=True)
            if value["frozen"]["plan_sha256"] != plan_hash or value["frozen"]["phase"] != phase:
                raise RuntimeError("training report belongs to another declared plan/split")
            actual = set(value["observations"])
            if not actual <= keys:
                raise RuntimeError("undeclared training candidate or cross-split contamination")
            if (not value["phase_complete"] or not value.get("finished_utc") or actual != keys
                    or value["phase_expected_candidates"] != len(keys)):
                pending[role] = {"completed": len(actual), "expected": len(keys), "missing": len(keys - actual)}
            reports[role] = {"path": casebook._portable(path), "sha256": digest, "value": value, "keys": keys, "payload": payload}
    return old, new, catalog, old_hash, new_hash, catalog_hash, reports, pending


def freeze(args, context_value):
    old, new, catalog, old_hash, new_hash, catalog_hash, reports, pending = context_value
    if pending:
        raise RuntimeError("all four full training phases are required: " + json.dumps(pending, sort_keys=True))
    previous = reportio.read_json(args.output) if args.output.exists() else None
    for folder in (args.baseline_matrix, args.extension_matrix):
        holdout = folder / "holdout.json"
        if previous is None and holdout.exists() and reportio.read_json(holdout).get("observations"):
            raise RuntimeError("holdout already observed; cannot claim a new pre-holdout freeze")
    source_images = {}
    for kind, folder in (("baseline", args.baseline_source), ("extension", args.extension_source)):
        marker = reportio.read_json(folder / "frozen-source.json")
        if not marker["pass"]:
            raise RuntimeError("numerical source image not verified")
        for name, digest in marker["source_sha256"].items():
            if corpus.digest_file(folder / name) != digest:
                raise RuntimeError("frozen numerical source changed")
        source_images[kind] = marker
    environments = {}
    for kind in ("baseline", "extension"):
        values = []
        for phase in ("development", "calibration"):
            frozen = reports[f"{kind}_{phase}"]["value"]["frozen"]
            values.append({key: value for key, value in frozen.items()
                           if key not in ("phase", "class_rule_sha256", "combined_class_rule_sha256")})
        if values[0] != values[1]:
            raise RuntimeError("training phases used different numerical versions or resources")
        environments[kind] = values[0]
    baseline_env, extension_env = environments["baseline"], environments["extension"]
    if (baseline_env["source_sha256"] != {name: corpus.digest_file(args.baseline_source / name)
                                            for name in baseline_env["source_sha256"]}
            or baseline_env["catalog_sha256"] != catalog_hash
            or baseline_env["executable_sha256"] != extension_env["native_sha256"]
            or baseline_env["trainer"] != extension_env["trainer"]
            or extension_env["baseline_source_image_sha256"] != source_images["baseline"]["archive_sha256"]):
        raise RuntimeError("baseline and extension do not share the declared source/evaluation lineage")
    for name, digest in extension_env["evaluation_source_sha256"].items():
        if corpus.digest_file(args.extension_source / name) != digest:
            raise RuntimeError("extension evaluation source differs")
    for name, digest in extension_env["new_fitting_source_sha256"].items():
        path = args.extension_source / ("pixi.lock" if name == "pixi.lock" else "python/lutlab/" + name)
        if corpus.digest_file(path) != digest:
            raise RuntimeError("extension fitting source differs from its frozen image")
    if (corpus.digest_file(ROOT / "build-r18-cpu/jshc.exe") != baseline_env["executable_sha256"]
            or corpus.digest_file(ROOT / "data/corpus-v1/inspection.json") != baseline_env["inspection_sha256"]
            or extension_env["inspection_sha256"] != [baseline_env["inspection_sha256"],
                corpus.digest_file(ROOT / "data/corpus-axis-bins-v1/inspection.json")]):
        raise RuntimeError("native runtime or complete dataset inspection changed")
    # Compare with the saved image, without importing the evolving main fitter.
    saved_fingerprint = source_images["extension"].get("public_cache_identity_probe")
    if not saved_fingerprint:
        raise RuntimeError("extension source image lacks its preserved public cache probe")
    index = reportio.read_json(args.casebook / "index.json")
    cases = {case["id"]: case for case in catalog["cases"]}
    groups = defaultdict(lambda: defaultdict(dict))
    failures = []
    seen = set()
    verified_models = set()
    primary_hashes = set()
    for role, report in reports.items():
        phase = role.rsplit("_", 1)[1]
        for key, item in report["value"]["observations"].items():
            if key in seen:
                raise RuntimeError("a candidate appears in both matrices")
            seen.add(key)
            case_id, profile, budget = key.split("/")
            case = cases[case_id]
            if case["split"] != phase or profile not in new["profiles"]:
                raise RuntimeError("invalid case/profile in training")
            evidence = casebook._path(item["path"])
            value, digest = snapshot(evidence)
            source_manifest = reportio.read_json(ROOT / "data/corpus-v1/cases" / case_id / "manifest.json")
            expected_source = [stage["sha256"] for stage in source_manifest["stages"]]
            if (digest != item["sha256"] or value["case_id"] != case_id
                    or value["source_sha256"] != expected_source or value["m"] != [int(budget[1:])] * 4
                    or index["cases"][case_id]["source_sha256"] != expected_source):
                raise RuntimeError("candidate evidence changed or belongs to another source/budget")
            if item["status"] != "screened":
                if value["status"] != item["status"] or item["status"] not in (
                        "fit_failure", "execution_failure", "correctness_failure") or value["strategy"] != profile:
                    raise RuntimeError("undeclared candidate failure")
                if not any(row["sha256"] == digest for row in index["cases"][case_id].get("failures", [])):
                    raise RuntimeError("training failure is missing from the canonical ledger")
                failures.append({"key": key, "role": role, "status": item["status"], "sha256": digest})
                continue
            identifier = hashlib.sha256(corpus.canonical(value)).hexdigest()
            stored = reportio.read_json(args.casebook / "observations" / (identifier + ".json"))
            if (identifier != item["observation_id"] or identifier not in index["cases"][case_id]["observations"]
                    or {key: val for key, val in stored.items() if key not in ("observation_id", "record_source")} != value
                    or value["profile"] != profile or not value["correctness_pass"] or value["semantics"] != "independent"):
                raise RuntimeError("candidate is not an integrity-bound canonical commit")
            casebook.validate_quality(value["cube"])
            models = [casebook._path(path) for path in value["models"]]
            model_key = (tuple(value["model_sha256"]), tuple(expected_source), tuple(map(str, models)))
            if value["node_payload_bytes"] != 4 * int(budget[1:]) ** 3 * 3:
                raise RuntimeError("model payload differs from the declared four-table budget")
            if model_key not in verified_models:
                if len(models) != 4 or [corpus.digest_file(path) for path in models] != value["model_sha256"]:
                    raise RuntimeError("measured model bytes changed")
                contract = io.inspect_submission_contract(models, semantics="independent")
                manifest = reportio.read_json(models[0].parent / "manifest.json")
                if (not contract["pass"] or contract["semantics_evidence"] != "verified_model_manifest"
                        or contract["grid_sizes"] != value["m"]
                        or [item["sha256"] for item in manifest["identity"]["inputs"]] != expected_source):
                    raise RuntimeError("model contract/source binding changed")
                verified_models.add(model_key)
            for proof in value["evidence"]:
                path = casebook._path(proof["path"])
                if corpus.digest_file(path) != proof["sha256"]:
                    raise RuntimeError("primary execution receipt changed")
                primary_hashes.add(proof["sha256"])
            primary = reportio.read_json(casebook._path(value["evidence"][0]["path"]))
            runtime = primary["runtime"]
            if (primary["kind"] != "casebook_native_cube_screen_v1" or not primary["inputs_unchanged"]
                    or primary["cube"] != value["cube"] or primary["source_sha256"] != expected_source
                    or primary["reference_sha256"] != source_manifest["composite"]["sha256"]
                    or list(runtime["models_sha256"].values()) != value["model_sha256"] or runtime["returncode"]
                    or runtime["executable_sha256"] != baseline_env["executable_sha256"]
                    or runtime_kernel(runtime) != value["kernel"]
                    or value["kernel"] != ("tri_float" if profile == "trilinear" else "tetra_avx2")):
                raise RuntimeError("primary full-cube measurement binding differs")
            bucket = groups[(case["family"], case["intensity"], budget)][profile]
            if phase in bucket:
                raise RuntimeError("more than one source seed in a class training phase")
            bucket[phase] = {"case_id": case_id, "observation_id": identifier, "cube": value["cube"]}
    rules = {}
    for (family, intensity, budget), profiles in sorted(groups.items()):
        eligible = {profile: rows for profile, rows in profiles.items() if set(rows) == {"development", "calibration"}}
        if not eligible:
            raise RuntimeError("no profile has both full-cube training cases")
        scores = {}
        for profile, rows in eligible.items():
            values = [row["cube"] for row in rows.values()]
            scores[profile] = {"mean": math.fsum(row["mean"] for row in values) / 2,
                               "rms": math.sqrt(math.fsum(row["rms"] ** 2 for row in values) / 2),
                               "p99": max(row["p99"] for row in values), "max": max(row["max"] for row in values)}
        rules[f"{family}/{intensity}/{budget}"] = {
            **{metric + "_profile": min(scores, key=lambda profile: (scores[profile][metric], profile))
               for metric in ("mean", "rms", "p99", "max")},
            "eligible_profiles": sorted(eligible), "declared_profiles": list(new["profiles"]),
            "cases_per_profile": 2, "training_scores": scores, "training_receipts": eligible}
    if len(rules) != 20 * 3 * 3 or len(seen) != 1620 * 2 + 720 * 2:
        raise RuntimeError("incomplete class/budget/training coverage")
    result = {"schema": 1, "scope": __doc__, "frozen_before_holdout": True,
              "frozen_utc": previous["frozen_utc"] if previous else datetime.now(timezone.utc).isoformat(),
              "baseline_plan_sha256": old_hash, "extension_plan_sha256": new_hash,
              "catalog_sha256": catalog_hash, "training_reports": {
                  role: {key: row[key] for key in ("path", "sha256")} for role, row in reports.items()},
              "source_sha256": {Path(__file__).relative_to(ROOT).as_posix(): corpus.digest_file(Path(__file__))},
              "frozen_training_environments": environments,
              "numerical_source_images": {key: value["archive_sha256"] for key, value in source_images.items()},
              "rules": rules, "failed_training_observations": failures,
              "checked_training_cells": len(seen), "distinct_verified_model_chains": len(verified_models),
              "distinct_primary_receipts": len(primary_hashes),
              "aggregation": {"mean": "mean of two equal-size full-cube means", "rms": "pooled equal-size full-cube RMS",
                              "p99": "maximum of the two case p99 values, not pooled p99", "max": "maximum over both source cubes",
                              "tie": "lexicographically smallest profile", "fit_failures": "kept in denominator, ineligible without both valid cases"},
              "heldout_generalisation_proven": False, "official": False}
    for role, row in reports.items():
        if corpus.digest_file(casebook._path(row["path"])) != row["sha256"]:
            raise RuntimeError("training report changed during freeze")
    if previous is not None:
        if previous != result:
            raise RuntimeError("preserve previous frozen rules; declare a separate epoch")
    else:
        reportio.write_report(args.output, result)
    print(json.dumps({"frozen_before_holdout": True, "rules": len(rules), "checked_training_cells": len(seen),
                      "reused": previous is not None, "output": str(args.output)}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-matrix", type=Path, default=ROOT / "artifacts/r29-matrix")
    parser.add_argument("--extension-matrix", type=Path, default=ROOT / "artifacts/r36-extension")
    parser.add_argument("--baseline-source", type=Path, default=ROOT / "artifacts/r29-frozen-source/19c69a6a7554b9920301")
    parser.add_argument("--extension-source", type=Path, default=ROOT / "artifacts/r36-frozen-source/ab02cab7af540d7cf09f")
    parser.add_argument("--casebook", type=Path, default=ROOT / "datasets/problem16-v1/casebook")
    parser.add_argument("--output", type=Path, default=ROOT / "datasets/problem16-v1/class-rules-combined-r41.json")
    parser.add_argument("--inspect-only", action="store_true", help="show missing declared training cells; never freeze or read holdout outputs")
    args = parser.parse_args()
    if args.inspect_only:
        state = context(args)
        print(json.dumps({"ready_to_freeze": not bool(state[-1]), "pending": state[-1],
                          "combined_declared_candidates": 7917, "holdout_outputs_read": False}))
        return
    lease = args.baseline_matrix / "phase-controller.lock"
    with lease.open("x", encoding="utf-8") as stream:
        json.dump({"pid": os.getpid(), "owner": "R41 combined immutable class rule freeze"}, stream)
    try:
        freeze(args, context(args))
    finally:
        lease.unlink()


if __name__ == "__main__":
    main()
