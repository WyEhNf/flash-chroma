"""仅聚合已有Velvia字节，分离参考裁剪端点与邻饱和/内部输出的误差贡献。"""
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
from lutlab import study_provenance

MAXIMUM_SQUARED = 3*255**2
DISTANCE = np.sqrt(np.arange(MAXIMUM_SQUARED+1, dtype=np.float64))
GROUPS = ('clipped', 'near_saturation', 'interior')
MEASURES = ('cube', 'photos60')


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def checked(spec):
    path = ROOT/spec['path']
    if digest(path) != spec['sha256']:
        raise ValueError(f'冻结输入SHA不同：{path}')
    return path


def hmetrics(hist):
    count = int(hist.sum())
    squared_sum = int(hist@np.arange(len(hist), dtype=np.int64))
    distance_sum = float(hist@DISTANCE)
    return {'count': count, 'distance_sum': distance_sum, 'squared_sum': squared_sum,
        'mean': distance_sum/count if count else None, 'rms': float(np.sqrt(squared_sum/count)) if count else None,
        'nonzero_error_count': count-int(hist[0]),
        **{f'gt_{t}_count': int(hist[t*t+1:].sum()) for t in (3, 7)},
        **{f'gt_{t}_distance_sum': float(hist[t*t+1:]@DISTANCE[t*t+1:]) for t in (3, 7)}}


def empty_channel():
    return {'count': 0, 'same_nonzero_count': 0, 'other_nonzero_count': 0, 'total_nonzero_count': 0,
        'same_signed_sum': 0, 'same_abs_sum': 0, 'same_squared_sum': 0, 'other_squared_sum': 0,
        'total_squared_sum': 0, 'total_distance_sum': 0., 'other_distance_sum': 0.}


def add_channel(record, e, squared, frequency):
    # int64先提升，再乘次数；本任务完整频数使所有和远小于2^63。
    f = frequency.astype(np.int64, copy=False)
    same = e.astype(np.int64, copy=False)
    same_squared = same*same
    other_squared = squared.astype(np.int64, copy=False)-same_squared
    record['count'] += int(f.sum())
    record['same_nonzero_count'] += int(f[same != 0].sum())
    record['other_nonzero_count'] += int(f[other_squared != 0].sum())
    record['total_nonzero_count'] += int(f[squared != 0].sum())
    record['same_signed_sum'] += int(np.sum(f*same, dtype=np.int64))
    record['same_abs_sum'] += int(np.sum(f*np.abs(same), dtype=np.int64))
    record['same_squared_sum'] += int(np.sum(f*same_squared, dtype=np.int64))
    record['other_squared_sum'] += int(np.sum(f*other_squared, dtype=np.int64))
    record['total_squared_sum'] += int(np.sum(f*squared.astype(np.int64), dtype=np.int64))
    record['total_distance_sum'] += float(f@DISTANCE[squared])
    record['other_distance_sum'] += float(f@DISTANCE[other_squared])


def describe_channel(record, total):
    n, own, other = record['count'], record['same_squared_sum'], record['other_squared_sum']
    if own+other != record['total_squared_sum']:
        raise AssertionError('同通道与其它通道SSE没有守恒')
    return {**record, 'population_mass': n/total['count'],
        'same_signed_mean': record['same_signed_sum']/n if n else None,
        'same_absolute_mean': record['same_abs_sum']/n if n else None,
        'same_channel_rmse': float(np.sqrt(own/n)) if n else None,
        'other_two_channel_vector_mean': record['other_distance_sum']/n if n else None,
        'other_two_channel_vector_rms': float(np.sqrt(other/n)) if n else None,
        'same_channel_fraction_of_cohort_sse': own/(own+other) if own+other else None,
        'cohort_distance_error_share': record['total_distance_sum']/total['distance_sum'],
        'same_channel_fraction_of_overall_sse': own/total['squared_sum'],
        'other_channel_fraction_of_overall_sse': other/total['squared_sum']}


