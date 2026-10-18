"""固定已验分通道几何，三次完整域整数矩/连续LS及合法盒节点有理下界。"""
from __future__ import annotations
import argparse
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import zipfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from lutlab import channel_coordinates as cc, fullfit, io, study_provenance
from prove_velvia_fixed_tetra_bound import raw_moments, q20_exact


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def array_sha(array):
    return hashlib.sha256(memoryview(np.ascontiguousarray(array))).hexdigest()


def rational(value):
    return {'numerator': str(value.numerator), 'denominator': str(value.denominator),
        'decimal_display_only': float(value)}


def checked(spec):
    path = ROOT/spec['path']
    if digest(path) != spec['sha256']: raise ValueError(f'冻结来源SHA不同：{path}')
    return path


def support(model, output):
    """原最近RGB见证，只检查一次；失败不是秩亏或不可行证明。"""
    m, (idx, frac) = model.m, model.tables()
    levels = np.rint(model.grid).astype(np.int64)
    if np.any(np.diff(levels, axis=1) <= 0) or levels.min() < 0 or levels.max() > 255:
        return {'pass': False, 'reason': '最近RGB见证重复或越界；不能推断秩亏'}, None
    points = np.stack(np.meshgrid(*levels, indexing='ij'), -1).reshape(-1, 3).astype(np.uint8)
    diagonal, column = [0]*(m**3), [0]*(m**3)
    indices, weights = np.empty((len(points), 4), np.uint32), np.empty((len(points), 4), np.uint32)
    for row, point in enumerate(points):
        f = [int(frac[a, int(point[a])]) for a in range(3)]
        order = sorted(range(3), key=lambda a: (-f[a], a))
        base = (int(idx[0, int(point[0])])*m+int(idx[1, int(point[1])]))*m+int(idx[2, int(point[2])])
        stride = [m*m, m, 1]
        vertex = [base, base+stride[order[0]], base+stride[order[0]]+stride[order[1]], base+m*m+m+1]
        x, y, z = [f[a] for a in order]
        weight = [io.ONE-x, x-y, y-z, z]
        if min(weight) < 0 or sum(weight) != io.ONE or min(vertex) < 0 or max(vertex) >= m**3:
            raise AssertionError('独立见证几何不合法')
        for i, value in zip(vertex, weight):
            column[i] += value
            if i == row: diagonal[row] += value
        indices[row], weights[row] = vertex, weight
    margins = [4*d-io.ONE-c for d, c in zip(diagonal, column)]
    minimum = min(margins)
    np.savez_compressed(output, points=points, indices=indices, weights=weights,
        margins=np.asarray(margins, np.int64), idx=idx, frac=frac)
    record = {'pass': minimum > 0, 'method': 'nearest_rgb_symmetric_gershgorin_q16',
        'witness_count': len(points), 'witness_rgb_sha256': array_sha(points),
        'axis_tables_sha256': hashlib.sha256(idx.tobytes()+frac.tobytes()).hexdigest(),
        'minimum_twice_symmetric_margin_q16': minimum,
        'scope': '正余量仅为SPD充分条件；非正余量不证明秩亏或RGB8不可行'}
    eigenvalue = Fraction(minimum**2, 64*(2*io.ONE)**2) if minimum > 0 else None
    if eigenvalue is not None: record['lambda_exact'] = rational(eigenvalue)
    return record, eigenvalue


def matrix(diagonal, upper, m):
    size = m**3
    offsets = np.asarray((1, m, m+1, m*m, m*m+1, m*m+m, m*m+m+1), np.int32)
    rows = np.repeat(np.arange(size, dtype=np.int32), 7)
    cols = rows+np.tile(offsets, size)
    nonzero = upper.ravel() != 0
    if np.any(cols[nonzero] >= size): raise AssertionError('原始上三角越界')
    positive = sp.coo_matrix((upper.ravel()[nonzero].astype(np.float64)*2.**-38,
        (rows[nonzero], cols[nonzero])), shape=(size, size)).tocsr()
    h = (positive+positive.T+sp.diags(diagonal.astype(np.float64)*2.**-38)).tocsr()
    h.sort_indices()
    return h


