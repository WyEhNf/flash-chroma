"""集中核对分通道几何的26方向联合收益/cap、共享角及fresh整数缓存。"""
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
from lutlab import channel_coordinates as cc, channel_global_nodes as cg, channel_joint_nodes as cj, io, study_provenance
from verify_channel_coordinates import integer_oracle


def actual(model, points, targets, mass, rho):
    output = integer_oracle(model, points)
    squared = cg.squared_error(output, targets)
    return float(mass@rho[squared]), output, squared


def counterexample(rho):
    axis = np.r_[np.arange(0, 256, 16), 255].astype(np.float64)
    model = cc.from_sparse(io.SparseLut(np.tile(axis, (3, 1)), np.full((17, 17, 17, 3), 10, np.uint8)))
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], np.uint8)
    targets = np.array([[11, 11, 10], [9, 10, 10], [10, 9, 10]], np.uint8)
    mass, caps = np.array([.5, .25, .25]), np.full(3, 49, np.int32)
    indices, weights = cg.design(model, points)
    acc, squared = cj.accumulate(indices, weights, model.nodes.reshape(-1, 3), targets)
    change, forbidden, invalid = cj.gains(indices, weights, acc, squared, targets, mass, caps,
        model.nodes.reshape(-1, 3), cj.parity(17), 0, rho, 4)
    singles = np.count_nonzero(cj.DIRECTIONS, axis=1) == 1
    joint = int(np.flatnonzero(np.all(cj.DIRECTIONS == (1, 1, 0), axis=1))[0])
    assert not invalid and np.all(change[singles, 0] > 0) and change[joint, 0] < -.08 and not forbidden[joint, 0]
    moves, predicted, count, joint_count = cj.select(change, forbidden, cj.parity(17), 0)
    np.testing.assert_array_equal(moves[0], [1, 1, 0])
    trial = cc.ChannelLut(model.grid, (model.nodes.reshape(-1, 3).astype(np.int32)+moves).astype(np.uint8).reshape(model.nodes.shape), model.idx, model.channel_frac)
    before, _, _ = actual(model, points, targets, mass, rho)
    after, _, _ = actual(trial, points, targets, mass, rho)
    assert count == joint_count == 1 and abs(after-before-predicted) < 1e-12
    return {'six_single_changes': change[singles, 0].tolist(), 'joint_change': float(change[joint, 0]),
        'independent_uint64_gain_error': abs(after-before-predicted)}


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖集中合同')
    numba.set_num_threads(4)
    rng = np.random.default_rng(2026101925)
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64)); rho = root+.02*np.maximum(root-6., 0.)**2
    records = []
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
        original_output = integer_oracle(model, points)
        targets = original_output.copy()
        targets[8:] = np.clip(targets[8:].astype(np.int32)+rng.integers(-3, 4, targets[8:].shape), 0, 255).astype(np.uint8)
        mass = rng.random(len(points)); mass[:8] = 0; mass /= mass.sum()
        indices, weights = cg.design(model, points)
        nodes = model.nodes.reshape(-1, 3).copy()
        acc, squared = cj.accumulate(indices, weights, nodes, targets)
        np.testing.assert_array_equal(((acc+io.ONE//2) >> io.Q).astype(np.uint8), original_output)
        caps = squared+rng.integers(0, 4, len(points), dtype=np.int32); caps[:8] = squared[:8]
        colours = cj.parity(m)
        # 验证全部cell的8角parity互异；三个四面体都是这些角的子集。
        xyz = np.indices((m-1,)*3).reshape(3, -1).T
        base = (xyz[:, 0]*m+xyz[:, 1])*m+xyz[:, 2]
        offsets = np.array([a*m*m+b*m+c for a in (0, 1) for b in (0, 1) for c in (0, 1)])
        np.testing.assert_array_equal(np.sort(colours[base[:, None]+offsets], axis=1), np.tile(np.arange(8), (len(base), 1)))
        maximum, checks, illegal, bad_directions, zero_mass_bad = 0., 0, 0, 0, 0
        for colour in range(8):
            before = float(mass@rho[squared])
            changes, forbidden, invalid = cj.gains(indices, weights, acc, squared, targets, mass, caps,
                nodes, colours, colour, rho, 4)
            assert not invalid
            supported = np.unique(indices[(weights > 0) & (colours[indices] == colour)])
            for node in supported:
                for direction, delta in enumerate(cj.DIRECTIONS):
                    values = nodes[node].astype(np.int32)+delta
                    if values.min() < 0 or values.max() > 255:
                        assert np.isinf(changes[direction, node]) and forbidden[direction, node] > 0
                        illegal += 1; continue
                    trial_nodes = nodes.copy(); trial_nodes[node] = values.astype(np.uint8)
                    trial = cc.ChannelLut(model.grid, trial_nodes.reshape(model.nodes.shape), model.idx, model.channel_frac)
                    loss, _, expected_squared = actual(trial, points, targets, mass, rho)
                    maximum = max(maximum, abs(loss-before-changes[direction, node]))
                    assert abs(loss-before-changes[direction, node]) < 1e-12
                    assert forbidden[direction, node] == np.count_nonzero(expected_squared > caps)
                    bad_directions += int(forbidden[direction, node] > 0)
                    zero_mass_bad += int(np.any((mass == 0) & (expected_squared > caps)))
                    checks += 1
            moves, predicted, _, _ = cj.select(changes, forbidden, colours, colour)
            cj.apply(indices, weights, acc, squared, targets, moves)
            nodes = (nodes.astype(np.int32)+moves).astype(np.uint8)
            current = cc.ChannelLut(model.grid, nodes.reshape(model.nodes.shape), model.idx, model.channel_frac)
            loss, independent, independent_squared = actual(current, points, targets, mass, rho)
            np.testing.assert_array_equal(((acc+io.ONE//2) >> io.Q).astype(np.uint8), independent)
            np.testing.assert_array_equal(squared, independent_squared)
            assert not np.any(squared > caps) and abs(loss-before-predicted) < 1e-12
        candidate, report = cj.propose(model, points, targets, mass, caps=caps)
        np.testing.assert_array_equal(candidate.nodes.reshape(-1, 3), nodes)
        np.testing.assert_array_equal(candidate.channel_frac, model.channel_frac)
        np.testing.assert_array_equal(candidate.idx, model.idx)
        np.testing.assert_array_equal(cc.predict(candidate, points), integer_oracle(candidate, points))
        assert bad_directions and zero_mass_bad and illegal and len(report['groups']) == 8
        records.append({'m': m, 'points': len(points), 'all_cells_checked': len(base),
            'all_positive_support_node_26_directions_checked': checks, 'illegal_rgb8_directions_checked': illegal,
            'nonzero_cap_prohibitions': bad_directions, 'zero_mass_cap_prohibitions': zero_mass_bad,
            'maximum_gain_error': maximum, 'geometry_errors': 0, 'cap_count_mismatches': 0,
            'uint64_output_mismatches': 0, 'fresh_cache_mismatches': 0, 'groups': 8})
    example = counterexample(rho)
    files = [Path(__file__), ROOT/'scripts/verify_channel_coordinates.py', *[ROOT/'python/lutlab'/name for name in
        ('channel_joint_nodes.py', 'channel_global_nodes.py', 'channel_coordinates.py', 'interp.py', 'io.py', 'study_provenance.py')]]
    sources = {f.relative_to(ROOT).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    args.output.mkdir(parents=True)
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for f in files: archive.write(f, f.relative_to(ROOT).as_posix())
    result = {'pass': True, 'purpose': __doc__, 'seed': 2026101925,
        'environment': study_provenance.environment_fingerprint(), 'numba_threads': 4,
        'cases': records, 'joint_counterexample': example, 'source_sha256': sources,
        'scope': '一次小型集中合同，覆盖全部实际正支撑节点26方向；不是完整RGB精度或性能验收'}
    (args.output/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__': main()
