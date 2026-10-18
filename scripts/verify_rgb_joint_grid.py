"""一次集中核对RGB联合步反例、26方向收益/cap及独立uint64前向。"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numba
import numpy as np
from lutlab import io, rgb_joint_grid as rgb, rounded_grid as rg, study_provenance
from verify_paired_grid import actual, candidate, digest, oracle


def counterexample(rho):
    axis = np.concatenate((np.arange(0, 256, 16), [255])).astype(np.float64)
    model = io.SparseLut(np.stack([axis]*3), np.full((17, 17, 17, 3), 10, np.uint8))
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], np.uint8)
    targets = np.array([[11, 11, 10], [9, 10, 10], [10, 9, 10]], np.uint8)
    mass, caps = np.array([.5, .25, .25]), np.full(3, 49, np.int32)
    indices, weights, acc, squared, colours = rg.prepare(model, points, targets)
    nodes = model.nodes.reshape(-1, 3).copy()
    change, forbidden = rgb.gains(indices, weights, acc, squared, targets, mass,
                                 nodes, colours, 0, rho, caps, 4)
    singles = np.count_nonzero(rgb.DIRECTIONS, axis=1) == 1
    chosen = int(np.flatnonzero(np.all(rgb.DIRECTIONS == (1, 1, 0), axis=1))[0])
    if np.any(change[singles, 0] <= 0) or not change[chosen, 0] < -.08 or forbidden[chosen, 0]:
        raise AssertionError('六个单通道步均变差、联合步改善的解析反例未被识别')
    moves, predicted, changed, joint = rgb.select(change, forbidden, colours, 0)
    np.testing.assert_array_equal(moves[0], [1, 1, 0])
    if changed != 1 or joint != 1:
        raise AssertionError('反例没有只选择一个双通道联合步')
    before, _, _ = actual(model, points, targets, mass, rho)
    rgb.apply_moves(indices, weights, acc, squared, targets, moves)
    after, output, sq = actual(candidate(model, (nodes.astype(np.int32)+moves).astype(np.uint8)), points, targets, mass, rho)
    np.testing.assert_array_equal((acc+io.ONE//2) >> io.Q, output)
    np.testing.assert_array_equal(squared, sq)
    if abs(after-before-predicted) > 1e-12:
        raise AssertionError('联合反例预测收益与独立oracle不符')
    return {'single_changes': change[singles, 0].tolist(), 'joint_change': float(change[chosen, 0]),
            'before': before, 'after': after, 'selected_joint_nodes': joint}


def random_contract(rho):
    rng = np.random.default_rng(2026101921)
    grid = io.uniform_grid(17)
    idx, frac = io.axis_tables(grid)
    frac[0, 16] += 1
    nodes = rng.integers(0, 256, (17, 17, 17, 3), dtype=np.uint8)
    nodes[0, 0, 0] = [0, 255, 0]
    model = io.SparseLut(grid, nodes, idx, frac)
    points = np.concatenate((np.zeros((1, 3), np.uint8), rng.integers(0, 256, (512, 3), dtype=np.uint8)))
    targets = rng.integers(0, 256, points.shape, dtype=np.uint8)
    mass = rng.random(len(points)); mass /= mass.sum()
    indices, weights, acc, squared, colours = rg.prepare(model, points, targets)
    caps = np.minimum(3*255**2, squared+rng.integers(0, 5, len(points))).astype(np.int32)
    before, output, sq = actual(model, points, targets, mass, rho)
    np.testing.assert_array_equal((acc+io.ONE//2) >> io.Q, output)
    np.testing.assert_array_equal(squared, sq)
    flat = nodes.reshape(-1, 3)
    chosen = np.unique(indices[weights > 0])[:24]
    maximum_error, checks, invalid = 0., 0, 0
    for colour in range(8):
        change, forbidden = rgb.gains(indices, weights, acc, squared, targets, mass, flat, colours, colour, rho, caps, 4)
        for node in chosen[colours[chosen] == colour]:
            for direction, delta in enumerate(rgb.DIRECTIONS):
                values = flat[node].astype(np.int32)+delta
                if np.any(values < 0) or np.any(values > 255):
                    if not np.isinf(change[direction, node]) or forbidden[direction, node] < 1:
                        raise AssertionError('RGB8越界方向没有拒绝')
                    invalid += 1
                    continue
                trial = flat.copy(); trial[node] = values.astype(np.uint8)
                loss, _, expected_sq = actual(candidate(model, trial), points, targets, mass, rho)
                error = abs(float(change[direction, node])-(loss-before))
                maximum_error = max(maximum_error, error)
                if error > 2e-10 or forbidden[direction, node] != np.count_nonzero(expected_sq > caps):
                    raise AssertionError('26方向收益或联合cap计数与独立oracle不同')
                checks += 1
    checkpoints, report = rgb.propose(model, points, targets, mass, caps=caps)
    final = checkpoints[-1][1]
    loss, output, final_sq = actual(final, points, targets, mass, rho)
    if loss > before+1e-11 or np.any(final_sq > caps) or abs(loss-report['after_weighted_objective']) > 1e-10:
        raise AssertionError('整个8色扫没有兑现收益/cap')
    for old, new in zip(model.tables(), final.tables()):
        np.testing.assert_array_equal(old, new)
    np.testing.assert_array_equal(model.grid, final.grid)
    for changes in ({'sweeps': 2}, {'caps': np.zeros(len(points), np.int32)}, {'parts': True}):
        try:
            rgb.propose(model, points, targets, mass, **({'caps': caps}|changes))
        except ValueError:
            pass
        else:
            raise AssertionError('非法预算/起点cap/分片类型未被拒绝')
    return {'valid_directions_checked': checks, 'invalid_rgb8_checked': invalid,
            'maximum_gain_error': maximum_error, 'full_sweep': report, 'oracle_byte_mismatches': 0}


def geometry():
    records = []
    for m in (17, 33):
        xyz = np.indices((m-1,)*3, dtype=np.int32).reshape(3, -1).T
        base = (xyz[:, 0]*m+xyz[:, 1])*m+xyz[:, 2]
        node_xyz = np.indices((m,)*3).reshape(3, -1).T
        colours = ((node_xyz[:, 0]%2)*4+(node_xyz[:, 1]%2)*2+node_xyz[:, 2]%2)
        stride = (m*m, m, 1)
        for order in itertools.permutations(range(3)):
            vertices = np.column_stack((base, base+stride[order[0]],
                base+stride[order[0]]+stride[order[1]], base+m*m+m+1))
            c = np.sort(colours[vertices], axis=1)
            if np.any(np.diff(c, axis=1) == 0):
                raise AssertionError('同色节点正支撑会相交，批量收益相加不合法')
        records.append({'m': m, 'tetrahedra': 6*(m-1)**3, 'same_colour_overlap': 0})
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖已有集中合同')
    args.output.mkdir(parents=True)
    numba.set_num_threads(4)
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    rho = root+.02*np.maximum(root-6., 0.)**2
    files = [Path(__file__), ROOT/'scripts/verify_paired_grid.py', ROOT/'python/lutlab/rgb_joint_grid.py',
             ROOT/'python/lutlab/rounded_grid.py', ROOT/'python/lutlab/interp.py', ROOT/'python/lutlab/io.py']
    sources = {str(p.relative_to(ROOT)).replace('\\', '/'): digest(p) for p in files}
    result = {'pass': True, 'purpose': '联合RGB数值与硬cap正确性，有限合成合同；不是精度或性能验收',
              'environment': study_provenance.environment_fingerprint(), 'numba_threads': numba.get_num_threads(),
              'source_sha256': sources, 'counterexample': counterexample(rho),
              'random': random_contract(rho), 'geometry': geometry()}
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name, sha in sources.items():
            if digest(ROOT/name) != sha:
                raise ValueError('合同期间源码改变')
            z.write(ROOT/name, name)
    (args.output/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
