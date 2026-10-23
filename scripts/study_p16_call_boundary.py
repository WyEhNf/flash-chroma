"""只诊断同87已有入口的整批/逐图边界，不实现新的批API或推断纯fork成本。"""
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
import numpy as np
import psutil
from study_p16_direct_compile import Library,save,digest,env
from bench_p16_model_pair import checked,source
from outplace_support import bind_to
from palette_support import info as palette_info
from direct16_support import info as direct_info

def setup(plan):
    psutil.Process().cpu_affinity(plan['cpus']);directory=os.add_dll_directory('E:/mingw64/bin') if os.name=='nt' else None
    lib=Library(checked(plan['library']),plan['library']['sha256']);assert lib.revision==87
    bind_to(lib.dll);probe=ct.CDLL(str(checked(plan['probe'])));f=probe.jshc_call_boundary;u8=ct.POINTER(ct.c_uint8)
    f.argtypes=[ct.c_void_p,ct.c_void_p,u8,u8,ct.c_size_t,ct.c_size_t,ct.c_int,ct.c_int,ct.c_size_t,ct.POINTER(ct.c_double),ct.POINTER(ct.c_char),ct.c_size_t];f.restype=ct.c_int
    mp=json.loads(checked(plan['model_plan']).read_text(encoding='utf-8'));frames,manifest=source(mp)
    chains={}
    for name,role in plan['roles'].items():chains[name]=lib.chain([checked(p) for p in role['models']],[checked(p) if p else None for p in role['sidecars']])
    assert direct_info(chains['direct'])['enabled'] and not direct_info(chains['fallback'])['enabled']
    return lib,f,frames,chains,mp,directory,probe

def call(f,chain,src,work,mode,threads,repeats):
    samples=np.empty(repeats,np.float64);error=ct.create_string_buffer(1024);u8=ct.POINTER(ct.c_uint8)
    rc=f(ct.cast(chain.library.dll.jshc_cc_apply_to,ct.c_void_p),chain.handle,src.ctypes.data_as(u8),work.ctypes.data_as(u8),src[0].nbytes,len(src),mode,threads,repeats,samples.ctypes.data_as(ct.POINTER(ct.c_double)),error,len(error))
    assert not rc,error.value
    return samples.tolist()

def cases(plan,frames):
    for role in plan['roles']:
        for scale in plan['role_scales'][role]:
            for n in plan['images']:yield role,scale,n,frames[:n,::scale,::scale].copy()

