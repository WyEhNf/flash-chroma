"""只证明首阶段全域max颜色在末级单节点邻域是否可改，不宣称全域门禁通过。"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import channel_coordinates as cc, channel_global_nodes as cg, channel_joint_nodes as cj, io
from run_channel_tail_nodes import load_model, digest, save
from verify_channel_coordinates import integer_oracle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-root', type=Path, required=True)
    parser.add_argument('--initial', type=Path, required=True)
    parser.add_argument('--cube', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖热点证书')
    cache = args.cache_root.resolve()
    if digest(args.cube) != '1fc01a27aa1737428d2a652a93cf9efcfd336e00b8dce81114563f9bd99c18ca':
        raise ValueError('不是首阶段incumbent完整流')
    reference = np.load(cache/'artifacts/cinema-axis-calibration-v1/envelope-reference.npy', mmap_mode='r')
    stream = np.memmap(args.cube, np.uint8, 'r', shape=(256**3, 3))
    largest, ids = -1, []
    for start in range(0, len(stream), 1 << 18):
        delta = stream[start:start+(1 << 18)].astype(np.int32)-reference[start:start+(1 << 18)].astype(np.int32)
        squared = np.sum(delta*delta, axis=1, dtype=np.int32)
        block_max = int(squared.max())
        if block_max > largest:
            largest, ids = block_max, []
        if block_max == largest:
            ids.extend((start+np.flatnonzero(squared == largest)).tolist())
    ids = np.asarray(ids, np.int64)
    rgb = np.column_stack((ids >> 16, (ids >> 8)&255, ids&255)).astype(np.uint8)
    first = load_model(args.initial)
    reached = integer_oracle(first, rgb)
    for stage in (2, 3):
        sparse = io.load_sparse(cache/'artifacts/cinema-envelope-v1/stage4_sweep004'/f'selected-stage{stage}.slut')
        reached = integer_oracle(cc.from_sparse(sparse), reached)
    last_path = cache/'artifacts/cinema-envelope-v1/stage4_sweep004/selected-stage4.slut'
    last = cc.from_sparse(io.load_sparse(last_path))
    np.testing.assert_array_equal(integer_oracle(last, reached), stream[ids])
    indices, weights = cg.design(last, reached)
    support = np.unique(indices[weights > 0])
    trials = []
    for n in support[:32]:
        for scale in (1, 2, 4):
            for d in cj.DIRECTIONS:
                value = last.nodes.reshape(-1, 3)[n].astype(np.int32)+scale*d
                if np.any(value < 0) or np.any(value > 255):
                    continue
                nodes = last.nodes.copy(); nodes.reshape(-1, 3)[n] = value
                proposed = cc.ChannelLut(last.grid, nodes, last.idx, last.channel_frac)
                result = integer_oracle(proposed, reached)
                delta = result.astype(np.int32)-reference[ids].astype(np.int32)
                square = np.sum(delta*delta, axis=1, dtype=np.int32)
                trials.append({'node': int(n), 'direction': (scale*d).tolist(), 'max_squared': int(square.max()),
                               'unreduced_max_colours': int(np.count_nonzero(square >= largest)),
                               'mean': float(np.sqrt(square.astype(np.float64)).mean())})
    trials.sort(key=lambda v: (v['max_squared'], v['unreduced_max_colours'], v['mean'], v['node'], v['direction']))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    save(args.output, {'input_sha256': {'cube': digest(args.cube), 'first_model': digest(args.initial), 'last_model': digest(last_path)},
        'source_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in [Path(__file__), ROOT/'scripts/verify_channel_coordinates.py']},
        'scope': '完整首阶段max颜色全部提取，但仅在这些颜色上评价末级单节点±1/2/4，不读取照片，不保护其余颜色；不是新模型的完整准确性证书。',
        'max_squared': largest, 'colours': len(ids), 'unique_last_stage_inputs': np.unique(reached, axis=0).tolist(),
        'support_nodes': support.tolist(), 'support_nodes_checked': support[:32].tolist(), 'trials': len(trials),
        'best': trials[:12], 'all_max_colours_locally_reducible': bool(trials and trials[0]['max_squared'] < largest)})
    print(args.output.read_text(encoding='utf-8'), flush=True)


if __name__ == '__main__':
    main()
