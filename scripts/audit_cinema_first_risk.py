"""独立按每源点箱大小展开RGB，复核全部鲁棒统计和危险安全CSR，不求解CP。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import channel_coordinates as cc, channel_hotspot_support as hs
from run_channel_tail_nodes import load_model, digest, save
from verify_channel_coordinates import integer_oracle


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--study', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖危险筛查独立审计')
    run = json.loads((args.study/'run.json').read_text(encoding='utf-8')); summary = json.loads((args.study/'summary.json').read_text(encoding='utf-8'))
    for name, expected in run['source_sha256'].items():
        if digest(ROOT/name) != expected: raise ValueError('实际筛查源已变化：'+name)
    with np.load(args.study/'screen.npz') as data: values = {k: data[k] for k in data.files}
    model = load_model(run['inputs']['first']['path']); keys = values['keys']; points = hs.rgb(keys); selected = values['selected_nodes']
    for shift, label in ((-2, 'lower_rgb'), (2, 'upper_rgb')):
        nodes = model.nodes.copy(); nodes.reshape(-1, 3)[selected] = np.clip(nodes.reshape(-1, 3)[selected].astype(np.int16)+shift, 0, 255)
        endpoint = cc.ChannelLut(model.grid, nodes, model.idx, model.channel_frac)
        np.testing.assert_array_equal(integer_oracle(endpoint, points), values[label])
    np.testing.assert_array_equal(integer_oracle(model, points), values['original_first'])
    gold_full = np.load(run['inputs']['reference']['path'], mmap_mode='r'); gold = gold_full[keys]
    suffix = np.load(ROOT/'artifacts/cinema-first-hotspot-v1/suffix.npy', mmap_mode='r')
    danger_map = np.full(len(keys), -1, np.int32); danger_map[values['dangerous_rows']] = np.arange(len(values['dangerous_rows']), dtype=np.int32)
    offsets = allowed = None
    if summary['within_predeclared_resource_gate']:
        with np.load(args.study/'danger-allowed.npz') as data: csr_keys, offsets, allowed = data['source_keys'], data['offsets'], data['allowed_rgb']
        np.testing.assert_array_equal(csr_keys, keys[values['dangerous_rows']])
    queries, max_chunk_queries = 0, 0
    for start in range(0, len(keys), 512):
        stop = min(start+512, len(keys)); lower = values['lower_rgb'][start:stop].astype(np.int64)
        width = values['upper_rgb'][start:stop].astype(np.int64)-lower+1; counts = np.prod(width, axis=1, dtype=np.int64)
        begins = np.r_[0, np.cumsum(counts, dtype=np.int64)]
        rows = np.repeat(np.arange(stop-start), counts); local = np.arange(int(begins[-1]))-np.repeat(begins[:-1], counts)
        blue = local%width[rows, 2]; divided = local//width[rows, 2]
        green = divided%width[rows, 1]; red = divided//width[rows, 1]
        rgb = (lower[rows]+np.column_stack((red, green, blue))).astype(np.uint8)
        error = suffix[hs.key(rgb)].astype(np.int32)-gold[start:stop][rows].astype(np.int32)
        squared = np.sum(error*error, axis=1, dtype=np.int32); safe = squared <= 49
        low = np.minimum.reduceat(squared, begins[:-1]); high = np.maximum.reduceat(squared, begins[:-1])
        safe_count = np.add.reduceat(safe.astype(np.int64), begins[:-1])
        np.testing.assert_array_equal(low, values['minimum_squared'][start:stop])
        np.testing.assert_array_equal(high, values['maximum_squared'][start:stop])
        np.testing.assert_array_equal(counts, values['query_count'][start:stop])
        np.testing.assert_array_equal(safe_count, values['safe_count'][start:stop])
        if offsets is not None:
            for point in np.flatnonzero(danger_map[start:stop] >= 0):
                index = danger_map[start+point]
                expected = rgb[begins[point]:begins[point+1]][safe[begins[point]:begins[point+1]]]
                np.testing.assert_array_equal(expected, allowed[offsets[index]:offsets[index+1]])
        queries += len(rgb); max_chunk_queries = max(max_chunk_queries, len(rgb))
    dangerous = np.flatnonzero(values['maximum_squared'] > 49)
    np.testing.assert_array_equal(dangerous, values['dangerous_rows'])
    assert queries == summary['aabb_queries_first_pass']
    assert int(values['safe_count'][dangerous].sum(dtype=np.int64)) == summary['safe_triples_in_dangerous_rows']
    assert int(np.count_nonzero(values['safe_count'][dangerous] == 0)) == summary['zero_safe_triple_rows']
    save(args.output, {'pass': True, 'source_sha256': digest(__file__), 'summary_sha256': digest(args.study/'summary.json'),
         'screen_sha256': digest(args.study/'screen.npz'), 'checked_source_rows': len(keys), 'checked_rgb_queries': queries,
         'maximum_chunk_rgb_queries': max_chunk_queries, 'dangerous_rows': len(dangerous),
         'safe_csr_checked': offsets is not None, 'cp_solver_called': False,
         'scope': '独立四角u64端点及每源点flatten展开重算全部RGB统计/安全CSR，非CP求解或平均预算证明。'})


if __name__ == '__main__': main()
