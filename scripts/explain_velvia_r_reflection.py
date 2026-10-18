"""唯一R轴反射的匹配L2诊断；先矩目标门槛，达到后才评价原冻结探针。"""
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
from lutlab import fullfit, interp, io, study_provenance, support_certificate
from prove_velvia_fixed_tetra_bound import raw_moments


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def array_sha(array):
    return hashlib.sha256(memoryview(np.ascontiguousarray(array))).hexdigest()


def checked(spec):
    path = ROOT/spec['path']
    if digest(path) != spec['sha256']:
        raise ValueError(f'冻结输入SHA不同：{path}')
    return path


def rgb8(values):
    return np.clip(np.floor(values+.5), 0, 255).astype(np.uint8)


def metrics(prediction, target):
    error = prediction.astype(np.float64)-target.astype(np.float64)
    distance_squared = np.sum(error*error, axis=1)
    distance = np.sqrt(distance_squared)
    return {'mean': float(distance.mean()), 'rms': float(np.sqrt(distance_squared.mean())),
            'p99': float(np.percentile(distance, 99)), 'max': float(distance.max())}


def oracle(model, points):
    """独立比较器排序和uint64累加，支持降序idx，不调用interp索引生成。"""
    idx, frac = model.tables()
    cell = [idx[a, points[:, a]].astype(np.int64) for a in range(3)]
    base = (cell[0]*model.m+cell[1])*model.m+cell[2]
    f = np.column_stack([frac[a, points[:, a]] for a in range(3)]).astype(np.int64)
    stride = np.tile(np.array([model.m**2, model.m, 1], np.int64), (len(points), 1))
    for a, b in ((0, 1), (1, 2), (0, 1)):
        swap = f[:, a] < f[:, b]
        f[swap, a], f[swap, b] = f[swap, b].copy(), f[swap, a].copy()
        stride[swap, a], stride[swap, b] = stride[swap, b].copy(), stride[swap, a].copy()
    weights = np.column_stack((io.ONE-f[:, 0], f[:, 0]-f[:, 1], f[:, 1]-f[:, 2], f[:, 2])).astype(np.uint64)
    indices = np.column_stack((base, base+stride[:, 0], base+stride[:, :2].sum(axis=1), base+model.m**2+model.m+1))
    values = model.nodes.reshape(-1, 3).astype(np.uint64)[indices]
    acc = np.sum(values*weights[:, :, None], axis=1, dtype=np.uint64)
    if np.any(np.sum(weights, axis=1, dtype=np.uint64) != io.ONE) or np.any(acc > 255*io.ONE):
        raise AssertionError('折回整数oracle守恒或界失败')
    return ((acc+io.ONE//2) >> io.Q).astype(np.uint8)


def float_system(diagonal, upper, rhs, m):
    """显式使用权威raw ABI矩，绝不从镜像浮点grid重生idx/frac。"""
    size = m**3
    offsets = np.array([1, m, m+1, m*m, m*m+1, m*m+m, m*m+m+1], np.int32)
    rows = np.repeat(np.arange(size, dtype=np.int32), 7)
    columns = rows+np.tile(offsets, size)
    nonzero = upper.ravel() != 0
    if np.any(columns[nonzero] >= size):
        raise AssertionError('反射域raw矩stencil越界')
    positive = sp.coo_matrix((upper.ravel()[nonzero].astype(np.float64)*2.**-38,
        (rows[nonzero], columns[nonzero])), shape=(size, size)).tocsr()
    hessian = (positive+positive.T+sp.diags(diagonal.astype(np.float64)*2.**-38)).tocsr()
    hessian.sort_indices()
    return hessian, rhs.astype(np.float64)*2.**-22


def evaluate(candidate, floating_nodes, points, target):
    indices, weights = interp.tetra_weights(points, *candidate.tables(), candidate.m)
    continuous = np.einsum('nk,nkc->nc', weights, floating_nodes.reshape(-1, 3)[indices])
    quantized_continuous = np.einsum('nk,nkc->nc', weights,
        candidate.nodes.reshape(-1, 3).astype(np.float64)[indices])
    actual = interp.apply_tetra_q16(candidate, points)
    independent = oracle(candidate, points)
    if not np.array_equal(actual, independent):
        raise AssertionError('折回模型NumPy整数映射不同于独立uint64 oracle')
    return {'continuous_nodes_unrounded': metrics(continuous, target),
        'continuous_nodes_rgb8_output': metrics(rgb8(continuous), target),
        'quantized_nodes_unrounded': metrics(quantized_continuous, target),
        'quantized_nodes_rgb8_output': metrics(actual, target),
        'independent_uint64_oracle_mismatching_channels': 0,
        'float_round_vs_integer_mismatching_channels': int(np.count_nonzero(rgb8(quantized_continuous) != actual)),
        'quantized_output_sha256': array_sha(actual)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=ROOT/'experiments/velvia-r-reflection-v1.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.plan, args.output = args.plan.resolve(), args.output.resolve()
    if args.output.exists():
        raise ValueError('不覆盖已冻结研究')
    plan = json.loads(args.plan.read_text(encoding='utf-8'))
    paths = {key: checked(spec) for key, spec in plan['inputs'].items()}
    os.environ['JSHC_FULL_FIT_LIB'] = str(checked(plan['trainer']))
    trainer = fullfit.trainer_fingerprint()
    if (trainer['abi_version'] != plan['trainer']['abi']
            or trainer['embedded_source_fingerprint'] != plan['trainer']['embedded_source_fingerprint']):
        raise ValueError('反射研究的库ABI或来源不同')
    model = io.load_sparse(paths['model'], competition=True)
    grid = np.load(paths['grid'])
    if not np.array_equal(grid, model.grid) or not all(np.array_equal(a, b)
            for a, b in zip(model.tables(), io.axis_tables(grid))):
        raise ValueError('原始小数网格/权威坐标不是冻结2dd设计')
    matched = json.loads(paths['matched_results'].read_text(encoding='utf-8'))
    baseline_mse = matched['solvers']['tetra']['unrounded_uniform_cube_mse_from_normal_moments']
    if baseline_mse != plan['gate']['reference_mse']:
        raise ValueError('matched原标准体对角线MSE不同')
    frozen_nodes = np.load(paths['matched_nodes'])
    if any(not np.array_equal(frozen_nodes[name], value) for name, value in
            (('grid', grid), ('idx', model.tables()[0]), ('frac', model.tables()[1]))):
        raise ValueError('matched暖启动的原设计不同')
    idx, frac = [a.copy() for a in model.tables()]
    mirrored_idx, mirrored_frac = idx.copy(), frac.copy()
    mirrored_idx[0] = (model.m-2-idx[0, ::-1].astype(np.int64)).astype(np.uint8)
    mirrored_frac[0] = (io.ONE-frac[0, ::-1].astype(np.int64)).astype(np.uint32)
    mirrored_grid = grid.copy()
    mirrored_grid[0] = 255.-grid[0, ::-1]
    if (np.any(np.diff(mirrored_idx.astype(np.int64), axis=1) < 0)
            or np.any(np.diff(mirrored_idx.astype(np.int64)*io.ONE+mirrored_frac, axis=1) < 0)):
        raise ValueError('反射域坐标不非降，禁止原生组装')
    reflected = io.SparseLut(mirrored_grid, model.nodes[::-1].copy(), mirrored_idx, mirrored_frac)
    io.validate_sparse(reflected, competition=True)
    certificate = support_certificate.certify(mirrored_grid, mirrored_idx, mirrored_frac)
    files = [Path(__file__), args.plan, ROOT/'scripts/prove_velvia_fixed_tetra_bound.py',
        *[ROOT/'python/lutlab'/name for name in ('fullfit.py', 'io.py', 'interp.py', 'support_certificate.py', 'study_provenance.py')],
        *[ROOT/name for name in fullfit.NATIVE_SOURCES]]
    source = {p.relative_to(ROOT).as_posix(): digest(p) for p in files}
    args.output.mkdir(parents=True)
    run = {'plan': plan, 'plan_sha256': digest(args.plan), 'source_sha256': source,
        'environment': study_provenance.environment_fingerprint(), 'trainer': trainer,
        'input_sha256': {key: digest(path) for key, path in paths.items()},
        'derived_axis_tables_sha256': hashlib.sha256(mirrored_idx.tobytes()+mirrored_frac.tobytes()).hexdigest(),
        'scope': '唯一R反射，先连续全域矩MSE门槛；触发后才固定探针，不运行native像素后端'}
    run['identity_sha256'] = study_provenance.identity_digest(run)
    (args.output/'run.json').write_text(json.dumps(run, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(ROOT).as_posix())
    table = io.load_full(paths['table'], mmap=True)
    reflected_table = np.ascontiguousarray(table[::-1, :, :])
    diagonal, upper, rhs, metadata = raw_moments(reflected_table, reflected, trainer)
    raw_hash = hashlib.sha256()
    for array in (diagonal, upper, rhs, metadata[4:]):
        raw_hash.update(memoryview(array))
    if metadata[4:].tolist() != matched['solvers']['tetra']['assembly']['target_squared_sum_rgb']:
        raise AssertionError('R反射应保持全域参考平方和')
    if sum(int(v) for v in diagonal)+2*sum(int(v) for v in upper.ravel()) != (256**3)*io.ONE**2:
        raise AssertionError('反射raw矩的完整域常量守恒失败')
    hessian, b = float_system(diagonal, upper, rhs, model.m)
    preconditioner = sp.diags(1/hessian.diagonal())
    warm = frozen_nodes['tetra_float64'][::-1].reshape(-1, 3)
    solution, diagnostics = np.empty_like(warm), []
    settings = plan['solver']
    for channel in range(3):
        count = [0]
        def callback(_):
            count[0] += 1
        solution[:, channel], info = spla.cg(hessian, b[:, channel], x0=warm[:, channel],
            M=preconditioner, rtol=settings['rtol'], maxiter=settings['maximum_iterations'], callback=callback)
        residual = hessian@solution[:, channel]-b[:, channel]
        relative = float(np.linalg.norm(residual)/np.linalg.norm(b[:, channel]))
        if info != 0 or not np.all(np.isfinite(solution[:, channel])) or relative > settings['required_relative_residual']:
            raise AssertionError('唯一反射无ridge CG未达到冻结残差要求，停止不换方案')
        diagnostics.append({'channel': channel, 'info': int(info), 'iterations': count[0],
            'relative_residual': relative, 'residual_norm': float(np.linalg.norm(residual))})
    mse = float((sum(int(v) for v in metadata[4:])-2*np.sum(solution*b)*64
        +np.sum(solution*(hessian@solution))*64)/256**3)
    reduction = 1.-mse/baseline_mse
    passed = mse <= (1.-plan['gate']['required_relative_reduction'])*baseline_mse
    floating_nodes = solution.reshape(model.nodes.shape)
    # 元数据float32存储可以舍入；函数始终只使用显式派生权威表。
    stored_grid = mirrored_grid.astype(np.float32).astype(np.float64)
    folded_idx, folded_frac = mirrored_idx.copy(), mirrored_frac.copy()
    folded_idx[0], folded_frac[0] = mirrored_idx[0, ::-1], mirrored_frac[0, ::-1]
    np.savez_compressed(args.output/'reflection-nodes.npz', nodes_float64=floating_nodes, nodes_rgb8=rgb8(floating_nodes),
        ideal_mirrored_grid=mirrored_grid, stored_grid=stored_grid, reflected_idx=mirrored_idx,
        reflected_frac=mirrored_frac, folded_idx=folded_idx, folded_frac=folded_frac)
    np.savez_compressed(args.output/'raw-integer-moments.npz', diagonal=diagonal, upper=upper, rhs=rhs, metadata=metadata)
    evaluation, slut = {}, None
    if passed:
        candidate = io.SparseLut(stored_grid, rgb8(floating_nodes), folded_idx, folded_frac)
        io.validate_sparse(candidate, competition=True)
        destination = args.output/'r-reflected-rgb8.slut'
        io.save_sparse(destination, candidate)
        saved = io.load_sparse(destination, competition=True)
        if not all(np.array_equal(a, b) for a, b in zip(candidate.tables(), saved.tables())):
            raise AssertionError('反射折回的SLUT权威表未保存')
        frozen = np.load(paths['probes'])
        if [len(frozen[name]) for name in ('uniform_keys', 'photo_keys', 'worst_keys')] != [16384, 16384, 16]:
            raise ValueError('不是原冻结32768+16探针')
        stream = np.memmap(paths['stream'], np.uint8, 'r', shape=(256**3, 3))
        for name in ('uniform_keys', 'photo_keys', 'worst_keys'):
            keys = frozen[name].astype(np.int64)
            points = np.column_stack((keys >> 16, (keys >> 8) & 255, keys & 255)).astype(np.uint8)
            target = table[points[:, 0], points[:, 1], points[:, 2]]
            reflected_points = points.copy(); reflected_points[:, 0] = 255-points[:, 0]
            direct_index, direct_weight = interp.tetra_index_weights_q(points, folded_idx, folded_frac, model.m)
            mirror_index, mirror_weight = interp.tetra_index_weights_q(reflected_points, mirrored_idx, mirrored_frac, model.m)
            if not np.array_equal(direct_index, mirror_index) or not np.array_equal(direct_weight, mirror_weight):
                raise AssertionError('折回坐标与反射输入域不是同一权威算子')
            evaluation[name] = {'rows': len(points), 'points_sha256': array_sha(points),
                'reflected': evaluate(saved, floating_nodes, points, target),
                'matched_standard_reference': matched['evaluation'][name]['matched_tetra'],
                'existing_2dd_different_objective': metrics(stream[keys], target),
                'folded_vs_reflected_design_mismatches': 0}
        slut = {'path': destination.name, 'sha256': digest(destination), 'bytes': destination.stat().st_size,
            'same_file_length_as_baseline': destination.stat().st_size == paths['model'].stat().st_size,
            'local_format_valid': True, 'native_validation_performed': False, 'official_contract_confirmed': False}
    if source != {p.relative_to(ROOT).as_posix(): digest(p) for p in files} or fullfit.trainer_fingerprint() != trainer:
        raise ValueError('唯一反射研究期间来源或库改变')
    regenerated = io.axis_tables(mirrored_grid)
    result = {'run_identity': run['identity_sha256'], 'assembly_calls': 1, 'native_metadata': metadata.tolist(),
        'integer_system_sha256': raw_hash.hexdigest(), 'reflected_table_array_sha256': array_sha(reflected_table),
        'support_certificate': certificate, 'solver': diagnostics, 'effective_regularization': 0.,
        'continuous_uniform_mse_from_normal_moments': mse, 'matched_standard_mse': baseline_mse,
        'relative_reduction': reduction, 'gate_passed': bool(passed),
        'gate_threshold_mse': (1.-plan['gate']['required_relative_reduction'])*baseline_mse,
        'continuous_node_min': float(floating_nodes.min()), 'continuous_node_max': float(floating_nodes.max()),
        'continuous_node_channels_outside_rgb8': int(np.count_nonzero((floating_nodes < 0) | (floating_nodes > 255))),
        'regenerated_grid_idx_mismatches': int(np.count_nonzero(regenerated[0] != mirrored_idx)),
        'regenerated_grid_frac_mismatches': int(np.count_nonzero(regenerated[1] != mirrored_frac)),
        'mirrored_grid_float32_maximum_change': float(np.max(np.abs(mirrored_grid-stored_grid))),
        'evaluation': evaluation, 'folded_rgb8_model': slut,
        'artifact_sha256': {name: digest(args.output/name) for name in ('reflection-nodes.npz', 'raw-integer-moments.npz', 'measured-source.zip')},
        'limits': plan['limits'],
        'interpretation': '连续矩MSE为浮点近似LS诊断，无区间舍入证书；probe及SLUT只在20%门槛触发后产生，native尚未验收'}
    (args.output/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'mse': mse, 'reference': baseline_mse, 'relative_reduction': reduction, 'gate_passed': bool(passed),
        'evaluation': evaluation, 'folded_rgb8_model': slut}, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
