"""同权威Q16设计和完整域L2的四面体/三线性匹配拟合，只评价冻结探针。"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from lutlab import fit, fullfit, interp, io, study_provenance


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def array_sha(array):
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def checked(spec):
    path = ROOT/spec['path']
    if digest(path) != spec['sha256']:
        raise ValueError(f'冻结来源SHA不同：{path}')
    return path


def contract64(table, matrices):
    """全程float64，轴收缩顺序固定，与旧float32 contract明确分开。"""
    x = np.tensordot(matrices[0], np.asarray(table, np.float64), axes=(1, 0))
    x = np.tensordot(matrices[1], x, axes=(1, 1))
    x = np.tensordot(matrices[2], x, axes=(1, 2))
    return np.ascontiguousarray(x.transpose(2, 1, 0, 3))


def basis_tables(idx, frac, m):
    basis, integer_basis = [], []
    for axis in range(3):
        q = np.zeros((256, m), np.int64)
        q[np.arange(256), idx[axis]] = io.ONE-frac[axis].astype(np.int64)
        q[np.arange(256), idx[axis].astype(np.intp)+1] += frac[axis]
        basis.append(q.astype(np.float64)/io.ONE)
        integer_basis.append(q)
    return basis, integer_basis


def rgb8(values):
    return np.clip(np.floor(values+.5), 0, 255).astype(np.uint8)


def metrics(prediction, target):
    error = prediction.astype(np.float64)-target.astype(np.float64)
    squared = np.sum(error*error, axis=1)
    distance = np.sqrt(squared)
    return {'mean': float(distance.mean()), 'rms': float(np.sqrt(squared.mean())),
            'p99': float(np.percentile(distance, 99)), 'max': float(distance.max())}


def tri_oracle(nodes, model, points):
    """独立八权重Q48整数累加；最大累加器255*2^48，uint64安全。"""
    idx, frac = model.tables()
    cell = np.column_stack([idx[a, points[:, a]] for a in range(3)]).astype(np.intp)
    f = np.column_stack([frac[a, points[:, a]] for a in range(3)]).astype(np.uint64)
    acc = np.zeros((len(points), 3), np.uint64)
    weight_sum = np.zeros(len(points), np.uint64)
    for dr in (0, 1):
        for dg in (0, 1):
            for db in (0, 1):
                weight = ((f[:, 0] if dr else io.ONE-f[:, 0])
                    *(f[:, 1] if dg else io.ONE-f[:, 1])*(f[:, 2] if db else io.ONE-f[:, 2]))
                values = nodes[cell[:, 0]+dr, cell[:, 1]+dg, cell[:, 2]+db].astype(np.uint64)
                acc += weight[:, None]*values
                weight_sum += weight
    if not np.all(weight_sum == 1 << 48) or np.any(acc > 255*(1 << 48)):
        raise AssertionError('Q48权重或累加器上界不成立')
    return ((acc+(1 << 47)) >> 48).astype(np.uint8)


def tri_horner(nodes, model, points):
    """独立逐轴整数嵌套，不展开Q48权重、不作中间舍入。"""
    idx, frac = model.tables()
    i = np.column_stack([idx[a, points[:, a]] for a in range(3)]).astype(np.intp)
    x, y, z = [frac[a, points[:, a]].astype(np.uint64)[:, None] for a in range(3)]
    values = []
    for dg in (0, 1):
        for db in (0, 1):
            left = nodes[i[:, 0], i[:, 1]+dg, i[:, 2]+db].astype(np.uint64)
            right = nodes[i[:, 0]+1, i[:, 1]+dg, i[:, 2]+db].astype(np.uint64)
            values.append(left*(io.ONE-x)+right*x)
    lower = values[0]*(io.ONE-y)+values[2]*y
    upper = values[1]*(io.ONE-y)+values[3]*y
    return ((lower*(io.ONE-z)+upper*z+(1 << 47)) >> 48).astype(np.uint8)


def tetra_oracle(nodes, model, points):
    """独立比较器排序，uint64累加，不使用interp索引生成。"""
    idx, frac = model.tables()
    base = ((idx[0, points[:, 0]].astype(np.int64)*model.m+idx[1, points[:, 1]])*model.m+idx[2, points[:, 2]])
    f = np.column_stack([frac[a, points[:, a]] for a in range(3)]).astype(np.int64)
    strides = np.tile(np.array([model.m**2, model.m, 1], np.int64), (len(points), 1))
    for a, b in ((0, 1), (1, 2), (0, 1)):
        swap = f[:, a] < f[:, b]
        f[swap, a], f[swap, b] = f[swap, b].copy(), f[swap, a].copy()
        strides[swap, a], strides[swap, b] = strides[swap, b].copy(), strides[swap, a].copy()
    w = np.column_stack((io.ONE-f[:, 0], f[:, 0]-f[:, 1], f[:, 1]-f[:, 2], f[:, 2])).astype(np.uint64)
    index = np.column_stack((base, base+strides[:, 0], base+strides[:, :2].sum(axis=1), base+model.m**2+model.m+1))
    return ((np.sum(nodes.reshape(-1, 3).astype(np.uint64)[index]*w[:, :, None], axis=1, dtype=np.uint64)+io.ONE//2) >> io.Q).astype(np.uint8)


def evaluate(nodes, model, points, target, kind):
    function = interp.tetra_weights if kind == 'tetra' else interp.tri_weights
    index, weight = function(points, *model.tables(), model.m)
    continuous = np.einsum('nk,nkc->nc', weight, nodes.reshape(-1, 3)[index])
    quantized = rgb8(nodes)
    quantized_continuous = np.einsum('nk,nkc->nc', weight, quantized.reshape(-1, 3)[index])
    if kind == 'tri':
        integer = tri_oracle(quantized, model, points)
        np.testing.assert_array_equal(integer, tri_horner(quantized, model, points))
    else:
        wrapped = io.SparseLut(model.grid, quantized, *model.tables())
        integer = interp.apply_tetra_q16(wrapped, points)
        np.testing.assert_array_equal(integer, tetra_oracle(quantized, model, points))
    return {'continuous_nodes_unrounded': metrics(continuous, target),
        'continuous_nodes_rgb8_output': metrics(rgb8(continuous), target),
        'quantized_nodes_unrounded': metrics(quantized_continuous, target),
        'quantized_nodes_rgb8_output': metrics(integer, target),
        'independent_integer_oracle_mismatches': 0,
        'float_round_vs_integer_rgb8_mismatching_channels': int(np.count_nonzero(rgb8(quantized_continuous) != integer)),
        'quantized_output_sha256': array_sha(integer)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=ROOT/'experiments/velvia-matched-operators-v1.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.plan = args.plan.resolve()
    if args.output.exists():
        raise ValueError('不覆盖已冻结诊断')
    plan = json.loads(args.plan.read_text(encoding='utf-8'))
    paths = {name: checked(spec) for name, spec in plan['inputs'].items()}
    library = checked(plan['trainer'])
    os.environ['JSHC_FULL_FIT_LIB'] = str(library)
    fingerprint = fullfit.trainer_fingerprint()
    if (fingerprint['abi_version'] != plan['trainer']['abi']
            or fingerprint['embedded_source_fingerprint'] != plan['trainer']['embedded_source_fingerprint']):
        raise ValueError('原生完整域组装器身份不同')
    model = io.load_sparse(paths['model'], competition=True)
    grid = np.load(paths['grid'])
    if not np.array_equal(model.grid, grid) or not all(
            np.array_equal(a, b) for a, b in zip(model.tables(), io.axis_tables(grid))):
        raise ValueError('小数网格不能再现基线权威idx/frac，不能作匹配比较')
    table = io.load_full(paths['table'], mmap=True)
    frozen = np.load(paths['probes'])
    if [len(frozen[name]) for name in ('uniform_keys', 'photo_keys', 'worst_keys')] != [16384, 16384, 16]:
        raise ValueError('不是原固定32768+16探针')
    files = [Path(__file__), args.plan, *[ROOT/'python/lutlab'/name for name in
        ('fit.py', 'fullfit.py', 'io.py', 'interp.py', 'support_certificate.py', 'study_provenance.py')],
        *[ROOT/name for name in fullfit.NATIVE_SOURCES]]
    source_sha = {p.relative_to(ROOT).as_posix(): digest(p) for p in files}
    args.output.mkdir(parents=True)
    run = {'plan': plan, 'plan_sha256': digest(args.plan), 'source_sha256': source_sha,
        'environment': study_provenance.environment_fingerprint(), 'trainer': fingerprint,
        'input_sha256': {name: digest(path) for name, path in paths.items()}}
    run['identity_sha256'] = study_provenance.identity_digest(run)
    (args.output/'run.json').write_text(json.dumps(run, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(ROOT).as_posix())
    basis, integer_basis = basis_tables(*model.tables(), model.m)
    inverses = [np.linalg.pinv(b, rcond=1e-14) for b in basis]
    tri = contract64(table, inverses)
    rhs = contract64(table, [b.T for b in basis])
    grams = [b.T@b for b in basis]
    gram_margins_q32 = [int(np.min(2*np.diag(q.T@q)-np.sum(np.abs(q.T@q), axis=1))) for q in integer_basis]
    if min(gram_margins_q32) <= 0:
        raise AssertionError('三线性轴Gram未得到正Gershgorin下界，不能给当前精确残差界')
    tri_lower = float(np.prod([margin/float(io.ONE**2) for margin in gram_margins_q32])/64)
    tri_residual = (contract64(tri, grams)-rhs).reshape(-1, 3)/64
    tri_report = {'solver': 'float64_Q16_axis_SVD_pseudoinverse_tensor_contraction',
        'basis_conditions': [float(np.linalg.cond(b)) for b in basis],
        'basis_left_inverse_maximum_error': max(float(np.max(np.abs(p@b-np.eye(model.m)))) for p, b in zip(inverses, basis)),
        'gram_integer_gershgorin_margins_q32': gram_margins_q32,
        'hessian_lower_bound_scaled': tri_lower,
        'normal_residual_norm': np.linalg.norm(tri_residual, axis=0).tolist(),
        'mean_squared_objective_gap_upper_bound': float(64*np.sum(tri_residual**2)/(tri_lower*256**3))}
    print('三线性float64匹配LS完成', flush=True)
    H, b, assembly = fullfit.normal_equations(table, grid, plan['trainer']['threads'])
    settings = plan['tetra_solver']
    helper_report = {}
    initial = fit.solve_spd(H, b, tri.reshape(-1, 3), lam=settings['helper_lambda'],
        tol=settings['helper_tolerance'], maxiter=settings['maximum_iterations_each_solve'], diagnostics=helper_report)
    tetra, raw_reports = np.empty_like(initial), []
    preconditioner = sp.diags(1/H.diagonal())
    for channel in range(3):
        count = [0]
        def callback(_):
            count[0] += 1
        tetra[:, channel], info = spla.cg(H, b[:, channel], x0=initial[:, channel], M=preconditioner,
            rtol=settings['raw_cg_tolerance'], maxiter=settings['maximum_iterations_each_solve'], callback=callback)
        residual = H@tetra[:, channel]-b[:, channel]
        relative = float(np.linalg.norm(residual)/np.linalg.norm(b[:, channel]))
        if info != 0 or not np.all(np.isfinite(tetra[:, channel])) or relative > 1e-12:
            raise AssertionError('原始无正则完整域正规方程未达到冻结残差要求')
        raw_reports.append({'channel': channel, 'info': int(info), 'iterations': count[0],
                            'relative_residual': relative, 'residual_norm': float(np.linalg.norm(residual))})
    tetra = tetra.reshape(model.nodes.shape)
    tetra_residual = H@tetra.reshape(-1, 3)-b
    tetra_report = {'assembly': assembly, 'helper_regularized_warmup': helper_report,
        'effective_final_regularization': 0., 'raw_cg': raw_reports,
        'mean_squared_objective_gap_upper_bound': float(64*np.sum(tetra_residual**2)/
            (assembly['data_hessian_eigenvalue_lower_bound']*256**3))}
    target_squared = float(sum(int(value) for value in assembly['target_squared_sum_rgb']))
    for kind, nodes, moment, h_times, record in (
            ('tri', tri, rhs, contract64(tri, grams), tri_report),
            ('tetra', tetra, b*64, (H@tetra.reshape(-1, 3)).reshape(tetra.shape)*64, tetra_report)):
        record['unrounded_uniform_cube_mse_from_normal_moments'] = float(
            (target_squared-2*np.sum(nodes*moment.reshape(nodes.shape))+np.sum(nodes*h_times))/256**3)
        record['continuous_node_min'] = float(nodes.min())
        record['continuous_node_max'] = float(nodes.max())
        record['node_channels_outside_rgb8'] = int(np.count_nonzero((nodes < 0) | (nodes > 255)))
    print('四面体原始无正则匹配LS完成', flush=True)
    results = {}
    stream = np.memmap(paths['stream'], np.uint8, 'r', shape=(256**3, 3))
    for name in ('uniform_keys', 'photo_keys', 'worst_keys'):
        keys = frozen[name].astype(np.int64)
        points = np.column_stack((keys >> 16, (keys >> 8) & 255, keys & 255)).astype(np.uint8)
        target = table[points[:, 0], points[:, 1], points[:, 2]]
        reference = interp.apply_tetra_q16(model, points)
        np.testing.assert_array_equal(reference, stream[keys])
        results[name] = {'rows': len(points), 'points_sha256': array_sha(points),
            'matched_tetra': evaluate(tetra, model, points, target, 'tetra'),
            'matched_tri': evaluate(tri, model, points, target, 'tri'),
            'existing_2dd_different_objective': metrics(reference, target), 'baseline_stream_mismatches': 0}
    np.savez_compressed(args.output/'matched-nodes.npz', tetra_float64=tetra, tri_float64=tri,
                        tetra_rgb8=rgb8(tetra), tri_rgb8=rgb8(tri), grid=grid, idx=model.tables()[0], frac=model.tables()[1])
    if source_sha != {p.relative_to(ROOT).as_posix(): digest(p) for p in files} or fullfit.trainer_fingerprint() != fingerprint:
        raise ValueError('匹配诊断过程中数值源码或原生库改变')
    result = {'run_identity': run['identity_sha256'], 'solvers': {'tetra': tetra_report, 'tri': tri_report},
        'evaluation': results, 'nodes_sha256': digest(args.output/'matched-nodes.npz'),
        'limits': plan['limits'], 'interpretation': '仅完整均匀L2的连续近似最优与固定探针；RGB8量化非整数最优，旧2dd目标不同；无新full/100图或性能结果'}
    (args.output/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'solvers': {'tri': tri_report, 'tetra_raw': raw_reports}, 'evaluation': results}, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
