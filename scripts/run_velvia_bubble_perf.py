"""冻结187三控制、百图及密集命中正式配对；必须获排他窗口再运行。"""
from __future__ import annotations
import argparse
import ctypes as ct
from datetime import datetime,timezone
import gc
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'python'));sys.path.insert(0,str(ROOT/'experiments/channel-runtime'))
import numpy as np
from PIL import Image
from channel_native import Library
from run_channel_tail_nodes import digest,save
from check_velvia_bubble_native import bind,set_mode,info
from lutlab import study_provenance


def array_sha(a):return hashlib.sha256(memoryview(a).cast('B')).hexdigest()


def datasets(cache):
    manifest=cache/'assets/photos/manifest.json'
    if digest(manifest)!='10893812e0d3cecea7ba8b6bbf4700addd09927feed220149501def03c374f7c':raise ValueError('manifest不符')
    refs={'off':np.memmap(cache/'artifacts/velvia-channel-coordinates-accept-v1/cube.rgb',np.uint8,'r',shape=(256**3,3)),
        'on':np.memmap(ROOT/'artifacts/velvia-bubble-accept-v1/candidate.rgb',np.uint8,'r',shape=(256**3,3))}
    photos=np.empty((78643200,3),np.uint8);offset=0;hashes={n:hashlib.sha256() for n in refs}
    for row in json.loads(manifest.read_text(encoding='utf-8'))['images']:
        path=cache/row['evaluation']['path']
        if digest(path)!=row['evaluation']['sha256']:raise ValueError('照片SHA不符')
        with Image.open(path) as image:rgb=np.asarray(image).reshape(-1,3)
        photos[offset:offset+len(rgb)]=rgb;offset+=len(rgb)
        keys=rgb.astype(np.int64)@np.array([65536,256,1],np.int64)
        for n,ref in refs.items():hashes[n].update(ref[keys].tobytes())
    if offset!=len(photos):raise ValueError('百图像素总数不符')
    dense=np.tile(np.array([[239,252,113]],np.uint8),(1048576,1));key=(239*256+252)*256+113
    expected={'photos':{n:h.hexdigest() for n,h in hashes.items()},
        'dense':{n:array_sha(np.tile(ref[key],(len(dense),1))) for n,ref in refs.items()}}
    del refs;gc.collect()
    return {'photos':photos,'dense':dense},expected


def bench(chain,source,work,path,threads,repeats):
    d=chain.library.dll;error=ct.create_string_buffer(1024);u8=ct.POINTER(ct.c_uint8)
    src,dst=source.ctypes.data_as(u8),work.ctypes.data_as(u8)
    a,b=np.empty(repeats,np.float64),np.empty(repeats,np.float64)
    ptr=lambda x:x.ctypes.data_as(ct.POINTER(ct.c_double))
    if path=='inplace':
        code=d.jshc_cc_bench(chain.handle,src,dst,source.nbytes,1,threads,repeats,ptr(a),ptr(b),error,len(error))
        values={'pure_apply_seconds':a.tolist(),'copy_apply_seconds':b.tolist()}
    else:
        d.jshc_cc_bench_to.argtypes=[ct.c_void_p,u8,u8,ct.c_size_t,ct.c_int,ct.c_int,ct.c_size_t,ct.POINTER(ct.c_double),ct.POINTER(ct.c_char),ct.c_size_t]
        d.jshc_cc_bench_to.restype=ct.c_int
        code=d.jshc_cc_bench_to(chain.handle,src,dst,source.nbytes,1,threads,repeats,ptr(a),error,len(error))
        values={'api_total_seconds':a.tolist()}
    if code:raise RuntimeError(error.value.decode('utf-8','replace'))
    if not all(v>0 for series in values.values() for v in series):raise AssertionError('计时非正')
    return values


def worker(args,plan):
    from contextlib import ExitStack
    folder=args.output/f'worker{args.worker}';folder.mkdir()
    frozen=json.loads((ROOT/'artifacts/velvia-bubble-native-v2/frozen.json').read_text(encoding='utf-8'))
    data,expected=datasets(args.cache_root)
    source_sha={n:array_sha(v) for n,v in data.items()}
    dirs=[os.add_dll_directory('E:/mingw64/bin'),os.add_dll_directory(str((ROOT/'artifacts/velvia-bubble-native-build-v1').resolve()))]
    libs={'87':Library(frozen['frozen_87_library'],plan['control_87_sha256']),
        '187':Library(ROOT/'artifacts/velvia-bubble-native-build-v1/libjshc_velvia_bubble.dll',plan['library_sha256'])}
    bind(libs['187'].dll)
    base=ROOT/'artifacts/velvia-bubble-native-v2/base.slut';side=base.with_name('channel-frac.bin')
    record={'worker':args.worker,'environment':study_provenance.environment_fingerprint(),'source_sha256':source_sha,
        'expected_output_sha256':expected,'groups':[],'plan_sha256':digest(ROOT/'experiments/velvia-bubble-perf-v1.json'),
        'driver_sha256':digest(Path(__file__))}
    with ExitStack() as stack:
        chains={n:stack.enter_context(libs['87' if n=='87' else '187'].chain([base],[side])) for n in ('87','187off','187on')}
        for chain in chains.values():
            if chain.inputs_sha256[str(base.resolve())]!=frozen['serialized_sha256']['base.slut'] or chain.inputs_sha256[str(side.resolve())]!=frozen['serialized_sha256']['channel-frac.bin']:
                raise ValueError('性能模型字节不再等于已验收冻结模型')
        set_mode(chains['187off'],0);set_mode(chains['187on'],1)
        record['capacity']={n:{'model_bytes':c.model_bytes,'bubble':info(c) if n!='87' else None} for n,c in chains.items()}
        scenarios=[(dataset,path,t) for dataset in ('photos','dense') for path in plan['paths'] for t in plan['threads']]
        if args.worker%2:scenarios.reverse()
        for dataset,path,threads in scenarios:
            source=data[dataset];work=np.empty_like(source)
            for label in plan['group_order']:
                model=label[:-1];phase=label[-1];chain=chains[model]
                bench(chain,source,work,path,threads,plan['warmup_per_group'])
                values=bench(chain,source,work,path,threads,plan['repeats_per_group'])
                output_sha=array_sha(work)
                if output_sha!=expected[dataset]['on' if model=='187on' else 'off'] or array_sha(source)!=source_sha[dataset]:raise AssertionError('末work或源SHA错误')
                row={'dataset':dataset,'path':path,'threads':threads,'model':model,'phase':phase,'seconds':values,
                    'medians':{n:statistics.median(v) for n,v in values.items()},'output_sha256':output_sha,'source_readonly':True,
                    'wall_end_utc':datetime.now(timezone.utc).isoformat()}
                record['groups'].append(row);save(folder/'results.json',record)
            del work
    print(json.dumps({'worker':args.worker,'groups':len(record['groups']),'all_sha_passed':True}),flush=True)


