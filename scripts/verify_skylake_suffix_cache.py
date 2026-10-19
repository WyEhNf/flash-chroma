"""集中验证有界缓存：每个合法表槽的独立整数oracle、混合命中、尾部及只读ABI，不测性能。"""
from __future__ import annotations
import argparse
import ctypes as ct
from pathlib import Path
import numpy as np
from skylake_support import build_libraries, claim, digest, save, unchanged
from suffix_cache_support import CacheInfo, bind, cache_info, cache_table, hit_mask
from lutlab import channel_coordinates as cc, io
from verify_channel_coordinates import integer_oracle


def altered(model):
    result = cc.from_sparse(model)
    for a in range(3):
        for cell in np.unique(result.idx[a]):
            ids = np.flatnonzero(result.idx[a] == cell)
            t = np.linspace(0, 1, len(ids))
            for c, power in enumerate((1, 8, .125)):
                result.channel_frac[c, a, ids] = np.rint(65536*t**power).astype(np.uint32)
    result.channel_frac[:, :, 0] = 0; result.channel_frac[:, :, 255] = 65536
    cc.validate(result)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('plan', 'build', 'contract', 'output'):
        p.add_argument('--'+name, type=Path, required=True)
    args = p.parse_args()
    plan, build, libraries, loaded = build_libraries(args.plan, args.build)
    import json
    contract = json.loads(args.contract.read_text(encoding='utf-8'))
    if not contract['pass'] or contract['build_sha256'] != digest(args.build/'build.json'):
        raise ValueError('需要同一构建的既有集中合同')
    names = [*plan['source_sha256'], 'scripts/verify_skylake_suffix_cache.py', 'scripts/suffix_cache_support.py',
             'scripts/verify_channel_coordinates.py', 'python/lutlab/io.py', 'python/lutlab/channel_coordinates.py']
    out, identity = claim(args.output, args.plan, names,
        {'purpose': __doc__, 'loaded_libraries': loaded, 'build_sha256': digest(args.build/'build.json')})
    rng = np.random.default_rng(plan['cache_policy']['contract_seed'])
    paths = []; ordinary = []; side_paths = []; extended = []
    for stage, m in enumerate((17, 18, 25, 33)):
        if stage == 0:
            axis = np.arange(m, dtype=np.float64)
            grey = np.rint(32+191*(axis[:, None, None]+axis[None, :, None]+axis[None, None, :])/(3*(m-1))).astype(np.uint8)
            nodes = np.repeat(grey[..., None], 3, axis=-1)
        else:
            nodes = rng.integers(0, 256, (m, m, m, 3), np.uint8)
        path = out/f'model{stage}.slut'; io.save_sparse(path, io.SparseLut(io.uniform_grid(m), nodes))
        model = io.load_sparse(path, competition=True); changed = altered(model)
        side = out/f'side{stage}.bin'; changed.channel_frac.astype('<u4').tofile(side)
        paths.append(path); ordinary.append(cc.from_sparse(model)); extended.append(changed); side_paths.append(side)
    equal = cc.from_sparse(io.load_sparse(paths[0], competition=True)); equal.channel_frac[:] = extended[0].channel_frac[0]
    equal_path = out/'equal-changed.bin'; equal.channel_frac.astype('<u4').tofile(equal_path); cc.validate(equal)
    cases = [
        ('shared_shared', [None]*4, ordinary, False),
        ('unshared_shared', [side_paths[0], None, None, None], [extended[0], *ordinary[1:]], True),
        ('shared_mixed', [None, side_paths[1], None, side_paths[3]], [ordinary[0], extended[1], ordinary[2], extended[3]], False),
        ('unshared_mixed', side_paths, extended, True),
        ('equal_changed_shared', [equal_path, None, None, None], [equal, *ordinary[1:]], False)]
    probes = rng.integers(0, 256, (8192, 3), np.uint8)
    records = []; slots = []; diagnostic_checks = 0
    for label, sides, models, mixed in cases:
        handles = {name: lib.chain(paths, sides) for name, lib in libraries.items()}
        try:
            h = handles['candidate']; info = cache_info(h)
            if not info or not info['enabled'] or info['table_capacity_bytes'] > 1048576:
                raise AssertionError('窄带样例未在固定预算内启用')
            axes = [np.arange(info[a], info[b]+1, dtype=np.int32) for a, b in
                    [('r_min', 'r_max'), ('dg_min', 'dg_max'), ('db_min', 'db_max')]]
            r, dg, db = np.meshgrid(*axes, indexing='ij')
            colours = np.column_stack((r.ravel(), (r+dg).ravel(), (r+db).ravel()))
            valid = ((colours >= 0) & (colours <= 255)).all(axis=1)
            truth = colours[valid].astype(np.uint8)
            for model in models[1:]:
                truth = integer_oracle(model, truth)
            packed = truth[:, 0].astype(np.uint32) | (truth[:, 1].astype(np.uint32) << 8) | (truth[:, 2].astype(np.uint32) << 16)
            table = cache_table(h, info)
            np.testing.assert_array_equal(table[valid], packed)
            if np.any(table[~valid]) or int(valid.sum()) != info['valid_entries']:
                raise AssertionError('非法颜色槽隔离或槽计数不符')
            # 失败ABI调用不得改写调用者缓冲区，包括错误长度与空句柄。
            d = bind(h); raw = CacheInfo(); ct.memset(ct.byref(raw), 0xa7, ct.sizeof(raw)); before = bytes(raw)
            assert d.jshc_cc_get_cache_info(h.handle, ct.byref(raw), ct.sizeof(raw)-1) == 1 and bytes(raw) == before
            assert d.jshc_cc_get_cache_info(None, ct.byref(raw), ct.sizeof(raw)) == 1 and bytes(raw) == before
            guard = np.full(len(table)+2, 0xa7a7a7a7, np.uint32)
            assert d.jshc_cc_copy_cache(h.handle, guard.ctypes.data_as(ct.POINTER(ct.c_uint32)), len(table)+1) == 1
            assert np.all(guard == 0xa7a7a7a7)
            assert d.jshc_cc_copy_cache(h.handle, None, len(table)) == 1
            diagnostic_checks += 4
            slots.append({'fixture': label, 'cache_info': info, 'legal_slots_checked': int(valid.sum()),
                          'invalid_slots_zero': int((~valid).sum()), 'oracle_mismatches': 0})
            first = integer_oracle(models[0], probes); hits = hit_mask(first, info)
            if not hits.any() or (mixed and hits.all()) or (not mixed and not hits.all()):
                raise AssertionError('合成命中/未命中覆盖不符合冻结预期')
            hit = probes[np.flatnonzero(hits)[0]]
            packet = np.repeat(hit[None, :], 8, axis=0)
            if mixed:
                packet[-1] = probes[np.flatnonzero(~hits)[0]]
                assert hit_mask(integer_oracle(models[0], packet), info).sum() == 7
            for length in plan['contract']['lengths']:
                source = np.resize(packet, (length, 3)).astype(np.uint8)
                truth = source.copy()
                for model in models:
                    truth = integer_oracle(model, truth)
                for name, handle in handles.items():
                    for kernel, threads in plan['contract']['backend_threads']:
                        for offset in plan['contract']['byte_offsets']:
                            storage = np.full(offset+length*3+17, 0xa7, np.uint8)
                            actual = storage[offset:offset+length*3].reshape(length, 3); actual[:] = source
                            handle.apply(actual, kernel=kernel, threads=threads)
                            np.testing.assert_array_equal(actual, truth)
                            assert np.all(storage[:offset] == 0xa7) and np.all(storage[offset+length*3:] == 0xa7)
                records.append({'fixture': label, 'pixels': length, 'packet_pixel_hits': 7 if mixed else 8,
                                'byte_mismatches': 0, 'sentinel_mismatches': 0})
        finally:
            for handle in handles.values():
                handle.close()
    # 宽输出的四级模型必须触发预算回退；不足四级不得构建缓存。
    disabled = []
    for count in (1, 4):
        model_paths = [out/f'model{i}.slut' for i in range(count)]
        if count == 4:
            wide = io.SparseLut(io.uniform_grid(17), rng.integers(0, 256, (17, 17, 17, 3), np.uint8))
            path = out/'wide.slut'; io.save_sparse(path, wide); model_paths[0] = path
        with libraries['candidate'].chain(model_paths) as handle:
            info = cache_info(handle)
            assert not info['enabled'] and info['entries'] == 0 and info['reason'] == (1 if count == 1 else 2)
            assert cache_table(handle, info).size == 0
            disabled.append(info)
    unchanged(identity)
    result = {'pass': True, 'purpose': __doc__, 'plan_sha256': digest(args.plan),
        'build_sha256': digest(args.build/'build.json'), 'libraries': build['libraries'],
        'base_contract_sha256': digest(args.contract), 'cache_entry_audits': slots,
        'cache_layout_length_cases': len(records), 'cases': records, 'disabled_cache_cases': disabled,
        'diagnostic_negative_checks': diagnostic_checks, 'performance_calls': 0, 'new_fits': 0,
        'limits': '有限缓存合同；完整实际模型/百图及性能仍需分别验收，未在Skylake实机执行。'}
    save(out/'results.json', result)
    print('缓存集中合同通过：', len(records), '组；表槽：', sum(v['legal_slots_checked'] for v in slots), flush=True)


if __name__ == '__main__':
    main()
