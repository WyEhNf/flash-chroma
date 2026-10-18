"""冻结实验NPZ的一次全域独立整数oracle与百图精度验收，不实现原生后端。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numba
import numpy as np
from PIL import Image
from lutlab import channel_coordinates as cc, io, study_provenance
from run_channel_coordinates import metrics
from verify_channel_coordinates import integer_oracle


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def checked(spec):
    path = ROOT/spec['path']
    if digest(path) != spec['sha256']: raise ValueError(f'冻结验收输入不同：{path}')
    return path


def hist_metrics(hist):
    root = np.sqrt(np.arange(len(hist), dtype=np.float64))
    count = int(hist.sum()); rank = .99*(count-1)
    lo, hi = np.searchsorted(np.cumsum(hist), [int(np.floor(rank)), int(np.ceil(rank))], side='right')
    remaining = n_tail = max(1, int(np.ceil(count*.01))); tail = 0.
    for d in np.flatnonzero(hist)[::-1]:
        take = min(remaining, int(hist[d])); tail += take*root[d]; remaining -= take
        if not remaining: break
    return {'n': count, 'mean': float(hist@root/count),
        'rms': float(np.sqrt(hist@np.arange(len(hist), dtype=np.int64)/count)),
        'p99': float(root[lo]+(rank-np.floor(rank))*(root[hi]-root[lo])),
        'max': float(root[np.flatnonzero(hist)[-1]]), 'cvar_1pct': tail/n_tail,
        **{f'fraction_ge_{t}': float(hist[t*t:].sum()/count) for t in (1, 2, 3, 5)}}


def aggregate(rows):
    return {'n_images': len(rows), 'mean': float(np.mean([r['mean'] for r in rows])),
        'rms': float(np.sqrt(np.mean([r['rms']**2 for r in rows]))),
        'worst_image_p99': max(r['p99'] for r in rows), 'max': max(r['max'] for r in rows),
        'mean_image_cvar_1pct': float(np.mean([r['cvar_1pct'] for r in rows])), 'per_image': rows}


def changes(old, new):
    if [r['image'] for r in old] != [r['image'] for r in new]: raise ValueError('逐图次序不同')
    result = {}
    for metric in ('mean', 'rms', 'p99', 'max', 'cvar_1pct'):
        count = {'better': 0, 'equal': 0, 'worse': 0}
        for left, right in zip(old, new):
            delta = right[metric]-left[metric]
            count['better' if delta < -1e-12 else 'worse' if delta > 1e-12 else 'equal'] += 1
        result[metric] = count
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=ROOT/'experiments/velvia-channel-coordinates-accept-v1.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); args.plan, args.output = args.plan.resolve(), args.output.resolve()
    if args.output.exists(): raise ValueError('不覆盖既有完整验收')
    plan = read(args.plan); paths = {name: checked(spec) for name, spec in plan['inputs'].items()}
    if plan['threads'] != 4 or plan['cube_block'] != 65536 or plan['top_count'] != 128:
        raise ValueError('只接受冻结线程/块长/top预算')
    numba.set_num_threads(4)
    fit_run, selected = read(paths['fit_run']), read(paths['fit_selection'])
    identity = dict(fit_run); identity.pop('identity_sha256')
    if (study_provenance.identity_digest(identity) != fit_run['identity_sha256']
            or selected['run_identity'] != fit_run['identity_sha256'] or not selected['selected'] or selected['failures']
            or selected['representation_sha256'] != plan['inputs']['candidate']['sha256']
            or any(digest(ROOT/name) != sha for name, sha in fit_run['source_sha256'].items())):
        raise ValueError('原拟合身份/选择或冻结源码不同')
    old_result, old_run = read(paths['baseline_results']), read(paths['baseline_run'])
    old = old_result['candidates']['joint_grid_iter1600']
    if (old_result['run_identity'] != old_run['identity_sha256']
            or old_run['identity_sha256'] != study_provenance.identity_digest(old_run['identity'])
            or old['model_sha256'] != plan['inputs']['baseline']['sha256']
            or old['cube']['prediction_sha256'] != plan['inputs']['baseline_stream']['sha256']
            or old['cube']['reference_sha256'] != plan['inputs']['table']['sha256']
            or old_run['identity']['image_manifest_sha256'] != plan['inputs']['manifest']['sha256']):
        raise ValueError('旧2dd完整证据或照片清单没有准确绑定')
    data = np.load(paths['candidate'])
    model = cc.ChannelLut(data['grid'], data['nodes'], data['shared_idx'], data['channel_frac'])
    cc.validate(model)
    initial = io.load_sparse(paths['initial'], competition=True)
    if (data['format'].item() != 'channel_coordinates_v1_experimental'
            or data['source_model_sha256'].item() != plan['inputs']['initial']['sha256']
            or data['baseline_model_sha256'].item() != plan['inputs']['baseline']['sha256']
            or not np.array_equal(model.nodes, initial.nodes) or not np.array_equal(model.idx, initial.tables()[0])
            or not np.array_equal(model.grid, initial.grid)
            or not np.array_equal(model.channel_frac[:, :, [0, 255]], np.repeat(initial.tables()[1][None, :, [0, 255]], 3, axis=0))):
        raise ValueError('候选表示/节点/idx/grid/端点或来源不同')
    rows = read(paths['manifest'])['images']; partition = read(paths['partition'])
    if len(rows) != 100 or len(old['photos']['per_image']) != 100: raise ValueError('需要原100图')
    group_ids = {'training': [r['id'] for r in partition['training']['images']],
        'guard': [r['id'] for r in partition['guard']['images']], 'audit': partition['audit_ids']}
    union = [v for group in group_ids.values() for v in group]
    if [len(v) for v in group_ids.values()] != [60, 20, 20] or len(set(union)) != 100 or set(union) != {r['id'] for r in rows}:
        raise ValueError('照片分组不是互斥穷尽60/20/20')
    manifest_rows = {row['id']: row for row in rows}
    for group in ('training', 'guard'):
        for entry in partition[group]['images']:
            if entry['file_sha256'] != manifest_rows[entry['id']]['evaluation']['sha256']:
                raise ValueError('照片分组SHA不同')
    files = [Path(__file__), args.plan, ROOT/'scripts/run_channel_coordinates.py', ROOT/'scripts/verify_channel_coordinates.py',
        *[ROOT/'python/lutlab'/name for name in ('channel_coordinates.py', 'axis_calibration.py', 'exact_axis.py',
            'monotone_axis.py', 'io.py', 'interp.py', 'study_provenance.py')]]
    sources = {path.relative_to(ROOT).as_posix(): digest(path) for path in files}
    args.output.mkdir(parents=True)
    run = {'plan': plan, 'plan_sha256': digest(args.plan), 'source_sha256': sources,
        'environment': study_provenance.environment_fingerprint(), 'numba_threads': numba.get_num_threads(),
        'input_sha256': {name: digest(path) for name, path in paths.items()},
        'scope': '一个冻结候选一次全域/独立整数oracle和100图，不含新拟合/native/性能'}
    run['identity_sha256'] = study_provenance.identity_digest(run)
    (args.output/'run.json').write_text(json.dumps(run, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files: archive.write(path, path.relative_to(ROOT).as_posix())
    table = io.load_full(paths['table'], mmap=True).reshape(-1, 3)
    caps = np.load(paths['caps'], mmap_mode='r')
    if caps.shape != (256**3,) or caps.dtype != np.int32: raise ValueError('cap布局不同')
    hist = np.zeros(3*255**2+1, np.int64)
    worst_ids, worst_d2 = np.empty(0, np.int64), np.empty(0, np.int32)
    prediction_hash, oracle_hash, reference_hash = hashlib.sha256(), hashlib.sha256(), hashlib.sha256()
    cap_violations = 0
    print('开始唯一完整256^3前向/独立u64 oracle/逐色cap', flush=True)
    with (args.output/'cube.rgb').open('wb') as stream:
        for start in range(0, 256**3, 65536):
            keys = np.arange(start, start+65536, dtype=np.int64)
            rgb = np.column_stack((keys >> 16, (keys >> 8)&255, keys&255)).astype(np.uint8)
            prediction = cc.predict(model, rgb); independent = integer_oracle(model, rgb)
            if not np.array_equal(prediction, independent): raise AssertionError('完整研究前向与独立u64 oracle不同')
            truth = table[start:start+len(rgb)]
            e = prediction.astype(np.int32)-truth.astype(np.int32)
            squared = np.sum(e*e, axis=1, dtype=np.int32)
            hist += np.bincount(squared, minlength=len(hist))
            cap_violations += int(np.count_nonzero(squared > caps[start:start+len(rgb)]))
            prediction_hash.update(prediction.tobytes()); oracle_hash.update(independent.tobytes()); reference_hash.update(truth.tobytes())
            stream.write(prediction.tobytes())
            top = np.argsort(-squared, kind='stable')[:128]
            worst_ids, worst_d2 = np.r_[worst_ids, keys[top]], np.r_[worst_d2, squared[top]]
            keep = np.lexsort((worst_ids, -worst_d2))[:128]; worst_ids, worst_d2 = worst_ids[keep], worst_d2[keep]
    if reference_hash.hexdigest() != plan['inputs']['table']['sha256'] or digest(args.output/'cube.rgb') != prediction_hash.hexdigest():
        raise AssertionError('完整域参考/实际输出流身份不同')
    output = np.memmap(args.output/'cube.rgb', np.uint8, 'r', shape=table.shape)
    cube = {**hist_metrics(hist), 'prediction_sha256': prediction_hash.hexdigest(), 'oracle_sha256': oracle_hash.hexdigest(),
        'reference_sha256': reference_hash.hexdigest(), 'integer_oracle_channel_mismatches': 0,
        'cap_violations': cap_violations, 'caps_file_sha256': plan['inputs']['caps']['sha256'],
        'hotspots': [{'rgb': [int(k >> 16), int((k >> 8)&255), int(k&255)],
            'squared_distance': int(d), 'distance': float(np.sqrt(d)), 'prediction': output[k].tolist(), 'reference': table[k].tolist()}
            for k, d in zip(worst_ids, worst_d2)]}
    np.savez_compressed(args.output/'cube-histogram.npz', squared_distance_hist=hist, top_keys=worst_ids, top_squared=worst_d2)
    print(f"完整cube mean={cube['mean']:.9f} p99={cube['p99']:.9f} max={cube['max']:.9f} cap={cap_violations}", flush=True)
    image_values = []
    for index, row in enumerate(rows):
        path = ROOT/row['evaluation']['path']
        if digest(path) != row['evaluation']['sha256']: raise ValueError('照片输入SHA不同')
        with Image.open(path) as image:
            if image.mode != 'RGB' or image.size != (1024, 768): raise ValueError('照片非1024x768 RGB8')
            rgb = np.asarray(image).reshape(-1, 3)
        truth = table[rgb.astype(np.int64)@np.array([65536, 256, 1], np.int64)]
        prediction = cc.predict(model, rgb)
        group = next(name for name, ids in group_ids.items() if row['id'] in ids)
        image_values.append({'image': row['id'], 'group': group, 'input_file_sha256': row['evaluation']['sha256'],
            'prediction_sha256': hashlib.sha256(prediction.tobytes()).hexdigest(), **metrics(prediction, truth)})
        if (index+1)%20 == 0: print(f'完整照片 {index+1}/100', flush=True)
    photos = aggregate(image_values)
    per_image_changes = changes(old['photos']['per_image'], image_values)
    grouped = {}
    for group, ids in group_ids.items():
        old_rows = [row for row in old['photos']['per_image'] if row['image'] in ids]
        new_rows = [row for row in image_values if row['image'] in ids]
        grouped[group] = {'baseline': aggregate(old_rows), 'candidate': aggregate(new_rows), 'changes': changes(old_rows, new_rows)}
    failed = []
    for metric in ('mean', 'rms', 'p99', 'max', 'cvar_1pct'):
        if cube[metric] > old['cube'][metric]+1e-12: failed.append('cube.'+metric)
    for metric in ('mean', 'rms', 'worst_image_p99', 'max'):
        if photos[metric] > old['photos'][metric]+1e-12: failed.append('photos.'+metric)
    old_cvar = float(np.mean([row['cvar_1pct'] for row in old['photos']['per_image']]))
    if photos['mean_image_cvar_1pct'] > old_cvar+1e-12: failed.append('photos.mean_image_cvar_1pct')
    if cube['mean'] > .97*old['cube']['mean']: failed.append('cube.mean_reduction_3pct')
    if photos['mean'] > .97*old['photos']['mean']: failed.append('photos.mean_reduction_3pct')
    if not (cube['p99'] <= .97*old['cube']['p99'] or photos['worst_image_p99'] <= .97*old['photos']['worst_image_p99']):
        failed.append('p99_reduction_3pct')
    if cap_violations: failed.append('full_colour_caps')
    if sources != {path.relative_to(ROOT).as_posix(): digest(path) for path in files}:
        raise ValueError('完整验收期间冻结来源改变')
    result = {'run_identity': run['identity_sha256'], 'representation_sha256': plan['inputs']['candidate']['sha256'],
        'cube': cube, 'photos': photos, 'groups': grouped, 'per_image_changes': per_image_changes,
        'baseline': old, 'baseline_mean_image_cvar_1pct': old_cvar,
        'acceptance': {'accepted': not failed, 'failed': failed}, 'native_validation_performed': False,
        'performance_evaluation_performed': False,
        'artifact_sha256': {'cube.rgb': digest(args.output/'cube.rgb'), 'cube-histogram.npz': digest(args.output/'cube-histogram.npz')},
        'scope': plan['limits']}
    (args.output/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'cube': {key: cube[key] for key in ('mean', 'rms', 'p99', 'max', 'cvar_1pct', 'prediction_sha256')},
        'photos': {key: photos[key] for key in ('mean', 'rms', 'worst_image_p99', 'max', 'mean_image_cvar_1pct')},
        'acceptance': result['acceptance'], 'per_image_changes': per_image_changes}, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__': main()
