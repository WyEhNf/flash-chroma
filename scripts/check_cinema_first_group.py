"""有限17/33合同：同方向多节点真实截断与部分固定角，52项全部独立整数验证。"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import channel_coordinates as cc, channel_first_joint as fj, channel_hotspot_support as hs, io
from run_channel_tail_nodes import digest, save
from verify_channel_coordinates import integer_oracle


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖整组有限合同')
    rng = np.random.default_rng(2026102452); records = []
    for m in (17, 33):
        nodes = rng.integers(0, 256, (m, m, m, 3), dtype=np.uint8)
        model = cc.from_sparse(io.SparseLut(np.tile(np.linspace(0, 255, m), (3, 1)), nodes))
        for c in range(3):
            model.channel_frac[c, :, 1:255] = np.clip(model.channel_frac[c, :, 1:255].astype(np.int64)+(c-1)*131, 0, io.ONE)
        cc.validate(model); sample = rng.integers(0, 256, (193, 3), dtype=np.uint8)
        sample[:2] = [[0, 0, 0], [255, 255, 255]]
        physical, raw_weights, _ = hs.basis(model, sample)
        selected = np.unique(physical[raw_weights > 0])[::2]
        model.nodes.reshape(-1, 3)[selected[0]] = (0, 255, 0)
        model.nodes.reshape(-1, 3)[selected[1]] = (255, 0, 255)
        model.nodes.reshape(-1, 3)[selected[2]] = (1, 254, 1)
        model.nodes.reshape(-1, 3)[selected[3]] = (254, 1, 254)
        indices, weights, baseline_acc = fj.compact_design(model, sample, selected)
        original = model.nodes.reshape(-1, 3)[selected].astype(np.int32); clipped_cases = 0
        counts = rng.integers(0, 5, len(sample), dtype=np.int64); counts[:4] = 0
        assert np.any(counts == 0)
        for delta in hs.DIRECTIONS:
            changed = np.clip(original+delta, 0, 255).astype(np.uint8); actual_moves = changed.astype(np.int32)-original
            clipped_cases += int(np.any(actual_moves != delta))
            actual_nodes = model.nodes.copy(); actual_nodes.reshape(-1, 3)[selected] = changed
            candidate = cc.ChannelLut(model.grid, actual_nodes, model.idx, model.channel_frac)
            fresh = integer_oracle(candidate, sample)
            predicted = ((fj.apply_accumulator(indices, weights, baseline_acc, actual_moves)+32768)>>16).astype(np.uint8)
            np.testing.assert_array_equal(fresh, predicted)
            square = np.sum((fresh.astype(np.int32)-127)**2, axis=1, dtype=np.int32)
            hist = hs.histogram(square, counts, max(51, int(square.max())+1))
            assert int(hist.sum()) == int(counts.sum())
        assert clipped_cases == 52
        records.append({'m': m, 'points': len(sample), 'selected_nodes': len(selected), 'independent_proposals': 52,
                        'clip_exercised_proposals': clipped_cases, 'zero_training_count_rows': int(np.count_nonzero(counts == 0))})
    sources = [Path(__file__), ROOT/'scripts/run_cinema_first_group.py', ROOT/'experiments/p16-cinema-first-group-v1.json',
               ROOT/'python/lutlab/channel_first_joint.py', ROOT/'python/lutlab/channel_hotspot_support.py']
    save(args.output, {'pass': True, 'cases': records, 'source_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in sources},
                      'scope': '有限17/33整数截断/固定角/训练零频数合同；不是实际整组52项结果'})


if __name__ == '__main__': main()
