"""从741e55f全域145热点重新选首级正权节点，做唯一±2必要证书。"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import channel_coordinates as cc, channel_hotspot_support as hs, integer_first_box as box, io, study_provenance
from run_channel_tail_nodes import digest, load_model, save
from verify_channel_coordinates import integer_oracle


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--frozen', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖当前max48热点唯一盒证书')
    frozen = json.loads(args.frozen.read_text(encoding='utf-8'))
    if not frozen['ast_pass']: raise ValueError('先通过源/协议冻结')
    for name, expected in frozen['source_sha256'].items():
        if digest(ROOT/name) != expected: raise ValueError('当前热点证书源已变：'+name)
    for spec in frozen['inputs'].values():
        if digest(spec['path']) != spec['sha256']: raise ValueError('当前max48固定输入已变')
    finite = json.loads((ROOT/'report/data/p16-cinema-first-box-20261024/contract.json').read_text(encoding='utf-8'))
    if not finite['pass']: raise ValueError('既有通用17/33盒合同未通过')
    for name, expected in finite['source_sha256'].items():
        if digest(ROOT/name) != expected: raise ValueError('通用整数盒合同源已变')
    spec = frozen['inputs']; model = load_model(spec['first']['path'])
    cube = np.memmap(spec['cube']['path'], np.uint8, 'r', shape=(1<<24, 3)); gold = np.load(spec['gold']['path'], mmap_mode='r')
    collected = []
    for start in range(0, 1<<24, 1<<20):
        difference = cube[start:start+(1<<20)].astype(np.int32)-gold[start:start+(1<<20)].astype(np.int32)
        square = np.sum(difference*difference, axis=1, dtype=np.int32)
        if square.max() > 48: raise AssertionError('当前完整流max²不再为48')
        collected.append((np.flatnonzero(square == 48)+start).astype(np.uint32))
    keys = np.concatenate(collected)
    if len(keys) != 145: raise AssertionError('不是已认证当前145热点')
    with np.load(spec['histograms']['path']) as data:
        if data['cube_candidate'][48] != 145: raise ValueError('已认证完整直方图热点计数不符')
    points = hs.rgb(keys); indices, weights, _ = hs.basis(model, points)
    selected = np.unique(indices[weights > 0]); corner_nodes, corner_weights = hs.corners(model, points)
    np.testing.assert_array_equal(selected, np.unique(corner_nodes[np.any(corner_weights > 0, axis=2)]))
    ordinary = [cc.from_sparse(io.load_sparse(spec['stage'+str(i)]['path'])) for i in (2, 3, 4)]
    first = integer_oracle(model, points); np.testing.assert_array_equal(cc.predict(model, points), first)
    current, numba = first.copy(), first.copy()
    for table in ordinary:
        current = integer_oracle(table, current); numba = cc.predict(table, numba)
    np.testing.assert_array_equal(current, cube[keys]); np.testing.assert_array_equal(numba, current)
    suffix = np.load(spec['suffix']['path'], mmap_mode='r')
    np.testing.assert_array_equal(suffix[hs.key(first)], current)
    bounds = [box.point_box(model, p.tolist(), selected) for p in points]
    lower, upper = np.array([b['lower_rgb'] for b in bounds], np.uint8), np.array([b['upper_rgb'] for b in bounds], np.uint8)
    for direction, expected in ((-2, lower), (2, upper)):
        nodes = model.nodes.copy(); nodes.reshape(-1, 3)[selected] = np.clip(nodes.reshape(-1, 3)[selected].astype(np.int64)+direction, 0, 255)
        endpoint = cc.ChannelLut(model.grid, nodes, model.idx, model.channel_frac)
        np.testing.assert_array_equal(integer_oracle(endpoint, points), expected)
    rgb_rows, source_rows, offsets = [], [], [0]
    for key, lo, hi in zip(keys, lower, upper):
        values = list(itertools.product(*[range(int(a), int(b)+1) for a, b in zip(lo, hi)]))
        if len(values) > 125: raise AssertionError('单点查询超过125')
        rgb_rows.extend(values); source_rows.extend([int(key)]*len(values)); offsets.append(len(rgb_rows))
    if len(rgb_rows) > 18125: raise AssertionError('总查询超过145×125')
    query_rgb = np.array(rgb_rows, np.uint8); source_keys = np.array(source_rows, np.uint32)
    direct = suffix[hs.key(query_rgb)]; oracle, numba = query_rgb.copy(), query_rgb.copy()
    for table in ordinary:
        oracle = integer_oracle(table, oracle); numba = cc.predict(table, numba)
    np.testing.assert_array_equal(direct, oracle); np.testing.assert_array_equal(numba, oracle)
    difference = direct.astype(np.int32)-gold[source_keys].astype(np.int32)
    squared = np.sum(difference*difference, axis=1, dtype=np.int32); records = []
    for j, key in enumerate(keys):
        begin, end = offsets[j:j+2]; q = squared[begin:end]; best = begin+int(np.argmin(q))
        records.append({'source_key': int(key), 'source_rgb': points[j].tolist(), 'gold_rgb': gold[key].tolist(),
            'baseline_first_rgb': first[j].tolist(), 'baseline_final_rgb': current[j].tolist(), 'baseline_squared': 48,
            'first_box': bounds[j], 'queries': end-begin, 'minimum_squared': int(q.min()),
            'safe_at47_count': int(np.count_nonzero(q <= 47)), 'argmin_first_rgb': query_rgb[best].tolist(),
            'argmin_final_rgb': direct[best].tolist(), 'blocks_node_box_at47': bool(q.min() > 47)})
    args.output.mkdir(parents=True)
    np.savez_compressed(args.output/'replay.npz', keys=keys, selected_nodes=selected, baseline_first=first, baseline_final=current,
        lower_rgb=lower, upper_rgb=upper, offsets=np.array(offsets, np.int64), query_rgb=query_rgb,
        query_source_keys=source_keys, query_final=direct, squared=squared)
    blocked = sum(r['blocks_node_box_at47'] for r in records)
    save(args.output/'results.json', {'inputs': spec, 'source_sha256': frozen['source_sha256'], 'frozen_sha256': digest(args.frozen),
        'hotspots': len(keys), 'selected_physical_nodes': len(selected), 'selected_rgb_components': 3*len(selected),
        'total_suffix_queries': len(query_rgb), 'blocked_hotspots': blocked, 'necessary_condition_not_blocked': blocked == 0,
        'records': records, 'u64_numba_mismatches': 0, 'suffix_oracle_mismatches': 0,
        'environment': study_provenance.environment_fingerprint(), 'cp_solver_called': False,
        'scope': '当前741e55f全部145热点的±2节点盒必要证书；任何阻断仅限此固定模型/盒/后缀，无阻断不证明共享赋值可行。没有拟合、新模型、照片择优或性能结论。'})
    print({'hotspots': len(keys), 'selected_nodes': len(selected), 'queries': len(query_rgb), 'blocked': blocked}, flush=True)


if __name__ == '__main__': main()
