"""只用固定ordinary首级节点/轴做精确结构普查；无gold/照片/16M输出/原生库。"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import numpy as np


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def first_witness(mask, actual, expected):
    positions = np.argwhere(mask)
    if not len(positions):
        return None
    pos = tuple(int(v) for v in positions[0])
    return {'index': list(pos), 'actual': int(actual[pos]), 'expected': int(expected[pos])}


def rank_certificate(matrix, prime):
    original = matrix.astype(np.int64) % prime
    reduced = original.copy()
    rank, columns = 0, []
    for column in range(reduced.shape[1]):
        candidates = np.flatnonzero(reduced[rank:, column])
        if not len(candidates):
            continue
        pivot = rank + int(candidates[0])
        reduced[[rank, pivot]] = reduced[[pivot, rank]]
        inverse = pow(int(reduced[rank, column]), prime - 2, prime)
        reduced[rank] = reduced[rank] * inverse % prime
        for row in range(rank + 1, reduced.shape[0]):
            reduced[row] = (reduced[row] - reduced[row, column] * reduced[rank]) % prime
        columns.append(column);rank += 1
        if rank == reduced.shape[0]:
            break
    # 满行秩时给原整数矩阵方形minor；非零模行列式是有理秩下界证书。
    minor = matrix[:, columns].astype(np.int64) if rank == matrix.shape[0] else None
    determinant = None
    if minor is not None:
        a = minor.copy() % prime;determinant = 1
        for j in range(rank):
            rows = np.flatnonzero(a[j:, j]);assert len(rows)
            k = j + int(rows[0])
            if j != k:
                a[[j, k]] = a[[k, j]];determinant = -determinant
            value = int(a[j, j]);determinant = determinant * value % prime
            inverse = pow(value, prime - 2, prime)
            for i in range(j + 1, rank):
                a[i] = (a[i] - a[i, j] * inverse % prime * a[j]) % prime
        assert determinant % prime
    return {'rank_mod_prime': rank, 'row_count': matrix.shape[0], 'column_count': matrix.shape[1],
        'pivot_columns': columns, 'full_row_rank': rank == matrix.shape[0],
        'selected_minor_integer_entries': None if minor is None else minor.tolist(),
        'selected_minor_determinant_mod_prime': determinant,
        'scope': '满行秩排除小于m的全局该模态低秩；不排除分块结构或其他精确表示。'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    plan = json.loads(a.plan.read_text(encoding='utf-8'))
    assert sha(Path(__file__)) == plan['script_sha256']
    path = Path(plan['model']['path']);assert sha(path) == plan['model']['sha256']
    for row in plan['code_sources']:
        assert sha(Path(row['path'])) == row['sha256']
    if a.output.exists():
        raise FileExistsError('固定纯模型普查不覆盖')
    a.output.mkdir(parents=True)
    raw = path.read_bytes();magic, version, m, reserved = struct.unpack('<4sIII', raw[:16])
    assert magic == b'SLUT' and version == 1 and reserved == 0
    assert len(raw) == 16 + 12 * m + 768 + 3072 + m * m * m * 3
    offset = 16 + 12 * m
    idx = np.frombuffer(raw, np.uint8, 768, offset).reshape(3, 256)
    frac = np.frombuffer(raw, '<u4', 768, offset + 768).reshape(3, 256)
    nodes = np.frombuffer(raw, np.uint8, m*m*m*3, offset + 768 + 3072).reshape(m, m, m, 3).astype(np.int64)
    assert np.all(idx < m - 1) and np.all(frac <= 65536)
    axis_tests, additive = [], []
    for c in range(3):
        channel = nodes[..., c]
        tests = []
        for axis in range(3):
            selection = [0, 0, 0];selection[axis] = slice(None)
            curve = channel[tuple(selection)]
            shape = [1, 1, 1];shape[axis] = m
            expected = np.broadcast_to(curve.reshape(shape), channel.shape)
            mask = channel != expected
            tests.append({'axis': axis, 'mismatched_nodes': int(mask.sum()),
                'exact': not bool(mask.any()), 'first_counterexample': first_witness(mask, channel, expected)})
        axis_tests.append({'channel': c, 'eligible_axis_curves': [v['axis'] for v in tests if v['exact']], 'tests': tests})
        expected = channel[:, 0, 0][:, None, None] + channel[0, :, 0][None, :, None] + channel[0, 0, :][None, None, :] - 2 * channel[0, 0, 0]
        bad = channel != expected
        additive.append({'channel': c, 'exact': not bool(bad.any()), 'mismatched_nodes': int(bad.sum()),
            'maximum_abs_residual': int(np.abs(channel - expected).max()),
            'first_counterexample': first_witness(bad, channel, expected)})
    weights = [np.bincount(axis, minlength=m - 1).astype(np.int64) for axis in idx]
    cell_weight = weights[0][:, None, None] * weights[1][None, :, None] * weights[2][None, None, :]
    assert int(cell_weight.sum()) == 1 << 24
    base = nodes[:-1, :-1, :-1]
    dr, dg, db = nodes[1:, :-1, :-1]-base, nodes[:-1, 1:, :-1]-base, nodes[:-1, :-1, 1:]-base
    local = np.ones(base.shape, dtype=bool)
    local_axis = np.ones((*base.shape, 3), dtype=bool)
    for x in (0, 1):
        for y in (0, 1):
            for z in (0, 1):
                actual = nodes[x:m-1+x, y:m-1+y, z:m-1+z]
                local &= actual == base + x*dr + y*dg + z*db
                for axis, coefficient in enumerate((dr, dg, db)):
                    local_axis[..., axis] &= actual == base + (x, y, z)[axis]*coefficient
    all_local = local.all(axis=3)
    local_curve = local_axis.any(axis=4).all(axis=3)
    constant = (local_axis.all(axis=4)).all(axis=3)
    prime = plan['rank_prime'];assert prime == 65521
    assert all(prime % v for v in range(2, math.isqrt(prime) + 1))
    ranks = []
    for c in range(3):
        for axis in range(3):
            matrix = np.moveaxis(nodes[..., c], axis, 0).reshape(m, -1)
            ranks.append({'channel': c, 'axis': axis, **rank_certificate(matrix, prime)})
    centered = (nodes.reshape(-1, 3) - nodes[0, 0, 0]).T
    chroma = {}
    for c in (1, 2):
        values = nodes[..., c] - nodes[..., 0]
        unique, counts = np.unique(values, return_counts=True)
        chroma[str(c)] = {'differences': unique.tolist(), 'counts': counts.tolist(), 'constant_offset': len(unique) == 1}
    result = {'purpose': plan['purpose'], 'model': plan['model'], 'm': m, 'node_count': m**3,
        'axis_curve_tests': axis_tests, 'core_separable_eligible': all(v['eligible_axis_curves'] for v in axis_tests),
        'all_fraction_endpoints': bool(np.isin(frac, (0, 65536)).all()),
        'interior_fraction_counts': [int(((v != 0) & (v != 65536)).sum()) for v in frac],
        'constant_channels': [bool(np.all(nodes[..., c] == nodes[0, 0, 0, c])) for c in range(3)],
        'additive_channel_tests': additive, 'rank_prime': prime, 'prime_trial_division_verified': True,
        'spatial_rank_certificates': ranks, 'centered_rgb_rank_certificate': rank_certificate(centered, prime),
        'node_chroma_offsets': chroma, 'reachable_cells': int((cell_weight > 0).sum()),
        'local_exact_affine': {'cells_all_rgb': int(all_local.sum()), 'uniform_rgb8_input_codes': int(cell_weight[all_local].sum()),
            'per_channel_cells': [int(local[..., c].sum()) for c in range(3)]},
        'local_axis_curve': {'cells_all_rgb': int(local_curve.sum()), 'uniform_rgb8_input_codes': int(cell_weight[local_curve].sum())},
        'local_constant': {'cells_all_rgb': int(constant.sum()), 'uniform_rgb8_input_codes': int(cell_weight[constant].sum())},
        'scope': '只节点/idx/frac及精确模minor；cell权重来自idx码数直积。无gold、照片、16M输出、拟合、JIT、BLAS或原生调用；局部结构比例不是实测速度。'}
    (a.output/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (a.output/'executed-plan.json').write_bytes(a.plan.read_bytes())
    print(json.dumps({k: result[k] for k in ('m','node_count','core_separable_eligible','all_fraction_endpoints',
        'interior_fraction_counts','local_exact_affine','local_axis_curve','local_constant')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
