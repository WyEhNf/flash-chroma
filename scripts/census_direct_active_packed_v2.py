"""只用293固定max41的全域ID，精确重编号并检验9/10bit；无图像apply/测速。"""
from __future__ import annotations
import os
os.environ.update(OMP_NUM_THREADS='4', OMP_THREAD_LIMIT='4', OMP_DYNAMIC='FALSE',
                  OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', OMP_WAIT_POLICY='PASSIVE')
import psutil
psutil.Process().cpu_affinity([0, 2, 4, 6])
import argparse
from collections import Counter
import ctypes as ct
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'experiments/channel-runtime'), str(ROOT / 'scripts')]
import numpy as np
from channel_native import Library
from census_direct_sentinel import snapshot
from suffix_cache_support import cache_info
from domain_cache_support import info as domain_info

BASE = ROOT / 'artifacts/p16-direct-active-packed-v2'
QUALITY = ROOT / 'artifacts/p16-direct-cache2-quality-frozen-v1/frozen.json'
LIB_SHA = 'f70f0e6ac98c753c15496e23fe1c2684dec04b6c0cdec47539d83e6df67c51a5'
N = 1 << 24


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(name, value):
    path = BASE / name
    if path.exists():
        raise FileExistsError('不覆盖实际颜色/位表证据：' + str(path))
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def freeze():
    if BASE.exists():
        raise FileExistsError('不覆盖实际颜色/位表阶段')
    old = json.loads(QUALITY.read_text(encoding='utf-8'))
    assert sha(QUALITY) == '34225eea610fdef21153435f4f0bb6638a6caecb57c5ea0eddafae74f62ee6cd'
    library = old['libraries']['u16']
    assert library['sha256'] == LIB_SHA and library['revision'] == 293 and sha(library['path']) == LIB_SHA
    sources = dict(old['sources_sha256'])
    for name in ['scripts/census_direct_active_packed_v2.py', 'scripts/prepare_direct_active_packed_v2.py',
                 'experiments/p16-direct-active-packed-mechanical-v2.md', 'scripts/census_direct_active_packed.py', 'experiments/p16-direct-active-packed-plan-v1.md',
                 'scripts/census_direct_sentinel.py', 'scripts/domain_cache_support.py']:
        sources[name] = sha(ROOT / name)
    inputs = {}
    for path in [QUALITY, ROOT / 'artifacts/p16-direct-cache2-quality-v1/results.json',
                 ROOT / 'artifacts/p16-direct-cache2-quality-v1/independent-check-v2.json']:
        inputs[str(path)] = sha(path)
    used = [Path(library['path']), *[Path(p) for p in old['models']['max41']['models']],
        *[Path(p) for p in old['models']['max41']['sidecars'] if p]]
    used += [Path('E:/mingw64/bin') / name for name in
        ('libgomp-1.dll', 'libgcc_s_seh-1.dll', 'libstdc++-6.dll', 'libwinpthread-1.dll')]
    for path in used:
        actual = sha(path)
        if str(path) in old['inputs_sha256']:
            assert actual == old['inputs_sha256'][str(path)]
        inputs[str(path)] = actual
    independent = json.loads((ROOT / 'artifacts/p16-direct-cache2-quality-v1/independent-check-v2.json').read_text(encoding='utf-8'))
    assert independent['passed']
    for name, expected in sources.items():
        assert sha(ROOT / name) == expected, name
    for name, expected in inputs.items():
        assert sha(name) == expected, name
    BASE.mkdir()
    save('frozen.json', dict(source_sha256=sources, inputs_sha256=inputs,
        library=library, model=old['models']['max41'], maximum_packed_bits=10,
        inherited_quality_input_count=len(old['inputs_sha256']),
        prior_quality_inputs_rehashed=False,
        logical_entries=N, native_apply_calls=0, native_prepare_calls_expected=1,
        environment=dict(python=sys.version, numpy=np.__version__, byteorder=sys.byteorder,
                         process_affinity=psutil.Process().cpu_affinity())))
    print({'frozen_sha256': sha(BASE / 'frozen.json'), 'sources': len(sources), 'inputs': len(inputs)}, flush=True)


