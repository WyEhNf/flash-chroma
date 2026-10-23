"""有向四面体设计/六区域前向/八色完整支撑方向的独立uint64合同，不拟合。"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numba
import numpy as np
from lutlab import channel_coordinates as cc, channel_global_nodes as cg, channel_joint_nodes as cj
from lutlab import channel_tail_nodes as tail, oriented_tetra as ot, io, study_provenance
from run_channel_tail_nodes import digest, save
from study_velvia_body_diagonals import physical_oracle
from study_velvia_stripe_diagonals import dense, MASKS


def independent(model, points, choices):
    width = model.m-1
    cells = (model.idx[0, points[:, 0]].astype(np.int64)*width+model.idx[1, points[:, 1]])*width+model.idx[2, points[:, 2]]
    output = np.empty(points.shape, np.uint8)
    for mask in (0, 1, 2, 4):
        use = choices[cells] == mask
        output[use] = physical_oracle(model, points[use], mask)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖有向支撑合同')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    numba.set_num_threads(4)
    rng = np.random.default_rng(2026102422)
    keys = np.arange(256**3, dtype=np.uint32)
    identity = np.column_stack((keys >> 16, (keys >> 8)&255, keys&255)).astype(np.uint8)
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    records = []
    for m in (17, 33):
        grid = np.tile(np.linspace(0, 255, m), (3, 1))
        model = cc.from_sparse(io.SparseLut(grid, rng.integers(116, 140, (m, m, m, 3), dtype=np.uint8)))
        for c in range(3):
            model.channel_frac[c, :, 1:255] = np.clip(model.channel_frac[c, :, 1:255].astype(np.int64)+(c-1)*113, 0, io.ONE)
        choices = MASKS[dense(rng.integers(0, 2, (3, m-1), dtype=np.uint8))]
        points = rng.integers(0, 256, (2056, 3), dtype=np.uint8)
        points[:8] = np.array(np.meshgrid(*[[0, 255]]*3, indexing='ij')).reshape(3, -1).T
        reference = rng.integers(120, 136, points.shape, dtype=np.uint8)
        mass = rng.random(len(points)); mass /= mass.sum()
        indices, weights = ot.design(model, points, choices)
        acc, squared = cj.accumulate(indices, weights, model.nodes.reshape(-1, 3), reference)
        old = independent(model, points, choices)
        np.testing.assert_array_equal(old, ot.predict(model, points, choices))
        np.testing.assert_array_equal(old, cg.design_output(model.nodes.reshape(-1, 3), indices, weights))
        initial, old_squared = tail.measure(old, reference, identity, mass, 40, 100)
        np.testing.assert_array_equal(squared, old_squared)
        caps = old_squared+rng.integers(0, 9, len(points), dtype=np.int32)
        colours = cj.parity(m)
        maximum_error, checked = 0., 0
        for colour in range(8):
            change, bad, invalid = tail.gains(indices, weights, acc, reference, identity, mass,
                model.nodes.reshape(-1, 3), colours, colour, caps, root, 4, 40, 100)
            if invalid:
                raise AssertionError('有向geometry不满足8色共同支撑')
            active = np.unique(indices[weights > 0])
            active = active[colours[active] == colour][:3]
            for node in active:
                for direction in (0, 12, 25):
                    nodes = model.nodes.reshape(-1, 3).copy()
                    nodes[node] = nodes[node].astype(np.int32)+cj.DIRECTIONS[direction]
                    trial = cc.ChannelLut(model.grid, nodes.reshape(model.nodes.shape), model.idx, model.channel_frac)
                    value = independent(trial, points, choices)
                    actual, sq = tail.measure(value, reference, identity, mass, 40, 100)
                    error = float(np.max(np.abs(actual-initial-change[:, direction, node])))
                    maximum_error = max(maximum_error, error)
                    if error > 1e-9 or bad[direction, node] != np.count_nonzero(sq > caps):
                        raise AssertionError('有向完整支撑gain或逐色cap不符')
                    checked += 1
        records.append({'m': m, 'points': len(points), 'node_directions_checked': checked,
            'fresh_vs_design_vs_independent_byte_mismatches': 0, 'maximum_gain_error': maximum_error,
            'cap_mismatches': 0, 'eight_colour_shared_support_pass': True})
    save(args.output, {'pass': True, 'records': records, 'seed': 2026102422, 'numba_threads': 4,
        'environment': study_provenance.environment_fingerprint(),
        'source_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in [Path(__file__), ROOT/'python/lutlab/oriented_tetra.py']},
        'scope': '17/33有限独立整数/方向合同，不证明真实拟合收益，不作原生或性能。'})
    print({'pass': True, 'records': records}, flush=True)


if __name__ == '__main__':
    main()
