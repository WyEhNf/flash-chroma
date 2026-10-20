"""只探测本进程用户态硬件计数器是否可读，不修改perf权限或系统设置，不执行候选映射。"""
import argparse,ctypes as ct,fcntl,os,platform,struct
from pathlib import Path
from skylake_server_support import save,digest
class Attr(ct.Structure):
    _fields_=[('type',ct.c_uint32),('size',ct.c_uint32)]+[(n,ct.c_uint64) for n in ('config','sample_period','sample_type','read_format','flags')]+[('wakeup',ct.c_uint32),('bp_type',ct.c_uint32)]+[(n,ct.c_uint64) for n in ('config1','config2','branch_sample_type','sample_regs_user')]+[('sample_stack_user',ct.c_uint32),('clockid',ct.c_int32),('sample_regs_intr',ct.c_uint64),('aux_watermark',ct.c_uint32),('sample_max_stack',ct.c_uint16),('reserved2',ct.c_uint16),('aux_sample_size',ct.c_uint32),('reserved3',ct.c_uint32),('sig_data',ct.c_uint64)]
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('不得覆盖探测')
    assert platform.system()=='Linux' and platform.machine()=='x86_64' and ct.sizeof(Attr)==128
    libc=ct.CDLL(None,use_errno=True);call=libc.syscall;call.restype=ct.c_long;call.argtypes=[ct.c_long,ct.c_void_p,ct.c_int,ct.c_int,ct.c_int,ct.c_ulong]
    names=['cycles','instructions','cache_references','cache_misses'];fds=[];failure=None;values=None
    try:
        for config,name in enumerate(names):
            attr=Attr();attr.size=128;attr.config=config;attr.read_format=11;attr.flags=32|64|(1 if not fds else 0)
            fd=call(298,ct.byref(attr),0,-1,fds[0] if fds else -1,8)
            if fd<0:failure={'event':name,'errno':ct.get_errno(),'error':os.strerror(ct.get_errno())};break
            fds.append(fd)
        if not failure:
            fcntl.ioctl(fds[0],0x2403,1);fcntl.ioctl(fds[0],0x2400,1)
            total=sum(range(20000))
            fcntl.ioctl(fds[0],0x2401,1);raw=os.read(fds[0],4096);data=struct.unpack('<'+'Q'*(len(raw)//8),raw)
            assert data[0]==4 and len(data)==7
            values={'time_enabled_ns':data[1],'time_running_ns':data[2],'python_probe_counts':dict(zip(names,data[3:])),'check_value':total}
    finally:
        for fd in fds:os.close(fd)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    result={'available':failure is None,'purpose':__doc__,'failure':failure,'values':values,'perf_event_paranoid':Path('/proc/sys/kernel/perf_event_paranoid').read_text().strip(),'event_sources':sorted(p.name for p in Path('/sys/bus/event_source/devices').iterdir()),'script_sha256':digest(__file__),'candidate_pixel_calls':0,'candidate_timing_calls':0,'changes':'只打开本进程exclude_kernel/exclude_hv计数器并关闭，没有更改权限、缓解或设置'}
    save(a.output,result);print(result)
if __name__=='__main__':main()
