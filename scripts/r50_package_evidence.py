"""Collect completed R50 scheduling/import evidence, excluding live matrix data.

This does no numerical work. The copied operational snapshots describe their
capture times; they are not a final audit or a freeze of the continuing matrix.
"""
from __future__ import annotations

import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import casebook, corpus, reportio


def main():
    folder = ROOT / "artifacts/r50-case-shard-qualification"
    output = folder / "completed-stage.json"
    if output.exists():
        raise RuntimeError("preserve the existing completed evidence epoch")
    sources = {"qualification": folder / "stage.json",
               "migration": ROOT / "artifacts/r50-case-migration/13d7f76d500d/stage.json",
               "canonical_import": ROOT / "artifacts/r46-qualified-import/4e4dac36d1b6/stage.json"}
    stages = {}
    hashes = {}
    for role, path in sources.items():
        value = reportio.read_json(path)
        if not value["pass"] or not value.get("finished_utc"):
            raise RuntimeError("an operational prerequisite is incomplete")
        for name, digest in value["source_sha256"].items():
            if corpus.digest_file(ROOT / name) != digest or name in hashes and hashes[name] != digest:
                raise RuntimeError("source differs between qualified operational stages")
            hashes[name] = digest
        stages[role] = value
    if (stages["qualification"]["fresh_native_full_cubes"] != 2 or stages["qualification"]["reused_receipts"] != 52
            or not stages["migration"]["all_captured_processes_confirmed_terminal"]
            or stages["canonical_import"]["newly_added_observations"] != 45):
        raise RuntimeError("declared operational scope was not completed")
    hashes[Path(__file__).relative_to(ROOT).as_posix()] = corpus.digest_file(Path(__file__))
    evidence = folder / "operational-evidence"
    evidence.mkdir()
    for role in ("migration", "canonical_import"):
        origin = sources[role].parent
        target = evidence / role
        shutil.copytree(origin, target)
    index_path = ROOT / "datasets/problem16-v1/casebook/index.json"
    payload = index_path.read_bytes()
    current = json.loads(payload)
    capture_path = evidence / "post-import-index-snapshot.json"
    capture_path.write_bytes(payload)
    for item in stages["canonical_import"]["imported"]:
        source = casebook._path(item["path"])
        value = reportio.read_json(source)
        identifier = item["observation_id"]
        if (corpus.digest_file(source) != item["sha256"] or identifier not in current["cases"][value["case_id"]]["observations"]
                or hashlib.sha256(corpus.canonical(value)).hexdigest() != identifier):
            raise RuntimeError("imported receipt not present in the captured canonical index")
        stored = reportio.read_json(index_path.parent / "observations" / (identifier + ".json"))
        if {key: value for key, value in stored.items() if key not in ("observation_id", "record_source")} != value:
            raise RuntimeError("canonical imported record differs from validated evidence")
    before = reportio.read_json(sources["migration"].parent / "before-canonical-index.json")
    mixed_plan = reportio.read_json(ROOT / "datasets/problem16-v1/mixed-capacity-plan-r47.json")
    rows = []
    for case in mixed_plan["cases"]:
        if case["split"] == "holdout":
            continue
        cid = case["id"]
        def champion(index):
            identifier = index["cases"][cid]["champions"]["best_measured_mean"]
            return identifier, reportio.read_json(index_path.parent / "observations" / (identifier + ".json"))
        old_id, old = champion(before)
        new_id, new = champion(current)
        if new["cube"]["mean"] > old["cube"]["mean"]:
            raise RuntimeError("canonical mean ranking regressed")
        rows.append({"case_id": cid, "old_observation_id": old_id, "new_observation_id": new_id,
                     "old_mean": old["cube"]["mean"], "new_mean": new["cube"]["mean"],
                     "old_node_payload_bytes": old["node_payload_bytes"], "new_node_payload_bytes": new["node_payload_bytes"],
                     "strict_mean_improvement": new["cube"]["mean"] < old["cube"]["mean"],
                     "same_mean_lower_payload": new["cube"]["mean"] == old["cube"]["mean"] and new["node_payload_bytes"] < old["node_payload_bytes"]})
    if len(rows) != 18 or sum(row["strict_mean_improvement"] for row in rows) != 9 or sum(row["same_mean_lower_payload"] for row in rows) != 4:
        raise RuntimeError("canonical post-import comparison differs from the measured 18-source study")
    reportio.write_report(evidence / "mixed-canonical-champions.json", rows)
    prepared = []
    for name in ("scripts/r48_mixed_holdout.py", "scripts/r49_holdout_comparison.py"):
        ast.parse((ROOT / name).read_bytes())
        hashes[name] = corpus.digest_file(ROOT / name)
        prepared.append({"path": name, "sha256": hashes[name], "syntax_parsed": True,
                         "actual_holdout_evaluation_executed": False, "holdout_outputs_read": False})
    if any(path.exists() for path in (ROOT / "artifacts/r29-matrix/holdout.json", ROOT / "artifacts/r36-extension/holdout.json")):
        raise RuntimeError("this evidence capture expected no held-out phase outputs yet")
    result = {"started_utc": stages["qualification"]["started_utc"], "finished_utc": datetime.now(timezone.utc).isoformat(),
              "scope": __doc__, "pass": True, "source_sha256": hashes, "inputs_unchanged": True,
              "completed_stage_inputs": {role: {"path": str(path), "sha256": corpus.digest_file(path)} for role, path in sources.items()},
              "fresh_native_full_cubes": 2, "reused_receipts": 52, "canonical_imported_receipts": 45,
              "original_indexed_receipts_preserved": True, "orphan_receipts_recovered": len(stages["migration"]["recovered"]),
              "mixed_training_sources": 18, "canonical_mean_improved_sources": 9, "canonical_equal_mean_lower_payload_sources": 4,
              "post_import_index_capture": {"path": str(capture_path), "sha256": hashlib.sha256(payload).hexdigest(),
                  "scope": "single separately captured index after import; continuing matrix may append later; not a final whole-book audit"},
              "prepared_holdout_tools": prepared, "full_declared_matrix_cells": 7917, "full_matrix_complete": False,
              "full_user_goal_complete": False, "holdout_outputs_read": False, "new_mapping_timing_runs": 0,
              "previous_goal_turn_classification": "progress", "previous_goal_evidence": "R47 completed training search and froze 135 rules; numerical source and records preserved",
              "current_goal_turn_classification": "progress", "official": False}
    for name, digest in hashes.items():
        if corpus.digest_file(ROOT / name) != digest:
            raise RuntimeError("packaging source changed")
    reportio.write_report(output, result)
    print(json.dumps({"pass": True, "fresh_native_cubes": 2, "reused_receipts": 52, "canonical_imported": 45,
                      "strict_mean_winners_updated": 9, "equal_mean_payload_winners_updated": 4, "stage": str(output)}))


if __name__ == "__main__":
    main()
