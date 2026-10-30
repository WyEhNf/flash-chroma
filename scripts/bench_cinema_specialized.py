"""同一a399实际四级模型，两独立库一次平衡比较编译期专门化。"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'experiments/channel-runtime'))
import numpy as np
from PIL import Image
from channel_native import Library,digest
from native_provenance import verify_dependencies


def checked(spec):
    p=ROOT/spec['path']
    if digest(p)!=spec['sha256']:raise ValueError(f'冻结SHA不同：{p}')
    return p


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def worker(args,plan):
    manifest=read(checked(plan['inputs']['manifest']))['images']
    if len(manifest)!=100:raise ValueError('需要冻结100图')
    images=[]
    for row in manifest:
        p=checked(row['evaluation'])
        with Image.open(p) as image:
            if image.mode!='RGB' or image.size!=(1024,768):raise ValueError('不是比赛RGB8图片')
            images.append(np.asarray(image).reshape(-1,3).copy())
    source=np.concatenate(images);del images
    if source.nbytes!=235929600:raise ValueError('预加载100图字节数不同')
    source_sha=hashlib.sha256(source.tobytes()).hexdigest()
    variants=plan.get('variants',['baseline','candidate'])
    cube={name:np.memmap(checked(plan['inputs'][name+'_cube']),np.uint8,'r',shape=(256**3,3)) for name in variants}
    expected={name:hashlib.sha256() for name in cube}
    for start in range(0,len(source),1024*768):
        chunk=source[start:start+1024*768];keys=chunk.astype(np.int64)@np.array([65536,256,1],np.int64)
        for name,c in cube.items():expected[name].update(c[keys].tobytes())
    expected={name:h.hexdigest() for name,h in expected.items()}
    native=read(checked(plan['inputs']['native_acceptance']))
    if (not native['acceptance']['accepted'] or native['acceptance']['failed'] or not native['native']['pass']
            or native['native']['byte_mismatches'] or expected['candidate']!=native['photos']['output_sha256']):
        raise ValueError('完整候选实际四级原生验收/100图身份不同')
    audit=read(checked(plan['inputs']['evidence_audit']))
    if not audit['pass'] or audit['acceptance_results_sha256']!=plan['inputs']['native_acceptance']['sha256']:
        raise ValueError('依赖与旧逐图来源补核未通过或绑定不同')
    lib=Library(checked(plan['inputs']['library']),plan['inputs']['library']['sha256'])
    if lib.capabilities!=7:raise ValueError('本次AVX2/OpenMP能力不同')
    specialized=read(checked(plan['inputs']['specialized_native']))
    if (not specialized['pass'] or specialized['library_sha256']!=lib.sha256
            or specialized['photos']['output_sha256']!=expected['candidate']
            or specialized['prior_full_results_sha256']!=plan['inputs']['native_acceptance']['sha256']):
        raise ValueError('新专门化库尚未完成同模型完整等价或身份不同')
    dependency_sources=verify_dependencies(checked(plan['inputs']['library']),read(checked(plan['inputs']['build'])),loaded=True)
    libraries={'candidate':lib,'baseline':lib}
    if 'baseline_library' in plan['inputs']:
        spec=plan['inputs']['baseline_library'];libraries['baseline']=Library(checked(spec),spec['sha256'])
    if any(v.capabilities!=7 for v in libraries.values()):raise ValueError('对照库能力不同')
    if 'required_revisions' in plan and any(libraries[k].revision!=v for k,v in plan['required_revisions'].items()):
        raise ValueError('实际载入的运行时修订不符')
    controls=[checked(p) for p in plan['controls']]
    models={'baseline':[checked(plan['inputs']['baseline_model']),*controls],
            'candidate':[checked(plan['inputs']['candidate_base']),*controls]}
    sidecars={'baseline':[None]*4,'candidate':[checked(plan['inputs']['candidate_sidecar']),None,None,None]}
    if 'baseline_sidecar' in plan['inputs']:sidecars['baseline']=[checked(plan['inputs']['baseline_sidecar']),None,None,None]
    if 'original' in variants:
        models['original']=[checked(plan['inputs']['original_model']),*controls];sidecars['original']=[None]*4
        libraries['original']=libraries['baseline']
    order=plan['orders'][args.worker_index];thread_order=plan['thread_orders'][args.worker_index]
    results=[]
    for threads in thread_order:
        for name in order:
            active_library=libraries[name]
            with active_library.chain(models[name],sidecars[name]) as chain:
                warm=chain.apply(source.copy(),kernel='avx2',threads=threads)
                actual=hashlib.sha256(warm.tobytes()).hexdigest();del warm
                if actual!=expected[name]:raise AssertionError('计时前完整100图输出不符合冻结完整流')
                measured=chain.bench(source,kernel='avx2',threads=threads,repeats=plan['repeats'])
                if any(b<a or a<=0 for a,b in zip(measured['apply_seconds'],measured['copy_apply_seconds'])):raise AssertionError('原生计时回执非法')
                results.append({'variant':name,'requested_threads':threads,'images':100,'stages':4,'kernel':'avx2',
                    'library_sha256':active_library.sha256,'library_revision':active_library.revision,
                    'native_preflight_sha256':actual,'model_accounting_bytes':chain.model_bytes,
                    'serialized_input_bytes':sum(p.stat().st_size for p in models[name])+sum(p.stat().st_size for p in sidecars[name] if p is not None),
                    **measured})
    if hashlib.sha256(source.tobytes()).hexdigest()!=source_sha:raise AssertionError('只读源图组被基准修改')
    return {'worker_index':args.worker_index,'pid':os.getpid(),'python':sys.version,'order':order,'thread_order':thread_order,
        'source_sha256':source_sha,'source_bytes':source.nbytes,'library_sha256':lib.sha256,'capabilities':lib.capabilities,
        'libraries':{k:{'sha256':v.sha256,'revision':v.revision} for k,v in libraries.items()},'loaded_dependency_sources':dependency_sources,
        'thread_environment':{n:os.environ.get(n) for n in ['OMP_NUM_THREADS','OMP_DYNAMIC','OMP_PROC_BIND','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']},'records':results}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--worker-index',type=int)
    args=parser.parse_args();args.plan=args.plan.resolve();args.output=args.output.resolve();plan=read(args.plan)
    if args.worker_index is not None:
        record=worker(args,plan);args.output.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'worker':args.worker_index,'records':len(record['records'])},ensure_ascii=False),flush=True);return
    if args.output.exists():raise ValueError('不覆盖已有性能研究')
    workers_count=len(plan['orders']);variants=plan.get('variants',['baseline','candidate'])
    policy=read(checked(plan['inputs']['policy']))['future_performance_gates']
    if (plan['repeats']!=5 or workers_count!=4 or len(plan['thread_orders'])!=workers_count
            or variants!=['baseline','candidate'] or plan['orders']!=policy['balanced_orders'] or plan['thread_orders']!=policy['thread_orders']):
        raise ValueError('必须固定四进程、两配置、每组五轮及冻结平衡顺序')
    if any(sorted(v)!=sorted(variants) for v in plan['orders']):raise ValueError('各进程配置顺序不完整')
    for spec in plan['inputs'].values():checked(spec)
    names=['scripts/bench_cinema_specialized.py','experiments/channel-runtime/channel_native.py',
        'experiments/channel-runtime/native_provenance.py',args.plan.relative_to(ROOT).as_posix()]
    sources={n:digest(ROOT/n) for n in names};args.output.mkdir(parents=True)
    (args.output/'run.json').write_text(json.dumps({'plan':plan,'source_sha256':sources,'purpose':'同机串行固定多进程、100图四级受控性能；不新增拟合或精度选型'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with zipfile.ZipFile(args.output/'measured-source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for n in sources:z.write(ROOT/n,n)
    workers=[]
    for index in range(workers_count):
        destination=args.output/f'worker{index}.json'
        result=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--plan',str(args.plan),'--output',str(destination),'--worker-index',str(index)],capture_output=True,text=True,encoding='utf-8')
        (args.output/f'worker{index}.stdout.log').write_text(result.stdout,encoding='utf-8')
        (args.output/f'worker{index}.stderr.log').write_text(result.stderr,encoding='utf-8')
        if result.returncode:raise RuntimeError(f'进程{index}失败：'+result.stderr)
        workers.append(read(destination));print('完成串行进程',index,flush=True)
    if len({w['source_sha256'] for w in workers})!=1:raise ValueError('各进程输入图组不同')
    summaries=[]
    for threads in [1,4]:
        for variant in variants:
            records=[next(r for r in w['records'] if r['variant']==variant and r['requested_threads']==threads) for w in workers]
            medians=[statistics.median(r['apply_seconds'])*10 for r in records]
            total=[statistics.median(r['copy_apply_seconds'])*10 for r in records]
            summaries.append({'variant':variant,'requested_threads':threads,'images':100,'stages':4,
                'median_apply_ms_per_image':statistics.median(medians),'process_medians_apply_ms_per_image':medians,
                'process_median_range_ms_per_image':[min(medians),max(medians)],
                'median_copy_apply_ms_per_image':statistics.median(total),'model_accounting_bytes':records[0]['model_accounting_bytes'],
                'serialized_input_bytes':records[0]['serialized_input_bytes']})
    paired=[]
    for threads in [1,4]:
        for denominator in ['baseline']+(['original'] if 'original' in variants else []):
            ratios=[]
            for w in workers:
                records={r['variant']:r for r in w['records'] if r['requested_threads']==threads}
                ratios.append(statistics.median(records['candidate']['apply_seconds'])/statistics.median(records[denominator]['apply_seconds']))
            paired.append({'requested_threads':threads,'numerator':'candidate','denominator':denominator,'process_ratios':ratios,'median_ratio':statistics.median(ratios)})
    if any(digest(ROOT/n)!=h for n,h in sources.items()):raise ValueError('性能期间源码变化')
    result={'pass':True,'summary':summaries,'paired':paired,'worker_sha256':[digest(args.output/f'worker{i}.json') for i in range(workers_count)],
        'scope':plan['limits'],'sample_unit':'一次100图完整组，ms/图为摊销值而非单图延迟','clock_temperature_affinity_controlled':False}
    (args.output/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False),flush=True)


if __name__=='__main__':main()
