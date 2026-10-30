"""RO/COW八角色一次同场：848调用、四最劣worker及八RSS，原件失败保留。"""
import ctypes as ct
import hashlib
import os
from pathlib import Path
import statistics
import sys
import time
import bench_memory_rom as bench
from bench_le16_block1024 import affinity,control_affinity,ALLOWED,K32
from study_memory_rom import ROOT,U8,read,save,sha,env,loadrom,Model
from win_readonly_rom import FileView,library,query

PERF_PLAN=ROOT/'experiments/memory-rom-readonly-performance-v1.json'
LABELS=['ref78','ref80','original_avx','original_c99','cow_avx','cow_c99','readonly_avx','readonly_c99']
original_setup=bench.setup
FINALIZERS=[]
VIEWS={}
def actual(d,path):
    get=ct.windll.kernel32.GetModuleFileNameW;get.argtypes=[ct.c_void_p,ct.c_wchar_p,ct.c_uint32];buffer=ct.create_unicode_buffer(32768)
    if not get(d._handle,buffer,len(buffer)) or Path(buffer.value).resolve()!=path.resolve():raise AssertionError('实际模块路径不同')
def setup(a,label):
    plan=read(PERF_PLAN)
    if label in ('ref78','ref80'):
        result=original_setup(a,label);actual(result[1][0],Path(result[3]));d,h=result[1];FINALIZERS.append(lambda:d.jshc_cc_destroy(h));return result
    path=Path(plan['library']);rom=Path(plan['rom']);d=library(path);actual(d,path);mode,kernel=label.rsplit('_',1)
    if mode=='original':
        m,keep=loadrom(d,rom);state=[keep]
        def close():
            ct.memset(ct.byref(m),0,ct.sizeof(m));stream,mapping,view=state.pop();del view;mapping.close();stream.close()
        FINALIZERS.append(close);owner=state;address=ct.cast(m.blob,ct.c_void_p).value
    else:
        owner=FileView(rom,mode);m=owner.prepare(d);FINALIZERS.append(owner.close);address=owner.address
    protected=query(address)
    if protected['Protect']!=(2 if mode=='readonly' else 8) or protected['Type']!=0x40000:raise AssertionError('实际loader保护不同')
    VIEWS[label]=dict(mode=mode,address=hex(address),bytes=rom.stat().st_size,first=protected,last=query(address+rom.stat().st_size-1))
    def apply(source,target,n,threads,io_mode):return d.jshc_mem_apply_parallel(ct.byref(m),target if io_mode=='inplace' else source,target,n,1 if kernel=='avx' else 0,threads)
    return apply,(d,m,owner),rom.stat().st_size+ct.sizeof(Model),str(path),sha(path)

def worker(a):
    out=a.output;out.mkdir(parents=True,exist_ok=False)
    if a.rss:
        before=bench.memory();fn,keep,capacity,path,libsha=setup(a,a.rss);after=bench.memory()
        save(out/'rss.json',dict(label=a.rss,before=before,prepared=after,model_capacity=capacity,library=path,library_sha256=libsha,view=VIEWS.get(a.rss),environment=env(),affinity_start=START_AFFINITY,affinity_end=affinity(),scope='独立新进程，同import群及0x55；含Python/库/流式预检，无照片；commit/WS/capacity分别列。'));return
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
    save(out/'results.json',dict(environment=env(),worker_index=a.worker_index,script_sha256=sha(__file__),order=order,thread_order=threads,roles=identities,views=VIEWS,rows=rows,controls=controls,memory=bench.memory(),photos=dict(path=str(photo),sha256=sha(photo),bytes=len(src)),affinity_start=START_AFFINITY,affinity_end=final,source_address=hex(ct.cast(source,ct.c_void_p).value),target_address=hex(ct.cast(target,ct.c_void_p).value),purpose=__doc__,scope='同进程全部角色驻留、同source/target；caller端点在wall外，固定允许集不是逐OMP绑定或锁频。不拿COW作主分母。'))
if __name__=='__main__':
    plan=read(PERF_PLAN)
    if any(sha(ROOT/n)!=v for n,v in plan['source_sha256'].items()) or any(sha(n)!=v for n,v in plan['input_sha256'].items()):raise AssertionError('冻结源/输入不同')
    if '--repeats' in sys.argv and int(sys.argv[sys.argv.index('--repeats')+1])!=5:raise ValueError('只允许完整五轮')
    for flag,expected in (('--build',plan['build']),('--roms',str(Path(plan['rom']).parent)),('--ref80',plan['reference80']),('--data-root',plan['data_root'])):
        if flag not in sys.argv or Path(sys.argv[sys.argv.index(flag)+1]).resolve()!=Path(expected).resolve():raise AssertionError('实际CLI输入路径不同：'+flag)
    os.environ['OMP_PROC_BIND']='false';os.environ.pop('OMP_PLACES',None);START_AFFINITY=control_affinity();module=Path(bench.__file__);bench.labels=lambda:list(LABELS);bench.setup=setup;bench.worker=worker;bench.__file__=__file__
    try:bench.main()
    finally:
        for close in reversed(FINALIZERS):close()
    output=Path(sys.argv[sys.argv.index('--output')+1]);summary=output/'summary.json'
    if summary.exists():
        data=read(summary)
        for key,control in data['controls'].items():
            if not control['pass_']:data['tiers'][key]={str(t):None for t in (100,90,80,70,60,50)}
        data['native_plan_sha256']=sha(PERF_PLAN);data['method']='四worker八角色1+5完整百图，0x55且无逐OMP绑定/锁频；848调用+8RSS，不重跑。';save(summary,data)
    save(output/'driver.json',dict(purpose=__doc__,plan_sha256=sha(PERF_PLAN),script_sha256=sha(__file__),benchmark_module_sha256=sha(module),affinity_start=START_AFFINITY,scope='输出精确但速度独立分档；AA失效清空，不以原/新COW慢分母授档。所有owner在测量原件落盘后关闭。'))
