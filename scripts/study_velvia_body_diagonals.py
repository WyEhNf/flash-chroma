"""冻结Velvia四种全局体对角线；独立整数几何与全域/百图质量，不宣称运行时兼容。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numba
import numpy as np
from PIL import Image
from lutlab import channel_coordinates as cc, io, study_provenance
from run_channel_tail_nodes import load_model, digest, save
from accept_channel_tail_nodes import histogram
from accept_channel_coordinates import hist_metrics, changes
from verify_channel_coordinates import integer_oracle


def physical_oracle(model, points, mask):
    """原节点物理索引：反向轴用负步长，u64凸权重，独立于重参数化核。"""
    base = sum(model.idx[a, points[:, a]].astype(np.int64)*model.m**(2-a) for a in range(3))
    stride = np.tile(np.array([model.m**2, model.m, 1], np.int64), (len(points), 1))
    for a in range(3):
        if mask & (1 << a):
            base += stride[:, a]
            stride[:, a] *= -1
    output = np.empty((len(points), 3), np.uint8)
    for channel in range(3):
        f = np.column_stack([model.channel_frac[channel, a, points[:, a]] for a in range(3)]).astype(np.int64)
        steps = stride.copy()
        for a in range(3):
            if mask & (1 << a):
                f[:, a] = io.ONE-f[:, a]
        for a, b in ((0, 1), (1, 2), (0, 1)):
            swap = f[:, a] < f[:, b]
            f[swap, a], f[swap, b] = f[swap, b].copy(), f[swap, a].copy()
            steps[swap, a], steps[swap, b] = steps[swap, b].copy(), steps[swap, a].copy()
        weights = np.column_stack((io.ONE-f[:, 0], f[:, 0]-f[:, 1], f[:, 1]-f[:, 2], f[:, 2]))
        ids = np.column_stack((base, base+steps[:, 0], base+steps[:, :2].sum(axis=1), base+steps.sum(axis=1)))
        if np.any(weights < 0) or np.any(weights.sum(axis=1) != io.ONE) or np.any(ids < 0) or np.any(ids >= model.m**3):
            raise AssertionError('有向四面体的凸权重或物理节点界错误')
        acc = np.sum(weights.astype(np.uint64)*model.nodes.reshape(-1, 3)[ids, channel].astype(np.uint64), axis=1, dtype=np.uint64)
        output[:, channel] = ((acc+io.ONE//2) >> io.Q).astype(np.uint8)
    return output


def reparameterize(model, mask):
    """仅研究核的等价数组；反向idx不满足现有ChannelLut非降契约。"""
    axes = tuple(a for a in range(3) if mask & (1 << a))
    nodes = np.flip(model.nodes, axes).copy() if axes else model.nodes.copy()
    idx, frac = model.idx.copy(), model.channel_frac.copy()
    for a in axes:
        idx[a] = model.m-2-idx[a]
        frac[:, a] = io.ONE-frac[:, a]
    return cc.ChannelLut(model.grid.copy(), nodes, idx, frac)


def raw_predict(model, points):
    return cc._predict(points, model.nodes.reshape(-1, 3), model.idx, model.channel_frac, model.m)


def contract():
    rng = np.random.default_rng(2026102419)
    records = []
    for m in (17, 33):
        grid = np.tile(np.linspace(0, 255, m), (3, 1))
        model = cc.from_sparse(io.SparseLut(grid, rng.integers(0, 256, (m, m, m, 3), dtype=np.uint8)))
        for channel in range(3):
            model.channel_frac[channel, :, 1:255] = np.clip(model.channel_frac[channel, :, 1:255].astype(np.int64)+(channel-1)*113, 0, io.ONE)
        cc.validate(model)
        points = rng.integers(0, 256, (4096, 3), dtype=np.uint8)
        points[:8] = np.array(np.meshgrid(*[[0, 255]]*3, indexing='ij')).reshape(3, -1).T
        outputs = {}
        for mask in range(8):
            mapped = reparameterize(model, mask)
            value = physical_oracle(model, points, mask)
            np.testing.assert_array_equal(value, raw_predict(mapped, points))
            outputs[mask] = value
        for mask in range(4):
            np.testing.assert_array_equal(outputs[mask], outputs[mask ^ 7])
        np.testing.assert_array_equal(outputs[0], integer_oracle(model, points))
        records.append({'m': m, 'points': len(points), 'masks': list(range(8)), 'physical_vs_reparameterized_mismatches': 0,
            'complement_pair_mismatches': 0, 'mask0_vs_existing_oracle_mismatches': 0})
    return {'seed': 2026102419, 'records': records, 'pass': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖四方向冻结结果')
    args.output.mkdir(parents=True)
    numba.set_num_threads(4)
    cache = args.cache_root.resolve()
    paths = {'model': cache/'artifacts/velvia-channel-coordinates-v1/channel-coordinates.npz',
        'table': cache/'artifacts/chain-error-cache/source-2ff0a4e385f9f9e49ca02f63/table.lut256',
        'baseline': cache/'artifacts/velvia-channel-coordinates-accept-v1/cube.rgb',
        'manifest': cache/'assets/photos/manifest.json'}
    hashes = {n: digest(p) for n, p in paths.items()}
    if hashes['model'] != '3e5f8fd94e8dc9b97dbfea2823896b8dffb6e014b5e6056ab5c10b58a69af3d0' or hashes['table'] != '6c4387352bd0845ce597f13dca32f2f808b39439d06ce78b4881922a4fc294b7' or hashes['baseline'] != '945d4b906ae9aa184fdddd7f084da0105fa87b7e756f88ea700ca53f61ed37f0':
        raise ValueError('不是冻结的Velvia当前最佳或参考')
    save(args.output/'run.json', {'input_sha256': hashes, 'environment': study_provenance.environment_fingerprint(),
        'numba_threads': 4, 'masks': [0, 1, 2, 4], 'policy': '当前3e5f节点/Q16坐标固定，只测四种全局一致体对角线。不拟合，不按照片追加方向或节点。',
        'scope': '研究表示质量，不将非降契约外的反向idx伪称普通SLUT；无原生或性能调用。'})
    save(args.output/'contract.json', contract())
    model = load_model(paths['model'])
    reference = io.load_full(paths['table'], mmap=True).reshape(-1, 3)
    baseline = np.memmap(paths['baseline'], np.uint8, 'r', shape=reference.shape)
    manifest = json.loads(paths['manifest'].read_text(encoding='utf-8'))
    results = {'variants': {}, 'new_default': False, 'native_calls': 0, 'performance_calls': 0}
    baseline_rows = None
    for mask in (0, 1, 2, 4):
        mapped = reparameterize(model, mask)
        output = np.memmap(args.output/f'mask{mask}.rgb', np.uint8, 'w+', shape=reference.shape)
        hist = np.zeros(3*255**2+1, np.int64)
        hasher = hashlib.sha256()
        for start in range(0, len(reference), 65536):
            keys = np.arange(start, start+65536, dtype=np.int64)
            rgb = np.column_stack((keys >> 16, (keys >> 8)&255, keys&255)).astype(np.uint8)
            value = physical_oracle(model, rgb, mask)
            np.testing.assert_array_equal(value, raw_predict(mapped, rgb))
            if mask == 0:
                np.testing.assert_array_equal(value, baseline[start:start+len(keys)])
            output[start:start+len(keys)] = value
            hist += histogram(value, reference[start:start+len(keys)])
            hasher.update(value.tobytes())
        output.flush()
        photo_rows, photo_hist = [], np.zeros_like(hist)
        for row in manifest['images']:
            path = cache/row['evaluation']['path']
            if digest(path) != row['evaluation']['sha256']:
                raise ValueError('照片manifest不符')
            with Image.open(path) as image:
                rgb = np.asarray(image).reshape(-1, 3)
            keys = rgb.astype(np.int64)@np.array([65536, 256, 1], np.int64)
            h = histogram(output[keys], reference[keys]); photo_hist += h
            photo_rows.append({'image': row['id'], **hist_metrics(h)})
        if mask == 0:
            baseline_rows = photo_rows
        photos = {**hist_metrics(photo_hist), 'per_image': photo_rows, 'changes': changes(baseline_rows, photo_rows)}
        cube = hist_metrics(hist)
        try:
            cc.validate(mapped)
            accepted_contract = True
        except ValueError:
            accepted_contract = False
        row = {'mask': mask, 'cube': cube, 'photos': photos, 'sha256': hasher.hexdigest(),
            'full_physical_vs_reparameterized_mismatches': 0, 'existing_channel_contract_accepts': accepted_contract}
        if mask:
            old = results['variants']['0']
            row['quality_gate_passed'] = all(row[g][k] <= old[g][k]+1e-12 for g in ('cube', 'photos') for k in ('mean', 'rms', 'p99', 'max', 'cvar_1pct'))
            row['strict_tail_improvement'] = any(row[g][k] < old[g][k]-1e-12 for g in ('cube', 'photos') for k in ('p99', 'max'))
        results['variants'][str(mask)] = row
        save(args.output/'results.json', results)
        print(json.dumps({'mask': mask, 'cube': cube, 'photos': {k: v for k, v in photos.items() if k not in ('per_image', 'changes')},
            'quality_gate_passed': row.get('quality_gate_passed'), 'strict_tail_improvement': row.get('strict_tail_improvement')}, ensure_ascii=False), flush=True)
    sources = [Path(__file__), ROOT/'python/lutlab/channel_coordinates.py', ROOT/'scripts/verify_channel_coordinates.py',
        ROOT/'scripts/accept_channel_coordinates.py', ROOT/'scripts/accept_channel_tail_nodes.py', ROOT/'python/lutlab/io.py']
    with zipfile.ZipFile(args.output/'source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sources:
            archive.write(path, path.relative_to(ROOT).as_posix())
    save(args.output/'manifest.json', {'source_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in sources},
        'files': {p.name: digest(p) for p in args.output.iterdir() if p.suffix in ('.json', '.zip')},
        'streams_sha256': {f'mask{k}.rgb': r['sha256'] for k, r in results['variants'].items()},
        'scope': '完整流仅离线质量证据；无新模型许可、原生兼容、速度或额外内存结论。'})


if __name__ == '__main__':
    main()
