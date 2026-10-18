"""一次集中合同：不同通道几何下块联合收益/cap、完整缓存与独立整数oracle。"""
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
from lutlab import channel_blocks as cb, channel_coordinates as cc, io, study_provenance
from verify_channel_coordinates import integer_oracle


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args(); args.output = args.output.resolve()
    if args.output.exists(): raise ValueError('不覆盖合同')
    numba.set_num_threads(4)
    rng = np.random.default_rng(2026101921)
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64)); rho = root+.02*np.maximum(root-6., 0.)**2
    cases = []
    for m in (17, 33):
        grid = np.tile(np.linspace(0, 255, m), (3, 1))
        original = io.SparseLut(grid, rng.integers(0, 256, (m, m, m, 3), dtype=np.uint8))
        original.nodes[0, 0, 0] = 0; original.nodes[-1, -1, -1] = 255
        model = cc.from_sparse(original)
        for c in range(3):
            model.channel_frac[c, :, 1:255] = np.clip(model.channel_frac[c, :, 1:255].astype(np.int64)+(c-1)*137, 0, io.ONE)
        cc.validate(model)
        points = rng.integers(0, 256, (64, 3), dtype=np.uint8)
        points[:8] = np.array(np.meshgrid(*[[0, 255]]*3, indexing='ij')).reshape(3, -1).T
        truth = rng.integers(0, 256, points.shape, dtype=np.uint8)
        output = integer_oracle(model, points)
        error = output.astype(np.int32)-truth.astype(np.int32)
        squared = np.sum(error*error, axis=1, dtype=np.int32)
        caps = squared+rng.integers(0, 3, len(points), dtype=np.int32)
        mass = rng.random(len(points)); mass[:8] = 0; mass /= mass.sum()
        blocks, colours, count = cb.layout(m)
        nodes = model.nodes.reshape(-1, 3)
        for channel in range(3):
            indices, weights = cb.design(model, points, channel)
            acc = cb.accumulate(indices, weights, nodes[:, channel])
            np.testing.assert_array_equal(((acc+32768) >> 16).astype(np.uint8), output[:, channel])
            max_error = 0.; directions = 0; forbidden_directions = 0; zero_mass_cap = 0
            for colour in range(8):
                gains, forbidden, invalid = cb.gains(indices, weights, acc, squared, truth[:, channel], mass,
                    caps, blocks, colours, colour, count, rho, 4)
                assert not invalid
                touched = np.unique(blocks[indices[(weights > 0) & (colours[indices] == colour)]])
                for b in touched:
                    members = blocks == b
                    for direction, sign in enumerate((1, -1)):
                        values = nodes[:, channel].astype(np.int32)+members.astype(np.int32)*sign
                        if values.min() < 0 or values.max() > 255: continue
                        trial = cc.ChannelLut(model.grid, model.nodes.copy(), model.idx, model.channel_frac)
                        trial.nodes.reshape(-1, 3)[:, channel] = values.astype(np.uint8)
                        actual = integer_oracle(trial, points)
                        e = actual.astype(np.int32)-truth.astype(np.int32)
                        d2 = np.sum(e*e, axis=1, dtype=np.int32)
                        expected_gain = float(mass@(rho[d2]-rho[squared]))
                        max_error = max(max_error, abs(expected_gain-gains[direction, b]))
                        expected_bad = int(np.count_nonzero(d2 > caps))
                        assert int(forbidden[direction, b]) == expected_bad
                        directions += 1; forbidden_directions += int(expected_bad > 0)
                        zero_mass_cap += int(np.any((mass == 0) & (d2 > caps)))
                move, predicted, selected = cb.select(gains, forbidden, nodes[:, channel], blocks, colours, colour, count)
                trial_acc, trial_d2 = acc.copy(), squared.copy()
                cb.apply(indices, weights, trial_acc, trial_d2, truth[:, channel], move, blocks)
                trial = cc.ChannelLut(model.grid, model.nodes.copy(), model.idx, model.channel_frac)
                trial.nodes.reshape(-1, 3)[:, channel] = (nodes[:, channel].astype(np.int32)+move[blocks]).astype(np.uint8)
                actual = integer_oracle(trial, points)
                np.testing.assert_array_equal(((trial_acc+32768) >> 16).astype(np.uint8), actual[:, channel])
                np.testing.assert_array_equal(actual[:, [c for c in range(3) if c != channel]], output[:, [c for c in range(3) if c != channel]])
                e = actual.astype(np.int32)-truth.astype(np.int32)
                np.testing.assert_array_equal(trial_d2, np.sum(e*e, axis=1, dtype=np.int32))
                assert not np.any(trial_d2 > caps)
                assert abs(float(mass@(rho[trial_d2]-rho[squared]))-predicted) < 1e-10
            assert max_error < 1e-10 and forbidden_directions > 0
            cases.append({'m': m, 'channel': channel, 'points': len(points), 'legal_directions_checked': directions,
                          'forbidden_directions': forbidden_directions, 'zero_mass_cap_directions': zero_mass_cap,
                          'maximum_gain_error': max_error, 'integer_oracle_mismatches': 0, 'cap_count_mismatches': 0})
        candidate, report = cb.propose(model, points, truth, mass, caps=caps, parts=4)
        np.testing.assert_array_equal(cc.predict(candidate, points), integer_oracle(candidate, points))
        assert len(report['groups']) == 24 and report['cache_recompute_mismatches'] == 0
        assert report['training_cap_violations'] == 0
    # 真实四面体四个正权重顶点均为1/4：单节点+1不改变输出，整块+1才跨舍入台阶。
    m = 17; blocks, colours, count = cb.layout(m)
    indices = np.array([[0, 1, m+1, m*m+m+1]], np.int32)
    weights = np.full((1, 4), 16384, np.int32); acc = np.array([100*65536], np.int32)
    gains, bad, invalid = cb.gains(indices, weights, acc, np.array([1], np.int32), np.array([101], np.uint8),
        np.ones(1), np.array([4], np.int32), blocks, colours, 0, count, rho, 4)
    assert gains[0, 0] == -1 and not bad[0, 0] and not invalid
    assert all((100*65536+int(w)+32768) >> 16 == 100 for w in weights[0])
    files = [Path(__file__), ROOT/'scripts/verify_channel_coordinates.py', *[ROOT/'python/lutlab'/n for n in
        ('channel_blocks.py', 'channel_coordinates.py', 'interp.py', 'io.py', 'study_provenance.py')]]
    args.output.mkdir(parents=True)
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for f in files: z.write(f, f.relative_to(ROOT).as_posix())
    result = {'pass': True, 'purpose': __doc__, 'environment': study_provenance.environment_fingerprint(), 'numba_threads': 4,
              'seed': 2026101921, 'cases': cases, 'full_24_block_cache_runs': [17, 33],
              'coherent_step_crosses_single_node_plateau': True,
              'source_sha256': {f.relative_to(ROOT).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest() for f in files},
              'limits': '合成整数合同，不是实际LUT精度、全色域验收或性能；没有证明任意块全局最优'}
    (args.output/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__': main()
