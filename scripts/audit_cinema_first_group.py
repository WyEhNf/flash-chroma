"""独立八角uint64重算所有52个整组提案和完整域/训练直方图，核严格门槛。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import channel_hotspot_support as hs
from run_channel_tail_nodes import load_model, digest, save
from run_cinema_first_hotspot import squared, train_counts, TOTAL, BLOCK, TRAINING_PIXELS


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--study', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖整组独立复核')
    run = json.loads((args.study/'run.json').read_text(encoding='utf-8'))
    records = json.loads((args.study/'directions.json').read_text(encoding='utf-8'))
    summary = json.loads((args.study/'summary.json').read_text(encoding='utf-8'))
    for name, sha in run['source_sha256'].items():
        if digest(ROOT/name) != sha: raise ValueError('执行源已变：'+name)
    model = load_model(run['inputs']['first']['path']); original = model.nodes.reshape(-1, 3).astype(np.int64)
    prior = ROOT/'artifacts/cinema-first-hotspot-v1'
    with np.load(prior/'support-index.npz') as data: keys, selected = data['union_keys'], data['selected_nodes']
    gold_full = np.load(run['inputs']['reference']['path'], mmap_mode='r'); gold = gold_full[keys]
    baseline = np.memmap(run['inputs']['cube']['path'], dtype=np.uint8, mode='r', shape=(TOTAL, 3))
    mass = np.load(run['inputs']['mass']['path'], mmap_mode='r'); mass_total = float(mass.sum(dtype=np.float64))
    count, _ = train_counts(mass[keys], mass_total)
    hist, train_hist = np.zeros(51, np.int64), np.zeros(51, np.int64); training_total = 0
    for start in range(0, TOTAL, BLOCK):
        sq = squared(baseline[start:start+BLOCK], gold_full[start:start+BLOCK]); n, _ = train_counts(mass[start:start+BLOCK], mass_total)
        hist += hs.histogram(sq); train_hist += hs.histogram(sq, n); training_total += int(n.sum())
    assert training_total == TRAINING_PIXELS
    initial, initial_train = hs.metrics(hist), hs.metrics(train_hist)
    assert initial == summary['before_uniform'] and initial_train == summary['before_training']
    original_square = squared(baseline[keys], gold); caps = np.maximum(49, original_square)
    outside, outside_train = hist-hs.histogram(original_square), train_hist-hs.histogram(original_square, count)
    assert outside[50] == outside_train[50] == 0
    ids, weights = hs.corners(model, hs.rgb(keys)); weights = weights.astype(np.uint64)
    suffix = np.load(prior/'suffix.npy', mmap_mode='r'); eligible = []; results = []
    for direction, (record, delta) in enumerate(zip(records, hs.DIRECTIONS)):
        assert record['direction'] == direction and record['group_delta'] == delta.tolist()
        values = original.copy(); values[selected] = np.minimum(np.maximum(original[selected]+delta, 0), 255)
        acc = np.sum(weights*values.astype(np.uint64)[ids], axis=1, dtype=np.uint64)
        first = ((acc+32768)>>16).astype(np.uint8); sq = squared(suffix[hs.key(first)], gold)
        size = max(51, int(sq.max())+1)
        new_hist = np.pad(outside, (0, size-len(outside)))+hs.histogram(sq, size=size)
        new_train_hist = np.pad(outside_train, (0, size-len(outside_train)))+hs.histogram(sq, count, size=size)
        uniform, train = hs.metrics(new_hist), hs.metrics(new_train_hist)
        assert uniform == record['uniform'] and train == record['training']
        assert new_hist.tolist() == record['uniform_hist'] and new_train_hist.tolist() == record['training_hist']
        failures = [label+'_'+metric for label, after, before in (('uniform', uniform, initial), ('training', train, initial_train))
                    for metric in ('mean', 'rms', 'p99', 'cvar_1pct') if after[metric] > before[metric]+1e-12]
        violating = int(np.count_nonzero(sq > caps))
        if violating: failures.append('fixed_point_caps')
        if uniform['max_squared'] > 49: failures.append('strict_max49')
        assert failures == record['failures'] and record['eligible'] == (not failures)
        if not failures: eligible.append(record)
        results.append({'direction': direction, 'independent_rows': len(keys), 'point_cap_violations': violating,
                        'max_squared': uniform['max_squared'], 'failures': failures})
    assert len(records) == len(results) == 52
    expected = min(eligible, key=lambda r: (r['uniform']['mean']+r['training']['mean'], r['uniform']['cvar_1pct']+r['training']['cvar_1pct'], r['direction'])) if eligible else None
    assert summary['winner'] == expected and summary['eligible_for_independent_final_checks'] == (expected is not None)
    save(args.output, {'pass': True, 'source_sha256': digest(__file__), 'summary_sha256': digest(args.study/'summary.json'),
        'directions_sha256': digest(args.study/'directions.json'), 'checked_proposals': len(results),
        'independent_eight_corner_u64_total_rows': len(keys)*52, 'eligible_directions': [r['direction'] for r in eligible],
        'results': results, 'scope': '全部52项独立八角u64前向及完整直方图/固定cap/八预算/选型复核；没有新的全四级/native/百图或性能验收。'})


if __name__ == '__main__': main()
