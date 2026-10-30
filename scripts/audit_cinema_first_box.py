"""独立八角uint64复算116个首级节点盒端点，并重新枚举全部整数RGB后缀。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import channel_hotspot_support as hs
from run_channel_tail_nodes import load_model, digest, save


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--certificate', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖首级盒独立复核')
    value = json.loads(args.certificate.read_text(encoding='utf-8'))
    frozen_path = args.certificate.with_name(args.certificate.stem+'-frozen.json')
    assert digest(frozen_path) == value['frozen_identity_sha256']
    frozen = json.loads(frozen_path.read_text(encoding='utf-8'))
    assert all(value[k] == v for k, v in frozen.items())
    for name, sha in value['source_sha256'].items():
        if digest(ROOT/name) != sha: raise ValueError('冻结证书源已变化：'+name)
    for spec in value['inputs'].values():
        if digest(spec['path']) != spec['sha256']: raise ValueError('冻结证书输入已变化')
    assert digest(ROOT/'artifacts/cinema-first-hotspot-v1/support-index.npz') == value['support_index_sha256']
    original = load_model(value['inputs']['first']['path'])
    gold_full = np.load(value['inputs']['reference']['path'], mmap_mode='r')
    baseline = np.memmap(value['inputs']['cube']['path'], dtype=np.uint8, mode='r', shape=(256**3, 3))
    with np.load(ROOT/'artifacts/cinema-first-hotspot-v1/support-index.npz') as data:
        selected, hotspots = data['selected_nodes'], data['hotspot_keys']
    assert len(value['records']) == len(hotspots) == 116
    assert [r['source_key'] for r in value['records']] == hotspots.tolist()
    model_nodes = original.nodes.reshape(-1, 3).astype(np.uint64)
    variable = np.zeros(original.m**3, bool); variable[selected] = True
    low_nodes = model_nodes.copy(); high_nodes = model_nodes.copy()
    low_nodes[selected] = np.maximum(model_nodes[selected].astype(np.int64)-2, 0).astype(np.uint64)
    high_nodes[selected] = np.minimum(model_nodes[selected]+2, 255)
    points = hs.rgb(hotspots); ids, weights = hs.corners(original, points); weights = weights.astype(np.uint64)
    lower_acc = np.sum(weights*low_nodes[ids], axis=1, dtype=np.uint64)
    upper_acc = np.sum(weights*high_nodes[ids], axis=1, dtype=np.uint64)
    original_acc = np.sum(weights*model_nodes[ids], axis=1, dtype=np.uint64)
    lower, upper = (lower_acc+32768)>>16, (upper_acc+32768)>>16
    suffix = np.load(ROOT/'artifacts/cinema-first-hotspot-v1/suffix.npy', mmap_mode='r')
    assert digest(ROOT/'artifacts/cinema-first-hotspot-v1/suffix.npy') == value['suffix_sha256']
    blocked, queries, rows = 0, 0, []
    for position, record in enumerate(value['records']):
        assert record['gold_rgb'] == gold_full[hotspots[position]].tolist()
        assert record['baseline_final_rgb'] == baseline[hotspots[position]].tolist()
        assert record['baseline_first_rgb'] == ((original_acc[position]+32768)>>16).tolist()
        assert [c['baseline_acc'] for c in record['first_box']['channels']] == original_acc[position].tolist()
        assert record['first_box']['lower_rgb'] == lower[position].tolist()
        assert record['first_box']['upper_rgb'] == upper[position].tolist()
        assert [c['lower_acc'] for c in record['first_box']['channels']] == lower_acc[position].tolist()
        assert [c['upper_acc'] for c in record['first_box']['channels']] == upper_acc[position].tolist()
        axes = [np.arange(lower[position, a], upper[position, a]+1, dtype=np.uint32) for a in range(3)]
        arrivals = np.stack(np.meshgrid(*axes, indexing='ij'), axis=-1).reshape(-1, 3).astype(np.uint8)
        final = suffix[hs.key(arrivals)]; error = final.astype(np.int64)-np.array(record['gold_rgb'], np.int64)
        square = np.sum(error*error, axis=1, dtype=np.int64)
        counts = {str(d): int(np.count_nonzero(square == d)) for d in np.unique(square)}
        minimum = int(np.min(square)); best = int(np.argmin(square))
        assert counts == record['error_histogram'] and len(square) == record['enumerated_integer_rgb_count']
        assert minimum == record['relaxed_minimum_squared'] and arrivals[best].tolist() == record['argmin_first_rgb']
        assert final[best].tolist() == record['argmin_final_rgb']
        assert record['blocks_entire_node_component_box_at_49'] == (minimum > 49)
        blocked += int(minimum > 49); queries += len(square)
        rows.append({'source_key': record['source_key'], 'box_rows': len(square), 'necessary_lower_bound_squared': minimum})
    assert blocked == value['blocked_hotspots'] and queries == value['total_suffix_queries']
    assert value['entire_component_box_cannot_reach_max49'] == (blocked > 0)
    save(args.output, {'pass': True, 'certificate_sha256': digest(args.certificate), 'source_sha256': digest(__file__),
        'checked_hotspots': len(rows), 'checked_suffix_queries': queries, 'blocked_hotspots': blocked,
        'entire_component_box_cannot_reach_max49': blocked > 0, 'rows': rows,
        'scope': '独立八角uint64端点与全部放松整数RGB重新枚举通过；全部下界<=49仍不能证明整数节点和共享热点联合可行。'})


if __name__ == '__main__': main()
