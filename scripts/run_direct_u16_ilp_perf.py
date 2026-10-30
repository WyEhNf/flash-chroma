"""冻结八角色287/87同场性能；仅在获独占计时窗后执行。"""
from __future__ import annotations
import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
from contextlib import ExitStack
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'python'),str(ROOT/'experiments/channel-runtime')]
import numpy as np
from PIL import Image
from channel_native import Library
from run_channel_tail_nodes import digest,save
from run_velvia_bubble_perf import bench,array_sha
from check_direct_u16_ilp_native import info
from direct16_support import info as direct_info
from lutlab import study_provenance


def definitions(cache,frozen):
    specs=frozen['models'];original=cache/'artifacts/cinema-envelope-v1/stage4_sweep004'
    first=cache/'artifacts/cinema-current-anchor-accept-v1'
    a399={'models':[str(first/'candidate-base.slut'),*[str(original/f'selected-stage{s}.slut') for s in (2,3,4)]],
        'sidecars':[str(first/'channel-frac.bin'),None,None,None]}
    oracle=first/'cube.rgb'
    expected='3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22'
    if digest(oracle)!=expected:raise ValueError('冻结a399完整oracle变更')
    a399['oracle']=str(oracle);a399['oracle_sha256']=expected
    a399['input_sha256']={str(Path(p).resolve()):digest(p) for p in [*a399['models'],a399['sidecars'][0]]}
    return {'87a399':(87,a399),'87old':(87,specs['old_best']),'288a399':(288,a399),'288old':(288,specs['old_best']),
        '287max':(287,specs['max_first']),'287p99':(287,specs['p99_first']),
        '288max':(288,specs['max_first']),'288p99':(288,specs['p99_first'])}


def dataset(cache,models,frozen):
    manifest_path=cache/'assets/photos/manifest.json'
    if digest(manifest_path)!=frozen['photo_manifest_sha256']:raise ValueError('照片manifest变更')
    unique={s['oracle']:s for _,s in models.values()}
    for s in unique.values():
        if digest(s['oracle'])!=s['oracle_sha256']:raise ValueError('完整oracle变更')
    refs={n:np.memmap(n,np.uint8,'r',shape=(256**3,3)) for n in unique}
    hashes={n:hashlib.sha256() for n in refs};photos=np.empty((78643200,3),np.uint8);offset=0
    for row in json.loads(manifest_path.read_text(encoding='utf-8'))['images']:
        path=cache/row['evaluation']['path']
        if digest(path)!=row['evaluation']['sha256']:raise ValueError('照片变更')
        with Image.open(path) as image:rgb=np.asarray(image).reshape(-1,3)
        photos[offset:offset+len(rgb)]=rgb;offset+=len(rgb);keys=rgb.astype(np.int64)@np.array([65536,256,1],np.int64)
        for n,ref in refs.items():hashes[n].update(ref[keys].tobytes())
    if offset!=len(photos):raise ValueError('百图像素总数变化')
    expected={n:hashes[s['oracle']].hexdigest() for n,(_,s) in models.items()}
    del refs;gc.collect();return photos,expected


def worker(args,plan):
    folder=args.output/f'worker{args.worker}';folder.mkdir()
    frozen=json.loads((ROOT/'artifacts/p16-direct-u16-ilp-frozen-v1/frozen.json').read_text(encoding='utf-8'))
    models=definitions(args.cache_root,frozen);source,expected=dataset(args.cache_root,models,frozen);source_sha=array_sha(source)
    dirs=[os.add_dll_directory('E:/mingw64/bin'),os.add_dll_directory(str((ROOT/'artifacts/p16-direct-u16-ilp-build-v1').resolve()))]
    libraries={87:Library(frozen['frozen_87_library'],plan['control_87_sha256']),287:Library(ROOT/'artifacts/p16-direct-u16-build-v1/libjshc_direct_u16.dll',plan['legacy_287_sha256']),288:Library(ROOT/'artifacts/p16-direct-u16-ilp-build-v1/libjshc_direct_u16_ilp.dll',plan['library_sha256'])}
    record={'worker':args.worker,'environment':study_provenance.environment_fingerprint(),'expected_output_sha256':expected,'source_sha256':source_sha,
        'groups':[],'prepare':[],'models':models,'plan_sha256':digest(ROOT/'experiments/p16-direct-u16-ilp-perf-v1.json'),'driver_sha256':digest(Path(__file__))}
    with ExitStack() as stack:
        chains={};work=np.empty_like(source)
        for role in plan['roles']:
            revision,spec=models[role]
            for p,sha in spec['input_sha256'].items():
                if digest(p)!=sha:raise ValueError('模型改变')
            started=time.perf_counter();c=stack.enter_context(libraries[revision].chain(spec['models'],spec['sidecars']));create=time.perf_counter()-started;chains[role]=c
            first=bench(c,source,work,'inplace',4,1)
            if array_sha(work)!=expected[role] or array_sha(source)!=source_sha:raise AssertionError('首次百图或源SHA错误')
            row={'role':role,'construction_seconds':create,'cold_first_seconds':first,'construction_plus_first_copy_apply_seconds':create+first['copy_apply_seconds'][0],
                'output_sha256':array_sha(work),'model_bytes':c.model_bytes,'direct':direct_info(c),'wide':info(c) if revision!=87 else None}
            record['prepare'].append(row);save(folder/'results.json',record)
        scenarios=[(path,t) for path in plan['paths'] for t in plan['threads']]
        if args.worker%2:scenarios.reverse()
        for path,threads in scenarios:
            for label in plan['group_order']:
                role,phase=label[:-1],label[-1];chain=chains[role]
                bench(chain,source,work,path,threads,plan['warmup_per_group']);values=bench(chain,source,work,path,threads,plan['repeats_per_group'])
                output_sha=array_sha(work)
                if output_sha!=expected[role] or array_sha(source)!=source_sha:raise AssertionError('组末work或源SHA错误')
                record['groups'].append({'role':role,'phase':phase,'path':path,'threads':threads,'seconds':values,
                    'medians':{k:statistics.median(v) for k,v in values.items()},'output_sha256':output_sha,'source_readonly':True})
                save(folder/'results.json',record)
    print(json.dumps({'worker':args.worker,'groups':len(record['groups']),'all_sha_passed':True}),flush=True)


