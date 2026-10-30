"""汇集逐配置完整的测量；中断场次原件保留，不合并不同环境的比较上下文。"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import statistics
import flash_chroma_support as support
import p16_frontier
from bench_flash_chroma import configs


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--measurements',type=Path,nargs='+',required=True)
    parser.add_argument('--profiles',nargs='+',required=True)
    parser.add_argument('--model-manifest',type=Path,required=True)
    parser.add_argument('--quality',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists(): raise FileExistsError('汇集目录已存在，拒绝覆盖')
    quality=json.loads(args.quality.read_text(encoding='utf-8'))
    inputs=[(path,json.loads((path/'results.json').read_text(encoding='utf-8'))) for path in args.measurements]
    first=inputs[0][1]
    if not quality.get('passed') or quality['library']['sha256']!=first['library']['sha256']:
        raise ValueError('缺少同库完整域正确性证据')
    observed={}
    catalog={'schema':p16_frontier.SCHEMA,'contexts':{},'models':{},'candidates':[],
        'notes':['各环境指纹和计时范围单独成组；未完成场次仅提取已经完整保存的配置，原始completed=false不改写。',
                 'A/A资格逐配置记录；首批单次观测没有稳定时间资格；未知LUT和Xeon6140未验。']}
    sessions=[]
    for folder,raw in inputs:
        if (raw['library']['sha256']!=first['library']['sha256'] or
                raw['source_pixels_sha256']!=first['source_pixels_sha256'] or
                raw['reference_source_luts']!=first['reference_source_luts'] or
                raw['executed_sources']!=first['executed_sources']):
            raise ValueError('场次的库、输入、原LUT或实际执行源码不一致')
        context={'source_luts_sha256':[r['sha256'] for r in raw['reference_source_luts']],
            'dataset_sha256':raw['source_pixels_sha256'],
            'platform_id':hashlib.sha256(json.dumps(raw['environment'],sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
            'timing_scope':raw.get('scope','preloaded-100x1024x768-rgb8-separate-output-hot-apply; excludes IO/hash/allocation/prepare'),
            'image_mode':'preloaded-batch-separate','build_id':raw['library']['sha256'],
            'measurement_session':folder.name,
            'memory_scope':'源模型+Runtime对象+保留的完整arena+百图输入输出；不含OS/OpenMP栈和分配器，非RSS硬上界。'}
        # 不同场次始终单独绑定，即使机器与依赖完全相同也不拼成一次配对实验。
        key=hashlib.sha256(json.dumps(context,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        cold=dict(context,timing_scope='prepare-to-first-preloaded-batch-wall; excludes image IO/hash/allocation')
        cold_key=hashlib.sha256(json.dumps(cold,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        catalog['contexts'][key]=context;catalog['contexts'][cold_key]=cold
        sessions.append({'id':folder.name,'original_completed':raw['completed'],'records':len(raw['records']),
                         'original_results_sha256':support.digest(folder/'results.json'),'environment':raw['environment']})
        for original in raw['records']:
            row=copy.deepcopy(original)
            identity=row['id']
            if identity in observed: raise ValueError('发现重复配置，拒绝择优覆盖：'+identity)
            if (len(row['hot_batch_ms'])!=5 or len(row['per_round_sha256'])!=5 or
                    len(row['aa_controls'])!=3 or len(row['per_image_sha256'])!=100 or
                    any(v!=row['batch_sha256'] for v in row['per_round_sha256'])):
                raise ValueError('配置缺少完整五轮、三周期A/A或100图输出证据：'+identity)
            row['measurement_session']=folder.name
            row['measurement_environment']=raw['environment']
            observed[identity]=row
            accuracy=json.loads((folder/(row['profile']+'-accuracy.json')).read_text(encoding='utf-8'))
            if len(accuracy['per_image'])!=100 or accuracy['pixels']!=100*768*1024:
                raise ValueError('精度覆盖不是整百图')
            resources=row['resources']
            candidate={'id':identity,'context':key,'model_id':row['profile'],'config':row['config'],
                'metrics':{'mean_error':accuracy['pixel_weighted_mean_delta_e'],
                    'worst_image_mean':max(r['mean_delta_e'] for r in accuracy['per_image']),
                    'batch_ms':statistics.median(row['hot_batch_ms']),
                    'runtime_bytes':resources['model_bytes']+resources['arena_bytes']+resources['object_bytes']+2*100*768*1024*3,
                    'workspace_bytes':resources['arena_bytes']},
                'verified':{'correctness':True,'accuracy':True,'resources':True,'time':True,'time_stable':row['aa_pass']},
                'evidence':'results.json#'+identity}
            catalog['candidates'].append(candidate)
            first_batch=copy.deepcopy(candidate);first_batch['id']+='-first';first_batch['context']=cold_key
            first_batch['metrics']['batch_ms']=row['prepare_to_first_ms'];first_batch['verified']['time_stable']=False
            catalog['candidates'].append(first_batch)
            catalog['models'][row['profile']]={'manifest':str(args.model_manifest.resolve()),
                'manifest_sha256':support.digest(args.model_manifest),'profile':row['profile'],
                'source_luts_sha256':context['source_luts_sha256']}
    expected={f'{name}-{c["representation"]}-{c["backend"]}-{c["threads"]}t'
              for name in args.profiles for c in configs(name)}
    if expected!=set(observed):
        raise ValueError('预声明配置未全部覆盖：缺少'+str(sorted(expected-set(observed)))+'；多出'+str(sorted(set(observed)-expected)))
    p16_frontier.validate_catalog(catalog)
    args.output.mkdir(parents=True)
    for folder,_ in inputs: shutil.copytree(folder,args.output/'sessions'/folder.name)
    support.write_json(args.output/'results.json',{'completed':True,'scope':'预声明20种配置均已完整记录；分场次保留比较上下文',
        'library':first['library'],'environment':first['environment'],'source_pixels_sha256':first['source_pixels_sha256'],
        'reference_source_luts':first['reference_source_luts'],'executed_sources':first['executed_sources'],
        'images':first['images'],'measurement_sessions':sessions,'records':list(observed.values())})
    support.write_json(args.output/'catalog.json',catalog)
    print('已核实并汇集',len(observed),'种配置，',len(sessions),'个场次，',len(catalog['contexts']),'个比较上下文')


if __name__=='__main__': main()
