"""集中合同：分通道几何、非线性后缀的26方向联合cost/cap与fresh缓存。"""
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
import numpy as np
from lutlab import channel_coordinates as cc, channel_global_nodes as cg, channel_joint_nodes as cj
from lutlab import channel_suffix_coordinates as cs, channel_suffix_joint_nodes as sj, io, study_provenance
from verify_channel_coordinates import integer_oracle


def actual(model, points, targets, terminal, reference, suffix, mass, rho):
    """独立u64首级；显式两标签loss与独立reference cap，不调用ac._cost。"""
    prediction = integer_oracle(model, points)
    own = cg.squared_error(prediction, targets)
    final = suffix[prediction.astype(np.int64)@np.array([65536, 256, 1], np.int64)]
    transformed = cg.squared_error(final, terminal)
    cap_d2 = cg.squared_error(final, reference)
    return float(mass@(rho[own]+rho[transformed])), prediction, own, cap_d2


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): raise ValueError('不覆盖集中合同')
    numba.set_num_threads(4)
    rng = np.random.default_rng(2026101929)
    suffix = np.empty((256**3, 3), np.uint8)
    for start in range(0, len(suffix), 1 << 18):
        key = np.arange(start, min(start+(1 << 18), len(suffix)), dtype=np.int32)
        r, g, b = key >> 16, (key >> 8) & 255, key & 255
        suffix[start:start+len(key), 0] = (r+2*g+b//7) % 256
        suffix[start:start+len(key), 1] = g ^ b
        suffix[start:start+len(key), 2] = np.minimum(255, (r*g+127)//255+b//2)
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64)); rho = root+.02*np.maximum(root-6., 0.)**2
    cases = []
    for m in (17, 33):
        grid = np.tile(np.linspace(0, 255, m), (3, 1))
        sparse = io.SparseLut(grid, rng.integers(110, 145, (m, m, m, 3), dtype=np.uint8))
        sparse.nodes[0, 0, 0] = [0, 255, 0]; sparse.nodes[-1, -1, -1] = [255, 0, 255]
        model = cc.from_sparse(sparse)
        for c in range(3):
            for axis in range(3):
                model.channel_frac[c, axis] = np.clip(model.channel_frac[c, axis].astype(np.int64)
                    +(c-1)*1999+(axis-1)*317, 0, io.ONE)
                model.channel_frac[c, axis, [0, 255]] = [0, io.ONE]
        cc.validate(model)
        points = rng.integers(0, 256, (25, 3), dtype=np.uint8)
        points[:8] = np.array(np.meshgrid(*[[0, 255]]*3, indexing='ij')).reshape(3, -1).T
        original = integer_oracle(model, points)
        targets = original.copy()
        targets[8:] = np.clip(targets[8:].astype(np.int32)+rng.integers(-3, 4, targets[8:].shape), 0, 255).astype(np.uint8)
        terminal = suffix[targets.astype(np.int64)@np.array([65536, 256, 1], np.int64)]
        reference = suffix[original.astype(np.int64)@np.array([65536, 256, 1], np.int64)]
        mass = rng.random(len(points)); mass[:8] = 0; mass /= mass.sum()
        caps = rng.integers(0, 20, len(points), dtype=np.int32); caps[:8] = 0
        indices, weights = cg.design(model, points)
        nodes = model.nodes.reshape(-1, 3).copy()
        acc, squared = cj.accumulate(indices, weights, nodes, targets)
        colours = cj.parity(m)
        maximum, checks, illegal, prohibitions, zero_mass = 0., 0, 0, 0, 0
        for colour in range(8):
            current = cc.ChannelLut(model.grid, nodes.reshape(model.nodes.shape), model.idx, model.channel_frac)
            before, output, own, cap_d2 = actual(current, points, targets, terminal, reference, suffix, mass, rho)
            measured, bad = cs.measure(output, targets, terminal, reference, caps, suffix, mass, rho, 4)
            assert abs(measured-before) < 1e-10 and not bad
            changes, forbidden, invalid = sj.gains(indices, weights, acc, squared, targets, terminal, reference,
                caps, suffix, mass, nodes, colours, colour, rho, 4)
            assert not invalid
            supported = np.unique(indices[(weights > 0) & (colours[indices] == colour)])
            for node in supported:
                for direction, delta in enumerate(sj.DIRECTIONS):
                    value = nodes[node].astype(np.int32)+delta
                    if value.min() < 0 or value.max() > 255:
                        assert np.isinf(changes[direction, node]) and forbidden[direction, node] > 0
                        illegal += 1; continue
                    trial_nodes = nodes.copy(); trial_nodes[node] = value.astype(np.uint8)
                    trial = cc.ChannelLut(model.grid, trial_nodes.reshape(model.nodes.shape), model.idx, model.channel_frac)
                    loss, _, _, final_d2 = actual(trial, points, targets, terminal, reference, suffix, mass, rho)
                    maximum = max(maximum, abs(loss-before-changes[direction, node]))
                    assert abs(loss-before-changes[direction, node]) < 1e-10
                    assert forbidden[direction, node] == np.count_nonzero(final_d2 > caps)
                    checks += 1; prohibitions += int(forbidden[direction, node] > 0)
                    zero_mass += int(np.any((mass == 0) & (final_d2 > caps)))
            moves, predicted, _, _ = cj.select(changes, forbidden, colours, colour)
            cj.apply(indices, weights, acc, squared, targets, moves)
            nodes = (nodes.astype(np.int32)+moves).astype(np.uint8)
            current = cc.ChannelLut(model.grid, nodes.reshape(model.nodes.shape), model.idx, model.channel_frac)
            loss, independent, own, cap_d2 = actual(current, points, targets, terminal, reference, suffix, mass, rho)
            np.testing.assert_array_equal(((acc+io.ONE//2) >> io.Q).astype(np.uint8), independent)
            np.testing.assert_array_equal(squared, own)
            assert not np.any(cap_d2 > caps) and abs(loss-before-predicted) < 1e-10
        fresh_acc, fresh_squared = cj.accumulate(indices, weights, nodes, targets)
        np.testing.assert_array_equal(fresh_acc, acc); np.testing.assert_array_equal(fresh_squared, squared)
        np.testing.assert_array_equal(cc.predict(current, points), integer_oracle(current, points))
        assert illegal and prohibitions and zero_mass
        cases.append({'m': m, 'points': len(points), 'groups': 8,
            'all_positive_support_node_26_directions_checked': checks, 'illegal_rgb8_directions_checked': illegal,
            'nonzero_cap_prohibitions': prohibitions, 'zero_mass_cap_prohibitions': zero_mass,
            'maximum_gain_error': maximum, 'geometry_errors': 0, 'cap_count_mismatches': 0,
            'uint64_output_mismatches': 0, 'fresh_cache_mismatches': 0})
    files = [Path(__file__), ROOT/'scripts/verify_channel_coordinates.py', *[ROOT/'python/lutlab'/n for n in
        ('channel_suffix_joint_nodes.py', 'channel_joint_nodes.py', 'channel_global_nodes.py', 'channel_suffix_coordinates.py',
         'channel_coordinates.py', 'axis_calibration.py', 'exact_axis.py', 'monotone_axis.py', 'interp.py', 'io.py', 'study_provenance.py')]]
    sources = {f.relative_to(ROOT).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    args.output.mkdir(parents=True)
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for f in files: archive.write(f, f.relative_to(ROOT).as_posix())
    result = {'pass': True, 'purpose': __doc__, 'seed': 2026101929,
        'environment': study_provenance.environment_fingerprint(), 'numba_threads': 4, 'cases': cases,
        'source_sha256': sources, 'scope': '一次合成小合同，独立u64+非线性suffix oracle，不是实际完整四级精度或性能验收'}
    (args.output/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__': main()
