"""独立纯整数核当前145热点身份、节点盒体积、完整查询和必要下界。"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from run_channel_tail_nodes import digest, save


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--stage', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖当前热点必要证书独立审计')
    run = json.loads((args.stage/'results.json').read_text(encoding='utf-8'))
    for name, expected in run['source_sha256'].items():
        if digest(ROOT/name) != expected: raise ValueError('当前热点执行源已变')
    for spec in run['inputs'].values():
        if digest(spec['path']) != spec['sha256']: raise ValueError('当前热点固定输入已变')
    with np.load(args.stage/'replay.npz') as data: arrays = {k: data[k] for k in data.files}
    keys = arrays['keys']; assert len(keys) == run['hotspots'] == 145 and np.all(keys[1:] > keys[:-1])
    gold = np.load(run['inputs']['gold']['path'], mmap_mode='r')
    cube = np.memmap(run['inputs']['cube']['path'], np.uint8, 'r', shape=(1<<24, 3))
    with np.load(run['inputs']['histograms']['path']) as data: assert int(data['cube_candidate'][48]) == 145
    assert np.all(np.sum((cube[keys].astype(np.int64)-gold[keys].astype(np.int64))**2, axis=1) == 48)
    np.testing.assert_array_equal(cube[keys], arrays['baseline_final'])
    offsets = arrays['offsets']; assert offsets[0] == 0 and offsets[-1] == len(arrays['query_rgb']) and np.all(np.diff(offsets) > 0)
    assert len(arrays['selected_nodes'])*3 == run['selected_rgb_components'] and len(arrays['selected_nodes']) == run['selected_physical_nodes']
    blocked = 0
    for j, record in enumerate(run['records']):
        key = int(keys[j]); assert record['source_key'] == key and record['baseline_squared'] == 48
        assert record['gold_rgb'] == gold[key].tolist()
        bounds = record['first_box']; lower, upper = [], []
        for c, channel in enumerate(bounds['channels']):
            coefficients = channel['coefficients']; assert sum(v['weight_q16'] for v in coefficients) == 65536
            baseline = sum(v['weight_q16']*v['original_value'] for v in coefficients)
            low, high = 0, 0
            for term in coefficients:
                is_variable = term['physical_node'] in arrays['selected_nodes']
                lo = max(0, term['original_value']-2) if is_variable else term['original_value']
                hi = min(255, term['original_value']+2) if is_variable else term['original_value']
                assert [term['lower_value'], term['upper_value'], term['variable']] == [lo, hi, is_variable]
                low += term['weight_q16']*lo; high += term['weight_q16']*hi
            assert [baseline, low, high] == [channel['baseline_acc'], channel['lower_acc'], channel['upper_acc']]
            assert (baseline+32768)//65536 == record['baseline_first_rgb'][c]
            lower.append((low+32768)//65536); upper.append((high+32768)//65536)
        assert [lower, upper] == [bounds['lower_rgb'], bounds['upper_rgb']]
        begin, end = int(offsets[j]), int(offsets[j+1])
        expected = list(itertools.product(*[range(a, b+1) for a, b in zip(lower, upper)]))
        assert arrays['query_rgb'][begin:end].tolist() == [list(v) for v in expected] and len(expected) <= 125
        assert np.all(arrays['query_source_keys'][begin:end] == key)
        errors = [sum((int(out[c])-int(gold[key, c]))**2 for c in range(3)) for out in arrays['query_final'][begin:end]]
        assert errors == arrays['squared'][begin:end].tolist()
        assert min(errors) == record['minimum_squared'] and sum(q <= 47 for q in errors) == record['safe_at47_count']
        best = int(np.argmin(errors)); assert record['argmin_first_rgb'] == list(expected[best])
        assert record['argmin_final_rgb'] == arrays['query_final'][begin+best].tolist()
        assert record['blocks_node_box_at47'] == (min(errors) > 47); blocked += int(min(errors) > 47)
    assert blocked == run['blocked_hotspots'] and run['necessary_condition_not_blocked'] == (blocked == 0)
    assert run['total_suffix_queries'] <= 18125 and not run['cp_solver_called']
    save(args.output, {'pass': True, 'results_sha256': digest(args.stage/'results.json'), 'replay_sha256': digest(args.stage/'replay.npz'),
        'source_sha256': digest(__file__), 'hotspots_checked': 145, 'queries_checked': int(offsets[-1]), 'blocked_hotspots': blocked,
        'scope': '核已认证直方图145与145独特点共同证明点集完整；整数重算所有系数/clip/边界/盒体积/误差/argmin。双链与端点u64由唯一主证书执行，未再次全域扫描或搜索。'})
    print({'pass': True, 'hotspots': 145, 'queries': int(offsets[-1]), 'blocked': blocked}, flush=True)


if __name__ == '__main__': main()