def csv_write(path, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=ROOT/'experiments/velvia-output-clipping-v1.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.plan, args.output = args.plan.resolve(), args.output.resolve()
    if args.output.exists():
        raise ValueError('不覆盖已冻结归因')
    plan = read(args.plan)
    paths = {name: checked(spec) for name, spec in plan['inputs'].items()}
    old_result, old_run = read(paths['historical_results']), read(paths['historical_run'])
    old = old_result['candidates']['joint_grid_iter1600']
    if (old_result['run_identity'] != old_run['identity_sha256']
            or old_run['identity_sha256'] != study_provenance.identity_digest(old_run['identity'])
            or old['model_sha256'] != plan['inputs']['model']['sha256']
            or old['cube']['prediction_sha256'] != plan['inputs']['stream']['sha256']
            or old['cube']['reference_sha256'] != plan['inputs']['table']['sha256']):
        raise ValueError('原2dd完整字节与历史模型/表/运行身份未绑定')
    frequency = np.load(paths['frequency'], mmap_mode='r')
    training, partition = read(paths['frequency_metadata']), read(paths['partition'])
    if (frequency.shape != (256**3,) or frequency.dtype != np.uint32
            or training['prefix_model_sha256'] != []
            or training['artifact_sha256']['photo-arrival-frequency.npy'] != plan['inputs']['frequency']['sha256']
            or hashlib.sha256(memoryview(frequency)).hexdigest() != plan['frequency_array_sha256']
            or int(frequency.sum(dtype=np.uint64)) != 60*1024*768
            or [r['id'] for r in training['training_images']] != [r['id'] for r in partition['training']['images']]
            or [r['sha256'] for r in training['training_images']] != [r['file_sha256'] for r in partition['training']['images']]):
        raise ValueError('不是已冻结原60训练图全部原色频数')
    table = np.memmap(paths['table'], np.uint8, 'r', shape=(256**3, 3))
    stream = np.memmap(paths['stream'], np.uint8, 'r', shape=table.shape)
    if paths['table'].stat().st_size != 256**3*3 or paths['stream'].stat().st_size != 256**3*3:
        raise ValueError('原表/输出大小不是完整RGB8域')
    files = [Path(__file__), args.plan, ROOT/'python/lutlab/study_provenance.py']
    sources = {p.relative_to(ROOT).as_posix(): digest(p) for p in files}
    args.output.mkdir(parents=True)
    run = {'plan': plan, 'plan_sha256': digest(args.plan), 'source_sha256': sources,
        'environment': study_provenance.environment_fingerprint(),
        'input_sha256': {name: digest(path) for name, path in paths.items()},
        'scope': '读取已有字节/频数的一次分块统计；不加载模型前向/图片解码或native'}
    run['identity_sha256'] = study_provenance.identity_digest(run)
    (args.output/'run.json').write_text(json.dumps(run, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(ROOT).as_posix())
    hist = np.zeros((2, 3, MAXIMUM_SQUARED+1), np.int64)
    # 通道条件会重叠；all/gt3/gt7分别保存，不当成互斥总表。
    channels = {(measure, channel, endpoint, band): empty_channel()
        for measure in MEASURES for channel in range(3) for endpoint in (0, 255) for band in ('all', 'gt3', 'gt7')}
    for start in range(0, len(table), 1 << 18):
        stop = min(start+(1 << 18), len(table))
        target = table[start:stop]
        error = stream[start:stop].astype(np.int32)-target.astype(np.int32)
        squared = np.sum(error*error, axis=1, dtype=np.int32)
        clipped = np.any((target == 0) | (target == 255), axis=1)
        near = ~clipped & np.any(((target >= 1) & (target <= 4)) | ((target >= 251) & (target <= 254)), axis=1)
        interior = np.all((target >= 5) & (target <= 250), axis=1)
        if np.any(clipped.astype(np.int8)+near.astype(np.int8)+interior.astype(np.int8) != 1):
            raise AssertionError('参考输出三组没有互斥穷尽')
        freq = frequency[start:stop].astype(np.int64)
        for group, selected in enumerate((clipped, near, interior)):
            hist[0, group] += np.bincount(squared[selected], minlength=MAXIMUM_SQUARED+1)
            # 次数和小于2^53，bincount浮点整数权重归约后仍精确，可无损转int64。
            hist[1, group] += np.bincount(squared[selected], weights=freq[selected], minlength=MAXIMUM_SQUARED+1).astype(np.int64)
        for channel in range(3):
            for endpoint in (0, 255):
                base = target[:, channel] == endpoint
                for band, cut in (('all', -1), ('gt3', 9), ('gt7', 49)):
                    selected = base & (squared > cut)
                    if not np.any(selected):
                        continue
                    for measure, weight in (('cube', np.ones(np.count_nonzero(selected), np.int64)), ('photos60', freq[selected])):
                        add_channel(channels[(measure, channel, endpoint, band)],
                            error[selected, channel], squared[selected], weight)
    totals = {measure: hmetrics(hist[i].sum(axis=0)) for i, measure in enumerate(MEASURES)}
    if (totals['cube']['count'] != 256**3 or totals['photos60']['count'] != 60*1024*768
            or abs(totals['cube']['mean']-old['cube']['mean']) > 1e-12
            or abs(totals['cube']['rms']-old['cube']['rms']) > 1e-12):
        raise AssertionError('全域数量/旧mean或RMS没有复现')
    groups, rows = {}, []
    for i, measure in enumerate(MEASURES):
        total = totals[measure]
        groups[measure] = {}
        for j, group in enumerate(GROUPS):
            value = hmetrics(hist[i, j])
            value.update(population_mass=value['count']/total['count'],
                distance_error_share=value['distance_sum']/total['distance_sum'],
                mean_contribution=value['distance_sum']/total['count'])
            value['error_share_over_population_mass'] = value['distance_error_share']/value['population_mass'] if value['count'] else None
            for threshold in (3, 7):
                count, distance = value[f'gt_{threshold}_count'], value[f'gt_{threshold}_distance_sum']
                value.update({f'gt_{threshold}_share_of_all_tail_count': count/total[f'gt_{threshold}_count'],
                    f'gt_{threshold}_share_of_all_tail_distance_sum': distance/total[f'gt_{threshold}_distance_sum'],
                    f'gt_{threshold}_share_of_overall_distance_sum': distance/total['distance_sum']})
            groups[measure][group] = value
            rows.append({'measure': measure, 'group': group, **value})
        if (sum(v['count'] for v in groups[measure].values()) != total['count']
                or sum(v['squared_sum'] for v in groups[measure].values()) != total['squared_sum']
                or abs(sum(v['distance_sum'] for v in groups[measure].values())-total['distance_sum']) > 1e-10*total['distance_sum']):
            raise AssertionError('分组没有保留全体计数/SSE/误差和')
    channel_rows = []
    for (measure, channel, endpoint, band), record in channels.items():
        value = describe_channel(record, totals[measure])
        channel_rows.append({'measure': measure, 'channel': 'RGB'[channel], 'reference': endpoint, 'band': band, **value})
    csv_write(args.output/'groups.csv', rows)
    csv_write(args.output/'channel-residuals.csv', channel_rows)
    np.savez_compressed(args.output/'group-histograms.npz', cube=hist[0], photos60=hist[1])
    if sources != {p.relative_to(ROOT).as_posix(): digest(p) for p in files}:
        raise ValueError('归因期间冻结源码改变')
    result = {'run_identity': run['identity_sha256'], 'totals': totals, 'groups': groups,
        'channel_residuals': channel_rows, 'model_forward_calls': 0, 'image_decodes': 0,
        'artifact_sha256': {name: digest(args.output/name) for name in
            ('groups.csv', 'channel-residuals.csv', 'group-histograms.npz', 'measured-source.zip')},
        'limits': plan['limits'], 'interpretation': plan['interpretation']}
    (args.output/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'totals': totals, 'groups': groups,
        'channel_all': [row for row in channel_rows if row['band'] == 'all']}, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
