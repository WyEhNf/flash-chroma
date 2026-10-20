"""冻结a399模型的完整色域/百图原生等价；复用已验精度，不重新拟合或计时。"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
import numpy as np
from PIL import Image
from skylake_support import ROOT, build_libraries, checked, claim, digest, read, save, unchanged
from lutlab import channel_coordinates as cc, io
from suffix_cache_support import cache_info, cache_table, coverage
from delta16_support import layouts
from axis_preweight_support import formats as axis_formats
from restrict_support import info as domain_info
from cache_encoding_support import info as encoding_info
from verify_channel_coordinates import integer_oracle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--contract', type=Path, required=True)
    parser.add_argument('--cache-contract', type=Path)
    parser.add_argument('--layout-contract', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    plan, build, libraries, loaded = build_libraries(args.plan, args.build)
    contract = read(args.contract)
    if (not contract['pass'] or contract['build_sha256'] != digest(args.build/'build.json')
            or contract['libraries'] != build['libraries']):
        raise ValueError('有限合同未通过或不是相同构建')
    cache_contract = None
    layout_contract = None
    if 'delta16_policy' in plan:
        if args.layout_contract is None:
            raise ValueError('坐标差候选需要边界/布局集中合同')
        layout_contract = read(args.layout_contract)
        if (not layout_contract['pass'] or layout_contract['build_sha256'] != digest(args.build/'build.json')
                or layout_contract['libraries'] != build['libraries']):
            raise ValueError('坐标差集中合同不是相同构建')
    if 'cache_policy' in plan:
        if args.cache_contract is None:
            raise ValueError('缓存候选需要单独表槽与命中合同')
        cache_contract = read(args.cache_contract)
        if (not cache_contract['pass'] or cache_contract['build_sha256'] != digest(args.build/'build.json')
                or cache_contract['libraries'] != build['libraries']):
            raise ValueError('缓存合同与构建不同')
    paths = {k: checked(v) for k, v in plan['fixed_inputs'].items()}
    prior = read(paths['prior_full'])
    if not prior['acceptance']['accepted'] or prior['acceptance']['failed'] or not prior['native']['pass']:
        raise ValueError('原精度验收未通过')
    if prior['cube']['prediction_sha256'] != plan['fixed_inputs']['cube']['sha256']:
        raise ValueError('既有完整oracle流身份不符')
    suffix = [checked(s) for s in plan['suffix_models']]
    data = np.load(paths['model'])
    model = cc.ChannelLut(data['grid'], data['nodes'], data['shared_idx'], data['channel_frac'])
    cc.validate(model)
    expected = np.memmap(paths['cube'], np.uint8, 'r', shape=(256**3, 3))
    out, identity = claim(args.output, args.plan,
        [*plan['source_sha256'], 'scripts/accept_skylake_runtime.py', 'scripts/verify_skylake_packed.py',
         'scripts/verify_channel_coordinates.py', 'scripts/suffix_cache_support.py',
         'scripts/delta16_support.py',
         'scripts/axis_preweight_support.py',
         'scripts/restrict_support.py',
         'scripts/cache_encoding_support.py',
         'python/lutlab/channel_coordinates.py', 'python/lutlab/io.py'],
        {'purpose': __doc__, 'build_sha256': digest(args.build/'build.json'),
         'contract_sha256': digest(args.contract), 'loaded_libraries': loaded})
    operators = {}; hashes = {}; photos = []; photos_hash = {name: hashlib.sha256() for name in libraries}
    memory = {}; cache_record = None; first_stream = None; layout_record = None; axis_record = None; domain_record = None; encoding_record = None
    try:
        for name, lib in libraries.items():
            operators[name] = {
                'single': lib.chain([paths['base']], [paths['sidecar']]),
                'chain': lib.chain([paths['base'], *suffix], [paths['sidecar'], None, None, None])}
            memory[name] = {mode: h.model_bytes for mode, h in operators[name].items()}
            hashes[name] = {mode+'_'+kernel: hashlib.sha256() for mode in ('single', 'chain') for kernel in ('scalar', 'avx2')}
        if layout_contract is not None:
            layout_record = {'contract_sha256': digest(args.layout_contract),
                'candidate': {mode: layouts(h) for mode, h in operators['candidate'].items()}}
            if (layout_record['candidate']['single'] != [2]
                    or layout_record['candidate']['chain'] != plan['delta16_policy']['actual_chain_layouts']):
                raise AssertionError('实际模型未使用冻结的有符号差布局')
        if 'axis_preweight_policy' in plan:
            axis_record={name:{mode:axis_formats(h) for mode,h in group.items()} for name,group in operators.items()}
            if axis_record['candidate']!={'single':[0],'chain':plan['axis_preweight_policy']['actual_chain_formats']}:
                raise AssertionError('实际模型未使用冻结的共享轴预计算')
            if memory['candidate']['single']!=memory['reference']['single'] or memory['candidate']['chain']-memory['reference']['chain']!=9216:
                raise AssertionError('实际模型的派生轴容量与三份3072字节不符')
        if 'restrict_policy' in plan:
            domain_record={mode:domain_info(h) for mode,h in operators['candidate'].items()}
            for mode,details in domain_record.items():
                if details is None or memory['candidate'][mode]-memory['reference'][mode]!=details['extra_model_bytes']:
                    raise AssertionError('实际模型读取域容量核算不同')
        if cache_contract is not None:
            handle = operators['candidate']['chain']; info = cache_info(handle)
            if 'compact_cache_policy' in plan:
                encoding_record={mode:encoding_info(h) for mode,h in operators['candidate'].items()}
                if encoding_record['single']['format']!=0 or encoding_record['chain']['format']!=1:
                    raise AssertionError('实际单级/四级编码状态不同')
                old=cache_info(operators['reference']['chain'])
                if memory['candidate']['single']-memory['reference']['single']!=16 or memory['candidate']['chain']-memory['reference']['chain']!=16+info['table_capacity_bytes']-old['table_capacity_bytes']:
                    raise AssertionError('实际编码容量不符合独立头/载荷核算')
            if not info or not info['enabled'] or info['table_capacity_bytes'] > plan['cache_policy']['budget_bytes']:
                raise AssertionError('实际模型未按冻结容量政策启用缓存')
            axes = [np.arange(info[a], info[b]+1, dtype=np.int32) for a, b in
                    [('r_min', 'r_max'), ('dg_min', 'dg_max'), ('db_min', 'db_max')]]
            r, dg, db = np.meshgrid(*axes, indexing='ij')
            colours = np.column_stack((r.ravel(), (r+dg).ravel(), (r+db).ravel()))
            valid = ((colours >= 0) & (colours <= 255)).all(axis=1)
            truth = colours[valid].astype(np.uint8)
            for path in suffix:
                truth = integer_oracle(cc.from_sparse(io.load_sparse(path, competition=True)), truth)
            packed = truth[:, 0].astype(np.uint32) | (truth[:, 1].astype(np.uint32) << 8) | (truth[:, 2].astype(np.uint32) << 16)
            table = cache_table(handle, info)
            np.testing.assert_array_equal(table[valid], packed)
            if np.any(table[~valid]) or int(valid.sum()) != info['valid_entries']:
                raise AssertionError('实际模型的缓存非法槽隔离或计数错误')
            cache_record = {'info': info, 'cache_contract_sha256': digest(args.cache_contract),
                'legal_slots_independent_u64_checked': int(valid.sum()), 'invalid_slots_zero': int((~valid).sum()),
                'entry_byte_mismatches': 0, 'cube_coverage': {}, 'photos_coverage': {}}
            first_stream = np.memmap(out/'first-stage.rgb', np.uint8, 'w+', shape=(256**3, 3))
        single_hash = hashlib.sha256()
        for start in range(0, 256**3, 65536):
            ids = np.arange(start, start+65536, dtype=np.int64)
            rgb = np.column_stack((ids >> 16, (ids >> 8) & 255, ids & 255)).astype(np.uint8)
            single = integer_oracle(model, rgb); single_hash.update(single.tobytes())
            if first_stream is not None:
                first_stream[start:start+len(single)] = single
                for key, value in coverage(single, info).items():
                    cache_record['cube_coverage'][key] = cache_record['cube_coverage'].get(key, 0)+value
            for name in libraries:
                for mode, truth in [('single', single), ('chain', expected[start:start+len(rgb)])]:
                    for kernel, threads in [('scalar', 1), ('avx2', 4)]:
                        actual = operators[name][mode].apply(rgb.copy(), kernel=kernel, threads=threads)
                        np.testing.assert_array_equal(actual, truth)
                        hashes[name][mode+'_'+kernel].update(actual.tobytes())
        values = {name: {k: v.hexdigest() for k, v in hs.items()} for name, hs in hashes.items()}
        for hs in values.values():
            if any(value != (single_hash.hexdigest() if key.startswith('single') else prior['cube']['prediction_sha256'])
                   for key, value in hs.items()):
                raise AssertionError('完整域SHA与独立oracle不符')
        if single_hash.hexdigest() != prior['native']['cube_sha256']['single_oracle']:
            raise AssertionError('本次独立单级oracle与既有模型输出不符')
        print('完整256³单级/实际四级：两库标量1和AVX2请求4均零字节差异', flush=True)
        rows = read(paths['manifest'])['images']; old = prior['photos']['per_image']
        if len(rows) != 100 or [r['id'] for r in rows] != [r['image'] for r in old]:
            raise ValueError('不是相同顺序100图')
        for row, previous in zip(rows, old):
            with Image.open(checked(row['evaluation'])) as image:
                if image.mode != 'RGB' or image.size != (1024, 768):
                    raise ValueError('图片契约不同')
                rgb = np.asarray(image).reshape(-1, 3).copy()
            keys = rgb.astype(np.int64) @ np.array([65536, 256, 1], np.int64)
            item = {'image': row['id'], 'outputs': {}, 'byte_mismatches': 0}
            if first_stream is not None:
                item['cache_coverage'] = coverage(first_stream[keys], info)
                for key, value in item['cache_coverage'].items():
                    cache_record['photos_coverage'][key] = cache_record['photos_coverage'].get(key, 0)+value
            for name in libraries:
                actual = operators[name]['chain'].apply(rgb.copy(), kernel='avx2', threads=4)
                np.testing.assert_array_equal(actual, expected[keys])
                sha = hashlib.sha256(actual.tobytes()).hexdigest()
                if sha != previous['prediction_sha256']:
                    raise AssertionError('百图输出与已验精度身份不同')
                photos_hash[name].update(actual.tobytes()); item['outputs'][name] = sha
            photos.append(item)
        photo_values = {k: v.hexdigest() for k, v in photos_hash.items()}
        if any(h != prior['photos']['output_sha256'] for h in photo_values.values()):
            raise AssertionError('百图整组输出与原精度验收不同')
    finally:
        for group in operators.values():
            for handle in group.values():
                handle.close()
        if first_stream is not None:
            first_stream.flush()
    unchanged(identity)
    result = {'pass': True, 'purpose': __doc__, 'plan_sha256': digest(args.plan),
        'build_sha256': digest(args.build/'build.json'), 'libraries': build['libraries'],
        'contract_sha256': digest(args.contract), 'accuracy_results_reused': plan['fixed_inputs']['prior_full'],
        'representation': plan['fixed_inputs']['model'], 'base': plan['fixed_inputs']['base'],
        'sidecar': plan['fixed_inputs']['sidecar'], 'suffix_models': plan['suffix_models'],
        'cube': {'pixels': 256**3, 'single_oracle_sha256': single_hash.hexdigest(), 'outputs': values, 'byte_mismatches': 0},
        'photos': {'count': 100, 'output_sha256': photo_values, 'per_image': photos, 'byte_mismatches': 0},
        'model_accounting_bytes': memory, 'suffix_cache': cache_record, 'coordinate_layouts': layout_record,
        'shared_axis_formats': axis_record,
        'model_read_domains': domain_record,
        'cache_encoding': encoding_record,
        'new_fits': 0, 'performance_calls': 0,
        'scope': '冻结同模型的完整后端等价；精度数据复用相同输出流，不新增精度选型，不代表Skylake服务器运行或性能。'}
    save(out/'results.json', result)
    print('完整等价通过；准备后模型容量：', memory, flush=True)


if __name__ == '__main__':
    main()
