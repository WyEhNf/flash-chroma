"""可逆后缀编码的只读元数据与真实u32词；诊断在计时区间之外，旧库返回None。"""
from __future__ import annotations
import ctypes as ct
import numpy as np


class EncodingInfo(ct.Structure):
    _fields_=[(n,ct.c_uint32) for n in ('version','format','reason','reserved')]
    _fields_ += [(n,ct.c_int32) for n in ('out_dg_base','out_db_base')]
    _fields_ += [(n,ct.c_uint64) for n in ('logical_entries','storage_words','capacity_bytes','raw_capacity_bytes','peak_payload_capacity_bytes')]


def bind(chain):
    chain._check();d=chain.library.dll
    if not hasattr(d,'jshc_cc_get_cache_encoding'):return None
    d.jshc_cc_get_cache_encoding.argtypes=[ct.c_void_p,ct.POINTER(EncodingInfo),ct.c_size_t];d.jshc_cc_get_cache_encoding.restype=ct.c_int
    d.jshc_cc_copy_cache_words.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint32),ct.c_size_t];d.jshc_cc_copy_cache_words.restype=ct.c_int
    return d


def info(chain):
    d=bind(chain)
    if d is None:return None
    x=EncodingInfo()
    if ct.sizeof(x)!=64 or d.jshc_cc_get_cache_encoding(chain.handle,ct.byref(x),ct.sizeof(x)) or x.version!=1 or x.format not in (0,1) or x.reserved:
        raise ValueError('编码诊断ABI或格式不同')
    expected=(x.logical_entries+1)//2 if x.format else x.logical_entries
    if x.storage_words!=expected or x.capacity_bytes<x.storage_words*4 or x.capacity_bytes>1048576:
        raise ValueError('编码容量/词数与格式不符')
    return {n:getattr(x,n) for n,_ in x._fields_}


def words(chain,record=None):
    d=bind(chain);record=info(chain) if record is None else record
    if d is None or record is None:raise ValueError('缺少编码词诊断')
    values=np.empty(record['storage_words'],dtype=np.uint32)
    if d.jshc_cc_copy_cache_words(chain.handle,values.ctypes.data_as(ct.POINTER(ct.c_uint32)),len(values)):
        raise ValueError('真实编码词复制失败')
    return values
