"""探测Zen4六事件组可读性，不执行候选像素或改变系统设置。"""
import argparse,json,os,platform
from pathlib import Path
from lookup_pmu_support import Group,EVENTS
from skylake_server_support import save,digest
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    assert not a.output.exists();os.sched_setaffinity(0,{0})
    result={'purpose':__doc__,'events':EVENTS,'platform':platform.platform(),'cpuinfo':Path('/proc/cpuinfo').read_text(),'available':False,'candidate_pixel_calls':0,'candidate_timing_calls':0,'source_sha256':{__file__:digest(__file__),str(Path(__file__).with_name('lookup_pmu_support.py')):digest(Path(__file__).with_name('lookup_pmu_support.py'))}}
    g=None
    try:
        assert 'cpu family\t: 25' in result['cpuinfo'] and 'model\t\t: 97' in result['cpuinfo']
        g=Group();g.enable();value=sum(range(200000));g.disable();result['probe']=g.read();assert value==19999900000
        result['available']=result['probe']['counts']['cycles']>0 and result['probe']['counts']['instructions']>0
    except BaseException as e:result['failure']=repr(e)
    finally:
        if g:g.close()
    a.output.parent.mkdir(parents=True,exist_ok=True);save(a.output,result);print({'available':result['available'],'probe':result.get('probe'),'failure':result.get('failure')})
if __name__=='__main__':main()
