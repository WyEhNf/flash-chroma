"""标准库以独立配置进程、来宾空闲前置条件比较40与23；冻结四进程80轮，每轮分别测旧接口与真实输出接口，逐轮核验输出。"""
import argparse,ctypes as ct,hashlib,math,os,statistics,subprocess,sys,time,zipfile
from pathlib import Path
from skylake_server_support import ROOT,read,save,digest,checked,topology,environment,loaded,driver_bind,team
from verify_skylake_linux_stdlib import bind,create
from paged_table_support import direct_info,paged_info
from outplace_support import bind_to
from quiet_host_support import require_quiet
from pinned_openmp_support import probe as pinned_probe,state as pinned_state,require_environment,places

def worker(args,policy):
    cpus=policy['affinity_cpus'];require_environment(cpus);os.sched_setaffinity(0,cpus);top=topology(cpus)
    plan=read(checked(policy['plan']));build=read(checked(policy['build']));full=read(checked(policy['full_acceptance']))
    if build['plan_sha256']!=policy['plan']['sha256'] or not full['pass'] or full['build_sha256']!=policy['build']['sha256'] or full['libraries']!=build['libraries']:
        raise ValueError('构建/完整验收身份不符')
    for name,sha in plan['source_sha256'].items():
        if digest(ROOT/name)!=sha:raise ValueError('冻结源码变化：'+name)
    models=[checked(plan['fixed_inputs']['base']),*[checked(s) for s in plan['suffix_models']]]
    sides=[checked(plan['fixed_inputs']['sidecar']),None,None,None]
    source_bytes=checked(policy['photos']).read_bytes()
    if len(source_bytes)!=235929600:raise ValueError('不是固定100图RGB8流')
    source=(ct.c_uint8*len(source_bytes)).from_buffer_copy(source_bytes);del source_bytes
    n=len(source);source_sha=hashlib.sha256(source).hexdigest();guard=ct.create_string_buffer(n+32)
    ct.memset(guard,0xa7,len(guard));work=ct.cast(ct.addressof(guard)+16,ct.POINTER(ct.c_uint8));source_pointer=ct.cast(source,ct.POINTER(ct.c_uint8))
    def output_hash():
        if bytes(guard[:16])!=b'\xa7'*16 or bytes(guard[n+16:n+32])!=b'\xa7'*16:raise AssertionError('计时器越界写')
        return hashlib.sha256(memoryview(guard).cast('B')[16:n+16]).hexdigest()
    libraries={args.worker_role:bind(checked(build['libraries'][args.worker_role]))}
    for role,d in libraries.items():
        if d.jshc_cc_abi_version()!=1 or d.jshc_cc_revision()!=build['revisions'][role] or d.jshc_cc_capabilities()!=7:raise ValueError('实际ABI/修订/后端不符')
    driver=driver_bind(checked(policy['driver']));records=[];error=ct.create_string_buffer(1024)
    other='candidate' if args.worker_role=='reference' else 'reference'
    maps=Path('/proc/self/maps').read_text()
    if str(checked(build['libraries'][other])) in maps:raise ValueError('独立配置进程加载了另一角色的主库')
    initial_team=pinned_probe(driver,4,cpus)
    index=args.worker_index
    for threads in (args.worker_threads,):
        probe=pinned_probe(driver,threads,cpus)
        for role in (args.worker_role,):
            d=libraries[role];start=time.perf_counter();handle=create(d,models,sides);prepare=time.perf_counter()-start
            try:
                state=direct_info(d,handle);pages=paged_info(d,handle)
                if role=='candidate' and (state['enabled']!=1 or state['format']!=9 or state['table_capacity_bytes']!=2**24 or not pages['fully_huge']):
                    raise ValueError('实际候选必须启用16MiB精确小端大工作块NTA输出索引及完全THP，不以advice代替页事实')
                f=d.jshc_cc_bench;f.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint8),ct.POINTER(ct.c_uint8),ct.c_size_t,ct.c_int,ct.c_int,ct.c_size_t,ct.POINTER(ct.c_double),ct.POINTER(ct.c_double),ct.POINTER(ct.c_char),ct.c_size_t];f.restype=ct.c_int
                bind_to(d)
                fto=d.jshc_cc_bench_to;fto.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint8),ct.POINTER(ct.c_uint8),ct.c_size_t,ct.c_int,ct.c_int,ct.c_size_t,ct.POINTER(ct.c_double),ct.POINTER(ct.c_char),ct.c_size_t];fto.restype=ct.c_int
                expected=policy['expected_output_sha256']
                if args.api_mode=='legacy':
                    ct.memmove(work,source_pointer,n)
                    if d.jshc_cc_apply(handle,work,n,1,threads,error,len(error)):raise RuntimeError(error.value.decode())
                else:
                    if d.jshc_cc_apply_to(handle,source_pointer,work,n,1,threads,error,len(error)):raise RuntimeError(error.value.decode())
                warm=output_hash()
                if warm!=expected:raise AssertionError('独立模式预热完整输出不同')
                apply_seconds=[];copy_apply_seconds=[];outplace_seconds=[];hashes=[];out_hashes=[];mode_orders=[]
                for round_index in range(policy['repeats']):
                    modes=[args.api_mode]
                    mode_orders.append(modes)
                    for mode in modes:
                        a=ct.c_double();c=ct.c_double()
                        if mode=='legacy':
                            if f(handle,source_pointer,work,n,1,threads,1,ct.byref(a),ct.byref(c),error,len(error)):raise RuntimeError(error.value.decode())
                            if not (math.isfinite(a.value) and math.isfinite(c.value) and 0<a.value<=c.value):raise ValueError('旧接口计时非法')
                            apply_seconds.append(a.value);copy_apply_seconds.append(c.value)
                        else:
                            if fto(handle,source_pointer,work,n,1,threads,1,ct.byref(c),error,len(error)):raise RuntimeError(error.value.decode())
                            if not (math.isfinite(c.value) and c.value>0):raise ValueError('真实输出计时非法')
                            outplace_seconds.append(c.value)
                        result_hash=output_hash()
                        if result_hash!=expected:raise AssertionError('计时轮完整输出不同')
                        (hashes if mode=='legacy' else out_hashes).append(result_hash)
                if sorted(os.sched_getaffinity(0))!=cpus[:1]:raise ValueError('实际主线程固定CPU变化')
                records.append({'task_affinities_after_rounds':pinned_state(cpus),'variant':role,'requested_threads':threads,'actual_team':probe,'kernel':'avx2','images':100,'stages':4,
                    'library_revision':d.jshc_cc_revision(),'library_sha256':build['libraries'][role]['sha256'],
                    'model_accounting_bytes':d.jshc_cc_model_bytes(handle),'prepare_wall_seconds':prepare,'direct_info':state,'paged_info':pages,
                    'paged_info_after_rounds':paged_info(d,handle),'warmup_output_sha256':warm,'apply_seconds':apply_seconds,'legacy_copy_apply_seconds':copy_apply_seconds,'outplace_seconds':outplace_seconds,'mode_orders':mode_orders,'outplace_output_sha256':out_hashes,
                    'per_round_output_sha256':hashes,'prepare_plus_first_100_copy_apply_seconds':(prepare+copy_apply_seconds[0] if copy_apply_seconds else None),'prepare_plus_first_100_outplace_seconds':(prepare+outplace_seconds[0] if outplace_seconds else None),
                    'prepare_plus_first_100_apply_seconds':(prepare+apply_seconds[0] if apply_seconds else None),'actual_affinity':sorted(os.sched_getaffinity(0))})
            finally:d.jshc_cc_destroy(handle)
    if hashlib.sha256(source).hexdigest()!=source_sha:raise AssertionError('只读源被改写')
    return {'worker_index':index,'pid':os.getpid(),'order':[args.worker_role],'role':args.worker_role,'api_mode':args.api_mode,'parent_pid':os.getppid(),'primary_library_isolated':True,'thread_order':[args.worker_threads],
        'initial_team':initial_team,'selected_cpus':cpus,'actual_affinity':sorted(os.sched_getaffinity(0)),'source_sha256':source_sha,'source_bytes':n,'records':records,'topology':top,
        'environment':environment(cpus),'loaded_libraries':loaded([build['libraries'][args.worker_role],policy['driver']]),
        'build_sha256':policy['build']['sha256'],'full_acceptance_sha256':policy['full_acceptance']['sha256'],'libraries':{args.worker_role:build['libraries'][args.worker_role]}}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--policy',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--worker-index',type=int);p.add_argument('--worker-role',choices=['reference','candidate'])
    p.add_argument('--worker-threads',type=int,choices=[1,4]);p.add_argument('--api-mode',choices=['legacy','outplace'])
    args=p.parse_args();policy=read(args.policy)
    for key in ('plan','build','full_acceptance','photos','driver','validation','benchmark_script','pinning_support','pinning_probe','quiet_support'):checked(policy[key])
    if args.output.exists():raise ValueError('不得覆盖或重试既有隔离性能输出')
    if args.worker_index is not None:
        if args.worker_role is None or args.worker_threads is None or args.api_mode is None:raise ValueError('子进程必须恰好指定一个角色、线程数和API模式')
        save(args.output,worker(args,policy));print('完成独立子配置',args.worker_index,args.worker_role,args.worker_threads,args.api_mode,flush=True);return
    assert policy['protocol_revision']=='isolated-config-v1' and policy['process_isolation']['dimensions']==['role','threads','api_mode']
    assert policy['orders']==[['reference','candidate'],['candidate','reference'],['candidate','reference'],['reference','candidate']] and policy['repeats']==5
    args.output.mkdir(parents=True)
    plan=read(checked(policy['plan']));names=[*plan['source_sha256'],'scripts/bench_skylake_isolated_pinned_linux.py','scripts/quiet_host_support.py','scripts/pinned_openmp_support.py','scripts/paged_table_support.py','scripts/outplace_support.py','scripts/skylake_server_support.py','scripts/verify_skylake_linux_stdlib.py',args.policy.resolve().relative_to(ROOT).as_posix()]
    sources={name:digest(ROOT/name) for name in sorted(set(names))}
    save(args.output/'run.json',{'purpose':__doc__,'policy':policy,'source_sha256':sources,'environment':environment(),'scope':'同Linux/AMD，32个串行独立配置进程，每配置5轮100图；不外推Skylake，不含I/O、分配、SHA，不混算旧协议'})
    with zipfile.ZipFile(args.output/'measured-source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in sources:z.write(ROOT/name,name)
    env=os.environ.copy();env.update(OMP_NUM_THREADS='1',OMP_DYNAMIC='FALSE',OMP_PROC_BIND='TRUE',OMP_PLACES=places(policy['affinity_cpus']),OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1');env.pop('GOMP_CPU_AFFINITY',None)
    q=policy['quiet_protocol'];require_quiet(q,policy['affinity_cpus'],args.output,'quiet-parent',q['minimum_parent_settle_seconds'])
    pairs=[];children={};pids=[]
    for index in range(4):
        configs={};records=[]
        for threads in policy['thread_orders'][index]:
            for role in policy['orders'][index]:
                for mode in policy['mode_orders'][index]:
                    key=f'p{index}-t{threads}-{role}-{mode}';path=args.output/(key+'.json')
                    require_quiet(q,policy['affinity_cpus'],args.output,'quiet-'+key,0)
                    command=[sys.executable,'-u',str(Path(__file__).resolve()),'--policy',str(args.policy.resolve()),'--output',str(path.resolve()),'--worker-index',str(index),'--worker-role',role,'--worker-threads',str(threads),'--api-mode',mode]
                    proc=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True)
                    (args.output/(key+'.stdout.log')).write_text(proc.stdout,encoding='utf-8');(args.output/(key+'.stderr.log')).write_text(proc.stderr,encoding='utf-8')
                    if proc.returncode:raise RuntimeError('独立子配置失败，保留全部部分数据：'+proc.stderr)
                    child=read(path);assert len(child['records'])==1
                    configs[(threads,role,mode)]=child;children[key]=digest(path);pids.append(child['pid'])
                    print('完成独立配置',len(children),'/32',key,flush=True)
        for threads in (1,4):
            for role in ('reference','candidate'):
                legacy=configs[(threads,role,'legacy')]['records'][0];out=configs[(threads,role,'outplace')]['records'][0]
                assert legacy['model_accounting_bytes']==out['model_accounting_bytes'] and legacy['library_sha256']==out['library_sha256']
                records.append({'variant':role,'requested_threads':threads,'apply_seconds':legacy['apply_seconds'],'legacy_copy_apply_seconds':legacy['legacy_copy_apply_seconds'],'outplace_seconds':out['outplace_seconds'],'prepare_wall_seconds':out['prepare_wall_seconds'],'prepare_plus_first_100_outplace_seconds':out['prepare_plus_first_100_outplace_seconds'],'model_accounting_bytes':out['model_accounting_bytes'],'measurement_sources':{mode:{'file':f'p{index}-t{threads}-{role}-{mode}.json','sha256':children[f'p{index}-t{threads}-{role}-{mode}'],'pid':configs[(threads,role,mode)]['pid']} for mode in ('legacy','outplace')}})
        pair={'kind':'derived_pair_of_independent_configuration_processes','pair_index':index,'order':policy['orders'][index],'thread_order':policy['thread_orders'][index],'mode_order':policy['mode_orders'][index],'records':records}
        pairs.append(pair);save(args.output/f'pair{index}.json',pair)
    assert len(children)==32 and len(set(pids))==32
    paired=[];summary=[];failed=[];g=policy['adoption_gate']
    for threads in (1,4):
        matches=[{r['variant']:r for r in pair['records'] if r['requested_threads']==threads} for pair in pairs];row={'requested_threads':threads}
        for key,label in [('apply_seconds','apply'),('legacy_copy_apply_seconds','legacy_copy_apply'),('outplace_seconds','outplace')]:
            ratios=[statistics.median(m['candidate'][key])/statistics.median(m['reference'][key]) for m in matches]
            row['pair_'+label+'_ratios']=ratios;row['median_'+label+'_ratio']=statistics.median(ratios)
        prep=[m['candidate']['prepare_plus_first_100_outplace_seconds']/m['reference']['prepare_plus_first_100_outplace_seconds'] for m in matches];row['pair_prepare_plus_100_outplace_ratios']=prep;row['median_prepare_plus_100_outplace_ratio']=statistics.median(prep)
        if row['median_apply_ratio']>g['median_apply_ratio_max']:failed.append(f'{threads}线程纯映射未达3倍')
        if row['median_outplace_ratio']>g['median_outplace_ratio_max']:failed.append(f'{threads}线程真实输出未达3倍')
        if max(row['pair_apply_ratios'])>g['any_process_apply_ratio_max']:failed.append(f'{threads}线程某配对回退超限')
        if statistics.median(prep)>g['median_prepare_plus_100_ratio_max']:failed.append(f'{threads}线程准备加首组回退')
        paired.append(row)
        for role in ('reference','candidate'):
            summary.append({'variant':role,'requested_threads':threads,**{'median_'+label+'_ms_per_image':statistics.median(statistics.median(m[role][key])*10 for m in matches) for key,label in [('apply_seconds','apply'),('legacy_copy_apply_seconds','legacy_copy_apply'),('outplace_seconds','outplace')]},'prepare_wall_seconds':[m[role]['prepare_wall_seconds'] for m in matches],'model_accounting_bytes':matches[0][role]['model_accounting_bytes']})
    for name,digest_before in sources.items():assert digest(ROOT/name)==digest_before,name
    result={'measurement_completed':True,'accepted_on_this_host':not failed,'failed_gates':failed,'paired':paired,'summary':summary,'child_sha256':children,'pair_sha256':[digest(args.output/f'pair{i}.json') for i in range(4)],'independent_child_processes':32,'unique_pids':pids,'mode_rounds':{'legacy':80,'outplace':80},'frequency_and_temperature_controlled':False,'scope':'每角色、线程、API模式独立进程，只加载自己的主库，避免不同实现的分配/大页/加载状态在同进程延续；来宾空闲不等于宿主独占，实际Skylake未测'}
    save(args.output/'results.json',result);print('隔离协议完成',result['accepted_on_this_host'],paired,flush=True)
if __name__=='__main__':main()
