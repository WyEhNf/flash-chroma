"""完整输入域证明的48字节只读诊断，旧库返回None；不在计时区间内调用。"""
import ctypes as ct
import hashlib
import numpy as np


class DomainInfo(ct.Structure):
    _fields_=[(n,ct.c_uint32) for n in ('version','eligible','cache_enabled','reserved')]
    _fields_ += [(n,ct.c_uint64) for n in ('reachable_cells','unproven_cells')]
    _fields_ += [(n,ct.c_int32) for n in ('dg_min','dg_max','db_min','db_max')]


def info(chain):
    chain._check();d=chain.library.dll
    if not hasattr(d,'jshc_cc_get_domain_info'):return None
    f=d.jshc_cc_get_domain_info;f.argtypes=[ct.c_void_p,ct.POINTER(DomainInfo),ct.c_size_t];f.restype=ct.c_int
    result=DomainInfo()
    if ct.sizeof(result)!=48 or f(chain.handle,ct.byref(result),ct.sizeof(result)) or result.version!=1 or result.reserved:
        raise ValueError('完整域证明诊断ABI不同')
    if result.eligible and (not result.cache_enabled or result.unproven_cells or not result.reachable_cells):
        raise ValueError('完整域证明诊断自相矛盾')
    record={n:getattr(result,n) for n,_ in result._fields_}
    if hasattr(d,'jshc_cc_domain_fast_enabled'):
        d.jshc_cc_domain_fast_enabled.argtypes=[ct.c_void_p];d.jshc_cc_domain_fast_enabled.restype=ct.c_uint32
        record['fast_path_enabled']=int(d.jshc_cc_domain_fast_enabled(chain.handle))
    return record


def checked_bench(chain,source,*,threads,repeats,expected_sha256):
    chain._check()
    if not source.flags.c_contiguous or source.dtype!=np.uint8 or repeats!=5:
        raise ValueError('逐轮核对基准需要连续RGB8和固定5轮')
    work=np.empty_like(source);apply=[];total=[];hashes=[];error=ct.create_string_buffer(1024)
    pointer=ct.POINTER(ct.c_uint8)
    for index in range(repeats):
        a=ct.c_double();b=ct.c_double()
        code=chain.library.dll.jshc_cc_bench(chain.handle,source.ctypes.data_as(pointer),work.ctypes.data_as(pointer),
            source.nbytes,1,threads,1,ct.byref(a),ct.byref(b),error,len(error))
        if code:raise RuntimeError('逐轮原生基准失败：'+error.value.decode('utf-8','replace'))
        # 哈希在原生apply/copy计时区间之外；轮间读取工作区是此新协议的一部分。
        output_sha=hashlib.sha256(memoryview(work).cast('B')).hexdigest()
        if output_sha!=expected_sha256:raise AssertionError('第'+str(index)+'轮完整100图SHA不同')
        apply.append(a.value);total.append(b.value);hashes.append(output_sha)
    return {'apply_seconds':apply,'copy_apply_seconds':total,'per_round_output_sha256':hashes,
            'round_protocol':'每次CABI repeats=1，计时外核对完整100图SHA后再进行下一轮；不与旧内部5轮绝对耗时混用'}
