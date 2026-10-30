"""只读坐标内存布局诊断；不做映射或量化，不进入计时热循环。"""
from __future__ import annotations
import ctypes as ct


def bind(chain):
    d = chain.library.dll
    if not hasattr(d, 'jshc_cc_get_layouts'):
        return None
    d.jshc_cc_get_layouts.argtypes = [ct.c_void_p, ct.POINTER(ct.c_uint32), ct.c_size_t]
    d.jshc_cc_get_layouts.restype = ct.c_int
    return d


def layouts(chain):
    chain._check(); d = bind(chain)
    if d is None:
        return None
    flags = (ct.c_uint32*len(chain.models))()
    if d.jshc_cc_get_layouts(chain.handle, flags, len(flags)):
        raise ValueError('坐标内存布局诊断失败')
    if any(x not in (0, 1, 2) for x in flags):
        raise ValueError('未知坐标布局：0九表、1共享、2双差值')
    return list(flags)
