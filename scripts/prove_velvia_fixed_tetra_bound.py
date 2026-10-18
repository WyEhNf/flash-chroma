"""以同SHA整数正规矩和有理残差给固定坐标四面体的表达能力下界。"""
from __future__ import annotations

import argparse
import ctypes as ct
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
from lutlab import fullfit, io, study_provenance


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


def rational_record(value):
    return {'numerator': str(value.numerator), 'denominator': str(value.denominator),
            'decimal_display_only': float(value)}


def q20_exact(value):
    """精确读取IEEE float的有理值，再half-up到Q20，不依赖浮点乘法/取整。"""
    numerator, denominator = float(value).as_integer_ratio()
    numerator *= 1 << 20
    return (2*numerator+denominator)//(2*denominator)


def integer_certificate(model, grid, output):
    """独立标量排序构造互异见证方阵；Python整数计算对称Gershgorin余量。"""
    m, (idx, frac) = model.m, model.tables()
    levels = np.rint(grid).astype(np.int64)
    if np.any(levels < 0) or np.any(levels > 255) or np.any(np.diff(levels, axis=1) <= 0):
        raise ValueError('最近整数见证重复或越界')
    points = np.stack(np.meshgrid(*levels, indexing='ij'), -1).reshape(-1, 3).astype(np.uint8)
    size = m**3
    diagonal, column = [0]*size, [0]*size
    indices, weights = np.empty((size, 4), np.uint32), np.empty((size, 4), np.uint32)
    for row, point in enumerate(points):
        coordinates = [int(frac[a, int(point[a])]) for a in range(3)]
        order = sorted(range(3), key=lambda a: (-coordinates[a], a))
        base = (int(idx[0, int(point[0])])*m+int(idx[1, int(point[1])]))*m+int(idx[2, int(point[2])])
        stride = [m*m, m, 1]
        vertex = [base, base+stride[order[0]], base+stride[order[0]]+stride[order[1]], base+m*m+m+1]
        x, y, z = [coordinates[a] for a in order]
        weight = [io.ONE-x, x-y, y-z, z]
        if min(weight) < 0 or sum(weight) != io.ONE or min(vertex) < 0 or max(vertex) >= size:
            raise AssertionError('见证四面体不合法')
        for index, value in zip(vertex, weight):
            column[index] += value
            if index == row:
                diagonal[row] += value
        indices[row], weights[row] = vertex, weight
    margins = [4*d-io.ONE-c for d, c in zip(diagonal, column)]
    minimum = min(margins)
    if minimum <= 0:
        raise ValueError('整数见证的正定充分证书失败')
    eigenvalue = Fraction(minimum**2, 64*(2*io.ONE)**2)
    # 保留未约分的历史表示，同时记录等值精确Fraction。
    report = {'method': 'nearest_rgb_symmetric_gershgorin_q16', 'witness_count': size,
        'witness_rgb_sha256': array_sha(points),
        'axis_tables_sha256': hashlib.sha256(idx.tobytes()+frac.tobytes()).hexdigest(),
        'minimum_twice_symmetric_margin_q16': minimum,
        'hessian_eigenvalue_lower_bound_ratio': [minimum**2, 64*(2*io.ONE)**2],
        'lambda_exact': rational_record(eigenvalue),
        'proof': '见证A的对称部分最小余量为minimum/(2Q)，故sigma_min(A)>=minimum/(2Q)；全域H>=A^T A/64'}
    np.savez_compressed(output/'witness-certificate.npz', points=points, indices=indices, weights=weights,
                        margins=np.asarray(margins, np.int64), grid=grid, idx=idx, frac=frac)
    return report, eigenvalue


def raw_moments(table, model, trainer):
    """只调用一次已验证C ABI，保留uint64；不创建float正规方程或执行求解。"""
    library, _ = fullfit._load(str(fullfit.resolve_library()), trainer['library_sha256'])
    idx, frac = [np.ascontiguousarray(a) for a in model.tables()]
    table = np.ascontiguousarray(table)
    size = model.m**3
    diagonal = np.empty(size, np.uint64)
    upper, rhs = np.empty((size, 7), np.uint64), np.empty((size, 3), np.uint64)
    metadata, error = np.empty(7, np.uint64), ct.create_string_buffer(1024)
    def pointer(a, kind):
        return a.ctypes.data_as(ct.POINTER(kind))
    status = library.jshc_full_normals_v1(pointer(table, ct.c_uint8), table.nbytes,
        pointer(idx, ct.c_uint8), pointer(frac, ct.c_uint32), model.m, 4,
        pointer(diagonal, ct.c_uint64), diagonal.size, pointer(upper, ct.c_uint64), upper.size,
        pointer(rhs, ct.c_uint64), rhs.size, pointer(metadata, ct.c_uint64), metadata.size, error, len(error))
    if status:
        raise RuntimeError(f'C ABI组装失败：{status} {error.value!r}')
    if (metadata[0] != 256**3 or metadata[2] != model.m-1 or metadata[3] != 1
            or not 1 <= metadata[1] <= 4):
        raise AssertionError('原始矩的完整域覆盖、ABI或线程元数据不符')
    return diagonal, upper, rhs, metadata


