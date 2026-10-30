"""纯模型普查固定top255精确颜色与8lane哨兵率，不读gold/照片，不计性能。"""
from __future__ import annotations
import argparse
from collections import Counter
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'experiments/channel-runtime'))
import numpy as np
from channel_native import Library
from direct16_support import info as direct_info, table as direct_table
from suffix_cache_support import cache_info, cache_table

TOTAL = 1 << 24
DLL = ROOT / 'artifacts/p16-direct-u16-ilp-build-v1/libjshc_direct_u16_ilp.dll'
DLL_SHA = 'd95332e9ac8b56a9d589bf176a5b020e2d60a176d1f360594a0300b5efae5b9f'
SOURCES = ['scripts/census_direct_sentinel.py', 'experiments/p16-sentinel-census-plan-v1.json',
           'experiments/channel-runtime/channel_native.py', 'scripts/direct16_support.py',
           'scripts/suffix_cache_support.py', 'scripts/exception_support.py', 'scripts/palette_support.py']


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


class WideInfo(ct.Structure):
    _fields_ = [(n, ct.c_uint32) for n in ('version', 'enabled', 'format', 'reason', 'palette_size', 'id_bytes', 'guard_bytes', 'reserved')]
    _fields_ += [(n, ct.c_uint64) for n in ('input_entries', 'raw_words', 'table_capacity_bytes', 'palette_capacity_bytes',
                                        'temporary_peak_bytes', 'guaranteed_alignment', 'data_mod_64')]
    _fields_ += [('prepare_seconds', ct.c_double)]


def snapshot(chain):
    fn = chain.library.dll.p16_cc_get_direct_u16_info
    fn.argtypes = [ct.c_void_p, ct.POINTER(WideInfo), ct.c_size_t]
    fn.restype = ct.c_int
    state = WideInfo()
    assert ct.sizeof(state) == 96 and fn(chain.handle, ct.byref(state), 96) == 0
    assert state.version == state.enabled == 1 and state.format == 16 and state.id_bytes == 2
    assert state.input_entries == TOTAL and state.raw_words == TOTAL // 2 + 1 and state.guard_bytes == 4
    assert direct_info(chain)['format'] == 16
    values = np.empty(state.palette_size, dtype=np.uint32)
    fn = chain.library.dll.p16_cc_copy_u16_palette
    fn.argtypes = [ct.c_void_p, ct.POINTER(ct.c_uint32), ct.c_size_t]
    fn.restype = ct.c_int
    assert fn(chain.handle, values.ctypes.data_as(ct.POINTER(ct.c_uint32)), len(values)) == 0
    raw = direct_table(chain)
    assert raw.dtype == np.uint32 and len(raw) == state.raw_words
    ids = raw.view('<u2')
    assert np.all(ids[-2:] == 0) and ids[:-2].max() < len(values)
    return {n: getattr(state, n) for n, _ in state._fields_}, values, raw


def freeze(output):
    if output.exists():
        raise ValueError('不覆盖哨兵纯模型冻结')
    previous = ROOT / 'artifacts/p16-direct-u16-ilp-frozen-v1/frozen.json'
    old = read(previous)
    models = {}
    for name in ('max_first', 'p99_first'):
        spec = old['models'][name]
        models[name] = {k: spec[k] for k in ('models', 'sidecars', 'input_sha256')}
        for path, expected in spec['input_sha256'].items():
            assert sha(path) == expected
    assert sha(DLL) == DLL_SHA
    output.mkdir(parents=True)
    save(output / 'frozen.json', {'schema': 'p16_direct_sentinel_census_v1', 'models': models,
         'library': str(DLL), 'library_sha256': DLL_SHA, 'metadata_source': str(previous), 'metadata_sha256': sha(previous),
         'source_sha256': {name: sha(ROOT / name) for name in SOURCES},
         'python': sys.version, 'numpy': np.__version__, 'byteorder': sys.byteorder,
         'scope': '两个固定模型各prepare一次，cache/domain两固定top255；无oracle/gold/照片输入或性能。',
         'resources': '一次32MiB owned ID快照；分块65536频数、最多4个R平面布尔包；不建立第二份canonical ID整表。'})
    print(json.dumps({'frozen_sha256': sha(output / 'frozen.json'), 'models': len(models), 'performance_calls': 0}))


