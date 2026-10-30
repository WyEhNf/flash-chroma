"""准备期共享轴格式的可选只读诊断；不映射像素、不在计时热区调用。"""
from __future__ import annotations
import ctypes as ct


def formats(chain):
    chain._check(); d=chain.library.dll
    if not hasattr(d,'jshc_cc_get_axis_formats'):
        return None
    f=d.jshc_cc_get_axis_formats
    f.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint32),ct.c_size_t];f.restype=ct.c_int
    values=(ct.c_uint32*len(chain.models))()
    if f(chain.handle,values,len(values)) or any(x not in (0,1) for x in values):
        raise ValueError('共享轴预计算只读诊断失败')
    return list(values)
