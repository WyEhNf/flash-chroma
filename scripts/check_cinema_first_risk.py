"""有限17/33完整小节点域穷举，检查首级AABB与鲁棒危险判定。"""
from __future__ import annotations
import argparse
import itertools
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import channel_coordinates as cc, channel_hotspot_support as hs, channel_first_risk as risk, io
from run_channel_tail_nodes import digest, save
from verify_channel_coordinates import integer_oracle


def lookup(rgb):
    r, g, b = rgb.astype(np.int64).T
    return np.column_stack(((r+g)%11, (2*g+b)%11, (r+2*b)%11)).astype(np.uint8)


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖鲁棒危险有限合同')
    records = []
    for m in (17, 33):
        model = cc.from_sparse(io.SparseLut(np.tile(np.linspace(0, 255, m), (3, 1)), np.full((m, m, m, 3), 127, np.uint8)))
        points = np.array([[8, 4, 2], [9, 5, 3], [200, 200, 200]], np.uint8)
        for c in range(3):
            model.channel_frac[c, :, 1:255] = np.clip(model.channel_frac[c, :, 1:255].astype(np.int64)+(c-1)*131, 0, io.ONE)
        cc.validate(model); raw_i, raw_w, _ = hs.basis(model, points)
        selected = np.unique(raw_i[:, 0][raw_w[:, 0] > 0])[:2]
        model.nodes.reshape(-1, 3)[selected] = np.array([[0, 255, 127], [255, 0, 128]] if m == 17 else [[127, 127, 127], [128, 128, 128]], np.uint8)
        raw_i, raw_w, acc = hs.basis(model, points)
        original = model.nodes.reshape(-1, 3)[selected].astype(np.int64)
        low_nodes = model.nodes.copy(); high_nodes = model.nodes.copy()
        low = np.maximum(original-2, 0); high = np.minimum(original+2, 255)
        low_nodes.reshape(-1, 3)[selected] = low; high_nodes.reshape(-1, 3)[selected] = high
        lower = integer_oracle(cc.ChannelLut(model.grid, low_nodes, model.idx, model.channel_frac), points)
        upper = integer_oracle(cc.ChannelLut(model.grid, high_nodes, model.idx, model.channel_frac), points)
        gold = np.zeros_like(points); gold[-1] = lookup(integer_oracle(model, points[-1:]))[0]
        minimum, maximum, counts, safe = risk.enumerate_stats(lower, upper, gold, lookup)
        offsets, allowed = risk.collect_allowed(lower, upper, gold, lookup)
        node_weights = np.stack([np.sum(np.where(raw_i == node, raw_w, 0), axis=2).T for node in selected], axis=1)
        fixed = acc-np.sum(node_weights*original[None], axis=1, dtype=np.int64)
        assignments = np.array(list(itertools.product(*[range(int(low[n, c]), int(high[n, c])+1) for n in range(2) for c in range(3)])), np.int64).reshape(-1, 2, 3)
        actual_acc = fixed[None]+np.sum(assignments[:, None]*node_weights[None], axis=2, dtype=np.int64)
        actual_rgb = ((actual_acc+32768)>>16).astype(np.uint8)
        for point in range(len(points)):
            box_values = np.array(list(itertools.product(*[range(int(lo), int(hi)+1) for lo, hi in zip(lower[point], upper[point])])), np.uint8)
            reached = np.unique(actual_rgb[:, point], axis=0)
            np.testing.assert_array_equal(reached, box_values)
            error = lookup(box_values).astype(np.int32)-gold[point].astype(np.int32)
            sq = np.sum(error*error, axis=1, dtype=np.int32)
            assert int(sq.min()) == minimum[point] and int(sq.max()) == maximum[point] and len(sq) == counts[point]
            assert int(np.count_nonzero(sq <= 49)) == safe[point]
            np.testing.assert_array_equal(allowed[offsets[point]:offsets[point+1]], box_values[sq <= 49])
        assert maximum[-1] == 0
        records.append({'m': m, 'source_points': len(points), 'variable_nodes': len(selected), 'exhaustive_node_assignments': len(assignments),
                        'point_reachable_set_equals_aabb': True, 'fixed_far_point_certified_safe': True, 'minimum': minimum.tolist(), 'maximum': maximum.tolist()})
    sources = [Path(__file__), ROOT/'python/lutlab/channel_first_risk.py', ROOT/'scripts/screen_cinema_first_risk.py',
               ROOT/'scripts/audit_cinema_first_risk.py', ROOT/'experiments/p16-cinema-first-risk-v1.json']
    save(args.output, {'pass': True, 'cases': records, 'source_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in sources},
         'scope': '有限17/33完整小节点域穷举；单点可达=AABB，跨输入共享节点耦合仍在，不能推出联合可行。'})


if __name__ == '__main__': main()
