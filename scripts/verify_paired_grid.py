"""集中验证成对抵消、组合cap计数、随机真实Q16收益和同色批量安全。"""
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
from lutlab import io, paired_grid as pg, rounded_grid as rg, study_provenance


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def oracle(model, rgb):
    """独立比较器排序和uint64累加；不调用interp或paired的权重构造。"""
    idx, frac = model.tables()
    xyz = rgb.astype(np.int64)
    base = ((idx[0, xyz[:, 0]].astype(np.int64)*model.m+idx[1, xyz[:, 1]])*model.m+idx[2, xyz[:, 2]])
    fraction = np.column_stack([frac[a, xyz[:, a]] for a in range(3)]).astype(np.int64)
    stride = np.tile(np.array([model.m**2, model.m, 1], np.int64), (len(rgb), 1))
    for a, b in ((0, 1), (1, 2), (0, 1)):
        swap = fraction[:, a] < fraction[:, b]
        fraction[swap, a], fraction[swap, b] = fraction[swap, b].copy(), fraction[swap, a].copy()
        stride[swap, a], stride[swap, b] = stride[swap, b].copy(), stride[swap, a].copy()
    f1, f2, f3 = fraction.T
    weight = np.column_stack((io.ONE-f1, f1-f2, f2-f3, f3)).astype(np.uint64)
    index = np.column_stack((base, base+stride[:, 0], base+stride[:, :2].sum(axis=1), base+model.m**2+model.m+1))
    nodes = model.nodes.reshape(-1, 3).astype(np.uint64)
    return ((np.sum(nodes[index]*weight[:, :, None], axis=1, dtype=np.uint64)+io.ONE//2) >> io.Q).astype(np.uint8)


def actual(model, points, target, mass, rho):
    output = oracle(model, points)
    error = output.astype(np.int32)-target.astype(np.int32)
    squared = np.sum(error*error, axis=1, dtype=np.int32)
    return float(mass@rho[squared]), output, squared


def candidate(model, node_values):
    return io.SparseLut(model.grid.copy(), node_values.reshape(model.nodes.shape).copy(),
                        *(array.copy() for array in model.tables()))


def counterexample(rho):
    axis = np.concatenate((np.arange(0, 256, 16), [255])).astype(np.float64)
    grid = np.stack([axis]*3)
    model = io.SparseLut(grid, np.full((17, 17, 17, 3), 10, np.uint8))
    points = np.array([[0, 0, 0], [6, 0, 0], [10, 0, 0], [16, 0, 0]], np.uint8)
    targets = np.array([[11, 10, 10], [10, 10, 10], [10, 10, 10], [9, 10, 10]], np.uint8)
    mass, caps = np.array([.1, .4, .4, .1]), np.array([1, 0, 0, 1], np.int32)
    indices, weights, acc, squared, _ = rg.prepare(model, points, targets)
    nodes = model.nodes.reshape(-1, 3).copy()
    geometry = pg.layout(17, 0)
    a, b, edge, direction = 0, 17**2, 3, 1
    old_loss, _, _ = actual(model, points, targets, mass, rho)
    singles = []
    for node, delta in ((a, 1), (b, -1)):
        trial = nodes.copy(); trial[node, 0] = int(trial[node, 0])+delta
        loss, _, sq = actual(candidate(model, trial), points, targets, mass, rho)
        singles.append({'loss_change': loss-old_loss, 'cap_violations': int(np.count_nonzero(sq > caps))})
    gain, count = pg.gains(indices, weights, acc, squared, targets, mass, nodes, geometry, 0, 0, rho, caps, 4)
    parts = pg._partials(indices, weights, acc, squared, targets, mass, nodes, *geometry[:3],
                         0, 0, rho, caps, 4, 17)
    if (abs(singles[0]['loss_change']-.3) > 1e-12 or abs(singles[1]['loss_change']-.3) > 1e-12
            or singles[0]['cap_violations'] != 1 or singles[1]['cap_violations'] != 1
            or abs(gain[direction, edge]+.2) > 1e-12 or count[direction, edge] != 0
            or int(parts[3][:, direction, edge].sum()) != -2):
        raise AssertionError('两单改禁止但联合允许的抵消/违规次数修正失败')
    move, predicted, selected = pg.select(gain, count, geometry[0], geometry[2], geometry[3])
    if selected != 1 or move[a] != 1 or move[b] != -1:
        raise AssertionError('每块最优配对没有选择抵消反例')
    pg.apply_moves(indices, weights, acc, squared, targets, 0, move)
    nodes[:, 0] = (nodes[:, 0].astype(np.int32)+move).astype(np.uint8)
    loss, output, expected_squared = actual(candidate(model, nodes), points, targets, mass, rho)
    np.testing.assert_array_equal((acc+io.ONE//2) >> io.Q, output)
    np.testing.assert_array_equal(squared, expected_squared)
    np.testing.assert_array_equal(output, targets)
    if abs(loss-old_loss-predicted) > 1e-12:
        raise AssertionError('成对全部顶点批量更新没有兑现预测收益')
    checkpoints, report = pg.propose(model, points, targets, mass, caps=caps)
    final_loss, final, final_sq = actual(checkpoints[-1][1], points, targets, mass, rho)
    np.testing.assert_array_equal(final, targets)
    if report['accepted_sweeps'] != 1 or final_loss != 0 or np.any(final_sq > caps):
        raise AssertionError('整扫抵消反例/逐点cap没有通过')
    np.testing.assert_array_equal(checkpoints[-1][1].grid, model.grid)
    for a0, a1 in zip(checkpoints[-1][1].tables(), model.tables()):
        np.testing.assert_array_equal(a0, a1)
    for kwargs in ({'sweeps': 2}, {'caps': np.zeros(4, np.int32)}):
        try:
            pg.propose(model, points, targets, mass, **({'caps': caps} | kwargs))
        except ValueError:
            pass
        else:
            raise AssertionError('固定预算或起点cap违规没有拒绝')
    return {'single_changes': singles, 'joint_change': float(gain[direction, edge]),
        'overlap_count_correction': int(parts[3][:, direction, edge].sum()), 'joint_cap_violations': int(count[direction, edge]),
        'initial_loss': old_loss, 'final_loss': final_loss, 'selected_pairs': report['selected_pairs'],
        'objective_delta_error': report['objective_delta_error'], 'authority_preserved': True}


def layout_contracts():
    records = []
    for m in (17, 33):
        xyz = np.indices((m-1,)*3, dtype=np.int32).reshape(3, -1).T
        base = (xyz[:, 0]*m+xyz[:, 1])*m+xyz[:, 2]
        stride = (m*m, m, 1)
        for offset in (0, 1):
            blocks, colours, upper, _ = pg.layout(m, offset)
            a = np.repeat(np.arange(m**3), 7)
            valid = upper >= 0
            b = upper[valid]
            if np.any(b >= m**3) or not np.all(blocks[a[valid]] == blocks[b]):
                raise AssertionError('配对节点越界或跨块')
            lo_xyz = np.column_stack((a[valid]//(m*m), (a[valid]//m) % m, a[valid] % m))
            hi_xyz = np.column_stack((b//(m*m), (b//m) % m, b % m))
            delta = hi_xyz-lo_xyz
            np.testing.assert_array_equal(delta[:, 0]*4+delta[:, 1]*2+delta[:, 2]-1,
                                           np.flatnonzero(valid) % 7)
            if np.any(delta < 0) or np.any(delta > 1):
                raise AssertionError('边不是0/1正差可比对')
            for order in itertools.permutations(range(3)):
                index = np.column_stack((base, base+stride[order[0]],
                    base+stride[order[0]]+stride[order[1]], base+m*m+m+1))
                for left in range(4):
                    for right in range(left+1, 4):
                        same_colour = colours[index[:, left]] == colours[index[:, right]]
                        if np.any(same_colour & (blocks[index[:, left]] != blocks[index[:, right]])):
                            raise AssertionError('一个四面体同时涉及两个同色块')
            records.append({'m': m, 'offset': offset, 'valid_edges': int(valid.sum()),
                            'tetrahedra_checked': 6*(m-1)**3})
    return records


def random_contracts(rho):
    rng = np.random.default_rng(2026101911)
    grid = io.uniform_grid(17)
    idx, frac = io.axis_tables(grid)
    frac[0, 16] += 1
    nodes = rng.integers(1, 255, (17, 17, 17, 3), dtype=np.uint8)
    nodes[0, 0, 0, 0], nodes[1, 0, 0, 0] = 0, 255
    model = io.SparseLut(grid, nodes, idx, frac)
    points = np.concatenate((rng.integers(0, 256, (513, 3), dtype=np.uint8),
        np.array([[0, 0, 0], [6, 0, 0], [10, 0, 0], [16, 0, 0], [255, 255, 255], [16, 16, 16]], np.uint8)))
    targets = rng.integers(0, 256, points.shape, dtype=np.uint8)
    mass = rng.uniform(.1, 1., len(points)); mass[::17] = 0; mass /= mass.sum()
    old_loss, old_output, old_sq = actual(model, points, targets, mass, rho)
    indices, weights, acc, squared, _ = rg.prepare(model, points, targets)
    np.testing.assert_array_equal(old_output, (acc+io.ONE//2) >> io.Q)
    np.testing.assert_array_equal(old_sq, squared)
    caps = np.minimum(3*255**2, squared+rng.integers(0, 31, len(points))).astype(np.int32)
    flat = nodes.reshape(-1, 3)
    maximum_error, changes, boundary_rejections, part_error = 0., 0, 0, 0.
    batch_records = []
    for offset in (0, 1):
        geometry = pg.layout(model.m, offset)
        blocks, colours, upper, block_count = geometry
        edges = set()
        for row, weight in zip(indices, weights):
            support = row[weight > 0]
            for a, b in itertools.combinations(support, 2):
                a, b = sorted((int(a), int(b)))
                if blocks[a] == blocks[b]:
                    delta = np.array([b//(17*17)-a//(17*17), (b//17) % 17-(a//17) % 17, b % 17-a % 17])
                    edges.add(a*7+int(delta@[4, 2, 1])-1)
        for colour in range(8):
            channel = (colour+offset) % 3
            gain, count = pg.gains(indices, weights, acc, squared, targets, mass, flat, geometry,
                                    colour, channel, rho, caps, 4)
            if colour == 0:
                g1, c1 = pg.gains(indices, weights, acc, squared, targets, mass, flat, geometry,
                                 colour, channel, rho, caps, 1)
                finite = np.isfinite(gain)
                np.testing.assert_array_equal(finite, np.isfinite(g1))
                np.testing.assert_array_equal(count, c1)
                part_error = max(part_error, float(np.max(np.abs(gain[finite]-g1[finite]))))
            active = [edge for edge in sorted(edges) if colours[edge//7] == colour][:2]
            for edge in active:
                a, b = edge//7, int(upper[edge])
                for direction in range(4):
                    da, db = (1 if direction < 2 else -1), (1 if direction % 2 == 0 else -1)
                    values = int(flat[a, channel])+da, int(flat[b, channel])+db
                    if not all(0 <= value <= 255 for value in values):
                        if not np.isinf(gain[direction, edge]):
                            raise AssertionError('RGB8节点边界没有全局禁止')
                        continue
                    trial = flat.copy(); trial[a, channel], trial[b, channel] = values
                    loss, _, sq = actual(candidate(model, trial), points, targets, mass, rho)
                    maximum_error = max(maximum_error, abs(loss-old_loss-gain[direction, edge]))
                    if int(count[direction, edge]) != int(np.count_nonzero(sq > caps)):
                        raise AssertionError('真实组合违规总数不同于独立整数oracle')
                    changes += 1
            # 即使没有任何训练支撑，节点边界方向仍应全局禁止。
            if offset == 0 and colour == 0:
                for edge in np.flatnonzero((upper >= 0) & (colours[np.arange(len(upper))//7] == colour)):
                    a, b = edge//7, int(upper[edge])
                    for direction in range(4):
                        da, db = (1 if direction < 2 else -1), (1 if direction % 2 == 0 else -1)
                        if not (0 <= int(flat[a, channel])+da <= 255 and 0 <= int(flat[b, channel])+db <= 255):
                            if not np.isinf(gain[direction, edge]):
                                raise AssertionError('无支撑边界方向没有全局禁止')
                            boundary_rejections += 1
        # 宽cap下选一组含多块的真实负收益配对，检验同色批量和全部顶点累加。
        batches = 0
        for colour in range(8):
            channel = (colour+offset) % 3
            gain, count = pg.gains(indices, weights, acc, squared, targets, mass, flat, geometry,
                                   colour, channel, rho, np.full(len(points), 3*255**2, np.int32), 4)
            move, predicted, pairs = pg.select(gain, count, blocks, upper, block_count)
            if pairs < 2:
                continue
            next_acc, next_sq = acc.copy(), squared.copy()
            pg.apply_moves(indices, weights, next_acc, next_sq, targets, channel, move)
            trial = flat.copy(); trial[:, channel] = (trial[:, channel].astype(np.int32)+move).astype(np.uint8)
            loss, expected, reference_sq = actual(candidate(model, trial), points, targets, mass, rho)
            fresh_acc, fresh_sq = rg._accumulate(indices, weights, trial, targets)
            np.testing.assert_array_equal(next_acc, fresh_acc)
            np.testing.assert_array_equal(next_sq, fresh_sq)
            np.testing.assert_array_equal((next_acc+io.ONE//2) >> io.Q, expected)
            np.testing.assert_array_equal(next_sq, reference_sq)
            error = abs(loss-old_loss-predicted)
            maximum_error = max(maximum_error, error)
            both = int(np.count_nonzero(np.sum((move[indices] != 0) & (weights > 0), axis=1) >= 2))
            if not both:
                continue
            batch_records.append({'offset': offset, 'colour': colour, 'pairs': pairs,
                'rows_with_multiple_moving_vertices': both, 'objective_change_error': error,
                'integer_output_mismatches': 0, 'accumulator_mismatches': 0, 'squared_mismatches': 0})
            batches += 1
            break
        if batches != 1:
            raise AssertionError('随机合同没有覆盖多块、多移动顶点的同色批量')
    if maximum_error > 1e-10 or part_error > 1e-10 or not changes or not boundary_rejections:
        raise AssertionError('随机配对收益/私有归约/边界覆盖未达集中合同')
    return {'seed': 2026101911, 'pixels': len(points), 'paired_changes': changes,
        'maximum_gain_error': maximum_error, 'parts_1_vs_4_maximum_error': part_error,
        'global_boundary_rejections': boundary_rejections, 'noncanonical_q16_coordinate': True,
        'zero_mass_rows': int(np.count_nonzero(mass == 0)), 'batches': batch_records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖已冻结合同结果')
    numba.set_num_threads(4)
    files = [Path(__file__), ROOT/'python/lutlab/paired_grid.py', ROOT/'python/lutlab/rounded_grid.py',
             ROOT/'python/lutlab/interp.py', ROOT/'python/lutlab/io.py', ROOT/'python/lutlab/study_provenance.py']
    hashes = {path.relative_to(ROOT).as_posix(): digest(path) for path in files}
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    rho = root+.02*np.maximum(root-6., 0.)**2
    result = {'status': '通过', 'contracts': ['单端均恶化而联合改善', '单端cap均禁止但组合允许',
        '随机真实Q16配对收益与逐点违规总数', '零质量硬约束/边界与parts归约',
        '同色多块批量的独立整数oracle', '两tiling全单元支撑互斥和权威坐标保持'],
        'purpose': '纯合成集中实现合同；非真实LUT拟合、全域精度或性能测试',
        'environment': study_provenance.environment_fingerprint(), 'numba_threads': numba.get_num_threads(),
        'source_sha256': hashes, 'counterexample': counterexample(rho),
        'layout_checks': layout_contracts(), 'random': random_contracts(rho)}
    args.output.mkdir(parents=True)
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            if digest(path) != hashes[path.relative_to(ROOT).as_posix()]:
                raise ValueError('合同过程中相关源码改变')
            archive.write(path, path.relative_to(ROOT).as_posix())
    (args.output/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
