"""Predeclare joint stage-capacity search without changing the 7917-cell study.

Only diagonal, separable curve chains are eligible for exact histogram
factorization. All declared cases remain visible; a failed structural proof is
not silently replaced by a sampled score. Held-out parents/results are gated.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import corpus, reportio


def main():
    catalog_path = ROOT / "datasets/problem16-v1/catalog.json"
    extension_path = ROOT / "datasets/problem16-v1/strategy-extension-r36.json"
    definition = reportio.read_json(catalog_path)
    families = ["gamma", "logistic", "filmic"]
    cases = [{key: row[key] for key in ("id", "family", "intensity", "seed", "split")}
             for row in definition["cases"] if row["family"] in families]
    configurations = list(itertools.product((17, 25, 33), repeat=4))
    budgets = sorted({sum(3 * m ** 3 for m in config) for config in configurations})
    if len(cases) != 27 or len(configurations) != 81 or len(budgets) != 15:
        raise RuntimeError("mixed-capacity declaration universe differs")
    value = {"schema": 1, "scope": __doc__, "kind": "joint_independent_stage_capacity",
             "catalog_sha256": corpus.digest_file(catalog_path), "parent_extension_plan_sha256": corpus.digest_file(extension_path),
             "parent_profile": "adaptive_bins", "families": families, "cases": cases,
             "stage_sizes": [17, 25, 33], "configurations": configurations, "node_payload_budgets": budgets,
             "all_logical_configurations": 27 * 81, "training_configurations": 18 * 81,
             "holdout_configurations": 9 * 81, "new_mixed_configurations": 27 * 78,
             "uniform_parent_configurations_reused": 27 * 3,
             "original_matrix_candidates_unchanged": 7917,
             "evaluation": "prove full target and all model nodes diagonal-separable, compose three complete 256-value integer curves, convolve exact integer squared-error histograms",
             "independence_proof": "output channel c depends only on input channel c; all 256^3 RGB input triples have unit weight",
             "existing_execution_gate": "all three uniform configurations must reproduce their actual R36 full-cube statistics for each source",
             "new_native_gate": "execute the distinct mean-optimal and max-optimal configurations per training source, with payload then lexicographic tie-breaks; no per-edit tests",
             "pareto": ["whole_cube_mean", "whole_cube_max", "RGB_node_payload_bytes"],
             "class_rules": "two training seeds per family/intensity; select separate mean and max profiles at each of 15 payload budgets",
             "holdout_policy": "mixed-capacity rules must be frozen before ANY R29/R36/mixed holdout strategy outputs; holdout evaluation also requires the original combined rule",
             "source_semantics": "copy each stage byte-for-byte from its own original-LUT parent fit; no composition or residual labels",
             "timing_policy": "no speed claim from concurrent fitting or analytic histogram calculation",
             "declared_plan_is_measurement": False, "official": False}
    path = ROOT / "datasets/problem16-v1/mixed-capacity-plan-r47.json"
    if path.exists():
        if reportio.read_json(path) != json.loads(json.dumps(value)):
            raise RuntimeError("preserve the previous mixed-capacity plan")
    else:
        reportio.write_report(path, value)
    print(json.dumps({"training_configurations": 1458, "holdout_configurations": 729,
                      "original_matrix_unchanged": 7917, "native_or_analytic_measurements": 0}))


if __name__ == "__main__":
    main()
