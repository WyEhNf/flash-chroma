"""冻结其余模型，按完整到达频数精化Cinema一级；一次选型后才终验。"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'python'))
import numba
import numpy as np
from PIL import Image
from lutlab import chain_envelope, error_analysis as ea, fit, interp, io, rounded_grid, study_provenance, suffix_objective
from lutlab.compatibility import write_json
from run_chain_error_study import colours, cube_evaluate, digest, photos_evaluate
from run_joint_box_study import native_verify, photo_samples


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def checked(spec):
    path = ROOT / spec['path']
    if digest(path) != spec['sha256']:
        raise ValueError(f'输入SHA不同：{path}')
    return path


def load_inputs(plan):
    for name in ('selection_basis', 'weight_basis'):
        if name in plan:
            checked(plan[name])
    models = [io.load_sparse(checked(s), competition=True) for s in plan['baseline_models']]
    tables = []
    for spec in plan['tables']:
        checked({'path': spec['source'], 'sha256': spec['source_sha256']})
        tables.append(io.load_full(checked(spec), mmap=True))
    evidence = plan['baseline_evidence']
    result, run, selection = (read(checked(evidence[k])) for k in ('results', 'run', 'selection'))
    if evidence.get('layout') == 'cinema-rounded':
        final = {k: result[k] for k in ('cube', 'photos')}
        final['native_parity'] = result['native']
        previous_plan = run['identity']['plan']
        historical_hashes = [s['sha256'] for s in previous_plan['baseline_models']]
        chosen = selection['winner']
        if not chosen or selection['candidates'][chosen]['failures'] or not result['acceptance']['accepted']:
            raise ValueError('新历史基线没有通过冻结选择与完整门禁')
        historical_hashes[previous_plan['optimized_stage']-1] = selection['candidates'][chosen]['model_sha256']
        if (historical_hashes != result['model_sha256'] or selection['run_identity'] != result['run_identity']):
            raise ValueError('新历史四模型与选择记录不同')
    else:
        final = result['final']
        historical_hashes = selection['model_sha256']
    hashes = [s['sha256'] for s in plan['baseline_models']]
    if (len(models) != 4 or any(m.m != plan['m'] for m in models)
            or plan['optimized_stage'] not in (1, 2, 3, 4)
            or plan['frozen_stages'] != [i for i in range(1, 5) if i != plan['optimized_stage']]
            or historical_hashes != hashes
            or result['run_identity'] != evidence['run_identity']
            or result['run_identity'] != run['identity_sha256']
            or run['identity_sha256'] != study_provenance.identity_digest(run['identity'])
            or final['cube']['prediction_sha256'] != evidence['cube']['sha256']
            or final['cube']['reference_sha256'] != evidence['reference_cube_sha256']
            or len(final['photos']['per_image']) != 100):
        raise ValueError('历史四级模型、完整结果或运行身份不一致')
    checked(evidence['cube'])
    parity = final['native_parity']
    if ({r['kernel'] for r in parity} != {'tetra_scalar', 'tetra_avx2', 'tetra_c99'}
            or any(r['byte_mismatches'] or r['sha256'] != evidence['cube']['sha256']
                   or r['executable_sha256'] != plan['environment']['executable_sha256'] for r in parity)):
        raise ValueError('历史完整三后端回执不同')
    checked(plan['photo_manifest'])
    checked(plan['partition'])
    return models, tables, final


def rgb_keys(rgb):
    value = np.asarray(rgb, np.uint32)
    return ((value[:, 0] << 16) | (value[:, 1] << 8) | value[:, 2]).astype(np.int64)


def add_counts(frequency, rgb):
    """保留重复颜色次数；频数桶uint32，守恒检查另用uint64。"""
    frequency += np.bincount(rgb_keys(rgb), minlength=len(frequency)).astype(np.uint32)


def arrival_mass(cube_frequency, photo_frequency, allocation):
    nc, npix = (int(f.sum(dtype=np.uint64)) for f in (cube_frequency, photo_frequency))
    if not nc or not npix or cube_frequency.shape != photo_frequency.shape:
        raise ValueError('到达频数为空或形状不一致')
    if abs(sum(allocation.values()) - 1.) > 1e-12 or min(allocation.values()) <= 0:
        raise ValueError('三种测度质量必须正且总和1')
    mass = np.full(len(cube_frequency), allocation['own_uniform'] / len(cube_frequency))
    mass += cube_frequency.astype(np.float64) * (allocation['cube_arrival'] / nc)
    mass += photo_frequency.astype(np.float64) * (allocation['photo_arrival'] / npix)
    if abs(float(mass.sum()) - 1.) > 1e-10:
        raise AssertionError('合并质量不守恒')
    return mass


def build_envelope(arrivals, points, models, tables, plan, folder):
    """参考整链仅用于硬上限，不进入本级目标或节点拟合标签。"""
    config = plan['chain_envelope']
    floor = config['floor_squared']
    baseline = np.memmap(checked(plan['baseline_evidence']['cube']), np.uint8, 'r', shape=points.shape)
    targets, caps = np.empty_like(points), np.empty(len(points), np.int32)
    for start in range(0, len(points), 1 << 18):
        stop = min(start+(1 << 18), len(points))
        targets[start:stop] = ea.exact_chain(tables, points[start:stop])
        error = baseline[start:stop].astype(np.int32)-targets[start:stop].astype(np.int32)
        caps[start:stop] = np.maximum(floor, np.sum(error*error, axis=1, dtype=np.int32))
    sha_array = lambda a: hashlib.sha256(a.tobytes()).hexdigest()
    if sha_array(targets) != plan['baseline_evidence']['reference_cube_sha256']:
        raise ValueError('硬约束原始整链参考流不同')
    suffix_models = models[plan['optimized_stage']:]
    suffix = None
    if suffix_models:
        # 仅缓存固定稀疏后缀逐级RGB8结果；不拿原始完整后缀代替运行时。
        suffix = np.empty_like(points)
        operator = ea.Operator(suffix_models)
        for start in range(0, len(points), 1 << 18):
            suffix[start:start+(1 << 18)] = operator(points[start:start+(1 << 18)])
        sample = np.random.default_rng(2026101904).choice(len(points), 4096, replace=False)
        oracle = points[sample].copy()
        for model in suffix_models:
            oracle = interp.apply_tetra_q16(model, oracle)
        np.testing.assert_array_equal(suffix[sample], oracle)
        np.save(folder / 'envelope-suffix.npy', suffix)
    np.save(folder / 'envelope-arrivals.npy', arrivals)
    np.save(folder / 'envelope-reference.npy', targets)
    np.save(folder / 'envelope-caps.npy', caps)
    metadata = {'rows': len(points), 'floor_squared': floor, 'formula': 'd_new(x)^2<=max(floor_squared,d_baseline(x)^2)',
        'labels_unchanged': f"拟合标签仍为独立第{plan['optimized_stage']}原表，整链参考仅约束禁止位",
        'baseline_cube_sha256': plan['baseline_evidence']['cube']['sha256'],
        'reference_sha256': sha_array(targets), 'arrivals_sha256': sha_array(arrivals), 'caps_sha256': sha_array(caps),
        'suffix_model_sha256': [s['sha256'] for s in plan['baseline_models'][plan['optimized_stage']:]],
        'suffix_cache_sha256': sha_array(suffix) if suffix is not None else None,
        'suffix_oracle_scope': '固定4096全域颜色逐级整数合同；完整整链仍另验' if suffix is not None else '空后缀'}
    write_json(folder / 'envelope.json', metadata)
    return chain_envelope.ChainEnvelope(rgb_keys(arrivals), targets, caps,
        expected_arrivals=arrivals, metadata=metadata, suffix=suffix)


def build_training(models, tables, plan, folder):
    """只用固定稀疏前三段到达分布；本级标签始终来自第四张原表。"""
    stage = plan['optimized_stage']-1
    prefix = ea.Operator(models[:stage])
    table = tables[stage]
    points = colours(np.arange(256**3, dtype=np.int64))
    frequency = np.zeros(256**3, np.uint32)
    arrivals = np.empty_like(points) if 'chain_envelope' in plan else None
    for start in range(0, len(points), 1 << 18):
        block = prefix(points[start:start+(1 << 18)])
        add_counts(frequency, block)
        if arrivals is not None:
            arrivals[start:start+len(block)] = block
        if start % (1 << 22) == 0:
            print(f'构造完整原始cube到达频数：{start}/{len(points)}', flush=True)
    if int(frequency.sum(dtype=np.uint64)) != plan['training']['cube_count']:
        raise AssertionError('原始cube频数不守恒')
    np.save(folder / 'cube-arrival-frequency.npy', frequency)
    manifest = {r['id']: r for r in read(ROOT / plan['photo_manifest']['path'])['images']}
    partition = read(ROOT / plan['partition']['path'])
    photo = np.zeros(256**3, np.uint32)
    records = []
    for record in partition['training']['images']:
        row = manifest[record['id']]
        if row['evaluation']['sha256'] != record['file_sha256']:
            raise ValueError('训练分组照片SHA不同')
        path = checked(row['evaluation'])
        with Image.open(path) as image:
            if image.mode != 'RGB' or image.size != (1024, 768):
                raise ValueError('训练照片不符合RGB8尺寸契约')
            rgb = np.asarray(image).reshape(-1, 3)
        add_counts(photo, prefix(rgb))
        records.append({'id': row['id'], 'sha256': digest(path), 'pixels': len(rgb)})
    if (len(records) != plan['training']['photo_count']
            or int(photo.sum(dtype=np.uint64)) != plan['training']['photo_pixels']):
        raise AssertionError('训练照片数量或到达频数不守恒')
    np.save(folder / 'photo-arrival-frequency.npy', photo)
    mass = arrival_mass(frequency, photo, plan['training']['mass'])
    targets = table.reshape(-1, 3).copy()
    np.save(folder / 'training-mass.npy', mass)
    sha_array = lambda a: hashlib.sha256(a.tobytes()).hexdigest()
    metadata = {'prefix_model_sha256': [r['sha256'] for r in plan['baseline_models'][:stage]],
        'training_images': records, 'rows': len(points), 'label': f'独立第{stage+1}原表，没有复合或残差标签',
        'points_sha256': sha_array(points), 'targets_sha256': sha_array(targets),
        'cube_arrival': {'total': int(frequency.sum(dtype=np.uint64)), 'array_sha256': sha_array(frequency),
                         'file_sha256': digest(folder / 'cube-arrival-frequency.npy')},
        'photo_arrival': {'total': int(photo.sum(dtype=np.uint64)), 'array_sha256': sha_array(photo),
                          'file_sha256': digest(folder / 'photo-arrival-frequency.npy')},
        'mass_sha256': sha_array(mass), 'mass_sum': float(mass.sum()), 'allocation': plan['training']['mass']}
    envelope = build_envelope(arrivals, points, models, tables, plan, folder) if arrivals is not None else None
    names = ['cube-arrival-frequency.npy', 'photo-arrival-frequency.npy', 'training-mass.npy']
    if envelope is not None:
        names += ['envelope.json', 'envelope-arrivals.npy', 'envelope-reference.npy', 'envelope-caps.npy']
        if envelope.suffix.size:
            names += ['envelope-suffix.npy']
        metadata['envelope'] = envelope.metadata
    metadata['artifact_sha256'] = {name: digest(folder / name) for name in names}
    return points, targets, mass, metadata, envelope


def selection_inputs(plan):
    manifest = {r['id']: r for r in read(ROOT / plan['photo_manifest']['path'])['images']}
    partition = read(ROOT / plan['partition']['path'])
    selection = plan['selection']
    photos, metadata = photo_samples([manifest[r['id']] for r in partition['guard']['images']], selection)
    if metadata != partition['guard'] or len(metadata['images']) != selection['photo_count']:
        raise ValueError('选择照片不符合历史固定20图抽样身份')
    cube = fit.stratified_points(selection['cube_seed'])
    if len(cube) != selection['cube_count']:
        raise ValueError('颜色选择数量不同')
    return {'cube': cube, 'photos': photos}, metadata


def evaluate_samples(models, tables, guard, group_size):
    operator, output = ea.Operator(models), {}
    for name, rgb in guard.items():
        prediction, truth = operator(rgb), ea.exact_chain(tables, rgb)
        output[name] = ea.metrics(prediction, truth)
        if name == 'photos':
            per = [ea.metrics(prediction[s:s+group_size], truth[s:s+group_size])
                   for s in range(0, len(rgb), group_size)]
            output[name].update(per_image=per, worst_image_p99=max(v['p99'] for v in per))
    return output


def failures(value, old, *, full=False):
    failed = []
    for group in ('cube', 'photos'):
        keys = (('mean', 'rms', 'p99', 'max', 'cvar_1pct') if full else ('mean', 'rms', 'p99', 'max')) if group == 'cube' else (
            ('mean', 'rms', 'worst_image_p99', 'max') if full else ('mean', 'rms', 'p99', 'max', 'worst_image_p99'))
        for key in keys:
            if value[group][key] > old[group][key] + 1e-12:
                failed.append(group + '.' + key)
        if value[group]['mean'] > .97 * old[group]['mean']:
            failed.append(group + '.mean_reduction_3pct')
    if full:
        cvar = lambda item: float(np.mean([r['cvar_1pct'] for r in item['photos']['per_image']]))
        if cvar(value) > cvar(old) + 1e-12:
            failed.append('photos.mean_image_cvar_1pct')
        if not (value['cube']['p99'] <= .97*old['cube']['p99']
                or value['photos']['worst_image_p99'] <= .97*old['photos']['worst_image_p99']):
            failed.append('p99_reduction_3pct')
    elif not any(value[g]['p99'] < old[g]['p99'] - 1e-12 for g in ('cube', 'photos')):
        failed.append('p99_strict_improvement')
    return failed


def rank(value, old, name):
    means = [value[g]['mean']/old[g]['mean'] for g in ('cube', 'photos')]
    tails = [value[g]['p99']/old[g]['p99'] for g in ('cube', 'photos')]
    return max(means), max(tails), sum(means), name


def source_identity(plan_path):
    files = sorted((ROOT / 'python/lutlab').glob('*.py'))
    files += [Path(__file__), ROOT / 'scripts/run_chain_error_study.py',
              ROOT / 'scripts/run_joint_box_study.py', ROOT / 'scripts/verify_cinema_arrivals.py',
              ROOT / 'scripts/verify_chain_envelope.py', plan_path]
    if 'suffix_objective' in read(plan_path):
        files.append(ROOT / 'scripts/verify_suffix_objective.py')
    return {str(p.relative_to(ROOT)).replace('\\', '/'): digest(p) for p in files}


def fit_run(args, plan):
    if args.output.exists():
        raise ValueError('不覆盖已有实验目录')
    started = time.perf_counter()
    models, tables, old = load_inputs(plan)
    identity = {'plan': plan, 'source_sha256': source_identity(args.plan),
        'environment': study_provenance.environment_fingerprint(), 'numba_threads': numba.get_num_threads(),
        'scope': '离线精度提议；不比较运行时性能，不升级默认，不创建PR'}
    run = {'identity': identity, 'identity_sha256': study_provenance.identity_digest(identity)}
    study_provenance.claim_run(args.output / 'run.json', run)
    write_json(args.output / 'historical-full-results.json', old)
    with zipfile.ZipFile(args.output / 'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, sha in identity['source_sha256'].items():
            if digest(ROOT / name) != sha:
                raise ValueError('冻结期间源码发生变化')
            archive.write(ROOT / name, name)
    for i, model in enumerate(models):
        path = args.output / f'baseline-stage{i+1}.slut'
        io.save_sparse(path, model)
        if digest(path) != plan['baseline_models'][i]['sha256']:
            raise ValueError('基线序列化字节改变')
    points, targets, mass, training, envelope = build_training(models, tables, plan, args.output)
    write_json(args.output / 'training.json', training)
    extra = None
    if 'suffix_objective' in plan:
        if envelope is None or not envelope.suffix.size:
            raise ValueError('后缀度量要求已冻结非空稀疏后缀缓存')
        extra = suffix_objective.SuffixObjective(envelope.suffix, targets, plan['suffix_objective']['weight'])
        write_json(args.output / 'suffix-objective.json', extra.metadata)
    stage = plan['optimized_stage']-1
    print(f'到达频数已冻结；仅拟合第{stage+1}级原表标签，固定4扫', flush=True)
    checkpoints, report = rounded_grid.propose(models[stage], points, targets, mass,
        sweeps=plan['sweeps'], tail_at=plan['tail_at'], tail_weight=plan['tail_weight'],
        maximum_squared=plan['maximum_squared'], parts=plan['environment']['threads'],
        envelope=envelope,
        extra_objective=extra,
        progress=lambda r: print(f"sweep={r['sweep']} loss={r['after_weighted_objective']:.6f} changed={r['changed_coordinates']} time={r['seconds']:.1f}s", flush=True))
    write_json(args.output / 'optimizer.json', report)
    candidates = {}
    for sweep, candidate in checkpoints:
        if sweep not in plan['candidate_sweeps']:
            continue
        if not all(np.array_equal(a, b) for a, b in zip(candidate.tables(), models[stage].tables())):
            raise AssertionError('本级权威表改变')
        name = f'stage{stage+1}_sweep{sweep:03d}'
        path = args.output / name / f'stage{stage+1}.slut'
        path.parent.mkdir()
        io.save_sparse(path, candidate)
        candidates[name] = {'sweep': sweep, 'model_sha256': digest(path)}
    guard, metadata = selection_inputs(plan)
    np.savez_compressed(args.output / 'selection-points.npz', **guard)
    write_json(args.output / 'selection-inputs.json', metadata)
    print('全部候选已冻结；一次比较真实四级链选择样本', flush=True)
    old_samples = evaluate_samples(models, tables, guard, plan['selection']['pixels_per_image'])
    for name, item in candidates.items():
        candidate = io.load_sparse(args.output / name / f'stage{stage+1}.slut', competition=True)
        chain = models.copy()
        chain[stage] = candidate
        item['samples'] = evaluate_samples(chain, tables, guard, plan['selection']['pixels_per_image'])
        item['failures'] = failures(item['samples'], old_samples)
        print(name, json.dumps({g: {k: item['samples'][g][k] for k in ('mean', 'rms', 'p99', 'max')}
            for g in ('cube', 'photos')}), '不满足项', item['failures'], flush=True)
    eligible = [n for n, item in candidates.items() if not item['failures']]
    winner = min(eligible, key=lambda n: rank(candidates[n]['samples'], old_samples, n)) if eligible else None
    write_json(args.output / 'selection.json', {'run_identity': run['identity_sha256'],
        'baseline_samples': old_samples, 'candidates': candidates, 'winner': winner,
        'training_sha256': digest(args.output / 'training.json'), 'full_evaluation_performed': False,
        'suffix_objective_sha256': digest(args.output / 'suffix-objective.json') if extra is not None else None,
        'historical_results_sha256': digest(args.output / 'historical-full-results.json'),
        'seconds': time.perf_counter()-started, 'numba_threading_layer': numba.threading_layer()})
    print('选择已冻结：' + str(winner), flush=True)


def accept_run(args, plan):
    result, run = read(args.output / 'selection.json'), read(args.output / 'run.json')
    if (result['run_identity'] != run['identity_sha256']
            or run['identity_sha256'] != study_provenance.identity_digest(run['identity'])
            or source_identity(args.plan) != run['identity']['source_sha256']):
        raise ValueError('拟合/验收来源不同')
    if (args.output / 'full-results.json').exists():
        raise ValueError('已有完整结果，不重复终验')
    models, tables, old = load_inputs(plan)
    if digest(args.output / 'training.json') != result['training_sha256']:
        raise ValueError('训练记录与冻结决策不同')
    training = read(args.output / 'training.json')
    for name, sha in training['artifact_sha256'].items():
        checked({'path': str(args.output / name), 'sha256': sha})
    if 'suffix_objective' in plan:
        checked({'path': str(args.output / 'suffix-objective.json'), 'sha256': result['suffix_objective_sha256']})
    if (digest(args.output / 'historical-full-results.json') != result['historical_results_sha256']
            or read(args.output / 'historical-full-results.json') != old):
        raise ValueError('历史完整基线不同')
    checked({'path': str(args.executable), 'sha256': plan['environment']['executable_sha256']})
    name = result['winner']
    if not name or result['candidates'][name]['failures']:
        raise ValueError('没有合格候选，不执行完整终验')
    folder = args.output / name
    stage = plan['optimized_stage']-1
    spec = {'path': str(folder / f'stage{stage+1}.slut'), 'sha256': result['candidates'][name]['model_sha256']}
    models[stage] = io.load_sparse(checked(spec), competition=True)
    print('完整四级256³、独立整数oracle及标量/AVX2/C99验收', flush=True)
    cube = cube_evaluate(tables, ea.Operator(models), folder / 'cube.rgb', 128)
    if cube['reference_sha256'] != plan['baseline_evidence']['reference_cube_sha256']:
        raise ValueError('四级完整参考流不同')
    native = native_verify(models, folder, cube['prediction_sha256'], args.executable)
    envelope_receipt = None
    if 'chain_envelope' in plan:
        caps = np.load(args.output / 'envelope-caps.npy', mmap_mode='r')
        truth = np.load(args.output / 'envelope-reference.npy', mmap_mode='r')
        prediction = np.memmap(folder / 'cube.rgb', np.uint8, 'r', shape=(256**3, 3))
        violations = 0
        for start in range(0, len(caps), 1 << 18):
            stop = min(start+(1 << 18), len(caps))
            error = prediction[start:stop].astype(np.int32)-truth[start:stop].astype(np.int32)
            violations += int(np.count_nonzero(np.sum(error*error, axis=1, dtype=np.int32) > caps[start:stop]))
        if violations:
            raise AssertionError('完整四级输出违反冻结尾部包络')
        envelope_receipt = {'original_input_colours': len(caps), 'violations': violations,
                            'caps_file_sha256': digest(args.output / 'envelope-caps.npy')}
    print(f"cube mean={cube['mean']:.6f} p99={cube['p99']:.6f} max={cube['max']:.6f}，进入100图", flush=True)
    photos = photos_evaluate(tables, {'candidate': ea.Operator(models)})['candidate']
    value = {'cube': cube, 'photos': photos}
    failed = failures(value, old, full=True)
    partition = read(ROOT / plan['partition']['path'])
    groups = {r['id']: group for group, rows in (
        ('training', partition['training']['images']), ('selection', partition['guard']['images'])) for r in rows}
    groups.update({image: 'audit' for image in partition['audit_ids']})
    changes = {group: {} for group in ('all', 'training', 'selection', 'audit')}
    for metric in ('mean', 'rms', 'p99', 'max', 'cvar_1pct'):
        for group in changes:
            changes[group][metric] = {'better': 0, 'equal': 0, 'worse': 0}
        for left, right in zip(old['photos']['per_image'], photos['per_image']):
            if left['image'] != right['image']:
                raise ValueError('逐图顺序或身份不同')
            delta = right[metric] - left[metric]
            status = 'better' if delta < -1e-12 else 'worse' if delta > 1e-12 else 'equal'
            for group in ('all', groups[right['image']]):
                changes[group][metric][status] += 1
    value.update(run_identity=result['run_identity'], native=native, per_image_changes=changes,
        chain_envelope=envelope_receipt,
        model_sha256=[digest(folder / f'selected-stage{k+1}.slut') for k in range(4)],
        acceptance={'accepted': not failed, 'failed': failed}, baseline=old,
        default_promoted=False, scope=plan['limits'])
    write_json(args.output / 'full-results.json', value)
    print(json.dumps({'acceptance': value['acceptance'], 'cube': cube['mean'], 'photos': photos['mean']}, ensure_ascii=False), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('fit', 'accept'))
    parser.add_argument('--plan', type=Path, default=ROOT / 'experiments/cinema-rounded-v1.json')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--executable', type=Path)
    args = parser.parse_args()
    args.plan, args.output = args.plan.resolve(), args.output.resolve()
    if args.mode == 'accept' and args.executable is None:
        parser.error('完整验收必须显式指定--executable')
    plan = read(args.plan)
    numba.set_num_threads(plan['environment']['threads'])
    (fit_run if args.mode == 'fit' else accept_run)(args, plan)


if __name__ == '__main__':
    main()
