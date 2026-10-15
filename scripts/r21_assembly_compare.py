"""Paired H/b assembly comparison on identical frozen boundary samples.

Each measurement runs in its own process. Timing includes tetrahedral basis and
matrix/right-hand-side assembly; input loading, sampling, CG, and refinement are
excluded. Whole-process peak working set is reported separately.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import statistics
import sys
import tempfile
import time

import numpy as np
import scipy.sparse as sp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import fit, io, metrics, runtime
from lutlab.entry import _write_report
from lutlab.performance import _paired_statistics


def worker(args):
    model = io.load_sparse(args.model)
    table = io.load_full(args.source, mmap=True)
    points, weights = fit.boundary_complete_points()
    target = table[points[:, 0], points[:, 1], points[:, 2]].astype(np.float64)
    started = time.perf_counter()
    if args.worker == "csr":
        H, transpose = fit._boundary_system(model.grid.astype(np.float64).tobytes(), model.m, 0x533231)
        b = transpose @ target
    else:
        H, b = fit.normal_equations(points, target, weights, model.grid)
    elapsed = time.perf_counter() - started
    result = {"assembly_seconds": elapsed, "nnz": int(H.nnz), "rows": len(points), "m": model.m}
    if args.matrix:
        sp.save_npz(str(args.matrix) + ".npz", H)
        np.save(str(args.matrix) + ".npy", b)
        prior = fit.fit_ls_sep(table, model.grid, "hat").reshape(-1, 3)
        nodes = fit.quantize(fit.int_refine(fit.solve_spd(H, b, prior), H, b).reshape(model.nodes.shape))
        if not np.array_equal(nodes, model.nodes):
            raise RuntimeError("assembly result changed frozen fitted node bytes")
        result["nodes_match_frozen_model"] = True
        result["nodes_sha256"] = hashlib.sha256(nodes.tobytes()).hexdigest()
    print(json.dumps(result), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", type=Path, default=ROOT / "artifacts/r21-boundary/study.json")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/r21-boundary/assembly-comparison.json")
    parser.add_argument("--worker", choices=["csr", "coo"])
    parser.add_argument("--model", type=Path)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--matrix", type=Path)
    args = parser.parse_args()
    if args.worker:
        worker(args)
        return
    os.environ.update(OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", OMP_NUM_THREADS="1")
    study = json.loads(args.study.read_text(encoding="utf-8"))
    if not study.get("structural_and_parity_pass"):
        raise RuntimeError("comparison needs a completed frozen study")
    case = next(row for row in study["cases"] if row["scenario"] == "clip-7" and row["m"] == 33)
    acceptance = json.loads(Path(case["result"]).read_text(encoding="utf-8"))
    model = Path(case["models"][1])
    source = Path(acceptance["sources"][1]["path"])
    files = [model, source, ROOT / "python/lutlab/fit.py", Path(__file__)]
    hashes = {str(path): metrics.file_sha256(path) for path in files}
    report = {"scope": __doc__, "input_sha256": hashes, "pairs": 7, "runs": []}

    def invoke(mode, matrix=None):
        command = [sys.executable, str(Path(__file__).resolve()), "--worker", mode,
                   "--model", str(model), "--source", str(source)]
        if matrix:
            command += ["--matrix", str(matrix)]
        record = runtime._execute(command)
        if record["returncode"]:
            raise RuntimeError(record["stderr"])
        return {"mode": mode, "command": command, **record, "result": json.loads(record["stdout"])}

    with tempfile.TemporaryDirectory(prefix="r21-assembly-") as temporary:
        directory = Path(temporary)
        preflight = [invoke(mode, directory / mode) for mode in ("coo", "csr")]
        H0, H1 = (sp.load_npz(directory / (mode + ".npz")) for mode in ("coo", "csr"))
        difference = H1 - H0
        b0, b1 = (np.load(directory / (mode + ".npy")) for mode in ("coo", "csr"))
        exact = not np.any(difference.data) and np.array_equal(b0, b1)
        report["preflight"] = {"H_and_b_bit_exact": bool(exact),
            "max_H_difference": float(abs(difference).max()), "max_b_difference": float(np.max(abs(b1 - b0))),
            "nodes_match_frozen_model": all(row["result"]["nodes_match_frozen_model"] for row in preflight),
            "executions": preflight}
        _write_report(args.output, report)
        if not exact:
            raise RuntimeError("matrix assembly is not bit-exact on the frozen preflight")
    for pair in range(7):
        order = ["coo", "csr"] if pair % 2 == 0 else ["csr", "coo"]
        for mode in order:
            report["runs"].append({"pair": pair, "order": order, **invoke(mode)})
            _write_report(args.output, report)
    ratios = []
    for pair in range(7):
        times = {row["mode"]: row["result"]["assembly_seconds"] for row in report["runs"] if row["pair"] == pair}
        ratios.append(times["coo"] / times["csr"])
    report["comparison"] = _paired_statistics(ratios, 2026101521)
    report["median_assembly_seconds"] = {mode: statistics.median(row["result"]["assembly_seconds"]
        for row in report["runs"] if row["mode"] == mode) for mode in ("coo", "csr")}
    report["median_process_peak_working_set_bytes"] = {mode: statistics.median(
        row["observed_peak_working_set_bytes"] for row in report["runs"]
        if row["mode"] == mode and row["observed_peak_working_set_bytes"] is not None)
        for mode in ("coo", "csr")}
    for path, digest in hashes.items():
        if metrics.file_sha256(path) != digest:
            raise RuntimeError("comparison source or input changed")
    report["inputs_unchanged"] = True
    _write_report(args.output, report)
    print(json.dumps({key: report[key] for key in ("median_assembly_seconds",
        "median_process_peak_working_set_bytes", "comparison")}, indent=2), flush=True)


if __name__ == "__main__":
    main()
