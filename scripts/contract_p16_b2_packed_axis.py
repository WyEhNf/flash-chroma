"""99唯一packed-axis B2纯整数合同；不构建/加载原生库，不映射照片或完整颜色域。"""
import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import struct
import numpy as np

F = 65536
M = 33
T = 17


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tile_index(coords):
    r, g, b = np.moveaxis(coords, -1, 0)
    return (((r//2)*T+g//2)*T+b//2)*8+4*(r%2)+2*(g%2)+b%2


def decode_tile(index):
    block, local = index//8, index%8
    return np.stack((2*(block//(T*T))+(local//4),
        2*((block//T)%T)+((local//2)%2), 2*(block%T)+(local%2)), axis=-1)


def eligible(m, shared, domain, direct_empty, compiled_empty):
    # 仅未来私有分派的参考合同，并非已经实现或调用了原生predicate。
    flags = (shared, domain, direct_empty, compiled_empty)
    return type(m) is int and m == M and all(type(v) is bool and v for v in flags)


def pack_axis(indices, fractions):
    if indices.shape != (3, 256) or fractions.shape != (3, 256):
        raise ValueError('轴形状必须3x256')
    if indices.dtype.kind not in 'ui' or fractions.dtype.kind not in 'ui':
        raise ValueError('轴必须为整数')
    if np.any(indices < 0) or np.any(indices >= 32) or np.any(fractions < 0) or np.any(fractions > F):
        raise ValueError('原idx或Q16越界')
    ni = indices.astype(np.int64)+(fractions == F)
    nf = np.where(fractions == F, 0, fractions).astype(np.int64)
    scale = np.array((8*T*T, 8*T, 8), dtype=np.int64)[:, None]
    parity = np.array((4, 2, 1), dtype=np.int64)[:, None]
    contribution = (ni//2)*scale+(ni%2)*parity
    assert np.all(contribution < F) and np.all(nf < F)
    words = ((contribution << 16) | nf).astype(np.uint32)
    decoded = words.astype(np.int64) >> 16
    restored_idx = 2*(decoded//scale)+(decoded%scale)//parity
    assert np.array_equal(restored_idx, ni)
    assert np.array_equal(words.astype(np.int64)&65535, nf)
    return words, ni, nf, contribution


def exact_float32(bits):
    # 只解释原grid，不用浮点运算生成或改变idx/frac。
    sign, exp, mantissa = bits >> 31, (bits >> 23)&255, bits&0x7fffff
    assert not sign and exp != 255
    if not exp:
        return Fraction(mantissa, 1 << 149)
    value = mantissa+(1 << 23)
    return Fraction(value*(1 << (exp-150)), 1) if exp >= 150 else Fraction(value, 1 << (150-exp))


def coefficient_map(values):
    interior = sorted(set(values)-{0, F})
    result = np.zeros((3, 4), dtype=np.int64)
    for a, value in enumerate(values):
        if value == F:
            result[a, 0] = F
        elif value:
            result[a, 1+interior.index(value)] = 1
    return result


def templates(order):
    # 三个坐标最多有三个不同内部值，1/2/3涵盖所有严格序、并列和端点组合。
    found = {}
    for values in itertools.product((0, 1, 2, 3, F), repeat=3):
        if any(values[order[i]] < values[order[i+1]] for i in (0, 1)):
            continue
        coef = coefficient_map(values)
        key = tuple(coef.ravel())
        found.setdefault(key, (values, coef))
    return list(found.values())


def new_geometry(values, coef):
    # 精确重述旧geometry的四个比较/选择；有并列时first/last可相同。
    x, y, z = values
    first = 1 if y > x else 0
    if z > max(x, y):
        first = 2
    last = 1 if x > y else 0
    if min(x, y) > z:
        last = 2
    high = coef[max(range(3), key=lambda a: values[a])]
    low = coef[min(range(3), key=lambda a: values[a])]
    middle = coef.sum(axis=0)-high-low
    full = np.array((F, 0, 0, 0), dtype=np.int64)
    return first, last, np.stack((full-high, high-middle, middle-low, low))


def compare_maps(old_addresses, old_weights, new_addresses, new_weights):
    count = len(old_addresses)
    addresses = np.concatenate((old_addresses, new_addresses), axis=1)
    coefficients = np.broadcast_to(np.concatenate((old_weights, -new_weights)), (count, 8, 4))
    sorting = np.argsort(addresses, axis=1, kind='stable')
    addresses = np.take_along_axis(addresses, sorting, axis=1)
    coefficients = np.take_along_axis(coefficients, sorting[..., None], axis=1)
    end_group = np.concatenate((addresses[:, :-1] != addresses[:, 1:], np.ones((count, 1), dtype=bool)), axis=1)
    # 每个logical node的系数和为零；先前各组均零时，组末累计和也必须严格零。
    assert np.all(np.cumsum(coefficients, axis=1)[end_group] == 0)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    args = p.parse_args()
    plan = json.loads(args.plan.read_text(encoding='utf-8'))
    assert digest(Path(__file__)) == plan['script_sha256']
    for row in plan['sources']:
        assert digest(Path(row['path'])) == row['sha256']
    if args.output.exists():
        raise FileExistsError('99唯一执行不覆盖原件')
    args.output.mkdir(parents=True)
    (args.output/'executed-plan.json').write_bytes(args.plan.read_bytes())
    proof = {'passed': False, 'native_calls': 0, 'performance_calls': 0}
    try:
        model = Path(plan['models']['ordinary']['path']);assert digest(model) == plan['models']['ordinary']['sha256']
        raw = model.read_bytes()
        assert struct.unpack('<4sIII', raw[:16]) == (b'SLUT', 1, M, 0)
        assert len(raw) == 16+12*M+768+3072+3*M**3
        grid = np.frombuffer(raw, '<u4', 3*M, 16).reshape(3, M)
        exact_grids = [[exact_float32(int(v)) for v in axis] for axis in grid]
        grid_differences = [[axis[i+1]-axis[i] for i in range(M-1)] for axis in exact_grids]
        assert all(axis[0] == 0 and axis[-1] == 255 for axis in exact_grids)
        assert all(min(delta) > 0 and len(set(delta)) > 1 for delta in grid_differences)
        start = 16+12*M
        indices = np.frombuffer(raw, np.uint8, 768, start).reshape(3, 256)
        fractions = np.frombuffer(raw, '<u4', 768, start+768).reshape(3, 256)
        words, norm_indices, norm_fractions, contribution = pack_axis(indices, fractions)
        assert words.nbytes == 3072
        nodes = np.frombuffer(raw, np.uint8, 3*M**3, start+768+3072).reshape(M, M, M, 3).astype(np.uint32)
        node_words = nodes[..., 0] | (nodes[..., 1] << 8) | (nodes[..., 2] << 16)
        padded = np.stack(np.indices((34, 34, 34), dtype=np.int64), axis=-1).reshape(-1, 3)
        labels = tile_index(padded)
        assert np.array_equal(np.sort(labels), np.arange(34**3))
        assert np.array_equal(decode_tile(labels), padded)
        clamped = np.minimum(padded, 32)
        table = np.empty(34**3, dtype=np.uint32)
        table[labels] = node_words[tuple(clamped.T)]
        assert np.array_equal(table[labels], node_words[tuple(clamped.T)])
        lower = np.stack(np.indices((32, 32, 32), dtype=np.int64), axis=-1).reshape(-1, 3)
        totals = {'cell_order_pairs': len(lower)*6, 'symbolic_templates': 0, 'cell_symbolic_maps': 0,
            'actual_uint32_corner_restores': 0, 'physical_corner_indices': 0, 'padding33_corner_loads': 0}
        records = []
        for order in itertools.permutations(range(3)):
            corners = np.repeat(lower[:, None, :], 4, axis=1)
            for j, axis in enumerate(order):
                corners[:, j+1:, axis] += 1
            old_addr = (corners[..., 0]*M+corners[..., 1])*M+corners[..., 2]
            for values, old_coef in templates(order):
                old_w = np.stack((np.array((F, 0, 0, 0))-old_coef[order[0]],
                    old_coef[order[0]]-old_coef[order[1]], old_coef[order[1]]-old_coef[order[2]], old_coef[order[2]]))
                endpoints = np.array(values) == F
                norm_values = tuple(0 if v == F else v for v in values)
                norm_coef = old_coef.copy();norm_coef[endpoints] = 0
                first, last, new_w = new_geometry(norm_values, norm_coef)
                new_base = lower+endpoints
                base = tile_index(new_base)
                stride = np.stack((4+(new_base[:, 0]%2)*(8*T*T-8),
                    2+(new_base[:, 1]%2)*(8*T-4), 1+6*(new_base[:, 2]%2)), axis=1)
                total_stride = stride.sum(axis=1)
                physical = np.stack((base, base+stride[:, first], base+total_stride-stride[:, last], base+total_stride), axis=1)
                assert physical.min() >= 0 and physical.max() < len(table)
                logical = decode_tile(physical)
                assert logical.min() >= 0 and logical.max() <= 33
                # 独立按坐标增量核动态stride；不只用同一tile公式反解自证。
                reference = np.repeat(new_base[:, None, :], 4, axis=1)
                reference[:, 1, first] += 1
                reference[:, 2, :] += 1;reference[:, 2, last] -= 1
                reference[:, 3, :] += 1
                assert np.array_equal(logical, reference)
                clamped_corners = np.minimum(logical, 32)
                new_addr = (clamped_corners[..., 0]*M+clamped_corners[..., 1])*M+clamped_corners[..., 2]
                compare_maps(old_addr, old_w, new_addr, new_w)
                assert np.array_equal(table[physical], node_words.reshape(-1)[new_addr])
                totals['symbolic_templates'] += 1;totals['cell_symbolic_maps'] += len(lower)
                totals['actual_uint32_corner_restores'] += physical.size
                totals['physical_corner_indices'] += physical.size
                totals['padding33_corner_loads'] += int((logical == 33).any(axis=2).sum())
                records.append({'old_order': order, 'representative_values': values,
                    'old_affine_weights': old_w.tolist(), 'new_affine_weights': new_w.tolist(),
                    'new_geometry_first_last': [first, last], 'all_cells_exact': True})
        guards = []
        for m in (17, 25, 33):
            for flags in itertools.product((False, True), repeat=4):
                got = eligible(m, *flags)
                assert got == (m == 33 and all(flags))
                guards.append({'m': m, 'shared_domain_directempty_compiledempty': flags, 'eligible': got})
        for key in ('m17', 'm25'):
            path = Path(plan['models'][key]['path']);assert digest(path) == plan['models'][key]['sha256']
            m = struct.unpack_from('<I', path.read_bytes(), 8)[0]
            assert not eligible(m, True, True, True, True)
        bad = []
        for name, axis, value in (('idx负', 'idx', -1), ('idx32', 'idx', 32), ('frac负', 'frac', -1), ('frac65537', 'frac', F+1)):
            ii, ff = indices.astype(np.int64), fractions.astype(np.int64)
            (ii if axis == 'idx' else ff)[0, 0] = value
            bad.append((name, ii, ff))
        bad += [('非整数', indices.astype(np.float64), fractions), ('形状', indices[:, :255], fractions)]
        for name, ii, ff in bad:
            try:
                pack_axis(ii, ff)
            except ValueError:
                continue
            raise AssertionError('未拒绝坏轴：'+name)
        proof.update({'passed': True, **totals, 'padded_indices_bijection_and_clamp_words': len(table),
            'original_nodes_restored': M**3, 'decoded_private_axis_entries': words.size,
            'normalized_endpoint_entries': int((fractions == F).sum()),
            'largest_axis_contribution': contribution.max(axis=1).tolist(), 'qualification_cases': guards,
            'invalid_axis_cases_rejected': [x[0] for x in bad], 'actual_irregular_grid_unique_gaps': [len(set(x)) for x in grid_differences],
            'private_axis_bytes': words.nbytes, 'tiled_node_logical_bytes': table.nbytes,
            'tiled_node_align64_min_roundup': ((table.nbytes+63)//64)*64,
            'minimum_new_payload_with_axis': ((table.nbytes+63)//64)*64+words.nbytes,
            'symbolic_records': records,
            'scope': '仿射系数按logical clamped node逐项合并严格相等，覆盖全部Q16关系/端点/并列；任意节点整数值的未舍入累加全等，故原单次+32768舍入完全相同。纯参考资格合同并非native实现；未验证实际allocator/owner/并发/原生代码/性能。'})
    finally:
        (args.output/'results.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in proof.items() if k not in ('symbolic_records', 'qualification_cases')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
