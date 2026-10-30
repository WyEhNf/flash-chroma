"""92显式预计总像素：默认/阈值两侧完整域、有限/u64与失败回退合同。"""
from __future__ import annotations
import argparse
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import sys
import numpy as np
import psutil
from bench_p16_model_pair import checked, source
from study_p16_direct_compile import ROOT, Library, save, digest, env
from outplace_support import apply_to, reject_to, bind_to
from suffix_cache_support import cache_info, cache_table
from domain_cache_support import info as domain_info
from palette_support import info as palette_info
from direct16_support import info as direct_info
sys.path.insert(0, str(ROOT / 'python'))
from lutlab import channel_coordinates as cc, io
from verify_channel_coordinates import integer_oracle
from p16_workload_support import THRESHOLD, HintLibrary, bind_workload, workload_chain


def state(c):
    return {'cache': cache_info(c), 'domain': domain_info(c), 'palette': palette_info(c),
            'direct': direct_info(c), 'model_bytes': c.model_bytes}


def complete(reference, candidate):
    streams = {n: hashlib.sha256() for n in ('reference', 'scalar1', 'scalar4', 'avx1', 'avx4', 'out1', 'out4')}
    for begin in range(0, 1 << 24, 1 << 18):
        code = np.arange(begin, begin + (1 << 18), dtype=np.uint32)
        source = np.stack([code >> 16, (code >> 8) & 255, code & 255], axis=1).astype(np.uint8)
        truth = reference.apply(source.copy(), kernel='scalar', threads=1)
        streams['reference'].update(memoryview(truth).cast('B'))
        for kernel, prefix in (('scalar', 'scalar'), ('avx2', 'avx')):
            for threads in (1, 4):
                actual = candidate.apply(source.copy(), kernel=kernel, threads=threads)
                assert np.array_equal(actual, truth)
                streams[f'{prefix}{threads}'].update(memoryview(actual).cast('B'))
        raw = source.tobytes()
        for threads in (1, 4):
            actual = apply_to(candidate.library.dll, candidate.handle, raw, 1, threads)
            assert actual == truth.tobytes()
            streams[f'out{threads}'].update(actual)
    hashes = {n: h.hexdigest() for n, h in streams.items()}
    assert len(set(hashes.values())) == 1
    return {'colors': 1 << 24, 'byte_mismatches': 0, 'streams': hashes}


def finite(reference, candidate, source):
    truth = reference.apply(source.copy(), kernel='scalar', threads=1)
    count = 0
    for offset in (0, 1, 7, 15, 31, 63):
        for kernel in (0, 1):
            for threads in (1, 4):
                for same in (False, True):
                    got = apply_to(candidate.library.dll, candidate.handle, source.tobytes(),
                        kernel, threads, offset, 63 - offset, same)
                    assert got == truth.tobytes()
                    count += 1
    return count


