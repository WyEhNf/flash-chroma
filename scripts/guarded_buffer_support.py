"""Linux页保护验证精确缓冲区末端与源只读；失败将使验证进程直接失败。"""
import ctypes as ct,mmap
class GuardedBuffer:
    def __init__(self,source):
        self.libc=ct.CDLL(None,use_errno=True);self.libc.mmap.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_int,ct.c_int,ct.c_int,ct.c_size_t];self.libc.mmap.restype=ct.c_void_p
        self.libc.mprotect.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_int];self.libc.mprotect.restype=ct.c_int
        self.libc.munmap.argtypes=[ct.c_void_p,ct.c_size_t];self.libc.munmap.restype=ct.c_int
        self.n=len(source);self.page=mmap.PAGESIZE;self.valid=max(self.page,((self.n+self.page-1)//self.page)*self.page);self.size=self.valid+2*self.page
        self.base=self.libc.mmap(None,self.size,3,mmap.MAP_PRIVATE|mmap.MAP_ANONYMOUS,-1,0)
        if self.base==ct.c_void_p(-1).value:raise OSError(ct.get_errno(),'mmap失败')
        self.address=self.base+self.page+self.valid-self.n
        try:
            self._protect(self.base,self.page,0);self._protect(self.base+self.page+self.valid,self.page,0)
            if self.n:ct.memmove(self.address,source,self.n)
        except BaseException:self.close();raise
    def _protect(self,address,size,mode):
        if self.libc.mprotect(address,size,mode):raise OSError(ct.get_errno(),'mprotect失败')
    def readonly(self):self._protect(self.base+self.page,self.valid,1)
    def bytes(self):return ct.string_at(self.address,self.n)
    def close(self):
        if self.base:self.libc.munmap(self.base,self.size);self.base=None
def guarded_apply(d,handle,source,kernel,threads,same=False):
    from outplace_support import bind_to
    bind_to(d);src=GuardedBuffer(source);dst=None
    try:
        if same:target=src
        else:src.readonly();dst=GuardedBuffer(bytes(len(source)));target=dst
        error=ct.create_string_buffer(1024);u8=ct.POINTER(ct.c_uint8)
        if d.jshc_cc_apply_to(handle,ct.cast(src.address,u8),ct.cast(target.address,u8),len(source),kernel,threads,error,len(error)):raise RuntimeError(error.value.decode())
        actual=target.bytes()
        if not same and src.bytes()!=source:raise AssertionError('只读源改变')
        return actual
    finally:
        if dst:dst.close()
        src.close()
