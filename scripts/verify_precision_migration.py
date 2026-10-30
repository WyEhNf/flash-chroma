"""独立NumPy重放完整RGB域，并核对冻结模型、百图及历史chain_ls同图基线。"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def load_stage(folder, number, metadata):
    blob = (folder / f'{number}.slut').read_bytes()
    m = metadata['m']
    assert blob[:4] == b'SLUT' and int.from_bytes(blob[8:12], 'little') == m
    index = np.frombuffer(blob, np.uint8, 768, 16 + 12 * m).reshape(3, 256)
    sidecar = (folder / f'{number}.fractions').read_bytes()
    fraction = (np.frombuffer(sidecar, '<u4').reshape(3, 3, 256) if sidecar else
                np.broadcast_to(np.frombuffer(blob, '<u4', 768, 16 + 12 * m + 768).reshape(3, 256), (3, 3, 256)))
    nodes = np.frombuffer(blob, np.uint8, offset=16 + 12 * m + 3840).reshape(-1, 3)
    return m, index, fraction, nodes, metadata['interpolation']


def mapping(rgb, stage):
    m, index, fraction, nodes, kind = stage
    cells = np.stack([index[a, rgb[:, a]] for a in range(3)], axis=1).astype(np.int64)
    base = cells @ np.array([m*m, m, 1], np.int64)
    result = np.empty_like(rgb)
    for c in range(3):
        f = np.stack([fraction[c, a, rgb[:, a]] for a in range(3)], axis=1).astype(np.uint64)
        if kind == 1:
            value = np.full(len(rgb), 1 << 47, np.uint64)
            for r in range(2):
                for g in range(2):
                    for b in range(2):
                        w = ((f[:, 0] if r else 65536-f[:, 0]) * (f[:, 1] if g else 65536-f[:, 1]) *
                             (f[:, 2] if b else 65536-f[:, 2]))
                        value += w * nodes[base+r*m*m+g*m+b, c]
            result[:, c] = value >> 48
        else:
            order = np.argsort(-f.astype(np.int64), axis=1, kind='stable')
            sorted_f = np.take_along_axis(f, order, axis=1)
            strides = np.array([m*m, m, 1])[order]
            positions = (base, base+strides[:, 0], base+strides[:, 0]+strides[:, 1], base+m*m+m+1)
            weights = (65536-sorted_f[:, 0], sorted_f[:, 0]-sorted_f[:, 1], sorted_f[:, 1]-sorted_f[:, 2], sorted_f[:, 2])
            value = np.full(len(rgb), 32768, np.uint64)
            for pos, weight in zip(positions, weights):
                value += nodes[pos, c] * weight
            result[:, c] = value >> 16
    return result


def pack(rgb):
    return rgb.astype(np.uint32) @ np.array([1, 256, 65536], np.uint32)


def measure(hist):
    n = int(hist.sum()); d = np.arange(len(hist), dtype=np.int64); root = np.sqrt(d)
    position, fraction = divmod(99*(n-1), 100)
    endpoints = np.searchsorted(np.cumsum(hist), [position, position+bool(fraction)], side='right')
    remaining = (n+99)//100; tail = 0.
    for error in np.flatnonzero(hist)[::-1]:
        take = min(remaining, int(hist[error])); tail += take*root[error]; remaining -= take
        if not remaining:
            break
    return dict(pixels=n, mean=float(hist @ root/n), sse=int(hist @ d), rms=float(np.sqrt(hist @ d/n)),
                p99=float(root[endpoints[0]]+(root[endpoints[1]]-root[endpoints[0]])*fraction/100),
                max=float(root[np.flatnonzero(hist)[-1]]), cvar01=tail/((n+99)//100))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('run', 'cache', 'photos', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    meta = json.loads((args.run / 'model.json').read_text(encoding='utf-8-sig'))
    stages = [load_stage(args.run, i, stage) for i, stage in enumerate(meta['stages'])]
    source_manifest = json.loads((args.cache / 'manifest.json').read_text(encoding='utf-8-sig'))
    raw = []
    for item in source_manifest['records']:
        path = args.cache / item['path']
        assert digest(path) == item['binary_sha256']
        raw.append(np.memmap(path, dtype='<u2', mode='r').reshape(-1, 3))
    output = np.memmap(args.run / 'domain.rgb', dtype=np.uint8, mode='r').reshape(-1, 3)
    assert output.shape == (256**3, 3)
    histogram = np.zeros(195076, np.int64)
    per_code_error = np.empty(256**3, np.int32)
    for begin in range(0, 256**3, 65536):
        codes = np.arange(begin, begin+65536, dtype=np.uint32)
        rgb = ((codes[:, None] >> np.array([0, 8, 16], np.uint32)) & 255).astype(np.uint8)
        expected = rgb.copy()
        for stage in stages:
            rgb = mapping(rgb, stage)
        assert np.array_equal(rgb, output[begin:begin+65536]), f'完整域输出不同：{begin}'
        for table in raw:
            expected = (table[pack(expected), ::-1]//16).astype(np.uint8)
        squared = np.sum((expected.astype(np.int32)-rgb)**2, axis=1)
        per_code_error[begin:begin+65536] = squared
        histogram += np.bincount(squared, minlength=len(histogram))
    measured = measure(histogram)
    recorded = json.loads((args.run/'domain.json').read_text(encoding='utf-8-sig'))
    for key in measured:
        assert abs(measured[key]-recorded[key]) < 1e-9, key
    photos = json.loads((args.photos/'manifest.json').read_text(encoding='utf-8-sig'))
    native = json.loads((args.run/'photos.json').read_text(encoding='utf-8-sig'))
    assert len(photos['images']) == len(native['images']) == 100
    for image, recorded in zip(photos['images'], native['images']):
        path = args.photos / image['raw']
        assert digest(path) == image['raw_sha256']
        rgb = np.fromfile(path, np.uint8).reshape(-1, 3)
        metric = measure(np.bincount(per_code_error[pack(rgb)], minlength=len(histogram)))
        for key in metric:
            assert abs(metric[key]-recorded['quality'][key]) < 1e-9, (image['index'], key)
    result = dict(scope='完整16777216输入/100图独立NumPy重放，非性能测试', domain=measured, images=100,
                  pixel_bytes_verified=int(output.size), domain_sha256=digest(args.run/'domain.rgb'),
                  sources=source_manifest['records'], photo_manifest_sha256=digest(args.photos/'manifest.json'),
                  model_files={p.name:digest(p) for p in args.run.iterdir() if p.suffix in ('.slut', '.fractions')},
                  mean=native['mean'], worst_image_mean=native['worst_image_mean'])
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(domain=measured, images=100, mean=native['mean']), ensure_ascii=False))


if __name__ == '__main__':
    main()
