"""独立17/33有限合同：外节点零变动权重、累计整数更新及52方向选择。"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import channel_coordinates as cc, channel_hotspot_support as hs, channel_first_joint as fj, io
from run_channel_tail_nodes import digest, save
from verify_channel_coordinates import integer_oracle


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖八色合同')
    rng = np.random.default_rng(2026102486); cases = []
    for m in (17, 33):
        sparse = io.SparseLut(np.tile(np.linspace(0, 255, m), (3, 1)), rng.integers(115, 140, (m, m, m, 3), dtype=np.uint8))
        model = cc.from_sparse(sparse)
        for channel in range(3):
            model.channel_frac[channel, :, 1:255] = np.clip(model.channel_frac[channel, :, 1:255].astype(np.int64)+(channel-1)*129, 0, io.ONE)
        cc.validate(model); points = rng.integers(0, 256, (257, 3), dtype=np.uint8)
        physical, weights, acc = hs.basis(model, points)
        available = np.unique(physical[weights > 0]); selected = available[np.linspace(0, len(available)-1, 9).astype(np.int64)]
        indices, compact_weights, compact_acc = fj.compact_design(model, points, selected)
        np.testing.assert_array_equal(acc, compact_acc)
        moves = rng.integers(-2, 3, (len(selected), 3), dtype=np.int32); moves[0] = (2, -2, 1)
        changed = model.nodes.copy(); changed.reshape(-1, 3)[selected] = changed.reshape(-1, 3)[selected].astype(np.int32)+moves
        candidate = cc.ChannelLut(model.grid, changed, model.idx, model.channel_frac)
        predicted = ((fj.apply_accumulator(indices, compact_weights, compact_acc, moves)+32768)>>16).astype(np.uint8)
        np.testing.assert_array_equal(predicted, integer_oracle(candidate, points))
        coords = np.column_stack(np.unravel_index(selected, (m,)*3)); colours = (coords[:, 0]&1)*4+(coords[:, 1]&1)*2+(coords[:, 2]&1)
        active = []
        for node in range(len(selected)):
            rows, node_weight = fj.node_support(indices, compact_weights, node)
            active.append(set(rows.tolist()))
            for other in range(node):
                if colours[node] == colours[other] and active[node] & active[other]: raise AssertionError('同色正支撑重叠')
        lookup = lambda a: (a.astype(np.int32)//8+110).astype(np.uint8)
        baseline = lookup(integer_oracle(model, points)); gold = baseline.copy(); gold[:, 0] += rng.integers(0, 3, len(gold), dtype=np.uint8)
        error = baseline.astype(np.int32)-gold.astype(np.int32); old_square = np.sum(error*error, axis=1, dtype=np.int32)
        counts = rng.integers(0, 6, len(points), dtype=np.int64); counts[0] = 2
        hist, train_hist = hs.histogram(old_square), hs.histogram(old_square, counts)
        initial, initial_train = hs.metrics(hist), hs.metrics(train_hist)
        rows, node_weight = fj.node_support(indices, compact_weights, 0)
        best, entries = fj.choose(acc[rows], node_weight, gold[rows], counts[rows], old_square[rows], np.maximum(49, old_square[rows]),
                                 hist, train_hist, initial, initial_train, model.nodes.reshape(-1, 3)[selected[0]], lookup)
        independent_eligible = []
        before_rank = (int(hist[50]), initial['mean']+initial_train['mean'], initial['cvar_1pct']+initial_train['cvar_1pct'], -1)
        for position, delta in enumerate(hs.DIRECTIONS):
            nodes = model.nodes.copy(); nodes.reshape(-1, 3)[selected[0]] = nodes.reshape(-1, 3)[selected[0]].astype(np.int32)+delta
            fresh = lookup(integer_oracle(cc.ChannelLut(model.grid, nodes, model.idx, model.channel_frac), points))
            error = fresh.astype(np.int32)-gold.astype(np.int32); square = np.sum(error*error, axis=1, dtype=np.int32)
            whole, whole_train = hs.metrics(hs.histogram(square)), hs.metrics(hs.histogram(square, counts))
            entry = entries[position]
            if 'uniform' in entry:
                assert entry['uniform'] == whole and entry['training'] == whole_train
            allowed = np.all(square <= np.maximum(49, old_square)) and all(after[k] <= before[k]+1e-12 for after, before in ((whole, initial), (whole_train, initial_train)) for k in ('mean', 'rms', 'p99', 'cvar_1pct'))
            rank = (int(np.count_nonzero(square == 50)), whole['mean']+whole_train['mean'], whole['cvar_1pct']+whole_train['cvar_1pct'], position)
            if allowed and (rank[0] < before_rank[0] or (rank[0] == before_rank[0] and rank[1] < before_rank[1]-1e-12)):
                independent_eligible.append((rank, position))
        expected = min(independent_eligible)[1] if independent_eligible else None
        assert (None if best is None else best['direction']) == expected
        cases.append({'m': m, 'points': len(points), 'selected_nodes': len(selected), 'simultaneous_moves_include_dummy_slot0': True,
                      'same_colour_support_overlaps': 0, 'independent_52_direction_choice': expected})
    sources = [Path(__file__), ROOT/'scripts/run_cinema_first_joint.py', ROOT/'python/lutlab/channel_first_joint.py',
               ROOT/'experiments/p16-cinema-first-joint-v1.json', ROOT/'python/lutlab/channel_hotspot_support.py']
    save(args.output, {'pass': True, 'cases': cases, 'source_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in sources},
                      'scope': '有限17/33合同；不代表实际86节点拟合或完整域/照片/性能验收'})


if __name__ == '__main__': main()
