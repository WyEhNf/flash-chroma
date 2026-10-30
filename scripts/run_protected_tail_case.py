"""把冻结的完整支撑尾部节点法用于普通四级SLUT及Velvia单级难例。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import time
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numba
import numpy as np
from lutlab import channel_coordinates as cc, channel_global_nodes as cg, channel_joint_nodes as cj
from lutlab import channel_tail_nodes as tail, io, study_provenance
from run_channel_tail_nodes import load_model, digest, save


def inputs(cache, case):
    if case == 'cinema_shared':
        model_path = cache/'artifacts/cinema-axis-calibration-v1/stage1_sweep012/stage1.slut'
        if digest(model_path) != 'af9747e4b396ee8382897cd9af717d7464eccfe066add1262c12ff95582f3fc0':
            raise ValueError('普通共享轴起点不是af974')
        model = cc.from_sparse(io.load_sparse(model_path, competition=True))
        reference_path = cache/'artifacts/cinema-axis-calibration-v1/envelope-reference.npy'
        suffix_path = cache/'artifacts/cinema-axis-calibration-v1/envelope-suffix.npy'
        reference = np.load(reference_path, mmap_mode='r')
        suffix = np.load(suffix_path, mmap_mode='r')
        baseline = cache/'artifacts/cinema-axis-calibration-v1/stage1_sweep012/cube.rgb'
        return model, reference, suffix, {'model': model_path, 'reference': reference_path, 'suffix': suffix_path, 'baseline': baseline}, 14, 36
    model_path = cache/'artifacts/velvia-channel-coordinates-v1/channel-coordinates.npz'
    if digest(model_path) != '3e5f8fd94e8dc9b97dbfea2823896b8dffb6e014b5e6056ab5c10b58a69af3d0':
        raise ValueError('Velvia起点不是3e5f')
    model = load_model(model_path)
    reference_path = cache/'artifacts/chain-error-cache/source-2ff0a4e385f9f9e49ca02f63/table.lut256'
    reference = io.load_full(reference_path, mmap=True).reshape(-1, 3)
    keys = np.arange(256**3, dtype=np.uint32)
    suffix = np.column_stack((keys >> 16, (keys >> 8)&255, keys&255)).astype(np.uint8)
    baseline = cache/'artifacts/velvia-channel-coordinates-accept-v1/cube.rgb'
    return model, reference, suffix, {'model': model_path, 'reference': reference_path, 'baseline': baseline}, 40, 100


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-root', type=Path, required=True)
    parser.add_argument('--case', choices=('cinema_shared', 'velvia'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖新案例')
    args.output.mkdir(parents=True)
    numba.set_num_threads(4)
    cache = args.cache_root.resolve()
    model, reference, suffix, paths, p99_sq, severe_sq = inputs(cache, args.case)
    paths['mass'] = cache/'artifacts/cinema-axis-calibration-v1/photo-arrival-frequency.npy'
    paths['points'] = cache/'artifacts/cinema-axis-calibration-v1/envelope-arrivals.npy'
    mass = np.asarray(np.load(paths['mass'], mmap_mode='r'), np.float64); mass /= mass.sum()
    points = np.load(paths['points'], mmap_mode='r')
    baseline = np.memmap(paths['baseline'], np.uint8, 'r', shape=reference.shape)
    save(args.output/'run.json', {'case': args.case, 'input_sha256': {k: digest(v) for k, v in paths.items()},
        'policy': '一次8色26方向，severe_first排序；双mean/双RMS及p99超阈计数逐节点非增；cap=max(49,本案例当前最佳逐色d²)。没有中途照片选择，没有后续追加轮数。',
        'labels': 'Cinema为四原表逐级RGB8真值及固定三稀疏后缀；Velvia为独立单原表与离线恒等后缀，不冒充四级。',
        'p99_squared': p99_sq, 'severe_squared': severe_sq,
        'source_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in [Path(__file__), ROOT/'python/lutlab/channel_tail_nodes.py']},
        'environment': study_provenance.environment_fingerprint(), 'numba_threads': 4})
    indices, weights = cg.design(model, points)
    acc, _ = cj.accumulate(indices, weights, model.nodes.reshape(-1, 3), reference)
    own = cc.predict(model, points)
    for start in range(0, len(points), 1 << 18):
        key = own[start:start+(1 << 18)].astype(np.int64)@np.array([65536, 256, 1], np.int64)
        np.testing.assert_array_equal(suffix[key], baseline[start:start+len(key)])
    initial, squared = tail.measure(own, reference, suffix, mass, p99_sq, severe_sq)
    caps, colours = np.maximum(49, squared), cj.parity(model.m)
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    current, metrics, records = model, initial.copy(), []
    started = time.perf_counter()
    for colour in range(8):
        change, bad, invalid = tail.gains(indices, weights, acc, reference, suffix, mass,
            current.nodes.reshape(-1, 3), colours, colour, caps, root, 4, p99_sq, severe_sq)
        if invalid:
            raise AssertionError('分色几何或初始cap不符')
        moves, predicted, accepted = tail.select(change, bad, colours, colour, 'severe_first')
        current = tail.apply(current, indices, weights, acc, moves, reference)
        fresh = cc.predict(current, points)
        np.testing.assert_array_equal(fresh, ((acc+io.ONE//2) >> io.Q).astype(np.uint8))
        after, squared = tail.measure(fresh, reference, suffix, mass, p99_sq, severe_sq)
        if np.max(np.abs(after-metrics-predicted)) > 1e-5 or np.any(squared > caps) or np.any(after[:4] > metrics[:4]+1e-5) or after[6] > metrics[6]:
            raise AssertionError('新案例fresh完整支撑收益/cap或均值门禁回退')
        entry = {'colour': colour, 'changed_nodes': len(accepted), 'before': metrics.tolist(), 'after': after.tolist(),
            'maximum_gain_error': float(np.max(np.abs(after-metrics-predicted))), 'max_squared': int(squared.max()),
            'moves': accepted, 'seconds': time.perf_counter()-started}
        records.append(entry); save(args.output/'progress.json', records)
        print(json.dumps({k: entry[k] for k in ('colour', 'changed_nodes', 'after', 'max_squared', 'seconds')}), flush=True)
        metrics = after
    candidate = args.output/'candidate'; candidate.mkdir()
    np.savez_compressed(candidate/'model.npz', format=np.array('channel_coordinates_v1_experimental'),
        grid=current.grid, nodes=current.nodes, shared_idx=current.idx, channel_frac=current.channel_frac)
    base = io.SparseLut(current.grid, current.nodes, current.idx, current.channel_frac[0])
    io.save_sparse(candidate/'candidate-base.slut', base)
    shared = bool(np.all(current.channel_frac == current.channel_frac[0]))
    if not shared:
        current.channel_frac.astype('<u4').tofile(candidate/'channel-frac.bin')
    save(args.output/'summary.json', {'case': args.case, 'before': initial.tolist(), 'after': metrics.tolist(),
        'max_squared': int(squared.max()), 'model_sha256': digest(candidate/'model.npz'),
        'shared_coordinates': shared, 'sidecar_bytes': 0 if shared else 9216,
        'cap_violations': 0, 'fresh_byte_mismatches': 0, 'new_runtime_bytes': 0})


if __name__ == '__main__':
    main()
