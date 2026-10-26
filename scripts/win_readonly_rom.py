"""Windows只读/COW文件视图所有者；保持已有M16D与计算库，显式管理借用生命周期。"""
import ctypes as ct
from pathlib import Path
from study_memory_rom import Model,U8,ROOT,sha,read,save,env
from bench_memory_rom import memory

PLAN=ROOT/'experiments/memory-rom-readonly-v1.json'
INVALID_HANDLE=(1<<(8*ct.sizeof(ct.c_void_p)))-1
class MBI(ct.Structure):
    _fields_=[('BaseAddress',ct.c_void_p),('AllocationBase',ct.c_void_p),('AllocationProtect',ct.c_uint32),('PartitionId',ct.c_uint16),('RegionSize',ct.c_size_t),('State',ct.c_uint32),('Protect',ct.c_uint32),('Type',ct.c_uint32)]
class Performance(ct.Structure):
    _fields_=[('cb',ct.c_uint32),*[(name,ct.c_size_t) for name in ('CommitTotal','CommitLimit','CommitPeak','PhysicalTotal','PhysicalAvailable','SystemCache','KernelTotal','KernelPaged','KernelNonpaged','PageSize')],('HandleCount',ct.c_uint32),('ProcessCount',ct.c_uint32),('ThreadCount',ct.c_uint32)]
class WinAPI:
    def __init__(self):
        k=ct.WinDLL('kernel32',use_last_error=True);p=ct.WinDLL('psapi',use_last_error=True)
        self.create_file=k.CreateFileW;self.create_file.argtypes=[ct.c_wchar_p,ct.c_uint32,ct.c_uint32,ct.c_void_p,ct.c_uint32,ct.c_uint32,ct.c_void_p];self.create_file.restype=ct.c_void_p
        self.size=k.GetFileSizeEx;self.size.argtypes=[ct.c_void_p,ct.POINTER(ct.c_int64)];self.size.restype=ct.c_int
        self.create_mapping=k.CreateFileMappingW;self.create_mapping.argtypes=[ct.c_void_p,ct.c_void_p,ct.c_uint32,ct.c_uint32,ct.c_uint32,ct.c_wchar_p];self.create_mapping.restype=ct.c_void_p
        self.map_view=k.MapViewOfFile;self.map_view.argtypes=[ct.c_void_p,ct.c_uint32,ct.c_uint32,ct.c_uint32,ct.c_size_t];self.map_view.restype=ct.c_void_p
        self.unmap=k.UnmapViewOfFile;self.unmap.argtypes=[ct.c_void_p];self.unmap.restype=ct.c_int
        self.close=k.CloseHandle;self.close.argtypes=[ct.c_void_p];self.close.restype=ct.c_int
        self.query=k.VirtualQuery;self.query.argtypes=[ct.c_void_p,ct.POINTER(MBI),ct.c_size_t];self.query.restype=ct.c_size_t
        self.process=k.GetCurrentProcess;self.process.restype=ct.c_void_p
        self.handles=k.GetProcessHandleCount;self.handles.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint32)];self.handles.restype=ct.c_int
        self.performance=p.GetPerformanceInfo;self.performance.argtypes=[ct.POINTER(Performance),ct.c_uint32];self.performance.restype=ct.c_int
API=WinAPI()
def query(address):
    value=MBI()
    if API.query(address,ct.byref(value),ct.sizeof(value))!=ct.sizeof(value):raise ct.WinError(ct.get_last_error())
    return {name:int(getattr(value,name) or 0) for name,_ in value._fields_}
def snapshot(address=None,length=0):
    result=memory();system=Performance();system.cb=ct.sizeof(system)
    if not API.performance(ct.byref(system),ct.sizeof(system)):raise ct.WinError(ct.get_last_error())
    handles=ct.c_uint32()
    if not API.handles(API.process(),ct.byref(handles)):raise ct.WinError(ct.get_last_error())
    result['process_handles']=handles.value
    result['system_commit_bytes']=system.CommitTotal*system.PageSize
    result['system_page_size']=system.PageSize
    if address:result['view']={'first':query(address),'last':query(address+length-1),'bytes':length,'address':address}
    return result
