"""标准库按来宾空闲前置条件直接比较冻结候选与23；冻结四进程80轮，每轮分别测旧接口与真实输出接口，逐轮核验输出。"""
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
    libraries={name:bind(checked(spec)) for name,spec in build['libraries'].items()}
    for role,d in libraries.items():
        if d.jshc_cc_abi_version()!=1 or d.jshc_cc_revision()!=build['revisions'][role] or d.jshc_cc_capabilities()!=7:raise ValueError('实际ABI/修订/后端不符')
    driver=driver_bind(checked(policy['driver']));records=[];error=ct.create_string_buffer(1024)
    initial_team=pinned_probe(driver,4,cpus)
    index=args.worker_index
    for threads in policy['thread_orders'][index]:
        probe=pinned_probe(driver,threads,cpus)
        for role in policy['orders'][index]:
            d=libraries[role];start=time.perf_counter();handle=create(d,models,sides);prepare=time.perf_counter()-start
            try:
                state=direct_info(d,handle);pages=paged_info(d,handle)
                if role=='candidate' and (state['enabled']!=1 or state['format']!=18 or state['table_capacity_bytes']!=2**24 or not pages['fully_huge']):
                    raise ValueError('实际候选必须启用16MiB精确小端大工作块NTA输出索引及完全THP，不以advice代替页事实')
                f=d.jshc_cc_bench;f.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint8),ct.POINTER(ct.c_uint8),ct.c_size_t,ct.c_int,ct.c_int,ct.c_size_t,ct.POINTER(ct.c_double),ct.POINTER(ct.c_double),ct.POINTER(ct.c_char),ct.c_size_t];f.restype=ct.c_int
                bind_to(d)
                fto=d.jshc_cc_bench_to;fto.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint8),ct.POINTER(ct.c_uint8),ct.c_size_t,ct.c_int,ct.c_int,ct.c_size_t,ct.POINTER(ct.c_double),ct.POINTER(ct.c_char),ct.c_size_t];fto.restype=ct.c_int
                ct.memmove(work,source_pointer,n)
                if d.jshc_cc_apply(handle,work,n,1,threads,error,len(error)):raise RuntimeError(error.value.decode())
                expected=policy['expected_output_sha256'];warm=output_hash()
                if warm!=expected:raise AssertionError('完整100图预热输出不同')
                if d.jshc_cc_apply_to(handle,source_pointer,work,n,1,threads,error,len(error)):raise RuntimeError(error.value.decode())
                if output_hash()!=expected:raise AssertionError('真实输出接口预热不同')
                apply_seconds=[];copy_apply_seconds=[];outplace_seconds=[];hashes=[];out_hashes=[];mode_orders=[]
                for round_index in range(policy['repeats']):
                    modes=['legacy','outplace'] if (index+round_index)%2==0 else ['outplace','legacy']
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
                    'per_round_output_sha256':hashes,'prepare_plus_first_100_copy_apply_seconds':prepare+copy_apply_seconds[0],'prepare_plus_first_100_outplace_seconds':prepare+outplace_seconds[0],
                    'prepare_plus_first_100_apply_seconds':prepare+apply_seconds[0],'actual_affinity':sorted(os.sched_getaffinity(0))})
            finally:d.jshc_cc_destroy(handle)
    if hashlib.sha256(source).hexdigest()!=source_sha:raise AssertionError('只读源被改写')
    return {'worker_index':index,'pid':os.getpid(),'order':policy['orders'][index],'thread_order':policy['thread_orders'][index],
        'initial_team':initial_team,'selected_cpus':cpus,'actual_affinity':sorted(os.sched_getaffinity(0)),'source_sha256':source_sha,'source_bytes':n,'records':records,'topology':top,
        'environment':environment(cpus),'loaded_libraries':loaded([*build['libraries'].values(),policy['driver']]),
        'build_sha256':policy['build']['sha256'],'full_acceptance_sha256':policy['full_acceptance']['sha256'],'libraries':build['libraries']}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--policy',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--worker-index',type=int)
    args=p.parse_args();policy=read(args.policy)
    for key in ('plan','build','full_acceptance','photos','driver','validation','benchmark_script','pinning_support','pinning_probe','quiet_support'):checked(policy[key])
    if args.worker_index is not None:
        save(args.output,worker(args,policy));print('完成Linux性能进程',args.worker_index,flush=True);return
    if args.output.exists():raise ValueError('不得覆盖或重试旧性能目录')
    if policy['orders']!=[['reference','candidate'],['candidate','reference'],['candidate','reference'],['reference','candidate']] or policy['repeats']!=5:raise ValueError('冻结顺序不符')
    args.output.mkdir(parents=True)
    plan=read(checked(policy['plan']));names=[*plan['source_sha256'],'scripts/bench_skylake_chroma_batch4_io_quiet_linux.py','scripts/pinned_openmp_support.py','scripts/quiet_host_support.py','scripts/paged_table_support.py','scripts/outplace_support.py','scripts/skylake_server_support.py','scripts/verify_skylake_linux_stdlib.py',args.policy.resolve().relative_to(ROOT).as_posix()]
    sources={name:digest(ROOT/name) for name in sorted(set(names))}
    save(args.output/'run.json',{'purpose':__doc__,'policy':policy,'source_sha256':sources,'environment':environment(),'scope':'同Linux/AMD，原生235MB整批apply、旧copy+apply及真实source→destination输出，不含IO/解码/分配/SHA，非Skylake实测'})
    with zipfile.ZipFile(args.output/'measured-source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in sources:z.write(ROOT/name,name)
    env=os.environ.copy();env.update(OMP_NUM_THREADS='1',OMP_DYNAMIC='FALSE',OMP_PROC_BIND='TRUE',OMP_PLACES=places(policy['affinity_cpus']),OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    for key in ('GOMP_CPU_AFFINITY',):env.pop(key,None)
    quiet=policy['quiet_protocol']
    require_quiet(quiet,policy['affinity_cpus'],args.output,'quiet-parent',quiet['minimum_parent_settle_seconds'])
    workers=[]
    for index in range(4):
        require_quiet(quiet,policy['affinity_cpus'],args.output,f'quiet-worker{index}',0)
        path=args.output/f'worker{index}.json';proc=subprocess.run([sys.executable,'-u',str(Path(__file__).resolve()),'--policy',str(args.policy.resolve()),'--output',str(path.resolve()),'--worker-index',str(index)],cwd=ROOT,env=env,capture_output=True,text=True)
        (args.output/f'worker{index}.stdout.log').write_text(proc.stdout,encoding='utf-8');(args.output/f'worker{index}.stderr.log').write_text(proc.stderr,encoding='utf-8')
        if proc.returncode:raise RuntimeError('性能进程失败，保留所有原始数据：'+proc.stderr)
        workers.append(read(path));print('完成串行Linux进程',index,flush=True)
    summary=[];paired=[];failed=[]
    for threads in (1,4):
        matches=[{r['variant']:r for r in w['records'] if r['requested_threads']==threads} for w in workers]
        for role in ('reference','candidate'):
            summary.append({'variant':role,'requested_threads':threads,'median_apply_ms_per_image':statistics.median(statistics.median(m[role]['apply_seconds'])*10 for m in matches),
                'median_legacy_copy_apply_ms_per_image':statistics.median(statistics.median(m[role]['legacy_copy_apply_seconds'])*10 for m in matches),
                'median_outplace_ms_per_image':statistics.median(statistics.median(m[role]['outplace_seconds'])*10 for m in matches),
                'prepare_wall_seconds':[m[role]['prepare_wall_seconds'] for m in matches],'model_accounting_bytes':matches[0][role]['model_accounting_bytes']})
        a=[statistics.median(m['candidate']['apply_seconds'])/statistics.median(m['reference']['apply_seconds']) for m in matches]
        c=[statistics.median(m['candidate']['legacy_copy_apply_seconds'])/statistics.median(m['reference']['legacy_copy_apply_seconds']) for m in matches]
        out=[statistics.median(m['candidate']['outplace_seconds'])/statistics.median(m['reference']['outplace_seconds']) for m in matches]
        prep=[m['candidate']['prepare_plus_first_100_outplace_seconds']/m['reference']['prepare_plus_first_100_outplace_seconds'] for m in matches]
        g=policy['adoption_gate']
        if statistics.median(a)>g['median_apply_ratio_max']:failed.append(f'{threads}线程apply未达3倍')
        if statistics.median(out)>g['median_outplace_ratio_max']:failed.append(f'{threads}线程真实输出未达3倍')
        if max(a)>g['any_process_apply_ratio_max']:failed.append(f'{threads}线程某apply进程回退超限')
        if statistics.median(prep)>g['median_prepare_plus_100_ratio_max']:failed.append(f'{threads}线程准备+首组回退')
        paired.append({'requested_threads':threads,'process_apply_ratios':a,'median_apply_ratio':statistics.median(a),'process_legacy_copy_apply_ratios':c,'median_legacy_copy_apply_ratio':statistics.median(c),'process_outplace_ratios':out,'median_outplace_ratio':statistics.median(out),
            'process_prepare_plus_100_outplace_ratios':prep,'median_prepare_plus_100_outplace_ratio':statistics.median(prep)})
    for name,sha in sources.items():
        if digest(ROOT/name)!=sha:raise ValueError('计时期间源码改变')
    result={'measurement_completed':True,'accepted_on_this_host':not failed,'failed_gates':failed,'summary':summary,'paired':paired,
        'worker_sha256':[digest(args.output/f'worker{i}.json') for i in range(4)],'selected_cpus':policy['affinity_cpus'],'actual_main_affinity':[policy['affinity_cpus'][0]],'frequency_and_temperature_controlled':False,
        'scope':'本机Linux/AMD同场比较冻结候选与23，不与Windows绝对耗时相除，不外推Skylake；新空闲协议首次计时，各固定候选只运行一次；旧协议及失败记录全部另存，不混算'}
    save(args.output/'results.json',result);print('Linux固定比较完成',result['accepted_on_this_host'],paired,flush=True)
if __name__=='__main__':main()