def contracts(libs, folder, models, high_hint):
    rng = np.random.default_rng(202610240091)
    axis = np.rint(np.linspace(0, 255, 17)).astype(np.uint8)
    red, green, blue = np.meshgrid(axis, axis, axis, indexing='ij')
    identity = io.SparseLut(io.uniform_grid(17), np.stack([red, green, blue], axis=3))
    identity_path = folder / 'identity17.slut'
    io.save_sparse(identity_path, identity)
    identity_model = cc.from_sparse(io.load_sparse(identity_path, competition=True))
    gray = io.SparseLut(io.uniform_grid(17), np.repeat(red[..., None], 3, axis=3))
    gray_path = folder / 'gray17.slut'
    io.save_sparse(gray_path, gray)
    gray_model = cc.from_sparse(io.load_sparse(gray_path, competition=True))
    # 固定身份后缀使缓存有>255种输出；不得换seed或改模型使门禁通过。
    cases = [('over255_palette', [gray_path, identity_path, identity_path, identity_path], [None] * 4,
              [gray_model, identity_model, identity_model, identity_model], False)]
    mixed = cc.from_sparse(io.load_sparse(identity_path, competition=True))
    for channel, power in enumerate((1., 1.125, .875)):
        mixed.channel_frac[channel] = np.rint(65536 * (mixed.channel_frac[channel] / 65536.) ** power).astype(np.uint32)
    mixed.channel_frac[:, :, 0] = 0
    mixed.channel_frac[:, :, 255] = 65536
    cc.validate(mixed)
    mixed_side = folder / 'mixed-suffix.bin'
    mixed.channel_frac.astype('<u4').tofile(mixed_side)
    cases.append(('mixed_suffix', [gray_path, identity_path, identity_path, identity_path],
                  [None, mixed_side, None, None], [gray_model, mixed, identity_model, identity_model], False))
    ordinary = [io.load_sparse(checked(row), competition=True) for row in models['models']]
    equal = cc.from_sparse(ordinary[0])
    for axis_index in range(3):
        frac = np.rint(65536 * (equal.channel_frac[0, axis_index] / 65536.) ** 1.125).astype(np.uint32)
        equal.channel_frac[:, axis_index] = frac
    equal.channel_frac[:, :, 0] = 0
    equal.channel_frac[:, :, 255] = 65536
    cc.validate(equal)
    assert not np.array_equal(equal.channel_frac[0], cc.from_sparse(ordinary[0]).channel_frac[0])
    equal_side = folder / 'changed-equal-side.bin'
    equal.channel_frac.astype('<u4').tofile(equal_side)
    paths = [checked(row) for row in models['models']]
    cases.append(('changed_equal_sidecar', paths, [equal_side, None, None, None],
                  [equal, *[cc.from_sparse(s) for s in ordinary[1:]]], True))
    cases.append(('single_shared', paths[:1], [None], [cc.from_sparse(ordinary[0])], False))
    for m in (17, 18, 25, 33):
        nodes = np.repeat(rng.integers(120, 129, (m, m, m), np.uint8)[..., None], 3, axis=3)
        path = folder / f'signed-gray{m}.slut'
        io.save_sparse(path, io.SparseLut(io.uniform_grid(m), nodes))
        model = cc.from_sparse(io.load_sparse(path, competition=True))
        cases.append((f'shared_signed_m{m}', [path, identity_path, identity_path, identity_path], [None] * 4,
                      [model, identity_model, identity_model, identity_model], True))
    probes = np.concatenate([rng.integers(0, 256, (8192, 3), np.uint8),
        np.array([[r, g, b] for r in (0, 255) for g in (0, 255) for b in (0, 255)], np.uint8)])
    records = []
    for name, paths, sides, truth_models, expected_direct in cases:
        expected_direct = expected_direct and high_hint
        truth = probes.copy()
        for model in truth_models:
            truth = integer_oracle(model, truth)
        with libs['reference'].chain(paths, sides) as a, libs['candidate'].chain(paths, sides) as b:
            states = {'reference': state(a), 'candidate': state(b)}
            assert bool(states['candidate']['direct']['enabled']) == expected_direct
            assert not states['candidate']['domain']['fast_path_enabled']
            if not expected_direct:
                assert a.model_bytes == b.model_bytes
            if name == 'over255_palette':
                unique_count = int(np.unique(cache_table(a, cache_info(a))).size)
                assert unique_count > 255
            else:
                unique_count = None
            checks = 0
            for kernel in (0, 1):
                for threads in (1, 4):
                    actual = b.apply(probes.copy(), kernel='avx2' if kernel else 'scalar', threads=threads)
                    assert np.array_equal(actual, truth)
                    raw = apply_to(b.library.dll, b.handle, probes.tobytes(), kernel, threads, 1, 62, False)
                    assert raw == truth.tobytes()
                    checks += 2
            records.append({'case': name, 'state': states, 'expected_direct': expected_direct,
                'oracle_pixels': len(probes), 'backend_comparisons': checks, 'byte_mismatches': 0,
                'over255_cache_unique_count': unique_count})
    return records


def photos(libs, plan):
    frames, manifest = source(json.loads(checked(plan['photo_model_plan']).read_text(encoding='utf-8')))
    source_sha = hashlib.sha256(memoryview(frames).cast('B')).hexdigest()
    assert source_sha == plan['photo_source_sha256']
    work = np.empty_like(frames)
    records, expected_rows = [], []
    u8 = ct.POINTER(ct.c_uint8)
    for role, model in plan['models'].items():
        paths = [checked(row) for row in model['models']]
        sides = [checked(row) if row else None for row in model['sidecars']]
        with libs['reference'].chain(paths, sides) as a:
            truth = a.apply(frames.copy(), kernel='scalar', threads=1)
        assert hashlib.sha256(memoryview(truth).cast('B')).hexdigest() == plan['expected_photo_sha256'][role]
        for images in plan['photo_images']:
            inputs, output = frames[:images], work[:images]
            expected = hashlib.sha256(memoryview(truth[:images]).cast('B')).hexdigest()
            expected_rows.append({'role': role, 'images': images, 'output_sha256': expected,
                'scope': '同场87 scalar1实际输出前缀；100图聚合与既有独立完整域真值的照片期望SHA相等。'})
            hint = images * 768 * 1024
            with workload_chain(libs['candidate'], paths, sides, expected_pixels=hint) as c:
                bind_to(c.library.dll)
                assert bool(direct_info(c)['enabled']) == (role == 'anchor' or hint >= THRESHOLD)
                for threads in (1, 4):
                    for separate in (False, True):
                        if separate:
                            output.fill(173)
                            error = ct.create_string_buffer(1024)
                            rc = c.library.dll.jshc_cc_apply_to(c.handle, inputs.ctypes.data_as(u8),
                                output.ctypes.data_as(u8), inputs.nbytes, 1, threads, error, len(error))
                            assert rc == 0, error.value
                        else:
                            output[:] = inputs
                            c.apply(output, kernel='avx2', threads=threads)
                        actual = hashlib.sha256(memoryview(output).cast('B')).hexdigest()
                        assert actual == expected
                        records.append({'role': role, 'images': images, 'expected_pixels': hint,
                            'threads': threads, 'separate': separate, 'actual_sha256': actual})
        del truth
    assert hashlib.sha256(memoryview(frames).cast('B')).hexdigest() == source_sha
    return {'actual': records, 'expected': expected_rows}


