"""只用288纯模型输出普查固定输入G分bank的8bit可表示性；不读gold/照片、不拟合或计时。"""
from __future__ import annotations
from collections import Counter
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'experiments/channel-runtime')]
import numpy as np
from channel_native import Library

OUT = ROOT / 'artifacts/p16-direct-gbank8-census-v1'
DLL = ROOT / 'artifacts/p16-direct-u16-ilp-build-v1/libjshc_direct_u16_ilp.dll'
DLL_SHA = 'd95332e9ac8b56a9d589bf176a5b020e2d60a176d1f360594a0300b5efae5b9f'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    if path.exists():
        raise FileExistsError('不覆盖固定G分bank证据：' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


class WideInfo(ct.Structure):
    _fields_ = [(n, ct.c_uint32) for n in ['version', 'enabled', 'format', 'reason', 'palette_size', 'id_bytes', 'guard_bytes', 'reserved']]
    _fields_ += [(n, ct.c_uint64) for n in ['input_entries', 'raw_words', 'table_capacity_bytes', 'palette_capacity_bytes', 'temporary_peak_bytes', 'guaranteed_alignment', 'data_mod_64']]
    _fields_ += [('prepare_seconds', ct.c_double)]


def pure_snapshot(chain):
    d = chain.library.dll
    f = d.p16_cc_get_direct_u16_info
    f.argtypes = [ct.c_void_p, ct.POINTER(WideInfo), ct.c_size_t]
    f.restype = ct.c_int
    state = WideInfo()
    assert ct.sizeof(state) == 96 and f(chain.handle, ct.byref(state), 96) == 0
    assert state.version == 1 and state.enabled and state.format == 16 and state.input_entries == 1 << 24
    raw = np.empty(state.raw_words, np.uint32)
    f = d.jshc_cc_copy_direct
    f.argtypes = [ct.c_void_p, ct.POINTER(ct.c_uint32), ct.c_size_t]
    f.restype = ct.c_int
    assert f(chain.handle, raw.ctypes.data_as(ct.POINTER(ct.c_uint32)), raw.size) == 0
    ids = raw.view('<u2')
    assert ids.size == (1 << 24) + 2 and np.all(ids[-2:] == 0)
    palette = np.empty(state.palette_size, np.uint32)
    f = d.p16_cc_copy_u16_palette
    f.argtypes = [ct.c_void_p, ct.POINTER(ct.c_uint32), ct.c_size_t]
    f.restype = ct.c_int
    assert f(chain.handle, palette.ctypes.data_as(ct.POINTER(ct.c_uint32)), palette.size) == 0
    assert 256 <= palette.size <= 65536 and np.max(ids[:-2]) < palette.size
    assert np.all(palette <= 0xffffff) and np.all(palette[1:] > palette[:-1])
    return raw, ids[:-2], palette


def main():
    if OUT.exists():
        raise FileExistsError('不覆盖G256单版普查目录')
    metadata = ROOT / 'artifacts/p16-direct-sentinel-perf-frozen-v1/plan.json'
    old = json.loads(metadata.read_text(encoding='utf-8'))
    models = {name: {'models': old['models'][name]['models'], 'sidecars': old['models'][name]['sidecars']}
              for name in ['max_first', 'p99_first', 'max48']}
    candidate = ROOT / 'artifacts/cinema-current-feasible-cpsat-accept-v1/candidate'
    models['max41'] = {'models': [str(candidate / 'candidate-base.slut'), str(candidate / 'stage2.slut'),
                                  old['models']['max48']['models'][2], str(candidate / 'stage4.slut')],
                       'sidecars': [str(candidate / 'channel-frac.bin'), None, None, None]}
    inputs = {str(DLL): DLL_SHA, str(metadata): sha(metadata)}
    for spec in models.values():
        for path in spec['models'] + [p for p in spec['sidecars'] if p]:
            inputs[path] = sha(path)
    sources = [Path(__file__), ROOT / 'experiments/p16-direct-gbank8-plan-v1.md', ROOT / 'experiments/channel-runtime/channel_native.py']
    source_hashes = {path.relative_to(ROOT).as_posix(): sha(path) for path in sources}
    assert sha(DLL) == DLL_SHA
    OUT.mkdir(parents=True)
    save(OUT / 'frozen.json', {'purpose': __doc__, 'sources_sha256': source_hashes, 'inputs_sha256': inputs,
                              'models': models, 'bank_channel': 'G', 'banks': 256, 'maximum_colors_per_bank': 256,
                              'canonical_order': 'RGB32升序', 'python': sys.version, 'platform': platform.platform(),
                              'numpy': np.__version__, 'pixel_apply_calls': 0, 'performance_calls': 0,
                              'decision': '逐模型固定G分区；任一bank>256则该模型本版不实施；不扫描其他分区'})
    dirs = [os.add_dll_directory('E:/mingw64/bin'), os.add_dll_directory(str(DLL.parent))]
    library = Library(str(DLL), DLL_SHA)
    assert library.revision == 288
    records = []
    for name, spec in models.items():
        directory = OUT / name
        directory.mkdir()
        with library.chain(spec['models'], spec['sidecars']) as chain:
            raw, ids, palette = pure_snapshot(chain)
            cube = ids.reshape(256, 256, 256)
            bank_palette = np.zeros((256, 256), dtype='<u4')
            lengths = np.zeros(256, dtype='<u2')
            physical = np.zeros((1 << 24) + 4, dtype=np.uint8)
            physical_cube = physical[:-4].reshape(256, 256, 256)
            banks = []
            over = []
            for green in range(256):
                values = palette[cube[:, green, :]].reshape(-1)
                colors, counts = np.unique(values, return_counts=True)
                # 第二条路径显式构造内部code，避免只用同一个reshape表达自证。
                codes = (np.arange(256, dtype=np.uint32)[:, None] << 16) | (green << 8) | np.arange(256, dtype=np.uint32)[None, :]
                independent = Counter(int(v) for v in palette[ids[codes]].reshape(-1))
                assert independent == dict(zip(colors.tolist(), counts.tolist())) and sum(independent.values()) == 65536
                row = {'green': green, 'colors': int(colors.size), 'colors_sha256': hashlib.sha256(colors.astype('<u4').tobytes()).hexdigest(),
                       'maximum_id_if_representable': int(colors.size - 1) if colors.size <= 256 else None}
                banks.append(row)
                if colors.size > 256:
                    over.append({'green': green, 'colors': int(colors.size), 'first257_rgb32': colors[:257].tolist()})
                    continue
                lengths[green] = colors.size
                bank_palette[green, :colors.size] = colors
                mapped = np.searchsorted(colors, values)
                assert np.max(mapped) < 256
                physical_cube[:, green, :] = mapped.reshape(256, 256).astype(np.uint8)
                np.testing.assert_array_equal(bank_palette[green, physical_cube[:, green, :]], values.reshape(256, 256))
            passed = not over
            products = {}
            if passed:
                for green in range(256):
                    np.testing.assert_array_equal(bank_palette[green, physical_cube[:, green, :]], palette[cube[:, green, :]])
                assert np.all(physical[-4:] == 0)
                for filename, value in [('physical-ids-u8.bin', physical), ('bank-palettes-le32.bin', bank_palette), ('bank-lengths-le16.bin', lengths)]:
                    path = directory / filename
                    value.tofile(path)
                    products[filename] = {'sha256': sha(path), 'bytes': path.stat().st_size}
                assert sum(v['bytes'] for v in products.values()) == 17039876
            record = {'model': name, 'representable': passed, 'banks': banks, 'overflow_banks': over,
                      'maximum_colors': max(row['colors'] for row in banks), 'logical_inputs': 1 << 24,
                      'legacy_physical_ids_sha256': hashlib.sha256(raw.tobytes()).hexdigest(),
                      'legacy_palette_sha256': hashlib.sha256(palette.tobytes()).hexdigest(), 'products': products,
                      'full_replay_mismatches': 0 if passed else None, 'production_model_bytes_measured': False}
            save(directory / 'results.json', record)
            records.append(record)
            del raw, ids, palette, cube, physical, physical_cube
    for name, expected in source_hashes.items():
        assert sha(ROOT / name) == expected, name
    for name, expected in inputs.items():
        assert sha(name) == expected, name
    save(OUT / 'results.json', {'passed': True, 'purpose': '普查执行/独立逐bank计数一致，不等于所有模型可表示或运行时合格',
                                'models': records, 'pixel_apply_calls': 0, 'performance_calls': 0,
                                'limitations': '没有新生产native/guard/100图或速度；固定payload不是实际总Model/RSS'})
    print(json.dumps({'census_completed': True, 'models': [{'model': row['model'], 'representable': row['representable'],
                       'maximum_colors': row['maximum_colors'], 'overflow_banks': len(row['overflow_banks'])} for row in records],
                       'pixel_apply_calls': 0, 'performance_calls': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
