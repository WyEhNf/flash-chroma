"""Audit clipping of unconstrained full-domain solutions, without tuning models.

Reconstruct two previously qualified float solutions and measure feasibility
and the box-constrained data objective's KKT residual after clipping to RGB8
range. This is a diagnosis of the current fitter, not a new candidate test.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import fit, fullfit, io, metrics, validation
from lutlab.entry import _write_report


def main():
    path = ROOT / "artifacts/r25-full/study.json"
    study = json.loads(path.read_text(encoding="utf-8"))
    if not study.get("structural_parity_and_full_domain_pass") or fullfit.trainer_fingerprint() != study["trainer"]:
        raise RuntimeError("requires the identical completed R25 fitter")
    files = [path, Path(__file__).resolve(), ROOT / "python/lutlab/fit.py", ROOT / "python/lutlab/fullfit.py", fullfit.resolve_library()]
    rows = []
    for scenario, m in (("clip-7", 33), ("clip-31", 18)):
        case = next(c for c in study["cases"] if (c["scenario"], c["m"]) == (scenario, m))
        result_path = Path(case["result"])
        if metrics.file_sha256(result_path) != case["result_sha256"]:
            raise RuntimeError("qualified reference changed")
        result = json.loads(result_path.read_text(encoding="utf-8"))
        source, model_path = Path(result["sources"][0]["path"]), Path(case["models"][0])
        model = io.load_sparse(model_path, competition=True)
        detail = {}
        with validation._mapped_full(source) as table:
            raw, H, b = fit.fit_full_tetra(table, model.grid, diagnostics=detail)
        x = raw.reshape(-1, 3)
        clipped = np.clip(x, 0, 255)
        gradient = H @ clipped - b
        projected = gradient.copy()
        projected[((clipped == 0) & (gradient >= 0)) | ((clipped == 255) & (gradient <= 0))] = 0
        def objective(value):
            return float(np.sum(value * (H @ value)) - 2 * np.sum(value * b) + detail["target_norm_squared_scaled"])
        row = {"scenario": scenario, "m": m, "stage": 1, "solver": detail["solver"],
            "float_min": float(x.min()), "float_max": float(x.max()),
            "float_components_below_zero": int(np.count_nonzero(x < 0)),
            "float_components_above_255": int(np.count_nonzero(x > 255)),
            "total_components": int(x.size), "clipped_float_projected_gradient_inf": float(np.max(abs(projected))),
            "maximum_free_coordinate_quadratic_displacement": float(np.max(abs(projected / H.diagonal()[:, None]))),
            "unrounded_rms": {"raw_float": float(np.sqrt(max(0, objective(x)) / 64 ** 3)),
                              "clipped_float": float(np.sqrt(max(0, objective(clipped)) / 64 ** 3)),
                              "qualified_integer": float(np.sqrt(max(0, objective(model.nodes.reshape(-1, 3).astype(float))) / 64 ** 3))},
            "scope": "unregularised full-domain data objective; projected gradient is diagnostic, not a final-chain error bound"}
        rows.append(row)
        files += [source, model_path, result_path]
        print(json.dumps(row), flush=True)
    _write_report(ROOT / "artifacts/r25-full/box-constraint-diagnosis.json", {
        "finished_utc": datetime.now(timezone.utc).isoformat(), "scope": __doc__, "cases": rows,
        "source_and_input_sha256": {str(p): metrics.file_sha256(p) for p in files}})


if __name__ == "__main__":
    main()
