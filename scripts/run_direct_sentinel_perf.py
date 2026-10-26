"""291九角色、成对ABBA/BAAB的固定百图性能；质量门后一次执行，保留所有原始轮。"""
from __future__ import annotations
import argparse
from contextlib import ExitStack
import gc
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts')]
from check_direct_sentinel_native_v2 import Library,Info,info,direct_info,cache_info,palette_info,domain_info,sha,save,BUILD,FROZEN as QUALITY_FROZEN,OUT as QUALITY_OUT
from run_velvia_bubble_perf import bench,array_sha
from lutlab import study_provenance
import numpy as np
import psutil

PLAN=ROOT/'artifacts/p16-direct-sentinel-perf-frozen-v1/plan.json'
OUT=ROOT/'artifacts/p16-direct-sentinel-perf-v1'
ORIGINAL=Path('F:/Hackathon/projects/16-lut-color')
RAW=ORIGINAL/'artifacts/skylake-server-matrix-v1/server-inputs/photos.rgb'
RAW_SHA='e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd'
ENV={'OMP_NUM_THREADS':'4','OMP_DYNAMIC':'FALSE','OMP_THREAD_LIMIT':'4','OMP_WAIT_POLICY':'PASSIVE','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONIOENCODING':'utf-8'}

def definitions(quality):
    previous=json.loads((ROOT/'artifacts/cinema-max48-pareto-quality-v1/identity.json').read_text(encoding='utf-8'))
    specs=dict(quality['roles']);specs['a399']=previous['roles']['a399']
    roles={'87a399':{'library':'old87','model':'a399'},'87old':{'library':'old87','model':'old_best'},'291old':{'library':'new','model':'old_best'}}
    for name,model in [('max','max_first'),('p99','p99_first'),('max48','max48')]:
        roles['291'+name]={'library':'new','model':model};roles['288'+name]={'library':'old288','model':model}
    pairs=[(base,'291'+name) for name in ('max','p99','max48') for base in ('87a399','87old','291old','288'+name)]+[('87old','291old')]
    return specs,roles,pairs

def freeze():
    if PLAN.parent.exists():raise FileExistsError('不覆盖291正式协议')
    quality_path=QUALITY_FROZEN/'frozen.json';quality=json.loads(quality_path.read_text(encoding='utf-8'))
    result_path=QUALITY_OUT/'results.json';result=json.loads(result_path.read_text(encoding='utf-8'))
    mt_path=ROOT/'artifacts/p16-direct-sentinel-v2-full-mt-v2/results.json';mt=json.loads(mt_path.read_text(encoding='utf-8'))
    if not result['passed'] or result['frozen_sha256']!=sha(quality_path) or not mt['passed'] or len(mt['outputs'])!=10:raise ValueError('完整质量尚未通过')
    if sha(RAW)!=RAW_SHA or RAW.stat().st_size!=78643200*3:raise ValueError('固定原100图RGB流不同')
    specs,roles,pairs=definitions(quality)
    source=np.memmap(RAW,np.uint8,'r',shape=(78643200,3));expected={}
    for name,spec in specs.items():
        for path,wanted in spec['input_sha256'].items():
            if sha(path)!=wanted:raise ValueError('模型变化')
        if sha(spec['oracle'])!=spec['oracle_sha256']:raise ValueError('oracle变化')
        reference=np.memmap(spec['oracle'],np.uint8,'r',shape=(2**24,3));digest=hashlib.sha256()
        for begin in range(0,len(source),262144):
            part=source[begin:begin+262144];keys=part.astype(np.uint32)@np.array([65536,256,1],np.uint32);digest.update(reference[keys])
        expected[name]=digest.hexdigest();del reference
    assert expected['a399']=='f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528'
    assert expected['max48']=='b61b35171a12b9e4cabf45f4f27c04e94489859161488b8543360c527d11bef8'
    mt_frozen=json.loads((ROOT/'artifacts/p16-direct-sentinel-v2-full-mt-frozen-v2/frozen.json').read_text(encoding='utf-8'))
    sources=dict(mt_frozen['sources_sha256'])
    for path in (Path(__file__),ROOT/'scripts/audit_direct_sentinel_perf.py',ROOT/'scripts/run_velvia_bubble_perf.py'):
        sources[path.relative_to(ROOT).as_posix()]=sha(path)
    for name,wanted in sources.items():
        if sha(ROOT/name)!=wanted:raise ValueError('源变化：'+name)
    PLAN.parent.mkdir(parents=True)
    for name in sources:
        target=PLAN.parent/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
    plan={'schema':'p16_direct_sentinel_pairwise_perf_v1','purpose':'固定100图AVX2稳态四模式、九角色同场；冷创建/首Out4及fresh RSS单列，不给冷首AA或跨环境资格','quality_frozen_sha256':sha(quality_path),'quality_results_sha256':sha(result_path),'full_mt_results_sha256':sha(mt_path),'sources_sha256':sources,'libraries':quality['libraries'],'models':specs,'roles':roles,'comparisons':pairs,'expected_output_sha256':expected,'source':str(RAW),'source_sha256':RAW_SHA,'pixels':78643200,'workers':4,'scenes':[{'path':path,'threads':threads} for path in ('inplace','to') for threads in (1,4)],'warmup_per_role_per_pair':2,'repeats_per_timed_group':3,'pair_palindromes':[['L1','R1','R2','L2'],['R1','L1','L2','R2'],['R1','L1','L2','R2'],['L1','R1','R2','L2']],'AA_time_ratio_bounds':[0.85,1.15],'no_obvious_time_ratio_cap':1.10,'tiers':[100,90,80,70,60,50],'required_denominators':['87a399','87old','291old'],'input_sha_scope':'每worker起点、每冷首及每pair末；每warmup/计时组末都核实际输出SHA','expected_native_output_sha_checks':1284,'expected_native_apply_calls':3364,'fresh_rss_roles':9,'environment':study_provenance.environment_fingerprint(),'required_environment':ENV,'allowed_cpus':[0,2,4,6],'per_tid_pin':False,'single_execution':True,'allocation_failure_injection':False,'limitations':'100图已见；未知官方Threshold、派生表许可及指定Intel性能。AA失效不授档，任一有效必需模式<50拒绝。未测所有可能合成输入的最差速度。'}
    save(PLAN,plan);print(json.dumps({'plan_sha256':sha(PLAN),'roles':len(roles),'pairs':len(pairs),'sources':len(sources),'expected_sha_checks':1284,'performance_started':False}))

