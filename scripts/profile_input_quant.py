"""固定三种输入近邻网格的完整域/百图精度与真实RGB32派生文件。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import struct
import sys
import hashlib
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'python'))
sys.path.insert(0, str(ROOT / 'scripts'))
from profile_palette_bitpack import sha, save, quality, joint, retention
from accept_channel_coordinates import hist_metrics
from lutlab.study_provenance import environment_fingerprint


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source = args.data_root.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    plan_path = ROOT / 'experiments/p16-input-quant-v1.json'
    plan = json.loads(plan_path.read_text(encoding='utf-8'))
    files = dict(cube=source / 'artifacts/cinema-current-anchor-accept-v1/cube.rgb',
                 reference=source / 'artifacts/cinema-axis-calibration-v1/envelope-reference.npy',
                 manifest=source / 'assets/photos/manifest.json')
    for name, path in files.items():
        assert sha(path) == plan[name + '_sha256'], name
    baseline = np.memmap(files['cube'], dtype=np.uint8, mode='r', shape=(256**3, 3))
    configs = [('baseline', 8, None, None)]
    for bits in plan['bits']:
        step = 1 << (8 - bits)
        axis = np.minimum(np.arange((1 << bits) + 1, dtype=np.uint32) * step, 255)
        keys = (axis[:, None, None] << 16) | (axis[None, :, None] << 8) | axis[None, None, :]
        table = baseline[keys].copy()
        rgba = np.zeros((*table.shape[:-1], 4), np.uint8)
        rgba[..., :3] = table
        header = b'Q16N' + struct.pack('<7I', 1, bits, len(axis), rgba.nbytes, 0, 0, 0)
        path = output / f'input{bits}.bin'
        path.write_bytes(header + rgba.tobytes())
        lookup = np.minimum((np.arange(256, dtype=np.uint32) + step // 2) >> (8 - bits), 1 << bits)
        # 端点和取整规则独立用距离最小值复核；等距选择较大索引。
        for value in range(256):
            distances = np.abs(axis.astype(np.int32) - value)
            winners = np.flatnonzero(distances == distances.min())
            assert lookup[value] == winners[-1]
        configs.append((f'input{bits}', bits, table, lookup))
    source_files = [Path(__file__), plan_path, ROOT / 'scripts/profile_palette_bitpack.py', ROOT / 'scripts/accept_channel_coordinates.py']
    save(output / 'run.json', dict(purpose=__doc__, plan_sha256=sha(plan_path),
        inputs={name: dict(path=str(path), sha256=sha(path)) for name, path in files.items()},
        source_sha256={str(path.relative_to(ROOT)): sha(path) for path in source_files}, environment=environment_fingerprint(),
        export='所有候选文件在读取gold/照片之前导出，只读固定a399模型流', limits=plan['limits']))
    reference = np.load(files['reference'], mmap_mode='r')

    def predict(table, lookup, rgb):
        keys = (rgb[:, 0].astype(np.uint32) << 16) | (rgb[:, 1].astype(np.uint32) << 8) | rgb[:, 2]
        if table is None:
            return baseline[keys]
        q = lookup[rgb]
        return table[q[:, 0], q[:, 1], q[:, 2]]

    def histogram(value, gold):
        delta = value.astype(np.int32) - gold.astype(np.int32)
        return np.bincount(np.sum(delta * delta, axis=1), minlength=3 * 255**2 + 1).astype(np.int64)

    hists = [np.zeros(3 * 255**2 + 1, np.int64) for _ in configs]
    hashes = [hashlib.sha256() for _ in configs]
    for start in range(0, 256**3, 65536):
        keys = np.arange(start, start + 65536, dtype=np.uint32)
        rgb = np.column_stack((keys >> 16, (keys >> 8) & 255, keys & 255)).astype(np.uint8)
        for hist, digest, (_, _, table, lookup) in zip(hists, hashes, configs):
            value = predict(table, lookup, rgb)
            hist += histogram(value, reference[start:start + len(keys)])
            digest.update(value.tobytes())
    rows = []
    photo_hists = [np.zeros_like(hist) for hist in hists]
    for hist, digest, (name, bits, table, _) in zip(hists, hashes, configs):
        row = dict(name=name, bits=bits, metrics=hist_metrics(hist), prediction_sha256=digest.hexdigest(), photos=dict(per_image=[]))
        if table is not None:
            path = output / (name + '.bin')
            row.update(grid_dimension=table.shape[0], file_bytes=path.stat().st_size, file_sha256=sha(path), native_decoder=False)
        rows.append(row)
    manifest = json.loads(files['manifest'].read_text(encoding='utf-8'))
    for photo in manifest['images']:
        path = source / photo['evaluation']['path']
        assert sha(path) == photo['evaluation']['sha256']
        with Image.open(path) as image:
            assert image.mode == 'RGB' and image.size == (1024, 768)
            rgb = np.asarray(image).reshape(-1, 3)
        keys = (rgb[:, 0].astype(np.uint32) << 16) | (rgb[:, 1].astype(np.uint32) << 8) | rgb[:, 2]
        gold = reference[keys]
        for row, hist, (_, _, table, lookup) in zip(rows, photo_hists, configs):
            image_hist = histogram(predict(table, lookup, rgb), gold)
            hist += image_hist
            row['photos']['per_image'].append(dict(id=photo['id'], input_sha256=photo['evaluation']['sha256'], **hist_metrics(image_hist)))
    for row, hist in zip(rows, photo_hists):
        row['photos']['merged'] = hist_metrics(hist)
        before = rows[0]
        row['full_retention'] = retention(before['metrics'], row['metrics'])
        row['photo_retention'] = retention(before['photos']['merged'], row['photos']['merged'])
        per_image = [retention(old, new)['minimum'] for old, new in zip(before['photos']['per_image'], row['photos']['per_image'])]
        row['worst_image_retention'] = min(per_image)
        row['worst_image_id'] = row['photos']['per_image'][int(np.argmin(per_image))]['id']
        row['minimum_retention'] = min(row['full_retention']['minimum'], row['photo_retention']['minimum'], min(per_image))
        row['accuracy_tiers'] = [tier for tier in [1., .9, .8, .7, .6, .5] if row['minimum_retention'] + 1e-12 >= tier]
        row['photo_changes'] = {key: {label: sum(1 for old, new in zip(before['photos']['per_image'], row['photos']['per_image'])
            if ('better' if new[key] < old[key] - 1e-12 else 'worse' if new[key] > old[key] + 1e-12 else 'equal') == label)
            for label in ('better', 'equal', 'worse')} for key in ('mean', 'rms', 'p99', 'max', 'cvar_1pct')}
        print(json.dumps({key: row[key] for key in ['name', 'metrics', 'minimum_retention', 'accuracy_tiers']}, ensure_ascii=False), flush=True)
    np.savez_compressed(output / 'histograms.npz', **{f'full_{row[0]}': hist for row, hist in zip(configs, hists)},
                        **{f'photo_{row[0]}': hist for row, hist in zip(configs, photo_hists)})
    save(output / 'results.json', dict(scope='有损派生网格，全16M与100图；文件为真实RGB32，尚无native吞吐/RSS或赛事合法结论', results=rows))


if __name__ == '__main__':
    main()
