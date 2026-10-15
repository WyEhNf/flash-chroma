"""Trace already-measured hotspots through exact and sparse independent stages.

The isolated-stage error substitutes one sparse stage at the exact intermediate
input, then completes the remaining full LUTs. It is diagnostic, not an additive
decomposition, a new held-out measurement, or a performance benchmark.
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import interp, io, metrics, validation


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, default=ROOT / "artifacts/r20-validation/audit.json")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/r20-validation/hotspot-traces.json")
    parser.add_argument("--scenarios", nargs="+", default=["clip-7"])
    args = parser.parse_args()
    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    traces = []
    for case in audit["cases"]:
        if case["scenario"] not in args.scenarios:
            continue
        result_path = Path(case["result"])
        result_sha = metrics.file_sha256(result_path)
        if case.get("result_sha256") and result_sha != case["result_sha256"]:
            raise RuntimeError("frozen hotspot evidence changed")
        result = json.loads(result_path.read_text(encoding="utf-8"))
        models = [io.load_sparse(path) for path in case["models"]]
        with ExitStack() as stack:
            tables = [stack.enter_context(validation._mapped_full(Path(row["path"]))) for row in result["sources"]]
            for hotspot in result["backends"]["cpu"]["cube"]["hotspots"][:5]:
                original = np.asarray([hotspot["rgb"]], dtype=np.uint8)
                exact = original.copy()
                sparse = original.copy()
                final = original.copy()
                for table in tables:
                    final = io.apply_full(table, final)
                stages = []
                for index, (table, model) in enumerate(zip(tables, models)):
                    own_target = io.apply_full(table, exact)
                    own_prediction = interp.apply_tetra_q16(model, exact)
                    sparse_next = interp.apply_tetra_q16(model, sparse)
                    isolated = own_prediction.copy()
                    for remaining in tables[index + 1:]:
                        isolated = io.apply_full(remaining, isolated)
                    stages.append({"stage": index + 1, "exact_input": exact[0].tolist(),
                        "sparse_chain_input": sparse[0].tolist(), "exact_output": own_target[0].tolist(),
                        "sparse_chain_output": sparse_next[0].tolist(),
                        "sparse_at_exact_input": own_prediction[0].tolist(),
                        "isolated_final_delta_e": float(np.linalg.norm(isolated.astype(float) - final))})
                    exact, sparse = own_target, sparse_next
                error = float(np.linalg.norm(sparse.astype(float) - final))
                if error != hotspot["delta_e"]:
                    raise RuntimeError("hotspot trace disagrees with native whole-cube evidence")
                traces.append({"scenario": case["scenario"], "m": case["m"], "rgb": hotspot["rgb"],
                    "result_sha256": result_sha, "final_delta_e": error, "stages": stages})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"scope": __doc__, "traces": traces}, indent=2) + "\n", encoding="utf-8")
    for scenario, m in sorted({(row["scenario"], row["m"]) for row in traces}):
        row = next(row for row in traces if (row["scenario"], row["m"]) == (scenario, m))
        print(f"{scenario}/m{m} rgb={row['rgb']} final={row['final_delta_e']:.6f} isolated="
              + str([round(stage["isolated_final_delta_e"], 6) for stage in row["stages"]]))


if __name__ == "__main__":
    main()
