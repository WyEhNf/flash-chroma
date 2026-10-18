"""唯一Q16三次Lagrange基：全域L2矩达到固定门槛才评价旧探针。"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import io, study_provenance


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def array_sha(array):
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def checked(spec):
    path = ROOT/spec['path']
    if digest(path) != spec['sha256']:
        raise ValueError(f'输入SHA不同：{path}')
    return path


def contract64(table, matrices):
    """沿用matched阶段的固定float64张量收缩顺序，未使用旧float32 contract。"""
    x = np.tensordot(matrices[0], np.asarray(table, np.float64), axes=(1, 0))
    x = np.tensordot(matrices[1], x, axes=(1, 1))
    x = np.tensordot(matrices[2], x, axes=(1, 2))
    return np.ascontiguousarray(x.transpose(2, 1, 0, 3))


def cubic_basis(model):
    idx, frac = model.tables()
    start = np.empty((3, 256), np.int32)
    weights = np.empty((3, 256, 4), np.int64)
    maximum_errors = [Fraction(0)]*4
    denominator = 6*io.ONE**2
    for axis in range(3):
        for code in range(256):
            i, f = int(idx[axis, code]), int(frac[axis, code])
            s = min(max(i-1, 0), model.m-4)
            t, q = (i-s)*io.ONE+f, io.ONE
            numerators = [-(t-q)*(t-2*q)*(t-3*q), 3*t*(t-2*q)*(t-3*q),
                          -3*t*(t-q)*(t-3*q), t*(t-q)*(t-2*q)]
            if sum(numerators) != denominator*q or not 0 <= s <= model.m-4:
                raise AssertionError('有理Lagrange常量或stencil不合法')
            row = [(2*n+denominator)//(2*denominator) for n in numerators[:3]]
            row.append(q-sum(row))
            if sum(row) != q:
                raise AssertionError('Q16常量守恒失败')
            for channel in range(4):
                error = Fraction(abs(row[channel]*denominator-numerators[channel]), denominator)
                maximum_errors[channel] = max(maximum_errors[channel], error)
                if error > Fraction(1 if channel < 3 else 3, 2):
                    raise AssertionError('有理权重量化超出预声明界')
            start[axis, code], weights[axis, code] = s, row
    if (np.any(start < 0) or np.any(start+3 >= model.m) or not np.any(weights < 0)
            or not np.all(weights.sum(axis=2) == io.ONE)):
        raise AssertionError('索引、负权重或常量守恒未覆盖')
    basis, integer_basis = [], []
    for axis in range(3):
        b = np.zeros((256, model.m), np.int64)
        for column in range(4):
            b[np.arange(256), start[axis]+column] += weights[axis, :, column]
        basis.append(b.astype(np.float64)/io.ONE)
        integer_basis.append(b)
    maximum_l1 = [int(np.abs(weights[a]).sum(axis=1).max()) for a in range(3)]
    bound = 255
    for value in maximum_l1:
        bound *= value
    if bound+(1 << 47) >= 1 << 63:
        raise AssertionError('显式64顶点signed int64 Q48累加器不安全')
    report = {'enumerated_axis_rows': 768, 'stencil_indices_in_bounds': True,
        'constant_q16_sum': io.ONE, 'negative_weights_retained': int(np.count_nonzero(weights < 0)),
        'maximum_weight_quantization_errors_q16_units': [float(e) for e in maximum_errors],
        'maximum_weight_error_ratios': [[e.numerator, e.denominator] for e in maximum_errors],
        'maximum_axis_l1_q16': maximum_l1, 'maximum_axis_l1_real': [v/io.ONE for v in maximum_l1],
        'signed_accumulator_absolute_bound': bound, 'bound_including_half_up_bias': bound+(1 << 47),
        'signed_int64_limit': (1 << 63)-1,
        'weight_sha256': array_sha(weights), 'start_sha256': array_sha(start),
        'local_coordinate': '有效索引i+frac/ONE，不是物理非均匀结点的三次基'}
    return start, weights, basis, integer_basis, report


def node_data(start, weights, points):
    return ([start[a, points[:, a]] for a in range(3)],
            [weights[a, points[:, a]] for a in range(3)])


def float_output(nodes, start, weights, points):
    index, q = node_data(start, weights, points)
    out = np.zeros((len(points), 3), np.float64)
    f = [a.astype(np.float64)/io.ONE for a in q]
    for dr in range(4):
        for dg in range(4):
            for db in range(4):
                w = f[0][:, dr]*f[1][:, dg]*f[2][:, db]
                out += w[:, None]*nodes[index[0]+dr, index[1]+dg, index[2]+db]
    return out


def integer_output(nodes, start, weights, points):
    """显式64个signed Q48权重；负中间量只在最后half-up并clip。"""
    index, q = node_data(start, weights, points)
    acc, total = np.zeros((len(points), 3), np.int64), np.zeros(len(points), np.int64)
    for dr in range(4):
        for dg in range(4):
            for db in range(4):
                w = q[0][:, dr]*q[1][:, dg]*q[2][:, db]
                acc += w[:, None]*nodes[index[0]+dr, index[1]+dg, index[2]+db].astype(np.int64)
                total += w
    if not np.all(total == 1 << 48):
        raise AssertionError('64顶点的Q48常量和不成立')
    return np.clip((acc+(1 << 47)) >> 48, 0, 255).astype(np.uint8)


def integer_horner(nodes, start, weights, points):
    """独立逐轴整数收缩，所有中间量保留原整数尺度而不舍入。"""
    index, q = node_data(start, weights, points)
    along_b = []
    for db in range(4):
        along_g = np.zeros((len(points), 3), np.int64)
        for dg in range(4):
            along_r = np.zeros((len(points), 3), np.int64)
            for dr in range(4):
                along_r += q[0][:, dr, None]*nodes[index[0]+dr, index[1]+dg, index[2]+db].astype(np.int64)
            along_g += q[1][:, dg, None]*along_r
        along_b.append(along_g)
    acc = sum(q[2][:, db, None]*along_b[db] for db in range(4))
    return np.clip((acc+(1 << 47)) >> 48, 0, 255).astype(np.uint8)


def rgb8(values):
    return np.clip(np.floor(values+.5), 0, 255).astype(np.uint8)


def metrics(prediction, target):
    squared = np.sum((prediction.astype(np.float64)-target.astype(np.float64))**2, axis=1)
    distance = np.sqrt(squared)
    return {'mean': float(distance.mean()), 'rms': float(np.sqrt(squared.mean())),
            'p99': float(np.percentile(distance, 99)), 'max': float(distance.max())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=ROOT/'experiments/velvia-cubic-lagrange-v1.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.plan = args.plan.resolve()
    if args.output.exists():
        raise ValueError('不覆盖既有唯一基实验')
    plan = json.loads(args.plan.read_text(encoding='utf-8'))
    paths = {name: checked(spec) for name, spec in plan['inputs'].items()}
    matched_path = checked(plan['matched_reference'])
    matched = json.loads(matched_path.read_text(encoding='utf-8'))
    if matched['run_identity'] != plan['matched_run_identity']:
        raise ValueError('matched参照身份不同')
    model = io.load_sparse(paths['model'], competition=True)
    grid = np.load(paths['grid'])
    if not np.array_equal(grid, model.grid) or not all(
            np.array_equal(a, b) for a, b in zip(model.tables(), io.axis_tables(grid))):
        raise ValueError('权威Q16设计不同')
    source_files = [Path(__file__), args.plan, ROOT/'python/lutlab/io.py', ROOT/'python/lutlab/study_provenance.py']
    source_sha = {p.relative_to(ROOT).as_posix(): digest(p) for p in source_files}
    args.output.mkdir(parents=True)
    run = {'plan': plan, 'environment': study_provenance.environment_fingerprint(),
        'source_sha256': source_sha, 'input_sha256': {name: digest(p) for name, p in paths.items()},
        'matched_results_sha256': digest(matched_path)}
    run['identity_sha256'] = study_provenance.identity_digest(run)
    (args.output/'run.json').write_text(json.dumps(run, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in source_files:
            archive.write(path, path.relative_to(ROOT).as_posix())
    start, weights, basis, integer_basis, verification = cubic_basis(model)
    print('768行有理权重、常量与signed int64绝对界通过', flush=True)
    table = io.load_full(paths['table'], mmap=True)
    inverse = [np.linalg.pinv(b, rcond=1e-14) for b in basis]
    left_inverse_error = max(float(np.max(np.abs(p@b-np.eye(model.m)))) for p, b in zip(inverse, basis))
    if left_inverse_error > 1e-12:
        raise AssertionError('基矩阵没有得到完整列秩的数值左逆')
    nodes = contract64(table, inverse)
    rhs = contract64(table, [b.T for b in basis])
    grams = [b.T@b for b in basis]
    h_times = contract64(nodes, grams)
    residual = (h_times-rhs).reshape(-1, 3)/64
    target_squared = float(sum(int(v) for v in matched['solvers']['tetra']['assembly']['target_squared_sum_rgb']))
    mse = float((target_squared-2*np.sum(nodes*rhs)+np.sum(nodes*h_times))/256**3)
    if not np.isfinite(mse) or mse < 0 or not np.all(np.isfinite(nodes)):
        raise AssertionError('连续节点或全域训练MSE矩不是合法有限值')
    reference_mse = matched['solvers']['tetra']['unrounded_uniform_cube_mse_from_normal_moments']
    trigger = bool(mse <= (1-plan['trigger']['required_relative_mse_reduction'])*reference_mse)
    solver = {'solver': 'float64_Q16_axis_SVD_tensor', 'basis_conditions': [float(np.linalg.cond(b)) for b in basis],
        'basis_left_inverse_maximum_error': left_inverse_error,
        'normal_residual_norm_scaled_1over64': np.linalg.norm(residual, axis=0).tolist(),
        'unrounded_uniform_cube_mse_from_normal_moments': mse, 'matched_tetra_mse': reference_mse,
        'relative_mse_reduction': 1-mse/reference_mse, 'fixed_reduction_threshold': .2,
        'probe_evaluation_triggered': trigger,
        'continuous_node_min': float(nodes.min()), 'continuous_node_max': float(nodes.max()),
        'node_channels_outside_rgb8': int(np.count_nonzero((nodes < 0) | (nodes > 255))),
        'numeric_scope': '浮点SVD、张量收缩、矩相减与残差诊断；未提供舍入区间或严密全局证书'}
    print(json.dumps({'solver': solver}, ensure_ascii=False, indent=2), flush=True)
    quantized = rgb8(nodes)
    np.savez_compressed(args.output/'basis-and-nodes.npz', start=start, q16_weights=weights,
        nodes_float64=nodes, nodes_rgb8=quantized, grid=grid, idx=model.tables()[0], frac=model.tables()[1])
    result = {'run_identity': run['identity_sha256'], 'weight_verification': verification, 'solver': solver,
        'nodes_file_sha256': digest(args.output/'basis-and-nodes.npz'),
        'capacity': {'baseline_slut_bytes': paths['model'].stat().st_size,
            'candidate_rgb8_node_payload_bytes': quantized.nbytes,
            'candidate_slut_created': False, 'operator_vertices': 64,
            'scope': '节点容量相同，不代表旧SLUT语义或tetra/tri_float后端支持本显式算子'},
        'evaluation': {}, 'limits': plan['limits']}
    if trigger:
        frozen = np.load(paths['probes'])
        if [len(frozen[name]) for name in ('uniform_keys', 'photo_keys', 'worst_keys')] != [16384, 16384, 16]:
            raise ValueError('固定探针身份不同')
        for name in ('uniform_keys', 'photo_keys', 'worst_keys'):
            keys = frozen[name].astype(np.int64)
            points = np.column_stack((keys >> 16, (keys >> 8) & 255, keys & 255)).astype(np.uint8)
            target = table[points[:, 0], points[:, 1], points[:, 2]]
            continuous = float_output(nodes, start, weights, points)
            quantized_continuous = float_output(quantized, start, weights, points)
            integer = integer_output(quantized, start, weights, points)
            np.testing.assert_array_equal(integer, integer_horner(quantized, start, weights, points))
            result['evaluation'][name] = {'rows': len(points), 'points_sha256': array_sha(points),
                'continuous_nodes_unrounded': metrics(continuous, target),
                'continuous_nodes_rgb8_output': metrics(rgb8(continuous), target),
                'quantized_nodes_unrounded': metrics(quantized_continuous, target),
                'quantized_nodes_rgb8_output': metrics(integer, target),
                'continuous_output_channels_outside_rgb8': int(np.count_nonzero((continuous < 0) | (continuous > 255))),
                'quantized_unrounded_output_channels_outside_rgb8': int(np.count_nonzero((quantized_continuous < 0) | (quantized_continuous > 255))),
                'independent_signed_integer_mismatches': 0,
                'float_round_vs_integer_rgb8_mismatching_channels': int(np.count_nonzero(rgb8(quantized_continuous) != integer)),
                'quantized_output_sha256': array_sha(integer)}
    else:
        result['stop'] = '未达预声明20%完整均匀L2矩改善，不评价探针、不生成SLUT'
    if source_sha != {p.relative_to(ROOT).as_posix(): digest(p) for p in source_files}:
        raise ValueError('研究过程中数值源码改变')
    (args.output/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'weight_verification': verification, 'evaluation': result['evaluation'],
                      'stop': result.get('stop')}, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