def verify(plan):
    for name,wanted in plan['required_environment'].items():
        if os.environ.get(name,'').upper()!=wanted.upper():raise ValueError('导入前环境不符：'+name)
    for name,wanted in plan['sources_sha256'].items():
        if sha(ROOT/name)!=wanted:raise ValueError('冻结源变化：'+name)
    for library in plan['libraries'].values():
        if sha(library['path'])!=library['sha256']:raise ValueError('库变化')

def load_libraries(plan):
    directories=[os.add_dll_directory('E:/mingw64/bin'),os.add_dll_directory(str(BUILD))]
    libraries={name:Library(spec['path'],spec['sha256']) for name,spec in plan['libraries'].items()}
    return libraries,directories

def role_state(chain,kind):
    return {'model_bytes':chain.model_bytes,'direct':direct_info(chain),'cache':cache_info(chain),'palette':palette_info(chain),'domain':domain_info(chain),'sentinel':info(chain) if kind=='new' else None}

def worker(number,plan):
    psutil.Process().cpu_affinity(plan['allowed_cpus']);folder=OUT/f'worker{number}';folder.mkdir()
    libraries,dirs=load_libraries(plan)
    if sha(plan['source'])!=plan['source_sha256']:raise ValueError('输入变化')
    source=np.memmap(plan['source'],np.uint8,'r',shape=(plan['pixels'],3));work=np.empty_like(source)
    record={'worker':number,'plan_sha256':sha(PLAN),'environment':study_provenance.environment_fingerprint(),'allowed_cpus':psutil.Process().cpu_affinity(),'cold':[],'groups':[],'warmup':[],'pair_source_checks':[],'source_sha256':array_sha(source)}
    save(folder/'start.json',record)
    with ExitStack() as stack:
        chains={};order=list(plan['roles']);order=order[number:]+order[:number]
        if number%2:order.reverse()
        for role in order:
            definition=plan['roles'][role];spec=plan['models'][definition['model']]
            for path,wanted in spec['input_sha256'].items():
                if sha(path)!=wanted:raise ValueError('输入模型变化')
            started=time.perf_counter();chain=stack.enter_context(libraries[definition['library']].chain(spec['models'],spec['sidecars']));created=time.perf_counter()-started;chains[role]=chain
            values=bench(chain,source,work,'to',4,1);actual=array_sha(work)
            if actual!=plan['expected_output_sha256'][definition['model']] or array_sha(source)!=plan['source_sha256']:raise ValueError('冷首输出/源不同')
            record['cold'].append({'role':role,'python_chain_create_seconds':created,'first_out4_seconds':values,'create_plus_first_out4_seconds':created+values['api_total_seconds'][0],'output_sha256':actual,'state':role_state(chain,definition['library'])})
        pairs=list(plan['comparisons']);pairs=pairs[number:]+pairs[:number]
        if number%2:pairs.reverse()
        scenes=list(plan['scenes'])
        if number%2:scenes.reverse()
        for scene in scenes:
            path=scene['path'];threads=scene['threads']
            for pair_index,(left,right) in enumerate(pairs):
                mapping={'L':left,'R':right}
                for side in ('L','R'):
                    role=mapping[side];definition=plan['roles'][role];bench(chains[role],source,work,path,threads,plan['warmup_per_role_per_pair']);actual=array_sha(work)
                    if actual!=plan['expected_output_sha256'][definition['model']]:raise ValueError('预热实际输出不同')
                    record['warmup'].append({'left':left,'right':right,'path':path,'threads':threads,'role':role,'output_sha256':actual})
                for position,label in enumerate(plan['pair_palindromes'][number]):
                    role=mapping[label[0]];definition=plan['roles'][role];values=bench(chains[role],source,work,path,threads,plan['repeats_per_timed_group']);actual=array_sha(work)
                    if actual!=plan['expected_output_sha256'][definition['model']]:raise ValueError('计时实际输出不同')
                    record['groups'].append({'left':left,'right':right,'role':role,'phase':int(label[1]),'position':position,'path':path,'threads':threads,'seconds':values,'output_sha256':actual})
                current=array_sha(source)
                if current!=plan['source_sha256']:raise ValueError('pair改变源')
                record['pair_source_checks'].append({'left':left,'right':right,'path':path,'threads':threads,'source_sha256':current})
                save(folder/f'pair-{len(record["pair_source_checks"]):03d}.json',{'groups':record['groups'][-4:],'warmup':record['warmup'][-2:],'source':record['pair_source_checks'][-1]})
        assert len(record['groups'])==208 and len(record['warmup'])==104 and len(record['cold'])==9
    save(folder/'results.json',record);print(json.dumps({'worker':number,'groups':208,'actual_output_sha_checks':321,'passed':True}),flush=True)

