"""固定两图读取旧/新完整字节，按训练频数归因；中间仅<=128个反例独立整数前向。"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys
import zipfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from PIL import Image
from lutlab import io, study_provenance

DISTANCE = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))


def digest(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path): return json.loads(Path(path).read_text(encoding='utf-8'))


def checked(spec):
    path = ROOT/spec['path']
    if digest(path) != spec['sha256']: raise ValueError(f'冻结输入不同：{path}')
    return path


def hist_metrics(squared, counts):
    hist = np.bincount(squared, weights=counts, minlength=len(DISTANCE)).astype(np.int64)
    n = int(hist.sum())
    if not n: return {'n': 0, 'mean': None, 'rms': None, 'p99': None, 'max': None, 'distance_sum': 0.}
    rank = .99*(n-1)
    lo, hi = np.searchsorted(np.cumsum(hist), [int(np.floor(rank)), int(np.ceil(rank))], side='right')
    distance_sum = float(hist@DISTANCE)
    return {'n': n, 'mean': distance_sum/n, 'rms': float(np.sqrt(hist@np.arange(len(hist), dtype=np.int64)/n)),
        'p99': float(DISTANCE[lo]+(rank-np.floor(rank))*(DISTANCE[hi]-DISTANCE[lo])),
        'max': float(DISTANCE[np.flatnonzero(hist)[-1]]), 'distance_sum': distance_sum}


def change_metrics(old_squared, new_squared, counts):
    improved, degraded = new_squared < old_squared, new_squared > old_squared
    delta = DISTANCE[new_squared]-DISTANCE[old_squared]
    n = int(counts.sum())
    return {'pixels': n, 'improved_pixels': int(counts[improved].sum()), 'degraded_pixels': int(counts[degraded].sum()),
        'equal_distance_pixels': int(counts[~(improved|degraded)].sum()),
        'improved_fraction': float(counts[improved].sum()/n) if n else None,
        'degraded_fraction': float(counts[degraded].sum()/n) if n else None,
        'gross_degradation_distance_sum': float(counts[degraded]@delta[degraded]),
        'gross_improvement_distance_sum': float(counts[improved]@(-delta[improved])),
        'net_distance_delta_sum': float(counts@delta)}


def intermediate_oracle(model, points):
    """一次小输入，独立比较器/u64，不调用interp或实验新表示前向。"""
    idx, frac = model.tables()
    base = (idx[0, points[:, 0]].astype(np.int64)*model.m+idx[1, points[:, 1]])*model.m+idx[2, points[:, 2]]
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
    if np.any(weights.sum(axis=1, dtype=np.uint64) != io.ONE) or np.any(acc > 255*io.ONE):
        raise AssertionError('中间小前向权重/整数界不符')
    return ((acc+io.ONE//2) >> io.Q).astype(np.uint8)


def csv_write(path, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=ROOT/'experiments/channel-frequency-transfer-v1.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); args.plan, args.output = args.plan.resolve(), args.output.resolve()
    if args.output.exists(): raise ValueError('不覆盖既有归因')
    plan = read(args.plan); paths = {name: checked(spec) for name, spec in plan['inputs'].items()}
    image_paths = {row['id']: checked(row) for row in plan['images']}
    history = read(paths['history'])
    old_rows = {row['image']: row for row in history['baseline']['photos']['per_image']}
    new_rows = {row['image']: row for row in history['photos']['per_image']}
    training_best = min((row for row in new_rows.values() if row['group'] == 'training'),
        key=lambda row: (row['mean']-old_rows[row['image']]['mean'], row['image']))
    if (training_best['image'] != 'div2k-0841' or [row['id'] for row in plan['images']] != ['div2k-0843', 'div2k-0841']
            or history['cube']['prediction_sha256'] != plan['inputs']['new_cube']['sha256']
            or history['baseline']['cube']['prediction_sha256'] != plan['inputs']['old_cube']['sha256']
            or history['cube']['reference_sha256'] != plan['inputs']['table']['sha256']
            or history['representation_sha256'] != plan['inputs']['candidate']['sha256']):
        raise ValueError('两图选择或模型/完整流身份不符')
    frequency = np.load(paths['frequency'], mmap_mode='r'); training, partition = read(paths['frequency_metadata']), read(paths['partition'])
    if (frequency.dtype != np.uint32 or frequency.shape != (256**3,)
            or hashlib.sha256(memoryview(frequency)).hexdigest() != plan['frequency_array_sha256']
            or int(frequency.sum(dtype=np.uint64)) != 60*1024*768 or training['prefix_model_sha256'] != []
            or training['artifact_sha256']['photo-arrival-frequency.npy'] != plan['inputs']['frequency']['sha256']
            or [r['id'] for r in training['training_images']] != [r['id'] for r in partition['training']['images']]
            or [r['sha256'] for r in training['training_images']] != [r['file_sha256'] for r in partition['training']['images']]):
        raise ValueError('冻结训练频数或分组不同')
    middle = io.load_sparse(paths['intermediate'], competition=True); candidate = np.load(paths['candidate'])
    if (not np.array_equal(candidate['nodes'], middle.nodes) or not np.array_equal(candidate['shared_idx'], middle.tables()[0])
            or not np.array_equal(candidate['grid'], middle.grid) or candidate['channel_frac'].shape != (3, 3, 256)):
        raise ValueError('新模型节点/shared idx/grid不是iter003固定值')
    files = [Path(__file__), args.plan, ROOT/'python/lutlab/io.py', ROOT/'python/lutlab/study_provenance.py']
    sources = {path.relative_to(ROOT).as_posix(): digest(path) for path in files}
    args.output.mkdir(parents=True)
    run = {'plan': plan, 'plan_sha256': digest(args.plan), 'source_sha256': sources,
        'environment': study_provenance.environment_fingerprint(),
        'input_sha256': {name: digest(path) for name, path in paths.items()},
        'image_sha256': {name: digest(path) for name, path in image_paths.items()},
        'scope': '固定两图查旧/新字节；top<=128一次中间独立u64，不拟合/新模型/原生'}
    run['identity_sha256'] = study_provenance.identity_digest(run)
    (args.output/'run.json').write_text(json.dumps(run, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files: archive.write(path, path.relative_to(ROOT).as_posix())
    shape = (256**3, 3)
    old_cube = np.memmap(paths['old_cube'], np.uint8, 'r', shape=shape)
    new_cube = np.memmap(paths['new_cube'], np.uint8, 'r', shape=shape)
    table = io.load_full(paths['table'], mmap=True).reshape(-1, 3)
    image_results, intermediate_keys, group_rows = {}, [], []
    hist_archive = {}
    for image in plan['images']:
        name = image['id']
        with Image.open(image_paths[name]) as picture:
            if picture.mode != 'RGB' or picture.size != (1024, 768): raise ValueError('固定两图格式不同')
            pixels = np.asarray(picture).reshape(-1, 3)
        if hashlib.sha256(pixels.tobytes()).hexdigest() != image['pixel_sha256']: raise ValueError('解码像素SHA不同')
        keys, counts = np.unique(pixels.astype(np.int64)@np.array([65536, 256, 1], np.int64), return_counts=True)
        target, old, new = table[keys], old_cube[keys], new_cube[keys]
        old_error, new_error = old.astype(np.int32)-target.astype(np.int32), new.astype(np.int32)-target.astype(np.int32)
        old_squared, new_squared = np.sum(old_error*old_error, axis=1, dtype=np.int32), np.sum(new_error*new_error, axis=1, dtype=np.int32)
        before, after = hist_metrics(old_squared, counts), hist_metrics(new_squared, counts)
        change = change_metrics(old_squared, new_squared, counts)
        for metric in ('mean', 'rms', 'p99', 'max'):
            if abs(before[metric]-old_rows[name][metric]) > 1e-12 or abs(after[metric]-new_rows[name][metric]) > 1e-12:
                raise AssertionError('旧/新字节查表没有复现保存的整图指标')
        groups, train_frequency = {}, frequency[keys]
        coverage = np.zeros(len(keys), np.int8)
        for group in plan['frequency_bins']:
            selected = (train_frequency >= group['min']) & (train_frequency <= group['max']); coverage += selected
            g_old, g_new = hist_metrics(old_squared[selected], counts[selected]), hist_metrics(new_squared[selected], counts[selected])
            g_change = change_metrics(old_squared[selected], new_squared[selected], counts[selected])
            value = {'unique_colours': int(selected.sum()), 'pixel_mass': int(counts[selected].sum())/len(pixels),
                'old': g_old, 'new': g_new, 'change': g_change,
                'old_error_share': g_old['distance_sum']/before['distance_sum'], 'new_error_share': g_new['distance_sum']/after['distance_sum'],
                'net_mean_delta_contribution': g_change['net_distance_delta_sum']/len(pixels),
                'share_of_gross_degradation': g_change['gross_degradation_distance_sum']/change['gross_degradation_distance_sum'] if change['gross_degradation_distance_sum'] else 0.,
                'share_of_gross_improvement': g_change['gross_improvement_distance_sum']/change['gross_improvement_distance_sum'] if change['gross_improvement_distance_sum'] else 0.}
            groups[group['id']] = value
            group_rows.append({'image': name, 'frequency_bin': group['id'], 'unique_colours': value['unique_colours'],
                'pixels': g_change['pixels'], 'pixel_mass': value['pixel_mass'], 'old_mean': g_old['mean'], 'new_mean': g_new['mean'],
                'old_p99': g_old['p99'], 'new_p99': g_new['p99'], 'old_error_sum': g_old['distance_sum'], 'new_error_sum': g_new['distance_sum'],
                **g_change, 'old_error_share': value['old_error_share'], 'new_error_share': value['new_error_share'],
                'net_mean_delta_contribution': value['net_mean_delta_contribution'],
                'share_of_gross_degradation': value['share_of_gross_degradation'], 'share_of_gross_improvement': value['share_of_gross_improvement']})
            for label, squared in (('old', old_squared), ('new', new_squared)):
                hist_archive[name+'_'+group['id'].replace('..', '_').replace('>=', 'ge')+'_'+label] = np.bincount(
                    squared[selected], weights=counts[selected], minlength=len(DISTANCE)).astype(np.int64)
        if np.any(coverage != 1) or sum(v['change']['pixels'] for v in groups.values()) != len(pixels):
            raise AssertionError('固定频数组没有互斥穷尽')
        delta = DISTANCE[new_squared]-DISTANCE[old_squared]
        eligible = np.flatnonzero(new_squared > old_squared)
        score = counts[eligible]*delta[eligible]
        chosen = eligible[np.lexsort((keys[eligible], -score))[:plan['top_count_per_image']]]
        intermediate_keys.extend(keys[chosen].tolist())
        top = [{'key': int(keys[i]), 'rgb': [int(keys[i] >> 16), int((keys[i] >> 8)&255), int(keys[i]&255)],
            'image_count': int(counts[i]), 'training_count': int(train_frequency[i]), 'target': target[i].tolist(),
            'old_prediction': old[i].tolist(), 'new_prediction': new[i].tolist(),
            'old_distance': float(DISTANCE[old_squared[i]]), 'new_distance': float(DISTANCE[new_squared[i]]),
            'weighted_delta': float(counts[i]*delta[i])} for i in chosen]
        image_results[name] = {'group': image['group'], 'pixels': len(pixels), 'unique_colours': len(keys),
            'old': before, 'new': after, 'change': change, 'frequency_groups': groups, 'top_degradation_colours': top}
    unique_keys = np.array(sorted(set(intermediate_keys)), np.int64)
    if len(unique_keys) > 128: raise AssertionError('超出预声明反例前向预算')
    points = np.column_stack((unique_keys >> 16, (unique_keys >> 8)&255, unique_keys&255)).astype(np.uint8)
    middle_output = intermediate_oracle(middle, points)  # 本阶段唯一中间模型前向调用。
    lookup = {int(key): middle_output[i] for i, key in enumerate(unique_keys)}
    _, common_frac = middle.tables()
    for result in image_results.values():
        phase1 = phase2 = 0.
        for example in result['top_degradation_colours']:
            rgb, prediction = example['rgb'], lookup[example['key']]
            error = prediction.astype(np.int32)-np.asarray(example['target'], np.int32)
            mid_distance = float(np.sqrt(np.sum(error*error)))
            d1, d2 = mid_distance-example['old_distance'], example['new_distance']-mid_distance
            if abs(d1+d2-(example['new_distance']-example['old_distance'])) > 1e-12:
                raise AssertionError('反例阶段距离增量不守恒')
            delta_frac = [[int(candidate['channel_frac'][c, a, rgb[a]])-int(common_frac[a, rgb[a]]) for a in range(3)] for c in range(3)]
            example.update(intermediate_prediction=prediction.tolist(), intermediate_distance=mid_distance,
                old_to_intermediate_distance_delta=d1, intermediate_to_new_distance_delta=d2,
                old_to_intermediate_weighted_delta=example['image_count']*d1,
                intermediate_to_new_weighted_delta=example['image_count']*d2,
                shared_cell=[int(middle.tables()[0][a, rgb[a]]) for a in range(3)],
                common_frac_before=[int(common_frac[a, rgb[a]]) for a in range(3)],
                channel_frac_after=[[int(candidate['channel_frac'][c, a, rgb[a]]) for a in range(3)] for c in range(3)],
                channel_frac_delta=delta_frac)
            phase1 += example['image_count']*d1; phase2 += example['image_count']*d2
        result['top_set_phase_deltas'] = {'old_to_intermediate': phase1, 'intermediate_to_new': phase2,
            'total': phase1+phase2, 'scope': '只覆盖按旧新退化选择的top颜色，不能归因整图累计变化'}
    csv_write(args.output/'frequency-groups.csv', group_rows)
    np.savez_compressed(args.output/'frequency-group-histograms.npz', **hist_archive)
    np.savez_compressed(args.output/'intermediate-counterexamples.npz', keys=unique_keys, points=points, prediction=middle_output)
    if sources != {path.relative_to(ROOT).as_posix(): digest(path) for path in files}: raise ValueError('统计中源码改变')
    result = {'run_identity': run['identity_sha256'], 'images': image_results,
        'new_nodes_idx_grid_equal_intermediate': True, 'intermediate_forward_calls': 1,
        'intermediate_forward_unique_colours': len(unique_keys), 'whole_image_model_forward_calls': 0,
        'image_decodes': 2, 'artifact_sha256': {name: digest(args.output/name) for name in
            ('frequency-groups.csv', 'frequency-group-histograms.npz', 'intermediate-counterexamples.npz', 'measured-source.zip')},
        'limits': plan['limits']}
    (args.output/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'images': {name: {key: value[key] for key in ('old', 'new', 'change', 'frequency_groups', 'top_set_phase_deltas')} for name, value in image_results.items()},
        'intermediate_unique_colours': len(unique_keys)}, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__': main()
