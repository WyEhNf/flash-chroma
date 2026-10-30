"""102固定模型完整RGB8、真实百图及尾部/非对齐/拒绝合同；不测性能或重新拟合。"""
from __future__ import annotations

import argparse
import ctypes as ct
import hashlib
from pathlib import Path
import struct
import traceback

import numpy as np

import p16_unified_support as s


def finite(chain, cube, backend, threads):
    rng = np.random.default_rng(202610260102)
    count = 0
    for length in (0, 1, 2, 7, 8, 9, 15, 16, 17, 31, 32, 33, 63, 64, 65, 4095, 4096, 4097, 65535, 65536, 65537):
        source = rng.integers(0, 256, (length, 3), np.uint8)
        code = source.astype(np.uint32)
        expected = cube[(code[:, 0] << 16) | (code[:, 1] << 8) | code[:, 2]]
        raw = source.reshape(-1)
        for offset in (0, 1, 7, 15, 31, 63):
            for same in (False, True):
                a = np.full(raw.size + offset + 64, 0xa7, np.uint8)
                a[offset:offset + raw.size] = raw
                source_view = a[offset:offset + raw.size].reshape(-1, 3)
                before = a.copy()
                target_offset = 63 - offset
                b = a if same else np.full(raw.size + target_offset + 64, 0x59, np.uint8)
                target_view = source_view if same else b[target_offset:target_offset + raw.size].reshape(-1, 3)
                chain.apply(source_view, target_view, backend, threads, same)
                assert np.array_equal(target_view, expected), (backend, threads, length, offset, same)
                if same:
                    assert np.array_equal(a[:offset], before[:offset])
                    assert np.array_equal(a[offset + raw.size:], before[offset + raw.size:])
                else:
                    assert np.array_equal(a, before), '分离源被改写'
                    assert np.all(b[:target_offset] == 0x59)
                    assert np.all(b[target_offset + raw.size:] == 0x59)
                count += 1
    return count


def rejects(chain):
    d = chain.library.dll
    a = (ct.c_uint8 * 64)(*([0xa7] * 64))
    b = (ct.c_uint8 * 64)(*([0x59] * 64))
    p, q = ct.cast(a, s.U8), ct.cast(b, s.U8)
    before = (bytes(a), bytes(b))
    error = ct.create_string_buffer(1024)
    maximum = (1 << (ct.sizeof(ct.c_void_p) * 8)) - 1
    cases = [(None, p, q, 3, 1, 1), (chain.handle, None, q, 3, 1, 1),
        (chain.handle, p, None, 3, 1, 1), (chain.handle, p, q, 1, 1, 1),
        (chain.handle, p, q, 3, -1, 1), (chain.handle, p, q, 3, 3, 1),
        (chain.handle, p, q, 3, 1, 0), (chain.handle, p, q, 3, 1, 257),
        (chain.handle, ct.cast(maximum - 2, s.U8), q, 6, 1, 1),
        (chain.handle, p, ct.cast(maximum - 2, s.U8), 6, 1, 1),
        (chain.handle, p, ct.cast(ct.addressof(a) + 1, s.U8), 6, 1, 1),
        (chain.handle, ct.cast(ct.addressof(a) + 1, s.U8), p, 6, 1, 1)]
    for args in cases:
        assert d.jshc_cc_apply_to(*args, error, len(error)) == 1, args
        assert (bytes(a), bytes(b)) == before, '拒绝调用改写缓冲区'
    return len(cases)


def unsupported(chain, backend, reason='当前CPU/OS不支持此后端'):
    a = (ct.c_uint8 * 48)(*range(48))
    b = (ct.c_uint8 * 48)(*([0x59] * 48))
    before = (bytes(a), bytes(b))
    error = ct.create_string_buffer(1024)
    kernel = s.BACKENDS[backend]
    assert chain.library.dll.jshc_cc_apply(chain.handle, a, 48, kernel, 1, error, len(error)) == 1
    inplace_error = error.value.decode('utf-8', 'replace')
    assert chain.library.dll.jshc_cc_apply_to(chain.handle, a, b, 48, kernel, 1, error, len(error)) == 1
    assert (bytes(a), bytes(b)) == before
    return {'backend': backend, 'executed': False, 'rejection_calls': 2,
        'inplace_error': inplace_error, 'outplace_error': error.value.decode('utf-8', 'replace'),
        'reason': reason, 'scope': '不满足后端条件时明确拒绝且缓冲区不变；不是AVX512像素执行正确性。'}


