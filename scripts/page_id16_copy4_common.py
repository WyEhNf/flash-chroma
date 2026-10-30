"""P4 copy4独立绑定：所有C99质量调用明确进入新符号，旧prepare/40B ABI不变。"""
import ctypes as ct
from pathlib import Path
from page_id16_common import ROOT,PageModel,Borrowed,sha,save,env,API,query,snapshot,U8
from page_id16_common import library as original_library
from study_memory_rom import read
PLAN=ROOT/'experiments/page-id16-copy4-runtime-v1.json'

def checked_plan():
    plan=read(PLAN)
    if any(sha(ROOT/name)!=value for name,value in plan['source_sha256'].items()) or any(sha(name)!=value for name,value in plan['input_sha256'].items()):raise AssertionError('copy4冻结源/输入改变')
    return plan

def library(path,parallel):
    value=original_library(path,False)
    value.jshc_p4_apply_copy4.argtypes=[ct.POINTER(PageModel),U8,U8,ct.c_size_t]
    old_address=int(ct.cast(value.jshc_p4_apply,ct.c_void_p).value)
    new_address=int(ct.cast(value.jshc_p4_apply_copy4,ct.c_void_p).value)
    if old_address==new_address:raise AssertionError('新入口不能与旧apply地址相同')
    receipt=dict(library=str(Path(path).resolve()),library_sha256=sha(path),old_apply_address=old_address,new_apply_address=new_address,new_apply_symbol='jshc_p4_apply_copy4',calls={'core':0,'omp_c99':0,'omp_avx':0},scope='Python绑定处入口调用数，含拒绝调用；明确调用新符号，不是native retired像素或指令计数器。')
    if parallel:
        value.jshc_p4_apply_copy4_parallel.argtypes=[ct.POINTER(PageModel),U8,U8,ct.c_size_t,ct.c_int,ct.c_int]
        receipt['parallel_symbol']='jshc_p4_apply_copy4_parallel'
        receipt['parallel_address']=int(ct.cast(value.jshc_p4_apply_copy4_parallel,ct.c_void_p).value)
    value.copy4_receipt=receipt
    return value

def call(value,model,source,target,pixels,kernel=None,threads=1):
    src=ct.cast(source,U8)
    dst=ct.cast(target,U8)
    label='core' if kernel is None else 'omp_c99' if kernel==0 else 'omp_avx'
    value.copy4_receipt['calls'][label]+=1
    return value.jshc_p4_apply_copy4(ct.byref(model),src,dst,pixels) if kernel is None else value.jshc_p4_apply_copy4_parallel(ct.byref(model),src,dst,pixels,kernel,threads)
