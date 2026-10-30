"""独立整数oracle核单调坐标切片收益、四面体分支与同轴批量更新。"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numba
import numpy as np
from lutlab import axis_calibration as ac, error_analysis as ea, fit, interp, io
from run_cinema_rounded import checked, load_inputs, read, rgb_keys


def main():
    numba.set_num_threads(4)
    first, second = np.meshgrid(np.arange(256), np.arange(256), indexing='ij')
    for axis in range(3):
        for code in (0, 127, 255):
            coordinates = [first.ravel(), second.ravel()]
            coordinates.insert(axis, np.full(65536, code))
            expected = np.ravel_multi_index(tuple(coordinates), (256, 256, 256))
            actual = np.fromiter((ac._slab_index(axis, code, t) for t in range(65536)), dtype=np.int64, count=65536)
            np.testing.assert_array_equal(actual, expected)
    plan = read(ROOT/'experiments/cinema-suffix-metric-v1.json')
    baseline, tables, _ = load_inputs(plan)
    parent = ROOT/'artifacts/cinema-suffix-metric-v1'
    selection = read(parent/'selection.json')
    spec = {'path': str(parent/'stage1_sweep004/stage1.slut'),
            'sha256': selection['candidates']['stage1_sweep004']['model_sha256']}
    model = io.load_sparse(checked(spec), competition=True)
    training = read(parent/'training.json')
    suffix = np.load(checked({'path': str(parent/'envelope-suffix.npy'),
        'sha256': training['artifact_sha256']['envelope-suffix.npy']}), mmap_mode='r')
    rng = np.random.default_rng(2026101906)
    pool = fit.stratified_points(2026101802)
    points = pool[rng.choice(len(pool), 4088, replace=False)]
    points = np.concatenate([points, np.array([[r, g, b] for r in (0, 255) for g in (0, 255) for b in (0, 255)], np.uint8)])
    targets = ea.source_apply(tables[0], points)
    reference = ea.exact_chain(tables, points)
    old = np.memmap(ROOT/plan['baseline_evidence']['cube']['path'], np.uint8, 'r', shape=(256**3, 3))[rgb_keys(points)]
    error = old.astype(np.int32)-reference.astype(np.int32)
    caps = np.maximum(49, np.sum(error*error, axis=1, dtype=np.int32))
    def terminal(rgb):
        for stage in baseline[1:]:
            rgb = interp.apply_tetra_q16(stage, rgb)
        return rgb
    terminal_targets = terminal(targets)
    np.testing.assert_array_equal(terminal_targets, suffix[rgb_keys(targets)])
    idx, original = model.tables()
    frac = original.astype(np.int64)
    nodes = model.nodes.reshape(-1, 3)
    predicted = np.array([ac._pixel(nodes, idx, frac, model.m, int(r), int(g), int(b), 0, 0)
                          for r, g, b in points], np.uint8)
    np.testing.assert_array_equal(predicted, interp.apply_tetra_q16(model, points))
    lower, upper = ac.bounds(idx, original, 4096)
    qlo, qhi = idx.astype(np.int64)*io.ONE+lower, idx.astype(np.int64)*io.ONE+upper
    if np.any(qhi[:, :-1] > qlo[:, 1:]) or not np.array_equal(lower[:, [0,255]], upper[:, [0,255]]):
        raise AssertionError('静态区间不足以保证任意同轴组合单调')
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64)); rho = root+.02*np.maximum(root-6., 0.)**2
    mass = rng.uniform(.2, 2., len(points)); mass /= mass.sum()
    def independent(candidate_frac):
        candidate = io.SparseLut(model.grid.copy(), model.nodes.copy(), idx.copy(), candidate_frac.astype(np.uint32))
        own = interp.apply_tetra_q16(candidate, points)
        final = terminal(own)
        error = own.astype(np.int32)-targets.astype(np.int32)
        local2 = np.sum(error*error, axis=1, dtype=np.int32)
        error = final.astype(np.int32)-terminal_targets.astype(np.int32)
        post2 = np.sum(error*error, axis=1, dtype=np.int32)
        error = final.astype(np.int32)-reference.astype(np.int32)
        violated = bool(np.any(np.sum(error*error, axis=1, dtype=np.int32) > caps))
        return float(mass@(rho[local2]+rho[post2])), violated
    initial, violating = independent(frac)
    if violating:
        raise AssertionError('合同起点需要满足冻结包络')
    common = (points, nodes, idx, frac, model.m, targets, terminal_targets, reference, caps, suffix, mass, rho, 1.)
    measured, nbad = ac._measure(*common, 4)
    maximum_error = abs(float(measured)-initial)
    checked_count, allowed_count = 0, 0
    for axis in range(3):
        order = np.argsort(points[:, axis], kind='stable').astype(np.int32)
        offsets = np.concatenate([[0], np.cumsum(np.bincount(points[:, axis], minlength=256))]).astype(np.int64)
        deltas = np.stack((np.minimum(frac[axis]+2048, upper[axis])-frac[axis],
                           np.maximum(frac[axis]-2048, lower[axis])-frac[axis]))
        before, gain, forbidden = ac._scores(*common, axis, deltas, order, offsets)
        maximum_error = max(maximum_error, abs(float(before.sum())-initial))
        codes = np.unique(points[:, axis])[1:-1:31]
        for code in codes:
            for direction in range(2):
                if not deltas[direction, code]:
                    continue
                changed = frac.copy(); changed[axis, code] += deltas[direction, code]
                value, violated = independent(changed)
                if bool(forbidden[direction, code]) != violated:
                    raise AssertionError('坐标切片的整链禁止位错误')
                if not violated:
                    maximum_error = max(maximum_error, abs(float(gain[direction, code])-(value-initial)))
                    allowed_count += 1
                checked_count += 1
        if axis == 2:
            gain[forbidden > 0] = np.inf
            direction = np.where((gain[0] < -1e-12) & (gain[0] <= gain[1]), 0,
                                 np.where(gain[1] < -1e-12, 1, -1))
            changed = frac.copy(); predicted_gain = 0.
            for code in np.flatnonzero(direction >= 0):
                d = direction[code]; changed[axis, code] += deltas[d, code]; predicted_gain += float(gain[d, code])
            after, violated = independent(changed)
            if violated or abs((after-initial)-predicted_gain) > 1e-11:
                raise AssertionError('同轴批量变化损失或包络不正确')
            effective = idx.astype(np.int64)*io.ONE+changed
            if np.any(np.diff(effective, axis=1) < 0):
                raise AssertionError('同轴组合打破单调性')
            batch_changes = int(np.count_nonzero(direction >= 0))
            frac[:] = changed
            new_measure, new_bad = ac._measure(*common, 4)
            if abs(float(new_measure)-after) > 1e-11 or new_bad:
                raise AssertionError('common未读取frac原位更新或整扫重算不正确')
    # 构造恰好保持当前终端输出的零容差保护，明确覆盖真正禁止的切片变化。
    current_model = io.SparseLut(model.grid.copy(), model.nodes.copy(), idx.copy(), frac.astype(np.uint32))
    tight_reference = terminal(interp.apply_tetra_q16(current_model, points))
    tight_common = list(common); tight_common[7] = tight_reference; tight_common[8] = np.zeros(len(points), np.int32)
    axis = 1
    order = np.argsort(points[:, axis], kind='stable').astype(np.int32)
    offsets = np.concatenate([[0], np.cumsum(np.bincount(points[:, axis], minlength=256))]).astype(np.int64)
    deltas = np.stack((np.minimum(frac[axis]+4096, upper[axis])-frac[axis],
                       np.maximum(frac[axis]-4096, lower[axis])-frac[axis]))
    _, _, tight_forbidden = ac._scores(*tight_common, axis, deltas, order, offsets)
    options = np.argwhere((tight_forbidden > 0) & (deltas != 0))
    if not len(options) or not batch_changes:
        raise AssertionError('合同必须实际覆盖禁止位和非空同轴批量变化')
    direction, code = map(int, options[0])
    changed = frac.copy(); changed[axis, code] += deltas[direction, code]
    changed_model = io.SparseLut(model.grid.copy(), model.nodes.copy(), idx.copy(), changed.astype(np.uint32))
    actual_violation = np.any(terminal(interp.apply_tetra_q16(changed_model, points)) != tight_reference)
    if not actual_violation:
        raise AssertionError('零容差禁止位没有对应独立oracle变化')
    if maximum_error > 1e-11 or not allowed_count or nbad:
        raise AssertionError('坐标损失与独立整数oracle不一致')
    print(json.dumps({'passed': 5, 'pixels': len(points), 'slab_changes': checked_count,
        'allowed_slab_changes': allowed_count, 'maximum_objective_error': maximum_error,
        'batched_changes': batch_changes, 'tight_forbidden_options': len(options), 'canonical_index_checks': 9*65536,
        'scope': '真实四面体/原表与后缀损失、切片禁止位及静态单调/同轴批量合同；非完整终验或性能结果'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
