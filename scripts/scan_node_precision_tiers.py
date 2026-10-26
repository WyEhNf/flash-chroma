"""固定a399模型的节点/坐标降位宽筛查；重建RGB8不代表压缩运行时已实现。"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'python'))
sys.path.insert(0, str(ROOT / 'scripts'))
import numba
import numpy as np
from lutlab import channel_coordinates as cc, io, study_provenance
from accept_channel_coordinates import hist_metrics


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def histogram(output, target):
    d = output.astype(np.int32) - target.astype(np.int32)
    return np.bincount(np.sum(d*d, axis=1), minlength=3*255**2+1).astype(np.int64)


def quantize(model, node_bits, frac_bits):
    """节点以端点保真的等间隔整数码重建；坐标保持Q16端点与单调性。"""
    levels = (1 << node_bits) - 1
    codes = (model.nodes.astype(np.uint32)*levels + 127)//255
    nodes = ((codes*255 + levels//2)//levels).astype(np.uint8)
    step = 1 << (16-frac_bits)
    frac = np.minimum(65536, ((model.channel_frac + step//2)//step)*step).astype(np.uint32)
    result = cc.ChannelLut(model.grid.copy(), nodes, model.idx.copy(), frac)
    cc.validate(result)
    return result


def predict(models, points):
    result = points
    for model in models:
        result = cc.predict(model, result)
    return result


def retention(old, new):
    ratios = {k: (1. if new[k] == 0 else old[k]/new[k]) for k in ('mean', 'p99', 'max')}
    return {'components': ratios, 'minimum': min(ratios.values()),
            'eligible_accuracy_tiers': [t for t in (1., .9, .8, .7, .6, .5) if min(ratios.values()) + 1e-12 >= t]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--full', action='store_true')
    parser.add_argument('--candidates', nargs='*')
    parser.add_argument('--native-library', type=Path)
    parser.add_argument('--native-sha256')
    args = parser.parse_args()
    source = args.inputs_root.resolve()
    output = args.output.resolve()
    if output.exists():
        raise ValueError('不覆盖既有位宽实验')
    plan_path = source/'experiments/cinema-current-anchor-accept-v1.json'
    plan = json.loads(plan_path.read_text(encoding='utf-8'))
    specs = [plan['inputs']['candidate'], plan['inputs']['reference'], plan['inputs']['prior_full']] if 'prior_full' in plan['inputs'] else [plan['inputs']['candidate'], plan['inputs']['reference']]
    specs += plan['suffix_models']
    for spec in specs:
        if digest(source/spec['path']) != spec['sha256']:
            raise ValueError('固定模型或完整参考SHA不符：' + spec['path'])
    first_data = np.load(source/plan['inputs']['candidate']['path'])
    first = cc.ChannelLut(first_data['grid'], first_data['nodes'], first_data['shared_idx'], first_data['channel_frac'])
    models = [first] + [cc.from_sparse(io.load_sparse(source/s['path'], competition=True)) for s in plan['suffix_models']]
    for model in models:
        cc.validate(model)
    reference = np.load(source/plan['inputs']['reference']['path'], mmap_mode='r')
    baseline_path = source/'artifacts/cinema-current-anchor-accept-v1/cube.rgb'
    if digest(baseline_path) != '3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22':
        raise ValueError('a399完整输出SHA不符')
    baseline = np.memmap(baseline_path, dtype=np.uint8, mode='r', shape=(256**3, 3))
    configs = [('baseline', 8, 16, False)]
    for bits in (7, 6, 5, 4):
        configs.extend([(f'nodes{bits}_first', bits, 16, True), (f'nodes{bits}_all', bits, 16, False)])
    configs += [(f'frac{bits}_all', 8, bits, False) for bits in (12, 10, 8, 6)]
    configs += [('nodes7_frac10_all', 7, 10, False)]
    if args.candidates:
        requested = set(args.candidates) | {'baseline'}
        if requested - {c[0] for c in configs}:
            raise ValueError('未知候选')
        configs = [c for c in configs if c[0] in requested]
    numba.set_num_threads(4)
    library = None
    if args.native_library:
        if not args.native_sha256:
            raise ValueError('原生产物必须绑定事先确定的SHA')
        if os.name == 'nt':
            dll_directory = os.add_dll_directory('E:/mingw64/bin')
        sys.path.insert(0, str(ROOT/'experiments/channel-runtime'))
        from channel_native import Library
        library = Library(args.native_library, args.native_sha256)
    output.mkdir(parents=True)
    identity = {'purpose': __doc__, 'source_commit': '16ae431030a5c734a1485089c8b58d15b21902f6',
                'source_sha256': {str(Path(__file__).relative_to(ROOT)): digest(__file__),
                                  'python/lutlab/channel_coordinates.py': digest(ROOT/'python/lutlab/channel_coordinates.py')},
                'environment': study_provenance.environment_fingerprint(), 'threads': 4,
                'inputs': specs, 'baseline_output_sha256': digest(baseline_path),
                'scope': '完整RGB色域' if args.full else '固定seed的262144个RGB颜色，非完整域或盲测',
                'seed': 2026102307, 'configs': configs,
                'native': None if library is None else {'path': str(library.path), 'sha256': library.sha256},
                'capacity_note': '仅报告节点bitstream逻辑容量；本脚本执行重建RGB8，未实现压缩native decoder，不作RSS或速度收益声明'}
    save(output/'run.json', identity)
    if not args.full:
        points = np.random.default_rng(identity['seed']).integers(0, 256, (262144, 3), dtype=np.uint8)
        indices = points.astype(np.int64) @ np.array([65536, 256, 1])
        gold = reference[indices]
        expected = baseline[indices]
        np.testing.assert_array_equal(predict(models, points), expected)
        (output/'probe.rgb').write_bytes(points.tobytes())
    results = []
    for name, node_bits, frac_bits, first_only in configs:
        candidate = [quantize(m, node_bits if i == 0 or not first_only else 8, frac_bits) for i, m in enumerate(models)]
        native = None
        if library is not None:
            paths, sides = [], []
            directory = output/name
            directory.mkdir()
            for i, model in enumerate(candidate):
                path = directory/f'stage{i+1}.slut'
                io.save_sparse(path, io.SparseLut(model.grid, model.nodes, model.idx, model.channel_frac[0]))
                paths.append(path)
                side = directory/f'stage{i+1}-frac.bin' if i == 0 else None
                if side is not None:
                    model.channel_frac.astype('<u4').tofile(side)
                sides.append(side)
            native = library.chain(paths, sides)
        hist = np.zeros(3*255**2+1, np.int64)
        sha = hashlib.sha256()
        if args.full:
            with (output/(name+'.rgb')).open('wb') as stream:
                for start in range(0, 256**3, 65536):
                    index = np.arange(start, start+65536, dtype=np.int64)
                    rgb = np.column_stack((index >> 16, (index >> 8) & 255, index & 255)).astype(np.uint8)
                    value = predict(candidate, rgb)
                    if native is not None:
                        np.testing.assert_array_equal(native.apply(rgb.copy(), kernel='avx2', threads=4), value)
                    if name == 'baseline':
                        np.testing.assert_array_equal(value, baseline[start:start+len(rgb)])
                    hist += histogram(value, reference[start:start+len(rgb)])
                    stream.write(value.tobytes())
                    sha.update(value.tobytes())
        else:
            value = predict(candidate, points)
            if native is not None:
                for kernel, threads in [('scalar', 1), ('avx2', 4)]:
                    np.testing.assert_array_equal(native.apply(points.copy(), kernel=kernel, threads=threads), value)
            hist = histogram(value, gold)
            sha.update(value.tobytes())
        node_payload = sum(m.nodes.size * (node_bits if i == 0 or not first_only else 8) for i, m in enumerate(models))
        row = {'name': name, 'node_bits': node_bits, 'fraction_bits': frac_bits, 'first_only': first_only,
               'metrics': hist_metrics(hist), 'prediction_sha256': sha.hexdigest(),
               'logical_node_bitstream_bytes': (node_payload+7)//8,
               'unchanged_rgb8_node_bytes': sum(m.nodes.nbytes for m in models),
               'node_changes_by_stage': [int(np.count_nonzero(a.nodes != b.nodes)) for a, b in zip(models, candidate)],
               'fraction_changes_by_stage': [int(np.count_nonzero(a.channel_frac != b.channel_frac)) for a, b in zip(models, candidate)]}
        if native is not None:
            row['decompressed_native'] = {'model_bytes': native.model_bytes, 'byte_mismatches': 0,
                                         'avx2_full_domain': args.full, 'scalar_probe_only': not args.full}
            native.close()
        if args.full:
            from PIL import Image
            stream_map = np.memmap(output/(name+'.rgb'), dtype=np.uint8, mode='r', shape=(256**3, 3))
            manifest = json.loads((source/'assets/photos/manifest.json').read_text(encoding='utf-8'))
            photo_hist = np.zeros_like(hist)
            per_image = []
            for photo in manifest['images']:
                image_path = source/photo['evaluation']['path']
                if digest(image_path) != photo['evaluation']['sha256']:
                    raise ValueError('照片SHA变化')
                with Image.open(image_path) as image:
                    if image.mode != 'RGB' or image.size != (1024, 768):
                        raise ValueError('照片格式不符')
                    rgb = np.asarray(image).reshape(-1, 3)
                keys = rgb.astype(np.int64) @ np.array([65536, 256, 1], np.int64)
                image_hist = histogram(stream_map[keys], reference[keys])
                photo_hist += image_hist
                per_image.append({'id': photo['id'], 'input_sha256': photo['evaluation']['sha256'], **hist_metrics(image_hist)})
            row['photos'] = {'scope': '完整100张既有照片，由已核验逐色映射索引；非独立盲测',
                             'merged': hist_metrics(photo_hist), 'per_image': per_image}
            if results:
                row['photo_accuracy_retention'] = retention(results[0]['photos']['merged'], row['photos']['merged'])
                row['worst_per_image_retention'] = min(
                    retention(old, new)['minimum'] for old, new in zip(results[0]['photos']['per_image'], per_image))
            stream_map._mmap.close()
            np.save(output/(name+'-photo-hist.npy'), photo_hist)
        if results:
            row['accuracy_retention'] = retention(results[0]['metrics'], row['metrics'])
        results.append(row)
        np.save(output/(name+'-hist.npy'), hist)
        save(output/'results.json', {'scope': identity['scope'], 'results': results, 'timing_performed': False})
        print(json.dumps(row, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