def rss(role,plan):
    psutil.Process().cpu_affinity(plan['allowed_cpus']);libraries,dirs=load_libraries(plan);process=psutil.Process()
    gc.collect();before=process.memory_info()._asdict();definition=plan['roles'][role];spec=plan['models'][definition['model']]
    with libraries[definition['library']].chain(spec['models'],spec['sidecars']) as chain:
        gc.collect();after=process.memory_info()._asdict();state=role_state(chain,definition['library'])
    gc.collect();closed=process.memory_info()._asdict()
    save(OUT/'rss'/f'{role}.json',{'role':role,'before':before,'after_prepare':after,'after_close':closed,'state':state,'plan_sha256':sha(PLAN),'pixels_allocated':0,'includes_python_and_all_three_dll_imports':True})

def run():
    if OUT.exists():raise FileExistsError('不覆盖正式性能')
    plan=json.loads(PLAN.read_text(encoding='utf-8'));verify(plan)
    if sha(QUALITY_OUT/'results.json')!=plan['quality_results_sha256']:raise ValueError('质量证据变更')
    process=psutil.Process();process.cpu_affinity(plan['allowed_cpus']);before={}
    for item in psutil.process_iter(['pid','name','cpu_times']):
        try:
            if any(word in (item.info['name'] or '').lower() for word in ('python','cc1','g++','gcc','7z','git')):before[item.pid]={'name':item.info['name'],'cpu':sum(item.info['cpu_times'][:2])}
        except (psutil.NoSuchProcess,psutil.AccessDenied):pass
    time.sleep(.25);observed=[]
    for pid,row in before.items():
        try:observed.append({'pid':pid,'name':row['name'],'cpu_delta':sum(psutil.Process(pid).cpu_times()[:2])-row['cpu']})
        except (psutil.NoSuchProcess,psutil.AccessDenied):observed.append({'pid':pid,'name':row['name'],'ended_or_unavailable':True})
    competitors=[row for row in observed if row['pid']!=os.getpid() and row.get('cpu_delta',0)>.10]
    if competitors:
        target=PLAN.parent/'preflight-stop.json';save(target,{'observed':observed,'competitors':competitors,'performance_started':False});raise ValueError('发现竞争CPU，未开始正式')
    OUT.mkdir(parents=True);(OUT/'rss').mkdir();save(OUT/'identity.json',{'plan_sha256':sha(PLAN),'driver_sha256':sha(__file__),'preflight_processes':observed,'environment':study_provenance.environment_fingerprint(),'scope':'团队协调独占窗，未声称主机绝对独占或锁频；不杀未知进程'})
    for number in range(plan['workers']):subprocess.run([sys.executable,str(Path(__file__)),'--worker',str(number)],cwd=ROOT,check=True)
    for role in plan['roles']:subprocess.run([sys.executable,str(Path(__file__)),'--rss',role],cwd=ROOT,check=True)
    print(json.dumps({'formal_execution_completed':True,'workers':4,'output_sha_checks':1284,'rss_roles':9,'audit_pending':True}),flush=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--freeze',action='store_true');parser.add_argument('--worker',type=int);parser.add_argument('--rss');args=parser.parse_args()
    if args.freeze:return freeze()
    if args.worker is not None or args.rss:
        plan=json.loads(PLAN.read_text(encoding='utf-8'));verify(plan)
        return worker(args.worker,plan) if args.worker is not None else rss(args.rss,plan)
    run()

if __name__=='__main__':main()
