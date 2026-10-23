"""同一87库比较两条固定模型，使用独立全域oracle验证照片后测量完整边界。"""
from __future__ import annotations
import argparse
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import statistics as st
import subprocess
import sys
import time
import numpy as np
from PIL import Image
import psutil
from study_p16_direct_compile import ROOT,Library,save,digest,env
from channel_native import Chain
from palette_support import info as palette_info
from suffix_cache_support import cache_info
from direct16_support import info as direct_info
from domain_cache_support import info as domain_info

def checked(row):
    p=Path(row['path']);assert digest(p)==row['sha256'],str(p);return p

def source(plan):
    manifest=json.loads(checked(plan['manifest']).read_text(encoding='utf-8'))
    frames=np.empty((100,768,1024,3),np.uint8)
    for i,row in enumerate(manifest['images']):
        p=Path(plan['data_root'])/row['evaluation']['path'];assert digest(p)==row['evaluation']['sha256']
        with Image.open(p) as image:frames[i]=np.asarray(image)
        assert hashlib.sha256(frames[i].tobytes()).hexdigest()==row['evaluation']['pixel_sha256']
    return frames,manifest

def preflight(args,plan):
    if args.output.exists():raise FileExistsError('保留已有目录')
    args.output.mkdir(parents=True)
    frames,manifest=source(plan);expected={}
    for name,role in plan['roles'].items():
        cube=np.memmap(checked(role['oracle']),dtype=np.uint8,mode='r',shape=(1<<24,3));h=hashlib.sha256();per_image=[]
        for row,frame in zip(manifest['images'],frames):
            a=frame.astype(np.uint32);code=(a[:,:,0]<<16)|(a[:,:,1]<<8)|a[:,:,2]
            raw=cube[code].tobytes();h.update(raw);per_image.append(hashlib.sha256(raw).hexdigest())
        expected[name]={'whole_sha256':h.hexdigest(),'per_image_sha256':per_image}
    accepted=json.loads(checked(plan['candidate_acceptance']).read_text(encoding='utf-8'))
    c=accepted['variants']['candidate']
    assert accepted['library_sha256']==plan['library']['sha256'] and c['full_native_byte_mismatches']==0 and c['photo_native_byte_mismatches']==0
    assert c['sha256']['oracle']==plan['roles']['candidate']['oracle']['sha256']
    assert expected['candidate']['per_image_sha256']==[r['prediction_sha256'] for r in c['photos']['per_image']]
    save(args.output/'preflight.json',{'oracle_photo_outputs':expected,
        'source_sha256':hashlib.sha256(frames.tobytes()).hexdigest(),'candidate_full_verified_by':plan['candidate_acceptance'],
        'scope':'读取既有独立完整RGB8 oracle生成照片预期，未重跑完整域或修改模型'})
    save(args.output/'executed-plan.json',plan)
    print('照片预期及既有87完整域身份通过',flush=True)

def native_create(lib,role):
    paths=[checked(p) for p in role['models']];sides=[checked(s) if s else None for s in role['sidecars']]
    p=(ct.c_char_p*4)(*(str(v).encode('utf-8') for v in paths));s=(ct.c_char_p*4)(*(str(v).encode('utf-8') if v else None for v in sides))
    handle=ct.c_void_p();error=ct.create_string_buffer(1024)
    started=time.perf_counter_ns();rc=lib.dll.jshc_cc_create(p,s,4,ct.byref(handle),error,len(error));elapsed=(time.perf_counter_ns()-started)*1e-9
    if rc:raise RuntimeError(error.value.decode('utf-8','replace'))
    chain=Chain.__new__(Chain);chain.library=lib;chain.handle=handle
    return chain,elapsed