def exact_quadratic(diagonal, upper, rhs, target_squared, zint, m):
    """只用Python任意精度整数；对称stencil矩乘和独立二次型交叉核对。"""
    size = m**3
    z = [[int(v) for v in row] for row in zint]
    hz = [[int(diagonal[i])*z[i][c] for c in range(3)] for i in range(size)]
    quadratic_direct = sum(int(diagonal[i])*sum(v*v for v in z[i]) for i in range(size))
    offsets = (1, m, m+1, m*m, m*m+1, m*m+m, m*m+m+1)
    nonzero_edges = 0
    for i, row in enumerate(upper):
        for offset, raw in zip(offsets, row):
            value = int(raw)
            if not value:
                continue
            j = i+offset
            if j >= size:
                raise AssertionError('原始stencil上三角越界')
            for c in range(3):
                hz[i][c] += value*z[j][c]
                hz[j][c] += value*z[i][c]
            quadratic_direct += 2*value*sum(z[i][c]*z[j][c] for c in range(3))
            nonzero_edges += 1
    quadratic_product = sum(z[i][c]*hz[i][c] for i in range(size) for c in range(3))
    if quadratic_product != quadratic_direct:
        raise AssertionError('整数矩乘与独立对称二次型不一致')
    rhs_dot = sum(z[i][c]*int(rhs[i, c]) for i in range(size) for c in range(3))
    gradient = [[hz[i][c]-(int(rhs[i, c]) << 36) for c in range(3)] for i in range(size)]
    gnorm = sum(v*v for row in gradient for v in row)
    fnum = sum(z[i][c]*(gradient[i][c]-(int(rhs[i, c]) << 36)) for i in range(size) for c in range(3))
    fnum += target_squared << 72
    direct = quadratic_direct-(rhs_dot << 37)+(target_squared << 72)
    if fnum != direct:
        raise AssertionError('两种完整有理目标表达不一致')
    return {'Hnum_quadratic': str(quadratic_direct), 'bnum_dot_zint': str(rhs_dot),
        'sum_gnum_squared': str(gnorm), 'Fnum': str(fnum), 'c_raw': str(target_squared),
        'nonzero_upper_edges': nonzero_edges, 'integer_quadratic_crosscheck_equal': True}, fnum, gnorm


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=ROOT/'experiments/velvia-fixed-tetra-bound-v1.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.plan, args.output = args.plan.resolve(), args.output.resolve()
    if args.output.exists():
        raise ValueError('不覆盖已冻结证明任务')
    plan = json.loads(args.plan.read_text(encoding='utf-8'))
    paths = {name: checked(spec) for name, spec in plan['inputs'].items()}
    os.environ['JSHC_FULL_FIT_LIB'] = str(checked(plan['trainer']))
    trainer = fullfit.trainer_fingerprint()
    if (trainer['abi_version'] != plan['trainer']['abi']
            or trainer['embedded_source_fingerprint'] != plan['trainer']['embedded_source_fingerprint']):
        raise ValueError('原生库ABI或来源合同不同')
    model = io.load_sparse(paths['model'], competition=True)
    grid = np.load(paths['grid'])
    if not np.array_equal(model.grid, grid) or not all(np.array_equal(a, b)
            for a, b in zip(model.tables(), io.axis_tables(grid))):
        raise ValueError('原2dd权威坐标与原离线网格不同')
    history = json.loads(paths['matched_results'].read_text(encoding='utf-8'))
    historical = history['solvers']['tetra']['assembly']
    if historical['integer_system_sha256'] != plan['raw_integer_system_sha256']:
        raise ValueError('matched历史整数矩合同不同')
    frozen = np.load(paths['matched_nodes'])
    if any(not np.array_equal(frozen[name], value) for name, value in
            (('grid', grid), ('idx', model.tables()[0]), ('frac', model.tables()[1]))):
        raise ValueError('matched向量所用权威坐标不同')
    nodes = frozen['tetra_float64']
    if nodes.shape != model.nodes.shape or nodes.dtype != np.float64 or not np.all(np.isfinite(nodes)):
        raise ValueError('冻结连续向量形状、类型或有限性不同')
    files = [Path(__file__), args.plan, *[ROOT/'python/lutlab'/name for name in
        ('fullfit.py', 'io.py', 'interp.py', 'support_certificate.py', 'study_provenance.py')],
        *[ROOT/name for name in fullfit.NATIVE_SOURCES]]
    source = {p.relative_to(ROOT).as_posix(): digest(p) for p in files}
    args.output.mkdir(parents=True)
    run = {'plan': plan, 'plan_sha256': digest(args.plan), 'source_sha256': source,
        'environment': study_provenance.environment_fingerprint(), 'trainer': trainer,
        'input_sha256': {name: digest(path) for name, path in paths.items()},
        'scope': '只一次旧输入原始矩组装、整数见证与有理证明；无模型求解或映射/性能计时'}
    run['identity_sha256'] = study_provenance.identity_digest(run)
    (args.output/'run.json').write_text(json.dumps(run, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(ROOT).as_posix())
    certificate, eigenvalue = integer_certificate(model, grid, args.output)
    if any(certificate[key] != value for key, value in plan['certificate'].items()):
        raise AssertionError('独立整数见证证书与冻结值不同')
    if any(certificate[key] != value for key, value in historical['support_certificate'].items()
            if key in plan['certificate']):
        raise AssertionError('独立整数证书与matched历史不一致')
    diagonal, upper, rhs, metadata = raw_moments(io.load_full(paths['table'], mmap=True), model, trainer)
    raw_hash = hashlib.sha256()
    for array in (diagonal, upper, rhs, metadata[4:]):
        raw_hash.update(memoryview(array))
    if raw_hash.hexdigest() != plan['raw_integer_system_sha256']:
        raise AssertionError('再生原始整数矩SHA与matched不同')
    # 全域常量设计守恒；总量2^56远小于uint64上界，以下仍使用Python int。
    constant_sum = sum(int(v) for v in diagonal)+2*sum(int(v) for v in upper.ravel())
    if constant_sum != (256**3)*io.ONE**2 or metadata[4:].tolist() != historical['target_squared_sum_rgb']:
        raise AssertionError('全域矩常量守恒或原目标平方和不同')
    zint = np.asarray([q20_exact(v) for v in nodes.ravel()], np.int64).reshape(-1, 3)
    evidence, fnum, gnorm = exact_quadratic(diagonal, upper, rhs,
        sum(int(v) for v in metadata[4:]), zint, model.m)
    fz = Fraction(fnum, 1 << 78)
    correction = Fraction(gnorm, (1 << 116))*Fraction(1, 1)/eigenvalue
    lower = (fz-correction)*Fraction(64, 256**3)
    k = int(plan['certificate']['hessian_eigenvalue_lower_bound_ratio'][0])
    closed_form = Fraction(k*fnum-4*gnorm, k*(1 << 96))
    if lower != closed_form or eigenvalue != Fraction(k, 1 << 40):
        raise AssertionError('独立Fraction缩放与冻结闭式公式不一致')
    impossible = lower > Fraction(3, 4)
    rational_rms_point49 = lower > Fraction(136, 100)**2 and Fraction(3, 4) < Fraction(87, 100)**2
    np.savez_compressed(args.output/'raw-integer-moments.npz', diagonal=diagonal, upper=upper,
                        rhs=rhs, metadata=metadata, idx=model.tables()[0], frac=model.tables()[1])
    np.savez_compressed(args.output/'rational-vector.npz', zint_q20=zint)
    artifacts = {name: digest(args.output/name) for name in ('raw-integer-moments.npz',
        'witness-certificate.npz', 'rational-vector.npz', 'measured-source.zip')}
    if source != {p.relative_to(ROOT).as_posix(): digest(p) for p in files} or fullfit.trainer_fingerprint() != trainer:
        raise ValueError('证明过程中来源或库改变')
    result = {'run_identity': run['identity_sha256'], 'integer_system_sha256': raw_hash.hexdigest(),
        'assembly_calls': 1, 'native_metadata': metadata.tolist(), 'certificate': certificate,
        'q20_vector_array_sha256': array_sha(zint.astype('<i8', copy=False)),
        'q20_conversion': '精确float.as_integer_ratio后half-up到Q20；证据向量非可部署节点',
        'integer_evidence': evidence, 'constant_design_sum': str(constant_sum),
        'scaled_objective_at_z_exact': rational_record(fz),
        'scaled_residual_correction_exact': rational_record(correction),
        'uniform_unrounded_mse_lower_exact': rational_record(lower),
        'comparison_threshold_exact': rational_record(Fraction(3, 4)),
        'mse_lower_minus_three_quarters_exact': rational_record(lower-Fraction(3, 4)),
        'rgb8_zero_error_impossible_for_fixed_coordinates_and_legal_nodes': impossible,
        'rgb8_output_rms_lower_display_only': max(0., math.sqrt(float(lower))-math.sqrt(.75)),
        'rgb8_output_rms_strictly_above_49_over_100_by_rational_comparisons': rational_rms_point49,
        'artifact_sha256': artifacts, 'limits': plan['limits'],
        'interpretation': '整数/Fraction证明无浮点舍入证书缺口；只对指定原表/权威设计/合法凸四面体范围成立；没有新拟合、模型或终验收益'}
    if not impossible:
        result['interpretation'] = '严格下界不足3/4，不得声称不可能；按冻结规则停止'
    (args.output/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'integer_system_sha256': raw_hash.hexdigest(), 'mse_lower': rational_record(lower),
        'zero_impossible': impossible, 'rgb8_rms_display': result['rgb8_output_rms_lower_display_only'],
        'rational_rms_above_point49': rational_rms_point49}, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