def rank(frequency, palette):
    return sorted(range(len(palette)), key=lambda i: (-int(frequency[i]), int(palette[i])))[:255]


def vector_counts(ids, palette, cache):
    domain = np.zeros(len(palette), np.uint64)
    for start in range(0, len(ids), 65536):
        domain += np.bincount(ids[start:start+65536], minlength=len(palette)).astype(np.uint64)
    index = np.searchsorted(palette, cache)
    assert np.array_equal(palette[index], cache)
    cached = np.bincount(index, minlength=len(palette)).astype(np.uint64)
    return cached, domain


def numpy_packets(ids, hot):
    physical, canonical = np.zeros(9, np.uint64), np.zeros(9, np.uint64)
    for start in range(0, TOTAL, 65536):
        misses = (~hot[ids[start:start+65536]]).reshape(-1, 8).sum(axis=1)
        physical += np.bincount(misses.astype(np.int64), minlength=9).astype(np.uint64)
    view = ids.reshape(256, 256, 256)
    for start in range(0, 256, 4):
        misses = (~hot[view[:, :, start:start+4].transpose(2, 1, 0)]).reshape(-1, 8).sum(axis=1)
        canonical += np.bincount(misses.astype(np.int64), minlength=9).astype(np.uint64)
    return physical, canonical


def independent(ids, palette, cache, rankings):
    # Python真整数Counter与逐8项计数，独立于np.bincount/reshape包算法。
    counts, cached = Counter(), Counter(int(value) for value in cache)
    physical = [Counter(), Counter()]
    canonical = [Counter(), Counter()]
    hot = [set(int(value) for value in row) for row in rankings]
    for start in range(0, TOTAL, 65536):
        values = [int(value) for value in ids[start:start+65536]]
        counts.update(values)
        for offset in range(0, len(values), 8):
            group = values[offset:offset+8]
            for index in range(2):
                physical[index][sum(value not in hot[index] for value in group)] += 1
    view = ids.reshape(256, 256, 256)
    for r in range(256):
        values = [int(value) for value in view[:, :, r].T.flat]
        for offset in range(0, len(values), 8):
            group = values[offset:offset+8]
            for index in range(2):
                canonical[index][sum(value not in hot[index] for value in group)] += 1
    domain = [counts[i] for i in range(len(palette))]
    cache_frequency = [cached[int(value)] for value in palette]
    expected_ranks = [sorted(range(len(palette)), key=lambda i: (-freq[i], int(palette[i])))[:255]
                      for freq in (cache_frequency, domain)]
    assert expected_ranks == rankings
    return cache_frequency, domain, physical, canonical


