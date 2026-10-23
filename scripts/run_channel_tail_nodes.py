"""从a399出发冻结两条尾部目标，各一次八色节点扫描；不改变运行时表示。"""
from __future__ import annotations
import argparse
import hashlib
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


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def load_model(path):
    with np.load(path) as data:
        model = cc.ChannelLut(data['grid'], data['nodes'], data['shared_idx'], data['channel_frac'])
    cc.validate(model)
    return model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    cache = args.cache_root.resolve()
    if args.output.exists():
        raise ValueError('不覆盖旧实验')
    args.output.mkdir(parents=True)
    numba.set_num_threads(4)
    files = {
        'model': cache/'artifacts/cinema-current-anchor-v1/current-anchor-pipeline.npz',
        'reference': cache/'artifacts/cinema-axis-calibration-v1/envelope-reference.npy',
        'suffix': cache/'artifacts/cinema-axis-calibration-v1/envelope-suffix.npy',
        'mass': cache/'artifacts/cinema-axis-calibration-v1/photo-arrival-frequency.npy',
        'points': cache/'artifacts/cinema-axis-calibration-v1/envelope-arrivals.npy',
        'baseline': cache/'artifacts/cinema-current-anchor-accept-v1/cube.rgb',
    }
    baseline_sha = '3c9ce8d9'
    model = load_model(files['model'])
    if digest(files['model']) != 'a399b72a2222acef815b6405ebd0132f94f1f3a4e4315f957e90b81f836744bb':
        raise ValueError('不是当前a399模型')
    reference = np.load(files['reference'], mmap_mode='r')
    suffix = np.load(files['suffix'], mmap_mode='r')
    points = np.load(files['points'], mmap_mode='r')
    mass = np.asarray(np.load(files['mass'], mmap_mode='r'), np.float64)
    mass /= mass.sum()
    baseline = np.memmap(files['baseline'], np.uint8, 'r', shape=(256**3, 3))
    if not digest(files['baseline']).startswith(baseline_sha):
        raise ValueError('不是当前完整四级流')
    identity = {
        'parent_commit': '16ae431', 'model': 'a399',
        'input_sha256': {k: digest(p) for k, p in files.items()},
        'source_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in
                          [Path(__file__), ROOT/'python/lutlab/channel_tail_nodes.py']},
        'environment': study_provenance.environment_fingerprint(), 'numba_threads': 4,
        'policy': '固定两模式severe_first/p99_first，各从同a399起步八色各一次26方向；双mean/双RMS/p99计数不增；cap=max(49,a399逐色d2)，最终百图只验不调参。',
        'labels': '本阶段显式以四个原表串联的RGB8 reference作整链优化目标；前三后缀固定实际稀疏模型，仍实际执行四次独立整数映射。不是上一轮独立T1/S(T1)双项标签。',
        'limits': '历史100图再次使用，不声称盲测；未获官方对分输出侧表许可；没有新增运行时残差表或额外节点。'
    }
    save(args.output/'run.json', identity)
    started = time.perf_counter()
    print('建立冻结a399完整设计及真实整数缓存', flush=True)
    indices, weights = cg.design(model, points)
    original_acc, _ = cj.accumulate(indices, weights, model.nodes.reshape(-1, 3), reference)
    original_output = ((original_acc+io.ONE//2) >> io.Q).astype(np.uint8)
    np.testing.assert_array_equal(original_output, cc.predict(model, points))
    initial, base_square = tail.measure(original_output, reference, suffix, mass)
    for start in range(0, len(points), 1 << 18):
        own = original_output[start:start+(1 << 18)]
        key = own.astype(np.int64)@np.array([65536, 256, 1], np.int64)
        np.testing.assert_array_equal(suffix[key], baseline[start:start+len(own)])
    caps = np.maximum(49, base_square)
    colours = cj.parity(model.m)
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    save(args.output/'baseline.json', {'objectives': initial.tolist(), 'maximum_squared_error': int(base_square.max()),
                                     'offline_design_bytes': indices.nbytes+weights.nbytes})
    del original_output
    for mode in ('severe_first', 'p99_first'):
        current, acc, metrics = model, original_acc.copy(), initial.copy()
        folder = args.output/mode
        folder.mkdir()
        records = []
        for colour in range(8):
            change, bad, invalid = tail.gains(indices, weights, acc, reference, suffix, mass,
                current.nodes.reshape(-1, 3), colours, colour, caps, root, 4)
            if invalid:
                raise AssertionError('八色几何或当前cap不符')
            moves, predicted, accepted = tail.select(change, bad, colours, colour, mode)
            current = tail.apply(current, indices, weights, acc, moves, reference)
            fresh = cc.predict(current, points)
            np.testing.assert_array_equal(fresh, ((acc+io.ONE//2) >> io.Q).astype(np.uint8))
            measured, squared = tail.measure(fresh, reference, suffix, mass)
            if np.any(squared > caps) or np.max(np.abs(measured-metrics-predicted)) > 1e-5:
                raise AssertionError('fresh收益或cap不符')
            if np.any(measured[:4] > metrics[:4]+1e-5) or measured[6] > metrics[6]:
                raise AssertionError('mean/RMS/p99计数门禁回退')
            entry = {'colour': colour, 'changed_nodes': len(accepted), 'before': metrics.tolist(),
                     'after': measured.tolist(), 'predicted': predicted.tolist(),
                     'maximum_gain_error': float(np.max(np.abs(measured-metrics-predicted))),
                     'maximum_squared_error': int(squared.max()), 'moves': accepted,
                     'seconds': time.perf_counter()-started}
            records.append(entry)
            save(folder/'progress.json', records)
            print(json.dumps({k: entry[k] for k in ('colour', 'changed_nodes', 'after', 'maximum_squared_error', 'seconds')}), flush=True)
            metrics = measured
        np.savez_compressed(folder/'model.npz', format=np.array('channel_coordinates_v1_experimental'),
            grid=current.grid, nodes=current.nodes, shared_idx=current.idx, channel_frac=current.channel_frac)
        base = io.load_sparse(cache/'artifacts/cinema-current-anchor-accept-v1/candidate-base.slut')
        base.nodes = current.nodes
        io.save_sparse(folder/'candidate-base.slut', base)
        current.channel_frac.astype('<u4').tofile(folder/'channel-frac.bin')
        save(folder/'summary.json', {'mode': mode, 'before': initial.tolist(), 'after': metrics.tolist(),
             'model_sha256': digest(folder/'model.npz'), 'changed_node_components': int(np.count_nonzero(current.nodes != model.nodes)),
             'maximum_squared_error': int(squared.max()), 'full_reference_training': True,
             'new_runtime_bytes': 0, 'fresh_byte_mismatches': 0, 'cap_violations': 0,
             'seconds': time.perf_counter()-started})
    print('两固定候选完成，待另行完整独立oracle/照片/原生验收', flush=True)


if __name__ == '__main__':
    main()