def mixed_m_contract(library, folder):
    """固定随机节点的普通SLUT四级混合m；独立uint64凸权重是数学真值。"""
    folder.mkdir()
    rng = np.random.default_rng(202610260103)
    stages, rows = [], []
    code = np.arange(256, dtype=np.int64)
    for index, m in enumerate((17, 18, 25, 33)):
        grid = np.tile(np.linspace(0, 255, m), (3, 1)).astype('<f4')
        cell = np.minimum(code * (m - 1) // 255, m - 2)
        numerator = code * (m - 1) - cell * 255
        fraction = ((numerator * 65536 + 127) // 255).astype('<u4')
        idx = np.tile(cell, (3, 1)).astype(np.uint8)
        frac = np.tile(fraction, (3, 1))
        nodes = rng.integers(0, 256, (m, m, m, 3), np.uint8)
        path = folder / f'stage{index + 1}-m{m}.slut'
        path.write_bytes(b'SLUT' + struct.pack('<III', 1, m, 0) + grid.tobytes()
            + idx.tobytes() + frac.astype('<u4').tobytes() + nodes.tobytes())
        rows.append({'path': str(path.resolve()), 'sha256': s.digest(path)})
        stages.append((m, idx, frac, nodes.reshape(-1, 3)))
    probes = rng.integers(0, 256, (65537, 3), np.uint8)
    probes[:8] = np.array([[r, g, b] for r in (0, 255) for g in (0, 255) for b in (0, 255)], np.uint8)
    truth = probes.copy()
    for m, idx, frac, nodes in stages:
        base = (idx[0, truth[:, 0]].astype(np.int64) * m + idx[1, truth[:, 1]]) * m + idx[2, truth[:, 2]]
        fractions = np.column_stack([frac[a, truth[:, a]] for a in range(3)]).astype(np.int64)
        strides = np.tile(np.array((m * m, m, 1), np.int64), (len(truth), 1))
        for a, b in ((0, 1), (1, 2), (0, 1)):
            swap = fractions[:, a] < fractions[:, b]
            fractions[swap, a], fractions[swap, b] = fractions[swap, b].copy(), fractions[swap, a].copy()
            strides[swap, a], strides[swap, b] = strides[swap, b].copy(), strides[swap, a].copy()
        weights = np.column_stack((65536 - fractions[:, 0], fractions[:, 0] - fractions[:, 1],
            fractions[:, 1] - fractions[:, 2], fractions[:, 2])).astype(np.uint64)
        indices = np.column_stack((base, base + strides[:, 0], base + strides[:, :2].sum(axis=1),
            base + m * m + m + 1))
        accumulator = np.sum(weights[:, :, None] * nodes[indices].astype(np.uint64), axis=1, dtype=np.uint64)
        assert np.all(weights.sum(axis=1) == 65536) and np.all(accumulator <= 255 * 65536)
        truth = ((accumulator + 32768) >> 16).astype(np.uint8)
    row = {'models': rows, 'sidecars': [None] * 4}
    comparisons = 0
    with library.create(row) as chain:
        state = s.diagnostics(chain)
        assert not state['direct']['enabled'] and not state['suffix_cache']['enabled']
        for backend in ('scalar', 'avx2'):
            if not library.supported(backend):
                continue
            for threads in (1, 4):
                for same in (False, True):
                    target = probes.copy() if same else np.empty_like(probes)
                    chain.apply(probes, target, backend, threads, same)
                    assert np.array_equal(target, truth), ('mixed_m', backend, threads, same)
                    comparisons += 1
        refusal = unsupported(chain, 'avx512', '固定混合m模型无direct资格；即使CPU支持亦拒绝')
    return {'models': rows, 'm': [17, 18, 25, 33], 'seed': 202610260103,
        'oracle': '独立uint64四凸权重，逐级RGB8 half-up；节点/坐标未按照片调整',
        'pixels': len(probes), 'source_sha256': s.sha(probes), 'expected_sha256': s.sha(truth),
        'backend_comparisons': comparisons, 'byte_mismatches': 0, 'state': state, 'no_direct_rejection': refusal}


def run(args, output):
    s.setup(args.dll_directory, args.cpus)
    plan = s.load_plan(args.plan)
    library = s.Library(args.library)
    assert library.revision == 102, '本工具只验证102统一库'
    environment = s.environment(args.build_receipt)
    environment['script_sha256'].update(s.script_records(__file__))
    executed = {'plan': plan, 'library': library.record(), 'backends': args.backends,
        'threads': args.threads, 'expected_pixels_hint': s.PIXELS,
        'environment': environment, 'finite_lengths': 21, 'finite_offsets': [0, 1, 7, 15, 31, 63],
        'finite_seed': 202610260102, 'mixed_m_seed': 202610260103,
        'scope': '同模型运行时逐字节一致性，不将零实现差异当作拟合ΔE；照片拟合误差沿独立模型研究。'}
    s.save(output / 'executed-plan.json', executed)
    generic = mixed_m_contract(library, output / 'mixed-m-contract')
    s.save(output / 'mixed-m-contract.json', generic)
    frames, photo_inputs = s.photos(plan)
    source_sha = s.sha(frames)
    records = []
    for name, row in plan['models'].items():
        cube = np.memmap(row['oracle']['path'], dtype=np.uint8, mode='r', shape=(1 << 24, 3))
        photo_expected = s.expected_photos(frames, cube)
        with library.create(row) as chain:
            state = s.diagnostics(chain)
            record = {'model': name, 'state': state, 'expected_full_sha256': row['oracle']['sha256'],
                'expected_photos': photo_expected, 'reject_calls': rejects(chain), 'backends': []}
            for backend in args.backends:
                if not library.supported(backend):
                    record['backends'].append(unsupported(chain, backend))
                    continue
                backend_row = {'backend': backend, 'executed': True, 'streams': [], 'photos': [], 'finite_cases': 0}
                for threads in args.threads:
                    backend_row['finite_cases'] += finite(chain, cube, backend, threads)
                    # 标量路径以边界合同覆盖，完整域针对本阶段SIMD入口。
                    if backend != 'scalar':
                        streams = {name: hashlib.sha256() for name in ('inplace', 'outplace')}
                        calls = 0
                        for begin in range(0, 1 << 24, 1 << 18):
                            code = np.arange(begin, begin + (1 << 18), dtype=np.uint32)
                            source = np.stack((code >> 16, (code >> 8) & 255, code & 255), axis=1).astype(np.uint8)
                            expected = cube[begin:begin + (1 << 18)]
                            for same in (True, False):
                                target = source.copy() if same else np.empty_like(source)
                                chain.apply(source, target, backend, threads, same)
                                assert np.array_equal(target, expected), (name, backend, threads, begin, same)
                                streams['inplace' if same else 'outplace'].update(memoryview(target).cast('B'))
                                calls += 1
                        hashes = {key: value.hexdigest() for key, value in streams.items()}
                        assert set(hashes.values()) == {row['oracle']['sha256']}
                        backend_row['streams'].append({'threads': threads, 'colors_per_stream': 1 << 24,
                            'byte_mismatches': 0, 'sha256': hashes, 'calls': calls})
                    for same in (True, False):
                        target = frames.copy() if same else np.empty_like(frames)
                        chain.apply(frames, target, backend, threads, same)
                        actual = s.sha(target)
                        assert actual == photo_expected['batch_sha256'], (name, backend, threads, same)
                        image_hashes = [s.sha(frame) for frame in target]
                        assert image_hashes == photo_expected['per_image_sha256']
                        backend_row['photos'].append({'threads': threads, 'inplace': same, 'images': 100,
                            'batch_sha256': actual, 'per_image_sha256': image_hashes})
                record['backends'].append(backend_row)
            records.append(record)
            assert s.sha(frames) == source_sha
            s.save(output / 'partial.json', {'models': records, 'source_sha256': source_sha})
            print('统一运行时完整域与百图通过：', name, flush=True)
    result = {'passed': True, 'library': library.record(), 'models': records, 'environment': environment,
        'mixed_m_contract': generic,
        'input_plan': plan['input_plan'], 'source_sha256': source_sha, 'photo_inputs': photo_inputs,
        'image_buffer_bytes': {'source': frames.nbytes, 'target': frames.nbytes},
        'scope': '固定模型、完整RGB8 SIMD流、真实100图逐字节与逐图SHA、有限偏移/尾部/哨兵及参数拒绝；未做OOM注入。'}
    s.save(output / 'correctness.json', result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library', type=Path, required=True)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--build-receipt', type=Path)
    parser.add_argument('--dll-directory')
    parser.add_argument('--cpus', default='0,2,4,6')
    parser.add_argument('--backends', nargs='+', choices=tuple(s.BACKENDS), default=['scalar', 'avx2', 'avx512'])
    parser.add_argument('--threads', nargs='+', type=int, default=[1, 4])
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('质量输出目录已存在，保留原件')
    args.output.mkdir(parents=True)
    try:
        run(args, args.output)
    except BaseException:
        s.save(args.output / 'failure.json', {'passed': False, 'traceback': traceback.format_exc()})
        raise


if __name__ == '__main__':
    main()
