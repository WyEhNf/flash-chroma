"""One real-data integration: fit, immutable cache reuse, selector and native runtime."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
from types import SimpleNamespace

for key in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ[key] = "1"

from lutlab import cli, data, metrics, selection


def main():
    root = data.ROOT
    output = root / "artifacts" / "r17-integration"
    data.DATA = output / "data"
    source = root / "artifacts" / "r17-algorithm" / "isp-0"
    destination = data.scenario_dir("isp-0")
    destination.mkdir(parents=True, exist_ok=True)
    for name in [*(f"lut{stage}.lut256" for stage in range(1, 5)), "composite.lut256"]:
        target = destination / name
        if not target.exists():
            shutil.copyfile(source / name, target)
        if metrics.file_sha256(target) != metrics.file_sha256(source / name):
            raise ValueError(f"integration source mismatch: {target}")
    metadata = {"id": "isp-0", "source": "frozen r17 algorithm assets",
                "sha256": {f"lut{stage}": metrics.file_sha256(destination / f"lut{stage}.lut256")[:16]
                           for stage in range(1, 5)}}
    (destination / "meta.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    args = SimpleNamespace(scenario="isp-0", m=18, method="ls_tetra_int", mode="seq",
                           grid="uniform", adaptive=False)
    entry = cli.model_entry(args)
    reused = cli.model_entry(args, existing_only=True)
    if reused is None or reused.directory != entry.directory:
        raise AssertionError("verified cache did not reuse a complete batch")
    for stage, path in enumerate(entry.paths, 1):
        if path.read_bytes() != (source / "baseline_m18" / f"stage{stage}.slut").read_bytes():
            raise AssertionError("public fitting path changed frozen baseline model bytes")
    result = selection.select("isp-0", [18], ["tetra"], 2.0,
        root / "artifacts" / "r17-acceptance" / "eval.txt",
        root / "artifacts" / "r17-acceptance" / "bench.txt", 4, 1,
        existing_only=True, constraint_scope="both", executable=metrics.resolve_jshc())
    if result["winner"] is None or len(result["pareto"]) != 1:
        raise AssertionError("qualified independent candidate missing from selector")
    if result["candidates"][0]["accuracy"]["model_contract"]["semantics_evidence"] != "verified_model_manifest":
        raise AssertionError("selector validation did not verify model provenance")
    report = {"scope": "one functional integration run, not an additional speed comparison",
              "cache_batch_reused": True, "all_four_models_match_frozen_baseline": True,
              "manifest": str(entry.directory / "manifest.json"), "selection": result}
    (output / "integration.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "selection"}, indent=2))


if __name__ == "__main__":
    main()
