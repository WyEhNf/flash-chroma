"""M16T六角色受控同场测量；四worker双接口单四线程，完整五轮不补跑。"""
import ctypes as ct
import hashlib
import os
from pathlib import Path
import statistics
import sys
import time
import bench_memory_rom as bench
from bench_le16_block1024 import affinity,control_affinity,ALLOWED,K32
from study_memory_rom import ROOT,Model,U8,romlib,loadrom,sha,read,save,env

original_setup=bench.setup
def actual(d,path):
    get=ct.windll.kernel32.GetModuleFileNameW;get.argtypes=[ct.c_void_p,ct.c_wchar_p,ct.c_uint32];buffer=ct.create_unicode_buffer(32768)
    if not get(d._handle,buffer,len(buffer)) or Path(buffer.value).resolve()!=path.resolve():raise AssertionError('DLL实际路径不同')
def setup(a,label):
    plan=read(ROOT/'experiments/tagged-block16-native-v1.json')
    if label in ('ref78','ref80'):
        result=original_setup(a,label);actual(result[1][0],Path(result[3]));return result
    if label in ('old32','old3B'):path=Path(plan[label]['library']);rom=Path(plan[label]['rom'])
    else:path=a.build/'jshc_memory_tag16.dll';rom=a.roms/'rom-4.bin'
    d=romlib(path);actual(d,path);d.jshc_mem_model_size.restype=ct.c_size_t
    if d.jshc_mem_model_size()!=ct.sizeof(Model):raise AssertionError('实际ABI不是1056B')
    m,keep=loadrom(d,rom)
    def apply(source,target,n,threads,mode):return d.jshc_mem_apply_parallel(ct.byref(m),target if mode=='inplace' else source,target,n,0 if label=='tag_c99' else 1,threads)
    return apply,(d,m,keep),rom.stat().st_size+ct.sizeof(Model),str(path),sha(path)

def worker(a):
    out=a.output;out.mkdir(parents=True,exist_ok=False)
    if a.rss:
        before=bench.memory();fn,keep,capacity,path,libsha=setup(a,a.rss);after=bench.memory()
        save(out/'rss.json',dict(label=a.rss,before=before,prepared=after,model_capacity=capacity,library=path,library_sha256=libsha,environment=env(),affinity_start=START_AFFINITY,affinity_end=affinity(),scope='独立新进程，同import群和固定process mask0x55；照片数组分配前，含Python/库/流式预检，不是纯核心RAM。'));return
    photo=a.data_root/'artifacts/skylake-server-matrix-v1/server-inputs/photos.rgb'
    if sha(photo)!='e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd':raise ValueError('照片SHA不同')
    src=bench.np.memmap(photo,dtype=bench.np.uint8,mode='r');dst=bench.np.empty(len(src),dtype=bench.np.uint8);n=len(src)//3;source=src.ctypes.data_as(U8);target=dst.ctypes.data_as(U8);operators={label:setup(a,label) for label in bench.labels()};rows=[];controls=[];identities={label:dict(capacity=x[2],library=x[3],library_sha256=x[4]) for label,x in operators.items()};order=bench.labels();shift=a.worker_index%len(order);order=order[shift:]+order[:shift]
    if a.worker_index%2:order=list(reversed(order))
    threads=[1,4] if a.worker_index%2==0 else [4,1]
    def call(fn,label,t,mode,phase,index):
        cpu_before=int(K32.GetCurrentProcessorNumber());start=time.perf_counter();rc=fn(source,target,n,t,mode);elapsed=time.perf_counter()-start;cpu_after=int(K32.GetCurrentProcessorNumber());record=dict(label=label,threads=t,mode=mode,phase=phase,index=index,seconds=elapsed,cpu_before=cpu_before,cpu_after=cpu_after)
        if rc or cpu_before not in ALLOWED or cpu_after not in ALLOWED:
            save(out/'failed-call.json',dict(call=record,returncode=rc,affinity=affinity(),rows=rows,controls=controls));raise AssertionError('调用失败或CPU不在预定mask；不补跑')
        return elapsed,record
    for t in threads:
        for mode in ('inplace','outplace'):
            for label in order:
                fn=operators[label][0];times=[];cpu_calls=[]
                for r in range(a.repeats+1):
                    bench.np.copyto(dst,src);elapsed,record=call(fn,label,t,mode,'warmup' if r==0 else 'measure',r);cpu_calls.append(record)
                    if r:times.append(elapsed)
                    if r==0 or r==a.repeats:
                        if hashlib.sha256(dst).hexdigest()!='f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528':raise AssertionError('百图SHA不同')
                rows.append(dict(label=label,threads=t,mode=mode,seconds=times,median_seconds=statistics.median(times),cpu_calls=cpu_calls));save(out/'partial.json',dict(rows=rows))
            times=[];cpu_calls=[];fn=operators['ref80'][0]
            for r in range(a.repeats):
                bench.np.copyto(dst,src);elapsed,record=call(fn,'ref80',t,mode,'control',r);times.append(elapsed);cpu_calls.append(record)
            primary=next(row['median_seconds'] for row in rows if row['label']=='ref80' and row['mode']==mode and row['threads']==t);controls.append(dict(threads=t,mode=mode,seconds=times,ratio=statistics.median(times)/primary,cpu_calls=cpu_calls))
    final=affinity()
    if final['allowed']!=list(ALLOWED):raise AssertionError('测后process mask变化')
    save(out/'results.json',dict(environment=env(),worker_index=a.worker_index,script_sha256=sha(__file__),order=order,thread_order=threads,roles=identities,rows=rows,controls=controls,memory=bench.memory(),photos=dict(path=str(photo),sha256=sha(photo),bytes=len(src)),affinity_start=START_AFFINITY,affinity_end=final,source_address=hex(ct.cast(source,ct.c_void_p).value),target_address=hex(ct.cast(target,ct.c_void_p).value),purpose=__doc__,scope='所有CPU号查询在native wall计时区间外；固定process mask不是逐OMP线程绑定，不能据此证明旧unbound漂移因果。'))
