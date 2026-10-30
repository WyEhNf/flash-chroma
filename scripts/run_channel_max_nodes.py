"""冻结两扫±2/±4尾部节点批量预算交换，严格保护首阶段incumbent均值。"""
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
from lutlab import channel_tail_nodes as tail, channel_max_nodes as mx, io, study_provenance
from run_channel_tail_nodes import load_model, digest, save


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-root', type=Path, required=True)
    parser.add_argument('--initial', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    cache = args.cache_root.resolve()
    if args.output.exists():
        raise ValueError('不覆盖已验阶段')
    args.output.mkdir(parents=True)
    numba.set_num_threads(4)
    model = load_model(args.initial)
    if digest(args.initial) != '0ea0a380b83e3581668654f45a7aa5682515b2dfb6ef7c8aeb96f82f60afa030':
        raise ValueError('不是冻结severe_first incumbent')
    files = {n: cache/'artifacts/cinema-axis-calibration-v1'/name for n, name in
             [('reference', 'envelope-reference.npy'), ('suffix', 'envelope-suffix.npy'),
              ('points', 'envelope-arrivals.npy'), ('mass', 'photo-arrival-frequency.npy')]}
    reference, suffix, points = [np.load(files[n], mmap_mode='r') for n in ('reference', 'suffix', 'points')]
    mass = np.asarray(np.load(files['mass'], mmap_mode='r'), np.float64); mass /= mass.sum()
    sources = [Path(__file__), ROOT/'python/lutlab/channel_max_nodes.py', ROOT/'python/lutlab/channel_tail_nodes.py']
    save(args.output/'run.json', {'initial_sha256': digest(args.initial), 'input_sha256': {k: digest(v) for k, v in files.items()},
        'source_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in sources},
        'policy': '±2/±4共52方向，两扫0..7共16批；初始局部严格均值收益作整批预算，按max d²>65计数/49超额/mean优先交换；每批9项统计全部非增；cap=max(49,incumbent逐色d²)。禁止中间照片选择或追加扫数。',
        'gate': '完整cube及历史100图的mean/RMS/p99/max/CVaR相对incumbent均非增，且cube max严格降低；未通过则保留负结果和首阶段候选。',
        'environment': study_provenance.environment_fingerprint(), 'numba_threads': 4})
    indices, weights = cg.design(model, points)
    acc, _ = cj.accumulate(indices, weights, model.nodes.reshape(-1, 3), reference)
    initial, square = mx.measure(cc.predict(model, points), reference, suffix, mass)
    caps, colours = np.maximum(49, square), cj.parity(model.m)
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    current, measured, records = model, initial.copy(), []
    started = time.perf_counter()
    for sweep in range(2):
        for colour in range(8):
            changes, bad, invalid = mx.gains(indices, weights, acc, reference, suffix, mass,
                current.nodes.reshape(-1, 3), colours, colour, caps, root, 4)
            if invalid:
                raise AssertionError('当前cap或共享几何错误')
            moves, predicted, accepted = mx.select(changes, bad, colours, colour)
            current = tail.apply(current, indices, weights, acc, moves, reference)
            fresh = cc.predict(current, points)
            np.testing.assert_array_equal(fresh, ((acc+io.ONE//2) >> io.Q).astype(np.uint8))
            after, squared = mx.measure(fresh, reference, suffix, mass)
            if np.max(np.abs(after-measured-predicted)) > 1e-5 or np.any(after > measured+1e-5) or np.any(squared > caps):
                raise AssertionError('完整fresh收益/cap或批量预算回退')
            entry = {'sweep': sweep, 'colour': colour, 'changed_nodes': len(accepted),
                'budget_exchanges': sum(v['budget_exchange'] for v in accepted), 'before': measured.tolist(), 'after': after.tolist(),
                'maximum_gain_error': float(np.max(np.abs(after-measured-predicted))), 'max_squared_error': int(squared.max()),
                'moves': accepted, 'seconds': time.perf_counter()-started}
            records.append(entry); save(args.output/'progress.json', records)
            print(json.dumps({k: entry[k] for k in ('sweep', 'colour', 'changed_nodes', 'budget_exchanges', 'after', 'max_squared_error', 'seconds')}), flush=True)
            measured = after
    folder = args.output/'max_bank'; folder.mkdir()
    np.savez_compressed(folder/'model.npz', format=np.array('channel_coordinates_v1_experimental'),
        grid=current.grid, nodes=current.nodes, shared_idx=current.idx, channel_frac=current.channel_frac)
    base = io.load_sparse(cache/'artifacts/cinema-current-anchor-accept-v1/candidate-base.slut'); base.nodes = current.nodes
    io.save_sparse(folder/'candidate-base.slut', base); current.channel_frac.astype('<u4').tofile(folder/'channel-frac.bin')
    save(args.output/'summary.json', {'before': initial.tolist(), 'after': measured.tolist(),
        'model_sha256': digest(folder/'model.npz'), 'max_squared_error': int(squared.max()),
        'strict_max_reduced': bool(squared.max() < square.max()), 'cap_violations': 0, 'fresh_byte_mismatches': 0,
        'new_runtime_bytes': 0, 'seconds': time.perf_counter()-started})


if __name__ == '__main__':
    main()