def summarize(records,plan):
    aa=[];ratios=[];lo,hi=plan['AA_time_ratio_bounds']
    for record in records:
        for path,t in [(p,t) for p in plan['paths'] for t in plan['threads']]:
            rows={(r['role'],r['phase']):r for r in record['groups'] if (r['path'],r['threads'])==(path,t)};valid={}
            for role in plan['roles']:
                valid[role]=True
                for metric in rows[role,'A']['medians']:
                    value=rows[role,'B']['medians'][metric]/rows[role,'A']['medians'][metric];passed=lo<=value<=hi;valid[role]&=passed
                    aa.append({'worker':record['worker'],'path':path,'threads':t,'role':role,'metric':metric,'B_over_A':value,'pass':passed})
            for left,right in plan['comparisons']:
                for phase in ('A','B'):
                    for metric in rows[left,phase]['medians']:
                        value=rows[right,phase]['medians'][metric]/rows[left,phase]['medians'][metric]
                        ratios.append({'worker':record['worker'],'path':path,'threads':t,'phase':phase,'comparison':right+'/'+left,'metric':metric,
                            'time_ratio':value,'throughput_retention':1/value,'AA_valid':bool(valid[left] and valid[right])})
    result={'AA':aa,'comparisons':ratios,'AA_all_passed':all(r['pass'] for r in aa),'pairs':{}}
    for left,right in plan['comparisons']:
        pair=right+'/'+left;rows=[r for r in ratios if r['comparison']==pair and r['AA_valid']];worst=min((r['throughput_retention'] for r in rows),default=None)
        result['pairs'][pair]={'valid_rows':len(rows),'worst':min(rows,key=lambda r:r['throughput_retention']) if rows else None,
            'minimum_valid_throughput_retention':worst,'tiers':{str(p):worst is not None and worst>=p/100 for p in (100,90,80,70,60,50)},
            'no_obvious_degradation':bool(worst is not None and worst>=1/plan['no_obvious_time_ratio_cap']),
            'rejected_by_valid_below_50':bool(worst is not None and worst<.5),'all_AA_passed_for_pair':all(r['AA_valid'] for r in ratios if r['comparison']==pair)}
    result['candidate_gates']={role:{'hard50':all(result['pairs'][role+'/'+base]['tiers']['50'] and result['pairs'][role+'/'+base]['all_AA_passed_for_pair'] for base in ('87a399','87old','288old')),
        'rejected_by_valid_below_50':any(result['pairs'][role+'/'+base]['rejected_by_valid_below_50'] for base in ('87a399','87old','288old'))} for role in ('288max','288p99')}
    result['scope']='全部raw worker/相位/AA保留；先组内中位数再最劣，不重跑挑样；冷首无AA单列、不切默认。'
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cache-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--worker',type=int);args=p.parse_args()
    plan_path=ROOT/'experiments/p16-direct-u16-ilp-perf-v1.json';plan=json.loads(plan_path.read_text(encoding='utf-8'))
    if args.worker is not None:return worker(args,plan)
    if args.output.exists():raise ValueError('不覆盖正式性能')
    frozen_path=ROOT/'artifacts/p16-direct-u16-ilp-frozen-v1/frozen.json';quality_path=ROOT/'artifacts/p16-direct-u16-ilp-quality-v1/results.json';quality=json.loads(quality_path.read_text(encoding='utf-8'))
    if digest(frozen_path)!=plan['quality_frozen_sha256'] or not quality['passed'] or quality['library_sha256']!=plan['library_sha256']:raise ValueError('必须保持已验收质量')
    args.output.mkdir(parents=True)
    save(args.output/'identity.json',{'plan':plan,'plan_sha256':digest(plan_path),'driver_sha256':digest(Path(__file__)),'quality_sha256':digest(quality_path),
        'helper_sha256':{p:digest(ROOT/p) for p in ('scripts/run_velvia_bubble_perf.py','scripts/check_direct_u16_ilp_native.py','experiments/channel-runtime/channel_native.py')},
        'environment':study_provenance.environment_fingerprint()})
    for n in range(plan['workers']):subprocess.run([sys.executable,str(Path(__file__)),'--cache-root',str(args.cache_root),'--output',str(args.output),'--worker',str(n)],check=True,cwd=ROOT)
    records=[json.loads((args.output/f'worker{n}/results.json').read_text(encoding='utf-8')) for n in range(plan['workers'])]
    result=summarize(records,plan);save(args.output/'results.json',result)
    print(json.dumps({'AA_all_passed':result['AA_all_passed'],'pairs':result['pairs'],'candidate_gates':result['candidate_gates']},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
