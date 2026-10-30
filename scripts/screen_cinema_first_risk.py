"""完整70571支撑AABB鲁棒筛查，门内保存全部危险点安全三元组，不求解CP。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import channel_coordinates as cc, channel_hotspot_support as hs, channel_first_risk as risk, study_provenance
from run_channel_tail_nodes import digest, save, load_model
from run_cinema_first_hotspot import squared, TOTAL, BLOCK
from verify_channel_coordinates import integer_oracle


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--contract', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖鲁棒危险一次筛查')
    contract = json.loads(args.contract.read_text(encoding='utf-8'))
    if not contract['pass']: raise ValueError('有限穷举合同未通过')
    for name, sha in contract['source_sha256'].items():
        if digest(ROOT/name) != sha: raise ValueError('有限合同源已变：'+name)
    prior = ROOT/'artifacts/cinema-first-hotspot-v1'
    old = json.loads((prior/'run.json').read_text(encoding='utf-8')); original_summary = json.loads((prior/'summary.json').read_text(encoding='utf-8'))
    for spec in old['inputs'].values():
        if digest(spec['path']) != spec['sha256']: raise ValueError('原max_first或原始数据已变')
    if digest(prior/'suffix.npy') != original_summary['suffix_sha256']: raise ValueError('原后缀字节已变')
    source_names = set(old['sources_sha256']) | set(contract['source_sha256'])
    args.output.mkdir(parents=True)
    save(args.output/'run.json', {'inputs': old['inputs'], 'source_sha256': {name: digest(ROOT/name) for name in sorted(source_names)},
         'contract_sha256': digest(args.contract), 'support_index_sha256': digest(prior/'support-index.npz'),
         'suffix_sha256': original_summary['suffix_sha256'], 'environment': study_provenance.environment_fingerprint(),
         'plan': json.loads((ROOT/'experiments/p16-cinema-first-risk-v1.json').read_text(encoding='utf-8')), 'cp_solver_called': False})
    model = load_model(old['inputs']['first']['path'])
    with np.load(prior/'support-index.npz') as data: keys, selected, hotspots = data['union_keys'], data['selected_nodes'], data['hotspot_keys']
    if len(keys) != 70571 or len(selected) != 86: raise ValueError('不是冻结完整支撑')
    points = hs.rgb(keys); gold_full = np.load(old['inputs']['reference']['path'], mmap_mode='r'); gold = gold_full[keys]
    baseline = np.memmap(old['inputs']['cube']['path'], dtype=np.uint8, mode='r', shape=(TOTAL, 3))
    suffix = np.load(prior/'suffix.npy', mmap_mode='r'); lookup = lambda rgb: suffix[hs.key(rgb)]
    hist = np.zeros(51, np.int64)
    for start in range(0, TOTAL, BLOCK):
        sq = squared(baseline[start:start+BLOCK], gold_full[start:start+BLOCK])
        if np.max(sq) > 50: raise AssertionError('原模型max50改变')
        hist += hs.histogram(sq)
    outside = hist-hs.histogram(squared(baseline[keys], gold))
    if np.any(outside < 0) or np.flatnonzero(outside)[-1] > 49: raise AssertionError('支撑外并非全部<=49')
    all_nodes = model.nodes.reshape(-1, 3).astype(np.uint64)
    low_nodes, high_nodes = all_nodes.copy(), all_nodes.copy()
    low_nodes[selected] = np.maximum(all_nodes[selected].astype(np.int64)-2, 0).astype(np.uint64)
    high_nodes[selected] = np.minimum(all_nodes[selected]+2, 255)
    ids, weights = hs.corners(model, points); weights = weights.astype(np.uint64)
    lower_acc = np.sum(weights*low_nodes[ids], axis=1, dtype=np.uint64)
    upper_acc = np.sum(weights*high_nodes[ids], axis=1, dtype=np.uint64)
    lower, upper = ((lower_acc+32768)>>16).astype(np.uint8), ((upper_acc+32768)>>16).astype(np.uint8)
    original_first = integer_oracle(model, points)
    original_acc = np.sum(weights*all_nodes[ids], axis=1, dtype=np.uint64)
    move_bound_nodes = np.maximum(all_nodes.astype(np.int64)-low_nodes.astype(np.int64), high_nodes.astype(np.int64)-all_nodes.astype(np.int64)).astype(np.uint64)
    move_bound = np.sum(weights*move_bound_nodes[ids], axis=1, dtype=np.uint64)
    z_bound = np.maximum(original_first.astype(np.int64)-lower.astype(np.int64), upper.astype(np.int64)-original_first.astype(np.int64)).astype(np.uint64)
    row_abs_bound = move_bound+65536*z_bound
    int64_pass = bool(np.all(weights <= 65536) and np.all(weights.sum(axis=1, dtype=np.uint64) == 65536) and
        np.all(lower_acc <= upper_acc) and np.all(upper_acc <= 255*65536) and np.all(row_abs_bound < (1 << 62)))
    if not int64_pass: raise AssertionError('实际每项Q16权/acc或节点域乘积int64审计失败')
    np.testing.assert_array_equal(lookup(original_first), baseline[keys])
    for values, expected in ((low_nodes, lower), (high_nodes, upper)):
        endpoint = cc.ChannelLut(model.grid, values.astype(np.uint8).reshape(model.nodes.shape), model.idx, model.channel_frac)
        np.testing.assert_array_equal(integer_oracle(endpoint, points), expected)
    minimum, maximum, query_count, safe_count = risk.enumerate_stats(lower, upper, gold, lookup)
    dangerous = maximum > 49; rows = np.flatnonzero(dangerous).astype(np.uint32)
    if not np.all(np.isin(hotspots, keys[rows])): raise AssertionError('116原热点未全部列入危险集合')
    triples = int(safe_count[rows].sum(dtype=np.int64)); empty = int(np.count_nonzero(safe_count[rows] == 0))
    gate = len(rows) <= 8192 and triples <= 1000000 and empty == 0
    np.savez_compressed(args.output/'screen.npz', keys=keys, selected_nodes=selected, original_first=original_first,
                        lower_rgb=lower, upper_rgb=upper, minimum_squared=minimum, maximum_squared=maximum,
                        query_count=query_count, safe_count=safe_count, dangerous_rows=rows)
    payload = 0
    if gate:
        offsets, allowed = risk.collect_allowed(lower[rows], upper[rows], gold[rows], lookup)
        if offsets[-1] != triples: raise AssertionError('第二遍安全三元组数不符')
        np.testing.assert_array_equal(np.diff(offsets), safe_count[rows])
        np.savez_compressed(args.output/'danger-allowed.npz', source_keys=keys[rows], offsets=offsets, allowed_rgb=allowed)
        payload = keys[rows].nbytes+offsets.nbytes+allowed.nbytes
    record = {'complete_support_rows': len(keys), 'selected_nodes': len(selected), 'aabb_queries_first_pass': int(query_count.sum(dtype=np.int64)),
              'universally_safe_rows': int(np.count_nonzero(~dangerous)), 'possibly_dangerous_rows': len(rows),
              'safe_triples_in_dangerous_rows': triples, 'zero_safe_triple_rows': empty, 'within_predeclared_resource_gate': bool(gate),
              'outside_support_max_squared': int(np.flatnonzero(outside)[-1]), 'all116_old_hotspots_in_dangerous_set': True,
              'independent_u64_endpoint_rows': len(keys)*2, 'endpoint_mismatches': 0, 'allowed_csr_payload_bytes': payload,
              'endpoint_array_payload_bytes': lower_acc.nbytes+upper_acc.nbytes+lower.nbytes+upper.nbytes,
              'corner_design_payload_bytes': ids.nbytes+weights.nbytes, 'cp_solver_called': False,
              'int64_domain_audit': {'pass': int64_pass, 'audited_channel_rows': len(keys)*3,
                  'maximum_q16_weight': int(weights.max()), 'maximum_original_acc': int(original_acc.max()),
                  'maximum_endpoint_acc': int(upper_acc.max()), 'maximum_rounding_lhs_absolute_bound': int(row_abs_bound.max()),
                  'safe_limit': (1 << 62)-1},
              'scope': 'AABB完整枚举给恒安全充分证书，危险只表示可能；门内只存全部安全三元组，不自动CP求解，不代表mean预算或联合可行。'}
    save(args.output/'summary.json', record); print(record, flush=True)


if __name__ == '__main__': main()