def summarize(records):
    aa,ratios=[],[]
    for record in records:
        groups=record['groups']
        for dataset,path,threads in sorted({(r['dataset'],r['path'],r['threads']) for r in groups}):
            current={(r['model'],r['phase']):r for r in groups if (r['dataset'],r['path'],r['threads'])==(dataset,path,threads)}
            valid=True
            for metric in current['87','A']['medians']:
                for model in ('87','187off'):
                    value=current[model,'B']['medians'][metric]/current[model,'A']['medians'][metric]
                    passed=.85<=value<=1.15;valid &= passed
                    aa.append({'worker':record['worker'],'dataset':dataset,'path':path,'threads':threads,'metric':metric,'model':model,'B_over_A':value,'pass':passed})
            for phase in ('A','B'):
                for left,right in [('87','187off'),('187off','187on'),('87','187on')]:
                    for metric in current[left,phase]['medians']:
                        value=current[right,phase]['medians'][metric]/current[left,phase]['medians'][metric]
                        ratios.append({'worker':record['worker'],'dataset':dataset,'path':path,'threads':threads,'phase':phase,'comparison':right+'/'+left,
                            'metric':metric,'time_ratio':value,'throughput_retention':1/value,'AA_valid':valid})
    valid=[r for r in ratios if r['AA_valid']]
    worst=min((r['throughput_retention'] for r in valid),default=None)
    return {'AA':aa,'comparisons':ratios,'AA_all_passed':all(r['pass'] for r in aa),'minimum_valid_throughput_retention':worst,
        'valid_worst':min(valid,key=lambda r:r['throughput_retention']) if valid else None,
        'speed_tiers':{str(p):worst is not None and worst>=p/100 for p in (100,90,80,70,60,50)},
        'rejected_by_valid_below_50':bool(worst is not None and worst<.5),
        'scope':'保留全部worker/重复/相位及AA无效场；阈值依据有效最劣组内中位数比，不挑最优重复。真分离API含其内部复制，未分解纯映射。'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cache-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--worker',type=int)
    args=p.parse_args();plan_path=ROOT/'experiments/velvia-bubble-perf-v1.json';plan=json.loads(plan_path.read_text(encoding='utf-8'))
    if args.worker is not None:return worker(args,plan)
    if args.output.exists():raise ValueError('不覆盖正式性能试验')
    frozen=json.loads((ROOT/'artifacts/velvia-bubble-native-v2/frozen.json').read_text(encoding='utf-8'))
    quality=json.loads((ROOT/'artifacts/velvia-bubble-native-check-v1/results.json').read_text(encoding='utf-8'))
    if not quality['passed'] or quality['quality_source_sha256']!=digest(ROOT/'scripts/check_velvia_bubble_native.py'):raise ValueError('必须保持通过的原生质量及typed绑定')
    if digest(args.cache_root/'artifacts/velvia-channel-coordinates-accept-v1/cube.rgb')!=frozen['oracle_baseline_sha256'] or digest(ROOT/'artifacts/velvia-bubble-accept-v1/candidate.rgb')!=frozen['oracle_candidate_sha256']:raise ValueError('冻结oracle流变动')
    args.output.mkdir(parents=True)
    save(args.output/'identity.json',{'plan':plan,'plan_sha256':digest(plan_path),'driver_sha256':digest(Path(__file__)),
        'environment':study_provenance.environment_fingerprint(),'started_utc':datetime.now(timezone.utc).isoformat()})
    for n in range(plan['workers']):
        command=[sys.executable,str(Path(__file__)),'--cache-root',str(args.cache_root),'--output',str(args.output),'--worker',str(n)]
        subprocess.run(command,check=True,cwd=ROOT)
    records=[json.loads((args.output/f'worker{n}/results.json').read_text(encoding='utf-8')) for n in range(plan['workers'])]
    result=summarize(records);save(args.output/'results.json',result)
    print(json.dumps({n:result[n] for n in ('AA_all_passed','minimum_valid_throughput_retention','valid_worst','speed_tiers','rejected_by_valid_below_50')},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
