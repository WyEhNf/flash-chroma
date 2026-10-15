"""One real public-entry fit/cache/selector check using frozen R17 source LUTs."""
from __future__ import annotations

import argparse
import datetime as dt
from functools import wraps
import json
import os
from pathlib import Path
import shutil
import sys
import time
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
for variable in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[variable] = "1"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts" / "r18-integration")
    parser.add_argument("--executable", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    os.environ["JSHC_LOG_DIR"] = str(output / "logs")
    from lutlab import cache, cascade, cli, data, metrics, selection

    started = dt.datetime.now(dt.timezone.utc).isoformat()
    clock = time.perf_counter()
    data.DATA = output / "data"
    source = ROOT / "artifacts" / "r17-algorithm" / "isp-0"
    destination = data.scenario_dir("isp-0")
    destination.mkdir(parents=True, exist_ok=True)
    sources = [source / f"lut{stage}.lut256" for stage in range(1, 5)]
    source_hashes = [metrics.file_sha256(path) for path in sources]
    if len(set(source_hashes)) != 4:
        raise AssertionError("integration requires four genuinely different source LUTs")
    links = []
    for name in [*(f"lut{stage}.lut256" for stage in range(1, 5)), "composite.lut256"]:
        target = destination / name
        if not target.exists():
            try:
                target.hardlink_to(source / name)
                links.append({"path": str(target), "mode": "hardlink"})
            except OSError:
                shutil.copyfile(source / name, target)
                links.append({"path": str(target), "mode": "copy"})
        if metrics.file_sha256(target) != metrics.file_sha256(source / name):
            raise AssertionError(f"integration source mismatch: {target}")
    metadata = {"id": "isp-0", "source": "frozen R17 full LUTs reused by R18",
                "sha256": {f"lut{k}": digest[:16] for k, digest in enumerate(source_hashes, 1)}}
    (destination / "meta.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    model_args = SimpleNamespace(scenario="isp-0", m=18, method="ls_tetra_jitter", mode="seq",
                                grid="dp", adaptive=False)
    namespace = cli.model_dir(model_args)
    fit_argv = ["fit", "--scenario", "isp-0", "--m", "18", "--mode", "seq",
                "--method", "ls_tetra_jitter", "--grid", "dp", "--model-dir", str(namespace),
                "--inputs", *map(str, sources)]
    initial_entry = cli.model_entry(model_args, existing_only=True)
    cli.main(fit_argv)
    entry = cli.model_entry(model_args, existing_only=True)
    if entry is None:
        raise AssertionError("public CLI did not publish a verified model batch")
    relocated_argv = [*fit_argv[:-4], *(str(destination / path.name) for path in sources)]
    # A repeated CLI fit must not call the numerical fitter, including when the
    # same bytes came from another path. This assertion does not mock validation.
    @wraps(cascade.fit_cascade_sequential)
    def refuse_refit(*unused_args, **unused_kwargs):
        raise AssertionError("unexpected refit")

    with patch.object(cascade, "fit_cascade_sequential", new=refuse_refit):
        cli.main(relocated_argv)
    reused = cli.model_entry(model_args, existing_only=True)
    if reused is None or reused.directory != entry.directory:
        raise AssertionError("cache reuse did not preserve the complete model batch")
    frozen = ROOT / "artifacts" / "r18-algorithm" / "isp-0" / "dp_jitter_m18"
    for stage, path in enumerate(entry.paths, 1):
        if path.read_bytes() != (frozen / f"stage{stage}.slut").read_bytes():
            raise AssertionError("public fitting path differs from frozen R18 DP+jitter bytes")

    evaluation = ROOT / "artifacts" / "r17-acceptance" / "eval.txt"
    result = selection.select("isp-0", [18], ["dp_jitter"], 2.0, evaluation, evaluation,
        threads=4, reps=1, existing_only=True, constraint_scope="both", executable=args.executable)
    if result["winner"] is None or len(result["pareto"]) != 1:
        raise AssertionError("qualified independent candidate missing from selector")
    row = result["candidates"][0]
    if row["accuracy"]["model_contract"]["semantics_evidence"] != "verified_model_manifest":
        raise AssertionError("selector validation did not verify model provenance")
    if row["manifest"] != str(entry.directory / "manifest.json"):
        raise AssertionError("selector did not reuse the CLI-published batch")
    report = {
        "started_utc": started, "completed_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "elapsed_s": time.perf_counter() - clock,
        "scope": "one public CLI fit, content-addressed reuse, and native selector acceptance; not a speed comparison",
        "official_threshold_known": False, "illustrative_gate": "every image mean < 2 and full cube mean < 2",
        "public_fit_argv": fit_argv, "cache_reuse_argv": relocated_argv,
        "initial_verified_model_present": initial_entry is not None,
        "cache_batch_reused_without_refitting": True, "input_path_is_not_identity": True,
        "all_four_models_match_frozen_r18": True, "four_distinct_source_sha256": source_hashes,
        "source_reuse": links, "manifest": str(entry.directory / "manifest.json"),
        "algorithm_settings": entry.manifest["identity"]["algorithm_settings"],
        "identity_sha256": entry.manifest["identity_sha256"],
        "original_fit_created_utc": entry.manifest["created_utc"],
        "original_fit_s": entry.manifest["fit"]["fit_s"],
        "selection_code_sha256": cache.file_sha256(ROOT / "python" / "lutlab" / "selection.py"),
        "selection": result,
    }
    (output / "integration.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "selection"}, indent=2))


if __name__ == "__main__":
    main()
