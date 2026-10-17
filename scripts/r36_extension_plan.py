"""Predeclare the complete new-policy matrix without changing R29's denominator.

The original 200 source cases gain four new profiles at m17/25/33. The three
new capacity controls compare all nine frozen baseline and four new profiles.
No holdout pixels may be observed until both baseline and extension training
phases are complete and a combined class rule has been frozen.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import axisbins, corpus, selection
from lutlab.entry import _write_report


def main():
    output = ROOT / "datasets/problem16-v1/strategy-extension-r36.json"
    old_path = ROOT / "datasets/problem16-v1/strategy-plan.json"
    old = json.loads(old_path.read_text(encoding="utf-8"))
    catalog_paths = [ROOT / "datasets/problem16-v1/catalog.json", ROOT / "datasets/problem16-axis-bins-v1/catalog.json"]
    definitions = [json.loads(path.read_text(encoding="utf-8")) for path in catalog_paths]
    new_profiles = list(axisbins.PROFILES)
    if len(new_profiles) != 4 or len(old["profiles"]) != 9 or old["total_candidates"] != 5400:
        raise RuntimeError("profile universe changed; declare a separate matrix epoch")
    profiles = dict(old["profiles"])
    profiles.update({name: list(selection.PROFILES[name]) for name in new_profiles})
    cases = []
    for number, definition in enumerate(definitions):
        for case in definition["cases"]:
            cases.append({"id": case["id"], "catalog": number, "split": case["split"],
                          "family": case["family"], "intensity": case["intensity"],
                          "profiles": new_profiles if number == 0 else list(profiles)})
    if len(cases) != 203 or len({case["id"] for case in cases}) != 203:
        raise RuntimeError("expected 200 original cases and three distinct capacity controls")
    sizes = [17, 25, 33]
    keys = [f"{case['id']}/{profile}/m{m}" for case in cases for m in sizes for profile in case["profiles"]]
    if len(set(keys)) != 2517:
        raise RuntimeError("incomplete extension matrix")
    counts = Counter()
    for case in cases: counts[case["split"]] += len(sizes) * len(case["profiles"])
    value = {"schema": 1, "scope": __doc__, "kind": "additive_same_source_profile_comparison",
             "baseline_plan_sha256": corpus.digest_file(old_path), "baseline_candidates": 5400,
             "catalogs": [{"path": path.relative_to(ROOT).as_posix(), "sha256": corpus.digest_file(path)} for path in catalog_paths],
             "profiles": profiles, "new_profiles": new_profiles, "sizes": sizes, "cases": cases,
             "extension_candidates": len(keys), "combined_declared_candidates": 5400 + len(keys),
             "phase_expected_candidates": dict(counts),
             "expected_keyset_sha256": hashlib.sha256(corpus.canonical(sorted(keys))).hexdigest(),
             "case_order": "new capacity controls first in regression; other cases by mild/medium/strong then family and ID",
             "evidence_reuse": "only identical four ordered source/model bytes, reference, executable, kernel and probe cohort; keep prior execution proof hashes",
             "baseline_fitter": "byte-preserved R29 public fitter; new profiles use the explicit R33 algorithms",
             "holdout_policy": "combined baseline+extension class rule frozen after both complete training phases and before ANY holdout strategy outputs",
             "timing_policy": "no speed ranking from fitting or parallel cube scans; representative paired comparisons in a separate quiet stage",
             "plan_creation_is_measurement": False, "class_sweet_zone_proven": False, "official": False}
    if output.exists():
        if json.loads(output.read_text(encoding="utf-8")) != value:
            raise RuntimeError("preserve the existing predeclared plan; choose another epoch")
    else:
        _write_report(output, value)
    print(json.dumps({"extension_candidates": len(keys), "phase_expected_candidates": dict(counts),
                      "combined_declared_candidates": value["combined_declared_candidates"], "measurements_executed": False}))


if __name__ == "__main__":
    main()
