"""修订24的只读直表诊断和真实载荷容量，不在计时区调用。"""
import ctypes as ct
import numpy as np
from exception_support import storage as old_storage

class DirectInfo(ct.Structure):
    _fields_=[(n,ct.c_uint32) for n in ('version','enabled','format','reserved')]+[(n,ct.c_uint64) for n in ('entries','table_capacity_bytes')]+[(n,ct.c_int32) for n in ('dg_min','db_min')]

def info(chain):
    d=chain.library.dll
    if not hasattr(d,'jshc_cc_get_direct_info'):return None
    f=d.jshc_cc_get_direct_info;f.argtypes=[ct.c_void_p,ct.POINTER(DirectInfo),ct.c_size_t];f.restype=ct.c_int
    value=DirectInfo()
    if f(chain.handle,ct.byref(value),ct.sizeof(value)) or value.version!=1:raise ValueError('直表诊断ABI不同')
    return {n:getattr(value,n) for n,_ in value._fields_}

def table(chain):
    state=info(chain)
    if state is None:raise ValueError('没有直表诊断')
    result=np.empty(state['entries'],np.uint32)
    f=chain.library.dll.jshc_cc_copy_direct;f.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint32),ct.c_size_t];f.restype=ct.c_int
    if f(chain.handle,result.ctypes.data_as(ct.POINTER(ct.c_uint32)),len(result)):raise ValueError('直表快照失败')
    return result

def storage(chain):
    state=info(chain)
    return old_storage(chain)+(state['table_capacity_bytes'] if state else 0)
