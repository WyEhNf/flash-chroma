"""只验证OpenMP团队/绑定，不加载候选内核或运行性能计时。"""
import argparse,os,json
from pathlib import Path
from skylake_server_support import checked,driver_bind,topology,save,digest
from pinned_openmp_support import probe,places
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('不得覆盖旧绑定探测')
    cpus=[0,2,4,6];os.sched_setaffinity(0,cpus);top=topology(cpus)
    os.environ.update(OMP_NUM_THREADS='1',OMP_DYNAMIC='FALSE',OMP_PROC_BIND='TRUE',OMP_PLACES=places(cpus))
    os.environ.pop('GOMP_CPU_AFFINITY',None)
    spec={'path':'artifacts/skylake-domain-server-v2/artifacts/linux domain-v2/driver/libjshc_server_driver.so','sha256':'b9a37fa74a2b454a274a7a38c19a4e34546b495e288e549bbae5b6395c354b75'}
    driver=driver_bind(checked(spec));records=[probe(driver,t,cpus) for t in [4,1]*16]
    a.output.parent.mkdir(parents=True,exist_ok=True);save(a.output,{'pass':True,'purpose':__doc__,'probes':records,'topology_before_openmp':top,'driver':spec,'script_sha256':digest(__file__),'new_pixel_calls':0,'new_performance_calls':0})
    print('显式绑定32次团队探测通过')
if __name__=='__main__':main()
