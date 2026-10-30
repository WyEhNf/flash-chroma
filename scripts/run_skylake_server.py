"""Linux服务器统一入口：固定字节检查、独立构建、集中正确性，再显式执行唯一平衡性能比较。"""
from __future__ import annotations
import argparse
import ctypes as ct
from datetime import datetime, timezone
import hashlib
import math
import os
from pathlib import Path
import resource
import shutil
import statistics
import subprocess
import sys
import time
import traceback
from skylake_server_support import ROOT,read,save,digest,checked,topology,environment,loaded,bind,create,apply,layouts,driver_bind,team,measure

ORDERS=[['reference','candidate'],['candidate','reference'],['candidate','reference'],['reference','candidate']]
THREADS=[[1,4],[4,1],[1,4],[4,1]]
MODES=[[0,1],[1,0],[1,0],[0,1]]
GATES={'median_apply_ratio_max':.97,'any_process_apply_ratio_max':1.02,'median_copy_apply_ratio_max':1.0}

def frozen_sources(bundle):
    for name,sha in bundle['source_sha256'].items():
        if digest(ROOT/name)!=sha:raise ValueError('包源码改变：'+name)
def load_native(policy):
    selected=policy['selected_cpus'];os.sched_setaffinity(0,selected)
    build=read(checked(policy['build']));plan=read(checked(policy['plan']))
    if build['plan_sha256']!=policy['plan']['sha256'] or build['source_sha256']!=plan['source_sha256']:
        raise ValueError('构建与计划绑定不同')
    for name,sha in plan['source_sha256'].items():
        if digest(ROOT/name)!=sha:raise ValueError('冻结实现改变：'+name)
    libs={name:bind(checked(s)) for name,s in build['libraries'].items()}
    for name,d in libs.items():
        if d.jshc_cc_abi_version()!=1 or d.jshc_cc_revision()!=build['revisions'][name] or d.jshc_cc_capabilities()!=7:
            raise ValueError('实际ABI/后端能力/修订与构建不符')
    driver=driver_bind(checked(policy['driver']))
    teams={str(n):team(driver,n,selected) for n in (1,4)}
    maps=loaded([*build['libraries'].values(),policy['driver']])
    return plan,build,libs,driver,teams,maps
def actual_chain(plan,d):
    models=[checked(plan['fixed_inputs']['base']),*[checked(s) for s in plan['suffix_models']]]
    sides=[checked(plan['fixed_inputs']['sidecar']),None,None,None]
    return create(d,models,sides)
def photo_buffers(bundle):
    path=ROOT/bundle['photo_pixels'];size=100*1024*768*3
    if path.stat().st_size!=size:raise ValueError('100图字节数不符')
    source=(ct.c_uint8*size)();work=(ct.c_uint8*size)()
    with path.open('rb') as f:
        if f.readinto(source)!=size:raise ValueError('未完整读入固定照片像素')
    sha=hashlib.sha256(source).hexdigest()
    if sha!=bundle['files'][bundle['photo_pixels']]['sha256']:raise ValueError('实际预载源不同')
    return source,work,sha
def driver_negative_contract(driver,d,handle):
    u8=(ct.c_uint8*32);source=u8(*range(32));work=u8(*([167]*32));a=(ct.c_double*2)(-7,-7)
    c=(ct.c_double*2)(-8,-8);w=(ct.c_double*2)(-9,-9);error=ct.create_string_buffer(1024)
    common=[ct.cast(d.jshc_cc_apply,ct.c_void_p),handle,ct.addressof(source),ct.addressof(work),3,2,1,1,0,1,a,c,w,error,len(error)]
    rows=[];limit=ct.c_size_t(-1).value
    changes=[('空回调',0,None),('空模型',1,None),('空源',2,None),('空工作区',3,None),
        ('非RGB长度',4,1),('零图',5,0),('非法后端',6,2),('零线程',7,0),('非法模式',8,2),('零轮次',9,0),
        ('源工作区重叠',3,ct.addressof(source)),('图像总长度溢出',5,limit),
        ('计时长度溢出',9,limit),('计时数组重叠',11,a)]
    for label,index,value in changes:
        params=common.copy();params[index]=value
        before=[bytes(x) for x in (source,work,a,c,w)]
        rc=driver.jshc_sb_run(*params)
        if rc!=1 or before!=[bytes(x) for x in (source,work,a,c,w)]:raise AssertionError('计时器拒绝保护失败：'+label)
        rows.append({'case':label,'returncode':rc,'error':error.value.decode('utf-8')})
    callback=ct.CFUNCTYPE(ct.c_int,ct.c_void_p,ct.c_void_p,ct.c_size_t,ct.c_int,ct.c_int,ct.c_void_p,ct.c_size_t)(lambda *args:1)
    params=common.copy();params[0]=ct.cast(callback,ct.c_void_p)
    if driver.jshc_sb_run(*params)!=2:raise AssertionError('回调失败没有中止整组')
    return rows
