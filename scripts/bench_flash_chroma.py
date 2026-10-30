"""固定百图与四个原始LUT，测单头配置的精度/时间/资源并生成可选择目录。"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import statistics
import time
import zipfile
from pathlib import Path

import numpy as np
import flash_chroma_support as support
import p16_frontier
import p16_submission


def photo_data():
    # 原计划保存图像文件及解码像素SHA；不替换为随机图。
    plan = support.native.load_plan(support.ROOT/'experiments/p16-score-quality-v1.json')
    frames, records = support.native.photos(plan)
    return frames, records, plan


def reference(frames, records):
    tables = []
    for record in records:
        if support.digest(record['path']) != record['sha256']:
            raise ValueError('原始LUT摘要改变')
        tables.append(np.memmap(record['path'], dtype=np.uint8, mode='r', shape=(256,256,256,3)))
    truth = np.empty_like(frames)
    for i, frame in enumerate(frames):
        value = frame
        for table in tables:
            value = table[value[...,0], value[...,1], value[...,2]]
        truth[i] = value
    for table in tables:
        table._mmap.close()
    return truth


def quality(target, truth):
    rows = [{'index': index, **p16_submission._error_row(a,b)}
            for index,(a,b) in enumerate(zip(target, truth))]
    return p16_submission.accuracy_summary(rows, None)


def configs(name, scalar=False):
    yield support.configuration(backend='scalar', target='portable')
    if scalar:
        return
    yield support.configuration(backend='avx2', threads=1)
    yield support.configuration(backend='avx2', threads=4)
    if name in ('default','max_first','max41','max48'):
        rep = 'direct_u8' if name=='default' else 'direct_u16'
        yield support.configuration(rep, 'avx2', 1)
        yield support.configuration(rep, 'avx2', 4)
    if name == 'default':
        yield support.configuration('direct_rgb24', 'avx2', 4)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--quality-receipt', type=Path, required=True)
    parser.add_argument('--profiles', nargs='+')
    parser.add_argument('--reference-luts', nargs=4, type=Path)
    parser.add_argument('--repeats', type=int, default=5)
    parser.add_argument('--cpus', default='0,2,4,6')
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('拒绝覆盖测量目录')
    if not 3 <= args.repeats <= 15:
        raise ValueError('正式批次次数应为3..15')
    receipt = json.loads(args.quality_receipt.read_text(encoding='utf-8'))
    library = support.Library(args.library)
    if not receipt.get('passed') or receipt['library']['sha256'] != library.sha256:
        raise ValueError('需先取得同一库的正确性回执')
    support.native.setup(cpus=args.cpus)
    args.output.mkdir(parents=True)
    executed_sources={}
    for relative in ('include/flash_chroma.hpp','include/flash_chroma_c.h',
                     'src/flash_chroma_cpp.inc','src/flash_chroma_selection.inc',
                     'src/flash_chroma_direct.inc','src/flash_chroma_prepare.inc',
                     'single_header/bridge.cpp','single_header/c_bridge.c',
                     'scripts/bench_flash_chroma.py','scripts/flash_chroma_support.py',
                     'scripts/p16_frontier.py'):
        source_path=support.ROOT/relative
        payload=source_path.read_bytes()
        destination_path=args.output/'executed-sources'/relative
        destination_path.parent.mkdir(parents=True,exist_ok=True)
        destination_path.write_bytes(payload)
        executed_sources[relative]=hashlib.sha256(payload).hexdigest()
    manifest, models = support.load_models(args.manifest, args.profiles)
    frames, images, plan = photo_data()
    source_sha = support.sha(frames)
    source_records = manifest.get('original_luts')
    if args.reference_luts:
        source_records=[{'path':str(p.resolve()),'sha256':support.digest(p),'bytes':p.stat().st_size}
                        for p in args.reference_luts]
        if manifest.get('source_luts_sha256') and [v['sha256'] for v in source_records]!=manifest['source_luts_sha256']:
            raise ValueError('提供的四张原始LUT与模型来源不一致')
    if not source_records:
        with zipfile.ZipFile(support.ROOT/'report/data/p16-score-candidate-20261027/raw-evidence.zip') as archive:
            source_records = json.loads(archive.read('run-default/results.json'))['quality']['sources']
    truth = reference(frames, source_records)
    target = np.empty_like(frames)
    source, destination = frames.reshape(-1,3), target.reshape(-1,3)
    environment = support.native.environment()
    identity = library.record()
    scope = 'preloaded-100x1024x768-rgb8-separate-output-hot-apply; excludes IO/hash/allocation/prepare'
    context = {'source_luts_sha256': [v['sha256'] for v in source_records],
        'dataset_sha256': source_sha,
        'platform_id': hashlib.sha256(json.dumps(environment,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
        'timing_scope': scope, 'image_mode': 'preloaded-batch-separate', 'build_id': library.sha256,
        'scope_note': '同一宿主软件构建；portable配置为宿主执行，不是实际MCU吞吐。',
        'memory_scope': 'runtime_bytes含源SLUT/sidecar、Runtime对象、保留整个arena及百图输入输出；OS线程栈/分配器另看RSS。'}
    context_key = hashlib.sha256(json.dumps(context,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    first_context=dict(context,timing_scope='prepare-to-first-preloaded-batch-wall; excludes image IO/hash/allocation')
    first_key=hashlib.sha256(json.dumps(first_context,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    catalog = {'schema': p16_frontier.SCHEMA, 'contexts': {context_key: context,first_key:first_context},
        'models': {name:{'manifest':str(args.manifest.resolve()), 'manifest_sha256':support.digest(args.manifest),'profile':name,
                         'source_luts_sha256':context['source_luts_sha256']}
                   for name in models}, 'candidates': [], 'notes': [
        '描述性单场目录；默认严格选择要求稳定时间，未取得A/A资格时需显式允许暂定时间或使用无时间目标。',
        '质量仅属于已见Cinema百图；未取得官方Threshold、目标Xeon6140或新盲测资格。']}
    raw = []
    for name, model in models.items():
        reference_sha = None
        profile_quality = None
        for index, config in enumerate(configs(name, scalar=not bool(library.capabilities & 2))):
            candidate_id = f'{name}-{config["representation"]}-{config["backend"]}-{config["threads"]}t'
            print('开始固定配置', candidate_id, flush=True)
            before = support.native.rss()
            begin = time.perf_counter_ns()
            with library.create(model, config) as engine:
                first = engine.apply(source, destination)
                first_wall = (time.perf_counter_ns()-begin)/1e6
                actual = support.sha(target)
                if reference_sha is not None and actual != reference_sha:
                    raise AssertionError('同模型配置输出不一致：'+candidate_id)
                reference_sha = actual
                if profile_quality is None:
                    profile_quality = quality(target, truth)
                    support.write_json(args.output/(name+'-accuracy.json'), profile_quality)
                warmup = engine.apply(source, destination)
                values, hashes = [], []
                for _ in range(args.repeats):
                    values.append(engine.apply(source, destination))
                    hashes.append(support.sha(target))
                if any(value != reference_sha for value in hashes):
                    raise AssertionError('正式批次输出改变')
                # 同配置的两个独立句柄，固定三周期ABBA/BAAB；不补轮或删慢轮。
                controls=[]
                with library.create(model,config) as second:
                    second.apply(source,destination)
                    for cycle in range(3):
                        order=(0,1,1,0) if cycle%2==0 else (1,0,0,1)
                        observations=[[],[]]
                        for side in order:
                            observations[side].append((engine if side==0 else second).apply(source,destination))
                        if support.sha(target)!=reference_sha:
                            raise AssertionError('A/A周期输出改变')
                        ratio=statistics.mean(observations[1])/statistics.mean(observations[0])
                        controls.append({'cycle':cycle,'order':order,'observations_ms':observations,'ratio':ratio})
                stable=all(0.90<=v['ratio']<=1.10 for v in controls)
                record = {'id':candidate_id, 'profile':name, 'config':dict(config),
                    'resources':engine.info, 'prepare_ms':engine.prepare_ms,
                    'preparation':engine.preparation,
                    'first_batch_ms':first, 'prepare_to_first_ms':first_wall, 'warmup_ms':warmup,
                    'hot_batch_ms':values, 'batch_sha256':actual, 'per_round_sha256':hashes,
                    'per_image_sha256':[support.sha(image) for image in target],
                    'aa_controls':controls,'aa_pass':stable,
                    'rss_before':before, 'rss_after_first_and_repeats':support.native.rss()}
                config['backend'] = {1:'scalar',2:'avx2'}[engine.info['selected_backend']]
                # 对实际保留的完整arena计账；不假定宿主适配器释放准备尾段。
                runtime_bytes = model.total_bytes + engine.info['arena_bytes'] + engine.info['object_bytes'] + frames.nbytes + target.nbytes
                row = {'id':candidate_id, 'context':context_key, 'model_id':name,
                    'config':config, 'metrics':{
                        'mean_error':profile_quality['pixel_weighted_mean_delta_e'],
                        'worst_image_mean':max(v['mean_delta_e'] for v in profile_quality['per_image']),
                        'batch_ms':statistics.median(values), 'runtime_bytes':runtime_bytes,
                        'workspace_bytes':engine.info['arena_bytes']},
                    'verified':{'correctness':True,'accuracy':True,'resources':True,'time':True,'time_stable':stable},
                    'evidence':str((args.output/'results.json').resolve())+'#'+candidate_id}
                catalog['candidates'].append(row)
                cold=copy.deepcopy(row)
                cold['id']+='-first'
                cold['context']=first_key
                cold['metrics']['batch_ms']=first_wall
                cold['verified']['time_stable']=False
                catalog['candidates'].append(cold)
                raw.append(record)
                print('完成', candidate_id, 'mean', row['metrics']['mean_error'],
                      'median_ms',row['metrics']['batch_ms'],'arena',engine.info['arena_bytes'],flush=True)
            # 每配置结束即保存，以保留失败前完成的测量，不恢复混用环境。
            support.write_json(args.output/'results.json', {'completed':False,'library':identity,
                'environment':environment,'executed_sources':executed_sources,'images':images,'source_pixels_sha256':source_sha,
                'reference_source_luts':source_records,'records':raw})
    p16_frontier.validate_catalog(catalog)
    support.write_json(args.output/'catalog.json', catalog)
    support.write_json(args.output/'results.json', {'completed':True,'library':identity,
        'quality_receipt_sha256':support.digest(args.quality_receipt), 'environment':environment,'executed_sources':executed_sources,
        'images':images,'source_pixels_sha256':source_sha, 'reference_source_luts':source_records,
        'records':raw, 'scope':scope, 'time_stable':False,
        'memory_limit_note':'受控容量账本不含OS/OpenMP栈和分配器；不能当进程峰值硬上界。'})
    print('已保存实际配置',len(raw),'个；目录',args.output/'catalog.json',flush=True)


if __name__ == '__main__':
    main()
