"""仅两个原max点/两cell完整612支撑的边界消失局部混合可行性探针。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import io, study_provenance
from run_channel_tail_nodes import load_model, digest, save
from accept_channel_tail_nodes import histogram
from accept_channel_coordinates import hist_metrics


def accumulator(model, points, mask):
    base = sum(model.idx[a, points[:, a]].astype(np.int64)*model.m**(2-a) for a in range(3))
    steps = np.tile(np.array([model.m**2, model.m, 1], np.int64), (len(points), 1))
    for a in range(3):
        if mask & (1 << a):
            base += steps[:, a]; steps[:, a] *= -1
    result = np.empty(points.shape, np.uint64)
    for c in range(3):
        f = np.column_stack([model.channel_frac[c, a, points[:, a]] for a in range(3)]).astype(np.int64)
        stride = steps.copy()
        for a in range(3):
            if mask & (1 << a):
                f[:, a] = io.ONE-f[:, a]
        order = np.argsort(-f, axis=1, kind='stable')
        f, stride = np.take_along_axis(f, order, axis=1), np.take_along_axis(stride, order, axis=1)
        weights = np.column_stack((io.ONE-f[:, 0], f[:, 0]-f[:, 1], f[:, 1]-f[:, 2], f[:, 2])).astype(np.uint64)
        ids = np.column_stack((base, base+stride[:, 0], base+stride[:, :2].sum(axis=1), base+stride.sum(axis=1)))
        result[:, c] = np.sum(weights*model.nodes.reshape(-1, 3)[ids, c].astype(np.uint64), axis=1, dtype=np.uint64)
    return result


def bubble(old, alternative, weights):
    mixed = (io.ONE-weights)*old+weights*alternative
    if np.any(mixed > np.uint64(255)*io.ONE**2):
        raise AssertionError('Q32混合越过RGB8凸界')
    value = ((mixed+np.uint64(1 << (2*io.Q-1))) >> (2*io.Q)).astype(np.uint8)
    expected = np.array([[(int(io.ONE-w)*int(a)+int(w)*int(b)+(1 << (2*io.Q-1))) >> (2*io.Q)
        for a, b, w in zip(a_row, b_row, w_row)] for a_row, b_row, w_row in zip(old, alternative, weights)], np.uint8)
    np.testing.assert_array_equal(value, expected)
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖最小bubble探针')
    cache = args.cache_root.resolve()
    model_path = cache/'artifacts/velvia-channel-coordinates-v1/channel-coordinates.npz'
    table_path = cache/'artifacts/chain-error-cache/source-2ff0a4e385f9f9e49ca02f63/table.lut256'
    baseline_path = cache/'artifacts/velvia-channel-coordinates-accept-v1/cube.rgb'
    expected = ['3e5f8fd94e8dc9b97dbfea2823896b8dffb6e014b5e6056ab5c10b58a69af3d0',
        '6c4387352bd0845ce597f13dca32f2f808b39439d06ce78b4881922a4fc294b7',
        '945d4b906ae9aa184fdddd7f084da0105fa87b7e756f88ea700ca53f61ed37f0']
    if [digest(p) for p in (model_path, table_path, baseline_path)] != expected:
        raise ValueError('必须保持原3e5f及冻结参考/完整流')
    model = load_model(model_path)
    reference = io.load_full(table_path, mmap=True).reshape(-1, 3)
    baseline = np.memmap(baseline_path, np.uint8, 'r', shape=reference.shape)
    mass_path = cache/'artifacts/cinema-axis-calibration-v1/photo-arrival-frequency.npy'
    mass = np.load(mass_path, mmap_mode='r')
    total_mass = float(mass.sum(dtype=np.float64))
    result = {'cells': [], 'input_sha256': {str(p): digest(p) for p in (model_path, table_path, baseline_path, mass_path)},
        'source_sha256': {'scripts/probe_velvia_bubble.py': digest(Path(__file__))},
        'environment': study_provenance.environment_fingerprint(), 'native_calls': 0, 'performance_calls': 0,
        'policy': '固定原3e5f；仅mask1/2，w_c=2*min三轴(f_c,ONE-f_c)，Q16；u64未舍入累加器混合到Q32后一次half-up。只查两max点与两cell612支撑，不做强度扫描/全域选择/拟合。',
        'scope': '局部必要可行性，不宣称全域mean/p99/max、原生兼容、速度或内存达标；C0边界归零来自代数，尚无完整面/实际邻接终验。'}
    for cell, peak in [(31725, [239, 252, 113]), (31726, [239, 252, 114])]:
        coords = [cell//32**2, (cell//32)%32, cell%32]
        codes = [np.flatnonzero(model.idx[a] == coords[a]).astype(np.uint8) for a in range(3)]
        points = np.array(np.meshgrid(*codes, indexing='ij')).reshape(3, -1).T
        keys = points.astype(np.int64)@np.array([65536, 256, 1], np.int64)
        old = accumulator(model, points, 0)
        old_rgb = ((old+io.ONE//2) >> io.Q).astype(np.uint8)
        np.testing.assert_array_equal(old_rgb, baseline[keys])
        f = np.stack([model.channel_frac[:, a, points[:, a]].T for a in range(3)], axis=2).astype(np.uint64)
        weights = 2*np.minimum(f, io.ONE-f).min(axis=2)
        common_weights = weights.min(axis=1)
        zero_mix = bubble(old, accumulator(model, points, 1), np.zeros_like(weights))
        np.testing.assert_array_equal(zero_mix, old_rgb)
        local_mass = mass[keys].astype(np.float64)/total_mass
        peak_id = int(np.flatnonzero(np.all(points == peak, axis=1))[0])
        row = {'cell': cell, 'coordinates': coords, 'points': len(points), 'baseline': hist_metrics(histogram(old_rgb, reference[keys])),
            'peak': {'rgb': peak, 'baseline': old_rgb[peak_id].tolist(), 'reference': reference[keys[peak_id]].tolist(),
                'fractions_by_output_axis': f[peak_id].tolist(), 'weights_by_output': weights[peak_id].tolist(),
                'common_weight_diagnostic': int(common_weights[peak_id])}, 'variants': {}}
        for mask in (1, 2):
            value = bubble(old, accumulator(model, points, mask), weights)
            difference = value.astype(np.int32)-reference[keys].astype(np.int32)
            square = np.sum(difference*difference, axis=1, dtype=np.int32)
            row['variants'][str(mask)] = {'metrics': hist_metrics(histogram(value, reference[keys])),
                'training_mean_contribution': float(local_mass@np.sqrt(square.astype(np.float64))),
                'peak_output': value[peak_id].tolist(), 'peak_squared': int(square[peak_id]),
                'integer_q32_python_vs_numpy_mismatches': 0}
        result['cells'].append(row)
    result['points_evaluated'] = sum(r['points'] for r in result['cells'])
    if result['points_evaluated'] != 612:
        raise AssertionError('shared-idx支撑不是冻结612色')
    result['both_original_max_points_can_strictly_improve'] = all(min(v['peak_squared'] for v in r['variants'].values()) < 1682 for r in result['cells'])
    save(args.output, result)
    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
