"""集中核验坐标差打包：int16两边界、越界回退、混合链及尾部，独立u64逐字节比较，不测性能。"""
from __future__ import annotations
import argparse
import ctypes as ct
from pathlib import Path
import zipfile
import numpy as np
from skylake_support import build_libraries, claim, digest, read, save, unchanged
from delta16_support import bind, layouts
from restrict_support import info as domain_info
from lutlab import channel_coordinates as cc, io
from verify_channel_coordinates import integer_oracle


def profile(model, kind):
    result = cc.from_sparse(model)
    middle = {'bounds': (32768, 0, 65535), 'over_positive': (32768, 65536, 65535),
              'over_negative': (32769, 0, 65535)}[kind]
    for axis in range(3):
        # 不同轴交换上下半字的极值，分别覆盖低/高字段的-32768与+32767。
        axis_middle = (middle[0], middle[2], middle[1]) if kind == 'bounds' and axis == 1 else middle
        for cell in np.unique(result.idx[axis]):
            codes = np.flatnonzero(result.idx[axis] == cell)
            part = np.minimum(np.arange(len(codes))*3//len(codes), 2)
            for c in range(3):
                result.channel_frac[c, axis, codes] = np.array([0, axis_middle[c], 65536], np.uint32)[part]
    result.channel_frac[:, :, 0] = 0; result.channel_frac[:, :, 255] = 65536
    cc.validate(result)
    difference = result.channel_frac[1:].astype(np.int64)-result.channel_frac[:1].astype(np.int64)
    if kind == 'bounds':
        assert difference.min() == -32768 and difference.max() == 32767
    elif kind == 'over_positive':
        assert difference.max() == 32768
    else:
        assert difference.min() == -32769
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('plan', 'build', 'contract', 'output'):
        p.add_argument('--'+name, type=Path, required=True)
    args = p.parse_args()
    plan, build, libraries, loaded = build_libraries(args.plan, args.build)
    contract = read(args.contract)
    if not contract['pass'] or contract['build_sha256'] != digest(args.build/'build.json'):
        raise ValueError('需要同一构建的原有集中合同')
    out, identity = claim(args.output, args.plan,
        [*plan['source_sha256'], 'scripts/verify_skylake_delta16.py', 'scripts/delta16_support.py',
         'scripts/verify_channel_coordinates.py', 'python/lutlab/channel_coordinates.py', 'python/lutlab/io.py'],
        {'purpose': __doc__, 'build_sha256': digest(args.build/'build.json'), 'loaded_libraries': loaded})
    paths = [args.contract.parent/f'model{s}.slut' for s in range(4)]
    ordinary = [cc.from_sparse(io.load_sparse(path, competition=True)) for path in paths]
    models = {}; sides = {}
    for kind in ('bounds', 'over_positive', 'over_negative'):
        models[kind] = []; sides[kind] = []
        for s, path in enumerate(paths):
            changed = profile(io.load_sparse(path, competition=True), kind)
            side = out/f'{kind}-{s}.bin'; changed.channel_frac.astype('<u4').tofile(side)
            models[kind].append(changed); sides[kind].append(side)
    equal = cc.from_sparse(io.load_sparse(paths[0], competition=True))
    equal.channel_frac[:] = models['bounds'][0].channel_frac[0]
    cc.validate(equal); assert not np.array_equal(equal.channel_frac, ordinary[0].channel_frac)
    equal_side = out/'equal-changed.bin'; equal.channel_frac.astype('<u4').tofile(equal_side)
    bounded = models['bounds']; bs = sides['bounds']
    cases = [
        ('delta_single_bounds', paths[:1], bs[:1], bounded[:1], [2]),
        ('delta_shared_shared_shared', paths, [bs[0], None, None, None], [bounded[0], *ordinary[1:]], [2, 1, 1, 1]),
        ('three_delta', paths[:3], bs[:3], bounded[:3], [2, 2, 2]),
        ('shared_delta_shared_delta', paths, [None, bs[1], None, bs[3]], [ordinary[0], bounded[1], ordinary[2], bounded[3]], [1, 2, 1, 2]),
        ('delta_unpacked_shared_delta', paths, [bs[0], sides['over_positive'][1], None, bs[3]], [bounded[0], models['over_positive'][1], ordinary[2], bounded[3]], [2, 0, 1, 2]),
        ('over_positive_single', paths[:1], sides['over_positive'][:1], models['over_positive'][:1], [0]),
        ('over_negative_single', paths[:1], sides['over_negative'][:1], models['over_negative'][:1], [0]),
        ('equal_changed_shared', paths, [equal_side, None, None, None], [equal, *ordinary[1:]], [1, 1, 1, 1])]
    rng = np.random.default_rng(plan['delta16_policy']['contract_seed'])
    anchors = np.array([[r, g, b] for r in (0, 255) for g in (0, 255) for b in (0, 255)], np.uint8)
    codes = np.column_stack([np.roll(np.arange(256), shift) for shift in range(3)]).astype(np.uint8)
    probes = np.concatenate([anchors, codes]); records = []; accounting = []; negative_checks = 0
    for label, model_paths, side_paths, chain_models, expected_flags in cases:
        handles = {name: lib.chain(model_paths, side_paths) for name, lib in libraries.items()}
        try:
            flags = layouts(handles['candidate'])
            if flags != expected_flags:
                raise AssertionError('实际压缩/回退布局不同：'+label+str(flags))
            memory = {name: h.model_bytes for name, h in handles.items()}
            if plan.get('reference_delta16', False):
                assert layouts(handles['reference']) == expected_flags
                if 'restrict_policy' in plan:
                    domains=domain_info(handles['candidate'])
                    assert domains and memory['candidate']-memory['reference']==domains['extra_model_bytes']
                else:
                    assert memory['reference'] == memory['candidate']
            else:
                assert memory['reference']-memory['candidate'] == expected_flags.count(2)*3072
            accounting.append({'fixture': label, 'layouts': flags, 'model_accounting_bytes': memory})
            h = handles['candidate']; d = bind(h); n = len(model_paths)
            storage = (ct.c_uint32*(n+2))(*([0xa7a7a7a7]*(n+2)))
            before = bytes(storage)
            assert d.jshc_cc_get_layouts(h.handle, storage, n+1) == 1 and bytes(storage) == before
            assert d.jshc_cc_get_layouts(h.handle, storage, n-1) == 1 and bytes(storage) == before
            assert d.jshc_cc_get_layouts(None, storage, n) == 1 and bytes(storage) == before
            assert d.jshc_cc_get_layouts(h.handle, None, n) == 1
            negative_checks += 4
            for length in plan['contract']['lengths']:
                source = rng.integers(0, 256, (length, 3), np.uint8)
                source[:min(length, len(probes))] = probes[:min(length, len(probes))]
                truth = source.copy()
                for model in chain_models:
                    truth = integer_oracle(model, truth)
                for name, handle in handles.items():
                    for kernel, threads in plan['contract']['backend_threads']:
                        for offset in plan['contract']['byte_offsets']:
                            storage = np.full(offset+length*3+17, 0xa7, np.uint8)
                            actual = storage[offset:offset+length*3].reshape(length, 3); actual[:] = source
                            handle.apply(actual, kernel=kernel, threads=threads)
                            np.testing.assert_array_equal(actual, truth)
                            assert np.all(storage[:offset] == 0xa7) and np.all(storage[offset+length*3:] == 0xa7)
                records.append({'fixture': label, 'pixels': length, 'layouts': flags,
                                'byte_mismatches': 0, 'sentinel_mismatches': 0})
        finally:
            for handle in handles.values():
                handle.close()
    unchanged(identity)
    fixtures = [*paths, *sorted(out.glob('*.bin'))]
    fixture_sha256 = {str(path.resolve()): digest(path) for path in fixtures}
    with zipfile.ZipFile(out/'fixtures.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in fixtures:
            archive.write(path, ('base/' if path in paths else 'sidecars/')+path.name)
    save(out/'results.json', {'pass': True, 'purpose': __doc__, 'build_sha256': digest(args.build/'build.json'),
        'plan_sha256': digest(args.plan), 'libraries': build['libraries'], 'base_contract_sha256': digest(args.contract),
        'layout_length_cases': len(records), 'cases': records, 'layout_memory_checks': accounting,
        'diagnostic_negative_checks': negative_checks, 'performance_calls': 0, 'new_fits': 0,
        'fixture_sha256': fixture_sha256,
        'scope': '有限整数编码/布局合同；不替代实际完整色域、百图、Skylake实机或性能。'})
    print('有符号坐标差集中合同通过：', len(records), '组；失败只读诊断：', negative_checks, flush=True)


if __name__ == '__main__':
    main()
