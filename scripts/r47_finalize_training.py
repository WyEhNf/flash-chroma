"""Join completed mixed-capacity analysis, native gates and pre-holdout rules.

Compare these 18 sources only after every original 13x3 candidate exists for
each. Preserve independent atomic index snapshots rather than claim the whole
still-running matrix is complete. No new fits, pixels or benchmarks occur.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import casebook, corpus, reportio
from r42_training_comparison import write_csv


def main():
    root = ROOT / "artifacts/r47-mixed-capacity"
    target = root / "completed-training-stage.json"
    if target.exists():
        raise RuntimeError("preserve the completed training-stage join")
    names = ["scripts/r47_finalize_training.py", "scripts/r47_mixed_capacity_study.py", "scripts/r47_mixed_native_gate.py",
             "scripts/r47_payload_tie_gate.py", "scripts/r47_freeze_capacity_rules.py", "scripts/r47_mixed_capacity_plan.py",
             "python/lutlab/curve_search.py", "python/lutlab/stage_bundle.py", "python/lutlab/io.py",
             "python/lutlab/cache.py", "python/lutlab/portable_export.py", "python/lutlab/casebook.py"]
    source_hashes = {name: corpus.digest_file(ROOT / name) for name in names}
    training_path = root / "training.json"
    native_path = root / "native-gate.json"
    tie_path = root / "payload-tie-gate.json"
    rules_path = ROOT / "datasets/problem16-v1/mixed-capacity-rules-r47.json"
    training = reportio.read_json(training_path)
    native = reportio.read_json(native_path)
    ties = reportio.read_json(tie_path)
    rules = reportio.read_json(rules_path)
    if (not training["analysis_pass"] or not native["pass"] or not ties["pass"]
            or not rules["frozen_before_any_holdout_strategy_outputs"] or len(rules["rules"]) != 135):
        raise RuntimeError("training/native/rule prerequisites incomplete")
    for report in (training, native, ties):
        for name, digest in report["source_sha256"].items():
            if corpus.digest_file(ROOT / name) != digest:
                raise RuntimeError("completed-stage source changed before freeze")
    old_plan = reportio.read_json(ROOT / "datasets/problem16-v1/strategy-plan.json")
    extension_plan = reportio.read_json(ROOT / "datasets/problem16-v1/strategy-extension-r36.json")
    phases = {}
    snapshots = {}
    for kind, folder in (("baseline", ROOT / "artifacts/r29-matrix"), ("extension", ROOT / "artifacts/r36-extension")):
        for phase in ("development", "calibration"):
            payload = (folder / (phase + ".json")).read_bytes()
            copied = root / f"original-{kind}-{phase}-snapshot.json"
            copied.write_bytes(payload)
            phases[kind, phase] = json.loads(payload)
            snapshots[f"{kind}_{phase}"] = {"path": str(copied), "sha256": hashlib.sha256(payload).hexdigest()}
    native_rows = {(row["case_id"], tuple(row["m"])): row for row in native["observations"]}
    for row in ties["pending_canonical_import"]:
        native_rows[row["case_id"], tuple(row["m"])] = row
    comparison = []
    for entry in training["cases"]:
        detail = reportio.read_json(casebook._path(entry["analysis"]))
        metadata = detail["case"]
        case_id, phase = metadata["id"], metadata["split"]
        rows = []
        for kind, profiles in (("baseline", old_plan["profiles"]), ("extension", extension_plan["new_profiles"])):
            for m in (17, 25, 33):
                for profile in profiles:
                    item = phases[kind, phase]["observations"].get(f"{case_id}/{profile}/m{m}")
                    if item is None or item["status"] != "screened":
                        raise RuntimeError("source lacks a complete valid 13x3 reference comparison")
                    path = casebook._path(item["path"])
                    if corpus.digest_file(path) != item["sha256"]:
                        raise RuntimeError("original measured observation changed")
                    value = reportio.read_json(path)
                    casebook.validate_quality(value["cube"])
                    rows.append({"profile": profile, "m": m, **{name: value["cube"][name] for name in ("mean", "max", "p99", "rms")},
                                 "node_payload_bytes": value["node_payload_bytes"]})
        if len(rows) != 39:
            raise RuntimeError("original comparison denominator changed")
        old = min(rows, key=lambda row: (row["mean"], row["node_payload_bytes"], row["profile"], row["m"]))
        new = detail["best_mean"]
        selected = native_rows.get((case_id, tuple(new["m"])))
        if selected is None:
            raise RuntimeError("mean-optimal selected model lacks a complete native proof")
        normalized_path = Path(selected["path"])
        if corpus.digest_file(normalized_path) != selected["sha256"]:
            raise RuntimeError("native mixed observation changed")
        normalized = reportio.read_json(normalized_path)
        if normalized["cube"]["mean"] != new["mean"]:
            raise RuntimeError("native selected mean differs")
        pure_max = min(detail["configurations"], key=lambda row: (row["max"], row["node_payload_bytes"], row["m"]))
        if (case_id, tuple(pure_max["m"])) not in native_rows:
            raise RuntimeError("capacity-priority max optimum lacks native proof")
        comparison.append({"case_id": case_id, "family": metadata["family"], "intensity": metadata["intensity"], "split": phase,
                           "reference_candidates": 39, "reference_best_mean_profile": old["profile"], "reference_best_mean_m": old["m"],
                           "reference_best_mean": old["mean"], "reference_node_payload_bytes": old["node_payload_bytes"],
                           "mixed_mean_m": "-".join(map(str, new["m"])), "mixed_best_mean": new["mean"],
                           "mixed_node_payload_bytes": new["node_payload_bytes"], "mixed_max_at_mean_optimum": new["max"],
                           "mean_relative_reduction": (old["mean"] - new["mean"]) / old["mean"] if old["mean"] else None,
                           "node_payload_relative_reduction": (old["node_payload_bytes"] - new["node_payload_bytes"]) / old["node_payload_bytes"],
                           "mixed_capacity_max_m": "-".join(map(str, pure_max["m"])), "mixed_best_max": pure_max["max"]})
    write_csv(root / "comparison-vs-original-13.csv", comparison)
    shutil.copyfile(rules_path, root / "frozen-capacity-rules.json")
    book = casebook.Casebook(root / "native-casebook")
    summary = book.summary()
    proof_paths = [training_path, native_path, tie_path, rules_path]
    result = {"finished_utc": datetime.now(timezone.utc).isoformat(), "source_sha256": source_hashes, "scope": __doc__,
              "evidence": [{"path": str(path), "sha256": corpus.digest_file(path)} for path in proof_paths],
              "original_phase_snapshots": snapshots, "training_configurations": 1458, "heldout_configurations_not_evaluated": 729,
              "reused_uniform_native_comparisons": 54, "native_cpu_selected_configurations": len(native_rows),
              "new_native_full_cube_streams": native["new_native_full_cube_streams"] + ties["new_native_full_cube_streams"],
              "native_cuda_checks": 2, "compiled_mixed_c99_rom_streams": 1, "class_budget_rules_frozen": 135,
              "original_reference_candidates_per_source": 39, "comparison": comparison,
              "sources_with_lower_mean_than_all_original_13": sum(row["mixed_best_mean"] < row["reference_best_mean"] for row in comparison),
              "sources_with_lower_mean_and_less_node_payload": sum(row["mixed_best_mean"] < row["reference_best_mean"]
                  and row["mixed_node_payload_bytes"] < row["reference_node_payload_bytes"] for row in comparison),
              "native_casebook_summary": {key: value for key, value in summary.items() if key != "groups"},
              "canonical_import_pending": len(native_rows), "original_matrix_candidates_unchanged": 7917,
              "new_fits": 0, "new_benchmarks": 0, "holdout_outputs_read": False,
              "class_sweet_zone_proven": False, "full_user_goal_complete": False, "official": False,
              "mixed_training_stage_pass": True}
    for name, digest in source_hashes.items():
        if corpus.digest_file(ROOT / name) != digest:
            raise RuntimeError("stage join source changed")
    reportio.write_report(target, result)
    print(json.dumps({key: result[key] for key in ("mixed_training_stage_pass", "training_configurations", "new_native_full_cube_streams",
        "class_budget_rules_frozen", "sources_with_lower_mean_than_all_original_13", "sources_with_lower_mean_and_less_node_payload",
        "canonical_import_pending")}))


if __name__ == "__main__":
    main()
