"""集中合同：不同输出几何的全局梯度、量化整数前向和硬cap只撤销恢复。"""
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
from lutlab import channel_coordinates as cc, channel_global_nodes as cg, io, study_provenance
from verify_channel_coordinates import integer_oracle


def objective_oracle(model, nodes, points, targets, mass):
    """独立逐像素排序/浮点节点累加，不借用设计或梯度核。"""
    value = 0.
    m = model.m
    for p, rgb in enumerate(points):
        error = []
        for c in range(3):
            f = [int(model.channel_frac[c, a, int(rgb[a])]) for a in range(3)]
            order = sorted(range(3), key=lambda a: (-f[a], a))
            stride = [m*m, m, 1]
            base = (int(model.idx[0, rgb[0]])*m+int(model.idx[1, rgb[1]]))*m+int(model.idx[2, rgb[2]])
            i = [base, base+stride[order[0]], base+stride[order[0]]+stride[order[1]], base+m*m+m+1]
            x, y, z = [f[a] for a in order]
            w = [io.ONE-x, x-y, y-z, z]
            error.append(sum(float(nodes[n, c])*v/io.ONE for n, v in zip(i, w))-int(targets[p, c]))
        distance = np.sqrt(sum(v*v for v in error)+.05**2)
        value += mass[p]*(distance+.02*max(distance-6., 0.)**2)
    return value


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖旧合同')
    numba.set_num_threads(4)
    rng = np.random.default_rng(2026101923)
    records = []
    for m in (17, 33):
        grid = np.tile(np.linspace(0, 255, m), (3, 1))
        sparse = io.SparseLut(grid, rng.integers(16, 240, (m, m, m, 3), dtype=np.uint8))
        sparse.nodes[0, 0, 0] = [0, 255, 0]; sparse.nodes[-1, -1, -1] = [255, 0, 255]
        model = cc.from_sparse(sparse)
        for c in range(3):
            for axis in range(3):
                model.channel_frac[c, axis] = np.clip(model.channel_frac[c, axis].astype(np.int64)
                    +(c-1)*1739+(axis-1)*217, 0, io.ONE)
                model.channel_frac[c, axis, [0, 255]] = [0, io.ONE]
        cc.validate(model)
        points = rng.integers(0, 256, (73, 3), dtype=np.uint8)
        points[:8] = np.array(np.meshgrid(*[[0, 255]]*3, indexing='ij')).reshape(3, -1).T
        targets = integer_oracle(model, points)
        targets[8:] = np.clip(targets[8:].astype(np.int32)+rng.integers(-9, 10, targets[8:].shape), 0, 255).astype(np.uint8)
        mass = rng.random(len(points)); mass[:8] = 0.; mass /= mass.sum()
        indices, weights = cg.design(model, points)
        nodes = model.nodes.reshape(-1, 3).astype(np.float64)+rng.uniform(-.4, .4, (m**3, 3))
        nodes = np.clip(nodes, 0, 255)
        loss, gradient = cg.loss_gradient(nodes, indices, weights, targets, mass, 4)
        independent_loss = objective_oracle(model, nodes, points, targets, mass)
        assert abs(loss-independent_loss) < 1e-12
        maximum, coordinates = 0., []
        for c in range(3):
            for n in np.unique(indices[c, 8:].ravel())[:6]:
                epsilon = 1e-4
                plus, minus = nodes.copy(), nodes.copy(); plus[n, c] += epsilon; minus[n, c] -= epsilon
                expected = (objective_oracle(model, plus, points, targets, mass)
                    -objective_oracle(model, minus, points, targets, mass))/(2*epsilon)
                maximum = max(maximum, abs(expected-gradient[n, c]))
                coordinates.append([int(n), c])
        assert maximum < 1e-8
        quantized = np.floor(nodes+.5).astype(np.uint8)
        wrapped = cc.ChannelLut(model.grid, quantized.reshape(model.nodes.shape), model.idx, model.channel_frac)
        np.testing.assert_array_equal(cg.design_output(quantized, indices, weights), integer_oracle(wrapped, points))
        # 全节点+2但边界保持合法，零质量端点同样必须受cap约束。
        shifted = np.clip(model.nodes.astype(np.int32)+2, 0, 255).astype(np.uint8)
        prediction = integer_oracle(model, points)
        caps = np.zeros(len(points), np.int32)
        changed = shifted.reshape(-1, 3)
        shifted_model = cc.ChannelLut(model.grid, shifted, model.idx, model.channel_frac)
        d2 = cg.squared_error(integer_oracle(shifted_model, points), prediction)
        bad = np.flatnonzero(d2 > caps).astype(np.int64)
        assert np.any((mass == 0) & (d2 > caps))
        actual = cg.veto_support(indices, weights, changed, model.nodes.reshape(-1, 3), bad, 4)
        expected = np.zeros_like(actual)
        for row in bad:
            for c in range(3):
                for n, w in zip(indices[c, row], weights[c, row]):
                    if w > 0 and changed[n, c] != model.nodes.reshape(-1, 3)[n, c]: expected[n, c] = True
        np.testing.assert_array_equal(actual, expected)
        candidate, squared, report = cg.veto(model, shifted, points, prediction, caps, indices, weights)
        np.testing.assert_array_equal(cc.predict(candidate, points), integer_oracle(candidate, points))
        np.testing.assert_array_equal(squared, cg.squared_error(integer_oracle(candidate, points), prediction))
        assert report['cap_violations_after'] == 0 and report['cache_recompute_mismatches'] == 0
        assert np.any(weights == 0) and report['rounds'] and np.count_nonzero(actual) > 0
        final = candidate.nodes.reshape(-1, 3)
        original = model.nodes.reshape(-1, 3)
        assert np.all((final == shifted.reshape(-1, 3)) | (final == original))
        records.append({'m': m, 'points': len(points), 'finite_difference_coordinates': coordinates,
            'maximum_gradient_absolute_error': maximum, 'independent_loss_error': abs(loss-independent_loss),
            'quantized_uint64_oracle_mismatches': 0, 'veto_support_mismatches': 0,
            'veto_rounds': report['rounds'], 'cap_violations_after': 0, 'fresh_cache_mismatches': 0,
            'zero_mass_cap_and_0_255_nodes_and_zero_weight_checked': True})
    files = [Path(__file__), ROOT/'scripts/verify_channel_coordinates.py', *[ROOT/'python/lutlab'/n for n in
        ('channel_global_nodes.py', 'channel_coordinates.py', 'interp.py', 'io.py', 'study_provenance.py')]]
    sources = {f.relative_to(ROOT).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    args.output.mkdir(parents=True)
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for f in files: archive.write(f, f.relative_to(ROOT).as_posix())
    result = {'pass': True, 'purpose': __doc__, 'seed': 2026101923,
        'environment': study_provenance.environment_fingerprint(), 'numba_threads': 4,
        'cases': records, 'source_sha256': sources, 'scope': '集中小型合成合同，不拟合真实模型，不代替精度或性能验收'}
    (args.output/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__': main()
