"""同场区分Cinema窄域和一般随机四级模型的RGB24冻结句柄容量/速度/RSS。"""
import argparse
import ctypes as ct
import hashlib
from pathlib import Path
import statistics
import subprocess
import sys
import time
import numpy as np
from study_memory_rom import ROOT,sha,read,save,env
from bench_memory_rom import memory
sys.path.insert(0,str(ROOT/'experiments/channel-runtime'))
from channel_native import Library

def setup(a,case,label,count=1):
    path={'compact':a.build/'jshc_compact_sparse.dll','specialized':a.build/'jshc_channel_specialized.dll','ref78':a.ref78,'ref80':a.ref80}[label];d=Library(path,sha(path))
    if case=='cinema':
        p=read(ROOT/'experiments/skylake-andn-split-v1.json');models=[a.data_root/p['fixed_inputs']['base']['path'],*[a.data_root/x['path'] for x in p['suffix_models']]];sides=[a.data_root/p['fixed_inputs']['sidecar']['path'],None,None,None]
    else:models=[a.fixtures/f'model-{i}.slut' for i in range(4)];sides=[a.fixtures/'frac-0.bin',None,None,None]
    chains=[d.chain(models,sides) for i in range(count)];metrics=None
    if label=='compact':
        fn=d.dll.jshc_cc_frozen_metrics;fn.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint64),ct.c_size_t];info=(ct.c_uint64*4)()
        if fn(chains[0].handle,info,4):raise AssertionError('容量诊断失败')
        metrics=dict(zip(('resident','freeze_peak_known','loader_peak_known','serialized_inputs'),list(info)))
    direct=None
    if label in ('ref78','ref80'):
        class Direct(ct.Structure):_fields_=[('version',ct.c_uint32),('enabled',ct.c_uint32),('format',ct.c_uint32),('reserved',ct.c_uint32),('entries',ct.c_uint64),('capacity',ct.c_uint64),('dg',ct.c_int32),('db',ct.c_int32)]
        info=Direct();fn=d.dll.jshc_cc_get_direct_info;fn.argtypes=[ct.c_void_p,ct.POINTER(Direct),ct.c_size_t]
        if fn(chains[0].handle,ct.byref(info),ct.sizeof(info)):raise AssertionError('原库诊断失败')
        direct=dict(enabled=info.enabled,capacity=info.capacity)
        if case=='general' and info.enabled:raise AssertionError('一般案例意外启用窄域直表')
    return d,chains,dict(capacity=chains[0].model_bytes,metrics=metrics,direct=direct,library=str(path),library_sha256=sha(path),models={str(x):sha(x) for x in models},sides={str(x):sha(x) for x in sides if x})

