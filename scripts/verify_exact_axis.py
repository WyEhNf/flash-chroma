"""集中检验解析事件表，不代替完整模型精度或性能验收。"""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numba
import numpy as np
from numba import njit
from lutlab import axis_calibration as ac, exact_axis as ex, interp, io, study_provenance


@njit(cache=False)
def brute(points, nodes, idx, frac, m, targets, terminal, reference, caps, suffix, mass,
          rho, axis, lower, upper, cost, forbidden):
    maximum = 0.
    mismatches = 0
    tested = 0
    for code in range(256):
        ids = np.where(points[:, axis] == code)[0]
        if len(ids) == 0:
            continue
        for f in range(lower[code], upper[code]+1):
            loss, violations = 0., 0
            delta = f-frac[axis, code]
            for p in ids:
                rgb = ac._pixel(nodes, idx, frac, m, int(points[p, 0]), int(points[p, 1]), int(points[p, 2]), axis, delta)
                value, squared = ac._cost(rgb[0], rgb[1], rgb[2], targets[p], terminal[p], reference[p], suffix, rho, 1.)
                loss += mass[p]*value
                violations += squared > caps[p]
            j = f-lower[code]
            maximum = max(maximum, abs(loss-cost[code, j]))
            mismatches += violations != forbidden[code, j]
            tested += 1
    return maximum, mismatches, tested


def main():
    numba.set_num_threads(4)
    rng = np.random.default_rng(2026101908)
    grid = np.tile(np.linspace(0, 255, 17, dtype=np.float32), (3, 1))
    model = io.SparseLut(grid, rng.integers(0, 256, (17, 17, 17, 3), dtype=np.uint8))
    idx, fraction = model.tables()
    frac = fraction.astype(np.int64)
    points = rng.integers(0, 256, (96, 3), dtype=np.uint8)
    # 同码值但不同其余轴，包含跨越两个四面体排序面的情况。
    points[:32] = points[:32] % 32+112
    for axis in range(3):
        points[32+axis*16:48+axis*16, axis] = 128
    suffix = np.load(ROOT/'artifacts/cinema-axis-calibration-v1/envelope-suffix.npy', mmap_mode='r')
    targets = rng.integers(0, 256, points.shape, dtype=np.uint8)
    terminal = suffix[targets.astype(np.int64)@np.array([65536, 256, 1], np.int64)]
    start = interp.apply_tetra_q16(model, points)
    reference = suffix[start.astype(np.int64)@np.array([65536, 256, 1], np.int64)]
    caps = np.zeros(len(points), np.int32)
    mass = rng.random(len(points)); mass /= mass.sum()
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    rho = root+.02*np.maximum(root-6., 0.)**2
    lower, upper = ac.bounds(idx, fraction, 4096)
    results = []
    for axis in range(3):
        order = np.argsort(points[:, axis], kind='stable').astype(np.int64)
        offsets = np.r_[0, np.cumsum(np.bincount(points[:, axis], minlength=256))].astype(np.int64)
        width = int(np.max(upper[axis]-lower[axis]))+1
        common = (points, model.nodes.reshape(-1, 3), idx, frac, model.m, targets, terminal,
                  reference, caps, suffix, mass, rho)
        diff, forbidden_diff, baseline, counts, invalid = ex.events(*common, 1., axis, lower[axis], upper[axis], order, offsets, width)
        if np.any(invalid):
            raise AssertionError('出现非前进舍入事件')
        losses, forbidden = np.cumsum(diff, axis=1), np.cumsum(forbidden_diff, axis=1)
        error, mismatch, tested = brute(*common, axis, lower[axis], upper[axis], losses, forbidden)
        if error > 1e-8 or mismatch:
            raise AssertionError((axis, error, mismatch))
        if not np.any(forbidden > 0):
            raise AssertionError('构造未覆盖禁止区间')
        # 额外经独立通用整数oracle核跨排序面与下降斜率，不只比较事件代码自身。
        for f in (0, 1, 1024, 4096, 32768, 65535, 65536):
            changed = fraction.copy(); changed[axis, 128] = f
            candidate = io.SparseLut(grid, model.nodes, idx, changed)
            subset = points[points[:, axis] == 128]
            oracle = interp.apply_tetra_q16(candidate, subset)
            raw = []
            for r, g, b in subset:
                c, slope = ex._line(model.nodes.reshape(-1, 3), idx, frac, 17, int(r), int(g), int(b), axis, f)
                raw.append((c+slope*f)//io.ONE)
            np.testing.assert_array_equal(np.asarray(raw), oracle)
        results.append({'axis': axis, 'all_integer_fraction_choices_checked': tested,
            'maximum_objective_difference': error, 'cap_count_mismatches': mismatch,
            'event_visits': int(counts.sum()), 'forbidden_choice_count': int(np.count_nonzero(forbidden))})
    output = {'environment': study_provenance.environment_fingerprint(), 'numba_threads': 4,
        'source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
            (Path(__file__), ROOT/'python/lutlab/exact_axis.py')}, 'results': results,
        'scope': '随机RGB8节点含下降斜率，96点和实际±4096静态边界全部整数frac枚举；零cap及独立整数oracle跨排序面；非完整模型验收'}
    print(json.dumps(output, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
