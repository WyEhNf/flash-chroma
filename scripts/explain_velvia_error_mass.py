"""只读取已验收输出，按码值/网格单元汇总Velvia误差质量与局部改善上界。"""
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
from lutlab import io, study_provenance


PLAN = {
    'model_sha256': '2dd467b040a4ed25f9000e7debd085af4a07f08d780be2fbcd156c9aa8118947',
    'stream': {'path': 'artifacts/joint-grid-budget-v2/joint_grid_iter1600/cube.rgb',
               'sha256': 'd5453bd8ab99eea82582b3f9710e9b9c40c79ea78e0e58f0c1d818d0910e74d7'},
    'table': {'path': 'artifacts/chain-error-cache/source-2ff0a4e385f9f9e49ca02f63/table.lut256',
              'sha256': '6c4387352bd0845ce597f13dca32f2f808b39439d06ce78b4881922a4fc294b7'},
    'grid': {'path': 'artifacts/joint-grid-full-prepare/baseline-grid.npy',
             'sha256': '1b62bbc42278fc9deb993e1dc3b1c1973fbc9a47aa7e108d891c51cec26d2eb3'},
    'frequency': {'path': 'artifacts/cinema-prefix-stage1-v1/photo-arrival-frequency.npy',
                   'sha256': '1eff7aab15715845bbc3efda68043a62a5c2dd9162f33717cee8bea5d36b756e'},
    'frequency_array_sha256': '20af718acb2868e9d2c1453aea7193bbbaac4c6cf91d8eff79c8185430dac300',
    'frequency_metadata': 'artifacts/cinema-prefix-stage1-v1/training.json',
    'partition': 'artifacts/full-photo-v1/photo-partition.json',
    'historical_results': 'artifacts/joint-grid-budget-v2/full-results.json',
    'scope': '原2dd已存输出的两遍只读聚合；不调用稀疏模型、不拟合、不生成或映射候选',
    'local_proposal': '仅讨论把G轴倒数第3/2内结点放到251/252；取从原倒数第4 knot起所有整数G为保守受影响支撑，其他输入输出保持不变',
}
DISTANCE = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def checked(spec):
    path = ROOT/spec['path']
    if digest(path) != spec['sha256']:
        raise ValueError(f'冻结输入SHA不同：{path}')
    return path


def histogram_metrics(hist):
    n = int(hist.sum())
    cumulative = np.cumsum(hist)
    rank = .99*(n-1)
    lower, upper = np.searchsorted(cumulative, [int(np.floor(rank)), int(np.ceil(rank))], side='right')
    fraction = rank-np.floor(rank)
    p99 = float(DISTANCE[lower]+fraction*(DISTANCE[upper]-DISTANCE[lower]))
    # 相邻顺序统计量之间没有观测；由整数顺序直接确定>=p99集合，避免sqrt平方误差。
    cutoff = int(upper if fraction > 0 and lower != upper else lower)
    return {'n': n, 'mean': float(hist@DISTANCE/n),
        'rms': float(np.sqrt(hist@np.arange(len(hist), dtype=np.float64)/n)),
        'p99': p99, 'max': float(DISTANCE[np.flatnonzero(hist)[-1]]),
        'tail_squared_cutoff': cutoff, 'tail_count': int(hist[cutoff:].sum()),
        'tail_mass': float(hist[cutoff:].sum()/n), 'distance_sum': float(hist@DISTANCE)}


def empty_group(size):
    return {key: np.zeros(size, np.int64 if key.endswith('count') else np.float64) for key in (
        'cube_count', 'cube_distance_sum', 'cube_squared_sum', 'cube_tail_count',
        'photo_count', 'photo_distance_sum', 'photo_squared_sum', 'photo_tail_count', 'photo_cube_tail_count')}


def accumulate(group, keys, squared, frequency, cube_cutoff, photo_cutoff):
    size = len(group['cube_count'])
    distance = DISTANCE[squared]
    fields = {
        'cube_count': None, 'cube_distance_sum': distance, 'cube_squared_sum': squared,
        'cube_tail_count': (squared >= cube_cutoff), 'photo_count': frequency,
        'photo_distance_sum': frequency*distance, 'photo_squared_sum': frequency*squared,
        'photo_tail_count': frequency*(squared >= photo_cutoff),
        'photo_cube_tail_count': frequency*(squared >= cube_cutoff),
    }
    for key, values in fields.items():
        group[key] += np.bincount(keys, weights=values, minlength=size).astype(group[key].dtype)