def census(frozen_path, output):
    if output.exists():
        raise ValueError('不覆盖哨兵普查')
    frozen = read(frozen_path)
    for name, expected in frozen['source_sha256'].items():
        assert sha(ROOT / name) == expected, name
    assert sha(frozen['library']) == frozen['library_sha256'] == DLL_SHA
    assert sys.byteorder == 'little'
    directories = [os.add_dll_directory('E:/mingw64/bin'), os.add_dll_directory(str(DLL.parent))]
    library = Library(DLL, DLL_SHA)
    assert library.revision == 288
    output.mkdir(parents=True)
    results = {}
    for name, spec in frozen['models'].items():
        for path, expected in spec['input_sha256'].items():
            assert sha(path) == expected
        directory = output / name
        directory.mkdir()
        with library.chain(spec['models'], spec['sidecars']) as chain:
            state, palette, raw = snapshot(chain)
            geometry = cache_info(chain)
            assert geometry['enabled'] == 1 and geometry['reason'] == 0
            cache = cache_table(chain, geometry)
            assert np.array_equal(np.unique(cache), palette) and np.all(palette <= 0xffffff)
            ids = raw.view('<u2')[:-2]
            raw.tofile(directory / 'physical-ids-u16-with-guard.bin')
            cache.tofile(directory / 'whole-cache-u32.bin')
            palette.tofile(directory / 'palette-u32.bin')
            cached, domain = vector_counts(ids, palette, cache)
            assert int(cached.sum()) == len(cache) and int(domain.sum()) == TOTAL
            rankings = [rank(cached, palette), rank(domain, palette)]
            py_cache, py_domain, py_physical, py_canonical = independent(ids, palette, cache, rankings)
            assert py_cache == cached.tolist() and py_domain == domain.tolist()
            illegal_zero, position, legal = 0, 0, 0
            for r in range(geometry['r_min'], geometry['r_max']+1):
                for dg in range(geometry['dg_min'], geometry['dg_max']+1):
                    for db in range(geometry['db_min'], geometry['db_max']+1):
                        valid = 0 <= r+dg <= 255 and 0 <= r+db <= 255
                        legal += valid
                        if not valid:
                            assert int(cache[position]) == 0
                            illegal_zero += 1
                        position += 1
            assert position == len(cache) and legal == geometry['valid_entries']
            ranks = {}
            for index, (label, chosen) in enumerate(zip(('cache_top255', 'domain_top255'), rankings)):
                hot = np.zeros(len(palette), bool)
                hot[chosen] = True
                physical, canonical = numpy_packets(ids, hot)
                assert physical.tolist() == [py_physical[index][i] for i in range(9)]
                assert canonical.tolist() == [py_canonical[index][i] for i in range(9)]
                misses = sum(int(domain[i]) for i in range(len(palette)) if i not in set(chosen))
                for histogram in (physical, canonical):
                    assert int(histogram.sum()) == TOTAL // 8
                    assert sum(i*int(histogram[i]) for i in range(9)) == misses
                ranks[label] = {'palette_ids': chosen, 'rgb32': [int(palette[i]) for i in chosen],
                    'cache_counts': [int(cached[i]) for i in chosen], 'domain_counts': [int(domain[i]) for i in chosen],
                    'hits': TOTAL-misses, 'misses': misses, 'pixel_hit_ratio': (TOTAL-misses)/TOTAL,
                    'physical_miss_lanes_histogram': physical.tolist(), 'canonical_miss_lanes_histogram': canonical.tolist(),
                    'canonical_any_miss_packet_ratio': 1-int(canonical[0])/(TOTAL//8),
                    'canonical_all_miss_packet_ratio': int(canonical[8])/(TOTAL//8)}
            zero_id = next((i for i, value in enumerate(palette) if int(value) == 0), None)
            row = {'model_bytes': chain.model_bytes, 'wide': state, 'cache_geometry': geometry,
                   'palette_size': len(palette), 'domain_positive_colors': int(np.count_nonzero(domain)),
                   'cache_counts': cached.tolist(), 'domain_counts': domain.tolist(), 'rankings': ranks,
                   'common_top_colors': len(set(rankings[0]) & set(rankings[1])),
                   'zero': {'palette_id': zero_id, 'cache_slots': int(cached[zero_id]) if zero_id is not None else 0,
                            'proven_invalid_unfilled_zero_slots': illegal_zero,
                            'domain_count': int(domain[zero_id]) if zero_id is not None else 0,
                            'cache_top255_contains_zero': zero_id in rankings[0]},
                   'independent_python_integer_check': True,
                   'files_sha256': {p.name: sha(p) for p in directory.iterdir() if p.is_file()},
                   'performance_calls': 0, 'apply_calls': 0}
            save(directory / 'results.json', row)
            results[name] = row
        print(json.dumps({'model': name, 'palette_size': len(palette),
                          'cache_pixel_hit_ratio': ranks['cache_top255']['pixel_hit_ratio'],
                          'cache_any_miss_packet_ratio': ranks['cache_top255']['canonical_any_miss_packet_ratio'],
                          'domain_pixel_hit_ratio': ranks['domain_top255']['pixel_hit_ratio']}, ensure_ascii=False), flush=True)
    for key, expected in frozen['source_sha256'].items():
        assert sha(ROOT / key) == expected
    save(output / 'results.json', {'passed': True, 'frozen_sha256': sha(frozen_path), 'models': results,
         'performance_calls': 0, 'apply_calls': 0, 'gold_or_photo_reads': 0,
         'scope': '两固定排名完整域频数和8包率，非照片包率、正式吞吐或免费prepare证明。'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--frozen', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.freeze:
        freeze(args.output)
    else:
        if not args.frozen:
            raise ValueError('普查需要先冻结')
        census(args.frozen, args.output)


if __name__ == '__main__':
    main()
