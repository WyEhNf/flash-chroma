"""集中合成合同：分通道几何的节点±1收益/cap及24块缓存，不测真实精度。"""
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
from lutlab import channel_coordinates as cc, channel_nodes as cn, io, study_provenance
from verify_channel_coordinates import integer_oracle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): raise ValueError('不覆盖旧合同')
    args.output.mkdir(parents=True)
    numba.set_num_threads(4)
    rng = np.random.default_rng(2026101918)
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    rho = root+.02*np.maximum(root-6., 0.)**2
    records = []
    for m in (17, 33):
        grid = np.tile(np.linspace(0, 255, m), (3, 1))
        sparse = io.SparseLut(grid, rng.integers(0, 256, (m, m, m, 3), dtype=np.uint8))
        model = cc.from_sparse(sparse)
        model.nodes[0, 0, 0] = [0, 255, 0]
        model.nodes[-1, -1, -1] = [255, 0, 255]
        for c in range(3):
            for axis in range(3):
                model.channel_frac[c, axis] = np.clip(model.channel_frac[c, axis].astype(np.int64)
                    +(c-1)*1537+(axis-1)*401, 0, io.ONE)
                model.channel_frac[c, axis, [0, 255]] = [0, io.ONE]
        cc.validate(model)
        points = rng.integers(0, 256, (521, 3), dtype=np.uint8)
        points[:8] = np.array(np.meshgrid(*[[0, 255]]*3, indexing='ij')).reshape(3, -1).T
        output = integer_oracle(model, points)
        np.testing.assert_array_equal(output, cc.predict(model, points))
        targets = np.clip(output.astype(np.int32)+rng.integers(-3, 4, output.shape), 0, 255).astype(np.uint8)
        mass = rng.random(len(points)); mass[:9] = 0.; mass /= mass.sum()
        e = output.astype(np.int32)-targets.astype(np.int32)
        squared = np.sum(e*e, axis=1, dtype=np.int32)
        caps = squared+rng.integers(0, 5, len(points), dtype=np.int32)
        caps[:9] = squared[:9]
        colours = cn.parity(m)
        nodes = model.nodes.reshape(-1, 3).copy()
        maximum, checked_moves, blocked, zero_weights = 0., 0, 0, 0
        for channel in range(3):
            indices, weights = cn.design(model, points, channel)
            zero_weights += int(np.count_nonzero(weights == 0))
            acc = cn.accumulate(indices, weights, nodes, channel)
            np.testing.assert_array_equal((acc+io.ONE//2) >> io.Q, output[:, channel])
            for colour in range(8):
                for row in range(len(points)):
                    assert np.count_nonzero((weights[row] > 0) & (colours[indices[row]] == colour)) <= 1
                costs, bad = cn.gains(indices, weights, acc, output, squared, targets, mass, caps,
                    nodes, colours, colour, channel, rho, 4)
                support = np.unique(indices[(weights > 0) & (colours[indices] == colour)])
                chosen = np.unique(np.r_[support[:12], np.flatnonzero((colours == colour)
                    & ((nodes[:, channel] == 0) | (nodes[:, channel] == 255)))[:3]])
                before = float(mass@rho[squared])
                for node in chosen:
                    for direction, delta in enumerate((1, -1)):
                        if not 0 <= int(nodes[node, channel])+delta <= 255: continue
                        trial_nodes = nodes.copy(); trial_nodes[node, channel] = int(nodes[node, channel])+delta
                        trial = cc.ChannelLut(model.grid, trial_nodes.reshape(model.nodes.shape), model.idx, model.channel_frac)
                        independent = integer_oracle(trial, points)
                        error = independent.astype(np.int32)-targets.astype(np.int32)
                        d2 = np.sum(error*error, axis=1, dtype=np.int32)
                        expected = float(mass@rho[d2])-before
                        maximum = max(maximum, abs(costs[direction, node]-expected))
                        assert abs(costs[direction, node]-expected) < 1e-12
                        assert bad[direction, node] == np.count_nonzero(d2 > caps)
                        blocked += int(bad[direction, node] > 0)
                        checked_moves += 1
                move, predicted = cn.choose(costs, bad, nodes, colours, colour, channel)
                assert not np.any((nodes[:, channel] == 255) & (move > 0))
                assert not np.any((nodes[:, channel] == 0) & (move < 0))
                other = output[:, [c for c in range(3) if c != channel]].copy()
                cn.apply(indices, weights, acc, output, squared, targets, colours, colour, channel, move)
                nodes[:, channel] = (nodes[:, channel].astype(np.int32)+move).astype(np.uint8)
                current = cc.ChannelLut(model.grid, nodes.reshape(model.nodes.shape), model.idx, model.channel_frac)
                independent = integer_oracle(current, points)
                np.testing.assert_array_equal(output, independent)
                np.testing.assert_array_equal(output[:, [c for c in range(3) if c != channel]], other)
                error = independent.astype(np.int32)-targets.astype(np.int32)
                np.testing.assert_array_equal(squared, np.sum(error*error, axis=1, dtype=np.int32))
                np.testing.assert_array_equal((acc+io.ONE//2) >> io.Q, output[:, channel])
                assert not np.any(squared > caps)
                assert abs(float(mass@rho[squared])-before-predicted) < 1e-12
        candidate, report = cn.propose(model, points, targets, mass, caps=caps)
        np.testing.assert_array_equal(candidate.nodes.reshape(-1, 3), nodes)
        np.testing.assert_array_equal(candidate.channel_frac, model.channel_frac)
        np.testing.assert_array_equal(candidate.idx, model.idx)
        np.testing.assert_array_equal(candidate.grid, model.grid)
        assert len(report['blocks']) == 24 and blocked and zero_weights
        records.append({'m': m, 'points': len(points), 'blocks': 24, 'independent_moves': checked_moves,
            'maximum_gain_error': maximum, 'nonzero_cap_prohibitions': blocked, 'zero_weights': zero_weights,
            'integer_output_mismatches': 0, 'cap_count_mismatches': 0, 'other_channel_cache_mismatches': 0,
            'fresh_cache_mismatches': 0, 'endpoints_0_255_and_zero_mass_checked': True})
    files = [Path(__file__), ROOT/'scripts/verify_channel_coordinates.py',
        *[ROOT/'python/lutlab'/name for name in ('channel_nodes.py', 'channel_coordinates.py', 'interp.py', 'io.py', 'study_provenance.py')]]
    sources = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files: archive.write(path, path.relative_to(ROOT).as_posix())
    result = {'pass': True, 'purpose': '一次集中小型独立u64节点±1收益/逐色cap/同色互斥/三输出不同几何/24块及fresh缓存合同',
        'environment': study_provenance.environment_fingerprint(), 'numba_threads': numba.get_num_threads(),
        'seed': 2026101918, 'cases': records, 'source_sha256': sources,
        'scope': '固定合成合同，不是Velvia真实精度、全域输出/百图、原生或性能验收'}
    (args.output/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__': main()
