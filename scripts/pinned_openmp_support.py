"""Linux显式OpenMP位置与每线程OS亲和性核对，不修改系统设置。"""
import os
from pathlib import Path
from skylake_server_support import team
def places(cpus):return ','.join('{'+str(c)+'}' for c in cpus)
def require_environment(cpus):
    if os.environ.get('OMP_PROC_BIND')!='TRUE' or os.environ.get('OMP_PLACES')!=places(cpus) or os.environ.get('OMP_DYNAMIC')!='FALSE':raise ValueError('显式OpenMP绑定环境不同')
def state(cpus):
    records=[]
    for path in sorted(Path('/proc/self/task').iterdir(),key=lambda p:int(p.name)):
        try:allowed=sorted(os.sched_getaffinity(int(path.name)))
        except ProcessLookupError:continue
        if len(allowed)!=1 or not set(allowed)<=set(cpus):raise ValueError('实际线程未固定到单个目标CPU')
        records.append({'tid':int(path.name),'allowed_cpus':allowed})
    if {r['allowed_cpus'][0] for r in records}!=set(cpus):raise ValueError('实际线程没有覆盖四个目标CPU')
    if sorted(os.sched_getaffinity(0))!=cpus[:1]:raise ValueError('主线程未固定到首个目标CPU')
    return records
def probe(driver,threads,cpus):
    require_environment(cpus);result=team(driver,threads,cpus)
    if result['cpus']!=cpus[:threads]:raise ValueError('实际OpenMP线程位置顺序不同')
    result['task_affinities']=state(cpus);return result