def validate(policy,bundle):
    plan,build,libs,driver,teams,maps=load_native(policy)
    fixture=read(ROOT/bundle['fixture_manifest']);source=(ROOT/fixture['input']).read_bytes()
    comparisons=0;negative=0;mem=[]
    for case in fixture['cases']:
        truth=(ROOT/case['expected']).read_bytes();handles={}
        if len(source)!=4097*3 or len(truth)!=len(source):raise ValueError('有限预期长度不同')
        try:
            for name,d in libs.items():
                handles[name]=create(d,[ROOT/x for x in case['models']],[ROOT/x if x else None for x in case['sidecars']])
            got=layouts(libs['candidate'],handles['candidate'],len(case['models']))
            if got!=case['layouts']:raise AssertionError('实际边界布局不同：'+case['name'])
            r=libs['reference'].jshc_cc_model_bytes(handles['reference']);c=libs['candidate'].jshc_cc_model_bytes(handles['candidate'])
            if r-c!=3072*case['layouts'].count(2):raise AssertionError('压缩容量不符合实际布局')
            mem.append({'case':case['name'],'reference':r,'candidate':c,'layouts':got})
            f=libs['candidate'].jshc_cc_get_layouts;n=len(got);sentinel=(ct.c_uint32*(n+2))(*([0xa7a7a7a7]*(n+2)))
            for handle,count in ((handles['candidate'],n+1),(handles['candidate'],n-1),(None,n)):
                before=bytes(sentinel)
                if f(handle,sentinel,count)!=1 or bytes(sentinel)!=before:raise AssertionError('布局失败保护不同')
                negative+=1
            if f(handles['candidate'],None,n)!=1:raise AssertionError('空诊断指针未拒绝')
            negative+=1
            for n in fixture['lengths']:
                for name,d in libs.items():
                    for kernel,threads in fixture['backend_threads']:
                        for offset in fixture['offsets']:
                            if apply(d,handles[name],source[:n*3],kernel,threads,offset)!=truth[:n*3]:
                                raise AssertionError('冻结独立整数预期不符：'+case['name'])
                            comparisons+=1
        finally:
            for name,h in handles.items():libs[name].jshc_cc_destroy(h)
    source,work,source_sha=photo_buffers(bundle);photos=[];driver_contract=[]
    for name,d in libs.items():
        h=actual_chain(plan,d)
        try:
            flags=layouts(d,h,4)
            if name=='candidate' and flags!=plan['delta16_policy']['actual_chain_layouts']:raise AssertionError('实际照片未启用差值布局')
            if not driver_contract:driver_contract=driver_negative_contract(driver,d,h)
            for threads in (1,4):
                for mode in (0,1):
                    # 本次只验证计时器两种调度的输出；返回的时长不作性能比较或选型。
                    measure(driver,d,h,source,work,1024*768*3,100,threads,mode,1)
                    sha=hashlib.sha256(work).hexdigest()
                    if sha!=bundle['photo_output_sha256']:raise AssertionError('100图或原生计时器调度输出不同')
                    photos.append({'variant':name,'threads':threads,'mode':mode,'output_sha256':sha,'layouts':flags})
        finally:d.jshc_cc_destroy(h)
    if hashlib.sha256(source).hexdigest()!=source_sha:raise AssertionError('计时器修改了只读源')
    return {'pass':True,'purpose':'Linux边界合同与两种真实原生调度的100图正确性，不作性能结论',
        'build_sha256':policy['build']['sha256'],'plan_sha256':policy['plan']['sha256'],
        'environment':environment(),'libraries':build['libraries'],'loaded_libraries':maps,'teams':teams,
        'finite_backend_offset_comparisons':comparisons,'diagnostic_negative_checks':negative,'memory':mem,
        'driver_negative_contract':driver_contract,'driver_callback_failure_aborted':True,'photos':photos,
        'photo_source_sha256':source_sha,'timings_used_for_selection':False,'new_fits':0,'byte_mismatches':0}
