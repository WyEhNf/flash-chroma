"""独立重放八色完整受影响域并恢复全域/原60图指标，不重跑选择器。"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import channel_coordinates as cc, channel_hotspot_support as hs
from run_channel_tail_nodes import load_model, digest, save
from run_cinema_first_hotspot import squared, train_counts, BLOCK, TOTAL, TRAINING_PIXELS
from verify_channel_coordinates import integer_oracle


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--study', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖联合独立复核')
    read = lambda n: json.loads((args.study/n).read_text(encoding='utf-8'))
    run, summary, colours, nodes, directions = [read(n) for n in ('run.json', 'summary.json', 'colours.json', 'nodes.json', 'directions.json')]
    for name, sha in run['sources_sha256'].items():
        if digest(ROOT/name) != sha: raise ValueError('执行源已变：'+name)
    original = load_model(run['inputs']['first']['path']); candidate = load_model(args.study/'candidate/model.npz')
    for name in ('grid', 'idx', 'channel_frac'):
        np.testing.assert_array_equal(getattr(original, name), getattr(candidate, name))
    prior = ROOT/'artifacts/cinema-first-hotspot-v1'
    with np.load(prior/'support-index.npz') as data: keys, selected = data['union_keys'], data['selected_nodes']
    gold_full = np.load(run['inputs']['reference']['path'], mmap_mode='r'); gold = gold_full[keys]
    baseline = np.memmap(run['inputs']['cube']['path'], np.uint8, 'r', shape=(TOTAL, 3))
    mass = np.load(run['inputs']['mass']['path'], mmap_mode='r'); total_mass = float(mass.sum(dtype=np.float64))
    training, _ = train_counts(mass[keys], total_mass)
    hist, train_hist = np.zeros(51, np.int64), np.zeros(51, np.int64)
    train_total = 0
    for start in range(0, TOTAL, BLOCK):
        square = squared(baseline[start:start+BLOCK], gold_full[start:start+BLOCK])
        count, _ = train_counts(mass[start:start+BLOCK], total_mass); train_total += int(count.sum())
        hist += hs.histogram(square); train_hist += hs.histogram(square, count)
    assert train_total == TRAINING_PIXELS
    initial_uniform, initial_training = hs.metrics(hist), hs.metrics(train_hist)
    assert initial_uniform == summary['before_uniform'] and initial_training == summary['before_training']
    original_square = squared(baseline[keys], gold); caps = np.maximum(49, original_square)
    outside = hist-hs.histogram(original_square); outside_training = train_hist-hs.histogram(original_square, training)
    assert outside[50] == 0 and outside_training[50] == 0
    source = hs.rgb(keys); suffix = np.load(prior/'suffix.npy', mmap_mode='r')
    moves = np.zeros((original.m**3, 3), np.int32); previous_count = 116
    directions_expected = [v for scale in (1, 2) for v in itertools.product((-scale, 0, scale), repeat=3) if v != (0, 0, 0)]
    assert len(nodes) == len(directions) == len(selected) == 86
    for node, proposals in zip(nodes, directions):
        assert node['physical_node'] == proposals['physical_node'] and node['colour'] == proposals['colour']
        assert [tuple(x['delta']) for x in proposals['proposals']] == directions_expected
        accepted = [x for x in proposals['proposals'] if x['accepted_for_node']]
        assert bool(accepted) == node['accepted'] and len(accepted) <= 1
        assert node['max50_before'] == previous_count and node['max50_after'] <= previous_count
        previous_count = node['max50_after']
        for proposal in proposals['proposals']:
            assert proposal['accepted_for_node'] or proposal.get('selection_rejection')
        if accepted:
            entry = accepted[0]
            assert entry['delta'] == node['delta'] and entry['uniform'] == node['uniform'] and entry['training'] == node['training']
    fresh = []
    for colour in range(8):
        for row in nodes:
            if row['colour'] == colour and row['accepted']: moves[row['physical_node']] = row['delta']
        changed = original.nodes.astype(np.int32).reshape(-1, 3)+moves
        assert changed.min() >= 0 and changed.max() <= 255
        model = cc.ChannelLut(original.grid, changed.astype(np.uint8).reshape(original.nodes.shape), original.idx, original.channel_frac)
        output = suffix[hs.key(integer_oracle(model, source))]; square = squared(output, gold)
        assert np.all(square <= caps)
        hist = outside+hs.histogram(square); train_hist = outside_training+hs.histogram(square, training)
        uniform, train = hs.metrics(hist), hs.metrics(train_hist)
        assert uniform == colours[colour]['uniform'] and train == colours[colour]['training']
        assert all(after[k] <= before[k]+1e-12 for after, before in ((uniform, initial_uniform), (train, initial_training)) for k in ('mean', 'rms', 'p99', 'cvar_1pct'))
        fresh.append({'colour': colour, 'independent_union_rows': len(keys), 'uniform': uniform, 'training': train, 'max50_rows': int(hist[50])})
    np.testing.assert_array_equal(candidate.nodes, changed.astype(np.uint8).reshape(original.nodes.shape))
    with np.load(args.study/'final-state.npz') as data:
        np.testing.assert_array_equal(data['moves'], moves[selected]); np.testing.assert_array_equal(data['uniform_hist'], hist)
        np.testing.assert_array_equal(data['training_hist'], train_hist); np.testing.assert_array_equal(data['union_square'], square)
    assert uniform == summary['after_uniform'] and train == summary['after_training']
    assert summary['max50_after'] == 91 and not summary['eligible_for_independent_final_checks']
    save(args.output, {'pass': True, 'source_sha256': digest(__file__), 'summary_sha256': digest(args.study/'summary.json'),
         'fresh_per_colour': fresh, 'checked_nodes': len(nodes), 'checked_proposals': len(nodes)*52,
         'outside_hist_max50': int(outside[50]), 'outside_training_hist_max50': int(outside_training[50]),
         'scope': '从原始完整流和原60图整数频数独立恢复支撑外直方图，逐色u64重放完整并集、节点日志/拒绝原因及最终模型；未重新搜索4472项选择优先序，不含新全四级/native/百图/性能。'})


if __name__ == '__main__': main()
