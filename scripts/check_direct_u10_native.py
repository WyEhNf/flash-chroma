"""固定10bit精确索引的独立解码、完整域和逐图验收；不计性能。"""
from __future__ import annotations
import argparse
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from contextlib import ExitStack
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'python'), str(ROOT / 'experiments/channel-runtime')]
import numpy as np
from PIL import Image
from lutlab import io, study_provenance
from channel_native import Library
from run_channel_tail_nodes import digest, save
from outplace_support import apply_to, reject_to
from suffix_cache_support import cache_info
from domain_cache_support import info as domain_info
from direct16_support import info as direct_info, table as direct_table
from palette_support import info as palette_info
from check_direct_u16_ilp_native import Info, to, _cache_bytes


def info(chain):
    fn = chain.library.dll.p16_cc_get_direct_u10_info
    fn.argtypes = [ct.c_void_p, ct.POINTER(Info), ct.c_size_t]
    fn.restype = ct.c_int
    value = Info()
    if ct.sizeof(value) != 96 or fn(chain.handle, ct.byref(value), 96) or value.version != 1:
        raise ValueError('10bit诊断ABI不同')
    return {name: getattr(value, name) for name, _ in value._fields_}


def verify_sources(build):
    for rel, row in build['sources'].items():
        if digest(ROOT / rel) != row['sha256']:
            raise ValueError('构建冻结源码变更：' + rel)


def freeze(args):
    if args.output.exists():
        raise ValueError('不覆盖冻结目录')
    build_path = ROOT / 'artifacts/p16-direct-u10-frozen-v1/frozen.json'
    build = json.loads(build_path.read_text(encoding='utf-8'))
    verify_sources(build)
    dependency_path = ROOT / 'artifacts/p16-direct-u10-build-v1/dependency-audit-v2.json'
    dependency = json.loads(dependency_path.read_text(encoding='utf-8'))
    if not dependency['passed'] or dependency['frozen_sha256'] != digest(build_path):
        raise ValueError('完整编译依赖审计尚未通过')
    previous_path = ROOT / 'artifacts/p16-direct-u16-ilp-frozen-v1/frozen.json'
    previous = json.loads(previous_path.read_text(encoding='utf-8'))
    legacy = ROOT / 'artifacts/p16-direct-u16-ilp-build-v1/libjshc_direct_u16_ilp.dll'
    expected_legacy = 'd95332e9ac8b56a9d589bf176a5b020e2d60a176d1f360594a0300b5efae5b9f'
    expected_new = 'adf2a544420b69a2054741a8af0a8e536556e3f717d3b90db3c7ea8d683e59d4'
    if digest(legacy) != expected_legacy or digest(args.library) != expected_new:
        raise ValueError('288或289 DLL身份不同')
    receipt = json.loads((ROOT / 'artifacts/p16-direct-u10-build-v1/build-receipt.json').read_text(encoding='utf-8'))
    if (receipt['library_sha256'] != expected_new or receipt['contracts_exe_sha256'] != digest(args.contracts)
            or receipt['frozen_sha256'] != digest(build_path) or receipt['observed_exit_code'] != 0):
        raise ValueError('DLL/合同exe与成功构建收据不匹配')
    for spec in previous['models'].values():
        for path, sha in spec['input_sha256'].items():
            if digest(path) != sha:
                raise ValueError('固定模型变更')
        if digest(spec['oracle']) != spec['oracle_sha256']:
            raise ValueError('完整域oracle变更')
    files = [Path(__file__), ROOT / 'experiments/p16-direct-u10-quality-plan-v1.md',
             ROOT / 'scripts/audit_direct_u10_dependencies.py', dependency_path,
             ROOT / 'artifacts/p16-direct-u10-build-v1/build-receipt.json',
             build_path, previous_path, args.library, args.contracts, legacy,
             Path(previous['frozen_87_library'])]
    args.output.mkdir(parents=True)
    save(args.output / 'frozen.json', {
        'schema': 'p16_direct_u10_quality_v1', 'revision': 289,
        'build_frozen': str(build_path), 'previous_frozen': str(previous_path),
        'models': previous['models'], 'frozen_87_library': previous['frozen_87_library'],
        'frozen_87_sha256': previous['frozen_87_sha256'],
        'frozen_288_library': str(legacy), 'frozen_288_sha256': expected_legacy,
        'library': str(args.library.resolve()), 'library_sha256': expected_new,
        'contracts': str(args.contracts.resolve()),
        'files_sha256': {str(p.resolve()): digest(p) for p in files},
        'photo_manifest_sha256': previous['photo_manifest_sha256'],
        'quality_scope': '24完整域/600逐图/729短输入组/独立5B解码；无性能',
        'environment': study_provenance.environment_fingerprint()})


