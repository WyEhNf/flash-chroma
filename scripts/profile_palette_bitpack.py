"""固定模型palette的两种量化筛查；完整误差联合频数支持独立复算。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'python'))
sys.path.insert(0, str(ROOT / 'scripts'))
from accept_channel_coordinates import hist_metrics
from lutlab.study_provenance import environment_fingerprint


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def rgb_codes(rgb):
    values = rgb.astype(np.uint32)
    return values[:, 0] | (values[:, 1] << 8) | (values[:, 2] << 16)


def joint(ids, gold):
    codes = (ids.astype(np.uint64) << 24) | rgb_codes(gold).astype(np.uint64)
    return np.unique(codes, return_counts=True)


def quality(pair, counts, decoded_palette):
    index = (pair >> 24).astype(np.intp)
    gold = np.column_stack((pair & 255, (pair >> 8) & 255, (pair >> 16) & 255)).astype(np.int32)
    delta = decoded_palette[index].astype(np.int32) - gold
    squared = np.sum(delta * delta, axis=1)
    hist = np.zeros(3 * 255**2 + 1, np.int64)
    np.add.at(hist, squared, counts)
    return hist


def retention(before, after):
    ratios = {key: (min(1., before[key] / after[key]) if after[key] else 1.) for key in ('mean', 'p99', 'max')}
    return dict(components=ratios, minimum=min(ratios.values()))


def map_nearest(palette, centers):
    squared = np.sum((palette.astype(np.int32)[:, None, :] - centers.astype(np.int32)[None, :, :])**2, axis=2)
    return np.argmin(squared, axis=1).astype(np.uint8)


def maximin(palette, weights, sizes):
    used = np.flatnonzero(weights)
    first = int(np.argmax(weights))
    chosen = [first]
    distance = np.sum((palette.astype(np.int32) - palette[first].astype(np.int32))**2, axis=1)
    distance[weights == 0] = -1
    results = {}
    for target in sorted(sizes):
        while len(chosen) < min(target, len(used)):
            pick = int(np.argmax(distance))
            chosen.append(pick)
            candidate = np.sum((palette.astype(np.int32) - palette[pick].astype(np.int32))**2, axis=1)
            distance = np.minimum(distance, candidate)
        centers = palette[chosen].copy()
        results[target] = (centers, map_nearest(palette, centers))
    return results


def ward(palette, weights, sizes):
    active = np.flatnonzero(weights).tolist()
    mass = weights.astype(np.float64).copy()
    sums = palette.astype(np.float64) * mass[:, None]
    groups = {index: [index] for index in active}
    results = {}
    for target in sorted(sizes, reverse=True):
        while len(active) > target:
            ids = np.asarray(active)
            centers = sums[ids] / mass[ids, None]
            squared = np.sum((centers[:, None, :] - centers[None, :, :])**2, axis=2)
            values = squared * mass[ids, None] * mass[ids][None, :] / (mass[ids, None] + mass[ids][None, :])
            values[np.tril_indices(len(ids))] = np.inf
            a, b = np.unravel_index(int(np.argmin(values)), values.shape)
            left, right = active[a], active[b]
            mass[left] += mass[right]
            sums[left] += sums[right]
            groups[left].extend(groups.pop(right))
            active.pop(b)
        centers = np.floor(sums[active] / mass[active, None] + .5).astype(np.uint8)
        mapping = map_nearest(palette, centers)
        for new_id, old_id in enumerate(active):
            mapping[groups[old_id]] = new_id
        results[target] = (centers.copy(), mapping.copy())
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root', type=Path, required=True)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source = args.data_root.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    plan_path = ROOT / 'experiments/p16-palette-bitpack-v1.json'
    plan = json.loads(plan_path.read_text(encoding='utf-8'))
    files = dict(rom=args.rom.resolve(), cube=source / 'artifacts/cinema-current-anchor-accept-v1/cube.rgb',
                 reference=source / 'artifacts/cinema-axis-calibration-v1/envelope-reference.npy',
                 manifest=source / 'assets/photos/manifest.json',
                 model=source / 'artifacts/cinema-current-anchor-v1/current-anchor-pipeline.npz')
    for name, path in files.items():
        assert sha(path) == plan[name + '_sha256'], name
    blob = files['rom'].read_bytes()
    assert blob[:4] == b'M16D' and struct.unpack_from('<I', blob, 8)[0] == 0
    colors = np.frombuffer(blob, dtype=np.uint8, offset=32, count=1024).reshape(256, 4)[:, :3].copy()
    ids = np.frombuffer(blob, dtype=np.uint8, offset=1056).reshape(256, 256, 256).transpose(2, 1, 0).reshape(-1).copy()
    weights = np.bincount(ids, minlength=256)
    expected = np.memmap(files['cube'], dtype=np.uint8, mode='r', shape=(256**3, 3))
    for start in range(0, len(ids), 65536):
        np.testing.assert_array_equal(colors[ids[start:start + 65536]], expected[start:start + 65536])
    # 此前所有拟合只读模型；从此处才开始读取参考与照片做验收。
    sizes = [1 << bits for bits in plan['bit_widths']]
    fits = dict(weighted_ward_centroid=ward(colors, weights, sizes), maximin_original_color=maximin(colors, weights, sizes))
    configs = [('baseline', 8, colors, np.arange(256, dtype=np.uint8))]
    for algorithm in plan['algorithms']:
        for bits in plan['bit_widths']:
            palette, mapping = fits[algorithm][1 << bits]
            configs.append((algorithm + str(bits), bits, palette, mapping))
    source_files = [Path(__file__), plan_path, ROOT / 'scripts/accept_channel_coordinates.py']
    save(output / 'run.json', dict(purpose=__doc__, plan_sha256=sha(plan_path), inputs={name: dict(path=str(path), sha256=sha(path)) for name, path in files.items()},
        source_sha256={str(path.relative_to(ROOT)): sha(path) for path in source_files}, environment=environment_fingerprint(),
        fitting_inputs='仅ROM palette与完整输入域频数，gold/照片不参与palette生成',
        scopes='全16M颜色与完整100图，已见非盲测；无新native/decoder/速度', configs=[name for name, *_ in configs]))
    reference = np.load(files['reference'], mmap_mode='r')
    full_pair, full_counts = joint(ids, reference)
    support = dict(full_pairs=full_pair, full_counts=full_counts, palette=colors, weights=weights)
    rows = []
    hists = []
    for name, bits, palette, mapping in configs:
        decoded = palette[mapping]
        hist = quality(full_pair, full_counts, decoded)
        hists.append(np.zeros_like(hist))
        np.savez_compressed(output / (name + '.npz'), palette=palette, mapping=mapping)
        rows.append(dict(name=name, bits=bits, palette_entries=len(palette), metrics=hist_metrics(hist), photos=dict(per_image=[]),
                         logical_id_bytes=2**24 * bits // 8, native_decoder=False))
    manifest = json.loads(files['manifest'].read_text(encoding='utf-8'))
    for index, photo in enumerate(manifest['images']):
        image_path = source / photo['evaluation']['path']
        assert sha(image_path) == photo['evaluation']['sha256']
        with Image.open(image_path) as image:
            assert image.mode == 'RGB' and image.size == (1024, 768)
            rgb = np.asarray(image).reshape(-1, 3).astype(np.uint32)
        keys = (rgb[:, 0] << 16) | (rgb[:, 1] << 8) | rgb[:, 2]
        pair, counts = joint(ids[keys], reference[keys])
        support[f'p{index:03d}_pairs'] = pair
        support[f'p{index:03d}_counts'] = counts
        for row, accum, (_, _, palette, mapping) in zip(rows, hists, configs):
            hist = quality(pair, counts, palette[mapping])
            accum += hist
            row['photos']['per_image'].append(dict(id=photo['id'], input_sha256=photo['evaluation']['sha256'], **hist_metrics(hist)))
    for row, hist in zip(rows, hists):
        row['photos']['merged'] = hist_metrics(hist)
        before = rows[0]
        row['full_retention'] = retention(before['metrics'], row['metrics'])
        row['photo_retention'] = retention(before['photos']['merged'], row['photos']['merged'])
        per_image = [retention(old, new)['minimum'] for old, new in zip(before['photos']['per_image'], row['photos']['per_image'])]
        row['worst_image_retention'] = min(per_image)
        row['worst_image_id'] = row['photos']['per_image'][int(np.argmin(per_image))]['id']
        row['photo_changes'] = {key: {label: sum(1 for old, new in zip(before['photos']['per_image'], row['photos']['per_image'])
            if ('better' if new[key] < old[key] - 1e-12 else 'worse' if new[key] > old[key] + 1e-12 else 'equal') == label)
            for label in ('better', 'equal', 'worse')} for key in ('mean', 'rms', 'p99', 'max', 'cvar_1pct')}
        row['minimum_retention'] = min(row['full_retention']['minimum'], row['photo_retention']['minimum'], min(per_image))
        row['accuracy_tiers'] = [tier for tier in [1., .9, .8, .7, .6, .5] if row['minimum_retention'] + 1e-12 >= tier]
        print(json.dumps({key: row[key] for key in ['name', 'metrics', 'minimum_retention', 'accuracy_tiers']}, ensure_ascii=False), flush=True)
    np.savez_compressed(output / 'joint-support.npz', **support)
    save(output / 'results.json', dict(scope='全域/100图及逐图min精度保留，不代表解码器、内存或吞吐验收', results=rows))


if __name__ == '__main__':
    main()
