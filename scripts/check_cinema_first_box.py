"""有限17/33合同：纯Python首级acc盒与独立uint64端点和随机内部节点。"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import channel_coordinates as cc, channel_hotspot_support as hs, integer_first_box as box, io
from run_channel_tail_nodes import digest, save
from verify_channel_coordinates import integer_oracle


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖首级盒有限合同')
    rng = np.random.default_rng(2026102449); records = []
    for m in (17, 33):
        grid = np.tile(np.linspace(0, 255, m), (3, 1)); values = rng.integers(0, 256, (m, m, m, 3), dtype=np.uint8)
        model = cc.from_sparse(io.SparseLut(grid, values)); points = rng.integers(0, 256, (37, 3), dtype=np.uint8)
        points[:2] = [[0, 0, 0], [255, 255, 255]]
        for c in range(3):
            model.channel_frac[c, :, 1:255] = np.clip(model.channel_frac[c, :, 1:255].astype(np.int64)+(c-1)*137, 0, io.ONE)
        cc.validate(model); indices, weights, _ = hs.basis(model, points)
        available = np.unique(indices[weights > 0]); selected = available[::2]
        bounds = [box.point_box(model, p.tolist(), selected) for p in points]
        lower, upper = np.array([b['lower_rgb'] for b in bounds], np.uint8), np.array([b['upper_rgb'] for b in bounds], np.uint8)
        for step, expected in ((-2, lower), (2, upper)):
            nodes = model.nodes.copy(); nodes.reshape(-1, 3)[selected] = np.clip(nodes.reshape(-1, 3)[selected].astype(np.int32)+step, 0, 255)
            endpoint = cc.ChannelLut(model.grid, nodes, model.idx, model.channel_frac)
            np.testing.assert_array_equal(integer_oracle(endpoint, points), expected)
        for trial in range(16):
            nodes = model.nodes.copy(); nodes.reshape(-1, 3)[selected] = np.clip(nodes.reshape(-1, 3)[selected].astype(np.int32)+rng.integers(-2, 3, (len(selected), 3)), 0, 255)
            output = integer_oracle(cc.ChannelLut(model.grid, nodes, model.idx, model.channel_frac), points)
            if np.any(output < lower) or np.any(output > upper): raise AssertionError('内部节点随机试验越过必要包围盒')
        records.append({'m': m, 'points': len(points), 'variable_nodes': len(selected), 'independent_endpoints': 2, 'random_internal_models': 16})
    sources = [Path(__file__), ROOT/'scripts/certify_cinema_first_box.py', ROOT/'python/lutlab/integer_first_box.py',
               ROOT/'experiments/p16-cinema-first-box-v1.json']
    save(args.output, {'pass': True, 'cases': records, 'source_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in sources},
                      'scope': '仅有限17/33端点和随机内部模型合同；未验证实际116热点的必要下界'})


if __name__ == '__main__': main()