def touch(address,length):
    # 每页只读一个字节及末字节；不复制ROM，也不承诺冷页/速度结论。
    checksum=0
    for offset in range(0,length,4096):checksum=(checksum+ct.c_uint8.from_address(address+offset).value)&0xffffffff
    checksum=(checksum+ct.c_uint8.from_address(address+length-1).value)&0xffffffff
    return dict(page_stride=4096,reads=(length+4095)//4096+1,checksum=checksum)
class FileView:
    # 调用者不得在native apply尚未返回时close；本owner不提供并发锁。
    def __init__(self,path,mode,on_mapped=None,_api=None):
        if mode not in ('cow','readonly'):raise ValueError('固定COW或只读模式')
        self.api=_api or API;self.file=None;self.mapping=None;self._address=None;self.length=0;self.models=[];self.closed=False;self._closing=False;self.mode=mode
        try:
            self.file=self.api.create_file(str(Path(path).resolve()),0x80000000,1,None,3,0x80,None)
            if self.file in (None,INVALID_HANDLE):self.file=None;raise ct.WinError(ct.get_last_error())
            length=ct.c_int64()
            if not self.api.size(self.file,ct.byref(length)):raise ct.WinError(ct.get_last_error())
            if length.value<=0 or length.value>INVALID_HANDLE:raise ValueError('文件长度不在可映射范围')
            self.length=length.value
            self.mapping=self.api.create_mapping(self.file,None,8 if mode=='cow' else 2,0,0,None)
            if not self.mapping:raise ct.WinError(ct.get_last_error())
            self._address=self.api.map_view(self.mapping,1 if mode=='cow' else 4,0,0,self.length)
            if not self._address:raise ct.WinError(ct.get_last_error())
            if on_mapped:on_mapped(self._address,self.length)
        except BaseException as error:
            try:self.close()
            except OSError as cleanup:error.add_note('清理同时失败：'+str(cleanup))
            raise
    @property
    def address(self):
        if self.closed or self._closing or not self._address:raise RuntimeError('映射已关闭或正在清理')
        return self._address
    def prepare(self,library):
        model=Model();self.models.append(model)
        if library.jshc_mem_prepare(ct.byref(model),self.address,self.length):
            self.close();raise ValueError('原M16D格式被拒绝')
        return model
    def close(self):
        if self.closed:return
        self._closing=True
        # 先失效所有借用model；此后native验证也会拒绝零model。
        for model in self.models:ct.memset(ct.byref(model),0,ct.sizeof(model))
        failures=[]
        if self._address:
            if not self.api.unmap(self._address):failures.append(ct.get_last_error())
            else:self._address=None
        for name in ('mapping','file'):
            handle=getattr(self,name)
            if handle:
                if not self.api.close(handle):failures.append(ct.get_last_error())
                else:setattr(self,name,None)
        self.closed=not(self._address or self.mapping or self.file)
        if failures:raise ct.WinError(failures[0])
    def __enter__(self):return self
    def __exit__(self,*unused):self.close()
def library(path):
    value=ct.CDLL(str(path));value.jshc_mem_prepare.argtypes=[ct.POINTER(Model),ct.c_void_p,ct.c_size_t]
    value.jshc_mem_apply_parallel.argtypes=[ct.POINTER(Model),U8,U8,ct.c_size_t,ct.c_int,ct.c_int]
    value.jshc_mem_model_size.restype=ct.c_size_t
    if value.jshc_mem_model_size()!=ct.sizeof(Model) or ct.sizeof(Model)!=1056:raise AssertionError('原Clang线性model ABI不同')
    return value
def checked_plan():
    plan=read(PLAN)
    if any(sha(ROOT/name)!=value for name,value in plan['source_sha256'].items()) or any(sha(name)!=value for name,value in plan['input_sha256'].items()):raise AssertionError('冻结源/原件身份不同')
    return plan
def call(d,model,source,target,n,kernel,threads):return d.jshc_mem_apply_parallel(ct.byref(model),ct.cast(source,U8),ct.cast(target,U8),n,kernel,threads)
