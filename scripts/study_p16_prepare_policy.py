"""显式准备策略的完整整数验证和短作业摊销边界，不自动更改87默认。"""
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
import psutil
from study_p16_direct_compile import Library,save,digest,env,direct
from channel_native import Chain
from bench_p16_model_pair import checked,source
from palette_support import info as palette_info
from suffix_cache_support import cache_info
from direct16_support import info as direct_info
from domain_cache_support import info as domain_info
from outplace_support import bind_to,apply_to,reject_to

def setup(plan):
    psutil.Process().cpu_affinity([0,2,4,6])
    dll_dir=os.add_dll_directory('E:/mingw64/bin') if os.name=='nt' else None
    lib=Library(checked(plan['library']),plan['library']['sha256']);assert lib.revision==88
    modelplan=json.loads(checked(plan['model_plan']).read_text(encoding='utf-8'))
    role=modelplan['roles']['baseline']
    paths=[checked(p) for p in role['models']];sides=[checked(p) if p else None for p in role['sidecars']]
    p=(ct.c_char_p*4)(*(str(v).encode('utf-8') for v in paths));s=(ct.c_char_p*4)(*(str(v).encode('utf-8') if v else None for v in sides))
    f=lib.dll.jshc_cc_create_policy
    f.argtypes=[ct.POINTER(ct.c_char_p),ct.POINTER(ct.c_char_p),ct.c_size_t,ct.c_uint32,ct.POINTER(ct.c_void_p),ct.POINTER(ct.c_char),ct.c_size_t];f.restype=ct.c_int
    return lib,modelplan,(p,s),dll_dir

def create(lib,arrays,policy,stages=4):
    handle=ct.c_void_p();error=ct.create_string_buffer(1024)
    start=time.perf_counter_ns();rc=lib.dll.jshc_cc_create_policy(*arrays,stages,policy,ct.byref(handle),error,len(error));duration=(time.perf_counter_ns()-start)*1e-9
    if rc:raise RuntimeError(error.value.decode('utf-8','replace'))
    chain=Chain.__new__(Chain);chain.library=lib;chain.handle=handle
    return chain,duration

def state(c):return {'model_bytes':c.model_bytes,'cache':cache_info(c),'domain':domain_info(c),'palette':palette_info(c),'direct':direct_info(c)}

def verify(args,plan):
    if args.output.exists():raise FileExistsError('保留已有验证')
    args.output.mkdir(parents=True);lib,mp,arrays,dll_dir=setup(plan)
    cube=np.memmap(checked(mp['roles']['baseline']['oracle']),dtype=np.uint8,mode='r',shape=(1<<24,3))
    chains={p:create(lib,arrays,p)[0] for p in (0,1)};states={p:state(c) for p,c in chains.items()}
    assert states[0]['direct']['enabled'] and not states[1]['direct']['enabled'] and states[1]['domain']['eligible']
    hashes={(p,k):hashlib.sha256() for p in (0,1) for k in ('scalar','in1','in4','to1','to4')}
    try:
        for begin in range(0,1<<24,1<<18):
            code=np.arange(begin,begin+(1<<18),dtype=np.uint32)
            src=np.stack([code>>16,(code>>8)&255,code&255],axis=1).astype(np.uint8);gold=cube[begin:begin+len(src)].tobytes()
            for policy,c in chains.items():
                raw=c.apply(src.copy(),kernel='scalar',threads=1).tobytes();assert raw==gold;hashes[policy,'scalar'].update(raw)
                for threads in (1,4):
                    raw=c.apply(src.copy(),kernel='avx2',threads=threads).tobytes();assert raw==gold;hashes[policy,f'in{threads}'].update(raw)
                    raw=apply_to(lib.dll,c.handle,src.tobytes(),1,threads);assert raw==gold;hashes[policy,f'to{threads}'].update(raw)
        finite=0;rng=np.random.default_rng(88)
        for n in (0,1,7,8,9,4095,4096,4097,65535,65536,65537,65793):
            src=rng.integers(0,256,(n,3),np.uint8);v=src.astype(np.uint32);gold=cube[(v[:,0]<<16)|(v[:,1]<<8)|v[:,2]].tobytes()
            for c in chains.values():
                for offset in (0,1,7,31,63):
                    for threads in (1,4):
                        for same in (False,True):assert apply_to(lib.dll,c.handle,src.tobytes(),1,threads,offset,63-offset,same)==gold;finite+=1
        rejected=sum(reject_to(lib.dll,c.handle) for c in chains.values())
        error=ct.create_string_buffer(1024)
        for bad in (2,0xffffffff):
            h=ct.c_void_p(123);assert lib.dll.jshc_cc_create_policy(*arrays,4,bad,ct.byref(h),error,len(error))==1 and not h.value
        paths=[Path(x['path']) for x in mp['roles']['baseline']['models']];sides=[Path(x['path']) if x else None for x in mp['roles']['baseline']['sidecars']]
        with lib.chain(paths,sides) as default:assert np.array_equal(direct(default),direct(chains[0]))
        outputs={f'{p}-{k}':h.hexdigest() for (p,k),h in hashes.items()};assert len(set(outputs.values()))==1
        save(args.output/'correctness.json',{'passed':True,'full_colors':1<<24,'byte_mismatches':0,'output_sha256':outputs,
            'states':states,'finite_cases':finite,'api_rejections':rejected,'policy_rejections':2,'old_create_matches_policy0':True,
            'library':plan['library'],'environment':env(),'scope':'完整域精确运行时；验证内prepare时长不作为性能结论'})
        save(args.output/'executed-plan.json',plan);print('两策略完整RGB8/边界/拒绝通过',flush=True)
    finally:
        for c in chains.values():c.close()

