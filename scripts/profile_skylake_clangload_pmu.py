"""探索性硬件计数画像：固定1/4线程，40/55各一次计数；不重新产生墙钟提速成绩。"""
import argparse,ctypes as ct,fcntl,hashlib,os,struct,zipfile
from pathlib import Path
from skylake_server_support import ROOT,read,save,digest,checked,topology,environment,driver_bind,loaded
from verify_skylake_linux_stdlib import bind,create
from pinned_openmp_support import places,probe,state
from paged_table_support import direct_info,paged_info
from probe_skylake_pmu import Attr
NAMES=['cycles','instructions','cache_references','cache_misses']
class Group:
    def __init__(self,tid):
        self.fds=[];self.tid=tid;libc=ct.CDLL(None,use_errno=True);call=libc.syscall;call.restype=ct.c_long;call.argtypes=[ct.c_long,ct.c_void_p,ct.c_int,ct.c_int,ct.c_int,ct.c_ulong]
        try:
            for config in range(4):
                attr=Attr();attr.size=ct.sizeof(attr);attr.config=config;attr.read_format=11;attr.flags=32|64|(1 if not self.fds else 0)
                fd=call(298,ct.byref(attr),tid,-1,self.fds[0] if self.fds else -1,8)
                if fd<0:raise OSError(ct.get_errno(),'perf_event_open本线程组失败')
                self.fds.append(fd)
        except BaseException:self.close();raise
    def enable(self):fcntl.ioctl(self.fds[0],0x2403,1);fcntl.ioctl(self.fds[0],0x2400,1)
    def disable(self):fcntl.ioctl(self.fds[0],0x2401,1)
    def read(self):
        raw=os.read(self.fds[0],4096);data=struct.unpack('<'+'Q'*(len(raw)//8),raw);assert len(data)==7 and data[0]==4
        return {'tid':self.tid,'time_enabled_ns':data[1],'time_running_ns':data[2],'running_fraction':data[2]/data[1] if data[1] else None,'counts':dict(zip(NAMES,data[3:]))}
    def close(self):
        for fd in self.fds:os.close(fd)
        self.fds=[]
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--policy',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('不得覆盖计数画像')
    assert os.environ.get('JSHC_CHANNEL_FORCE_LINEAR_INDEX') is None,'画像要求默认可选分块路径'
    policy=read(a.policy);cpus=policy['cpus'];os.sched_setaffinity(0,cpus);top=topology(cpus)
    os.environ.update(OMP_NUM_THREADS='1',OMP_DYNAMIC='FALSE',OMP_PROC_BIND='TRUE',OMP_PLACES=places(cpus));os.environ.pop('GOMP_CPU_AFFINITY',None)
    assert read(checked(policy['probe']))['available']
    checked(policy['script']);checked(policy['pinning_probe']);plan=read(checked(policy['models_plan']))
    models=[checked(plan['fixed_inputs']['base']),*[checked(x) for x in plan['suffix_models']]];sides=[checked(plan['fixed_inputs']['sidecar']),None,None,None]
    source_bytes=checked(policy['photos']).read_bytes();assert len(source_bytes)==235929600
    source=(ct.c_uint8*len(source_bytes)).from_buffer_copy(source_bytes);del source_bytes;n=len(source);pixels=n//3
    guard=ct.create_string_buffer(n+32);ct.memset(guard,0xa7,len(guard));work=ct.cast(ct.addressof(guard)+16,ct.POINTER(ct.c_uint8));src=ct.cast(source,ct.POINTER(ct.c_uint8))
    def output_sha():
        assert bytes(guard[:16])==bytes([0xa7])*16 and bytes(guard[n+16:n+32])==bytes([0xa7])*16
        return hashlib.sha256(memoryview(guard).cast('B')[16:n+16]).hexdigest()
    libraries={};sources={k:digest(ROOT/k) for k in policy['python_sources']}
    for label,spec in policy['cases'].items():
        build=read(checked(spec['build']));full=read(checked(spec['full']));caseplan=read(checked(spec['plan']))
        assert full['pass'] and full['build_sha256']==spec['build']['sha256'] and full['libraries'][spec['build_role']]==spec['library']
        assert build['plan_sha256']==spec['plan']['sha256']
        for name,sha in caseplan['source_sha256'].items():assert digest(ROOT/name)==sha,name;sources[name]=sha
        d=bind(checked(spec['library']));assert d.jshc_cc_revision()==spec['revision'] and d.jshc_cc_capabilities()==7 and d.jshc_cc_abi_version()==1;libraries[label]=d
    sources[a.policy.resolve().relative_to(ROOT).as_posix()]=digest(a.policy)
    a.output.mkdir(parents=True);save(a.output/'run.json',{'purpose':__doc__,'policy':policy,'source_sha256':sources,'environment':environment(cpus),'topology_before_openmp':top,'wallclock_timing':False})
    with zipfile.ZipFile(a.output/'measured-source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in sorted(sources):z.write(ROOT/name,name)
    driver=driver_bind(checked(policy['driver']));initial=probe(driver,4,cpus);records=[];error=ct.create_string_buffer(1024)
    for config in policy['orders']:
        threads=config['threads']
        for label in config['variants']:
            d=libraries[label];handle=create(d,models,sides);groups=[]
            try:
                team=probe(driver,threads,cpus);ds=direct_info(d,handle);pages=paged_info(d,handle)
                if label=='clangload55':assert ds['format']==9
                if label!='reference23':assert ds['enabled']==1 and pages['fully_huge'] and pages['bytes']==2**24
                ct.memmove(work,src,n)
                if d.jshc_cc_apply(handle,work,n,1,threads,error,len(error)):raise RuntimeError(error.value.decode())
                assert output_sha()==policy['expected_output_sha256']
                ct.memmove(work,src,n)
                tasks=state(cpus);chosen=[r for r in tasks if r['allowed_cpus'][0] in cpus[:threads]]
                assert len(chosen)==threads
                for task in chosen:groups.append(Group(task['tid']))
                for group in groups:group.enable()
                status=d.jshc_cc_apply(handle,work,n,1,threads,error,len(error))
                for group in groups:group.disable()
                counters=[group.read() for group in groups]
                if status:raise RuntimeError(error.value.decode())
                assert output_sha()==policy['expected_output_sha256'];tasks_after=state(cpus)
                sums={name:sum(r['counts'][name] for r in counters) for name in NAMES}
                record={'variant':label,'revision':d.jshc_cc_revision(),'requested_threads':threads,'actual_team':team,'tasks_before':tasks,'tasks_after':tasks_after,'thread_counters':counters,'sum_counts':sums,'cycles_per_pixel':sums['cycles']/pixels,'instructions_per_pixel':sums['instructions']/pixels,'ipc':sums['instructions']/sums['cycles'],'generic_cache_references_per_pixel':sums['cache_references']/pixels,'generic_cache_misses_per_pixel':sums['cache_misses']/pixels,'generic_cache_miss_fraction':sums['cache_misses']/sums['cache_references'] if sums['cache_references'] else None,'multiplexing_acceptable':all(r['running_fraction'] is not None and r['running_fraction']>=0.99 for r in counters),'output_sha256':output_sha(),'model_bytes':d.jshc_cc_model_bytes(handle),'direct_info':ds,'paged_info':pages}
                records.append(record);save(a.output/f"sample-{threads}-{label}.json",record);print('完成用户态计数',threads,label,record['cycles_per_pixel'],record['instructions_per_pixel'],flush=True)
            finally:
                for group in groups:group.close()
                d.jshc_cc_destroy(handle)
    assert len(records)==4 and hashlib.sha256(source).hexdigest()==policy['photos']['sha256']
    for name,sha in sources.items():assert digest(ROOT/name)==sha,name
    save(a.output/'results.json',{'profile_completed':True,'purpose':__doc__,'records':records,'initial_team':initial,'loaded_libraries':loaded([*[x['library'] for x in policy['cases'].values()],policy['driver']]),'candidate_warmup_calls':4,'candidate_counted_calls':4,'candidate_wallclock_timing_calls':0,'limitation':'一次探索计数，不替代四进程性能；泛化cache事件不保证对应特定缓存级，周期受频率影响；包括少量启停/ct调用开销，四线程结束后存在短暂自旋计数，不改变任何安全设置'})
if __name__=='__main__':main()
