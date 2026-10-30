"""P4新40B投影ABI及原只读映射借用；不调用旧1056B prepare。"""
import ctypes as ct
import hashlib
import json
from pathlib import Path
from win_readonly_rom import FileView,API,query,snapshot,touch
from study_memory_rom import env,save,read,sha,U8
ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'experiments/page-id16-runtime-v1.json'
class PageModel(ct.Structure):
    _fields_=[('blob',ct.c_void_p),('blob_bytes',ct.c_size_t),('page_ids',ct.c_void_p),('pool',ct.c_void_p),('palette',ct.c_void_p)]
def checked_plan():
    plan=read(PLAN)
    if any(sha(ROOT/name)!=value for name,value in plan['source_sha256'].items()) or any(sha(name)!=value for name,value in plan['input_sha256'].items()):raise AssertionError('冻结源/原件改变')
    return plan
def library(path,parallel):
    d=ct.CDLL(str(path));d.jshc_p4_model_size.restype=ct.c_size_t
    if d.jshc_p4_model_size()!=ct.sizeof(PageModel):raise AssertionError('真实PageModel ABI与ctypes不同')
    d.jshc_p4_prepare.argtypes=[ct.POINTER(PageModel),ct.c_void_p,ct.c_size_t];d.jshc_p4_apply.argtypes=[ct.POINTER(PageModel),U8,U8,ct.c_size_t]
    if parallel:d.jshc_p4_apply_parallel.argtypes=[ct.POINTER(PageModel),U8,U8,ct.c_size_t,ct.c_int,ct.c_int]
    return d
class Borrowed:
    def __init__(self,path,d):
        self.view=FileView(path,'readonly');self.model=PageModel();self.view.models.append(self.model)
        try:
            if d.jshc_p4_prepare(ct.byref(self.model),self.view.address,self.view.length):raise ValueError('新P4 prepare拒绝')
        except BaseException:
            self.view.close();raise
    def close(self):self.view.close()
    def __enter__(self):return self
    def __exit__(self,*unused):self.close()
def call(d,m,source,target,n,kernel=None,threads=1):
    src=ct.cast(source,U8);dst=ct.cast(target,U8)
    return d.jshc_p4_apply(ct.byref(m),src,dst,n) if kernel is None else d.jshc_p4_apply_parallel(ct.byref(m),src,dst,n,kernel,threads)
