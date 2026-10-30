"""40单线程访存诊断：真实图原地、固定灰色原地、真实图分离输出各一次；不是重做候选验收。"""
import argparse,ctypes as ct,hashlib,os,zipfile
from pathlib import Path
from skylake_server_support import ROOT,read,save,digest,checked,environment,driver_bind
from verify_skylake_linux_stdlib import bind,create
from outplace_support import bind_to
from pinned_openmp_support import places,probe,state
from paged_table_support import direct_info,paged_info
from lookup_pmu_support import Group,EVENTS
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--policy',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('不得覆盖诊断')
    policy=read(a.policy);assert read(checked(policy['probe']))['available'];cpus=[0,2,4,6]
    assert policy['events']==[list(x) for x in EVENTS]
    for name,h in policy['source_hashes'].items():assert digest(ROOT/name)==h,name
    os.sched_setaffinity(0,cpus);os.environ.update(OMP_NUM_THREADS='1',OMP_DYNAMIC='FALSE',OMP_PROC_BIND='TRUE',OMP_PLACES=places(cpus));os.environ.pop('GOMP_CPU_AFFINITY',None)
    plan=read(checked(policy['plan']));build=read(checked(policy['build']));full=read(checked(policy['full']))
    assert full['pass'] and full['build_sha256']==policy['build']['sha256'] and build['plan_sha256']==policy['plan']['sha256']
    for name,h in plan['source_sha256'].items():assert digest(ROOT/name)==h,name
    d=bind(checked(build['libraries']['candidate']));assert d.jshc_cc_revision()==40
    to=bind_to(d);driver=driver_bind(checked(policy['driver']))
    raw=checked(policy['photos']).read_bytes();n=len(raw);assert n==235929600;pixels=n//3
    photo=(ct.c_uint8*n).from_buffer_copy(raw);del raw
    colour=bytes(policy['uniform_rgb']);raw=colour*pixels;uniform=(ct.c_uint8*n).from_buffer_copy(raw);del raw
    assert hashlib.sha256(uniform).hexdigest()==policy['uniform_source_sha256']
    storage=ct.create_string_buffer(n+128);base=ct.addressof(storage);addr=(base+63)&~63
    # 前后至少一个保护字节，统一64字节目标对齐，避免诊断混入前缀差异。
    if addr==base:addr+=64
    assert addr-base>=1 and addr+n<base+len(storage)
    target=ct.cast(addr,ct.POINTER(ct.c_uint8));error=ct.create_string_buffer(1024)
    models=[checked(plan['fixed_inputs']['base']),*[checked(x) for x in plan['suffix_models']]];sides=[checked(plan['fixed_inputs']['sidecar']),None,None,None]
    handle=create(d,models,sides);a.output.mkdir();records=[]
    sources={**plan['source_sha256'],**policy['source_hashes'],a.policy.resolve().relative_to(ROOT).as_posix():digest(a.policy)}
    save(a.output/'run.json',{'purpose':__doc__,'policy':policy,'source_sha256':sources,'environment':environment(cpus),'candidate_wallclock_timing_calls':0})
    with zipfile.ZipFile(a.output/'measured-source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in sorted(sources):z.write(ROOT/name,name)
    try:
        pages=paged_info(d,handle);info=direct_info(d,handle);assert info['format']==9 and pages['fully_huge'] and pages['bytes']==2**24
        for label in policy['order']:
            src=uniform if label=='uniform_inplace' else photo;expected=policy['uniform_output_sha256'] if label=='uniform_inplace' else policy['photo_output_sha256']
            team=probe(driver,1,cpus);assert team['actual']==1 and team['cpus']==[0]
            def reset():ct.memset(storage,0xa7,len(storage));ct.memmove(target,src,n)
            def call():
                if label=='photo_outplace':return to(handle,ct.cast(src,ct.POINTER(ct.c_uint8)),target,n,1,1,error,len(error))
                return d.jshc_cc_apply(handle,target,n,1,1,error,len(error))
            def check():
                offset=addr-base;view=memoryview(storage).cast('B')
                assert bytes(view[:offset])==bytes([0xa7])*offset and bytes(view[offset+n:])==bytes([0xa7])*(len(storage)-offset-n)
                assert hashlib.sha256(view[offset:offset+n]).hexdigest()==expected
            reset();assert call()==0,error.value;check();reset();before=state(cpus);g=Group()
            try:
                g.enable();status=call();g.disable();counters=g.read()
            finally:g.close()
            assert status==0,error.value;check();after=state(cpus)
            c=counters['counts'];assert c['cycles']>0 and 0<=c['oldest_load_not_complete']<=c['oldest_not_complete']<=c['cycles']
            record={'case':label,'team':team,'tasks_before':before,'tasks_after':after,'counters':counters,'per_pixel':{k:v/pixels for k,v in c.items()},'oldest_load_wait_cycle_fraction':c['oldest_load_not_complete']/c['cycles'],'oldest_pending_cycle_fraction':c['oldest_not_complete']/c['cycles'],'expected_output_sha256':expected,'paged_info':pages}
            records.append(record);save(a.output/(label+'.json'),record);print(label,record['per_pixel'],record['oldest_load_wait_cycle_fraction'],flush=True)
        assert hashlib.sha256(photo).hexdigest()==policy['photos']['sha256'] and hashlib.sha256(uniform).hexdigest()==policy['uniform_source_sha256']
        for name,h in sources.items():assert digest(ROOT/name)==h,name
        save(a.output/'results.json',{'pass':True,'purpose':__doc__,'records':records,'warmup_calls':3,'counted_calls':3,'wallclock_calls':0,'threefold_goal_completed':False,'limits':['单次不同工作负载诊断，不重新验收40或57，也不以它们的周期差代替整体吞吐','原始事件来自Linux v6.18的Zen4表；虚拟PMU事件语义未由宿主校准','等待最老load完成的周期比例不能直接推导平均延迟或未完成请求数量','固定灰色仅改变诊断输入，不增加图像内容特判或改变模型']})
    finally:d.jshc_cc_destroy(handle)
if __name__=='__main__':main()
