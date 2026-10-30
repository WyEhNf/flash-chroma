"""私有restrict候选的只读域诊断；默认摘要不含地址，不在计时热区调用。"""
from __future__ import annotations
import ctypes as ct


def bind(chain):
    chain._check();d=chain.library.dll
    if not hasattr(d,'jshc_cc_domain_count'):return None
    for name in ('jshc_cc_domain_count','jshc_cc_domain_capacity'):
        f=getattr(d,name);f.argtypes=[ct.c_void_p];f.restype=ct.c_size_t
    d.jshc_cc_copy_domains.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint64),ct.c_size_t];d.jshc_cc_copy_domains.restype=ct.c_int
    d.jshc_cc_view_regions.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint64),ct.c_size_t];d.jshc_cc_view_regions.restype=ct.c_size_t
    d.jshc_cc_check_domain_range.argtypes=[ct.c_void_p,ct.c_uint64,ct.c_uint64];d.jshc_cc_check_domain_range.restype=ct.c_int
    return d


def info(chain):
    d=bind(chain)
    if d is None:return None
    count=d.jshc_cc_domain_count(chain.handle);capacity=d.jshc_cc_domain_capacity(chain.handle)
    if not 0<count<=capacity<=64 or capacity<6+7*len(chain.models):raise ValueError('读取域诊断容量无效')
    return {'domain_count':count,'domain_capacity':capacity,'domain_storage_bytes':capacity*16,'extra_model_bytes':24+capacity*16}


def regions(chain,views=False):
    d=bind(chain)
    if d is None:raise ValueError('缺少读取域诊断')
    count=d.jshc_cc_view_regions(chain.handle,None,0) if views else d.jshc_cc_domain_count(chain.handle)
    if not 0<count<=64:raise ValueError('读取区数量无效')
    values=(ct.c_uint64*(count*2))()
    result=d.jshc_cc_view_regions(chain.handle,values,count) if views else d.jshc_cc_copy_domains(chain.handle,values,count)
    if result!=(count if views else 0):raise ValueError('读取区复制失败')
    return [(values[2*i],values[2*i+1]) for i in range(count)]