def verify(args,plan):
    if args.output.exists():raise FileExistsError('保留已有验证')
    args.output.mkdir(parents=True);lib,f,frames,chains,mp,directory,probe=setup(plan);rows=[]
    try:
        for role,scale,n,src in cases(plan,frames):
            chain=chains[role];gold=chain.apply(src.copy(),kernel='scalar',threads=1);expected=hashlib.sha256(gold.tobytes()).hexdigest();work=np.empty_like(src)
            for mode in (0,1):
                for threads in (1,4):call(f,chain,src,work,mode,threads,1);assert np.array_equal(work,gold)
            rows.append({'role':role,'scale':scale,'images':n,'output_sha256':expected,'modes_threads_equal':True})
        # 不同图像边界会改变向量尾部和65536块；无对齐假设且不写源。
        finite=0;rng=np.random.default_rng(901)
        for role,c in chains.items():
            for pixels in (1,7,8,9,65535,65536,65537):
                src=rng.integers(0,256,(3,pixels,3),np.uint8);gold=c.apply(src.copy(),kernel='scalar',threads=1);before=src.tobytes()
                storage=np.full(src.nbytes+126,0xc7,np.uint8);work=np.ndarray(src.shape,np.uint8,buffer=storage,offset=63)
                for mode in (0,1):
                    for threads in (1,4):
                        call(f,c,src,work,mode,threads,1);assert np.array_equal(work,gold) and np.all(storage[:63]==0xc7) and np.all(storage[-63:]==0xc7);finite+=1
                assert src.tobytes()==before
        c=chains['direct'];u8=ct.POINTER(ct.c_uint8);src=np.zeros((1,8,3),np.uint8);work=np.full_like(src,0xc7)
        seconds=np.empty(1,np.float64);error=ct.create_string_buffer(1024)
        base=[ct.cast(lib.dll.jshc_cc_apply_to,ct.c_void_p),c.handle,src.ctypes.data_as(u8),work.ctypes.data_as(u8),src.nbytes,1,0,1,1,seconds.ctypes.data_as(ct.POINTER(ct.c_double)),error,len(error)]
        badcases=[{0:None},{1:None},{2:None},{3:None},{4:0},{4:1},{5:0},{5:101},{6:-1},{6:2},{7:0},{7:257},{8:0},{8:257},{9:None},{3:src.ctypes.data_as(u8)},
            {4:((2**(ct.sizeof(ct.c_size_t)*8)-1)//100//3+1)*3,5:100}]
        for bad in badcases:
            values=base.copy()
            for index,value in bad.items():values[index]=value
            assert f(*values)==1 and np.all(work==0xc7)
        assert hashlib.sha256(frames.tobytes()).hexdigest()=='e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd'
        save(args.output/'correctness.json',{'passed':True,'photos':rows,'finite_cases':finite,'rejection_cases':len(badcases),'library':plan['library'],'probe':plan['probe'],
            'state':{k:{'palette':palette_info(c),'direct':direct_info(c),'model_bytes':c.model_bytes} for k,c in chains.items()},'environment':env(),
            'scope':'9照片形状/模型×2模式×1/4请求和56非整8/非整块合同；未重跑模型完整RGB8拟合精度。'})
        save(args.output/'executed-plan.json',plan);print('调用边界两模式、两模型照片及有限合同通过',flush=True)
    finally:
        for c in chains.values():c.close()

def worker(args,plan):
    lib,f,frames,chains,mp,directory,probe=setup(plan);proof=json.loads((args.output/'correctness.json').read_text(encoding='utf-8'));records=[]
    expected={(r['role'],r['scale'],r['images']):r['output_sha256'] for r in proof['photos']}
    try:
        for role,scale,n,src in cases(plan,frames):
            src_sha=hashlib.sha256(src.tobytes()).hexdigest();work=np.empty_like(src)
            for threads in plan['thread_orders'][args.worker]:
                for mode in plan['orders'][args.worker]:
                    call(f,chains[role],src,work,mode,threads,plan['warm_repeats'])
                    samples=call(f,chains[role],src,work,mode,threads,plan['repeats'][str(n)])
                    assert hashlib.sha256(work.tobytes()).hexdigest()==expected[role,scale,n]
                    control=call(f,chains[role],src,work,mode,threads,plan['repeats'][str(n)])
                    assert hashlib.sha256(work.tobytes()).hexdigest()==expected[role,scale,n]
                    records.append({'role':role,'scale':scale,'images':n,'threads':threads,'mode':mode,'seconds':samples,'control':control,
                        'source_sha256':src_sha,'output_sha256':expected[role,scale,n]})
                    save(args.output/f'worker{args.worker}-partial.json',{'records':records})
            assert hashlib.sha256(src.tobytes()).hexdigest()==src_sha
        save(args.output/f'worker{args.worker}.json',{'records':records,'environment':env()})
    finally:
        for c in chains.values():c.close()

def measure(args,plan):
    if any(args.output.glob('worker*.json')):raise FileExistsError('保留原始轮次，不择优重跑')
    assert json.loads((args.output/'correctness.json').read_text(encoding='utf-8'))['passed'];workers=[]
    for i in range(4):
        subprocess.run([sys.executable,'-X','utf8',__file__,'--plan',str(args.plan),'--output',str(args.output),'--mode','measure','--worker',str(i)],check=True)
        workers.append(json.loads((args.output/f'worker{i}.json').read_text(encoding='utf-8')));print('完成调用边界进程',i,flush=True)
    rows=[]
    for p in json.loads((args.output/'correctness.json').read_text(encoding='utf-8'))['photos']:
        for threads in (1,4):
            ratios=[];controls=[]
            for w in workers:
                pair={r['mode']:r for r in w['records'] if (r['role'],r['scale'],r['images'],r['threads'])==(p['role'],p['scale'],p['images'],threads)}
                ratios.append(st.median(pair[0]['seconds'])/st.median(pair[1]['seconds']))
                controls.extend(st.median(pair[m]['control'])/st.median(pair[m]['seconds']) for m in (0,1))
            valid=all(plan['control_min']<=v<=plan['control_max'] for v in controls)
            rows.append({'role':p['role'],'scale':p['scale'],'images':p['images'],'threads':threads,'bulk_over_loop_ratios':ratios,'median_ratio':st.median(ratios),
                'worst_retained':1/max(ratios),'controls':controls,'control_valid':valid,
                'grades':{str(g):valid and 1/max(ratios)>=g/100 for g in plan['grades']}})
    save(args.output/'results.json',{'summary':rows,'worker_sha256':[digest(args.output/f'worker{i}.json') for i in range(4)],
        'scope':'已有87连续整批相对逐图串行API调用的诊断，不是新批API收益。4线程块分配/小图有效worker数也不同，不能相减叫纯fork/join。未优化模型或默认。'})

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--mode',choices=('verify','measure'),required=True);p.add_argument('--worker',type=int);a=p.parse_args()
    plan=json.loads(a.plan.read_text(encoding='utf-8'));assert digest(Path(__file__))==plan['script_sha256']
    if a.worker is not None:return worker(a,plan)
    return (verify if a.mode=='verify' else measure)(a,plan)
if __name__=='__main__':main()
