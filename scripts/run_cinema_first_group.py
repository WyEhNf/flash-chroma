"""原max_first固定86首级节点的52项同方向整组探针，所有项完整并集独立u64验证。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import channel_coordinates as cc, channel_first_joint as fj, channel_hotspot_support as hs, study_provenance
from run_channel_tail_nodes import digest, save, load_model
from run_cinema_first_hotspot import squared, train_counts, BLOCK, TOTAL, TRAINING_PIXELS
from verify_channel_coordinates import integer_oracle


def padded_add(outside, local):
    size = max(len(outside), len(local))
    return np.pad(outside, (0, size-len(outside)))+np.pad(local, (0, size-len(local)))


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--contract', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖整组52项冻结研究')
    contract = json.loads(args.contract.read_text(encoding='utf-8'))
    if not contract['pass']: raise ValueError('整组截断合同未通过')
    for name, sha in contract['source_sha256'].items():
        if digest(ROOT/name) != sha: raise ValueError('有限合同源已变：'+name)
    prior = ROOT/'artifacts/cinema-first-hotspot-v1'
    old = json.loads((prior/'run.json').read_text(encoding='utf-8')); original_summary = json.loads((prior/'summary.json').read_text(encoding='utf-8'))
    independent = json.loads((ROOT/'artifacts/cinema-first-hotspot-independent-v1.json').read_text(encoding='utf-8'))
    if not independent['pass'] or digest(prior/'support-index.npz') != independent['support_index_sha256']:
        raise ValueError('完整支撑身份已变')
    for spec in old['inputs'].values():
        if digest(spec['path']) != spec['sha256']: raise ValueError('原max_first或数据字节已变')
    if digest(prior/'suffix.npy') != original_summary['suffix_sha256']: raise ValueError('冻结904e/95cb/5b8后缀已变')
    source_names = set(old['sources_sha256']) | {'scripts/check_cinema_first_group.py', 'scripts/run_cinema_first_group.py',
                   'scripts/audit_cinema_first_group.py', 'experiments/p16-cinema-first-group-v1.json', 'python/lutlab/channel_first_joint.py'}
    args.output.mkdir(parents=True)
    save(args.output/'run.json', {'inputs': old['inputs'], 'source_sha256': {name: digest(ROOT/name) for name in sorted(source_names)},
        'contract_sha256': digest(args.contract), 'support_index_sha256': digest(prior/'support-index.npz'),
        'suffix_sha256': original_summary['suffix_sha256'], 'plan': json.loads((ROOT/'experiments/p16-cinema-first-group-v1.json').read_text(encoding='utf-8')),
        'environment': study_provenance.environment_fingerprint(), 'test_type': '固定52项整组完整支撑质量，非性能'})
    model = load_model(old['inputs']['first']['path']); baseline = np.memmap(old['inputs']['cube']['path'], np.uint8, 'r', shape=(TOTAL, 3))
    gold_full = np.load(old['inputs']['reference']['path'], mmap_mode='r'); mass = np.load(old['inputs']['mass']['path'], mmap_mode='r')
    total_mass = float(mass.sum(dtype=np.float64)); suffix = np.load(prior/'suffix.npy', mmap_mode='r')
    with np.load(prior/'support-index.npz') as data: keys, selected = data['union_keys'], data['selected_nodes']
    if len(keys) != 70571 or len(selected) != 86: raise ValueError('不是固定70571输入/86节点')
    source, gold = hs.rgb(keys), gold_full[keys]; counts, _ = train_counts(mass[keys], total_mass)
    hist, train_hist = np.zeros(51, np.int64), np.zeros(51, np.int64); training_total = 0
    for start in range(0, TOTAL, BLOCK):
        square = squared(baseline[start:start+BLOCK], gold_full[start:start+BLOCK]); count, _ = train_counts(mass[start:start+BLOCK], total_mass)
        hist += hs.histogram(square); train_hist += hs.histogram(square, count); training_total += int(count.sum())
    assert training_total == TRAINING_PIXELS
    initial, initial_train = hs.metrics(hist), hs.metrics(train_hist)
    assert initial == original_summary['baseline_uniform'] and initial_train == original_summary['baseline_training']
    initial_square = squared(baseline[keys], gold); caps = np.maximum(49, initial_square)
    outside, outside_train = hist-hs.histogram(initial_square), train_hist-hs.histogram(initial_square, counts)
    assert outside[50] == 0 and outside_train[50] == 0
    indices, weights, baseline_acc = fj.compact_design(model, source, selected)
    original = model.nodes.reshape(-1, 3)[selected].astype(np.int32)
    records = []
    for direction, delta in enumerate(hs.DIRECTIONS):
        changed = np.clip(original+delta, 0, 255).astype(np.uint8); moves = changed.astype(np.int32)-original
        all_nodes = model.nodes.copy(); all_nodes.reshape(-1, 3)[selected] = changed
        candidate = cc.ChannelLut(model.grid, all_nodes, model.idx, model.channel_frac)
        acc = fj.apply_accumulator(indices, weights, baseline_acc, moves)
        fresh = integer_oracle(candidate, source)
        np.testing.assert_array_equal(fresh, ((acc+32768)>>16).astype(np.uint8))
        square = squared(suffix[hs.key(fresh)], gold); size = max(51, int(square.max())+1)
        candidate_hist, candidate_train_hist = padded_add(outside, hs.histogram(square, size=size)), padded_add(outside_train, hs.histogram(square, counts, size=size))
        uniform, train = hs.metrics(candidate_hist), hs.metrics(candidate_train_hist)
        failures = [label+'_'+metric for label, after, before in (('uniform', uniform, initial), ('training', train, initial_train))
                    for metric in ('mean', 'rms', 'p99', 'cvar_1pct') if after[metric] > before[metric]+1e-12]
        violations = int(np.count_nonzero(square > caps))
        if violations: failures.append('fixed_point_caps')
        if uniform['max_squared'] > 49: failures.append('strict_max49')
        records.append({'direction': direction, 'group_delta': delta.tolist(), 'actual_changed_components': int(np.count_nonzero(moves)),
                        'clipped_components': int(np.count_nonzero(moves != delta)), 'uniform': uniform, 'training': train,
                        'max50_rows': int(candidate_hist[50]), 'point_cap_violations': violations, 'failures': failures,
                        'eligible': not failures, 'independent_u64_union_rows': len(keys), 'fresh_mismatches': 0,
                        'uniform_hist': candidate_hist.tolist(), 'training_hist': candidate_train_hist.tolist()})
    eligible = [r for r in records if r['eligible']]
    winner = min(eligible, key=lambda r: (r['uniform']['mean']+r['training']['mean'], r['uniform']['cvar_1pct']+r['training']['cvar_1pct'], r['direction'])) if eligible else None
    save(args.output/'directions.json', records)
    result = {'before_uniform': initial, 'before_training': initial_train, 'proposals': 52,
              'independent_u64_total_rows': len(keys)*52, 'fresh_mismatches': 0,
              'eligible_directions': [r['direction'] for r in eligible], 'winner': winner,
              'eligible_for_independent_final_checks': winner is not None,
              'scope': '原max_first一次52项同方向整组探针；全部无strict49则STOP负例，无追加扫轮或新native/百图/性能。'}
    save(args.output/'summary.json', result)
    print({'proposals': 52, 'eligible': len(eligible), 'strict_max49_directions': [r['direction'] for r in records if r['uniform']['max_squared'] <= 49]}, flush=True)


if __name__ == '__main__': main()
