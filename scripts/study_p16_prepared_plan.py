"""验证显式准备snapshot所有权，并区分首次prepare、多owner生命周期与纯映射。"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import statistics as st
import subprocess
import sys
import threading
import time
import numpy as np
import psutil
from study_p16_direct_compile import Library,save,digest,env
from channel_native import Chain
from bench_p16_model_pair import checked,source
from outplace_support import apply_to

class PlanInfo(ct.Structure):
    _fields_=[('version',ct.c_uint32),('reserved',ct.c_uint32),('generation',ct.c_uint64),('owners',ct.c_uint64)]

def setup(plan):
    psutil.Process().cpu_affinity(plan['cpus'])
    directory=os.add_dll_directory('E:/mingw64/bin') if os.name=='nt' else None
    libs={k:Library(checked(v),v['sha256']) for k,v in plan['libraries'].items()}
    assert libs['baseline'].revision==87 and libs['candidate'].revision==89
    d=libs['candidate'].dll
    d.jshc_cc_get_plan_info.argtypes=[ct.c_void_p,ct.POINTER(PlanInfo),ct.c_size_t];d.jshc_cc_get_plan_info.restype=ct.c_int
    d.jshc_cc_acquire_plan.argtypes=[ct.c_void_p,ct.c_uint64,ct.POINTER(ct.c_void_p),ct.POINTER(ct.c_char),ct.c_size_t];d.jshc_cc_acquire_plan.restype=ct.c_int
    mp=json.loads(checked(plan['model_plan']).read_text(encoding='utf-8'));role=mp['roles']['baseline']
    paths=[checked(p) for p in role['models']];sides=[checked(p) if p else None for p in role['sidecars']]
    arrays=((ct.c_char_p*4)(*(str(p).encode('utf-8') for p in paths)),(ct.c_char_p*4)(*(str(p).encode('utf-8') if p else None for p in sides)))
    return libs,arrays,mp,directory

def wrap(lib,h):
    chain=Chain.__new__(Chain);chain.library=lib;chain.handle=h;return chain
def create(lib,arrays):
    h=ct.c_void_p();error=ct.create_string_buffer(1024)
    begin=time.perf_counter_ns();rc=lib.dll.jshc_cc_create(*arrays,4,ct.byref(h),error,len(error));elapsed=(time.perf_counter_ns()-begin)*1e-9
    if rc:raise RuntimeError(error.value.decode('utf-8','replace'))
    return wrap(lib,h),elapsed
def info(c):
    out=PlanInfo();assert not c.library.dll.jshc_cc_get_plan_info(c.handle,ct.byref(out),ct.sizeof(out))
    return {n:int(getattr(out,n)) for n,_ in out._fields_}
def acquire(c,generation):
    h=ct.c_void_p();error=ct.create_string_buffer(1024)
    if c.library.dll.jshc_cc_acquire_plan(c.handle,generation,ct.byref(h),error,len(error)):raise RuntimeError(error.value.decode('utf-8','replace'))
    return wrap(c.library,h)

def verify(args,plan):
    if args.output.exists():raise FileExistsError('保留原始验证')
    args.output.mkdir(parents=True);libs,arrays,mp,directory=setup(plan)
    runtime=args.output/'runtime'
    subprocess.run([sys.executable,'-X','utf8',str(Path(__file__).with_name('study_p16_direct_compile.py')),'--mode','verify',
        '--data-root',mp['data_root'],'--baseline',str(libs['baseline'].path),'--candidate',str(libs['candidate'].path),'--output',str(runtime)],check=True,stdout=subprocess.DEVNULL)
    proof=json.loads((runtime/'correctness.json').read_text(encoding='utf-8'))
    assert proof['passed'] and set(proof['output_sha256'].values())=={mp['roles']['baseline']['oracle']['sha256']}
    c,_=create(libs['candidate'],arrays);initial=info(c);assert initial['owners']==1
    generation=initial['generation'];error=ct.create_string_buffer(1024);rejections=0
    for handle,expected,out in ((c.handle,generation^1,True),(None,generation,True),(c.handle,generation,False)):
        output=ct.c_void_p(123)
        rc=c.library.dll.jshc_cc_acquire_plan(handle,expected,ct.byref(output) if out else None,error,len(error))
        assert rc==1 and (not out or not output.value);rejections+=1
    p=PlanInfo()
    for handle,size in ((None,ct.sizeof(p)),(c.handle,0)):
        assert c.library.dll.jshc_cc_get_plan_info(handle,ct.byref(p),size)==1;rejections+=1
    aliases=[acquire(c,generation) for _ in range(3)];assert info(c)['owners']==4
    assert all(x.handle.value==c.handle.value for x in aliases)
    c.close();assert info(aliases[0])['owners']==3
    src=np.random.default_rng(89).integers(0,256,(4097,3),np.uint8)
    with libs['baseline'].chain([Path(p['path']) for p in mp['roles']['baseline']['models']],
            [Path(p['path']) if p else None for p in mp['roles']['baseline']['sidecars']]) as baseline:
        gold=baseline.apply(src.copy(),kernel='scalar',threads=1).tobytes()
    for alias in aliases:assert alias.apply(src.copy(),kernel='avx2',threads=1).tobytes()==gold
    for alias in aliases[1:]:alias.close()
    root=aliases[0];assert info(root)['owners']==1
    # 保持root存活，四个独立owner同时读plan且处理不同目标；最后一方在barrier检查计数。
    def check_live():assert info(root)['owners']==5
    live=threading.Barrier(4,action=check_live);released=threading.Barrier(4)
    def thread_work(_):
        for _ in range(plan['concurrent_rounds']):
            alias=acquire(root,generation);live.wait(timeout=10)
            assert apply_to(alias.library.dll,alias.handle,src.tobytes(),1,1)==gold
            alias.close();released.wait(timeout=10)
    with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(thread_work,range(4)))
    assert info(root)['owners']==1;root.close()
    # 修改专用临时副本而非模型原件；已有snapshot不重载，新create仍读当前路径。
    original=Path(mp['roles']['baseline']['models'][0]['path']);temp=args.output/'stale-first.slut';temp.write_bytes(original.read_bytes())
    altered=(ct.c_char_p*4)(str(temp.resolve()).encode('utf-8'),*list(arrays[0])[1:])
    c,_=create(libs['candidate'],(altered,arrays[1]));old_generation=info(c)['generation'];temp.write_bytes('已改变的非法SLUT'.encode('utf-8'))
    alias=acquire(c,old_generation);c.close();assert alias.apply(src.copy(),kernel='avx2',threads=1).tobytes()==gold;alias.close()
    output=ct.c_void_p(123);assert libs['candidate'].dll.jshc_cc_create(altered,arrays[1],4,ct.byref(output),error,len(error))==1 and not output.value
    save(args.output/'correctness.json',{'passed':True,'runtime_proof_sha256':digest(runtime/'correctness.json'),'runtime_output_sha256':proof['output_sha256'],
        'initial_info':initial,'lifecycle_rejections':rejections,'outlives_original_owner':True,'same_pointer_different_owners':True,
        'concurrent_owners':4,'concurrent_rounds':plan['concurrent_rounds'],'concurrent_disjoint_output_equal':True,'final_owner_count_before_destroy':1,
        'stale_snapshot':{'old_snapshot_equal':True,'fresh_create_rejected_changed_file':True,'original_sha256':digest(original),'changed_copy_sha256':digest(temp),
            'semantics':'generation只识别存活实例；snapshot不读取后续文件变化，不是路径SHA自动校验'},'environment':env()})
    save(args.output/'executed-plan.json',plan);print('89完整域及显式owner/错实例/并发/文件snapshot语义通过',flush=True)

def worker(args,plan):
    libs,arrays,mp,directory=setup(plan);records=[];proc=psutil.Process()
    for n in plan['owner_counts']:
        for repeat in range(plan['lifecycle_repeats']):
            for variant in plan['orders'][args.worker]:
                lib=libs[variant];chains=[];native_create=[];before=proc.memory_info()._asdict()
                begin=time.perf_counter_ns()
                first,duration=create(lib,arrays);chains.append(first);native_create.append(duration)
                if variant=='candidate':
                    generation=info(first)['generation'] if n>1 else None
                    for _ in range(n-1):chains.append(acquire(first,generation))
                else:
                    for _ in range(n-1):
                        c,duration=create(lib,arrays);chains.append(c);native_create.append(duration)
                construct=(time.perf_counter_ns()-begin)*1e-9;after=proc.memory_info()._asdict()
                unique={c.handle.value:c.model_bytes for c in chains}
                owners=info(first)['owners'] if variant=='candidate' else None
                assert len(unique)==(1 if variant=='candidate' else n) and (owners is None or owners==n)
                begin=time.perf_counter_ns()
                for c in reversed(chains):c.close()
                destroy=(time.perf_counter_ns()-begin)*1e-9
                records.append({'owners':n,'repeat':repeat,'variant':variant,'construct_wall_seconds':construct,'native_create_seconds':native_create,
                    'destroy_wall_seconds':destroy,'unique_capacity_bytes':sum(unique.values()),'unique_handles':len(unique),'owner_count':owners,
                    'memory_before':before,'memory_after_construct':after,'memory_after_destroy':proc.memory_info()._asdict()})
                save(args.output/f'worker{args.worker}-partial.json',{'lifecycle':records})
    frames,_=source(mp);expected='f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528';mapping=[]
    for variant in plan['orders'][args.worker]:
        c,prepared=create(libs[variant],arrays)
        with c:
            if variant=='candidate':
                alias=acquire(c,info(c)['generation']);c.close();c=alias
            try:
                for threads in plan['thread_orders'][args.worker]:
                    assert hashlib.sha256(c.apply(frames.copy(),kernel='avx2',threads=threads).tobytes()).hexdigest()==expected
                    a=c.bench(frames,kernel='avx2',threads=threads,repeats=plan['mapping_repeats'])
                    d=c.library.dll;u8=ct.POINTER(ct.c_uint8);f=d.jshc_cc_bench_to
                    f.argtypes=[ct.c_void_p,u8,u8,ct.c_size_t,ct.c_int,ct.c_int,ct.c_size_t,ct.POINTER(ct.c_double),ct.POINTER(ct.c_char),ct.c_size_t];f.restype=ct.c_int
                    dst=np.empty_like(frames);t=np.empty(plan['mapping_repeats'],np.float64);err=ct.create_string_buffer(1024)
                    def run_to():
                        assert not f(c.handle,frames.ctypes.data_as(u8),dst.ctypes.data_as(u8),frames.nbytes,1,threads,t.size,t.ctypes.data_as(ct.POINTER(ct.c_double)),err,len(err))
                        assert hashlib.sha256(dst.tobytes()).hexdigest()==expected
                        return t.tolist()
                    outplace=run_to()
                    control=c.bench(frames,kernel='avx2',threads=threads,repeats=plan['mapping_repeats'])
                    control_to=run_to()
                    mapping.append({'variant':variant,'threads':threads,'apply':a['apply_seconds'],'outplace':outplace,'control':control['apply_seconds'],'control_outplace':control_to,'output_sha256':expected,
                        'prepare_seconds':prepared,'model_bytes':c.model_bytes})
            finally:c.close()
    save(args.output/f'worker{args.worker}.json',{'lifecycle':records,'mapping':mapping,'source_sha256':hashlib.sha256(frames.tobytes()).hexdigest(),'environment':env()})

def measure(args,plan):
    if any(args.output.glob('worker*.json')):raise FileExistsError('保留已有性能原件')
    assert json.loads((args.output/'correctness.json').read_text(encoding='utf-8'))['passed'];workers=[]
    for i in range(4):
        subprocess.run([sys.executable,'-X','utf8',__file__,'--plan',str(args.plan),'--output',str(args.output),'--mode','measure','--worker',str(i)],check=True)
        workers.append(json.loads((args.output/f'worker{i}.json').read_text(encoding='utf-8')));print('完成snapshot配对进程',i,flush=True)
    controls=[];mapping=[]
    for threads in (1,4):
        pairs=[{r['variant']:r for r in w['mapping'] if r['threads']==threads} for w in workers]
        for p in pairs:
            for v in ('baseline','candidate'):
                controls.extend((st.median(p[v]['control'])/st.median(p[v]['apply']),st.median(p[v]['control_outplace'])/st.median(p[v]['outplace'])))
        row={'threads':threads}
        for metric in ('apply','outplace'):
            ratios=[st.median(p['candidate'][metric])/st.median(p['baseline'][metric]) for p in pairs]
            row[metric]={'ratios':ratios,'median_ratio':st.median(ratios),'worst_retained':1/max(ratios)}
        mapping.append(row)
    valid=all(plan['control_min']<=v<=plan['control_max'] for v in controls)
    for row in mapping:
        for metric in ('apply','outplace'):row[metric]['grades']={str(g):valid and row[metric]['worst_retained']>=g/100 for g in plan['grades']}
    lifecycle=[]
    for n in plan['owner_counts']:
        pairs=[{v:[r for r in w['lifecycle'] if r['owners']==n and r['variant']==v] for v in ('baseline','candidate')} for w in workers]
        ratios=[st.median(r['construct_wall_seconds'] for r in p['candidate'])/st.median(r['construct_wall_seconds'] for r in p['baseline']) for p in pairs]
        lifecycle.append({'owners':n,'construct_ratios':ratios,'median_ratio':st.median(ratios),'worst_retained':1/max(ratios),
            'capacity_bytes':{v:sorted({r['unique_capacity_bytes'] for p in pairs for r in p[v]}) for v in ('baseline','candidate')}})
    save(args.output/'results.json',{'mapping':mapping,'controls':controls,'control_valid':valid,'lifecycle':lifecycle,
        'worker_sha256':[digest(args.output/f'worker{i}.json') for i in range(4)],
        'scope':'首次prepare全算；1/10/100个显式owner独立于标准100图单句柄纯映射。内存仅构造后工作集采样与容量，不冒充进程峰值/RSS减幅。'})
    print('snapshot生命周期与纯映射分离测量完成',flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--mode',choices=('verify','measure'),required=True);p.add_argument('--worker',type=int);a=p.parse_args()
    plan=json.loads(a.plan.read_text(encoding='utf-8'));assert digest(Path(__file__))==plan['script_sha256']
    if a.worker is not None:return worker(a,plan)
    return (verify if a.mode=='verify' else measure)(a,plan)
if __name__=='__main__':main()
