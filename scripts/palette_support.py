"""调色板研究只读诊断，不进入正式映射计时区间。"""
import ctypes as ct
import numpy as np

class PaletteInfo(ct.Structure):
    _fields_=[(n,ct.c_uint32) for n in ('version','enabled','palette_size','reason')]
    _fields_ += [(n,ct.c_uint64) for n in ('blocks','fast_blocks','table_capacity_bytes','temporary_peak_bytes')]
    _fields_ += [('prepare_seconds',ct.c_double)]

def info(chain):
    d=chain.library.dll
    if not hasattr(d,'jshc_cc_get_palette_info'):return None
    f=d.jshc_cc_get_palette_info;f.argtypes=[ct.c_void_p,ct.POINTER(PaletteInfo),ct.c_size_t];f.restype=ct.c_int
    value=PaletteInfo()
    if f(chain.handle,ct.byref(value),ct.sizeof(value)) or value.version!=1:raise ValueError('调色板诊断ABI不同')
    return {n:getattr(value,n) for n,_ in value._fields_}

def tables(chain):
    state=info(chain)
    if state is None:raise ValueError('本库没有调色板编码')
    words=np.empty(state['blocks'],np.uint32);palette=np.empty(256,np.uint32)
    f=chain.library.dll.jshc_cc_copy_palette
    f.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint32),ct.c_size_t,ct.POINTER(ct.c_uint32),ct.c_size_t];f.restype=ct.c_int
    if f(chain.handle,words.ctypes.data_as(ct.POINTER(ct.c_uint32)),words.size,palette.ctypes.data_as(ct.POINTER(ct.c_uint32)),palette.size):
        raise ValueError('编码表只读快照失败')
    return words,palette

def metadata_bytes(libraries,first,side):
    with libraries['reference'].chain([first],[side]) as ref,libraries['candidate'].chain([first],[side]) as cand:
        delta=cand.model_bytes-ref.model_bytes
        state=info(cand)
        if delta<=0 or state['enabled'] or state['table_capacity_bytes']:raise ValueError('元数据容量基准不符')
        return delta
