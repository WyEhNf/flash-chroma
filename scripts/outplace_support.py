"""标准库核验真实分离输入/输出API、源只读、同址及部分重叠拒绝。"""
import ctypes as ct

def bind_to(d):
    f=d.jshc_cc_apply_to
    f.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint8),ct.POINTER(ct.c_uint8),ct.c_size_t,ct.c_int,ct.c_int,ct.POINTER(ct.c_char),ct.c_size_t];f.restype=ct.c_int
    return f

def apply_to(d,h,source,kernel,threads,source_offset=0,target_offset=0,same=False):
    f=bind_to(d);n=len(source);s=(ct.c_uint8*(n+source_offset+17))();ct.memset(s,0xa7,len(s))
    p=ct.addressof(s)+source_offset;ct.memmove(p,source,n);before=bytes(s)
    if same:t=s;q=p;target_offset=source_offset;sentinel=0xa7
    else:
        t=(ct.c_uint8*(n+target_offset+17))();ct.memset(t,0x59,len(t));q=ct.addressof(t)+target_offset;sentinel=0x59
    error=ct.create_string_buffer(1024)
    if f(h,ct.cast(p,ct.POINTER(ct.c_uint8)),ct.cast(q,ct.POINTER(ct.c_uint8)),n,kernel,threads,error,len(error)):
        raise RuntimeError(error.value.decode('utf-8','replace'))
    if not same and bytes(s)!=before:raise AssertionError('分离输入被改写')
    if bytes(t[:target_offset])!=bytes([sentinel])*target_offset or bytes(t[target_offset+n:])!=bytes([sentinel])*17:raise AssertionError('输出越界')
    return ct.string_at(q,n)

def reject_to(d,h):
    f=bind_to(d);s=(ct.c_uint8*64)(*([0xa7]*64));t=(ct.c_uint8*64)(*([0x59]*64));before=(bytes(s),bytes(t));error=ct.create_string_buffer(1024)
    p=ct.cast(s,ct.POINTER(ct.c_uint8));q=ct.cast(t,ct.POINTER(ct.c_uint8));maxp=(1<<(ct.sizeof(ct.c_void_p)*8))-1
    cases=[(None,p,q,3,1,1),(h,None,q,3,1,1),(h,p,None,3,1,1),(h,p,q,1,1,1),
        (h,p,q,3,-1,1),(h,p,q,3,1,0),(h,p,q,3,1,257),
        (h,ct.cast(maxp-2,ct.POINTER(ct.c_uint8)),q,6,1,1),(h,p,ct.cast(maxp-2,ct.POINTER(ct.c_uint8)),6,1,1),
        (h,p,ct.cast(ct.addressof(s)+1,ct.POINTER(ct.c_uint8)),6,1,1),(h,ct.cast(ct.addressof(s)+1,ct.POINTER(ct.c_uint8)),p,6,1,1)]
    for handle,source,target,n,kernel,threads in cases:
        if f(handle,source,target,n,kernel,threads,error,len(error))!=1 or (bytes(s),bytes(t))!=before:raise AssertionError('无效分离范围未拒绝或改写')
    if f(h,None,None,0,1,1,error,len(error))!=0:raise AssertionError('合法空输入被拒绝')
    return len(cases)
