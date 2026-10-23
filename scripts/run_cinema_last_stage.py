"""固定首阶段正式incumbent和中间两级，一次末级完整到达域节点扫描。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import sys
import time
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numba
import numpy as np
from lutlab import channel_coordinates as cc, channel_global_nodes as cg, channel_joint_nodes as cj
from lutlab import channel_tail_nodes as tail, channel_max_nodes as mx, io, study_provenance
from run_channel_tail_nodes import load_model, digest, save
from accept_channel_coordinates import hist_metrics
from accept_channel_tail_nodes import histogram
from verify_channel_coordinates import integer_oracle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-root', type=Path, required=True)
    parser.add_argument('--first-folder', type=Path, required=True)
    parser.add_argument('--cube', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖末级新阶段')
    args.output.mkdir(parents=True)
    cache = args.cache_root.resolve(); numba.set_num_threads(4)
    first = load_model(args.first_folder/'model.npz')
    if digest(args.first_folder/'model.npz') != '0ea0a380b83e3581668654f45a7aa5682515b2dfb6ef7c8aeb96f82f60afa030':
        raise ValueError('不是正式severe_first')
    points = np.load(cache/'artifacts/cinema-axis-calibration-v1/envelope-arrivals.npy', mmap_mode='r')
    reference = np.load(cache/'artifacts/cinema-axis-calibration-v1/envelope-reference.npy', mmap_mode='r')
    mass_path = cache/'artifacts/cinema-axis-calibration-v1/photo-arrival-frequency.npy'
    mass = np.asarray(np.load(mass_path, mmap_mode='r'), np.float64); mass /= mass.sum()
    suffix_paths = [cache/'artifacts/cinema-envelope-v1/stage4_sweep004'/f'selected-stage{k}.slut' for k in (2, 3, 4)]
    suffix_models = [cc.from_sparse(io.load_sparse(p, competition=True)) for p in suffix_paths]
    model = suffix_models[2]
    save(args.output/'run.json', {'first_model_sha256': digest(args.first_folder/'model.npz'),
        'suffix_model_sha256': [digest(p) for p in suffix_paths], 'cube_sha256': digest(args.cube),
        'mass_sha256': digest(mass_path), 'source_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in
            [Path(__file__), ROOT/'python/lutlab/channel_max_nodes.py', ROOT/'python/lutlab/channel_tail_nodes.py']},
        'policy': '一次8批，52个±2/±4方向，整批九项保护；cap=max(65,severe_first逐色d²)，禁止非原max颜色新建d²66；全域max必须严格降，双mean/RMS和p99/CVaR不退才另终验。只使用原60图训练质量，不中间读100图。',
        'labels': '末级拟合整链真实reference，显式联合目标；原始第4 LUT独立源误差另列，不能宣称每级独立拟合质量都不变。',
        'environment': study_provenance.environment_fingerprint(), 'numba_threads': 4})
    reached = cc.predict(first, points)
    for prefix in suffix_models[:2]:
        reached = cc.predict(prefix, reached)
    initial_output = cc.predict(model, reached)
    baseline = np.memmap(args.cube, np.uint8, 'r', shape=(256**3, 3))
    np.testing.assert_array_equal(initial_output, baseline)
    probe = np.arange(0, len(points), 4096)
    independent = integer_oracle(first, points[probe])
    for prefix in suffix_models[:2]:
        independent = integer_oracle(prefix, independent)
    np.testing.assert_array_equal(reached[probe], independent)
    initial, squared = mx.measure(initial_output, reference, points, mass)
    caps = np.maximum(65, squared)
    colours, root = cj.parity(model.m), np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    indices, weights = cg.design(model, reached)
    acc, _ = cj.accumulate(indices, weights, model.nodes.reshape(-1, 3), reference)
    current, measured, records = model, initial.copy(), []
    started = time.perf_counter()
    for colour in range(8):
        changes, bad, invalid = mx.gains(indices, weights, acc, reference, points, mass,
            current.nodes.reshape(-1, 3), colours, colour, caps, root, 4)
        if invalid:
            raise AssertionError('末级几何或当前cap错误')
        moves, predicted, accepted = mx.select(changes, bad, colours, colour)
        current = tail.apply(current, indices, weights, acc, moves, reference)
        fresh = cc.predict(current, reached)
        np.testing.assert_array_equal(fresh, ((acc+io.ONE//2) >> io.Q).astype(np.uint8))
        after, squared = mx.measure(fresh, reference, points, mass)
        if np.max(np.abs(after-measured-predicted)) > 1e-5 or np.any(after > measured+1e-5) or np.any(squared > caps):
            raise AssertionError('末级fresh完整收益/cap/批量预算不符')
        entry = {'colour': colour, 'changed_nodes': len(accepted), 'before': measured.tolist(), 'after': after.tolist(),
            'budget_exchanges': sum(v['budget_exchange'] for v in accepted), 'max_squared': int(squared.max()),
            'maximum_gain_error': float(np.max(np.abs(after-measured-predicted))), 'moves': accepted,
            'seconds': time.perf_counter()-started}
        records.append(entry); save(args.output/'progress.json', records)
        print(json.dumps({k: entry[k] for k in ('colour', 'changed_nodes', 'after', 'max_squared', 'seconds')}), flush=True)
        measured = after
    candidate = args.output/'candidate'; candidate.mkdir()
    for name in ('model.npz', 'candidate-base.slut', 'channel-frac.bin'):
        shutil.copyfile(args.first_folder/name, candidate/name)
    io.save_sparse(candidate/'stage4.slut', io.SparseLut(current.grid, current.nodes, current.idx, current.channel_frac[0]))
    # 下述独立源指标仍是研究前向，不冒充新末级的完整uint64/原生证明。
    stage4_table = io.load_full(cache/'artifacts/chain-error-cache/source-d69ca4fa6f34c990a0bc752d/table.lut256', mmap=True).reshape(-1, 3)
    source_metrics = {}
    for label, last in [('before', model), ('after', current)]:
        hist = np.zeros(3*255**2+1, np.int64)
        for start in range(0, len(points), 1 << 18):
            value = cc.predict(last, points[start:start+(1 << 18)])
            hist += histogram(value, stage4_table[start:start+len(value)])
        source_metrics[label] = hist_metrics(hist)
    save(args.output/'summary.json', {'before': initial.tolist(), 'after': measured.tolist(),
        'max_squared': int(squared.max()), 'strict_max_reduced': bool(squared.max() < 66),
        'stage4_model_sha256': digest(candidate/'stage4.slut'), 'independent_stage4_source_accuracy': source_metrics,
        'changed_node_components': int(np.count_nonzero(current.nodes != model.nodes)),
        'cap_violations': 0, 'fresh_byte_mismatches': 0, 'new_runtime_bytes': 0})


if __name__ == '__main__':
    main()
