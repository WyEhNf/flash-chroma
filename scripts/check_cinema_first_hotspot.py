"""独立有限17/33节点合同，检查完整编码盒、八角权重、整数更新和精确直方图。"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import channel_coordinates as cc, channel_hotspot_support as hs, io
from run_channel_tail_nodes import save, digest
from verify_channel_coordinates import integer_oracle


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): raise ValueError('不覆盖有限合同')
    rng = np.random.default_rng(2026102450); records = []
    for m in (17, 33):
        sparse = io.SparseLut(np.tile(np.linspace(0, 255, m), (3, 1)), rng.integers(20, 230, (m, m, m, 3), dtype=np.uint8))
        model = cc.from_sparse(sparse)
        for channel in range(3):
            model.channel_frac[channel, :, 1:255] = np.clip(model.channel_frac[channel, :, 1:255].astype(np.int64)+(channel-1)*127, 0, io.ONE)
        cc.validate(model)
        sample = rng.integers(0, 256, (1024, 3), dtype=np.uint8)
        _, _, acc = hs.basis(model, sample)
        np.testing.assert_array_equal(((acc+32768)>>16).astype(np.uint8), integer_oracle(model, sample))
        for physical in (0, (m//2*m+m//2)*m+m//2, m**3-1):
            points, acc, weight = hs.support(model, physical, 1 << 20)
            i, w = hs.corners(model, sample)
            expected = np.any((i == physical) & np.any(w > 0, axis=2), axis=1)
            available = np.isin(hs.key(sample), hs.key(points))
            np.testing.assert_array_equal(expected, available)
            for delta in hs.DIRECTIONS:
                nodes = model.nodes.copy(); nodes.reshape(-1, 3)[physical] = nodes.reshape(-1, 3)[physical].astype(np.int32)+delta
                candidate = cc.ChannelLut(model.grid, nodes, model.idx, model.channel_frac)
                predicted = ((acc+weight.astype(np.int64)*delta+32768)>>16).astype(np.uint8)
                np.testing.assert_array_equal(predicted, integer_oracle(candidate, points))
            records.append({'m': m, 'physical_node': physical, 'complete_support_rows': len(points), 'directions': 52})
    square = np.array([0, 1, 4, 9, 16, 25, 36, 49, 50], np.int32)
    count = np.array([10, 3, 11, 5, 1, 7, 2, 5, 1], np.int64)
    measured = hs.metrics(hs.histogram(square, count)); expanded = np.repeat(np.sqrt(square), count)
    if (abs(measured['mean']-expanded.mean()) > 1e-12 or abs(measured['rms']-np.sqrt((expanded**2).mean())) > 1e-12 or
            abs(measured['p99']-np.quantile(expanded, .99)) > 1e-12 or
            abs(measured['cvar_1pct']-np.sort(expanded)[-int(np.ceil(len(expanded)*.01)):].mean()) > 1e-12):
        raise AssertionError('独立展开频数统计不符')
    sources = [Path(__file__), ROOT/'python/lutlab/channel_hotspot_support.py', ROOT/'scripts/run_cinema_first_hotspot.py',
               ROOT/'experiments/p16-cinema-first-hotspot-v1.json']
    save(args.output, {'pass': True, 'cases': records, 'source_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in sources},
                      'scope': '有限17/33节点、边界/内部及52方向合同；不等于真实模型完整域或速度通过'})


if __name__ == '__main__': main()
