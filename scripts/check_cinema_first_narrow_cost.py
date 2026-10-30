"""有限混合RGB活动分量窄域穷举，核完整几何正支撑与整数端点。"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import channel_coordinates as cc, channel_component_box as component, channel_hotspot_support as hs, io
from run_channel_tail_nodes import save, digest
from verify_channel_coordinates import integer_oracle


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖窄域有限合同')
    records = []
    for m in (17, 33):
        original = cc.from_sparse(io.SparseLut(np.tile(np.linspace(0, 255, m), (3, 1)), np.full((m, m, m, 3), 127, np.uint8)))
        for channel in range(3):
            original.channel_frac[channel, :, 1:255] = np.clip(original.channel_frac[channel, :, 1:255].astype(np.int64)+(channel-1)*131, 0, 65536)
        original.nodes.reshape(-1, 3)[:2] = [[0, 255, 127], [255, 0, 128]]
        witness_nodes = original.nodes.copy(); witness_nodes.reshape(-1, 3)[:2] = [[2, 254, 127], [253, 0, 129]]
        witness = cc.ChannelLut(original.grid, witness_nodes, original.idx, original.channel_frac)
        lower, upper, active = component.domains(original, witness)
        values = (0, 1, 7, 8, 9, 15, 16, 127, 128, 254, 255)
        points = np.array(list(itertools.product(values, repeat=3)), np.uint8)
        hats = component.positive_hats(original, points, active); tetra = component.positive_tetra(original, points, active)
        np.testing.assert_array_equal(hats, tetra)
        low, high, low_acc, high_acc = component.endpoint_rgb(original, points, lower, upper)
        np.testing.assert_array_equal(hats, np.any(low_acc != high_acc, axis=1))
        keys, profile = component.complete_support(original, active, full_domain=False)
        np.testing.assert_array_equal(np.isin(hs.key(points), keys), hats)
        selected = np.argwhere(active); assignments = list(itertools.product(*[range(int(lower[n, c]), int(upper[n, c])+1) for n, c in selected]))
        outcomes = []
        for assignment in assignments:
            nodes = original.nodes.copy(); flat = nodes.reshape(-1, 3)
            for (node, channel), delta in zip(selected, assignment): flat[node, channel] = int(flat[node, channel])+delta
            candidate = cc.ChannelLut(original.grid, nodes, original.idx, original.channel_frac)
            first = integer_oracle(candidate, points); outcomes.append(first)
            np.testing.assert_array_equal(first[~hats], integer_oracle(original, points[~hats]))
        outcomes = np.array(outcomes)
        np.testing.assert_array_equal(outcomes.min(axis=0), low); np.testing.assert_array_equal(outcomes.max(axis=0), high)
        for i in range(len(points)):
            expected = np.array(list(itertools.product(*[range(int(a), int(b)+1) for a, b in zip(low[i], high[i])])), np.uint8)
            np.testing.assert_array_equal(np.unique(outcomes[:, i], axis=0), expected)
        records.append({'m': m, 'sampled_finite_rgb_points': len(points), 'node_assignments': len(assignments),
            'active_components': len(selected), 'geometry_support_rows': len(keys), 'reachable_rgb_equals_aabb': True,
            'fixed_components_preserved': True, 'zero_training_mass_coverage': '复用整数成本合同零权重案例'})
    costs_path = ROOT/'artifacts/cinema-first-error-cost-contract-v1.json'; costs = json.loads(costs_path.read_text(encoding='utf-8'))
    assert costs['pass']
    for name, expected in costs['source_sha256'].items():
        if digest(ROOT/name) != expected: raise ValueError('既有完整成本合同源已变')
    names = set(costs['source_sha256']) | {'python/lutlab/channel_component_box.py', 'scripts/check_cinema_first_narrow_cost.py',
        'scripts/census_cinema_first_narrow_cost.py', 'experiments/p16-cinema-first-narrow-cost-census-v1.json'}
    save(args.output, {'pass': True, 'cases': records, 'reused_error_cost_contract_sha256': digest(costs_path),
        'source_sha256': {name: digest(ROOT/name) for name in sorted(names)},
        'scope': '有限混合节点分量闭整数域穷举；真实窄域完整16M独立支撑验证由唯一普查执行，不建CP。'})
    print({'pass': True, 'cases': len(records)}, flush=True)


if __name__ == '__main__': main()
