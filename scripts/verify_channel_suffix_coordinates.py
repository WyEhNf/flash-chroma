"""一次集中合同：分输出单轴65537状态、非线性耦合后缀、独立u64及单调缓存。"""
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
from lutlab import channel_coordinates as cc, channel_suffix_coordinates as cs, io, monotone_axis, study_provenance
from verify_channel_coordinates import integer_oracle


@njit(cache=False)
def scalar_oracle(nodes, idx, frac, m, r, g, b, channel, axis, f):
    """独立六分支、uint64四权重；不调用事件line或原像素排序核。"""
    x = f if axis == 0 else np.int64(frac[channel, 0, r])
    y = f if axis == 1 else np.int64(frac[channel, 1, g])
    z = f if axis == 2 else np.int64(frac[channel, 2, b])
    base = (np.int64(idx[0, r])*m+np.int64(idx[1, g]))*m+np.int64(idx[2, b])
    sr, sg, sb = m*m, m, 1
    if x >= y:
        if y >= z: first, second, high, middle, low = sr, sg, x, y, z
        elif x >= z: first, second, high, middle, low = sr, sb, x, z, y
        else: first, second, high, middle, low = sb, sr, z, x, y
    else:
        if x >= z: first, second, high, middle, low = sg, sr, y, x, z
        elif y >= z: first, second, high, middle, low = sg, sb, y, z, x
        else: first, second, high, middle, low = sb, sg, z, y, x
    acc = (np.uint64(io.ONE-high)*np.uint64(nodes[base, channel])
        +np.uint64(high-middle)*np.uint64(nodes[base+first, channel])
        +np.uint64(middle-low)*np.uint64(nodes[base+first+second, channel])
        +np.uint64(low)*np.uint64(nodes[base+sr+sg+sb, channel]))
    return np.int64((acc+np.uint64(io.ONE//2)) >> np.uint64(io.Q))


@njit(cache=False)
def brute(points, nodes, idx, frac, m, targets, terminal, reference, caps, suffix, mass, rho, output, channel, axis):
    losses, bad = np.zeros(io.ONE+1), np.zeros(io.ONE+1, np.int64)
    for f in range(io.ONE+1):
        for p in range(len(points)):
            rgb = np.empty(3, np.int64)
            for c in range(3): rgb[c] = np.int64(output[p, c])
            rgb[channel] = scalar_oracle(nodes, idx, frac, m, int(points[p, 0]), int(points[p, 1]), int(points[p, 2]), channel, axis, f)
            own, transformed, d2 = 0, 0, 0
            key = (rgb[0] << 16) | (rgb[1] << 8) | rgb[2]
            for c in range(3):
                e = rgb[c]-np.int64(targets[p, c]); own += e*e
                e = np.int64(suffix[key, c])-np.int64(terminal[p, c]); transformed += e*e
                e = np.int64(suffix[key, c])-np.int64(reference[p, c]); d2 += e*e
            losses[f] += mass[p]*(rho[own]+rho[transformed])
            bad[f] += int(d2 > caps[p])
    return losses, bad


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): raise ValueError('不覆盖集中合同')
    numba.set_num_threads(4)
    rng = np.random.default_rng(2026101927)
    suffix = np.empty((256**3, 3), np.uint8)
    for start in range(0, len(suffix), 1 << 18):
        key = np.arange(start, min(start+(1 << 18), len(suffix)), dtype=np.int32)
        r, g, b = key >> 16, (key >> 8) & 255, key & 255
        suffix[start:start+len(key), 0] = (r+2*g+b//7) % 256
        suffix[start:start+len(key), 1] = g ^ b
        suffix[start:start+len(key), 2] = np.minimum(255, (r*g+127)//255+b//2)
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64)); rho = root+.02*np.maximum(root-6., 0.)**2
    cases, forward = [], []
    for m in (17, 33):
        grid = np.tile(np.linspace(0, 255, m), (3, 1))
        model = cc.from_sparse(io.SparseLut(grid, rng.integers(90, 166, (m, m, m, 3), dtype=np.uint8)))
        for c in range(3):
            for axis in range(3):
                model.channel_frac[c, axis] = np.clip(model.channel_frac[c, axis].astype(np.int64)
                    +(c-1)*1739+(axis-1)*257, 0, io.ONE)
                model.channel_frac[c, axis, [0, 255]] = [0, io.ONE]
        cc.validate(model)
        check = rng.integers(0, 256, (1033, 3), dtype=np.uint8)
        np.testing.assert_array_equal(cc.predict(model, check), integer_oracle(model, check))
        nodes, frac = model.nodes.reshape(-1, 3), model.channel_frac.astype(np.int64)
        for channel in range(3):
            for axis in range(3):
                points = rng.integers(0, 256, (9, 3), dtype=np.uint8); points[:, axis] = 128
                output = integer_oracle(model, points)
                targets = rng.integers(110, 145, points.shape, dtype=np.uint8)
                terminal = suffix[targets.astype(np.int64)@np.array([65536, 256, 1])]
                reference = suffix[output.astype(np.int64)@np.array([65536, 256, 1])]
                caps = rng.integers(0, 20, len(points), dtype=np.int32); caps[:2] = 0
                mass = rng.random(len(points)); mass[:2] = 0; mass /= mass.sum()
                order = np.argsort(points[:, axis], kind='stable').astype(np.int64)
                offsets = np.r_[0, np.cumsum(np.bincount(points[:, axis], minlength=256))].astype(np.int64)
                diff, bdiff, baseline, count, invalid = cs.events(points, nodes, model.idx, frac, m, targets,
                    terminal, reference, caps, suffix, mass, rho, output, channel, axis, order, offsets)
                assert not np.any(invalid)
                costs, violations = np.cumsum(diff, axis=1), np.cumsum(bdiff, axis=1)
                del diff, bdiff
                expected_loss, expected_bad = brute(points, nodes, model.idx, frac, m, targets, terminal,
                    reference, caps, suffix, mass, rho, output, channel, axis)
                maximum = float(np.max(np.abs(costs[128]-expected_loss)))
                assert maximum < 1e-8 and np.array_equal(violations[128], expected_bad)
                assert expected_bad.max() > 0
                old = frac[channel, axis].copy()
                np.testing.assert_allclose(costs[np.arange(256), old], baseline, rtol=0, atol=1e-8)
                measured, bad = cs.measure(output, targets, terminal, reference, caps, suffix, mass, rho, 4)
                assert not bad and abs(float(baseline.sum())-measured) < 1e-8
                selected, predicted = monotone_axis.choose_axis(costs, violations, model.idx[axis], old)
                del costs, violations
                trial_frac = frac.copy(); trial_frac[channel, axis] = selected
                assert np.all(np.diff(model.idx[axis].astype(np.int64)*io.ONE+selected) >= 0)
                np.testing.assert_array_equal(selected[[0, 255]], old[[0, 255]])
                error = output.astype(np.int32)-targets.astype(np.int32)
                squared = np.sum(error*error, axis=1, dtype=np.int32)
                cached = output.copy()
                cc._refresh(points, nodes, model.idx, trial_frac, m, targets, cached, squared, channel)
                trial = cc.ChannelLut(model.grid, model.nodes, model.idx, trial_frac.astype(np.uint32))
                independent = integer_oracle(trial, points)
                np.testing.assert_array_equal(cached, independent)
                np.testing.assert_array_equal(cached[:, [c for c in range(3) if c != channel]], output[:, [c for c in range(3) if c != channel]])
                e = independent.astype(np.int32)-targets.astype(np.int32)
                np.testing.assert_array_equal(squared, np.sum(e*e, axis=1, dtype=np.int32))
                applied, bad = cs.measure(cached, targets, terminal, reference, caps, suffix, mass, rho, 4)
                assert not bad and abs(applied-predicted) < 1e-8
                for f in (0, 1, 16384, 32768, 65535, 65536):
                    changed = frac.copy(); changed[channel, axis, 128] = f
                    wrapped = cc.ChannelLut(model.grid, model.nodes, model.idx, changed.astype(np.uint32))
                    actual = integer_oracle(wrapped, points)
                    for p, rgb in enumerate(points):
                        assert actual[p, channel] == scalar_oracle(nodes, model.idx, frac, m,
                            int(rgb[0]), int(rgb[1]), int(rgb[2]), channel, axis, f)
                cases.append({'m': m, 'channel': channel, 'axis': axis, 'points': len(points),
                    'integer_states': io.ONE+1, 'maximum_event_loss_error': maximum,
                    'cap_count_mismatches': 0, 'uint64_output_mismatches': 0,
                    'other_channel_cache_mismatches': 0, 'fresh_cache_mismatches': 0,
                    'dp_monotone_endpoints_and_cap_pass': True, 'events': int(count.sum())})
        forward.append({'m': m, 'points': len(check), 'independent_uint64_mismatches': 0})
    files = [Path(__file__), ROOT/'scripts/verify_channel_coordinates.py', *[ROOT/'python/lutlab'/name for name in
        ('channel_suffix_coordinates.py', 'channel_coordinates.py', 'axis_calibration.py', 'exact_axis.py',
         'monotone_axis.py', 'io.py', 'study_provenance.py')]]
    sources = {f.relative_to(ROOT).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    args.output.mkdir(parents=True)
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for f in files: archive.write(f, f.relative_to(ROOT).as_posix())
    result = {'pass': True, 'purpose': __doc__, 'seed': 2026101927,
        'environment': study_provenance.environment_fingerprint(), 'numba_threads': 4,
        'suffix': '固定非线性跨通道耦合RGB8查表，T1与S(T1)标签和单独reference区分',
        'cases': cases, 'forward': forward, 'source_sha256': sources,
        'scope': '一次集中合成合同，非实际四级LUT精度、全域输出/照片或性能验收'}
    (args.output/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__': main()
