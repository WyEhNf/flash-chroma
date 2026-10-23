"""冻结训练mean最优cell方向，独立全域/百图及精确面与RGB8邻近边界验收。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from PIL import Image
from lutlab import io, study_provenance
from run_channel_tail_nodes import load_model, digest, save
from study_velvia_body_diagonals import physical_oracle
from accept_channel_tail_nodes import histogram
from accept_channel_coordinates import hist_metrics, changes


def face_values(nodes, m, cells, frac, masks):
    """显式cell及分数的独立argsort/u64核，不从RGB8坐标表推导。"""
    steps = np.tile(np.array([m*m, m, 1], np.int64), (len(cells), 1))
    base = cells.astype(np.int64)@np.array([m*m, m, 1], np.int64)
    f = frac.astype(np.int64).copy()
    for axis in range(3):
        flip = (masks & (1 << axis)) != 0
        base[flip] += steps[flip, axis]
        steps[flip, axis] *= -1
        f[flip, axis] = io.ONE-f[flip, axis]
    order = np.argsort(-f, axis=1, kind='stable')
    f = np.take_along_axis(f, order, axis=1)
    steps = np.take_along_axis(steps, order, axis=1)
    weights = np.column_stack((io.ONE-f[:, 0], f[:, 0]-f[:, 1], f[:, 1]-f[:, 2], f[:, 2])).astype(np.uint64)
    ids = np.column_stack((base, base+steps[:, 0], base+steps[:, :2].sum(axis=1), base+steps.sum(axis=1)))
    acc = np.sum(weights[:, :, None]*nodes.reshape(-1, 3)[ids].astype(np.uint64), axis=1, dtype=np.uint64)
    return ((acc+io.ONE//2) >> io.Q).astype(np.uint8)


def exact_faces(model, choices):
    width = model.m-1
    faces = []
    for axis in range(3):
        shape = [width]*3; shape[axis] -= 1
        cells = np.indices(shape).reshape(3, -1).T
        other = [a for a in range(3) if a != axis]
        left_ids = cells@np.array([width**2, width, 1])
        right_cells = cells.copy(); right_cells[:, axis] += 1
        right_ids = right_cells@np.array([width**2, width, 1])
        any_seam = np.zeros(len(cells), bool)
        hist = np.zeros(3*255**2+1, np.int64)
        maximum_sample = None
        for u in (io.ONE//4, io.ONE//2, 3*io.ONE//4):
            for v in (io.ONE//4, io.ONE//2, 3*io.ONE//4):
                f = np.zeros(cells.shape, np.int64); f[:, axis] = io.ONE
                f[:, other[0]], f[:, other[1]] = u, v
                rf = f.copy(); rf[:, axis] = 0
                zeros = np.zeros(len(cells), np.uint8)
                np.testing.assert_array_equal(face_values(model.nodes, model.m, cells, f, zeros),
                    face_values(model.nodes, model.m, right_cells, rf, zeros))
                left = face_values(model.nodes, model.m, cells, f, choices[left_ids])
                right = face_values(model.nodes, model.m, right_cells, rf, choices[right_ids])
                h = histogram(left, right); hist += h
                changed = np.any(left != right, axis=1); any_seam |= changed
                delta = left.astype(np.int32)-right.astype(np.int32)
                squared = np.sum(delta*delta, axis=1, dtype=np.int32)
                n = int(np.argmax(squared))
                if maximum_sample is None or squared[n] > maximum_sample['squared_jump']:
                    maximum_sample = {'left_cell': cells[n].tolist(), 'right_cell': right_cells[n].tolist(),
                        'left_mask': int(choices[left_ids[n]]), 'right_mask': int(choices[right_ids[n]]),
                        'face_fractions': f[n].tolist(), 'left_rgb8': left[n].tolist(), 'right_rgb8': right[n].tolist(),
                        'squared_jump': int(squared[n])}
        faces.append({'axis': axis, 'faces': len(cells), 'differing_mask_faces': int(np.count_nonzero(choices[left_ids] != choices[right_ids])),
            'faces_with_sampled_discontinuity': int(any_seam.sum()), 'sampled_jump': hist_metrics(hist),
            'baseline_all_faces_exact_mismatches': 0, 'maximum_sample': maximum_sample})
    return faces


def rgb8_boundaries(model, baseline, output, reference):
    cubes = {name: np.asarray(value).reshape(256, 256, 256, 3) for name, value in [('baseline', baseline), ('candidate', output), ('reference', reference)]}
    result = []
    for axis in range(3):
        codes = np.flatnonzero(np.diff(model.idx[axis].astype(np.int64)))
        jump = {name: np.zeros(3*255**2+1, np.int64) for name in cubes}
        error_jump = {name: np.zeros(3*510**2+1, np.int64) for name in ('baseline', 'candidate')}
        for code in codes:
            low = [slice(None)]*3; low[axis] = int(code)
            high = [slice(None)]*3; high[axis] = int(code)+1
            values = {name: (cube[tuple(low)].reshape(-1, 3).astype(np.int32), cube[tuple(high)].reshape(-1, 3).astype(np.int32)) for name, cube in cubes.items()}
            for name, (a, b) in values.items():
                jump[name] += histogram(a, b)
                if name != 'reference':
                    refa, refb = values['reference']
                    delta = (b-refb)-(a-refa)
                    square = np.sum(delta*delta, axis=1, dtype=np.int32)
                    error_jump[name] += np.bincount(square, minlength=len(error_jump[name]))
        result.append({'axis': axis, 'crossing_codes': codes.tolist(), 'jump': {n: hist_metrics(h) for n, h in jump.items()},
            'approximation_error_jump': {n: hist_metrics(h) for n, h in error_jump.items()}})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖冻结cell终验')
    args.output.mkdir(parents=True)
    cache = args.cache_root.resolve()
    choice_path = ROOT/'artifacts/velvia-cell-feasibility-v1/cap1522-min-training_frequency_mean-choices.npy'
    choices = np.load(choice_path)
    if choices.shape != (32768,) or choices.dtype != np.uint8 or not np.all(np.isin(choices, [0, 1, 2, 4])):
        raise ValueError('只接受冻结的cap1522训练mean最优单项')
    choices.tofile(args.output/'cell-orientation.bin')
    model_path = cache/'artifacts/velvia-channel-coordinates-v1/channel-coordinates.npz'
    if digest(model_path) != '3e5f8fd94e8dc9b97dbfea2823896b8dffb6e014b5e6056ab5c10b58a69af3d0':
        raise ValueError('必须保持3e5f节点与Q16轴')
    model = load_model(model_path)
    table_path = cache/'artifacts/chain-error-cache/source-2ff0a4e385f9f9e49ca02f63/table.lut256'
    reference = io.load_full(table_path, mmap=True).reshape(-1, 3)
    source = ROOT/'artifacts/velvia-body-diagonals-v1'
    streams = {k: np.memmap(source/f'mask{k}.rgb', np.uint8, 'r', shape=reference.shape) for k in (0, 1, 2, 4)}
    old = streams[0]
    save(args.output/'run.json', {'model_sha256': digest(model_path), 'reference_sha256': digest(table_path),
        'choice_source_sha256': digest(choice_path), 'cell_orientation_sha256': digest(args.output/'cell-orientation.bin'),
        'source_sha256': {Path(__file__).relative_to(ROOT).as_posix(): digest(Path(__file__))},
        'environment': study_provenance.environment_fingerprint(),
        'policy': '唯一cap1522训练mean最优单项，不根据100图在mean/RMS两项中选择或继续调参。byte/cell实际32768B；原节点/坐标保持。',
        'scope': '新插值表示，既有ChannelLut/native不支持；全域下界限于当前四固定方向与固定模型。'})
    output = np.memmap(args.output/'candidate.rgb', np.uint8, 'w+', shape=reference.shape)
    hist, old_hist = np.zeros(3*255**2+1, np.int64), np.zeros(3*255**2+1, np.int64)
    hasher = hashlib.sha256()
    for start in range(0, len(reference), 65536):
        keys = np.arange(start, start+65536, dtype=np.int64)
        rgb = np.column_stack((keys >> 16, (keys >> 8)&255, keys&255)).astype(np.uint8)
        cells = (model.idx[0, rgb[:, 0]].astype(np.int64)*32+model.idx[1, rgb[:, 1]])*32+model.idx[2, rgb[:, 2]]
        value = np.empty(rgb.shape, np.uint8)
        for mask in (0, 1, 2, 4):
            select = choices[cells] == mask
            value[select] = physical_oracle(model, rgb[select], mask)
            np.testing.assert_array_equal(value[select], streams[mask][start:start+len(keys)][select])
        output[start:start+len(keys)] = value
        hist += histogram(value, reference[start:start+len(keys)])
        old_hist += histogram(old[start:start+len(keys)], reference[start:start+len(keys)])
        hasher.update(value.tobytes())
    output.flush()
    rows, old_rows = [], []
    photo_hist, old_photo_hist = np.zeros_like(hist), np.zeros_like(hist)
    manifest = json.loads((cache/'assets/photos/manifest.json').read_text(encoding='utf-8'))
    for row in manifest['images']:
        path = cache/row['evaluation']['path']
        if digest(path) != row['evaluation']['sha256']:
            raise ValueError('照片SHA不符')
        with Image.open(path) as image:
            rgb = np.asarray(image).reshape(-1, 3)
        keys = rgb.astype(np.int64)@np.array([65536, 256, 1], np.int64)
        h, h0 = histogram(output[keys], reference[keys]), histogram(old[keys], reference[keys])
        photo_hist += h; old_photo_hist += h0
        rows.append({'image': row['id'], **hist_metrics(h), 'prediction_sha256': hashlib.sha256(output[keys].tobytes()).hexdigest()})
        old_rows.append({'image': row['id'], **hist_metrics(h0)})
    result = {'baseline_cube': hist_metrics(old_hist), 'cube': hist_metrics(hist),
        'baseline_photos': {**hist_metrics(old_photo_hist), 'per_image': old_rows},
        'photos': {**hist_metrics(photo_hist), 'per_image': rows, 'changes': changes(old_rows, rows)},
        'sha256': hasher.hexdigest(), 'full_independent_recompute_vs_reparameterized_stream_mismatches': 0,
        'orientation_bytes': int(choices.nbytes), 'native_calls': 0, 'performance_calls': 0, 'new_default': False}
    result['quality_gate_passed'] = all(result[g][k] <= result['baseline_'+g][k]+1e-12 for g in ('cube', 'photos') for k in ('mean', 'rms', 'p99', 'max', 'cvar_1pct'))
    save(args.output/'results.json', result)
    print(json.dumps({k: v for k, v in result.items() if k not in ('photos', 'baseline_photos')}, ensure_ascii=False), flush=True)
    save(args.output/'exact-faces.json', exact_faces(model, choices))
    save(args.output/'rgb8-boundaries.json', rgb8_boundaries(model, old, output, reference))
    print(json.dumps({'faces_and_rgb8_boundaries_complete': True, 'photos': {k: v for k, v in result['photos'].items() if k != 'per_image'}}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
