"""Freeze the mixed-capacity family/budget guide before any holdout outputs.

Two training seeds define descriptive mean and worst-max choices at 15 node
payload budgets. The capacity rule breaks objective ties by payload then m;
the separately validated legacy casebook max/p99 preference remains available.
No global casebook write, new fit, native pixels or held-out model read occurs.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import casebook, corpus, reportio


def main():
    output = ROOT / "datasets/problem16-v1/mixed-capacity-rules-r47.json"
    if output.exists():
        raise RuntimeError("preserve the frozen mixed-capacity guide")
    root = ROOT / "artifacts/r47-mixed-capacity"
    lock = root / "class-rule-freeze.lock"
    with lock.open("x", encoding="utf-8") as stream:
        json.dump({"pid": os.getpid(), "owner": "R47 independent mixed-capacity guide freeze"}, stream)
    try:
        for folder in (ROOT / "artifacts/r29-matrix", ROOT / "artifacts/r36-extension", root):
            if (folder / "holdout.json").exists():
                raise RuntimeError("refuse first rule freeze after a holdout phase has started")
        plan_path = ROOT / "datasets/problem16-v1/mixed-capacity-plan-r47.json"
        training_path = root / "training.json"
        native_path = root / "native-gate.json"
        payload_path = root / "payload-tie-gate.json"
        plan = reportio.read_json(plan_path)
        training = reportio.read_json(training_path)
        native = reportio.read_json(native_path)
        payload = reportio.read_json(payload_path)
        if (not training["analysis_pass"] or training["analytic_configurations"] != 1458
                or training["uniform_native_statistics_matched"] != 54 or not native["pass"] or not payload["pass"]
                or training["plan_sha256"] != corpus.digest_file(plan_path)
                or native["training_sha256"] != corpus.digest_file(training_path)
                or payload["first_native_gate_sha256"] != corpus.digest_file(native_path)):
            raise RuntimeError("complete, mutually bound analysis/native gates required")
        expected_configs = {tuple(row) for row in plan["configurations"]}
        if expected_configs != set(itertools.product((17, 25, 33), repeat=4)):
            raise RuntimeError("configuration universe changed")
        groups = defaultdict(dict)
        captured = []
        for case in training["cases"]:
            path = casebook._path(case["analysis"])
            if corpus.digest_file(path) != case["sha256"]:
                raise RuntimeError("complete training source analysis changed")
            value = reportio.read_json(path)
            metadata = value["case"]
            configs = {tuple(row["m"]): row for row in value["configurations"]}
            if set(configs) != expected_configs or len(value["configurations"]) != 81 or value["target_complete_color_proof"] != 256 ** 3:
                raise RuntimeError("training source has an incomplete analytic proof")
            for configuration, row in configs.items():
                casebook.validate_quality(row)
                if row["node_payload_bytes"] != sum(3 * m ** 3 for m in configuration):
                    raise RuntimeError("node payload budget differs")
            family_key = (metadata["family"], metadata["intensity"])
            phase = metadata["split"]
            if phase not in ("development", "calibration") or phase in groups[family_key]:
                raise RuntimeError("class seed/split leakage")
            groups[family_key][phase] = {"case_id": metadata["id"], "configs": configs}
            captured.append({"path": str(path), "sha256": case["sha256"]})
        if len(groups) != 9:
            raise RuntimeError("expected three families and three strengths")
        rules = {}
        class_scores = {}
        for (family, intensity), cases in sorted(groups.items()):
            if set(cases) != {"development", "calibration"}:
                raise RuntimeError("both source training seeds required")
            scores = {}
            for configuration in sorted(expected_configs):
                values = [row["configs"][configuration] for row in cases.values()]
                scores[configuration] = {"m": list(configuration), "node_payload_bytes": values[0]["node_payload_bytes"],
                    "serialized_model_bytes": values[0]["serialized_model_bytes"],
                    "mean": math.fsum(row["mean"] for row in values) / 2,
                    "rms": math.sqrt(math.fsum(row["rms"] ** 2 for row in values) / 2),
                    "p99": max(row["p99"] for row in values), "max": max(row["max"] for row in values)}
                if values[0]["serialized_model_bytes"] != values[1]["serialized_model_bytes"]:
                    raise RuntimeError("serialized model size unexpectedly depends on source values")
            class_scores[f"{family}/{intensity}"] = list(scores.values())
            for budget in plan["node_payload_budgets"]:
                feasible = {configuration: row for configuration, row in scores.items() if row["node_payload_bytes"] <= budget}
                if not feasible:
                    raise RuntimeError("no feasible configuration at declared budget")
                mean = min(feasible, key=lambda config: (feasible[config]["mean"], feasible[config]["node_payload_bytes"], config))
                tail = min(feasible, key=lambda config: (feasible[config]["max"], feasible[config]["node_payload_bytes"], config))
                rules[f"{family}/{intensity}/b{budget}"] = {"max_node_payload_bytes": budget,
                    "mean_m": list(mean), "max_m": list(tail), "mean_training_score": feasible[mean],
                    "max_training_score": feasible[tail], "training_cases": [row["case_id"] for row in cases.values()],
                    "feasible_configurations": len(feasible)}
        if len(rules) != 135:
            raise RuntimeError("class-budget guide coverage is incomplete")
        proof_paths = [plan_path, training_path, native_path, payload_path]
        sources = ["scripts/r47_freeze_capacity_rules.py", "python/lutlab/curve_search.py", "python/lutlab/stage_bundle.py"]
        result = {"schema": 1, "scope": __doc__, "frozen_utc": datetime.now(timezone.utc).isoformat(),
                  "frozen_before_any_holdout_strategy_outputs": True, "plan_sha256": corpus.digest_file(plan_path),
                  "source_sha256": {name: corpus.digest_file(ROOT / name) for name in sources},
                  "training_evidence": [{"path": str(path), "sha256": corpus.digest_file(path)} for path in proof_paths],
                  "source_training_analyses": captured, "class_scores": class_scores, "rules": rules,
                  "selection": {"mean": ["mean of two source full cubes", "node_payload_bytes", "stage_sizes_lexicographic"],
                                "max": ["worst max across two source full cubes", "node_payload_bytes", "stage_sizes_lexicographic"],
                                "p99": "reported as worst source p99; not pooled and not a capacity-rule tie-break"},
                  "application_scope": "only proven diagonal chains in the three declared families; class label is supplied, not automatically inferred",
                  "heldout_generalisation_proven": False, "original_13_profile_freeze_still_required": True, "official": False}
        for row in captured:
            if corpus.digest_file(Path(row["path"])) != row["sha256"]:
                raise RuntimeError("training proof changed during freeze")
        reportio.write_report(output, result)
        print(json.dumps({"frozen_before_any_holdout_strategy_outputs": True, "rules": 135,
                          "training_sources": 18, "holdout_outputs_read": False, "output": str(output)}))
    finally:
        lock.unlink()


if __name__ == "__main__":
    main()
