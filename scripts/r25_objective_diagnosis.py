"""Separate exact LS data-objective changes from actual rounded one-stage errors.

Two preselected first-stage cases are evaluated: clip-7/m33 (large mean gain)
and clip-31/m18 (still fails the image gate). R22, R24 and R25 models have the
same fixed grid. Exact H,b/C moments evaluate their unrounded quadratic; the
native CPU cube command separately evaluates actual integer-rounded output.
Neither quantity is an additive decomposition or a final-chain optimality bound.
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tempfile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import fullfit, io, metrics, runtime, validation
from lutlab.entry import _write_report

CASES = [("clip-7", 33, 1), ("clip-31", 18, 1)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/r25-full/objective-diagnosis.json")
    args = parser.parse_args()
    cpu = args.cpu.resolve()
    study_path = ROOT / "artifacts/r25-full/study.json"
    study = json.loads(study_path.read_text(encoding="utf-8"))
    if not study.get("structural_parity_and_full_domain_pass"):
        raise RuntimeError("complete R25 acceptance first")
    if fullfit.trainer_fingerprint() != study["trainer"]:
        raise RuntimeError("diagnosis must use the frozen native trainer")
    files = [study_path, Path(__file__).resolve(), cpu, *(ROOT / n for n in fullfit.NATIVE_SOURCES),
             ROOT / "python/lutlab/fullfit.py", ROOT / "python/lutlab/validation.py", fullfit.resolve_library()]
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__,
              "predeclared_cases": CASES, "cases": []}
    for scenario, m, stage in CASES:
        case = next(c for c in study["cases"] if (c["scenario"], c["m"]) == (scenario, m))
        path = Path(case["result"])
        if metrics.file_sha256(path) != case["result_sha256"]:
            raise RuntimeError("frozen final-chain evidence changed")
        result = json.loads(path.read_text(encoding="utf-8"))
        target = Path(result["sources"][stage - 1]["path"])
        paths = {"r22": Path(case["baseline_models"][stage - 1]),
                 "r24": Path(case["supported_models"][stage - 1]), "r25": Path(case["models"][stage - 1])}
        models = {key: io.load_sparse(value, competition=True) for key, value in paths.items()}
        if any(not np.array_equal(value.grid, models["r25"].grid) or
               any(not np.array_equal(a, b) for a, b in zip(value.tables(), models["r25"].tables()))
               for value in models.values()):
            raise RuntimeError("fixed-grid objective comparison requires identical axis tables")
        inputs = [target, path, *paths.values()]
        hashes = {str(p): metrics.file_sha256(p) for p in inputs}
        values = {}
        with ExitStack() as stack, tempfile.TemporaryDirectory(prefix="r25-stage-") as directory:
            truth = stack.enter_context(validation._mapped_full(target))
            H, b, assembly = fullfit.normal_equations(truth, models["r25"].grid)
            C = assembly["target_norm_squared_scaled"]
            for mode, model in models.items():
                x = model.nodes.reshape(-1, 3).astype(np.float64)
                value = float(np.sum(x * (H @ x)) - 2 * np.sum(x * b) + C)
                if value < 0:
                    raise RuntimeError("negative unrounded objective on a nontrivial diagnostic LUT")
                raw = Path(directory) / f"{mode}.rgb"
                execution = runtime.cube([paths[mode]], raw, backend="cpu", executable=cpu,
                    kernel="tetra_avx2", threads=4, competition=False)
                with validation._mapped_full(raw) as mapped:
                    rounded = validation._cube_stats(mapped, truth, 3, threshold=2.)
                values[mode] = {"unrounded_sse_float64_evaluation": 64 * value,
                    "unrounded_rms": float(np.sqrt(value / (64 ** 3))),
                    "quadratic_scope": "float64 evaluation of exact integer moments; not a global optimality certificate",
                    "actual_rounded_stage": rounded, "native_cube": execution,
                    "mapped_sha256": metrics.file_sha256(raw)}
        for name, digest in hashes.items():
            if metrics.file_sha256(name) != digest:
                raise RuntimeError("diagnostic input changed")
        files += inputs
        report["cases"].append({"scenario": scenario, "m": m, "stage": stage,
            "input_sha256": hashes, "assembly": assembly, "objectives": values})
        print(f"[objective] {scenario}/m{m}/stage{stage}: " + "; ".join(
            f"{mode} unrounded_rms={row['unrounded_rms']:.6f}, rounded_rms={row['actual_rounded_stage']['rms']:.6f}"
            for mode, row in values.items()), flush=True)
    report["source_and_input_sha256"] = {str(p): metrics.file_sha256(p) for p in files}
    report["finished_utc"] = datetime.now(timezone.utc).isoformat()
    report["fixed_grid_objective_and_integer_stage_diagnosis_pass"] = True
    _write_report(args.output.resolve(), report)


if __name__ == "__main__":
    main()
