"""两个冻结节点候选的完整RGB8独立四级oracle、真实原生及历史百图验收。"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
sys.path.insert(0, str(ROOT/'experiments/channel-runtime'))
import numba
import numpy as np
from PIL import Image
from lutlab import channel_coordinates as cc, io
from channel_native import Library
from run_channel_tail_nodes import load_model, digest, save
from verify_channel_coordinates import integer_oracle
from accept_channel_coordinates import hist_metrics, changes


def histogram(prediction, reference):
    delta = prediction.astype(np.int32)-reference.astype(np.int32)
    square = np.sum(delta*delta, axis=1, dtype=np.int32)
    return np.bincount(square, minlength=3*255**2+1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-root', type=Path, required=True)
    parser.add_argument('--models', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--modes', nargs='+', default=['severe_first', 'p99_first'])
    parser.add_argument('--case', choices=('cinema', 'cinema_shared', 'velvia'), default='cinema')
    parser.add_argument('--baseline-cube', type=Path)
    parser.add_argument('--library', type=Path)
    parser.add_argument('--library-sha256')
    parser.add_argument('--suffix-stage4', type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖终验')
    args.output.mkdir(parents=True)
    cache = args.cache_root.resolve()
    numba.set_num_threads(4)
    plan = json.loads((ROOT/'experiments/cinema-current-anchor-v1.json').read_text(encoding='utf-8'))
    if args.case == 'velvia':
        velvia = json.loads((ROOT/'experiments/velvia-channel-coordinates-accept-v1.json').read_text(encoding='utf-8'))
        plan = {'suffix_models': [], 'tables': [velvia['inputs']['table']]}
    suffix_paths = [cache/p['path'] for p in plan['suffix_models']]
    for p, spec in zip(suffix_paths, plan['suffix_models']):
        if digest(p) != spec['sha256']:
            raise ValueError('后三模型不同')
    if args.suffix_stage4 is not None:
        if len(suffix_paths) != 3:
            raise ValueError('末级替换只适用四级链')
        suffix_paths[2] = args.suffix_stage4.resolve()
    suffix_models = [cc.from_sparse(io.load_sparse(p, competition=True)) for p in suffix_paths]
    tables = [io.load_full(cache/spec['path'], mmap=True).reshape(-1, 3) for spec in plan['tables']]
    for spec in plan['tables']:
        if digest(cache/spec['path']) != spec['sha256']:
            raise ValueError('独立四原表不同')
    library = cache/'artifacts/channel-native-runtime-v3/jshc_channel_packed.dll'
    expected_library_sha = '7ceb30d7913a8cf032e1828c25c3fe062082be8e9d531d105282ba8d1794b072'
    if args.library is not None:
        if args.library_sha256 is None:
            raise ValueError('新后端必须冻结SHA')
        library, expected_library_sha = args.library.resolve(), args.library_sha256
    toolchain_dir = os.add_dll_directory('E:/mingw64/bin') if Path('E:/mingw64/bin').is_dir() else None
    dll_dir = os.add_dll_directory(str(library.parent))
    lib = Library(library, expected_library_sha)
    reference = tables[0] if args.case == 'velvia' else np.load(cache/'artifacts/cinema-axis-calibration-v1/envelope-reference.npy', mmap_mode='r')
    baseline_path = cache/'artifacts/cinema-current-anchor-accept-v1/cube.rgb'
    if args.case == 'cinema_shared':
        baseline_path = cache/'artifacts/cinema-axis-calibration-v1/stage1_sweep012/cube.rgb'
    if args.case == 'velvia':
        baseline_path = cache/'artifacts/velvia-channel-coordinates-accept-v1/cube.rgb'
    if args.baseline_cube is not None:
        baseline_path = args.baseline_cube.resolve()
    baseline = np.memmap(baseline_path, np.uint8, 'r', shape=(256**3, 3))
    manifest = json.loads((cache/'assets/photos/manifest.json').read_text(encoding='utf-8'))
    partition = json.loads((cache/'artifacts/full-photo-v1/photo-partition.json').read_text(encoding='utf-8'))
    old_hist = np.zeros(3*255**2+1, np.int64)
    for start in range(0, len(baseline), 1 << 18):
        old_hist += histogram(baseline[start:start+(1 << 18)], reference[start:start+(1 << 18)])
    results = {'case': args.case, 'baseline': hist_metrics(old_hist), 'baseline_stream_sha256': digest(baseline_path),
               'source_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in [Path(__file__), ROOT/'scripts/verify_channel_coordinates.py']},
               'variants': {}, 'library_sha256': digest(library),
               'partition': partition, 'numba_threads': 4, 'native_threads': [1, 4], 'native_capabilities': lib.capabilities}
    for mode in args.modes:
        folder = args.models/mode
        model = load_model(folder/'model.npz')
        output = np.memmap(args.output/(mode+'.rgb'), np.uint8, 'w+', shape=(256**3, 3))
        hist, own_hist = np.zeros_like(old_hist), np.zeros_like(old_hist)
        hashes = {n: hashlib.sha256() for n in ('oracle', 'scalar', 'avx2', 'reference')}
        sidecar = folder/'channel-frac.bin'
        with lib.chain([folder/'candidate-base.slut', *suffix_paths], [sidecar if sidecar.exists() else None, *[None for _ in suffix_paths]]) as native:
            for start in range(0, 256**3, 65536):
                keys = np.arange(start, start+65536, dtype=np.int64)
                rgb = np.column_stack((keys >> 16, (keys >> 8)&255, keys&255)).astype(np.uint8)
                predicted = integer_oracle(model, rgb)
                hist1 = histogram(predicted, tables[0][keys]); own_hist += hist1
                for suffix in suffix_models:
                    predicted = integer_oracle(suffix, predicted)
                truth = tables[0][keys]
                for table in tables[1:]:
                    truth = table[truth.astype(np.int64)@np.array([65536, 256, 1], np.int64)]
                np.testing.assert_array_equal(truth, reference[start:start+65536])
                for name, kernel, threads in (('scalar', 'scalar', 1), ('avx2', 'avx2', 4)):
                    actual = native.apply(rgb.copy(), kernel=kernel, threads=threads)
                    np.testing.assert_array_equal(actual, predicted)
                    hashes[name].update(actual.tobytes())
                hashes['oracle'].update(predicted.tobytes()); hashes['reference'].update(truth.tobytes())
                output[start:start+65536] = predicted
                hist += histogram(predicted, truth)
            output.flush()
            photo_rows, photo_hist = [], np.zeros_like(hist)
            old_photo_rows, old_photo_hist = [], np.zeros_like(hist)
            for row in manifest['images']:
                p = cache/row['evaluation']['path']
                if digest(p) != row['evaluation']['sha256']:
                    raise ValueError('照片不同')
                with Image.open(p) as image:
                    rgb = np.asarray(image).reshape(-1, 3).copy()
                keys = rgb.astype(np.int64)@np.array([65536, 256, 1], np.int64)
                actual = native.apply(rgb, kernel='avx2', threads=4)
                np.testing.assert_array_equal(actual, output[keys])
                h = histogram(actual, reference[keys]); photo_hist += h
                old_h = histogram(baseline[keys], reference[keys]); old_photo_hist += old_h
                old_photo_rows.append({'image': row['id'], **hist_metrics(old_h)})
                photo_rows.append({'image': row['id'], **hist_metrics(h), 'prediction_sha256': hashlib.sha256(actual.tobytes()).hexdigest()})
            memory = native.model_bytes
        photos = hist_metrics(photo_hist)
        photos.update(worst_image_p99=max(r['p99'] for r in photo_rows), per_image=photo_rows)
        photos['changes'] = changes(old_photo_rows, photo_rows)
        baseline_photos = hist_metrics(old_photo_hist)
        results['baseline_photos'] = baseline_photos
        results['baseline_photos']['per_image'] = old_photo_rows
        cube = hist_metrics(hist)
        passed = all(cube[k] <= results['baseline'][k]+1e-12 and photos[k] <= baseline_photos[k]+1e-12
                     for k in ('mean', 'rms', 'p99', 'max', 'cvar_1pct'))
        results['variants'][mode] = {'cube': cube, 'photos': photos, 'passed_aggregate': passed,
            'sha256': {n: h.hexdigest() for n, h in hashes.items()}, 'first_stage_accuracy': hist_metrics(own_hist),
            'model_sha256': digest(folder/'model.npz'), 'model_accounting_bytes': memory,
            'full_native_byte_mismatches': 0, 'photo_native_byte_mismatches': 0,
            'scope': '全域用于目标训练；历史100图是回顾终验，不是盲测；无计时，未实测新硬件。'}
        save(args.output/'results.json', results)
        print(json.dumps({'mode': mode, 'cube': cube, 'photos': {k: v for k, v in photos.items() if k != 'per_image'},
                          'passed_aggregate': passed}, ensure_ascii=False), flush=True)
    dll_dir.close()
    if toolchain_dir is not None:
        toolchain_dir.close()


if __name__ == '__main__':
    main()
