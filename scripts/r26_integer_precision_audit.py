"""Focused bit-precision audit of the integer Q16 model-selection numerator.

An independent Python-integer quadratic subtraction includes odd low bits,
values beyond uint64, and an exact -1 numerator hidden by float cancellation.
No LUT fitting, pixel run or performance measurement is repeated here.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys

import numpy as np
import scipy.sparse as sp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from lutlab import box, metrics
from lutlab.entry import _write_report


def exact_quadratic(raw_H, raw_b, nodes):
    n = len(nodes)
    return sum(int(nodes[i, c]) * int(raw_H[i, j]) * int(nodes[j, c])
               for c in range(3) for i in range(n) for j in range(n)) - 2 ** 17 * sum(
        int(raw_b[i, c]) * int(nodes[i, c]) for i in range(n) for c in range(3))


def main():
    report = {"scope": __doc__, "source_sha256": {name: metrics.file_sha256(ROOT / name) for name in (
        "python/lutlab/box.py", "scripts/r26_integer_precision_audit.py")}, "cases": []}
    large = np.diag(np.asarray([2 ** 50 + 113, 2 ** 49 + 41, 2 ** 50 + 67, 2 ** 49 + 17], dtype=np.int64))
    for i in range(3):
        large[i, i + 1] = large[i + 1, i] = 2 ** 47 + 19 + i
    rhs = np.arange(12, dtype=np.int64).reshape(4, 3) * (2 ** 35 + 11)
    old = np.array([[255, 128, 0], [20, 255, 90], [5, 70, 255], [200, 1, 30]], np.uint8)
    new = np.array([[0, 127, 5], [23, 254, 85], [8, 71, 250], [199, 7, 31]], np.uint8)
    fixtures = [("odd_low_bits_and_big_reduction", large, rhs, old, new)]
    h = 2 ** 45 + pow(509, -1, 2 ** 17)
    raw_H = np.diag(np.array([h, 2 ** 44 + 13, 2 ** 43 + 31, 2 ** 44 + 7], np.int64))
    raw_b = np.zeros((4, 3), np.int64)
    raw_b[0, 0] = (509 * h - 1) // 2 ** 17
    before = np.zeros((4, 3), np.uint8)
    before[0, 0] = 255
    after = before.copy()
    after[0, 0] = 254
    fixtures += [("negative_one_hidden_by_float", raw_H, raw_b, before, after),
                 ("positive_one_hidden_by_float", raw_H, raw_b, after, before)]
    for name, raw_H, raw_b, before, after in fixtures:
        H, b = sp.csr_matrix(raw_H.astype(np.float64) * 2. ** -38), raw_b.astype(np.float64) * 2. ** -22
        expected = exact_quadratic(raw_H, raw_b, after) - exact_quadratic(raw_H, raw_b, before)
        actual = box.integer_sse_change_numerator(H, b, before, after)
        def naive(nodes):
            values = nodes.astype(np.float64)
            return float(np.sum(values * (H @ values)) - 2 * np.sum(values * b))
        rounded = (naive(after) - naive(before)) * 2. ** 38
        if actual != expected:
            raise RuntimeError("integer model selection lost exact low bits")
        if name == "negative_one_hidden_by_float" and (expected != -1 or rounded == -1):
            raise RuntimeError("cancellation fixture does not exercise its stated case")
        if name == "positive_one_hidden_by_float" and expected != 1:
            raise RuntimeError("reverse comparison lost its sign")
        if name == "odd_low_bits_and_big_reduction" and abs(expected) <= 2 ** 64:
            raise RuntimeError("wide-reduction fixture did not exceed uint64")
        report["cases"].append({"name": name, "exact_numerator": str(actual),
            "independent_integer_oracle": str(expected), "naive_float_numerator": rounded, "pass": True})
    for name, digest in report["source_sha256"].items():
        if metrics.file_sha256(ROOT / name) != digest:
            raise RuntimeError("precision-audit source changed")
    report.update(finished_utc=datetime.now(timezone.utc).isoformat(), exact_integer_precision_pass=True)
    _write_report(ROOT / "artifacts/r26-box/integer-precision-audit.json", report)
    print(json.dumps(report["cases"], indent=2), flush=True)


if __name__ == "__main__":
    main()
