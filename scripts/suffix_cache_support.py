"""精确后缀缓存的只读诊断与覆盖统计；不参与映射、不进入计时热循环。"""
from __future__ import annotations
import ctypes as ct
import numpy as np


class CacheInfo(ct.Structure):
    _fields_ = [(name, ct.c_uint32) for name in ('version', 'enabled', 'reason', 'reserved')]
    _fields_ += [(name, ct.c_uint64) for name in ('entries', 'valid_entries', 'table_capacity_bytes', 'temporary_capacity_bytes')]
    _fields_ += [('prepare_seconds', ct.c_double)]
    _fields_ += [(name, ct.c_int32) for name in ('r_min', 'r_max', 'dg_min', 'dg_max', 'db_min', 'db_max')]


def bind(chain):
    d = chain.library.dll
    if not hasattr(d, 'jshc_cc_get_cache_info'):
        return None
    d.jshc_cc_get_cache_info.argtypes = [ct.c_void_p, ct.POINTER(CacheInfo), ct.c_size_t]
    d.jshc_cc_get_cache_info.restype = ct.c_int
    d.jshc_cc_copy_cache.argtypes = [ct.c_void_p, ct.POINTER(ct.c_uint32), ct.c_size_t]
    d.jshc_cc_copy_cache.restype = ct.c_int
    return d


def cache_info(chain):
    chain._check(); d = bind(chain)
    if d is None:
        return None
    info = CacheInfo()
    if d.jshc_cc_get_cache_info(chain.handle, ct.byref(info), ct.sizeof(info)) or info.version != 1:
        raise ValueError('缓存诊断ABI不符')
    return {name: getattr(info, name) for name, _ in info._fields_}


def cache_table(chain, info):
    chain._check(); d = bind(chain)
    array = np.empty(info['entries'], dtype=np.uint32)
    if d.jshc_cc_copy_cache(chain.handle, array.ctypes.data_as(ct.POINTER(ct.c_uint32)), array.size):
        raise ValueError('缓存只读快照失败')
    return array


def hit_mask(rgb, info):
    x = np.asarray(rgb, dtype=np.int32).reshape(-1, 3)
    r = x[:, 0]; dg = x[:, 1]-r; db = x[:, 2]-r
    return ((r >= info['r_min']) & (r <= info['r_max']) & (dg >= info['dg_min'])
            & (dg <= info['dg_max']) & (db >= info['db_min']) & (db <= info['db_max']))


def coverage(rgb, info):
    hits = hit_mask(rgb, info)
    packets = hits[:len(hits)//8*8].reshape(-1, 8).all(axis=1)
    return {'pixels': len(hits), 'pixel_hits': int(hits.sum()),
            'packets': len(packets), 'all_hit_packets': int(packets.sum())}
