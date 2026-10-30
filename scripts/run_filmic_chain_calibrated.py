"""用统一CLI拟合四张不同原LUT，冻结后一次验证可分离链的精度和容量。"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numba
import numpy as np
from PIL import Image
from lutlab import cache, cli, curve, error_analysis as ea, io, runtime, source_lut, study_provenance
from lutlab.compatibility import write_json
from run_filmic_calibration import integer_oracle
from run_chain_error_study import colours, digest


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def checked(spec):
    path = ROOT/spec['path']
    if digest(path) != spec['sha256']:
        raise ValueError(f'冻结输入SHA不同：{path}')
    return path


def sources(plan_path):
    files = sorted((ROOT/'python/lutlab').glob('*.py'))
    files += [Path(__file__), ROOT/'scripts/run_filmic_calibration.py',
              ROOT/'scripts/run_chain_error_study.py', ROOT/'scripts/verify_separable_calibration.py', plan_path]
    return {p.relative_to(ROOT).as_posix(): digest(p) for p in files}


def model_curves(model, axes):
    from lutlab.separable_calibration import evaluate_curve
    nodes = []
    for channel, axis in enumerate(axes):
        selection = [0, 0, 0, channel]
        selection[axis] = slice(None)
        values = model.nodes[tuple(selection)]
        shape = [1, 1, 1]; shape[axis] = model.m
        if not np.array_equal(model.nodes[..., channel], np.broadcast_to(values.reshape(shape), (model.m,)*3)):
            raise ValueError('模型节点不能兑现源的通道轴关系')
        nodes.append(values)
    idx, frac = model.tables()
    return np.stack([evaluate_curve(nodes[c], idx[a], frac[a]) for c, a in enumerate(axes)], axis=1)


def compose_curves(stages):
    output = np.tile(np.arange(256, dtype=np.uint8)[:, None], (1, 3))
    dependencies = [0, 1, 2]
    for axes, values in stages:
        output = np.column_stack([values[output[:, a], c] for c, a in enumerate(axes)])
        dependencies = [dependencies[a] for a in axes]
    if len(set(dependencies)) != 3:
        raise ValueError('本先导的独立轴直方图只适用于轴置换，不能套用共享原轴的卷积')
    return dependencies, output


def generate_control(kind):
    """生成完整合法原表，等距控制只用于不让后缀吞掉首级误差。"""
    table = np.empty((256**3, 3), np.uint8)
    for start in range(0, len(table), 1 << 18):
        rgb = colours(np.arange(start, start+(1 << 18), dtype=np.int64))
        if kind == 'cycle_gbr':
            table[start:start+len(rgb)] = rgb[:, [1,2,0]]
        elif kind == 'invert_rgb':
            table[start:start+len(rgb)] = 255-rgb
        elif kind == 'swap_rg':
            table[start:start+len(rgb)] = rgb[:, [1,0,2]]
        else:
            raise ValueError('未冻结的控制生成器')
    return table.reshape(io.FULL_SHAPE)


def prepare(args, plan):
    if args.output.exists():
        raise ValueError('不覆盖已有实验')
    if len(plan['sources']) != 4 or len({s['sha256'] for s in plan['sources']}) != 4:
        raise ValueError('必须四张不同原LUT')
    checked(plan['photos']); checked(plan['executable'])
    for spec in plan['sources']:
        if 'path' in spec:
            checked(spec)
    identity = {'plan': plan, 'source_sha256': sources(args.plan),
                'environment': study_provenance.environment_fingerprint(), 'numba_threads': numba.get_num_threads()}
    run = {'identity': identity, 'identity_sha256': study_provenance.identity_digest(identity)}
    study_provenance.claim_run(args.output/'run.json', run)
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, sha in identity['source_sha256'].items():
            if digest(ROOT/name) != sha:
                raise ValueError('冻结源码时文件改变')
            archive.write(ROOT/name, name)
    source_dir = args.output/'sources'
    source_dir.mkdir()
    paths, curves, input_records = [], [], []
    for spec in plan['sources']:
        if 'generator' in spec:
            table = generate_control(spec['generator'])
            if hashlib.sha256(table.tobytes()).hexdigest() != spec['sha256']:
                raise ValueError('控制原表生成字节不符合冻结SHA')
            policy = {'generator': spec['generator'], 'scope': '完整256³ RGB8等距控制原表，非自然ISP承诺'}
        else:
            table, policy = source_lut.bake_source(checked(spec), spec)
        channels = curve.separable_channels(table)
        if channels is None or len({a for a, _ in channels}) != 3:
            raise ValueError('本链先导需要完整验证的轴可分离置换原表，失败不换来源')
        axes = [a for a, _ in channels]
        values = np.stack([v for _, v in channels], axis=1)
        curves.append((axes, values))
        path = source_dir/f"stage{spec['stage']}.lut256"
        io.save_full(path, table)
        paths.append(path)
        input_records.append({'path': str(path), 'sha256': digest(path), 'source': spec, 'channel_axes': axes,
                              'policy': policy, 'verified_source_colors': 256**3})
    if len({row['sha256'] for row in input_records}) != 4:
        raise ValueError('实际展开的四张完整原表必须不同')
    reference_axes, reference_curve = compose_curves(curves)
    np.save(args.output/'reference-curves.npy', reference_curve)
    variants = {}
    for config in plan['chains']:
        name, namespace = config['name'], args.output/config['name']
        command = [sys.executable, '-m', 'lutlab', 'fit', '--scenario', 'filmic-calibrated-chain',
                   '--mode', 'seq', '--grid', 'dp', '--method', config['method'], '--m', str(config['m']),
                   '--model-dir', str(namespace), '--inputs', *map(str, paths)]
        env = os.environ.copy()
        env.update(PYTHONPATH=str(ROOT/'python'), PYTHONUTF8='1', NUMBA_NUM_THREADS='4',
                   OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
        result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8')
        (args.output/f'{name}-fit.stdout.txt').write_text(result.stdout, encoding='utf-8')
        (args.output/f'{name}-fit.stderr.txt').write_text(result.stderr, encoding='utf-8')
        if result.returncode:
            raise RuntimeError(f'统一CLI拟合失败：{name}；已保存stdout/stderr')
        params = cli.fit_parameters(argparse.Namespace(m=config['m'], mode='seq', method=config['method'],
                                                       grid='dp', adaptive=False))
        identity = cache.build_identity(paths, params)
        entry = cache.lookup(namespace, identity)
        if entry is None:
            raise AssertionError('统一CLI未发布与当前来源一致的可复用模型')
        models = [io.load_sparse(p, competition=True) for p in entry.paths]
        stages = [(axes, model_curves(model, axes)) for model, (axes, _) in zip(models, curves)]
        from lutlab.separable_calibration import cube_metrics
        output_axes, output_curve = compose_curves(stages)
        if output_axes != reference_axes:
            raise AssertionError('参考与模型的原轴依赖不同')
        metrics = cube_metrics(output_curve, reference_curve)
        variants[name] = {'config': config, 'model_paths': [str(p) for p in entry.paths],
            'model_sha256': [digest(p) for p in entry.paths], 'serialized_bytes': sum(p.stat().st_size for p in entry.paths),
            'cache_identity_sha256': entry.manifest['identity_sha256'],
            'cache_manifest_path': str(entry.directory/'manifest.json'),
            'cache_manifest_sha256': digest(entry.directory/'manifest.json'), 'fit': entry.manifest['fit'],
            'analytic_cube': metrics, 'per_stage_exact': [bool(np.array_equal(a[1], b[1])) for a, b in zip(stages, curves)],
            'cli_command': command, 'cli_returncode': result.returncode}
        print(name, json.dumps({'analytic_cube': metrics, 'per_stage_exact': variants[name]['per_stage_exact'],
                                'bytes': variants[name]['serialized_bytes']}, ensure_ascii=False), flush=True)
    candidate = variants['calibrated17']
    nonconstant = any(len(np.unique(reference_curve[:, a])) > 1 for a in range(3))
    eligible = (all(candidate['per_stage_exact']) and nonconstant
                and candidate['analytic_cube']['mean'] < variants['baseline17']['analytic_cube']['mean'])
    result = {'run_identity': run['identity_sha256'], 'sources': input_records, 'variants': variants,
              'reference_curve_sha256': digest(args.output/'reference-curves.npy'), 'reference_axes': reference_axes,
              'reference_distinct_codes_per_channel': [len(np.unique(reference_curve[:, a])) for a in range(3)],
              'full_eligible': eligible, 'scope': plan['limits']}
    write_json(args.output/'preparation.json', result)
    print('完整验收触发：'+str(eligible), flush=True)


def load_prepared(args, plan):
    run, prepared = read(args.output/'run.json'), read(args.output/'preparation.json')
    if (run['identity_sha256'] != study_provenance.identity_digest(run['identity'])
            or prepared['run_identity'] != run['identity_sha256']
            or sources(args.plan) != run['identity']['source_sha256'] or plan != run['identity']['plan']):
        raise ValueError('冻结来源、计划或运行身份不同')
    tables = []
    for row in prepared['sources']:
        if 'path' in row['source']:
            checked(row['source'])
        elif row['source']['sha256'] != row['sha256']:
            raise ValueError('生成器原表与冻结源SHA不同')
        tables.append(io.load_full(checked(row), mmap=True))
    variants = {}
    for name, row in prepared['variants'].items():
        if digest(Path(row['cache_manifest_path'])) != row['cache_manifest_sha256']:
            raise ValueError('CLI缓存清单已改变')
        if [digest(Path(p)) for p in row['model_paths']] != row['model_sha256']:
            raise ValueError('冻结模型不同')
        variants[name] = [io.load_sparse(p, competition=True) for p in row['model_paths']]
    return run, prepared, tables, variants


def accept(args, plan):
    run, prepared, tables, models = load_prepared(args, plan)
    if (args.output/'full-results.json').exists() or not prepared['full_eligible']:
        raise ValueError('已完成或未达到冻结完整验收触发条件')
    executable = checked(plan['executable']); checked(plan['photos'])
    reference_curve = np.load(args.output/'reference-curves.npy')
    if digest(args.output/'reference-curves.npy') != prepared['reference_curve_sha256']:
        raise ValueError('解析参考曲线不同')
    results = {}
    for name, chain in models.items():
        folder = args.output/name
        path = folder/'cube.rgb'
        histogram = np.zeros(3*255**2+1, np.int64)
        prediction_sha, reference_sha = hashlib.sha256(), hashlib.sha256()
        operator = ea.Operator(chain)
        with path.open('wb') as stream:
            for start in range(0, 256**3, 1 << 17):
                rgb = colours(np.arange(start, start+(1 << 17), dtype=np.int64))
                truth = ea.exact_chain(tables, rgb)
                closed_truth = np.column_stack([reference_curve[rgb[:, a], c] for c, a in enumerate(prepared['reference_axes'])])
                np.testing.assert_array_equal(truth, closed_truth)
                prediction = operator(rgb)
                oracle = rgb.copy()
                for model in chain:
                    oracle = integer_oracle(model, oracle)
                np.testing.assert_array_equal(prediction, oracle)
                stream.write(prediction.tobytes()); prediction_sha.update(prediction.tobytes())
                reference_sha.update(truth.tobytes())
                histogram += ea.histogram(prediction, truth)[0]
        cube = {**ea.hist_metrics(histogram), 'prediction_sha256': prediction_sha.hexdigest(),
                'reference_sha256': reference_sha.hexdigest(), 'independent_integer_mismatches': 0}
        if any(abs(cube[k]-prepared['variants'][name]['analytic_cube'][k]) > 1e-12 for k in ('mean','rms','p99','max')):
            raise AssertionError('实际完整链与解析曲线不符')
        native = []
        for kernel in ('tetra_scalar', 'tetra_avx2', 'tetra_c99'):
            destination = folder/'native-check.rgb'
            record = runtime.cube(prepared['variants'][name]['model_paths'], destination,
                                 executable=executable, kernel=kernel, threads=1, competition=True)
            if digest(destination) != prediction_sha.hexdigest():
                raise AssertionError('完整原生链不同于独立整数oracle')
            native.append({**record, 'sha256': digest(destination), 'byte_mismatches': 0})
        results[name] = {'cube': cube, 'native': native, 'photos': []}
        print(name, '完整256³及标量/AVX2/C99一致', flush=True)
    photo_rows = read(checked(plan['photos']))['images']
    if len(photo_rows) != 100:
        raise ValueError('不是冻结100图')
    operators = {name: ea.Operator(chain) for name, chain in models.items()}
    expected_photos = hashlib.sha256()
    for row in photo_rows:
        with Image.open(checked(row['evaluation'])) as image:
            if image.mode != 'RGB' or image.size != (1024,768):
                raise ValueError('不满足比赛RGB8照片契约')
            rgb = np.asarray(image).reshape(-1,3)
        truth = ea.exact_chain(tables, rgb)
        for name, operator in operators.items():
            output = operator(rgb)
            results[name]['photos'].append({'image': row['id'], **ea.metrics(output, truth)})
            if name == 'calibrated17':
                expected_photos.update(output.tobytes())
    for result in results.values():
        per = result['photos']
        result['photos'] = {'n_images': len(per), 'mean': float(np.mean([v['mean'] for v in per])),
            'rms': float(np.sqrt(np.mean([v['rms']**2 for v in per]))),
            'worst_image_p99': max(v['p99'] for v in per), 'max': max(v['max'] for v in per),
            'mean_image_cvar_1pct': float(np.mean([v['cvar_1pct'] for v in per])), 'per_image': per}
    listing = args.output/'photos.txt'
    listing.write_text('\n'.join(str(ROOT/r['evaluation']['path']) for r in photo_rows)+'\n', encoding='utf-8')
    destination = args.output/'calibrated17'/'native-photos.rgb'
    receipt = runtime.verify(prepared['variants']['calibrated17']['model_paths'], listing,
        executable=executable, kernel='tetra_avx2', threads=1, competition=True, output=destination)
    if digest(destination) != expected_photos.hexdigest():
        raise AssertionError('实际原生百图输出不同')
    results['calibrated17']['native_photos'] = {**receipt, 'sha256': digest(destination), 'byte_mismatches': 0}
    candidate = results['calibrated17']
    accepted = all(candidate[g][k] == 0 for g, keys in (('cube', ('mean','rms','p99','max')),
                    ('photos', ('mean','rms','worst_image_p99','max'))) for k in keys)
    write_json(args.output/'full-results.json', {'run_identity': run['identity_sha256'], 'variants': results,
        'acceptance': {'accepted': accepted, 'scope': '预声明一条四级可分离链；不外推其他来源'},
        'preparation_sha256': digest(args.output/'preparation.json'), 'scope': plan['limits']})
    print(json.dumps({'accepted': accepted, 'mean': candidate['cube']['mean'],
                      'photos_mean': candidate['photos']['mean']}, ensure_ascii=False), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('prepare','accept'))
    parser.add_argument('--plan', type=Path, default=ROOT/'experiments/filmic-chain-calibrated-v1.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.plan, args.output = args.plan.resolve(), args.output.resolve()
    numba.set_num_threads(4)
    (prepare if args.mode == 'prepare' else accept)(args, read(args.plan))


if __name__ == '__main__':
    main()
