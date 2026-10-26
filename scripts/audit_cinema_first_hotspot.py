"""只读复算有限方向判定，并独立检查单物理节点覆盖下界的逐节点反例。"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from run_channel_tail_nodes import digest, save, load_model


def scalar_positive(model, rgb):
    """Python整数比较器排序，独立列出三个输出正支撑物理节点。"""
    base = (int(model.idx[0, rgb[0]])*model.m+int(model.idx[1, rgb[1]]))*model.m+int(model.idx[2, rgb[2]])
    result = set()
    for channel in range(3):
        f = [int(model.channel_frac[channel, a, rgb[a]]) for a in range(3)]
        stride = [model.m**2, model.m, 1]
        for a, b in ((0, 1), (1, 2), (0, 1)):
            if f[a] < f[b]: f[a], f[b], stride[a], stride[b] = f[b], f[a], stride[b], stride[a]
        ids = [base, base+stride[0], base+stride[0]+stride[1], base+sum(stride)]
        weights = [65536-f[0], f[0]-f[1], f[1]-f[2], f[2]]
        for node, weight in zip(ids, weights):
            if weight > 0: result.add(node)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--study', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖独立复核')
    read = lambda name: json.loads((args.study/name).read_text(encoding='utf-8'))
    run, summary, records = read('run.json'), read('summary.json'), read('directions.json')
    for name, sha in run['sources_sha256'].items():
        if digest(ROOT/name) != sha: raise ValueError('实际执行源已变：'+name)
    for spec in run['inputs'].values():
        if digest(spec['path']) != spec['sha256']: raise ValueError('原始输入字节已变')
    with np.load(args.study/'support-index.npz') as data:
        hotspots, nodes, union, keys, offsets = [data[k] for k in ('hotspot_keys', 'selected_nodes', 'union_keys', 'support_keys', 'offsets')]
    np.testing.assert_array_equal(np.unique(keys), union)
    assert offsets[-1] == len(keys) and len(nodes) == 86 and len(hotspots) == 116 and len(union) == 70571
    assert len(records) == len(nodes)*52 == summary['total_directions']
    model = load_model(run['inputs']['first']['path'])
    gold = np.load(run['inputs']['reference']['path'], mmap_mode='r')
    baseline = np.memmap(run['inputs']['cube']['path'], dtype=np.uint8, mode='r', shape=(256**3, 3))
    independent_support = [scalar_positive(model, (int(k)>>16, (int(k)>>8)&255, int(k)&255)) for k in hotspots]
    np.testing.assert_array_equal(np.array(sorted(set().union(*independent_support))), nodes)
    directions = [v for scale in (1, 2) for v in itertools.product((-scale, 0, scale), repeat=3) if v != (0, 0, 0)]
    witnesses, coverage, qualified_budget = [], [], []
    for position, node in enumerate(nodes):
        local = keys[offsets[position]:offsets[position+1]]
        assert np.all(local[1:] > local[:-1])
        overlap = np.isin(hotspots, local)
        expected = np.array([int(node) in support for support in independent_support])
        np.testing.assert_array_equal(overlap, expected); coverage.append(int(overlap.sum()))
        row = summary['support'][position]
        assert row['physical_node'] == node and row['complete_support_rows'] == len(local) and row['hotspot_rows'] == overlap.sum()
        missing = int(hotspots[np.flatnonzero(~overlap)[0]])
        delta = baseline[missing].astype(np.int32)-gold[missing].astype(np.int32)
        assert int(delta@delta) == 50
        witnesses.append({'physical_node': int(node), 'covered_hotspots': int(overlap.sum()),
            'unaffected_source_key': missing, 'unaffected_source_rgb': [missing>>16, (missing>>8)&255, missing&255],
            'final_rgb': baseline[missing].tolist(), 'gold_rgb': gold[missing].tolist(), 'square': 50,
            'positive_weight_in_all_three_output_bases': False})
        actual = records[position*52:(position+1)*52]
        assert [tuple(r['delta']) for r in actual] == directions
        for record in actual:
            assert record['physical_node'] == node and record['support_rows'] == len(local)
            if 'uniform' not in record: continue
            failures = [label+'_'+metric for label, before, after in (
                ('uniform', summary['baseline_uniform'], record['uniform']),
                ('training', summary['baseline_training'], record['training'])) for metric in ('mean', 'rms', 'p99', 'cvar_1pct')
                if after[metric] > before[metric]+1e-12]
            assert record['uniform']['max_squared'] <= 50
            if record['uniform']['max_squared'] >= 50: failures.append('strict_max49')
            assert failures == record['failures']
            if failures == ['strict_max49']: qualified_budget.append(record)
    assert max(coverage) == summary['maximum_hotspots_covered_by_single_node'] == 32
    assert summary['support_count_and_union_mismatches'] == summary['full_domain_baseline_replay_mismatches'] == 0
    assert not summary['eligible_for_independent_final_checks'] and not summary['eligible_directions']
    save(args.output, {'pass': True, 'source_sha256': digest(__file__), 'summary_sha256': digest(args.study/'summary.json'),
        'directions_sha256': digest(args.study/'directions.json'), 'support_index_sha256': digest(args.study/'support-index.npz'),
        'checked_directions': len(records), 'independent_scalar_hotspots': len(hotspots), 'selected_nodes': len(nodes),
        'independent_support_union_rows': len(union), 'maximum_hotspots_covered_by_single_node': max(coverage),
        'minimum_hotspots_necessarily_unaffected_by_any_single_node': len(hotspots)-max(coverage),
        'single_node_witnesses': witnesses, 'all_eight_budgets_pass_directions': len(qualified_budget),
        'best_max50_count_all_eight_budgets_pass': min((r['max50_rows'] for r in qualified_budget), default=len(hotspots)),
        'scope': '复核全部4472项判定与独立Python整数逐节点覆盖反例；固定几何与后缀下任何单物理节点均保留至少84个原max50。未重算每项完整像素目标，不证明联合节点无解。'})


if __name__ == '__main__': main()