def describe(group, index, totals):
    nc, npix = int(group['cube_count'][index]), int(group['photo_count'][index])
    cu, ph = float(group['cube_distance_sum'][index]), float(group['photo_distance_sum'][index])
    ct, pt = int(group['cube_tail_count'][index]), int(group['photo_tail_count'][index])
    return {'cube_count': nc, 'cube_mass': nc/totals['cube']['n'],
        'cube_local_mean': cu/nc if nc else None,
        'cube_mean_contribution': cu/totals['cube']['n'],
        'cube_error_share': cu/totals['cube']['distance_sum'],
        'cube_tail_count': ct, 'cube_tail_mass': ct/totals['cube']['n'],
        'cube_tail_share': ct/totals['cube']['tail_count'],
        'photo_count': npix, 'photo_mass': npix/totals['photos']['n'],
        'photo_local_mean': ph/npix if npix else None,
        'photo_mean_contribution': ph/totals['photos']['n'],
        'photo_error_share': ph/totals['photos']['distance_sum'],
        'photo_tail_count': pt, 'photo_tail_mass': pt/totals['photos']['n'],
        'photo_tail_share': pt/totals['photos']['tail_count'],
        'photo_cube_tail_count': int(group['photo_cube_tail_count'][index])}


def concentration(values):
    ordered = np.sort(values)[::-1]
    total = float(ordered.sum())
    cumulative = np.cumsum(ordered)/total
    return {'nonzero_cells': int(np.count_nonzero(values)),
        'cells_for_50pct': int(np.searchsorted(cumulative, .5)+1),
        'cells_for_90pct': int(np.searchsorted(cumulative, .9)+1),
        'top_shares': {str(k): float(ordered[:k].sum()/total) for k in (1, 10, 100, 1000)}}


def error_bands(hist, total):
    result = []
    previous = -1
    for label, upper in (('0', 0), ('(0,1]', 1), ('(1,2]', 4), ('(2,3]', 9),
                         ('(3,5]', 25), ('(5,7]', 49), ('>7', len(hist)-1)):
        selected = hist[previous+1:upper+1]
        error = float(selected@DISTANCE[previous+1:upper+1])
        result.append({'distance_band': label, 'count': int(selected.sum()),
            'mass': float(selected.sum()/total['n']), 'mean_contribution': error/total['n'],
            'error_share': error/total['distance_sum']})
        previous = upper
    return result