def worker(args,plan):
    psutil.Process().cpu_affinity(plan['cpus'])
    dll_dir=os.add_dll_directory('E:/mingw64/bin') if os.name=='nt' else None
    lib=Library(checked(plan['library']),plan['library']['sha256']);assert lib.revision==87
    pre=json.loads((args.output/'preflight.json').read_text(encoding='utf-8'))
    frames,_=source(plan);source_sha=hashlib.sha256(frames.tobytes()).hexdigest();assert source_sha==pre['source_sha256']
    d=lib.dll;u8=ct.POINTER(ct.c_uint8);f=d.jshc_cc_bench_to
    f.argtypes=[ct.c_void_p,u8,u8,ct.c_size_t,ct.c_int,ct.c_int,ct.c_size_t,ct.POINTER(ct.c_double),ct.POINTER(ct.c_char),ct.c_size_t];f.restype=ct.c_int
    records=[]
    for name in plan['orders'][args.worker]:
        work=np.empty_like(frames);chain,prepared=native_create(lib,plan['roles'][name])
        with chain:
            di=direct_info(chain);assert di['enabled'] and di['format']==9
            state={'cache':cache_info(chain),'domain':domain_info(chain),'palette':palette_info(chain),'direct':di,'model_bytes':chain.model_bytes}
            error=ct.create_string_buffer(1024)
            def outplace(n,threads):
                times=np.empty(n,np.float64)
                assert not f(chain.handle,frames.ctypes.data_as(u8),work.ctypes.data_as(u8),frames.nbytes,1,threads,n,times.ctypes.data_as(ct.POINTER(ct.c_double)),error,len(error)),error.value
                assert hashlib.sha256(work.tobytes()).hexdigest()==pre['oracle_photo_outputs'][name]['whole_sha256']
                return times.tolist()
            cold=outplace(1,4)[0]
            for threads in plan['thread_orders'][args.worker]:
                expected=pre['oracle_photo_outputs'][name]['whole_sha256']
                got=chain.apply(frames.copy(),kernel='avx2',threads=threads);assert hashlib.sha256(got.tobytes()).hexdigest()==expected;del got
                rounds=plan['repeats'][str(threads)]
                first=chain.bench(frames,kernel='avx2',threads=threads,repeats=rounds)
                separate=outplace(rounds,threads)
                control=chain.bench(frames,kernel='avx2',threads=threads,repeats=rounds)
                records.append({'role':name,'threads':threads,'prepare_seconds':prepared,'cold_outplace4_seconds':cold,
                    'state':state,'output_sha256':expected,'apply':first['apply_seconds'],'copy_apply':first['copy_apply_seconds'],
                    'outplace':separate,'control_apply':control['apply_seconds']})
                save(args.output/f'worker{args.worker}-partial.json',{'records':records,'source_sha256':source_sha})
    assert hashlib.sha256(frames.tobytes()).hexdigest()==source_sha
    save(args.output/f'worker{args.worker}.json',{'records':records,'source_sha256':source_sha,'environment':env()})

def measure(args,plan):
    if any(args.output.glob('worker*.json')):raise FileExistsError('已有性能证据，不重跑')
    workers=[]
    for i in range(4):
        subprocess.run([sys.executable,'-X','utf8',__file__,'--plan',str(args.plan),'--output',str(args.output),'--mode','measure','--worker',str(i)],check=True)
        workers.append(json.loads((args.output/f'worker{i}.json').read_text(encoding='utf-8')));print('完成模型配对进程',i,flush=True)
    summary=[];controls=[];retentions=[]
    for threads in (1,4):
        pairs=[{r['role']:r for r in w['records'] if r['threads']==threads} for w in workers];row={'threads':threads}
        for key in ('apply','copy_apply','outplace'):
            ratios=[st.median(p['candidate'][key])/st.median(p['baseline'][key]) for p in pairs]
            row[key]={'time_ratios':ratios,'median_time_ratio':st.median(ratios),'worst_throughput_retained':1/max(ratios),
                'ms_per_image':{n:[st.median(p[n][key])*10 for p in pairs] for n in ('baseline','candidate')}}
            if key in ('apply','outplace'):retentions.extend([1/r for r in ratios])
        row['controls']={n:[st.median(p[n]['control_apply'])/st.median(p[n]['apply']) for p in pairs] for n in ('baseline','candidate')}
        controls.extend(v for values in row['controls'].values() for v in values)
        row['prepare_time_ratios']=[p['candidate']['prepare_seconds']/p['baseline']['prepare_seconds'] for p in pairs]
        row['prepare_plus_cold_outplace4_ratios']=[(p['candidate']['prepare_seconds']+p['candidate']['cold_outplace4_seconds'])/(p['baseline']['prepare_seconds']+p['baseline']['cold_outplace4_seconds']) for p in pairs]
        summary.append(row)
    gates=plan['gates'];valid=all(gates['control_any_min']<=v<=gates['control_any_max'] for v in controls)
    floor=valid and min(retentions)>=.5
    no_obvious=valid and all(r[k]['median_time_ratio']<=1.05 and max(r[k]['time_ratios'])<=1.1 for r in summary for k in ('apply','outplace'))
    save(args.output/'results.json',{'control_valid':valid,'meets_50_percent_speed_floor':floor,'no_obvious_slowdown':no_obvious,
        'worst_throughput_retained':min(retentions),'grades':{str(v):valid and min(retentions)>=v/100 for v in (100,90,80,70,60,50)},
        'summary':summary,'worker_sha256':[digest(args.output/f'worker{i}.json') for i in range(4)],
        'scope':'固定100张已见图，同87库不同模型；完整prepare含读取/原生校验，不含Python文件hash；无锁频/控温，非官方服务器。'})
    print('控制/50%底线/无明显退化：',valid,floor,no_obvious,'最劣吞吐保留',min(retentions),flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--mode',choices=('preflight','measure'),required=True);p.add_argument('--worker',type=int);args=p.parse_args()
    plan=json.loads(args.plan.read_text(encoding='utf-8'));assert digest(Path(__file__))==plan['script_sha256']
    if args.worker is not None:return worker(args,plan)
    return (preflight if args.mode=='preflight' else measure)(args,plan)
if __name__=='__main__':main()