def quadratic(diagonal, upper, rhs, c_raw, zint, m):
    """Python整数矩乘/独立二次型；盒下界无需SPD或浮点误差界。"""
    z = [int(v) for v in zint]
    hz = [int(d)*v for d, v in zip(diagonal, z)]
    direct = sum(int(d)*v*v for d, v in zip(diagonal, z))
    offsets = (1, m, m+1, m*m, m*m+1, m*m+m, m*m+m+1)
    for i, row in enumerate(upper):
        for offset, raw in zip(offsets, row):
            value = int(raw)
            if not value: continue
            j = i+offset
            if j >= len(z): raise AssertionError('有理矩乘stencil越界')
            hz[i] += value*z[j]; hz[j] += value*z[i]
            direct += 2*value*z[i]*z[j]
    if direct != sum(a*b for a, b in zip(z, hz)): raise AssertionError('整数二次型与矩乘不符')
    bdot = sum(int(b)*v for b, v in zip(rhs, z))
    g = [value-(int(b) << 36) for value, b in zip(hz, rhs)]
    fnum = direct-(bdot << 37)+(int(c_raw) << 72)
    if fnum != sum(v*(a-(int(b) << 36)) for v, a, b in zip(z, g, rhs))+(int(c_raw) << 72):
        raise AssertionError('整数目标两种表达不符')
    # F=||Az-y||²/64；g=Hz-b，不含导数中的2。
    linear = 2*sum(a*((0 if a >= 0 else 255)*(1 << 20)-v) for a, v in zip(g, z))
    box_num = fnum+linear
    return {'Fnum': str(fnum), 'Hnum_quadratic': str(direct), 'bnum_dot_zint': str(bdot),
        'linear_box_correction_numerator': str(linear), 'box_lower_numerator_over_2pow96': str(box_num),
        'sum_gnum_squared': str(sum(v*v for v in g)), 'integer_quadratic_crosscheck_equal': True}, fnum, box_num, sum(v*v for v in g)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=ROOT/'experiments/channel-continuous-floor-v1.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); args.plan, args.output = args.plan.resolve(), args.output.resolve()
    if args.output.exists(): raise ValueError('不覆盖既有诊断')
    plan = json.loads(args.plan.read_text(encoding='utf-8'))
    paths = {name: checked(spec) for name, spec in plan['inputs'].items()}
    os.environ['JSHC_FULL_FIT_LIB'] = str(checked(plan['trainer']))
    trainer = fullfit.trainer_fingerprint()
    if (trainer['abi_version'] != plan['trainer']['abi'] or trainer['library_sha256'] != plan['trainer']['sha256']
            or trainer['embedded_source_fingerprint'] != plan['trainer']['embedded_source_fingerprint']):
        raise ValueError('既有C ABI来源不同')
    frozen = np.load(paths['model'])
    if str(frozen['format']) != 'channel_coordinates_v1_experimental': raise ValueError('输入格式不同')
    rep = cc.ChannelLut(frozen['grid'], frozen['nodes'], frozen['shared_idx'], frozen['channel_frac'])
    cc.validate(rep)
    if rep.m != 33 or plan['assemblies'] != 3: raise ValueError('只接受冻结m33三次组装')
    history = json.loads(paths['matched_results'].read_text(encoding='utf-8'))
    old_mse = history['solvers']['tetra']['unrounded_uniform_cube_mse_from_normal_moments']
    if old_mse != plan['shared_reference_mse']: raise ValueError('旧共享设计参照不同')
    accepted = json.loads(paths['accepted_results'].read_text(encoding='utf-8'))
    if accepted['representation_sha256'] != plan['inputs']['model']['sha256']: raise ValueError('已验模型绑定不同')
    files = [Path(__file__), args.plan, ROOT/'scripts/prove_velvia_fixed_tetra_bound.py',
        *[ROOT/'python/lutlab'/name for name in ('fullfit.py', 'channel_coordinates.py', 'io.py', 'study_provenance.py')],
        *[ROOT/name for name in fullfit.NATIVE_SOURCES]]
    sources = {p.relative_to(ROOT).as_posix(): digest(p) for p in files}
    args.output.mkdir(parents=True)
    run = {'plan': plan, 'plan_sha256': digest(args.plan), 'source_sha256': sources,
        'environment': study_provenance.environment_fingerprint(), 'trainer': trainer,
        'input_sha256': {name: digest(p) for name, p in paths.items()},
        'scope': '三输出权威设计各组装一次，仅连续节点/整数证据矩；不映射任何像素/模型/照片'}
    run['identity_sha256'] = study_provenance.identity_digest(run)
    (args.output/'run.json').write_text(json.dumps(run, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for p in files: archive.write(p, p.relative_to(ROOT).as_posix())
    table = io.load_full(paths['table'], mmap=True)
    records, all_nodes, all_q20, all_residuals = [], [], [], []
    lower_box, lower_spd, clipped_upper, actual = Fraction(0), Fraction(0), Fraction(0), Fraction(0)
    mse, assembly_calls = 0., 0
    for channel in range(3):
        # 明确传入权威表，不调用会重生frac的normal_equations。
        model = io.SparseLut(rep.grid, rep.nodes, rep.idx, rep.channel_frac[channel])
        certificate, eigenvalue = support(model, args.output/f'witness-c{channel}.npz')
        diagonal, upper, rhs_all, metadata = raw_moments(table, model, trainer)
        assembly_calls += 1
        raw_hash = hashlib.sha256()
        for a in (diagonal, upper, rhs_all, metadata[4:]): raw_hash.update(memoryview(a))
        constant = sum(int(v) for v in diagonal)+2*sum(int(v) for v in upper.ravel())
        if constant != (256**3)*io.ONE**2: raise AssertionError('原始矩常量设计不守恒')
        np.savez_compressed(args.output/f'raw-moments-c{channel}.npz', diagonal=diagonal, upper=upper,
            rhs=rhs_all, metadata=metadata, idx=rep.idx, frac=rep.channel_frac[channel])
        h, b = matrix(diagonal, upper, rep.m), rhs_all[:, channel].astype(np.float64)*2.**-22
        if np.any(h.diagonal() <= 0): raise ValueError('存在无支撑节点，本轮CG策略不能据此宣称全局不可行')
        count = [0]
        def callback(_): count[0] += 1
        nodes, info = spla.cg(h, b, x0=rep.nodes.reshape(-1, 3)[:, channel].astype(np.float64),
            M=sp.diags(1/h.diagonal()), rtol=plan['solver']['rtol'],
            maxiter=plan['solver']['maxiter'], callback=callback)
        residual = h@nodes-b
        relative = float(np.linalg.norm(residual)/np.linalg.norm(b))
        if info != 0 or not np.all(np.isfinite(nodes)) or relative > 1e-12:
            raise AssertionError('本轮唯一无ridge CG未达到冻结残差要求；不自动换解法/预算')
        c_raw, rhs = int(metadata[4+channel]), rhs_all[:, channel]
        continuous = float((c_raw/64.-2*nodes@b+nodes@(h@nodes))*64/(256**3))
        q20 = np.asarray([q20_exact(v) for v in nodes], np.int64)
        evidence, fnum, boxnum, gnorm = quadratic(diagonal, upper, rhs, c_raw, q20, rep.m)
        bound = Fraction(boxnum, 1 << 96)
        lower_box += bound
        spd = None
        if eigenvalue is not None:
            spd = (Fraction(fnum, 1 << 78)-Fraction(gnorm, 1 << 116)/eigenvalue)*Fraction(64, 256**3)
            lower_spd += spd
        clipped = np.clip(q20, 0, 255*(1 << 20))
        clipped_evidence, clipped_fnum, _, _ = quadratic(diagonal, upper, rhs, c_raw, clipped, rep.m)
        current_evidence, current_fnum, _, _ = quadratic(diagonal, upper, rhs, c_raw,
            rep.nodes.reshape(-1, 3)[:, channel].astype(np.int64)*(1 << 20), rep.m)
        clipped_value, current_value = Fraction(clipped_fnum, 1 << 96), Fraction(current_fnum, 1 << 96)
        if bound > clipped_value: raise AssertionError('盒下界超过可行盒节点上界')
        clipped_upper += clipped_value; actual += current_value; mse += continuous
        records.append({'channel': channel, 'assembly_call': assembly_calls, 'integer_system_sha256': raw_hash.hexdigest(),
            'native_metadata': metadata.tolist(), 'constant_design_sum': str(constant), 'nnz': h.nnz,
            'zero_diagonal_nodes': int(np.count_nonzero(diagonal == 0)), 'support_certificate': certificate,
            'cg': {'info': int(info), 'iterations': count[0], 'relative_residual': relative,
                'residual_norm': float(np.linalg.norm(residual)), 'regularization': 0.},
            'unbounded_approximate_ls_unrounded_uniform_mse': continuous,
            'continuous_node_min': float(nodes.min()), 'continuous_node_max': float(nodes.max()),
            'continuous_nodes_outside_0_255': int(np.count_nonzero((nodes < 0) | (nodes > 255))),
            'q20_integer_evidence': evidence, 'box_first_order_unrounded_mse_lower_exact': rational(bound),
            'spd_residual_unrounded_mse_lower_exact_if_supported': rational(spd) if spd is not None else None,
            'clipped_q20_feasible_continuous_mse_upper_exact': rational(clipped_value),
            'clipped_q20_integer_evidence': clipped_evidence,
            'current_rgb8_nodes_unrounded_mse_exact': rational(current_value), 'current_node_integer_evidence': current_evidence})
        all_nodes.append(nodes); all_q20.append(q20); all_residuals.append(residual)
        print(json.dumps({'channel': channel, 'mse': continuous, 'box_lower': float(bound),
            'clipped_upper': float(clipped_value), 'current_nodes_mse': float(current_value),
            'support_pass': certificate['pass'], 'support_margin': certificate.get('minimum_twice_symmetric_margin_q16'),
            'iterations': count[0]}, ensure_ascii=False), flush=True)
    nodes = np.column_stack(all_nodes).reshape(rep.nodes.shape)
    np.savez_compressed(args.output/'continuous-evidence-nodes.npz', continuous_float64=nodes,
        zint_q20=np.column_stack(all_q20), normal_residual_float64=np.column_stack(all_residuals),
        grid=rep.grid, shared_idx=rep.idx, channel_frac=rep.channel_frac)
    if assembly_calls != 3: raise AssertionError('组装次数不是冻结3次')
    if sources != {p.relative_to(ROOT).as_posix(): digest(p) for p in files} or trainer != fullfit.trainer_fingerprint():
        raise ValueError('诊断过程中数值来源发生变化')
    result = {'run_identity': run['identity_sha256'], 'assembly_calls': assembly_calls, 'channels': records,
        'sum_unbounded_approximate_ls_unrounded_uniform_mse': mse,
        'shared_old_geometry_approximate_ls_same_objective_mse': old_mse,
        'fractional_mse_reduction_vs_shared_old_geometry': 1-mse/old_mse,
        'box_first_order_uniform_mse_lower_exact': rational(lower_box),
        'unbounded_spd_uniform_mse_lower_exact_if_all_supported': rational(lower_spd) if all(r['support_certificate']['pass'] for r in records) else None,
        'clipped_q20_feasible_continuous_mse_upper_exact': rational(clipped_upper),
        'current_rgb8_nodes_unrounded_uniform_mse_exact': rational(actual),
        'continuous_unbounded_gap_vs_current_nodes_display': 1-mse/float(actual),
        'clipped_feasible_continuous_gap_vs_current_nodes_display': 1-float(clipped_upper/actual),
        'rgb8_zero_error_impossible_for_frozen_geometry_and_legal_nodes': lower_box > Fraction(3, 4),
        'rgb8_output_rms_lower_display_only': max(0., math.sqrt(max(0., float(lower_box)))-math.sqrt(.75)),
        'current_frozen_rgb8_output_full_rms_historical': accepted['cube']['rms'],
        'all_pixel_mapping_calls': 0, 'new_deployable_models': 0, 'limits': plan['limits'],
        'proof': '原始整数H为全域Q16外积和，PSD；F(x)>=F(z)+2(Hz-b)·(x-z)，对x逐坐标取0/255最小化线性项。Q20转换、矩乘、二次型和Fraction全为精确整数；无需SPD。连续输出凸组合且合法节点在[0,255]，RGB8 half-up舍入误差L2<=sqrt(3/4)，反三角给最终RGB8 RMS下界。',
        'interpretation': '连续无界LS与合法盒连续上/下界回答固定几何表达能力；不证明真实RGB距离/照片加权目标、RGB8整数节点最优或可部署精度收益。'}
    artifacts = [p for p in args.output.iterdir() if p.is_file()]
    result['artifact_sha256'] = {p.name: digest(p) for p in artifacts}
    (args.output/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('sum_unbounded_approximate_ls_unrounded_uniform_mse',
        'shared_old_geometry_approximate_ls_same_objective_mse', 'fractional_mse_reduction_vs_shared_old_geometry',
        'box_first_order_uniform_mse_lower_exact', 'clipped_q20_feasible_continuous_mse_upper_exact',
        'current_rgb8_nodes_unrounded_uniform_mse_exact', 'rgb8_zero_error_impossible_for_frozen_geometry_and_legal_nodes',
        'rgb8_output_rms_lower_display_only')}, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__': main()
