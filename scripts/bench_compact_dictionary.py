"""同机同模型比较100..50%速度底线；记录各原始轮次、两种接口和独立进程RSS。"""
from __future__ import annotations
import argparse
import ctypes as ct
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time
import numpy as np
from study_memory_rom import Model,U8,ROOT,sha,save,read,env,native,create,romlib,loadrom

class Counters(ct.Structure):
    _fields_=[('cb',ct.c_uint32),('PageFaultCount',ct.c_uint32),*[ (x,ct.c_size_t) for x in ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage')]]
def memory():
    c=Counters();c.cb=ct.sizeof(c);p=ct.windll.kernel32.GetCurrentProcess;p.restype=ct.c_void_p
    f=ct.windll.psapi.GetProcessMemoryInfo;f.argtypes=[ct.c_void_p,ct.c_void_p,ct.c_uint32]
    if not f(p(),ct.byref(c),ct.sizeof(c)):raise ct.WinError()
    return {name:getattr(c,name) for name in ('PeakWorkingSetSize','WorkingSetSize','PrivateUsage','PeakPagefileUsage')}

def labels():return ['ref78','ref80','dict32','avx2_24','avx2_17','c99_24','c99_17']
def setup(a,label):
    if label=='dict32':
        plan=read(ROOT/'experiments/compact-dictionary-v1.json');path=Path(plan['reference32']['path']);rom=Path(plan['input_rom_path'])
        if sha(path)!=plan['reference32']['sha256'] or sha(rom)!=plan['input_rom_sha256']:raise ValueError('原32bit字典身份变化')
        d=romlib(path);m,keep=loadrom(d,rom)
        def apply(source,target,n,threads,mode):return d.jshc_mem_apply_parallel(ct.byref(m),target if mode=='inplace' else source,target,n,1,threads)
        return apply,(d,m,keep),rom.stat().st_size+ct.sizeof(Model),str(path),sha(path)

    if label in ('ref78','ref80','specialized'):
        path={'ref78':a.build/'jshc_memory_ref78.dll','ref80':a.ref80,'specialized':a.data_root/'artifacts/channel-native-specialized-v1/jshc_channel_specialized.dll'}[label]
        d=native(path) if label!='specialized' else None
        if d is None:
            d=ct.CDLL(str(path));text=ct.POINTER(ct.c_char)
            d.jshc_cc_create.argtypes=[ct.POINTER(ct.c_char_p),ct.POINTER(ct.c_char_p),ct.c_size_t,ct.POINTER(ct.c_void_p),text,ct.c_size_t]
            d.jshc_cc_destroy.argtypes=[ct.c_void_p];d.jshc_cc_model_bytes.argtypes=[ct.c_void_p];d.jshc_cc_model_bytes.restype=ct.c_size_t
            d.jshc_cc_apply.argtypes=[ct.c_void_p,U8,ct.c_size_t,ct.c_int,ct.c_int,text,ct.c_size_t]
        h=create(d,a.data_root);err=ct.create_string_buffer(1024)
        if label!='specialized':d.jshc_cc_apply_to.argtypes=[ct.c_void_p,U8,U8,ct.c_size_t,ct.c_int,ct.c_int,ct.POINTER(ct.c_char),ct.c_size_t]
        def apply(source,target,n,threads,mode):
            if mode=='inplace':return d.jshc_cc_apply(h,target,n*3,1,threads,err,1024)
            return d.jshc_cc_apply_to(h,source,target,n*3,1,threads,err,1024)
        return apply,(d,h),d.jshc_cc_model_bytes(h),str(path),sha(path)
    backend,bits=label.split('_');bits=int(bits)
    path=a.build/'jshc_memory_rom.dll';d=romlib(path);m,keep=loadrom(d,a.roms/f'rom-{bits}.bin')
    def apply(source,target,n,threads,mode):return d.jshc_mem_apply_parallel(ct.byref(m),target if mode=='inplace' else source,target,n,1 if backend=='avx2' else 0,threads)
    return apply,(d,m,keep),(a.roms/f'rom-{bits}.bin').stat().st_size+ct.sizeof(Model),str(path),sha(path)

def worker(a):
    out=a.output;out.mkdir(parents=True,exist_ok=False)
    if a.rss:
        before=memory();fn,keep,capacity,path,libsha=setup(a,a.rss);after=memory()
        save(out/'rss.json',dict(label=a.rss,before=before,prepared=after,model_capacity=capacity,library=path,library_sha256=libsha,environment=env(),scope='独立新进程；模型准备后立刻读取Windows进程工作集与峰值，尚未分配图片。不是扣除运行库后的纯模型RSS。'))
        return
    photo=a.data_root/'artifacts/skylake-server-matrix-v1/server-inputs/photos.rgb'
    if sha(photo)!='e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd':raise ValueError('输入SHA不同')
    src=np.memmap(photo,dtype=np.uint8,mode='r');dst=np.empty(len(src),dtype=np.uint8);n=len(src)//3
    source=src.ctypes.data_as(U8);target=dst.ctypes.data_as(U8)
    operators={label:setup(a,label) for label in labels()};rows=[];controls=[];identities={label:dict(capacity=x[2],library=x[3],library_sha256=x[4]) for label,x in operators.items()}
    order=labels();shift=a.worker_index%len(order);order=order[shift:]+order[:shift]
    if a.worker_index%2:order=list(reversed(order))
    threads=[1,4] if a.worker_index%2==0 else [4,1]
    for t in threads:
        for mode in ('inplace','outplace'):
            for label in order:
                if mode=='outplace' and label=='specialized':continue
                fn=operators[label][0];times=[]
                for r in range(a.repeats+1):
                    np.copyto(dst,src)
                    start=time.perf_counter()
                    if fn(source,target,n,t,mode):raise AssertionError('映射失败：'+label)
                    elapsed=time.perf_counter()-start
                    if r:times.append(elapsed)
                    if r==0 or r==a.repeats:
                        if __import__('hashlib').sha256(dst).hexdigest()!='f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528':raise AssertionError('百图SHA不同：'+label)
                rows.append(dict(label=label,threads=t,mode=mode,seconds=times,median_seconds=statistics.median(times)))
                save(out/'partial.json',dict(rows=rows))
            times=[];fn=operators['ref80'][0]
            for r in range(a.repeats):
                np.copyto(dst,src);start=time.perf_counter()
                if fn(source,target,n,t,mode):raise AssertionError('A/A调用失败')
                times.append(time.perf_counter()-start)
            primary=next(r['median_seconds'] for r in rows if r['label']=='ref80' and r['mode']==mode and r['threads']==t)
            controls.append(dict(threads=t,mode=mode,seconds=times,ratio=statistics.median(times)/primary))
    save(out/'results.json',dict(environment=env(),worker_index=a.worker_index,script_sha256=sha(__file__),order=order,thread_order=threads,roles=identities,rows=rows,controls=controls,memory=memory(),photos=dict(path=str(photo),sha256=sha(photo),bytes=len(src)),purpose=__doc__))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for field in ('build','roms','ref80','data-root','output'):p.add_argument('--'+field,type=Path,required=True)
    p.add_argument('--worker-index',type=int);p.add_argument('--rss');p.add_argument('--repeats',type=int,default=5)
    a=p.parse_args()
    plan=read(ROOT/'experiments/compact-dictionary-v1.json')
    if any(sha(ROOT/n)!=v for n,v in plan['source_sha256'].items()) or a.repeats!=5:raise ValueError('冻结源/五轮协议变化')
    if a.worker_index is not None or a.rss:return worker(a)
    a.output.mkdir(parents=True,exist_ok=False);records=[]
    common=[sys.executable,'-X','utf8',str(Path(__file__).resolve()),'--build',str(a.build),'--roms',str(a.roms),'--ref80',str(a.ref80),'--data-root',str(a.data_root),'--repeats',str(a.repeats)]
    for i in range(4):
        out=a.output/f'worker-{i}';r=subprocess.run(common+['--worker-index',str(i),'--output',str(out)],capture_output=True,text=True,encoding='utf-8');records.append(dict(command=r.args,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));save(a.output/'execution.json',records)
        if r.returncode:raise RuntimeError(r.stderr)
    for label in labels():
        out=a.output/('rss-'+label);r=subprocess.run(common+['--rss',label,'--output',str(out)],capture_output=True,text=True,encoding='utf-8');records.append(dict(command=r.args,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));save(a.output/'execution.json',records)
        if r.returncode:raise RuntimeError(r.stderr)
    workers=[read(a.output/f'worker-{i}/results.json') for i in range(4)];ratios=[];tiers={}
    for mode in ('inplace','outplace'):
        for threads in (1,4):
            lookup=[{r['label']:r['median_seconds'] for r in w['rows'] if r['mode']==mode and r['threads']==threads} for w in workers]
            for label in lookup[0]:
                # 同场两个冻结最佳端点，按每进程较快值设保守分母，避免拼历史最快值。
                retains=[min(w['ref78'],w['ref80'])/w[label] for w in lookup]
                ratios.append(dict(label=label,mode=mode,threads=threads,speed_retention=statistics.median(retains),per_worker=retains,capacity=workers[0]['roles'][label]['capacity'],accuracy_retention=1.0))
            eligible=[r for r in ratios if r['mode']==mode and r['threads']==threads]
            tiers[f'{mode}_{threads}']={str(t):min([r for r in eligible if min(r['per_worker'])>=t/100],key=lambda r:r['capacity'],default=None) for t in (100,90,80,70,60,50)}
    controls={}
    for mode in ('inplace','outplace'):
        for t in (1,4):
            values=[next(c['ratio'] for c in w['controls'] if c['mode']==mode and c['threads']==t) for w in workers]
            controls[f'{mode}_{t}']=dict(ratios=values,median=statistics.median(values),pass_=all(.8<=x<=1.25 for x in values) and 1/1.1<=statistics.median(values)<=1.1)
    for key,control in controls.items():
        if not control['pass_']:tiers[key]={str(t):None for t in (100,90,80,70,60,50)}
    save(a.output/'summary.json',dict(purpose=__doc__,script_sha256=sha(__file__),plan_sha256=sha(ROOT/'experiments/compact-dictionary-v1.json'),ratios=ratios,tiers=tiers,gate='精度mean/p99/max及逐图输出全部不变；速度主判使用四进程中最劣吞吐保留率，另列中位；同候选可占多档。A/A控制失败的档位只作描述观察，不正式优选。',controls=controls,method='四进程轮转/反序；每角色每线程每接口一次预热和5次全百图；未锁频/绑核；线程竞争由root安排排他窗口。',rss={label:read(a.output/('rss-'+label)/'rss.json') for label in labels()}))
    print(json.dumps({'summary':str(a.output/'summary.json'),'tiers':tiers},ensure_ascii=False))
if __name__=='__main__':main()
