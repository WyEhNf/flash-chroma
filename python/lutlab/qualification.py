"""Problem-16 local acceptance with explicit source, scope and threshold evidence."""
from __future__ import annotations

import argparse
from contextlib import ExitStack
from datetime import datetime, timezone
import json
from pathlib import Path
import time

import numpy as np
from PIL import Image

from . import cache, data, io, metrics, runtime, validation


def _verify_sources(paths, reference):
    hashes = [metrics.file_sha256(path) for path in paths]
    if len(paths) != 4 or len(set(hashes)) != 4:
        raise ValueError("four byte-distinct original LUTs are required")
    with ExitStack() as stack:
        tables = [stack.enter_context(validation._mapped_full(path)) for path in paths]
        truth = stack.enter_context(validation._mapped_full(reference))
        for red in range(0, 256, 8):
            values = tables[0][red:red + 8].copy()
            for table in tables[1:]:
                values = table[values[..., 0], values[..., 1], values[..., 2]]
            if not np.array_equal(values, truth[red:red + 8]):
                raise ValueError(f"reference does not equal all four full LUTs at red block {red}")
    return [{"stage": stage, "path": str(path), "bytes": io.FULL_NBYTES, "sha256": digest}
            for stage, (path, digest) in enumerate(zip(paths, hashes), 1)]


def _model_provenance(models, sources):
    try:
        manifest_path = models[0].parent / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entry = cache.inspect_entry(models[0].parent, manifest["identity"])
        if entry is None or entry.paths != models:
            raise ValueError("invalid model manifest")
        identity = manifest["identity"]
        if identity["parameters"]["semantics"] != "independent":
            raise ValueError("model manifest is not an independent four-LUT fit")
        for expected, actual in zip(sources, identity["inputs"]):
            if (expected["stage"], expected["sha256"], expected["bytes"]) != (actual["stage"], actual["sha256"], actual["bytes"]):
                raise ValueError("model source binding differs from supplied full LUTs")
        return {"verified": True, "manifest": str(manifest_path),
                "manifest_sha256": metrics.file_sha256(manifest_path),
                "identity_sha256": manifest["identity_sha256"], "parameters": identity["parameters"],
                "fit": manifest.get("fit"), "algorithm_settings": identity.get("algorithm_settings")}
    except (OSError, ValueError, KeyError, TypeError) as error:
        return {"verified": False, "error": str(error)}


def accept(args):
    started = time.perf_counter()
    models = [path.resolve() for path in args.models]
    sources = [path.resolve() for path in args.full_luts]
    reference, listing = args.reference.resolve(), args.images.resolve()
    lines = [s.strip() for s in listing.read_text(encoding="utf-8").splitlines() if s.strip()]
    image_paths = [Path(s) if Path(s).is_absolute() else data.ROOT / s for s in lines]
    if len(image_paths) != 100 or len(set(map(str, image_paths))) != 100:
        raise ValueError("problem throughput acceptance requires 100 distinct image paths")
    for path in image_paths:
        with Image.open(path) as image:
            if image.mode != "RGB" or image.size != (1024, 768):
                raise ValueError(f"expected 1024x768 RGB8: {path}")
    source_records = _verify_sources(sources, reference)
    provenance = _model_provenance(models, source_records)
    if not provenance["verified"] and not args.allow_declared_models:
        raise ValueError("acceptance needs verified model-to-source binding: " + provenance["error"])
    report = {"started_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "local problem-16 structural and numerical acceptance; no official score",
        "official_threshold_known": args.threshold_origin == "official", "threshold_origin": args.threshold_origin,
        "official_dataset": False, "official_score_available": False,
        "sources": source_records, "reference_sha256": metrics.file_sha256(reference),
        "full_reference_composition_verified_colors": 256**3,
        "model_provenance": provenance, "n_images": 100,
        "images": {str(path): metrics.file_sha256(path) for path in image_paths},
        "image_list_sha256": metrics.file_sha256(listing), "backends": {}}
    for backend in (["cpu", "cuda"] if args.backend == "both" else [args.backend]):
        result = validation.validate(models, reference, listing, backend=backend,
            executable=args.cpu_executable if backend == "cpu" else args.cuda_executable,
            kernel=args.kernel if backend == "cpu" else "cuda_q16_fused4",
            threads=args.threads if backend == "cpu" else 0, device=args.device,
            threshold=args.threshold, metric=args.metric, full_cube=True,
            constraint_scope="both", competition=True, semantics="independent")
        result["threshold_diagnostics"] = {metric: {
            "all_100_images_pass": all(row[metric] < args.threshold for row in result["per_image"]),
            "whole_cube_pass": result["cube"][metric] < args.threshold}
            for metric in ("mean", "p99", "max")}
        report["backends"][backend] = result
        print(f"[accept] {backend}: cube_mean={result['cube']['mean']:.6f}, max={result['cube']['max']:.6f}, images={result['n_images']}, selected_gate={result['pass']}", flush=True)
    outputs = [row["mapped_cube_sha256"] for row in report["backends"].values()]
    report["backend_cube_sha256_equal"] = len(outputs) > 1 and len(set(outputs)) == 1
    if len(outputs) > 1 and not report["backend_cube_sha256_equal"]:
        raise RuntimeError("CPU and CUDA whole-cube outputs differ")
    for record in source_records:
        if metrics.file_sha256(record["path"]) != record["sha256"]:
            raise RuntimeError("source changed during acceptance")
    report["structural_contract_pass"] = provenance["verified"] and all(
        row["submission_contract_pass"] for row in report["backends"].values())
    report["selected_local_accuracy_pass"] = all(row["pass"] for row in report["backends"].values())
    report["pass"] = report["structural_contract_pass"] and report["selected_local_accuracy_pass"]
    report["elapsed_seconds"] = time.perf_counter() - started
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", nargs=4, required=True, type=Path)
    parser.add_argument("--full-luts", nargs=4, required=True, type=Path)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--images", required=True, type=Path)
    parser.add_argument("--backend", choices=["cpu", "cuda", "both"], default="both")
    parser.add_argument("--cpu-executable", type=Path)
    parser.add_argument("--cuda-executable", type=Path)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--kernel", default="auto")
    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--threshold", type=float, required=True)
    parser.add_argument("--threshold-origin", choices=["illustrative", "official"], default="illustrative")
    parser.add_argument("--metric", choices=["mean", "p99", "max"], default="max")
    parser.add_argument("--allow-declared-models", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    result = accept(parser.parse_args(argv))
    return 0 if result["pass"] else 2