def worker(a):
    a.output.mkdir(parents=True,exist_ok=False)
    if a.rss:
        case,label=a.rss.split(':');before=memory();d,chains,info=setup(a,case,label,a.count);after=memory()
        save(a.output/'rss.json',dict(case=case,label=label,count=a.count,before=before,prepared=after,info=info,scope='独立新进程，分配图片前准备指定数量句柄；工作集/峰值包含Python、NumPy、库及分配器。'))
        return
    photo=a.data_root/'artifacts/skylake-server-matrix-v1/server-inputs/photos.rgb'
    if sha(photo)!='e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd':raise ValueError('百图身份变化')
    src=np.memmap(photo,dtype=np.uint8,mode='r').reshape(-1,3);work=np.empty_like(src);rows=[];controls=[];identities={}
    order=['ref78','compact','ref80','specialized'];shift=a.worker%4;order=order[shift:]+order[:shift]
    if a.worker%2:order=order[::-1]
    threads=[1,4] if a.worker%2==0 else [4,1]
    for case in ('cinema','general'):
        objects={label:setup(a,case,label) for label in order};identities[case]={label:x[2] for label,x in objects.items()}
        np.copyto(work,src);objects['ref78'][1][0].apply(work,kernel='avx2',threads=1);expected=hashlib.sha256(work).hexdigest()
        for t in threads:
            for label in order:
                chain=objects[label][1][0];times=[]
                for r in range(6):
                    np.copyto(work,src);start=time.perf_counter();chain.apply(work,kernel='avx2',threads=t);elapsed=time.perf_counter()-start
                    if r:times.append(elapsed)
                    if r in (0,5) and hashlib.sha256(work).hexdigest()!=expected:raise AssertionError('百图原生输出不同')
                rows.append(dict(case=case,label=label,threads=t,seconds=times,median_seconds=statistics.median(times),output_sha256=expected))
                save(a.output/'partial.json',dict(rows=rows))
            times=[];chain=objects['ref80'][1][0]
            for r in range(5):
                np.copyto(work,src);start=time.perf_counter();chain.apply(work,kernel='avx2',threads=t);times.append(time.perf_counter()-start)
            primary=next(x['median_seconds'] for x in rows if x['case']==case and x['label']=='ref80' and x['threads']==t)
            controls.append(dict(case=case,threads=t,seconds=times,ratio=statistics.median(times)/primary))
        for d,chains,info in objects.values():
            for chain in chains:chain.close()
    save(a.output/'results.json',dict(environment=env(),script_sha256=sha(__file__),worker=a.worker,order=order,threads=threads,rows=rows,controls=controls,identities=identities,source_sha256=sha(photo)))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('build','data-root','fixtures','ref78','ref80','output'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--worker',type=int);p.add_argument('--rss');p.add_argument('--count',type=int,default=1);a=p.parse_args()
    plan=ROOT/'experiments/rgb24-sparse-v1.json'
    if any(sha(ROOT/n)!=v for n,v in read(plan)['source_sha256'].items()):raise ValueError('冻结源码变化')
    if a.worker is not None or a.rss:return worker(a)
    a.output.mkdir(parents=True,exist_ok=False);commands=[];common=[sys.executable,'-X','utf8',__file__]
    for key in ('build','data-root','fixtures','ref78','ref80'):common+=['--'+key,str(getattr(a,key.replace('-','_')))]
    jobs=[['--worker',str(i),'--output',str(a.output/f'worker-{i}')] for i in range(4)]
    for case in ('cinema','general'):
        for label in ('compact','specialized','ref78','ref80'):
            for count in ([1,32] if label in ('compact','specialized') else [1]):jobs.append(['--rss',case+':'+label,'--count',str(count),'--output',str(a.output/f'rss-{case}-{label}-{count}')])
    for job in jobs:
        r=subprocess.run(common+job,capture_output=True,text=True,encoding='utf-8');commands.append(dict(command=r.args,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));save(a.output/'execution.json',commands)
        if r.returncode:raise RuntimeError(r.stderr)
    workers=[read(a.output/f'worker-{i}/results.json') for i in range(4)];results=[]
    for case in ('cinema','general'):
        for t in (1,4):
            lookups=[{r['label']:r['median_seconds'] for r in w['rows'] if r['case']==case and r['threads']==t} for w in workers]
            retain=[min(v['ref78'],v['ref80'],v['specialized'])/v['compact'] for v in lookups];same=[v['specialized']/v['compact'] for v in lookups];aa=[next(c['ratio'] for c in w['controls'] if c['case']==case and c['threads']==t) for w in workers];control=all(.8<=x<=1.25 for x in aa) and 1/1.1<=statistics.median(aa)<=1.1
            results.append(dict(case=case,threads=t,retention=retain,median_retention=statistics.median(retain),worst_retention=min(retain),specialized_retention=same,control_ratios=aa,control_pass=control,tiers={str(x):bool(control and min(retain)>=x/100) for x in (100,90,80,70,60,50)},identities=workers[0]['identities'][case]))
    save(a.output/'summary.json',dict(purpose=__doc__,plan_sha256=sha(plan),results=results,scope='同场1/4线程原地RGB8；Cinema必须与最快窄域表比，一般模型必须证明78/80未启用直表。A/A失败不升级资格，不跨场拼接。',rss={p.name:read(p/'rss.json') for p in a.output.glob('rss-*')}))
    print(a.output/'summary.json')
if __name__=='__main__':main()