def cases(frames):
    for scale in (1,2):
        for n in (1,10,100):yield f's{scale}-n{n}',frames[:n,::scale,::scale].copy(),n,scale

def worker(args,plan):
    lib,mp,arrays,dll_dir=setup(plan);frames,_=source(mp);cube=np.memmap(checked(mp['roles']['baseline']['oracle']),dtype=np.uint8,mode='r',shape=(1<<24,3))
    d=lib.dll;u8=ct.POINTER(ct.c_uint8);f=d.jshc_cc_bench_to
    f.argtypes=[ct.c_void_p,u8,u8,ct.c_size_t,ct.c_int,ct.c_int,ct.c_size_t,ct.POINTER(ct.c_double),ct.POINTER(ct.c_char),ct.c_size_t];f.restype=ct.c_int
    records=[]
    for name,src,n,scale in cases(frames):
        expected=hashlib.sha256();shape=src.shape
        for frame in src:
            a=frame.astype(np.uint32);expected.update(cube[(a[:,:,0]<<16)|(a[:,:,1]<<8)|a[:,:,2]].tobytes())
        expected=expected.hexdigest();source_sha=hashlib.sha256(src.tobytes()).hexdigest()
        for threads in plan['thread_orders'][args.worker]:
            for repeat in range(3):
                for policy in plan['orders'][args.worker]:
                    work=np.empty_like(src);c,prepared=create(lib,arrays,policy)
                    with c:
                        error=ct.create_string_buffer(1024)
                        def run(repeats):
                            t=np.empty(repeats,np.float64)
                            assert not f(c.handle,src.ctypes.data_as(u8),work.ctypes.data_as(u8),src.nbytes,1,threads,repeats,t.ctypes.data_as(ct.POINTER(ct.c_double)),error,len(error)),error.value
                            assert hashlib.sha256(work.tobytes()).hexdigest()==expected
                            return t.tolist()
                        first=run(1)[0];steady=control=[]
                        if repeat==0:
                            rounds=plan['steady_repeats'][str(n)];steady=run(rounds);control=run(rounds)
                        records.append({'case':name,'images':n,'scale':scale,'pixels':src.size//3,'threads':threads,'repeat':repeat,'policy':policy,
                            'create_seconds':prepared,'first_outplace_seconds':first,'create_plus_first_seconds':prepared+first,
                            'steady':steady,'control':control,'output_sha256':expected,'model_bytes':c.model_bytes,'state':state(c) if repeat==0 else None})
                    save(args.output/f'worker{args.worker}-partial.json',{'records':records})
        assert hashlib.sha256(src.tobytes()).hexdigest()==source_sha
    save(args.output/f'worker{args.worker}.json',{'records':records,'environment':env()})

def measure(args,plan):
    if any(args.output.glob('worker*.json')):raise FileExistsError('保留已有性能原件')
    assert json.loads((args.output/'correctness.json').read_text(encoding='utf-8'))['passed']
    workers=[]
    for i in range(4):
        subprocess.run([sys.executable,'-X','utf8',__file__,'--plan',str(args.plan),'--output',str(args.output),'--mode','measure','--worker',str(i)],check=True)
        workers.append(json.loads((args.output/f'worker{i}.json').read_text(encoding='utf-8')));print('完成摊销配对进程',i,flush=True)
    rows=[]
    for scale in (1,2):
        for n in (1,10,100):
            for threads in (1,4):
                parts=[];controls=[]
                for w in workers:
                    subset=[r for r in w['records'] if r['scale']==scale and r['images']==n and r['threads']==threads]
                    p={v:[r for r in subset if r['policy']==v] for v in (0,1)}
                    parts.append({'create_ratio':st.median(r['create_seconds'] for r in p[1])/st.median(r['create_seconds'] for r in p[0]),
                        'first_ratio':st.median(r['first_outplace_seconds'] for r in p[1])/st.median(r['first_outplace_seconds'] for r in p[0]),
                        'end_to_end_ratio':st.median(r['create_plus_first_seconds'] for r in p[1])/st.median(r['create_plus_first_seconds'] for r in p[0]),
                        'steady_ratio':st.median(p[1][0]['steady'])/st.median(p[0][0]['steady'])})
                    controls.extend(st.median(p[v][0]['control'])/st.median(p[v][0]['steady']) for v in (0,1))
                valid=all(plan['control_min']<=v<=plan['control_max'] for v in controls)
                row={'scale':scale,'images':n,'threads':threads,'pairs':parts,'controls':controls,'control_valid':valid}
                for metric in ('create','first','end_to_end','steady'):
                    ratios=[p[metric+'_ratio'] for p in parts];row[metric]={'median_time_ratio':st.median(ratios),'worst_throughput_retained':1/max(ratios),
                        'grades':{str(v):valid and 1/max(ratios)>=v/100 for v in (100,90,80,70,60,50)}}
                rows.append(row)
    save(args.output/'results.json',{'scope':'显式suffix-only相对完整direct；端到端与纯稳态分开，不用前者掩盖后者低于50%。热文件缓存、无锁频控温，不外推官方。',
        'summary':rows,'worker_sha256':[digest(args.output/f'worker{i}.json') for i in range(4)],'default_policy_changed':False})
    print('摊销矩阵完成，端到端/稳态分档分别保留',flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--mode',choices=('verify','measure'),required=True);p.add_argument('--worker',type=int);a=p.parse_args()
    plan=json.loads(a.plan.read_text(encoding='utf-8'));assert digest(Path(__file__))==plan['script_sha256']
    if a.worker is not None:return worker(a,plan)
    return (verify if a.mode=='verify' else measure)(a,plan)
if __name__=='__main__':main()