def palette_copy(chain):
    values = np.empty(info(chain)['palette_size'], np.uint32)
    fn = chain.library.dll.p16_cc_copy_u10_palette
    fn.argtypes = [ct.c_void_p, ct.POINTER(ct.c_uint32), ct.c_size_t]
    fn.restype = ct.c_int
    if fn(chain.handle, values.ctypes.data_as(ct.POINTER(ct.c_uint32)), len(values)):
        raise AssertionError('10bit palette快照失败')
    return values


def compare_layout(new, old):
    raw_new, raw_old = direct_table(new), direct_table(old)
    packed = raw_new.view(np.uint8)
    ids_old = raw_old.view(np.uint16)
    assert len(packed) == 20_971_524 and len(ids_old) == (1 << 24) + 2
    assert np.all(packed[-4:] == 0) and np.all(ids_old[-2:] == 0)
    pal = palette_copy(new)
    expected_palette = np.unique(np.frombuffer(_cache_bytes(old), np.uint32))
    np.testing.assert_array_equal(pal, expected_palette)
    np.testing.assert_array_equal(pal, np.unique(np.frombuffer(_cache_bytes(new), np.uint32)))
    maximum = 0
    # 独立重组整个40bit整数，再按10bit分离；不复用被测两字节地址公式。
    for first in range(0, 1 << 24, 1 << 18):
        groups = packed[first * 5 // 4:(first + (1 << 18)) * 5 // 4].reshape(-1, 5)
        aggregate = np.zeros(len(groups), np.uint64)
        for byte in range(5):
            aggregate |= groups[:, byte].astype(np.uint64) << (8 * byte)
        for lane in range(4):
            values = ((aggregate >> (10 * lane)) & 1023).astype(np.uint16)
            np.testing.assert_array_equal(values, ids_old[first + lane:first + (1 << 18):4])
            maximum = max(maximum, int(values.max()))
    assert maximum < len(pal)
    assert old.model_bytes - new.model_bytes == 12_582_912
    return {'packed_sha256': hashlib.sha256(raw_new.tobytes()).hexdigest(),
            'u16_sha256': hashlib.sha256(raw_old.tobytes()).hexdigest(),
            'palette_sha256': hashlib.sha256(pal.tobytes()).hexdigest(),
            'decoded_entries': 1 << 24, 'max_id': maximum, 'palette_size': len(pal),
            'guard_bytes': 4, 'guard_zero': True, 'ids_equal': True, 'palette_equal': True,
            'new_model_bytes': new.model_bytes, 'old_model_bytes': old.model_bytes,
            'capacity_saved_bytes': old.model_bytes - new.model_bytes,
            'new_data_mod64': info(new)['data_mod_64']}


def synthetic(library, output):
    directory = output / 'synthetic'
    directory.mkdir()
    line = np.arange(17, dtype=np.float64) * 16
    line[-1] = 255
    grid = np.tile(line, (3, 1))
    r, g, b = np.meshgrid(line, line, line, indexing='ij')
    identity = np.stack((r, g, b), axis=-1).astype(np.uint8)
    suffix = directory / 'identity.slut'
    io.save_sparse(suffix, io.SparseLut(grid, identity))
    _, frac = io.axis_tables(grid)
    side = np.repeat(frac[None], 3, axis=0)
    side[1, 2, 1] += 1
    side_path = directory / 'side.bin'
    side.astype('<u4').tofile(side_path)
    rng = np.random.default_rng(2026102416)
    sample = np.concatenate((rng.integers(0, 256, (4096, 3), dtype=np.uint8),
                             np.array([[0, 0, 0], [255, 255, 255]], np.uint8)))
    records = []
    for name in ('255', '256', 'overflow', 'one_stage'):
        nodes = (np.stack((r // 2, r // 2 + g // 8, r // 2 + b // 8), axis=-1)
                 if name == 'overflow' else np.repeat(r[..., None], 3, axis=-1)).astype(np.uint8)
        first = directory / (name + '-first.slut')
        io.save_sparse(first, io.SparseLut(grid, nodes))
        tail = suffix
        if name in ('255', '256'):
            tail = directory / (name + '-tail.slut')
            values = np.repeat(np.minimum(r, 254 if name == '255' else 255)[..., None], 3, axis=-1).astype(np.uint8)
            io.save_sparse(tail, io.SparseLut(grid, values))
        models = [first] if name == 'one_stage' else [first, tail, tail, tail]
        sides = [side_path] + [None] * (len(models) - 1)
        with library.chain(models, sides) as chain:
            state = info(chain)
            row = {'name': name, 'wide': state, 'direct': direct_info(chain),
                   'cache': cache_info(chain), 'domain': domain_info(chain), 'model_bytes': chain.model_bytes}
            if name == '255':
                assert not state['enabled'] and state['reason'] == 1 and row['direct']['format'] == 9
            elif name == '256':
                assert state['enabled'] and state['palette_size'] == 256 and row['direct']['format'] == 10
            elif name == 'overflow':
                assert not state['enabled'] and state['reason'] == 3 and state['palette_size'] > 1024
            else:
                assert not state['enabled'] and state['reason'] == 2
            with library.baseline.chain(models, sides) as reference:
                expected = reference.apply(sample.copy(), kernel='scalar', threads=1)
            for kernel, threads in [('scalar', 1), ('avx2', 1), ('avx2', 4)]:
                np.testing.assert_array_equal(chain.apply(sample.copy(), kernel=kernel, threads=threads), expected)
                np.testing.assert_array_equal(to(chain, sample, kernel, threads), expected)
            row['sample_sha256'] = hashlib.sha256(expected.tobytes()).hexdigest()
            records.append(row)
    return records


def validate(args):
    if args.output.exists():
        raise ValueError('不覆盖验收目录')
    frozen = json.loads(args.frozen.read_text(encoding='utf-8'))
    for path, sha in frozen['files_sha256'].items():
        if digest(path) != sha:
            raise ValueError('验收冻结文件变更：' + path)
    verify_sources(json.loads(Path(frozen['build_frozen']).read_text(encoding='utf-8')))
    for spec in frozen['models'].values():
        for path, sha in spec['input_sha256'].items():
            if digest(path) != sha:
                raise ValueError('模型变更')
        if digest(spec['oracle']) != spec['oracle_sha256']:
            raise ValueError('oracle变更')
    args.output.mkdir(parents=True)
    dll_dirs = [os.add_dll_directory('E:/mingw64/bin'), os.add_dll_directory(str(Path(frozen['library']).parent))]
    contract = subprocess.run([frozen['contracts']], capture_output=True, text=True)
    (args.output / 'contracts-stdout.txt').write_text(contract.stdout, encoding='utf-8')
    (args.output / 'contracts-stderr.txt').write_text(contract.stderr, encoding='utf-8')
    if contract.returncode:
        raise RuntimeError('guard合同失败：' + str(contract.returncode))
    guard = json.loads(contract.stdout)
    assert guard['guarded_cases'] == (88 if guard['bmi_supported'] else 22)
    library = Library(Path(frozen['library']), frozen['library_sha256'])
    library.baseline = Library(frozen['frozen_87_library'], frozen['frozen_87_sha256'])
    legacy = Library(frozen['frozen_288_library'], frozen['frozen_288_sha256'])
    assert library.revision == 289 and legacy.revision == 288 and library.baseline.revision == 87
    result = {'frozen_sha256': digest(args.frozen), 'library_sha256': library.sha256,
              'environment': study_provenance.environment_fingerprint(), 'performance_calls': 0,
              'new_default': False, 'guard_contract': guard, 'full_matrix': [], 'photo_matrix': [], 'capacity': {}}
    save(args.output / 'run.json', result)
    result['synthetic'] = synthetic(library, args.output)
    refs = {name: np.memmap(spec['oracle'], np.uint8, 'r', shape=(256 ** 3, 3))
            for name, spec in frozen['models'].items()}
    with ExitStack() as stack:
        chains = {name: stack.enter_context(library.chain(spec['models'], spec['sidecars']))
                  for name, spec in frozen['models'].items()}
        spec = frozen['models']['old_best']
        chains['87_old_best'] = stack.enter_context(library.baseline.chain(spec['models'], spec['sidecars']))
        for name, chain in chains.items():
            result['capacity'][name] = {'model_bytes': chain.model_bytes, 'cache': cache_info(chain),
                'domain': domain_info(chain), 'palette': palette_info(chain), 'direct': direct_info(chain),
                'wide': info(chain) if name != '87_old_best' else None}
            if name in ('max_first', 'p99_first'):
                assert info(chain)['enabled'] and direct_info(chain)['format'] == 10
            else:
                assert direct_info(chain)['format'] == 9 and direct_info(chain)['enabled']
        result['288_layout_identity'] = {}
        for name in ('max_first', 'p99_first', 'old_best'):
            spec = frozen['models'][name]
            with legacy.chain(spec['models'], spec['sidecars']) as old:
                if name == 'old_best':
                    np.testing.assert_array_equal(direct_table(chains[name]), direct_table(old))
                    assert chains[name].model_bytes == old.model_bytes
                    result['288_layout_identity'][name] = {'old8_table_equal': True, 'capacity_equal': True}
                else:
                    result['288_layout_identity'][name] = compare_layout(chains[name], old)
        save(args.output / 'layout.json', result)
        print(json.dumps({'layout_identity_passed': True, 'capacity': result['capacity']}, ensure_ascii=False), flush=True)
        hashes = {(n, k, t, p): hashlib.sha256() for n in chains
                  for k, t in [('scalar', 1), ('avx2', 1), ('avx2', 4)] for p in ('inplace', 'to')}
        for start in range(0, 256 ** 3, 65536):
            keys = np.arange(start, start + 65536, dtype=np.int64)
            rgb = np.column_stack((keys >> 16, (keys >> 8) & 255, keys & 255)).astype(np.uint8)
            before = rgb.copy()
            for name, chain in chains.items():
                expected = refs['old_best' if name == '87_old_best' else name][keys]
                for kernel, threads in [('scalar', 1), ('avx2', 1), ('avx2', 4)]:
                    for path in ('inplace', 'to'):
                        out = chain.apply(rgb.copy(), kernel=kernel, threads=threads) if path == 'inplace' else to(chain, rgb, kernel, threads)
                        np.testing.assert_array_equal(out, expected)
                        hashes[name, kernel, threads, path].update(out.tobytes())
            np.testing.assert_array_equal(rgb, before)
        result['full_matrix'] = [{'model': n, 'kernel': k, 'threads': t, 'path': p, 'sha256': h.hexdigest(), 'mismatches': 0}
                                 for (n, k, t, p), h in hashes.items()]
        save(args.output / 'full.json', result)
        print(json.dumps({'full_configs': len(hashes), 'mismatches': 0}, ensure_ascii=False), flush=True)
        manifest = args.cache_root / 'assets/photos/manifest.json'
        if digest(manifest) != frozen['photo_manifest_sha256']:
            raise ValueError('照片清单变更')
        for row in json.loads(manifest.read_text(encoding='utf-8'))['images']:
            path = args.cache_root / row['evaluation']['path']
            if digest(path) != row['evaluation']['sha256']:
                raise ValueError('照片变更')
            with Image.open(path) as image:
                rgb = np.asarray(image).reshape(-1, 3).copy()
            keys = rgb.astype(np.int64) @ np.array([65536, 256, 1], np.int64)
            for name, chain in chains.items():
                if name == '87_old_best':
                    continue
                expected = refs[name][keys]
                for path in ('inplace', 'to'):
                    out = chain.apply(rgb.copy(), kernel='avx2', threads=4) if path == 'inplace' else to(chain, rgb, 'avx2', 4)
                    np.testing.assert_array_equal(out, expected)
                    result['photo_matrix'].append({'image': row['id'], 'model': name, 'path': path,
                                                  'sha256': hashlib.sha256(out.tobytes()).hexdigest(), 'mismatches': 0})
        short = 0
        rng = np.random.default_rng(2026102417)
        for name in ('max_first', 'p99_first', 'old_best'):
            chain = chains[name]
            for length in [*range(18), 31, 32, 33, 4095, 4096, 4097, 65535, 65536, 65537]:
                for pattern in ('random', 'white', 'mixed'):
                    rgb = np.full((length, 3), 255, np.uint8) if pattern == 'white' else rng.integers(0, 256, (length, 3), dtype=np.uint8)
                    if pattern == 'mixed':
                        rgb[::7] = 255
                    keys = rgb.astype(np.int64) @ np.array([65536, 256, 1], np.int64)
                    expected = refs[name][keys]
                    for kernel, threads in [('scalar', 1), ('avx2', 1), ('avx2', 4)]:
                        np.testing.assert_array_equal(chain.apply(rgb.copy(), kernel=kernel, threads=threads), expected)
                        for same in (False, True):
                            actual = apply_to(chain.library.dll, chain.handle, rgb.tobytes(), int(kernel == 'avx2'), threads,
                                              source_offset=1, target_offset=3, same=same)
                            if actual != expected.tobytes():
                                raise AssertionError('短输入/同址/未对齐错误')
                        short += 1
            result.setdefault('outplace_rejections', {})[name] = reject_to(chain.library.dll, chain.handle)
        chain = chains['max_first']
        fn = library.dll.p16_cc_get_direct_u10_info
        value = Info()
        ct.memset(ct.byref(value), 0xa7, ct.sizeof(value))
        before = bytes(value)
        rejected = 0
        for handle, pointer, size in [(None, ct.byref(value), 96), (chain.handle, None, 96),
                                      (chain.handle, ct.byref(value), 95), (chain.handle, ct.byref(value), 97)]:
            assert fn(handle, pointer, size) == 1 and bytes(value) == before
            rejected += 1
        fn = library.dll.p16_cc_copy_u10_palette
        values = np.full(info(chain)['palette_size'], 0xa7a7a7a7, np.uint32)
        pointer = values.ctypes.data_as(ct.POINTER(ct.c_uint32))
        before = values.copy()
        for handle, output, count in [(None, pointer, len(values)), (chain.handle, None, len(values)),
                                       (chain.handle, pointer, len(values) - 1), (chain.handle, pointer, len(values) + 1)]:
            assert fn(handle, output, count) == 1 and np.array_equal(values, before)
            rejected += 1
        result['contract'] = {'short_pattern_backend_cases': short, 'diagnostic_rejections': rejected,
                              'mismatches': 0, 'allocation_failure_injection': False}
        assert len(result['full_matrix']) == 24 and len(result['photo_matrix']) == 600
        assert short == 729 and rejected == 8
        assert all(count == 11 for count in result['outplace_rejections'].values())
    for path, sha in frozen['files_sha256'].items():
        assert digest(path) == sha, path
    verify_sources(json.loads(Path(frozen['build_frozen']).read_text(encoding='utf-8')))
    result['passed'] = True
    result['limitations'] = '仅正确性及逻辑容量；未正式性能/RSS/构造峰值，分配失败未注入；x86小端AVX2，sidecar官方许可未知'
    save(args.output / 'results.json', result)
    print(json.dumps({'passed': True, 'full_configs': len(result['full_matrix']),
                      'photo_configs': len(result['photo_matrix']), 'contract': result['contract']}, ensure_ascii=False), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--frozen', type=Path)
    parser.add_argument('--library', type=Path)
    parser.add_argument('--contracts', type=Path)
    args = parser.parse_args()
    if args.freeze:
        if not args.library or not args.contracts:
            raise ValueError('冻结需要已构建DLL及合同exe')
        freeze(args)
    else:
        if not args.frozen:
            raise ValueError('验收需要冻结清单')
        validate(args)


if __name__ == '__main__':
    main()
