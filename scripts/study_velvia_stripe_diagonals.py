"""冻结96bit面相容方向场：两起点各两扫，只读cell统计求受约束可行项。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import channel_coordinates as cc, io, study_provenance
from accept_velvia_cell_diagonals import exact_faces
from run_channel_tail_nodes import digest, save

MASKS = np.array([0, 1, 2, 4], np.uint8)
INDICES = np.array([0, 1, 2, 3, 3, 2, 1, 0], np.uint8)


def dense(bits):
    width = bits.shape[1]
    raw = bits[0, :, None, None]+2*bits[1, None, :, None]+4*bits[2, None, None, :]
    return INDICES[raw].reshape(width**3)


def face_contract():
    rng = np.random.default_rng(2026102421)
    result = []
    for m in (17, 33):
        grid = np.tile(np.linspace(0, 255, m), (3, 1))
        model = cc.from_sparse(io.SparseLut(grid, rng.integers(0, 256, (m, m, m, 3), dtype=np.uint8)))
        bits = rng.integers(0, 2, (3, m-1), dtype=np.uint8)
        choices = MASKS[dense(bits)]
        faces = exact_faces(model, choices)
        if any(row['faces_with_sampled_discontinuity'] or row['sampled_jump']['max'] for row in faces):
            raise AssertionError('stripe面相容合同失败')
        result.append({'m': m, 'stripe_bits': bits.tolist(), 'faces': faces})
    return {'seed': 2026102421, 'pass': True, 'records': result,
        'proof': '跨R面时G/B位不变，跨G面时R/B位不变，跨B面时R/G位不变；每面的二维对角线只由该两位xor决定。互补mask的几何等价，因此归一成0/1/2/4后仍匹配。有限u64面采样检验不替代该代数论证。'}


def score(values, baseline):
    ratios = values/baseline
    positive = np.maximum(ratios-1., 0.)
    return (float(positive.max()), float(positive.sum()), float(ratios[2]), float(ratios[0]))


def improves(new, old):
    for a, b in zip(new, old):
        if a < b-1e-12:
            return True
        if a > b+1e-12:
            return False
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖受限方向场冻结结果')
    args.output.mkdir(parents=True)
    path = ROOT/'artifacts/velvia-cell-feasibility-v1/cell-statistics.npz'
    save(args.output/'run.json', {'input_sha256': {str(path): digest(path)},
        'source_sha256': {'scripts/study_velvia_stripe_diagonals.py': digest(Path(__file__))},
        'environment': study_provenance.environment_fingerprint(),
        'policy': '先17/33随机stripe面合同和96个基线单slab；固定global1/global2两起点各两扫，每扫R/G/B及0..31，max d²<=1522始终硬约束；五指标正超额(max,sum)作可行性目标，再训练mean、uniformmean。最终五约束全过才可选，按训练mean、uniformmean、起点序选择，不看照片。',
        'scope': '96个布尔变量受限局部坐标下降，不证明方向场全局最优，不改节点/轴，不调用原生或性能。初始mean可不合格，不放宽最终门禁。'})
    save(args.output/'face-contract.json', face_contract())
    data = np.load(path)
    stats, maximum = data['stats'], data['max_squared']
    cells = np.arange(stats.shape[1])
    baseline = stats[0].sum(axis=0)
    def evaluate(bits):
        indices = dense(bits)
        return stats[indices, cells].sum(axis=0), int(maximum[indices, cells].max()), indices
    singles = []
    for axis in range(3):
        for code in range(32):
            bits = np.zeros((3, 32), np.uint8); bits[axis, code] = 1
            values, cap, _ = evaluate(bits)
            singles.append({'axis': axis, 'cell_coordinate': code, 'metrics': values.tolist(), 'max_squared': cap,
                'all_five_nonincrease': bool(np.all(values <= baseline+1e-7))})
    save(args.output/'single-slabs.json', singles)
    runs = []
    for start in (1, 2):
        bits = np.zeros((3, 32), np.uint8); bits[start-1] = 1
        values, cap, indices = evaluate(bits)
        if cap != 1522:
            raise AssertionError('冻结起点不是已证1522上界')
        records = []
        for sweep in range(2):
            for axis in range(3):
                for code in range(32):
                    trial = bits.copy(); trial[axis, code] ^= 1
                    candidate, cap, candidate_indices = evaluate(trial)
                    if cap <= 1522 and improves(score(candidate, baseline), score(values, baseline)):
                        records.append({'sweep': sweep, 'axis': axis, 'cell_coordinate': code,
                            'before': values.tolist(), 'after': candidate.tolist(), 'score': score(candidate, baseline)})
                        bits, values, indices = trial, candidate, candidate_indices
        final_cap = int(maximum[indices, cells].max())
        feasible = bool(final_cap <= 1522 and np.all(values <= baseline+1e-7))
        runs.append({'initial_global_mask': start, 'metrics': values.tolist(), 'max_squared': final_cap,
            'score': score(values, baseline), 'five_constraints_passed': feasible, 'stripe_bits': bits.tolist(), 'accepted_moves': records})
        print(json.dumps({k: v for k, v in runs[-1].items() if k not in ('stripe_bits', 'accepted_moves')}, ensure_ascii=False), flush=True)
    feasible = [r for r in runs if r['five_constraints_passed']]
    result = {'baseline_metrics': baseline.tolist(), 'runs': runs, 'feasible': bool(feasible), 'new_default': False}
    if feasible:
        chosen = min(feasible, key=lambda r: (r['metrics'][2], r['metrics'][0], r['initial_global_mask']))
        bits = np.array(chosen['stripe_bits'], np.uint8)
        bits.tofile(args.output/'selected-stripes-byte.bin')
        packed = np.packbits(bits.reshape(-1), bitorder='little')
        np.testing.assert_array_equal(np.unpackbits(packed, bitorder='little'), bits.reshape(-1))
        packed.tofile(args.output/'selected-stripes-packed.bin')
        MASKS[dense(bits)].tofile(args.output/'selected-cell-orientation.bin')
        result['selected_initial_global_mask'] = chosen['initial_global_mask']
        result['selected_metrics'] = chosen['metrics']
        result['serialized_stripe_bytes'] = {'byte_per_bit': int(bits.nbytes), 'bitpacked': int(packed.nbytes), 'expanded_cell_masks': 32768}
    save(args.output/'results.json', result)


if __name__ == '__main__':
    main()
