"""冻结两个网格/节点联合方案；选样一次选型后才执行完整终验。"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'python'))
import numba
import numpy as np
from lutlab import error_analysis as ea, fit, interp, io, joint_grid as jg, study_provenance
from lutlab.compatibility import write_json
from run_chain_error_study import colours, cube_evaluate, digest, photos_evaluate
from run_joint_box_study import native_verify, photo_samples


def check_file(path, expected):
    path = ROOT / path
    if digest(path) != expected:
        raise ValueError(f'输入SHA不同：{path}')
    return path


def baseline(plan):
    model = io.load_sparse(check_file(plan['baseline'], plan['baseline_sha256']), competition=True)
    model.grid = np.load(check_file(plan['offline_grid'], plan['offline_grid_sha256']))
    if not all(np.array_equal(a, b) for a, b in zip(io.axis_tables(model.grid), model.tables())):
        raise ValueError('离线小数网格与基线权威轴表不同')
    check_file(plan['source'], plan['source_sha256'])
    table = io.load_full(check_file(plan['table'], plan['table_sha256']), mmap=True)
    return model, table


def historical_evidence(plan):
    result = json.loads((ROOT / plan['baseline_results']).read_text(encoding='utf-8'))
    run = json.loads((ROOT / plan['baseline_run']).read_text(encoding='utf-8'))
    if (result['run_identity'] != run['identity_sha256']
            or run['identity_sha256'] != study_provenance.identity_digest(run['identity'])):
        raise ValueError('历史运行身份不一致')
    if 'baseline_case' in plan:
        matching = [r for r in result['cases'] if r['case']['id'] == plan['baseline_case']]
        if len(matching) != 1 or matching[0]['sources'][0]['table_sha256'] != plan['table_sha256']:
            raise ValueError('历史案例或本级参考表身份不同')
        case = matching[0]
        final = case['final']
        record = {'model_sha256': case['selection']['model_sha256']}
    elif 'baseline_candidate' in plan:
        record = result['candidates'][plan['baseline_candidate']]
        final = {'cube': record['cube'], 'photos': record['photos'], 'native': record['native']}
    else:
        if result['selection']['selected'] != 'joint_0002':
            raise ValueError('历史选择与冻结基线不同')
        record = next(r for r in result['records'] if r['name'] == 'joint_0002')
        final = result['final']
    if (final['cube']['prediction_sha256'] != plan['baseline_cube_sha256']
            or final['cube']['reference_sha256'] != plan['table_sha256']
            or len(final['photos']['per_image']) != 100):
        raise ValueError('历史完整验收身份不一致')
    if record['model_sha256'] != plan['baseline_sha256']:
        raise ValueError('历史完整指标未绑定当前模型SHA')
    return final


def boundary_points():
    values = np.arange(0, 256, 2, dtype=np.uint8)
    a, b = np.meshgrid(values, values, indexing='ij')
    parts = []
    for axis in range(3):
        other = [v for v in range(3) if v != axis]
        for end in (0, 255):
            p = np.empty((a.size, 3), np.uint8)
            p[:, axis], p[:, other[0]], p[:, other[1]] = end, a.ravel(), b.ravel()
            parts.append(p)
    return np.unique(np.concatenate(parts), axis=0)


def hotspots(plan, table):
    """复用已验收完整流发现训练热点，不重新执行基线全域映射。"""
    path = check_file(plan.get('hotspot_source_cube', plan['baseline_cube']),
                      plan.get('hotspot_source_cube_sha256', plan['baseline_cube_sha256']))
    stream = np.memmap(path, np.uint8, mode='r', shape=(256**3, 3))
    truth = table.reshape(-1, 3)
    ids, squared = np.empty(0, np.int64), np.empty(0, np.int32)
    k = plan['hotspot_count']
    for start in range(0, len(stream), 1 << 18):
        block = stream[start:start+(1 << 18)].astype(np.int32) - truth[start:start+(1 << 18)].astype(np.int32)
        d2 = np.sum(block * block, axis=1, dtype=np.int32)
        keep = np.argsort(-d2, kind='stable')[:k]
        ids, squared = np.concatenate((ids, keep + start)), np.concatenate((squared, d2[keep]))
        order = np.lexsort((ids, -squared))[:k]
        ids, squared = ids[order], squared[order]
    return colours(ids)


def sample_data(plan, table):
    manifest = json.loads((ROOT / 'assets/photos/manifest.json').read_text(encoding='utf-8'))
    rows = {r['id']: r for r in manifest['images']}
    partition = json.loads((ROOT / plan['partition']).read_text(encoding='utf-8'))
    training, train_info = photo_samples([rows[r['id']] for r in partition['training']['images']], plan)
    selection, select_info = photo_samples([rows[r['id']] for r in partition['guard']['images']], plan)
    if train_info != partition['training'] or select_info != partition['guard']:
        raise ValueError('照片抽样身份与既有60/20分组不同')
    cube = (colours(np.arange(256**3, dtype=np.int64)) if plan.get('cube_training') == 'full'
            else fit.stratified_points(plan['cube_training_seed']))
    train = {'cube': cube, 'photos': training,
             'boundary': boundary_points(), 'hotspots': hotspots(plan, table)}
    guard = {'cube': fit.stratified_points(plan['cube_selection_seed']), 'photos': selection,
             'hotspots': train['hotspots']}
    points = np.concatenate(list(train.values()))
    target = ea.source_apply(table, points)
    mass = np.concatenate([np.full(len(p), plan['mass'][key] / len(p)) for key, p in train.items()])
    metadata = {key: {'n': len(p), 'sha256': hashlib.sha256(p.tobytes()).hexdigest()} for key, p in train.items()}
    return points, target, mass, guard, {'partition': partition, 'training': metadata,
        'selection': {k: {'n': len(v), 'sha256': hashlib.sha256(v.tobytes()).hexdigest()} for k, v in guard.items()}}


def evaluate_samples(model, table, guard, pixels_per_image):
    out = {}
    for key, rgb in guard.items():
        prediction, truth = ea.Operator([model])(rgb), ea.source_apply(table, rgb)
        out[key] = ea.metrics(prediction, truth)
        if key == 'photos':
            per = [ea.metrics(prediction[s:s+pixels_per_image], truth[s:s+pixels_per_image])
                   for s in range(0, len(rgb), pixels_per_image)]
            out[key].update(worst_image_p99=max(r['p99'] for r in per), per_image=per)
    return out


def selection_failures(value, old):
    failures = []
    for group in ('cube', 'photos'):
        for metric in ('mean', 'rms', 'p99', 'max'):
            if value[group][metric] > old[group][metric] + 1e-12:
                failures.append(group + '.' + metric)
        if value[group]['mean'] > .97 * old[group]['mean']:
            failures.append(group + '.mean_reduction_3pct')
    if value['photos']['worst_image_p99'] > old['photos']['worst_image_p99'] + 1e-12:
        failures.append('photos.worst_image_p99')
    if not any(value[g]['p99'] < old[g]['p99'] - 1e-12 for g in ('cube', 'photos')):
        failures.append('p99_strict_improvement')
    if value['hotspots']['max'] > old['hotspots']['max'] + 1e-12:
        failures.append('hotspots.max')
    return failures


def rank(value, old, name):
    means = [value[g]['mean'] / old[g]['mean'] for g in ('cube', 'photos')]
    tails = [value[g]['p99'] / old[g]['p99'] for g in ('cube', 'photos')]
    return max(means), max(tails), sum(means), name


def source_identity(plan_path):
    files = [Path(__file__), ROOT / 'python/lutlab/joint_grid.py', ROOT / 'python/lutlab/interp.py',
             ROOT / 'python/lutlab/io.py', ROOT / 'python/lutlab/error_analysis.py',
             ROOT / 'python/lutlab/study_kernels.py', ROOT / 'python/lutlab/fit.py',
             ROOT / 'scripts/run_chain_error_study.py', ROOT / 'scripts/run_joint_box_study.py',
             ROOT / 'scripts/verify_joint_grid.py', ROOT / 'python/lutlab/study_provenance.py', plan_path]
    return {str(p.relative_to(ROOT)).replace('\\', '/'): digest(p) for p in files}


def run_fit(args, plan):
    if args.output.exists():
        raise ValueError('不覆盖已有实验目录，请使用新的输出路径')
    model, table = baseline(plan)
    identity = source_identity(args.plan)
    environment = study_provenance.environment_fingerprint()
    environment.update(numba_threads=numba.get_num_threads(), timing_scope='仅拟合用时，不比较运行时性能')
    old_full = historical_evidence(plan)
    metadata = {'identity': {'source_sha256': identity, 'plan': plan, 'environment': environment,
        'image_manifest_sha256': digest(ROOT / 'assets/photos/manifest.json'),
        'partition_sha256': digest(ROOT / plan['partition']),
        'baseline_results_sha256': digest(ROOT / plan['baseline_results']),
        'baseline_run_sha256': digest(ROOT / plan['baseline_run'])}}
    metadata['identity_sha256'] = study_provenance.identity_digest(metadata['identity'])
    study_provenance.claim_run(args.output / 'run.json', metadata)
    write_json(args.output / 'historical-full-results.json', old_full)
    points, targets, mass, guard, samples = sample_data(plan, table)
    write_json(args.output / 'samples.json', samples)
    np.savez_compressed(args.output / 'frozen-samples.npz', points=points, targets=targets, mass=mass,
                        **{key + '_selection': value for key, value in guard.items()})
    with zipfile.ZipFile(args.output / 'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name, sha in identity.items():
            path = ROOT / name
            if digest(path) != sha:
                raise ValueError('冻结期间源码发生变化')
            z.write(path, name)
    io.save_sparse(args.output / 'baseline.slut', model)
    if digest(args.output / 'baseline.slut') != plan['baseline_sha256']:
        raise AssertionError('恢复离线网格后基线序列化字节改变')
    candidates = {}
    for profile in plan['profiles']:
        print(f'[{profile}] 开始冻结预算的连续提议，训练颜色{len(points)}', flush=True)
        checkpoints, report = jg.propose(model, points, targets, mass, move_grid=profile == 'joint_grid',
            iterations=plan['iterations'], checkpoint_every=plan['checkpoint_every'],
            spacing_factor=plan['spacing_factor'], minimum_step=plan['minimum_step'],
            epsilon=plan['epsilon'], tail_at=plan['tail_at'], tail_weight=plan['tail_weight'], parts=plan['threads'],
            progress=lambda r: print(f"[{profile}] iteration={r['iteration']} loss={r['continuous_objective']:.6f} time={r['seconds']:.1f}s", flush=True))
        write_json(args.output / (profile + '-optimizer.json'), report)
        for iteration, candidate in checkpoints:
            name = profile + f'_iter{iteration:03d}'
            path = args.output / name / 'model.slut'
            path.parent.mkdir()
            io.save_sparse(path, candidate)
            candidates[name] = {'profile': profile, 'iteration': iteration, 'model_sha256': digest(path)}
    print('两个拟合方案已冻结，集中执行一次固定选择样本比较', flush=True)
    old = evaluate_samples(model, table, guard, plan['pixels_per_image'])
    for name, item in candidates.items():
        candidate = io.load_sparse(args.output / name / 'model.slut', competition=True)
        item['samples'] = evaluate_samples(candidate, table, guard, plan['pixels_per_image'])
        item['failures'] = selection_failures(item['samples'], old)
        brief = {g: {k: item['samples'][g][k] for k in ('mean', 'rms', 'p99', 'max')} for g in ('cube', 'photos')}
        print(name, json.dumps(brief), '不满足项', item['failures'], flush=True)
    selection = {}
    for profile in plan['profiles']:
        eligible = [n for n, v in candidates.items() if v['profile'] == profile and not v['failures']]
        all_names = [n for n, v in candidates.items() if v['profile'] == profile]
        selection[profile] = {'winner': min(eligible, key=lambda n: rank(candidates[n]['samples'], old, n)) if eligible else None,
            'best_mean_diagnostic_only': min(all_names, key=lambda n: rank(candidates[n]['samples'], old, n)), 'eligible': eligible}
    result = {'run_identity': metadata['identity_sha256'],
              'historical_full_results_sha256': digest(args.output / 'historical-full-results.json'),
              'baseline_samples': old, 'candidates': candidates,
              'selection_before_full_evaluation': selection, 'full_evaluation_performed': False}
    write_json(args.output / 'selection.json', result)
    print('选型已冻结：' + json.dumps(selection, ensure_ascii=False), flush=True)


def run_accept(args, plan):
    result = json.loads((args.output / 'selection.json').read_text(encoding='utf-8'))
    record = json.loads((args.output / 'run.json').read_text(encoding='utf-8'))
    if (result['run_identity'] != record['identity_sha256']
            or record['identity_sha256'] != study_provenance.identity_digest(record['identity'])
            or source_identity(args.plan) != record['identity']['source_sha256']
            or digest(ROOT / 'assets/photos/manifest.json') != record['identity']['image_manifest_sha256']
            or digest(ROOT / plan['partition']) != record['identity']['partition_sha256']):
        raise ValueError('拟合源码与终验源码不同，拒绝混合身份')
    _, table = baseline(plan)
    check_file(args.executable, plan['executable_sha256'])
    old_path = check_file(args.output / 'historical-full-results.json', result['historical_full_results_sha256'])
    old = json.loads(old_path.read_text(encoding='utf-8'))
    names = [r['winner'] for r in result['selection_before_full_evaluation'].values() if r['winner']]
    if not names:
        raise ValueError('没有符合冻结门禁的候选，不运行重复完整测试')
    models, metrics = {}, {}
    for name in names:
        folder = args.output / name
        path = check_file(folder / 'model.slut', result['candidates'][name]['model_sha256'])
        models[name] = io.load_sparse(path, competition=True)
        print(f'[{name}] 完整256³和独立整数oracle/原生验收', flush=True)
        cube = cube_evaluate([table], ea.Operator([models[name]]), folder / 'cube.rgb', 128)
        native = native_verify([models[name]], folder, cube['prediction_sha256'], args.executable)
        metrics[name] = {'cube': cube, 'native': native, 'model_sha256': digest(path)}
        print(f'[{name}] mean={cube["mean"]:.6f} p99={cube["p99"]:.6f} max={cube["max"]:.6f}', flush=True)
    print('冻结候选集中执行完整100图，各图均记录所有误差指标', flush=True)
    photos = photos_evaluate([table], {n: ea.Operator([m]) for n, m in models.items()})
    for name in metrics:
        metrics[name]['photos'] = photos[name]
        new = metrics[name]
        failed = []
        for metric in ('mean', 'rms', 'p99', 'max', 'cvar_1pct'):
            if new['cube'][metric] > old['cube'][metric] + 1e-12:
                failed.append('cube.' + metric)
        for metric in ('mean', 'rms', 'worst_image_p99', 'max'):
            if new['photos'][metric] > old['photos'][metric] + 1e-12:
                failed.append('photos.' + metric)
        cvars = [float(np.mean([r['cvar_1pct'] for r in item['photos']['per_image']])) for item in (old, new)]
        if cvars[1] > cvars[0] + 1e-12:
            failed.append('photos.mean_image_cvar_1pct')
        for group in ('cube', 'photos'):
            if new[group]['mean'] > .97 * old[group]['mean']:
                failed.append(group + '.mean_reduction_3pct')
        if not (new['cube']['p99'] <= .97 * old['cube']['p99'] or
                new['photos']['worst_image_p99'] <= .97 * old['photos']['worst_image_p99']):
            failed.append('p99_reduction_3pct')
        changes = {}
        for metric in ('mean', 'rms', 'p99', 'max', 'cvar_1pct'):
            counts = {'better': 0, 'equal': 0, 'worse': 0}
            for left, right in zip(old['photos']['per_image'], new['photos']['per_image']):
                if left['image'] != right['image']:
                    raise ValueError('逐图顺序或清单不同')
                delta = right[metric] - left[metric]
                counts['better' if delta < -1e-12 else 'worse' if delta > 1e-12 else 'equal'] += 1
            changes[metric] = counts
        new.update(acceptance={'accepted': not failed, 'failed': failed}, per_image_changes=changes,
                   mean_image_cvar_1pct=cvars[1])
    write_json(args.output / 'full-results.json', {'run_identity': result['run_identity'], 'candidates': metrics,
        'baseline': old, 'scope': plan['limits'], 'executable_sha256': digest(args.executable)})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('fit', 'accept'))
    parser.add_argument('--plan', type=Path, default=ROOT / 'experiments/joint-grid-v1.json')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--executable', type=Path)
    args = parser.parse_args()
    args.plan, args.output = args.plan.resolve(), args.output.resolve()
    if args.mode == 'accept' and args.executable is None:
        parser.error('完整验收需要显式--executable')
    plan = json.loads(args.plan.read_text(encoding='utf-8'))
    numba.set_num_threads(plan['threads'])
    (run_fit if args.mode == 'fit' else run_accept)(args, plan)


if __name__ == '__main__':
    main()
