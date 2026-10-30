"""固定原3e5两cell/κ3的全域、照片与真实坐标边界验收；不选择新参数。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numba
import numpy as np
from PIL import Image
from lutlab import bubble_tetra as bt, io, study_provenance
from run_channel_tail_nodes import load_model, digest, save
from probe_velvia_bubble import accumulator, bubble
from verify_channel_coordinates import integer_oracle
from accept_channel_tail_nodes import histogram
from accept_channel_coordinates import hist_metrics, changes


def selected(model, rgb):
    cells = (model.idx[0, rgb[:, 0]].astype(np.int64)*32+model.idx[1, rgb[:, 1]])*32+model.idx[2, rgb[:, 2]]
    return np.isin(cells, bt.CELLS)


def mixed_oracle(model, rgb):
    """全部普通点重新用独立u64求值；修改点再用u64及Python int混合复核。"""
    value = integer_oracle(model, rgb)
    sel = selected(model, rgb)
    if np.any(sel):
        pts = rgb[sel]
        f = np.stack([model.channel_frac[:, a, pts[:, a]].T for a in range(3)], axis=2).astype(np.uint64)
        t = np.minimum(f, io.ONE-f).min(axis=2)
        weights = np.minimum(io.ONE, bt.KAPPA*t)
        value[sel] = bubble(accumulator(model, pts, 0), accumulator(model, pts, 1), weights)
    return value, int(sel.sum())


def explicit_acc(model, cells, frac):
    """共享面的独立uint64 mask0累加器；每输出使用自己的三轴fraction。"""
    base = cells.astype(np.int64)@np.array([model.m**2, model.m, 1], np.int64)
    result = np.empty((len(cells), 3), np.uint64)
    for c in range(3):
        f = frac[:, c].astype(np.int64)
        stride = np.tile(np.array([model.m**2, model.m, 1], np.int64), (len(cells), 1))
        order = np.argsort(-f, axis=1, kind='stable')
        f, stride = np.take_along_axis(f, order, axis=1), np.take_along_axis(stride, order, axis=1)
        weights = np.column_stack((io.ONE-f[:, 0], f[:, 0]-f[:, 1], f[:, 1]-f[:, 2], f[:, 2])).astype(np.uint64)
        ids = np.column_stack((base, base+stride[:, 0], base+stride[:, :2].sum(axis=1), base+stride.sum(axis=1)))
        result[:, c] = np.sum(weights*model.nodes.reshape(-1, 3)[ids, c].astype(np.uint64), axis=1, dtype=np.uint64)
    return result


def faces(model):
    rows = []
    uv = np.indices((256, 256)).reshape(2, -1).T.astype(np.uint8)
    for axis in range(3):
        other = [a for a in range(3) if a != axis]
        count = mismatches = changed_from_old = before_round_mismatches = 0
        for plane in range(31):
            cells = np.zeros((len(uv), 3), np.int64)
            frac = np.zeros((len(uv), 3, 3), np.int64)
            cells[:, axis] = plane; frac[:, :, axis] = io.ONE
            for n, a in enumerate(other):
                cells[:, a] = model.idx[a, uv[:, n]]
                frac[:, :, a] = model.channel_frac[:, a, uv[:, n]].T
            right_cells, right_frac = cells.copy(), frac.copy()
            right_cells[:, axis] += 1; right_frac[:, :, axis] = 0
            left_acc, right_acc = explicit_acc(model, cells, frac), explicit_acc(model, right_cells, right_frac)
            before_round_mismatches += int(np.count_nonzero(left_acc != right_acc))
            left = bt.explicit_faces(cells, frac, model.nodes.reshape(-1, 3), model.m)
            right = bt.explicit_faces(right_cells, right_frac, model.nodes.reshape(-1, 3), model.m)
            expected = ((left_acc+io.ONE//2) >> io.Q).astype(np.uint8)
            mismatches += int(np.count_nonzero(left != right))
            changed_from_old += int(np.count_nonzero(left != expected)+np.count_nonzero(right != expected))
            count += len(uv)
        rows.append({'axis': axis, 'planes': 31, 'true_per_output_fraction_cross_sections': count,
            'before_round_Q16_component_mismatches': before_round_mismatches,
            'left_right_component_mismatches': mismatches, 'bubble_vs_original_face_component_mismatches': changed_from_old})
    return {'axes': rows, 'algebra': '每输出任一轴fraction为0或65536时t=0，w=0，混合严格等于原mask0未舍入值；相邻cell的mask0面三角剖分相同。因此未舍入实函数C0；最后RGB8舍入本身仍为阶梯函数。',
        'scope': '全部31内部面×其他两轴实际256²编码，且每个输出独立真实Q16；不是仅把三个输出共用虚构fraction。代数证明覆盖截面以外的连续face点。',
        'pass': all(all(row[k] == 0 for k in ('before_round_Q16_component_mismatches', 'left_right_component_mismatches', 'bubble_vs_original_face_component_mismatches')) for row in rows)}


def adjacency(model, old, new, reference):
    cubes = {n: np.asarray(v).reshape(256, 256, 256, 3) for n, v in [('baseline', old), ('candidate', new), ('reference', reference)]}
    rows = []
    for axis in range(3):
        store = {}
        for scope in ('all_rgb8_neighbors', 'cross_shared_idx_neighbors'):
            store[scope] = {'jump': {n: np.zeros(3*255**2+1, np.int64) for n in cubes},
                'error_jump': {n: np.zeros(3*510**2+1, np.int64) for n in ('baseline', 'candidate')},
                'raw_squared_jump_changes': [0, 0, 0], 'error_squared_jump_changes': [0, 0, 0]}
        maximum_regression = {'raw': None, 'error': None}
        other = [a for a in range(3) if a != axis]
        for code in range(255):
            low = [slice(None)]*3; low[axis] = code
            high = [slice(None)]*3; high[axis] = code+1
            delta = {n: cube[tuple(high)].reshape(-1, 3).astype(np.int32)-cube[tuple(low)].reshape(-1, 3).astype(np.int32) for n, cube in cubes.items()}
            squares = {n: np.sum(v*v, axis=1, dtype=np.int32) for n, v in delta.items()}
            err_sq = {n: np.sum((delta[n]-delta['reference'])**2, axis=1, dtype=np.int32) for n in ('baseline', 'candidate')}
            scopes = ['all_rgb8_neighbors']
            if model.idx[axis, code] != model.idx[axis, code+1]:
                scopes.append('cross_shared_idx_neighbors')
            for scope in scopes:
                entry = store[scope]
                for n, square in squares.items():
                    entry['jump'][n] += np.bincount(square, minlength=len(entry['jump'][n]))
                for n, square in err_sq.items():
                    entry['error_jump'][n] += np.bincount(square, minlength=len(entry['error_jump'][n]))
                for kind, scores in [('raw', squares), ('error', err_sq)]:
                    diff = scores['candidate']-scores['baseline']
                    entry[kind+'_squared_jump_changes'] = [a+b for a, b in zip(entry[kind+'_squared_jump_changes'], [int((diff < 0).sum()), int((diff == 0).sum()), int((diff > 0).sum())])]
            for kind, scores in [('raw', squares), ('error', err_sq)]:
                diff = scores['candidate']-scores['baseline']; n = int(np.argmax(diff))
                if maximum_regression[kind] is None or diff[n] > maximum_regression[kind]['squared_increase']:
                    point = [0, 0, 0]; point[axis] = code; point[other[0]], point[other[1]] = n//256, n%256
                    maximum_regression[kind] = {'low_rgb8': point, 'squared_increase': int(diff[n]), 'baseline_squared': int(scores['baseline'][n]), 'candidate_squared': int(scores['candidate'][n])}
        rows.append({'axis': axis, 'scopes': {scope: {'jump': {n: hist_metrics(h) for n, h in item['jump'].items()},
            'approximation_error_jump': {n: hist_metrics(h) for n, h in item['error_jump'].items()},
            'raw_squared_jump_changes_better_equal_worse': item['raw_squared_jump_changes'],
            'error_squared_jump_changes_better_equal_worse': item['error_squared_jump_changes']} for scope, item in store.items()}, 'maximum_regression': maximum_regression})
    return {'axes': rows, 'scope': '全部3×255×256²=50,135,040对及跨shared-idx子集；记录C0以外的实际RGB8局部跳变代价，不用连续性证明替代。'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): raise ValueError('不覆盖冻结bubble终验')
    args.output.mkdir(parents=True)
    cache = args.cache_root.resolve()
    numba.set_num_threads(4)
    plan_path = ROOT/'experiments/velvia-bubble-accept-v1.json'
    plan = json.loads(plan_path.read_text(encoding='utf-8'))
    if plan['cells'] != list(bt.CELLS) or plan['masks'] != [1, 1] or plan['kappa'] != bt.KAPPA:
        raise ValueError('源码与冻结方案不符')
    paths = {'model': cache/'artifacts/velvia-channel-coordinates-v1/channel-coordinates.npz',
        'reference': cache/'artifacts/chain-error-cache/source-2ff0a4e385f9f9e49ca02f63/table.lut256',
        'baseline': cache/'artifacts/velvia-channel-coordinates-accept-v1/cube.rgb',
        'training_frequency': cache/'artifacts/cinema-axis-calibration-v1/photo-arrival-frequency.npy',
        'photo_manifest': cache/'assets/photos/manifest.json'}
    expected = ['3e5f8fd94e8dc9b97dbfea2823896b8dffb6e014b5e6056ab5c10b58a69af3d0', '6c4387352bd0845ce597f13dca32f2f808b39439d06ce78b4881922a4fc294b7',
        '945d4b906ae9aa184fdddd7f084da0105fa87b7e756f88ea700ca53f61ed37f0', '1eff7aab15715845bbc3efda68043a62a5c2dd9162f33717cee8bea5d36b756e',
        '10893812e0d3cecea7ba8b6bbf4700addd09927feed220149501def03c374f7c']
    actual = {n: digest(p) for n, p in paths.items()}
    if list(actual.values()) != expected: raise ValueError('输入SHA不符')
    source_names = ['scripts/accept_velvia_bubble.py', 'python/lutlab/bubble_tetra.py', 'experiments/velvia-bubble-accept-v1.json',
        'scripts/probe_velvia_bubble.py', 'scripts/verify_channel_coordinates.py']
    save(args.output/'run.json', {'input_sha256': actual, 'input_paths': {n: str(p) for n, p in paths.items()},
        'source_sha256': {n: digest(ROOT/n) for n in source_names}, 'environment': study_provenance.environment_fingerprint(),
        'numba_threads': 4, 'plan': plan, 'performance_calls': 0, 'native_calls': 0})
    model = load_model(paths['model'])
    reference = io.load_full(paths['reference'], mmap=True).reshape(-1, 3)
    old = np.memmap(paths['baseline'], np.uint8, 'r', shape=reference.shape)
    mass = np.load(paths['training_frequency'], mmap_mode='r'); mass_total = float(mass.sum(dtype=np.float64))
    new = np.memmap(args.output/'candidate.rgb', np.uint8, 'w+', shape=reference.shape)
    h, h0 = np.zeros(3*255**2+1, np.int64), np.zeros(3*255**2+1, np.int64)
    support = modified = 0
    training = np.zeros(2, np.float64)
    hasher = hashlib.sha256()
    for start in range(0, len(reference), 65536):
        keys = np.arange(start, start+65536, dtype=np.int64)
        rgb = np.column_stack((keys >> 16, (keys >> 8)&255, keys&255)).astype(np.uint8)
        oracle, selected_count = mixed_oracle(model, rgb); support += selected_count
        actual = bt.predict(model, rgb)
        np.testing.assert_array_equal(actual, oracle)
        sel = selected(model, rgb)
        np.testing.assert_array_equal(actual[~sel], old[start:start+len(rgb)][~sel])
        modified += int(np.count_nonzero(np.any(actual != old[start:start+len(rgb)], axis=1)))
        new[start:start+len(rgb)] = actual; hasher.update(actual.tobytes())
        h += histogram(actual, reference[start:start+len(rgb)]); h0 += histogram(old[start:start+len(rgb)], reference[start:start+len(rgb)])
        truth = reference[start:start+len(rgb)].astype(np.int32)
        for i, values in enumerate((old[start:start+len(rgb)], actual)):
            dist = np.sqrt(np.sum((values.astype(np.int32)-truth)**2, axis=1, dtype=np.int32))
            training[i] += float(np.dot(mass[start:start+len(rgb)], dist))
    new.flush()
    assert support == 612
    save(args.output/'cube.json', {'baseline': hist_metrics(h0), 'candidate': hist_metrics(h), 'training_mean': (training/mass_total).tolist(),
        'support': support, 'modified_RGB8_colors': modified, 'sha256': hasher.hexdigest(), 'full_numba_vs_u64_mismatches': 0,
        'selected_612_python_int_vs_uint64_mismatches': 0, 'outside_selected_cells_vs_baseline_mismatches': 0})
    print(json.dumps({'cube': hist_metrics(h), 'baseline': hist_metrics(h0), 'training_mean': (training/mass_total).tolist()}, ensure_ascii=False), flush=True)
    photo_h, photo_h0 = np.zeros_like(h), np.zeros_like(h)
    rows, old_rows = [], []
    manifest = json.loads(paths['photo_manifest'].read_text(encoding='utf-8'))
    for row in manifest['images']:
        path = cache/row['evaluation']['path']
        if digest(path) != row['evaluation']['sha256']: raise ValueError('照片SHA不符')
        with Image.open(path) as image: rgb = np.asarray(image).reshape(-1, 3).copy()
        keys = rgb.astype(np.int64)@np.array([65536, 256, 1], np.int64)
        predicted = bt.predict(model, rgb)
        np.testing.assert_array_equal(predicted, new[keys])
        ph, ph0 = histogram(predicted, reference[keys]), histogram(old[keys], reference[keys])
        photo_h += ph; photo_h0 += ph0
        rows.append({'image': row['id'], **hist_metrics(ph), 'prediction_sha256': hashlib.sha256(predicted.tobytes()).hexdigest()})
        old_rows.append({'image': row['id'], **hist_metrics(ph0)})
    result = {'cube': hist_metrics(h), 'baseline_cube': hist_metrics(h0), 'training_mean': (training/mass_total).tolist(),
        'photos': {**hist_metrics(photo_h), 'per_image': rows, 'changes': changes(old_rows, rows)},
        'baseline_photos': {**hist_metrics(photo_h0), 'per_image': old_rows}, 'sha256': hasher.hexdigest(),
        'support': support, 'modified_RGB8_colors': modified, 'full_numba_vs_u64_mismatches': 0,
        'selected_612_python_int_vs_uint64_mismatches': 0, 'all_100_fresh_numba_vs_stream_mismatches': 0,
        'native_calls': 0, 'performance_calls': 0, 'new_default': False}
    save(args.output/'results.json', result)
    face_result = faces(model); save(args.output/'faces.json', face_result)
    neighbor_result = adjacency(model, old, new, reference); save(args.output/'adjacency.json', neighbor_result)
    result['quality_gate_passed'] = bool(result['cube']['mean'] <= result['baseline_cube']['mean']+1e-12 and training[1] <= training[0]+1e-10
        and result['cube']['p99'] <= result['baseline_cube']['p99'] and result['cube']['max'] < result['baseline_cube']['max'] and face_result['pass'])
    result['limitations'] = '所有照片已见，只验不调；C0属于舍入前函数，RGB8映射本身不连续。新basis非stock SLUT/既有ChannelLut；未测native/速度/真实runtime容量，未切默认。'
    save(args.output/'results.json', result)
    print(json.dumps({'quality_gate_passed': result['quality_gate_passed'], 'faces': face_result, 'photos': {k: v for k, v in result['photos'].items() if k != 'per_image'}}, ensure_ascii=False), flush=True)


if __name__ == '__main__': main()