def argument_contracts(library):
    bind_workload(library)
    rejects = []
    # 包装在解析路径之前拒绝隐式ctypes转换，不会构造任何原生句柄。
    for value in (False, True, -1, 1 << 64, 0., float('inf'), '67108864', None, np.int64(1), np.uint64(1)):
        try:
            workload_chain(library, [], expected_pixels=value)
        except ValueError as error:
            assert 'Python int' in str(error)
            rejects.append({'type': type(value).__name__, 'value': repr(value), 'message': str(error)})
        else:
            raise AssertionError('包装应拒绝非合同类型')
    native = []
    for hint in (0, THRESHOLD - 1, THRESHOLD, THRESHOLD + 1, (1 << 64) - 1):
        for stages in (0, 5):
            handle, error = ct.c_void_p(1), ct.create_string_buffer(1024)
            rc = library.dll.jshc_cc_create_for_workload(None, None, stages, hint,
                ct.byref(handle), error, len(error))
            assert rc != 0 and not handle.value
            native.append({'expected_pixels': hint, 'stages': stages, 'return_code': rc,
                'output_null': True, 'message': error.value.decode('utf-8')})
    return {'typed_rejects': rejects, 'native_unsigned_invalid_arguments': native,
        'scope': 'C ABI接收uint64，无法检测调用者此前有符号转换意图；Python包装额外拒绝隐式转换。'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    plan = json.loads(args.plan.read_text(encoding='utf-8'))
    assert digest(Path(__file__)) == plan['script_sha256']
    for row in plan['sources']:
        checked(row)
    if args.output.exists():
        raise FileExistsError('保留首次质量证据')
    args.output.mkdir(parents=True)
    psutil.Process().cpu_affinity(plan['cpus'])
    directory = os.add_dll_directory('E:/mingw64/bin') if os.name == 'nt' else None
    libs = {k: Library(checked(v), v['sha256']) for k, v in plan['libraries'].items()}
    assert libs['reference'].revision == 87 and libs['candidate'].revision == 92
    bind_workload(libs['candidate'])
    full, finite_cases, states = {}, {}, {}
    rng = np.random.default_rng(202610240091)
    for role, model in plan['models'].items():
        paths = [checked(row) for row in model['models']]
        sides = [checked(row) if row else None for row in model['sidecars']]
        states[role], full[role], finite_cases[role] = {}, {}, {}
        with libs['reference'].chain(paths, sides) as a:
            for name, hint in (('default', None), ('below', THRESHOLD - 1), ('at', THRESHOLD)):
                c = libs['candidate'].chain(paths, sides) if hint is None else workload_chain(
                    libs['candidate'], paths, sides, expected_pixels=hint)
                with c as b:
                    snapshot = state(b)
                    expected_direct = role == 'anchor' or (hint is not None and hint >= THRESHOLD)
                    assert bool(snapshot['direct']['enabled']) == expected_direct
                    assert b.model_bytes == a.model_bytes + ((1 << 24) if role == 'ordinary' and expected_direct else 0)
                    states[role][name] = snapshot
                    full[role][name] = complete(a, b)
                    assert full[role][name]['streams']['reference'] == plan['expected_full_sha256'][role]
                    print('92固定链完整RGB8通过', role, name, flush=True)
            for hint in (0, THRESHOLD - 1, THRESHOLD, THRESHOLD + 1, (1 << 64) - 1):
                with workload_chain(libs['candidate'], paths, sides, expected_pixels=hint) as b:
                    expected_direct = role == 'anchor' or hint >= THRESHOLD
                    assert bool(direct_info(b)['enabled']) == expected_direct
                    finite_cases[role][str(hint)] = {
                        'comparisons': sum(finite(a, b, rng.integers(0, 256, (n, 3), np.uint8)) for n in plan['lengths']),
                        'rejects': reject_to(b.library.dll, b.handle), 'state': state(b)}
    cases = {}
    for name, hint in (('low', THRESHOLD - 1), ('high', THRESHOLD)):
        folder = args.output / name
        folder.mkdir()
        views = {'reference': libs['reference'], 'candidate': HintLibrary(libs['candidate'], hint)}
        cases[name] = contracts(views, folder, plan['models']['ordinary'], hint >= THRESHOLD)
    arguments = argument_contracts(libs['candidate'])
    photo_checks = photos(libs, plan)
    save(args.output / 'correctness.json', {'passed': True, 'full': full, 'states': states,
        'finite_cases': finite_cases, 'contracts': cases, 'arguments': arguments, 'photos': photo_checks,
        'libraries': plan['libraries'], 'environment': env(),
        'scope': '两模型默认/阈值下/恰阈值各完整RGB8；五个unsigned hint有限/资格/容量；低高hint各八个独立u64合同；10个typed拒绝；无AVX2硬件及分配失败未故障注入，未拟合/计性能。'})
    save(args.output / 'executed-plan.json', plan)
    print('92全部质量通过；未执行性能计时', flush=True)


if __name__ == '__main__':
    main()
