"""本机Zen4用户态原始计数器；仅诊断，不输出性能验收结论。"""
import ctypes as ct,fcntl,os,struct
from probe_skylake_pmu import Attr
EVENTS=[('cycles',0x76),('instructions',0xc0),('l2_request_misses',0x0964),
        ('oldest_not_complete',0x02d6),('oldest_load_not_complete',0xa2d6),('load_dispatch',0x0129)]
class Group:
    def __init__(self):
        self.fds=[];libc=ct.CDLL(None,use_errno=True);call=libc.syscall;call.restype=ct.c_long
        call.argtypes=[ct.c_long,ct.c_void_p,ct.c_int,ct.c_int,ct.c_int,ct.c_ulong]
        try:
            for name,config in EVENTS:
                attr=Attr();attr.type=4;attr.size=ct.sizeof(attr);attr.config=config;attr.read_format=11
                attr.flags=32|64|(5 if not self.fds else 0)
                fd=call(298,ct.byref(attr),0,-1,self.fds[0] if self.fds else -1,8)
                if fd<0:raise OSError(ct.get_errno(),'原始计数器不可用：'+name)
                self.fds.append(fd)
        except BaseException:self.close();raise
    def enable(self):fcntl.ioctl(self.fds[0],0x2403,1);fcntl.ioctl(self.fds[0],0x2400,1)
    def disable(self):fcntl.ioctl(self.fds[0],0x2401,1)
    def read(self):
        raw=os.read(self.fds[0],4096);values=struct.unpack('<'+'Q'*(len(raw)//8),raw)
        if len(values)!=9 or values[0]!=6:raise RuntimeError('六事件组未同时调度')
        result={'time_enabled_ns':values[1],'time_running_ns':values[2],'counts':dict(zip([x[0] for x in EVENTS],values[3:]))}
        result['running_fraction']=values[2]/values[1] if values[1] else 0
        if result['running_fraction']<.99:raise RuntimeError('六事件组运行比例不足99%')
        return result
    def close(self):
        for fd in self.fds:os.close(fd)
        self.fds=[]
