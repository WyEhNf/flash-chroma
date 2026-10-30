"""只读四方向流，给出shared-idx cell离散方向的max与均值可行性证书。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import io, study_provenance
from run_channel_tail_nodes import load_model, digest, save


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖cell可行证书')
    args.output.mkdir(parents=True)
    cache = args.cache_root.resolve()
    source = ROOT/'artifacts/velvia-body-diagonals-v1'
    run = json.loads((source/'run.json').read_text(encoding='utf-8'))
    streams = json.loads((source/'manifest.json').read_text(encoding='utf-8'))['streams_sha256']
    model_path = cache/'artifacts/velvia-channel-coordinates-v1/channel-coordinates.npz'
    if digest(model_path) != run['input_sha256']['model']:
        raise ValueError('不允许换基线')
    model = load_model(model_path)
    table_path = cache/'artifacts/chain-error-cache/source-2ff0a4e385f9f9e49ca02f63/table.lut256'
    reference = io.load_full(table_path, mmap=True).reshape(-1, 3)
    mass_path = cache/'artifacts/cinema-axis-calibration-v1/photo-arrival-frequency.npy'
    mass = np.asarray(np.load(mass_path, mmap_mode='r'), np.float64); mass /= mass.sum()
    masks = [0, 1, 2, 4]
    outputs = [np.memmap(source/f'mask{k}.rgb', np.uint8, 'r', shape=reference.shape) for k in masks]
    for k in masks:
        if digest(source/f'mask{k}.rgb') != streams[f'mask{k}.rgb']:
            raise ValueError('四方向流发生改变')
    cells = (model.m-1)**3
    stats = np.zeros((4, cells, 5), np.float64)
    maxsq = np.zeros((4, cells), np.int32)
    counts = np.zeros(cells, np.int64)
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    hotspot_keys = []
    for start in range(0, len(reference), 65536):
        keys = np.arange(start, start+65536, dtype=np.int64)
        rgb = np.column_stack((keys >> 16, (keys >> 8)&255, keys&255)).astype(np.uint8)
        ids = ((model.idx[0, rgb[:, 0]].astype(np.int64)*(model.m-1)+model.idx[1, rgb[:, 1]])*(model.m-1)+model.idx[2, rgb[:, 2]])
        counts += np.bincount(ids, minlength=cells)
        for d, output in enumerate(outputs):
            delta = output[start:start+len(keys)].astype(np.int32)-reference[start:start+len(keys)].astype(np.int32)
            squared = np.sum(delta*delta, axis=1, dtype=np.int32)
            values = [root[squared], squared, mass[keys]*root[squared], mass[keys]*squared, squared > 40]
            for n, values1 in enumerate(values):
                stats[d, :, n] += np.bincount(ids, weights=values1, minlength=cells)
            np.maximum.at(maxsq[d], ids, squared)
            if d == 0:
                hotspot_keys.extend(int(v) for v in keys[squared == 1682])
    np.savez_compressed(args.output/'cell-statistics.npz', stats=stats, max_squared=maxsq, counts=counts, masks=masks)
    metrics = ['distance_sum', 'squared_sum', 'training_frequency_mean', 'training_frequency_squared', 'count_above_40']
    baseline = stats[0].sum(axis=0)
    floor = int(maxsq.min(axis=0).max())
    results = {'max_squared_floor_ignoring_other_metrics': floor, 'baseline_metrics': dict(zip(metrics, baseline.tolist())),
        'baseline_max_squared': int(maxsq[0].max()), 'shared_idx_cells': cells, 'nonempty_cells': int(np.count_nonzero(counts)),
        'hotspots': [], 'thresholds': {}, 'new_default': False, 'native_calls': 0, 'performance_calls': 0}
    for key in hotspot_keys:
        rgb = [key >> 16, (key >> 8)&255, key&255]
        cell = int((model.idx[0, rgb[0]]*np.int64(model.m-1)+model.idx[1, rgb[1]])*(model.m-1)+model.idx[2, rgb[2]])
        results['hotspots'].append({'rgb': rgb, 'cell': cell, 'cell_max_squared_by_mask': maxsq[:, cell].tolist(),
            'cell_metrics_by_mask': stats[:, cell].tolist(), 'points_in_cell': int(counts[cell])})
    for cap in sorted(set([1681, floor]), reverse=True):
        legal = maxsq <= cap
        lower = {}
        for metric, label in enumerate(metrics):
            costs = np.where(legal, stats[:, :, metric], np.inf)
            chosen = np.argmin(costs, axis=0)
            aggregate = stats[chosen, np.arange(cells)].sum(axis=0)
            lower[label] = {'lower_bound': float(aggregate[metric]), 'baseline': float(baseline[metric]),
                'selected_counts': np.bincount(chosen, minlength=4).tolist(),
                'selected_max_squared': int(maxsq[chosen, np.arange(cells)].max()),
                'all_metrics': dict(zip(metrics, aggregate.tolist())),
                'all_five_aggregate_constraints_pass': bool(np.all(aggregate <= baseline+1e-7))}
            np.save(args.output/f'cap{cap}-min-{label}-choices.npy', np.array(masks, np.uint8)[chosen])
        results['thresholds'][str(cap)] = {'all_cells_have_option': bool(np.all(legal.any(axis=0))),
            'independent_metric_lower_bounds': lower,
            'impossible_mean_or_p99_count_certificate': bool(any(v['lower_bound'] > v['baseline']+1e-7 for v in lower.values()))}
    save(args.output/'results.json', results)
    save(args.output/'run.json', {'input_sha256': {'model': digest(model_path), 'table': digest(table_path), 'mass': digest(mass_path), **streams},
        'source_sha256': {Path(__file__).relative_to(ROOT).as_posix(): digest(Path(__file__))},
        'environment': study_provenance.environment_fingerprint(),
        'policy': '只聚合既有四方向完整流；每cell单选方向，先给最坏误差最优下界及cap1681/最优cap的五种独立最优均值下界；没有多次搜索、照片反馈或原生。',
        'scope': '独立metric最优是必要可行性下界，不自动保证五约束同时可行。整cell选择可能面间不连续；当前不作原生/边界/照片终验结论。'})
    print(json.dumps({'max_squared_floor': floor, 'hotspots': results['hotspots'], 'thresholds': results['thresholds']}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
