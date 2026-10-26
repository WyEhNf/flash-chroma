"""从两个训练max点的精确整数舍入区间推导最小κ，再仅验证612支撑一次。"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import io, study_provenance
from run_channel_tail_nodes import load_model, digest, save
from probe_velvia_bubble import accumulator, bubble
from accept_channel_tail_nodes import histogram
from accept_channel_coordinates import hist_metrics

INF = 10**18


def ceil_div(a, b):
    return -((-a)//b)


def weight_interval(old, alternative, output):
    scale = io.ONE**2
    lower = output*scale-scale//2-io.ONE*int(old)
    upper = (output+1)*scale-scale//2-1-io.ONE*int(old)
    delta = int(alternative)-int(old)
    if delta == 0:
        return (0, io.ONE) if lower <= 0 <= upper else None
    if delta < 0:
        lower, upper, delta = -upper, -lower, -delta
    lo, hi = max(0, ceil_div(lower, delta)), min(io.ONE, upper//delta)
    return (lo, hi) if lo <= hi else None


def slope_interval(interval, distance):
    lo, hi = interval
    if distance == 0:
        return (1, INF) if lo == 0 else None
    lower = max(1, ceil_div(lo, distance))
    upper = INF if hi == io.ONE else hi//distance
    return (lower, upper) if lower <= upper else None


def interval_contract():
    fixtures = [(0, 255*io.ONE), (255*io.ONE, 0), (123*io.ONE+9, 123*io.ONE+9),
        (38*io.ONE+12345, 43*io.ONE+5432), (100*io.ONE+io.ONE//2, 90*io.ONE+7)]
    weights = np.arange(io.ONE+1, dtype=np.uint64)
    tested = 0
    for old, alternative in fixtures:
        outputs = (((io.ONE-weights)*np.uint64(old)+weights*np.uint64(alternative)+np.uint64(io.ONE**2//2)) >> (2*io.Q)).astype(np.int32)
        for output in np.unique(outputs):
            ids = np.flatnonzero(outputs == output)
            expected = (int(ids[0]), int(ids[-1]))
            if weight_interval(old, alternative, int(output)) != expected or len(ids) != expected[1]-expected[0]+1:
                raise AssertionError('精确half-up权重区间合同失败')
            tested += 1
    for distance in (0, 1, 720, io.ONE//2):
        for interval in ((0, 0), (0, 12345), (30000, 60000), (60000, io.ONE), (io.ONE, io.ONE)):
            mapped = slope_interval(interval, distance)
            candidates = {1, 2, 65537}
            if distance:
                candidates.add(ceil_div(io.ONE, distance))
            if mapped:
                candidates |= {max(1, mapped[0]-1), mapped[0], mapped[0]+1}
                if mapped[1] != INF:
                    candidates |= {max(1, mapped[1]-1), mapped[1], mapped[1]+1}
            for k in candidates:
                weight = min(io.ONE, k*distance)
                actual = interval[0] <= weight <= interval[1]
                expected = mapped is not None and mapped[0] <= k <= mapped[1]
                if actual != expected:
                    raise AssertionError('饱和斜率区间合同失败')
    return {'half_up_fixtures': len(fixtures), 'weights_per_fixture': io.ONE+1,
        'output_weight_intervals_checked': tested, 'saturation_interval_checks_pass': True, 'mismatches': 0,
        'scope': '合成整数区间合同，不是实际κ参数扫描。'}


def fractions(model, points):
    return np.stack([model.channel_frac[:, a, points[:, a]].T for a in range(3)], axis=2).astype(np.uint64)


def regions(old, alternative, target, distances, mask):
    ends = [[(int(a)+io.ONE//2)//io.ONE, (int(b)+io.ONE//2)//io.ONE] for a, b in zip(old, alternative)]
    result = []
    for output in itertools.product(*(range(min(v), max(v)+1) for v in ends)):
        if sum((output[c]-int(target[c]))**2 for c in range(3)) > 1681:
            continue
        weight_boxes, slopes = [], []
        for c in range(3):
            box = weight_interval(old[c], alternative[c], output[c])
            slope = None if box is None else slope_interval(box, int(distances[c]))
            if slope is None:
                break
            weight_boxes.append(box); slopes.append(slope)
        if len(slopes) != 3:
            continue
        lower, upper = max(v[0] for v in slopes), min(v[1] for v in slopes)
        if lower <= upper:
            result.append({'mask': mask, 'output': list(output), 'weight_intervals': weight_boxes,
                'kappa_interval': [lower, None if upper == INF else upper]})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖解析κ独立阶段')
    args.output.mkdir(parents=True)
    cache = args.cache_root.resolve()
    model_path = cache/'artifacts/velvia-channel-coordinates-v1/channel-coordinates.npz'
    table_path = cache/'artifacts/chain-error-cache/source-2ff0a4e385f9f9e49ca02f63/table.lut256'
    baseline_path = cache/'artifacts/velvia-channel-coordinates-accept-v1/cube.rgb'
    mass_path = cache/'artifacts/cinema-axis-calibration-v1/photo-arrival-frequency.npy'
    old_probe = json.loads((ROOT/'artifacts/velvia-bubble-probe-v1.json').read_text(encoding='utf-8'))
    for path in (model_path, table_path, baseline_path, mass_path):
        if digest(path) != old_probe['input_sha256'][str(path)]:
            raise ValueError('不得改变κ=2阶段的冻结输入')
    save(args.output/'run.json', {'input_sha256': {str(p): digest(p) for p in (model_path, table_path, baseline_path, mass_path)},
        'source_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in [Path(__file__), ROOT/'scripts/probe_velvia_bubble.py']},
        'environment': study_provenance.environment_fingerprint(),
        'policy': '固定原3e5f，仅mask1/2；不扫κ。按两训练max点的整数RGB可行输出和精确Q32舍入区间，推导共同最小正整数κ。先落盘阈值和方向见证，再仅此κ评估612支撑一次，不扩展全域/拟合。',
        'scope': 'κ来自训练极值，不是盲测；两个点/612支撑的可行性不等于完整域或原生/速度结论。'})
    save(args.output/'interval-contract.json', interval_contract())
    model = load_model(model_path)
    reference = io.load_full(table_path, mmap=True).reshape(-1, 3)
    baseline = np.memmap(baseline_path, np.uint8, 'r', shape=reference.shape)
    peaks = np.array([[239, 252, 113], [239, 252, 114]], np.uint8)
    peak_keys = peaks.astype(np.int64)@np.array([65536, 256, 1], np.int64)
    old_acc = accumulator(model, peaks, 0)
    f = fractions(model, peaks)
    distances = np.minimum(f, io.ONE-f).min(axis=2)
    peak_reports, alternatives = [], {mask: accumulator(model, peaks, mask) for mask in (1, 2)}
    for point in range(2):
        options = []
        for mask in (1, 2):
            options.extend(regions(old_acc[point], alternatives[mask][point], reference[peak_keys[point]], distances[point], mask))
        peak_reports.append({'rgb': peaks[point].tolist(), 'reference': reference[peak_keys[point]].tolist(),
            'old_acc_q16': old_acc[point].tolist(), 'alternative_acc_q16': {str(mask): alternatives[mask][point].tolist() for mask in (1, 2)},
            'distance_to_nearest_face_by_output': distances[point].tolist(), 'kappa2_weights': (2*distances[point]).tolist(),
            'feasible_integer_output_regions': options})
    candidates = []
    for a, b in itertools.product(peak_reports[0]['feasible_integer_output_regions'], peak_reports[1]['feasible_integer_output_regions']):
        lower = max(a['kappa_interval'][0], b['kappa_interval'][0])
        upper = min(INF if a['kappa_interval'][1] is None else a['kappa_interval'][1], INF if b['kappa_interval'][1] is None else b['kappa_interval'][1])
        if lower <= upper:
            candidates.append((lower, a['mask'], b['mask'], a['output'], b['output']))
    threshold = {'peaks': peak_reports, 'common_integer_kappa_exists': bool(candidates), 'scope': '只按两个训练max点推导，不使用后续612结果改参数。'}
    if not candidates:
        save(args.output/'derived-threshold.json', threshold)
        print(json.dumps({'common_integer_kappa_exists': False}), flush=True)
        return
    chosen = min(candidates)
    kappa, masks = chosen[0], chosen[1:3]
    threshold.update(selected_kappa=kappa, selected_masks=list(masks), selected_peak_outputs=chosen[3:])
    save(args.output/'derived-threshold.json', threshold)
    print(json.dumps({'selected_kappa_before_612_validation': kappa, 'selected_masks': masks, 'selected_peak_outputs': chosen[3:]}), flush=True)
    mass = np.load(mass_path, mmap_mode='r'); total_mass = float(mass.sum(dtype=np.float64))
    result = {'selected_kappa': kappa, 'cells': [], 'native_calls': 0, 'performance_calls': 0, 'new_default': False}
    combined_old = np.zeros(3*255**2+1, np.int64); combined_new = np.zeros_like(combined_old)
    training_delta = 0.
    for i, cell in enumerate((31725, 31726)):
        coords = [cell//32**2, (cell//32)%32, cell%32]
        codes = [np.flatnonzero(model.idx[a] == coords[a]).astype(np.uint8) for a in range(3)]
        points = np.array(np.meshgrid(*codes, indexing='ij')).reshape(3, -1).T
        keys = points.astype(np.int64)@np.array([65536, 256, 1], np.int64)
        original = accumulator(model, points, 0)
        original_rgb = ((original+io.ONE//2) >> io.Q).astype(np.uint8)
        np.testing.assert_array_equal(original_rgb, baseline[keys])
        fraction = fractions(model, points)
        weights = np.minimum(io.ONE, kappa*np.minimum(fraction, io.ONE-fraction).min(axis=2))
        local_mass = mass[keys].astype(np.float64)/total_mass
        old_hist = histogram(original_rgb, reference[keys]); combined_old += old_hist
        old_delta = original_rgb.astype(np.int32)-reference[keys].astype(np.int32)
        old_dist = np.sqrt(np.sum(old_delta*old_delta, axis=1, dtype=np.int32).astype(np.float64))
        row = {'cell': cell, 'points': len(points), 'baseline': hist_metrics(old_hist), 'selected_mask_before_612': int(masks[i]), 'variants': {}}
        for mask in (1, 2):
            value = bubble(original, accumulator(model, points, mask), weights)
            hist = histogram(value, reference[keys])
            row['variants'][str(mask)] = {'metrics': hist_metrics(hist), 'q32_numpy_vs_python_mismatches': 0}
            if mask == masks[i]:
                combined_new += hist
                delta = value.astype(np.int32)-reference[keys].astype(np.int32)
                distances1 = np.sqrt(np.sum(delta*delta, axis=1, dtype=np.int32).astype(np.float64))
                training_delta += float(local_mass@(distances1-old_dist))
        result['cells'].append(row)
    result.update(combined_baseline=hist_metrics(combined_old), combined_selected=hist_metrics(combined_new),
        original_60_frequency_mean_delta_from_612=training_delta,
        local_612_mean_and_max_pass=bool(hist_metrics(combined_new)['mean'] <= hist_metrics(combined_old)['mean'] and np.flatnonzero(combined_new)[-1] <= 1681),
        p99_above40_count_delta=int(combined_new[41:].sum()-combined_old[41:].sum()),
        scope='只验证此κ一次及612完整支撑，没有完整域/照片/面邻接/native/performance，不自动扩展。')
    save(args.output/'results.json', result)
    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
