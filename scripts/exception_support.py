"""精确例外池的只读诊断与真实容量；不进入像素计时。"""
import ctypes as ct
import numpy as np
from palette_support import info as palette_info


class ExceptionInfo(ct.Structure):
    _fields_ = [('version', ct.c_uint32), ('enabled', ct.c_uint32),
                ('entries', ct.c_uint64), ('table_capacity_bytes', ct.c_uint64)]


def info(chain):
    d = chain.library.dll
    if not hasattr(d, 'jshc_cc_get_exception_info'):
        return None
    f = d.jshc_cc_get_exception_info
    f.argtypes = [ct.c_void_p, ct.POINTER(ExceptionInfo), ct.c_size_t]; f.restype = ct.c_int
    value = ExceptionInfo()
    if f(chain.handle, ct.byref(value), ct.sizeof(value)) or value.version != 1:
        raise ValueError('例外池诊断ABI不符')
    return {n: getattr(value, n) for n, _ in value._fields_}


def table(chain):
    state = info(chain)
    if state is None:
        raise ValueError('此修订没有例外池')
    words = np.empty(state['entries'], np.uint32)
    f = chain.library.dll.jshc_cc_copy_exceptions
    f.argtypes = [ct.c_void_p, ct.POINTER(ct.c_uint32), ct.c_size_t]; f.restype = ct.c_int
    if f(chain.handle, words.ctypes.data_as(ct.POINTER(ct.c_uint32)), words.size):
        raise ValueError('例外池复制失败')
    return words


def storage(chain):
    p = palette_info(chain); e = info(chain)
    return (p['table_capacity_bytes'] if p else 0)+(e['table_capacity_bytes'] if e else 0)