def verify(frozen):
    for name, expected in frozen['source_sha256'].items():
        assert sha(ROOT / name) == expected, name
    for name, expected in frozen['inputs_sha256'].items():
        assert sha(name) == expected, name


def positions(code, bits):
    if bits == 9:
        return code + (code >> 3), code & 7
    if bits == 10:
        return code + (code >> 2), (code & 3) << 1
    raise ValueError('仅固定9/10bit')


def packed_bytes(ids, bits):
    output = np.zeros((len(ids) * bits + 7) // 8 + 4, np.uint8)
    for begin in range(0, len(ids), 65536):
        end = min(begin + 65536, len(ids))
        code = np.arange(begin, end, dtype=np.uint64)
        address, shift = positions(code, bits)
        words = ids[begin:end].astype(np.uint32) << shift.astype(np.uint32)
        output[address] |= (words & 255).astype(np.uint8)
        output[address + 1] |= (words >> 8).astype(np.uint8)
    assert np.all(output[-4:] == 0)
    return output


def read_packed(data, begin, end, bits):
    code = np.arange(begin, end, dtype=np.uint64)
    address, shift = positions(code, bits)
    words = data[address].astype(np.uint32)
    for offset in (1, 2, 3):
        words |= data[address + offset].astype(np.uint32) << (8 * offset)
    return ((words >> shift.astype(np.uint32)) & ((1 << bits) - 1)).astype(np.uint16)


def finite():
    records = []
    for bits in (9, 10):
        for length in [*range(34), 63, 64, 65, 255, 256, 257, 65535, 65536, 65537]:
            for pattern in ('zero', 'maximum', 'alternate', 'increment'):
                maximum = (1 << bits) - 1
                ids = np.array([0 if pattern == 'zero' else maximum if pattern == 'maximum'
                    else (maximum if i % 2 else 0) if pattern == 'alternate' else i % (maximum + 1)
                    for i in range(length)], np.uint16)
                actual = packed_bytes(ids, bits)
                expected = bytearray((length * bits + 7) // 8 + 4)
                for i, value in enumerate(ids):
                    for b in range(bits):
                        if (int(value) >> b) & 1:
                            expected[(i * bits + b) // 8] |= 1 << ((i * bits + b) % 8)
                assert actual.tobytes() == expected
                decoded = read_packed(actual, 0, length, bits)
                assert np.array_equal(decoded, ids)
                for i in range(length):
                    byte, shift = divmod(i * bits, 8)
                    word = int.from_bytes(expected[byte:byte + 4], 'little')
                    assert (word >> shift) & maximum == int(ids[i])
                records.append({'bits': bits, 'length': length, 'pattern': pattern})
        last_byte, shift = divmod((N - 1) * bits, 8)
        assert last_byte == (N - 1) + ((N - 1) >> (3 if bits == 9 else 2))
        assert shift == ((N - 1) & 7 if bits == 9 else 2 * ((N - 1) & 3))
        assert last_byte + 4 <= N * bits // 8 + 4
    return records


def run():
    frozen = json.loads((BASE / 'frozen.json').read_text(encoding='utf-8'))
    verify(frozen)
    if (BASE / 'start.json').exists():
        raise FileExistsError('唯一实际颜色/位表不重采')
    save('start.json', dict(frozen_sha256=sha(BASE / 'frozen.json'), native_apply_calls=0))
    contracts = finite()
    save('finite.json', dict(passed=True, cases=contracts, cases_count=len(contracts), native_calls=0))
    dirs = [os.add_dll_directory('E:/mingw64/bin'),
            os.add_dll_directory(str(Path(frozen['library']['path']).parent))]
    library = Library(frozen['library']['path'], LIB_SHA)
    assert library.revision == 293
    with library.chain(frozen['model']['models'], frozen['model']['sidecars']) as chain:
        wide, palette, raw = snapshot(chain)
        cache, domain = cache_info(chain), domain_info(chain)
        assert cache['enabled'] and domain['eligible'] and domain['unproven_cells'] == 0
        assert wide['palette_size'] == 613 and len(palette) == 613
        old_capacity = chain.model_bytes
        ids = raw.view('<u2')[:-2]
        assert len(ids) == N and np.all(palette[1:] > palette[:-1])
        prior_quality = json.loads((ROOT / 'artifacts/p16-direct-cache2-quality-v1/results.json').read_text(encoding='utf-8'))
        prior_physical = [row for row in prior_quality['physical'] if row['variant'] == 'u16' and row['model'] == 'max41']
        assert len(prior_physical) == 1
        actual_physical_sha = hashlib.sha256(raw).hexdigest()
        assert actual_physical_sha == prior_physical[0]['raw_sha256']
        raw.tofile(BASE / 'physical-ids-u16-with-guard.bin')
        palette.tofile(BASE / 'whole-palette-u32.bin')
        counts = np.zeros(len(palette), np.uint64)
        python_counts = Counter()
        for begin in range(0, N, 65536):
            part = ids[begin:begin + 65536]
            counts += np.bincount(part, minlength=len(palette)).astype(np.uint64)
            python_counts.update(int(v) for v in part)
        assert counts.tolist() == [python_counts[i] for i in range(len(palette))]
        assert int(counts.sum()) == N
        active = np.flatnonzero(counts).astype(np.uint16)
        if len(active) > 1024:
            save('results.json', dict(passed=False, stop='active_colors_exceed1024', active_colors=len(active),
                cache_colors=len(palette), native_prepare_calls=1, native_apply_calls=0))
            return
        bits = 9 if len(active) <= 512 else 10
        mapping = np.zeros(len(palette), np.uint16)
        mapping[active] = np.arange(len(active), dtype=np.uint16)
        compact = mapping[ids]
        colors = palette[active].copy()
        packed = packed_bytes(compact, bits)
        assert len(packed) == N * bits // 8 + 4
        packed.tofile(BASE / 'packed-ids-with-guard.bin')
        colors.tofile(BASE / 'active-palette-u32.bin')
        for begin in range(0, N, 65536):
            end = begin + 65536
            decoded = read_packed(packed, begin, end, bits)
            assert np.array_equal(decoded, compact[begin:end])
            assert np.array_equal(colors[decoded], palette[ids[begin:end]])
        result = dict(passed=True, frozen_sha256=sha(BASE / 'frozen.json'), native_prepare_calls=1,
            native_apply_calls=0, performance_samples=0, logical_entries=N, physical_r_fastest=True,
            physical_ids_sha256=actual_physical_sha, physical_ids_equal_to_prior_full_quality=True,
            whole_cache_colors=len(palette), active_colors=len(active), packed_bits=bits,
            active_old_palette_ids=active.tolist(), whole_palette=palette.tolist(), whole_id_frequencies=counts.tolist(),
            actual_state=dict(wide=wide, cache=cache, domain=domain), old_model_capacity=old_capacity,
            packed_payload_bytes=N * bits // 8, packed_owned_bytes=len(packed), palette_bytes=colors.nbytes,
            old_u16_table_bytes=wide['table_capacity_bytes'],
            census_extra_payload_bytes=dict(raw_snapshot=raw.nbytes, compact_ids=compact.nbytes,
                packed_ids=packed.nbytes, whole_palette=palette.nbytes, compact_palette=colors.nbytes,
                frequencies=counts.nbytes, old_to_new_mapping=mapping.nbytes),
            candidate_table_and_palette_bytes=len(packed) + colors.nbytes,
            finite_cases=len(contracts), full_decoded_entries=N, independent_python_frequency_equal=True,
            process_memory=psutil.Process().memory_info()._asdict(),
            artifacts={p.name: dict(bytes=p.stat().st_size, sha256=sha(p))
                for p in BASE.iterdir() if p.is_file()},
            scope='只证完整实际颜色频数与离线位表逐ID/RGB32精确；不是native packed、速度、免费prepare或准备峰节省。')
    verify(frozen)
    save('results.json', result)
    print({k: result[k] for k in ('passed', 'whole_cache_colors', 'active_colors', 'packed_bits',
        'candidate_table_and_palette_bytes', 'full_decoded_entries', 'native_apply_calls')}, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('freeze', 'run'))
    args = parser.parse_args()
    freeze() if args.mode == 'freeze' else run()