def worker(policy,bundle,index):
    if (policy['orders']!=ORDERS or policy['thread_orders']!=THREADS or policy['mode_orders']!=MODES
            or policy['repeats']!=5 or policy['gates']!=GATES):raise ValueError('性能策略不是固定预声明方案')
    full=read(checked(policy['correctness']['full']));contract=read(checked(policy['correctness']['contract']))
    if (not full['pass'] or not contract['pass'] or full['build_sha256']!=policy['build']['sha256']
            or contract['build_sha256']!=policy['build']['sha256']
            or len(full['full_domain_pixels_per_configuration'])!=12
            or set(full['full_domain_pixels_per_configuration'].values())!={256**3}
            or contract['finite_backend_offset_comparisons']!=2112 or len(contract['photos'])!=8):
        raise ValueError('性能调用前需要同构建的完整正确性证据')
    plan,build,libs,driver,teams,maps=load_native(policy);source,work,source_sha=photo_buffers(bundle);records=[]
    for threads in THREADS[index]:
        for mode in MODES[index]:
            for name in ORDERS[index]:
                d=libs[name];started=time.perf_counter();h=actual_chain(plan,d);prepare=time.perf_counter()-started
                try:
                    flags=layouts(d,h,4)
                    if name=='candidate' and flags!=plan['delta16_policy']['actual_chain_layouts']:raise ValueError('计时实际布局不同')
                    measure(driver,d,h,source,work,1024*768*3,100,threads,mode,1)
                    if hashlib.sha256(work).hexdigest()!=bundle['photo_output_sha256']:raise AssertionError('预热100图不同')
                    start=environment();values=measure(driver,d,h,source,work,1024*768*3,100,threads,mode,5)
                    output_sha=hashlib.sha256(work).hexdigest()
                    if output_sha!=bundle['photo_output_sha256']:raise AssertionError('计时后100图不同')
                    records.append({'variant':name,'threads':threads,'mode':mode,'images':100,'repeats':5,
                        'prepare_wall_seconds':prepare,'model_accounting_bytes':d.jshc_cc_model_bytes(h),
                        'coordinate_layouts':flags,'library_sha256':build['libraries'][name]['sha256'],
                        'output_sha256':output_sha,'start_state':start,'end_state':environment(),**values})
                finally:d.jshc_cc_destroy(h)
    if hashlib.sha256(source).hexdigest()!=source_sha:raise AssertionError('计时改变只读源')
    if loaded([*build['libraries'].values(),policy['driver']])!=maps:raise ValueError('计时期间动态库来源改变')
    return {'worker_index':index,'pid':os.getpid(),'environment':environment(),'teams':teams,'loaded_libraries':maps,
        'source_sha256':source_sha,'records':records,'whole_process_peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'rss_scope':'Linux整个worker峰值，包含235929600字节源和同大小工作区；不是模型容量'}
def aggregate(workers):
    rows=[];failures=[]
    for threads in (1,4):
        for mode in (0,1):
            pairs=[{r['variant']:r for r in w['records'] if r['threads']==threads and r['mode']==mode} for w in workers]
            apply_ratios=[statistics.median(p['candidate']['round_apply_seconds'])/statistics.median(p['reference']['round_apply_seconds']) for p in pairs]
            copy_ratios=[statistics.median(p['candidate']['round_copy_apply_seconds'])/statistics.median(p['reference']['round_copy_apply_seconds']) for p in pairs]
            wall_ratios=[statistics.median(p['candidate']['round_wall_seconds'])/statistics.median(p['reference']['round_wall_seconds']) for p in pairs]
            if statistics.median(apply_ratios)>GATES['median_apply_ratio_max']:failures.append(f'{threads}线程/mode{mode} apply中位不足3%改善')
            if max(apply_ratios)>GATES['any_process_apply_ratio_max']:failures.append(f'{threads}线程/mode{mode} 单进程回退超2%')
            if statistics.median(copy_ratios)>GATES['median_copy_apply_ratio_max']:failures.append(f'{threads}线程/mode{mode} copy+apply退化')
            details={}
            for name in ('reference','candidate'):
                samples=sorted(x for p in pairs for x in p[name]['segment_apply_seconds'])
                details[name]={'process_round_medians_seconds':[statistics.median(p[name]['round_apply_seconds']) for p in pairs],
                    'model_accounting_bytes':[p[name]['model_accounting_bytes'] for p in pairs],
                    'prepare_wall_seconds':[p[name]['prepare_wall_seconds'] for p in pairs],
                    'segment_apply_ms_median':statistics.median(samples)*1000,
                    'segment_apply_ms_p99_nearest_rank':samples[math.ceil(.99*len(samples))-1]*1000,
                    'segment_apply_ms_max':samples[-1]*1000,
                    'segment_scope':'一次100图批调用' if mode==0 else '一次单图原生调用；重复照片/轮次不是独立随机请求'}
            rows.append({'threads':threads,'mode':mode,'process_apply_ratios':apply_ratios,
                'median_apply_ratio':statistics.median(apply_ratios),'process_copy_apply_ratios':copy_ratios,
                'median_copy_apply_ratio':statistics.median(copy_ratios),'process_round_wall_ratios':wall_ratios,
                'median_round_wall_ratio':statistics.median(wall_ratios),'variants':details})
    return {'measurement_completed':True,'passed_fixed_host_gates':not failures,'failed_gates':failures,'paired':rows,
        'scope':'实际主机、编译器和固定模型下的描述性配对比较；未经SKU核对不自称Skylake，不是官方成绩或文件端到端',
        'statistical_scope':'4个新进程各配置5轮中位后配对；不报告总体显著性，不混用旧内部bench绝对时间'}
def run_command(command,out,env):
    r=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace')
    save(out,{'command':command,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
    if r.returncode:raise RuntimeError('子步骤失败，保留日志：'+str(out))
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--compiler',default='g++');p.add_argument('--c-compiler',default='gcc');p.add_argument('--cmake',default='cmake')
    p.add_argument('--cpus');p.add_argument('--expected-cpu');p.add_argument('--measure',action='store_true')
    p.add_argument('--child-policy',type=Path);p.add_argument('--worker',type=int);p.add_argument('--validate',action='store_true')
    args=p.parse_args();bundle=read(args.bundle)
    if args.bundle.resolve()!=ROOT/'bundle-manifest.json':raise ValueError('请在独立固定字节包内运行，避免误用当前开发树的输入')
    if args.child_policy:
        policy=read(args.child_policy);frozen_sources(bundle)
        if policy['bundle_sha256']!=digest(args.bundle):raise ValueError('子进程包身份不同')
        if args.validate:result=validate(policy,bundle)
        elif args.worker in range(4):result=worker(policy,bundle,args.worker)
        else:raise ValueError('内部子进程参数错误')
        frozen_sources(bundle);save(args.output,result);print('子步骤完成',flush=True);return
    top=topology([int(x) for x in args.cpus.split(',')] if args.cpus else None);env0=environment()
    if 'avx2' not in env0['cpu'].get('flags','').split():raise ValueError('当前CPU不支持AVX2')
    if args.expected_cpu and args.expected_cpu!=env0['cpu'].get('model name'):raise ValueError('实际CPU与指定SKU不符')
    for name,s in bundle['files'].items():
        if name!=s['path']:raise ValueError('包文件名与路径不同')
        checked(s)
    out=args.output.resolve()
    if out.exists():raise ValueError('输出目录必须全新；失败后不自动重试或覆盖')
    out.mkdir(parents=True)
    selected=top['selected_cpus'];env=os.environ.copy()
    for key in list(env):
        if key.startswith(('OMP_','GOMP_','KMP_')):env.pop(key)
    env.update(OMP_NUM_THREADS='1',OMP_DYNAMIC='FALSE',OMP_THREAD_LIMIT='256',OMP_SCHEDULE='STATIC',
        OMP_PROC_BIND='CLOSE',OMP_PLACES=','.join('{'+str(x)+'}' for x in selected),
        OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONIOENCODING='utf-8')
    save(out/'run.json',{'purpose':__doc__,'bundle_sha256':digest(args.bundle),'topology':top,'environment_before':env0,
        'child_thread_environment':{k:v for k,v in env.items() if k.startswith(('OMP_','GOMP_','KMP_'))},
        'performance_requested':args.measure,'orders':ORDERS,'thread_orders':THREADS,'mode_orders':MODES,'gates':GATES,
        'expected_cpu':args.expected_cpu,'target_scope':'仅报告实际CPU，当前目标硬件认定须由记录的SKU核对','started_utc':datetime.now(timezone.utc).isoformat()})
    try:
        compiler=shutil.which(args.compiler);ccompiler=shutil.which(args.c_compiler);cmake=shutil.which(args.cmake)
        if not compiler or not ccompiler or not cmake:raise ValueError('找不到CMake/GNU C/C++编译器，不自动安装依赖')
        plan_path=ROOT/bundle['plan'];build=out/'backend';driver=out/'driver'
        run_command([sys.executable,str(ROOT/'scripts/build_skylake_runtime.py'),'--plan',str(plan_path),'--output',str(build),
            '--compiler',compiler,'--c-compiler',ccompiler,'--cmake',cmake],out/'backend-build-command.json',env)
        run_command([cmake,'-S',str(ROOT/'experiments/skylake-server-driver'),'-B',str(driver),'-DCMAKE_BUILD_TYPE=Release',
            '-DCMAKE_EXPORT_COMPILE_COMMANDS=ON','-DCMAKE_CXX_COMPILER='+compiler],out/'driver-configure.json',env)
        run_command([cmake,'--build',str(driver),'--parallel','4'],out/'driver-build.json',env)
        for r in read(driver/'compile_commands.json'):
            if any(s in r['command'] for s in ('-march=','-mavx','-mfma','-ffast-math','-Ofast')):raise ValueError('计时器不得包含目标ISA或fast-math选项')
        lib=Path(read(driver/'driver-Release.json')['path'])
        policy={'bundle_sha256':digest(args.bundle),'selected_cpus':selected,
            'plan':{'path':str(plan_path),'sha256':digest(plan_path)},'build':{'path':str(build/'build.json'),'sha256':digest(build/'build.json')},
            'driver':{'path':str(lib),'sha256':digest(lib)},'orders':ORDERS,'thread_orders':THREADS,'mode_orders':MODES,'repeats':5,'gates':GATES,
            'compiler':{'path':compiler,'sha256':digest(compiler),'version':subprocess.check_output([compiler,'--version'],text=True)},
            'c_compiler':{'path':ccompiler,'sha256':digest(ccompiler)},'cmake':{'path':cmake,'sha256':digest(cmake)}}
        policy_path=out/'policy.json';save(policy_path,policy)
        run_command([sys.executable,str(ROOT/'scripts/verify_skylake_linux_stdlib.py'),'--plan',str(plan_path),'--build',str(build),
            '--single-oracle-stream',str(ROOT/bundle['single_oracle_stream']),'--affinity-cpus',','.join(map(str,selected)),
            '--output',str(out/'full')],out/'full-command.json',env)
        if not read(out/'full/results.json')['pass']:raise ValueError('完整色域未通过')
        run_command([sys.executable,str(Path(__file__).resolve()),'--bundle',str(args.bundle.resolve()),'--output',str(out/'contract.json'),
            '--child-policy',str(policy_path),'--validate'],out/'contract-command.json',env)
        if not read(out/'contract.json')['pass']:raise ValueError('边界或计时器合同未通过')
        if args.measure:
            performance_policy={**policy,'correctness':{
                'full':{'path':str(out/'full/results.json'),'sha256':digest(out/'full/results.json')},
                'contract':{'path':str(out/'contract.json'),'sha256':digest(out/'contract.json')}}}
            performance_path=out/'performance-policy.json';save(performance_path,performance_policy)
            workers=[]
            for index in range(4):
                destination=out/f'worker{index}.json'
                run_command([sys.executable,str(Path(__file__).resolve()),'--bundle',str(args.bundle.resolve()),'--output',str(destination),
                    '--child-policy',str(performance_path),'--worker',str(index)],out/f'worker{index}-command.json',env)
                workers.append(read(destination));print('完成串行性能进程',index,flush=True)
            if len({w['source_sha256'] for w in workers})!=1:raise ValueError('计时源不同')
            measured=aggregate(workers);measured['policy_sha256']=digest(performance_path)
            measured['worker_sha256']=[digest(out/f'worker{i}.json') for i in range(4)]
            save(out/'performance.json',measured)
        frozen_sources(bundle)
        for s in bundle['files'].values():checked(s)
        save(out/'results.json',{'pass':True,'correctness_passed':True,'performance_measured':args.measure,
            'performance_gates_passed':read(out/'performance.json')['passed_fixed_host_gates'] if args.measure else None,
            'bundle_sha256':digest(args.bundle),'full_sha256':digest(out/'full/results.json'),
            'contract_sha256':digest(out/'contract.json'),'policy_sha256':digest(policy_path),
            'finished_utc':datetime.now(timezone.utc).isoformat(),
            'scope':'实际Linux主机见run/contract，性能未请求时不作任何加速结论；不自动标为Skylake或官方通过'})
        print('服务器入口完成；正式性能比较：',args.measure,flush=True)
    except Exception:
        save(out/'failure.json',{'pass':False,'traceback':traceback.format_exc(),'scope':'失败后保留证据，不自动重试或调参'})
        raise

if __name__=='__main__':main()
