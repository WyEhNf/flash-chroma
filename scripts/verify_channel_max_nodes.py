"""用独立uint64暴力重算，验证±2/±4提议的九项完整支撑统计与cap。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numba
import numpy as np
from lutlab import channel_coordinates as cc, channel_global_nodes as cg, channel_joint_nodes as cj
from lutlab import channel_max_nodes as tail, io
from verify_channel_coordinates import integer_oracle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖已有合同')
    numba.set_num_threads(4)
    rng = np.random.default_rng(20261023)
    suffix = np.empty((256**3, 3), np.uint8)
    for start in range(0, len(suffix), 1 << 18):
        keys = np.arange(start, min(start+(1 << 18), len(suffix)), dtype=np.int64)
        r, g, b = keys >> 16, (keys >> 8)&255, keys&255
        suffix[start:start+len(keys)] = np.column_stack(((r+g//8)%256, np.minimum(g+((b//32)%2)*3, 255), b^((r//64)*3)))
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    cases = []
    for m in (17, 33):
        sparse = io.SparseLut(io.uniform_grid(m), rng.integers(0, 256, (m, m, m, 3), dtype=np.uint8))
        model = cc.from_sparse(sparse)
        for c in range(3):
            model.channel_frac[c] = ((model.channel_frac[c].astype(np.uint64)*(20-c))//20).astype(np.uint32)
        points = rng.integers(0, 256, (768, 3), dtype=np.uint8)
        points[:8] = np.asarray([[r, g, b] for r in (0, 255) for g in (0, 255) for b in (0, 255)], np.uint8)
        original = integer_oracle(model, points)
        key = original.astype(np.int64)@np.array([65536, 256, 1], np.int64)
        reference = np.clip(suffix[key].astype(np.int32)+rng.integers(-6, 7, original.shape), 0, 255).astype(np.uint8)
        mass = rng.random(len(points)); mass[::3] = 0.; mass /= mass.sum()
        initial, square = tail.measure(original, reference, suffix, mass)
        caps = np.maximum(49, square)
        indices, weights = cg.design(model, points)
        acc, _ = cj.accumulate(indices, weights, model.nodes.reshape(-1, 3), reference)
        colours = cj.parity(m)
        error, forbidden_mismatches, probes = 0., 0, 0
        for colour in range(8):
            changes, bad, invalid = tail.gains(indices, weights, acc, reference, suffix, mass,
                model.nodes.reshape(-1, 3), colours, colour, caps, root, 4)
            if invalid:
                raise AssertionError('几何合同失败')
            possible = np.unique(indices[weights > 0])
            possible = possible[colours[possible] == colour][:3]
            for n in possible:
                for d in (0, 9, 16, 25, 26, 35, 42, 51):
                    values = model.nodes.reshape(-1, 3)[n].astype(np.int32)+tail.DIRECTIONS[d]
                    if np.any(values < 0) or np.any(values > 255):
                        if not bad[d, n]:
                            forbidden_mismatches += 1
                        continue
                    nodes = model.nodes.copy(); nodes.reshape(-1, 3)[n] = values
                    proposed = cc.ChannelLut(model.grid, nodes, model.idx, model.channel_frac)
                    output = integer_oracle(proposed, points)
                    fresh, squared = tail.measure(output, reference, suffix, mass)
                    error = max(error, float(np.max(np.abs(fresh-initial-changes[:, d, n]))))
                    forbidden_mismatches += int(bad[d, n] != np.count_nonzero(squared > caps))
                    probes += 1
        if error > 1e-8 or forbidden_mismatches:
            raise AssertionError('独立oracle收益或cap不符')
        cases.append({'m': m, 'pixels': len(points), 'zero_mass_pixels': int(np.count_nonzero(mass == 0)),
                      'independent_node_direction_probes': probes, 'maximum_gain_error': error,
                      'forbidden_mismatches': forbidden_mismatches})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({'pass': True, 'seed': 20261023, 'cases': cases,
        'scope': '17/33网格、边界/随机原色、分输出权重、非线性后缀、零质量支撑；有限合同，不替代真实模型完整域和原生验证。'}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(cases), flush=True)


if __name__ == '__main__':
    main()
