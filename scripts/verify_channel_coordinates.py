"""集中验证实验分通道坐标的完整事件/单调DP/独立整数前向，不测真实拟合收益。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numba
from numba import njit
import numpy as np
from lutlab import channel_coordinates as cc, interp, io, monotone_axis, study_provenance


def integer_oracle(model, points):
    """每个输出通道独立比较器排序、uint64四权重累加，不用实验模块的像素核。"""
    result = np.empty((len(points), 3), np.uint8)
    idx = model.idx
    base = (idx[0, points[:, 0]].astype(np.int64)*model.m+idx[1, points[:, 1]])*model.m+idx[2, points[:, 2]]
    for channel in range(3):
        f = np.column_stack([model.channel_frac[channel, a, points[:, a]] for a in range(3)]).astype(np.int64)
        stride = np.tile(np.array([model.m**2, model.m, 1], np.int64), (len(points), 1))
        for a, b in ((0, 1), (1, 2), (0, 1)):
            swap = f[:, a] < f[:, b]
            f[swap, a], f[swap, b] = f[swap, b].copy(), f[swap, a].copy()
            stride[swap, a], stride[swap, b] = stride[swap, b].copy(), stride[swap, a].copy()
        weights = np.column_stack((io.ONE-f[:, 0], f[:, 0]-f[:, 1], f[:, 1]-f[:, 2], f[:, 2])).astype(np.uint64)
        indices = np.column_stack((base, base+stride[:, 0], base+stride[:, :2].sum(axis=1), base+model.m**2+model.m+1))
        acc = np.sum(weights*model.nodes.reshape(-1, 3).astype(np.uint64)[indices, channel], axis=1, dtype=np.uint64)
        if np.any(weights.sum(axis=1, dtype=np.uint64) != io.ONE) or np.any(acc > 255*io.ONE):
            raise AssertionError('独立u64守恒或累加界失败')
        result[:, channel] = ((acc+io.ONE//2) >> io.Q).astype(np.uint8)
    return result


@njit(cache=False)
def brute(points, nodes, idx, frac, m, targets, mass, caps, output, squared, rho, channel, axis, losses, violations):
    fcopy = frac.copy()
    maximum, mismatches = 0., 0
    for f in range(io.ONE+1):
        fcopy[channel, axis, 128] = f
        cost, bad = 0., 0
        for p in range(len(points)):
            other = squared[p]-(np.int64(output[p, channel])-np.int64(targets[p, channel]))**2
            value = cc._pixel(nodes, idx, fcopy, m, int(points[p, 0]), int(points[p, 1]), int(points[p, 2]), channel)
            d2 = other+(value-np.int64(targets[p, channel]))**2
            cost += mass[p]*rho[d2]
            bad += int(d2 > caps[p])
        maximum = max(maximum, abs(cost-losses[f]))
        mismatches += int(bad != violations[f])
    return maximum, mismatches


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): raise ValueError('不覆盖旧合同')
    args.output.mkdir(parents=True)
    numba.set_num_threads(4)
    rng = np.random.default_rng(2026101914)
    grid = np.tile(np.linspace(0, 255, 17), (3, 1))
    sparse = io.SparseLut(grid, rng.integers(116, 140, (17, 17, 17, 3), dtype=np.uint8))
    rep = cc.from_sparse(sparse)
    check = rng.integers(0, 256, (1033, 3), dtype=np.uint8)
    check[:8] = np.array(np.meshgrid(*[[0, 255]]*3, indexing='ij')).reshape(3, -1).T
    np.testing.assert_array_equal(cc.predict(rep, check), interp.apply_tetra_q16(sparse, check))
    np.testing.assert_array_equal(cc.predict(rep, check), integer_oracle(rep, check))
    for channel in range(3):
        for axis in range(3):
            change = (channel*3+axis-4)*173
            rep.channel_frac[channel, axis] = np.clip(rep.channel_frac[channel, axis].astype(np.int64)+change, 0, io.ONE)
            rep.channel_frac[channel, axis, [0, 255]] = [0, io.ONE]
    cc.validate(rep)
    np.testing.assert_array_equal(cc.predict(rep, check), integer_oracle(rep, check))
    grid33 = np.tile(np.linspace(0, 255, 33), (3, 1))
    sparse33 = io.SparseLut(grid33, rng.integers(0, 256, (33, 33, 33, 3), dtype=np.uint8))
    rep33 = cc.from_sparse(sparse33)
    np.testing.assert_array_equal(cc.predict(rep33, check), interp.apply_tetra_q16(sparse33, check))
    for channel in range(3):
        rep33.channel_frac[channel, :, 1:255] = np.clip(
            rep33.channel_frac[channel, :, 1:255].astype(np.int64)+(channel-1)*113, 0, io.ONE)
    cc.validate(rep33)
    np.testing.assert_array_equal(cc.predict(rep33, check), integer_oracle(rep33, check))
    frac = rep.channel_frac.astype(np.int64)
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    rho = root+.02*np.maximum(root-6., 0.)**2
    records = []
    for channel in range(3):
        for axis in range(3):
            points = rng.integers(0, 256, (17, 3), dtype=np.uint8); points[:, axis] = 128
            targets = rng.integers(118, 138, points.shape, dtype=np.uint8)
            output = cc.predict(rep, points)
            error = output.astype(np.int32)-targets.astype(np.int32)
            squared = np.sum(error*error, axis=1, dtype=np.int32)
            caps = squared+rng.integers(0, 45, len(points), dtype=np.int32)
            caps[:2] = squared[:2]
            mass = rng.random(len(points)); mass[:2] = 0; mass /= mass.sum()
            order = np.argsort(points[:, axis], kind='stable').astype(np.int64)
            offsets = np.r_[0, np.cumsum(np.bincount(points[:, axis], minlength=256))].astype(np.int64)
            diff, bd, baseline, count, invalid = cc.events(points, rep.nodes.reshape(-1, 3), rep.idx, frac,
                rep.m, targets, mass, caps, output, squared, rho, channel, axis, order, offsets)
            if np.any(invalid): raise AssertionError('事件没有前进')
            costs, violations = np.cumsum(diff, axis=1), np.cumsum(bd, axis=1)
            del diff, bd
            maximum, mismatches = brute(points, rep.nodes.reshape(-1, 3), rep.idx, frac, rep.m,
                targets, mass, caps, output, squared, rho, channel, axis, costs[128], violations[128])
            if maximum > 1e-8 or mismatches: raise AssertionError((maximum, mismatches))
            assert np.count_nonzero(violations) > 0
            old = frac[channel, axis].copy()
            np.testing.assert_allclose(costs[np.arange(256), old], baseline, rtol=0, atol=1e-12)
            selected, predicted = monotone_axis.choose_axis(costs, violations, rep.idx[axis], old)
            del costs, violations
            trial = frac.copy(); trial[channel, axis] = selected
            assert np.all(np.diff(rep.idx[axis].astype(np.int64)*io.ONE+selected) >= 0)
            np.testing.assert_array_equal(selected[[0, 255]], old[[0, 255]])
            cached, checked_squared = output.copy(), squared.copy()
            cc._refresh(points, rep.nodes.reshape(-1, 3), rep.idx, trial, rep.m, targets, cached, checked_squared, channel)
            candidate = cc.ChannelLut(rep.grid, rep.nodes, rep.idx, trial.astype(np.uint32))
            independent = integer_oracle(candidate, points)
            np.testing.assert_array_equal(cached, independent)
            np.testing.assert_array_equal(cached[:, [c for c in range(3) if c != channel]], output[:, [c for c in range(3) if c != channel]])
            difference = independent.astype(np.int32)-targets.astype(np.int32)
            np.testing.assert_array_equal(checked_squared, np.sum(difference*difference, axis=1, dtype=np.int32))
            assert not np.any(checked_squared > caps)
            assert abs(float(mass@rho[checked_squared])-predicted) < 1e-8
            for f in (0, 1, 16384, 32768, 65535, 65536):
                trial = frac.copy(); trial[channel, axis, 128] = f
                candidate = cc.ChannelLut(rep.grid, rep.nodes, rep.idx, trial.astype(np.uint32))
                np.testing.assert_array_equal(cc._predict(points, rep.nodes.reshape(-1, 3), rep.idx, trial, rep.m), integer_oracle(candidate, points))
            records.append({'channel': channel, 'axis': axis, 'integer_states': io.ONE+1, 'points': len(points),
                'maximum_event_cost_difference': maximum, 'cap_count_mismatches': mismatches,
                'integer_forward_mismatches': 0, 'other_channel_cache_mismatches': 0,
                'dp_monotone_endpoints_and_cap_pass': True, 'events': int(count.sum())})
    files = [Path(__file__), *[ROOT/'python/lutlab'/name for name in
        ('channel_coordinates.py', 'axis_calibration.py', 'exact_axis.py', 'monotone_axis.py', 'interp.py', 'io.py', 'study_provenance.py')]]
    sources = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files: archive.write(path, path.relative_to(ROOT).as_posix())
    result = {'pass': True, 'purpose': '复制等价/分通道独立u64前向；9种channel/axis的65537事件、单调DP、cap和只更新一个输出缓存',
        'environment': study_provenance.environment_fingerprint(), 'numba_threads': numba.get_num_threads(), 'seed': 2026101914,
        'copy_equivalence_points': len(check), 'distinct_coordinate_oracle_points': len(check),
        'grid_sizes_checked': [17, 33],
        'cases': records, 'source_sha256': sources, 'scope': '集中合成合同，不是新表示的真实LUT精度/百图/native/性能验收'}
    (args.output/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__': main()