def csv_write(path, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖既有归因')
    paths = {name: checked(PLAN[name]) for name in ('stream', 'table', 'grid', 'frequency')}
    old = read(ROOT/PLAN['historical_results'])['candidates']['joint_grid_iter1600']
    if (old['model_sha256'] != PLAN['model_sha256']
            or old['cube']['prediction_sha256'] != PLAN['stream']['sha256']
            or old['cube']['reference_sha256'] != PLAN['table']['sha256']):
        raise ValueError('已验收流与模型/原表绑定不同')
    table = io.load_full(paths['table'], mmap=True).reshape(-1, 3)
    stream = np.memmap(paths['stream'], np.uint8, 'r', shape=(256**3, 3))
    grid = np.load(paths['grid'])
    if grid.shape != (3, 33):
        raise ValueError('需要当前33³小数网格')
    cell_index, _ = io.axis_tables(grid)
    frequency = np.load(paths['frequency'], mmap_mode='r')
    training, partition = read(ROOT/PLAN['frequency_metadata']), read(ROOT/PLAN['partition'])
    if (frequency.dtype != np.uint32 or frequency.shape != (256**3,)
            or training['prefix_model_sha256'] != []
            or training['artifact_sha256']['photo-arrival-frequency.npy'] != PLAN['frequency']['sha256']
            or hashlib.sha256(frequency.astype('<u4', copy=False).tobytes()).hexdigest() != PLAN['frequency_array_sha256']
            or int(frequency.sum(dtype=np.uint64)) != 60*1024*768
            or [r['id'] for r in training['training_images']] != [r['id'] for r in partition['training']['images']]
            or [r['sha256'] for r in training['training_images']] != [r['file_sha256'] for r in partition['training']['images']]):
        raise ValueError('频数不是冻结原60图原色频数')
    hist, photo_hist = np.zeros(len(DISTANCE), np.int64), np.zeros(len(DISTANCE), np.int64)
    # 第一遍只做全体旧误差直方图，以准确确定两种不同测度的p99集合。
    for start in range(0, len(table), 1 << 18):
        stop = min(start+(1 << 18), len(table))
        error = stream[start:stop].astype(np.int32)-table[start:stop].astype(np.int32)
        squared = np.sum(error*error, axis=1, dtype=np.int32)
        hist += np.bincount(squared, minlength=len(DISTANCE))
        photo_hist += np.bincount(squared, weights=frequency[start:stop], minlength=len(DISTANCE)).astype(np.int64)
    totals = {'cube': histogram_metrics(hist), 'photos': histogram_metrics(photo_hist)}
    if totals['cube']['n'] != 256**3 or totals['photos']['n'] != 60*1024*768:
        raise AssertionError('直方图没有保留全部颜色/照片频数')
    axes = [empty_group(256) for _ in range(3)]
    cells = empty_group(32**3)
    # 第二遍仍仅比较已有字节，不调用模型；所有汇总共用固定两个p99集合。
    for start in range(0, len(table), 1 << 18):
        stop = min(start+(1 << 18), len(table))
        keys = np.arange(start, stop, dtype=np.int64)
        codes = (keys >> 16, (keys >> 8) & 255, keys & 255)
        error = stream[start:stop].astype(np.int32)-table[start:stop].astype(np.int32)
        squared = np.sum(error*error, axis=1, dtype=np.int32)
        # 转float64后做乘法，避免uint32频数和int32误差平方相乘的溢出。
        freq = frequency[start:stop].astype(np.float64)
        for axis in range(3):
            accumulate(axes[axis], codes[axis], squared, freq,
                       totals['cube']['tail_squared_cutoff'], totals['photos']['tail_squared_cutoff'])
        cell_keys = (cell_index[0, codes[0]].astype(np.int32)*32+cell_index[1, codes[1]])*32+cell_index[2, codes[2]]
        accumulate(cells, cell_keys, squared, freq,
                   totals['cube']['tail_squared_cutoff'], totals['photos']['tail_squared_cutoff'])
    for group in [*axes, cells]:
        for measure, prefix in (('cube', 'cube'), ('photos', 'photo')):
            total = totals[measure]
            if (int(group[prefix+'_count'].sum()) != total['n']
                    or int(group[prefix+'_tail_count'].sum()) != total['tail_count']
                    or abs(float(group[prefix+'_distance_sum'].sum())-total['distance_sum']) > 1e-11*total['distance_sum']):
                raise AssertionError('分组贡献/尾部没有与全局测度守恒')
    axis_rows, interval_rows, axis_top = [], [], {}
    for axis, group in enumerate(axes):
        name = 'RGB'[axis]
        for code in range(256):
            axis_rows.append({'axis': name, 'code': code, 'cell': int(cell_index[axis, code]), **describe(group, code, totals)})
        intervals = {key: np.bincount(cell_index[axis], weights=value, minlength=32).astype(value.dtype)
                     for key, value in group.items()}
        for cell in range(32):
            codes_here = np.flatnonzero(cell_index[axis] == cell)
            interval_rows.append({'axis': name, 'cell': cell, 'knot_lo': float(grid[axis, cell]),
                'knot_hi': float(grid[axis, cell+1]),
                'code_lo': int(codes_here[0]) if len(codes_here) else None,
                'code_hi': int(codes_here[-1]) if len(codes_here) else None, **describe(intervals, cell, totals)})
        axis_top[name] = {criterion: [{'code': int(code), **describe(group, code, totals)} for code in
            np.argsort(-group[field], kind='stable')[:16]] for criterion, field in (
                ('photo_error', 'photo_distance_sum'), ('cube_tail', 'cube_tail_count'))}
    def cell_record(key):
        xyz = [int(key)//1024, (int(key)//32) % 32, int(key) % 32]
        return {'cell': xyz, 'knot_lo': [float(grid[a, xyz[a]]) for a in range(3)],
                'knot_hi': [float(grid[a, xyz[a]+1]) for a in range(3)], **describe(cells, key, totals)}
    cell_tops = {name: [cell_record(key) for key in np.argsort(-cells[field], kind='stable')[:30]]
        for name, field in (('photo_error', 'photo_distance_sum'), ('cube_tail', 'cube_tail_count'))}
    g_start = int(np.ceil(grid[1, -4]))
    g_error = float(axes[1]['photo_distance_sum'][g_start:].sum())
    upper = {'last_four_g_knots': grid[1, -4:].tolist(), 'integer_codes': [g_start, 255],
        'photo_pixels': int(axes[1]['photo_count'][g_start:].sum()),
        'photo_mass': float(axes[1]['photo_count'][g_start:].sum()/totals['photos']['n']),
        'photo_mean_absolute_improvement_upper_bound': g_error/totals['photos']['n'],
        'photo_mean_relative_improvement_upper_bound': g_error/totals['photos']['distance_sum'],
        'photo_mean_lower_bound_if_only_region_changes': totals['photos']['mean']-g_error/totals['photos']['n'],
        'cube_tail_share': float(axes[1]['cube_tail_count'][g_start:].sum()/totals['cube']['tail_count']),
        'photo_tail_share': float(axes[1]['photo_tail_count'][g_start:].sum()/totals['photos']['tail_count']),
        'excluded_as_3pct_training_mean_solution': bool(g_error < .03*totals['photos']['distance_sum']),
        'limits': '假定支撑内误差全部清零且支撑外完全不变的宽松上界；仅60训练图测度，非20/100图数学不可能性；全局节点重拟合可能改变支撑外，不适用此界'}
    source_files = [Path(__file__), ROOT/'python/lutlab/io.py', ROOT/'python/lutlab/study_provenance.py']
    result = {'plan': PLAN, 'environment': study_provenance.environment_fingerprint(),
        'source_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in source_files},
        'input_sha256': {name: digest(path) for name, path in paths.items()},
        'metadata_sha256': {name: digest(ROOT/PLAN[name]) for name in ('frequency_metadata', 'partition', 'historical_results')},
        'totals': totals, 'tail_definition': '各测度distance>=其自身p99；离散平台的质量可以大于1%，另列照片落入cube尾部的像素数',
        'axis_top_codes': axis_top, 'top_cells': cell_tops,
        'cell_concentration': {'photo_error': concentration(cells['photo_distance_sum']),
                               'cube_tail': concentration(cells['cube_tail_count'])},
        'error_bands': {'cube': error_bands(hist, totals['cube']), 'photos': error_bands(photo_hist, totals['photos'])},
        'upper_g_support': upper, 'conservation_checks': '全部轴/单元的数量、误差和、尾部数量与全局一致',
        'limits': '旧已验收流的描述统计；均值贡献不是因果可修复收益，不能单凭分组区分量化与拟合误差；无新模型、拟合、全域映射或参数扫描'}
    args.output.mkdir(parents=True)
    csv_write(args.output/'axis-codes.csv', axis_rows)
    csv_write(args.output/'axis-grid-intervals.csv', interval_rows)
    np.savez_compressed(args.output/'cell-aggregates.npz', grid=grid, cell_index=cell_index,
                        cube_histogram=hist, photo_histogram=photo_hist, **cells)
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in source_files:
            if digest(path) != result['source_sha256'][path.relative_to(ROOT).as_posix()]:
                raise ValueError('只读归因期间相关源码改变')
            archive.write(path, path.relative_to(ROOT).as_posix())
    result['aggregate_sha256'] = {name: digest(args.output/name) for name in
        ('axis-codes.csv', 'axis-grid-intervals.csv', 'cell-aggregates.npz')}
    (args.output/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'totals': totals, 'upper_g_support': upper,
        'cell_concentration': result['cell_concentration'], 'error_bands': result['error_bands'],
        'top_photo_cells': cell_tops['photo_error'][:8], 'top_cube_tail_cells': cell_tops['cube_tail'][:8]},
        ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