if __name__=='__main__':
    path=ROOT/'experiments/tagged-block16-native-v1.json';plan=read(path)
    if any(sha(ROOT/n)!=v for n,v in plan['source_sha256'].items()) or any(sha(n)!=v for n,v in plan['input_sha256'].items()):raise AssertionError('冻结源/输入不同')
    if '--repeats' in sys.argv and int(sys.argv[sys.argv.index('--repeats')+1])!=5:raise AssertionError('只允许完整五轮')
    os.environ['OMP_PROC_BIND']='false';os.environ.pop('OMP_PLACES',None);START_AFFINITY=control_affinity();module=Path(bench.__file__);bench.labels=lambda:['ref78','ref80','old32','old3B','tag_avx','tag_c99'];bench.setup=setup;bench.worker=worker;bench.__file__=__file__;bench.main();output=Path(sys.argv[sys.argv.index('--output')+1]);summary=output/'summary.json'
    if summary.exists():
        data=read(summary)
        for key,control in data['controls'].items():
            if not control['pass_']:data['tiers'][key]={str(t):None for t in (100,90,80,70,60,50)}
        data['native_plan_sha256']=sha(path);data['method']='四进程轮转/反序；六角色每线程/接口预热1+5完整百图，process允许集0x55，OMP_PROC_BIND=false，未逐OMP线程绑定或锁频；全组排他窗口。';save(summary,data)
    save(output/'driver.json',dict(purpose=__doc__,plan_sha256=sha(path),script_sha256=sha(__file__),benchmark_module_sha256=sha(module),copied_worker_source_sha256=sha(ROOT/'scripts/bench_le16_block1024.py'),affinity_start=START_AFFINITY,scope='六角色、24情形、四worker，共480主要/96预热/80AA=656 native端点。0x55实际允许集，不逐OMP线程绑定或锁频，不拼旧unbound绝对时间或恢复旧3B。'))
