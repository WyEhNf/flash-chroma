"""固定4KiB页别名/对齐控制的Windows所有者；导入不申请新API映射。"""
import ctypes as ct
import hashlib
from pathlib import Path
import struct
import time
from profile_page_alias import OwnerState
from win_readonly_rom import API as BASE,FileView,Model,U8,library,query,sha,read,save,env

PAGE=4096
PAGES=4096
MODEL_BYTES=16778272
DATA_SPAN=16781312
RESERVE_SPAN=16785408
INVALID=(1<<(8*ct.sizeof(ct.c_void_p)))-1
class AliasFailure(RuntimeError):
    def __init__(self,owner,cause,cleanup=None):
        super().__init__('页别名失败：'+str(cause));self.owner=owner;self.cause=cause;self.cleanup=cleanup
        if cleanup:self.add_note('回收同时失败，保留owner供显式重试：'+str(cleanup))
class NewAPI:
    def __init__(self,disabled=(),hook=None):
        self.hook=hook;self.functions={};self.missing=[];self.resolved={}
        modules=[ct.WinDLL(name,use_last_error=True) for name in ('kernelbase','kernel32')]
        definitions={'reserve':('VirtualAlloc2',[ct.c_void_p,ct.c_void_p,ct.c_size_t,ct.c_uint32,ct.c_uint32,ct.c_void_p,ct.c_uint32],ct.c_void_p),'map':('MapViewOfFile3',[ct.c_void_p,ct.c_void_p,ct.c_void_p,ct.c_uint64,ct.c_size_t,ct.c_uint32,ct.c_uint32,ct.c_void_p,ct.c_uint32],ct.c_void_p),'unmap':('UnmapViewOfFile2',[ct.c_void_p,ct.c_void_p,ct.c_uint32],ct.c_int)}
        for key,(name,args,result) in definitions.items():
            value=None
            if name not in disabled:
                for module in modules:
                    value=getattr(module,name,None)
                    if value is not None:self.resolved[name]=module._name;break
            if value is None:self.missing.append(name)
            else:value.argtypes=args;value.restype=result;self.functions[key]=value
        k=modules[-1];free=k.VirtualFree;free.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32];free.restype=ct.c_int
        self.functions.update(open=BASE.create_file,section=BASE.create_mapping,file_size=BASE.size,split=free,coalesce=free,release=free,close_section=BASE.close,close_file=BASE.close)
        self.process=BASE.process()
    @property
    def available(self):return not self.missing
    def invoke(self,name,*args,index=None):
        if self.hook:self.hook(name,index)
        value=self.functions[name](*args)
        if not value:raise ct.WinError(ct.get_last_error())
        return value

class AliasView:
    # 同一个owner只管理自身一份model；外部复制仍须遵守原ROM借用生命周期。
    def __init__(self,mode,api):
        if mode not in ('alias','aligned'):raise ValueError('固定alias或对齐RO控制')
        if not api.available:raise RuntimeError('新API缺失：'+','.join(api.missing))
        self._state=OwnerState();self._state.reserved=0 if mode=='alias' else 1;self.model=Model();self.api=api;self.startup={}
        if ct.sizeof(self._state)!=48 or ct.sizeof(self.model)!=1056:raise AssertionError('实际owner/model ABI不同')
    @property
    def mode(self):return 'alias' if self._state.reserved==0 else 'aligned'
    @property
    def closed(self):return not(self._state.file or self._state.section or self._state.base)
    @property
    def blob(self):
        if self._state.state!=5:raise RuntimeError('owner尚未READY或已关闭')
        return self._state.base+3040
    def _bounded(self,address,length):
        base=self._state.base;span=self._state.span
        if not base or length<=0 or address<base or address+length>base+span or base+span>INVALID:raise AssertionError('操作范围不属于自有保留区')
    def open(self,path,d):
        if not self.closed or self._state.state!=0:raise RuntimeError('owner已使用；关闭后不可重开')
        started=time.perf_counter()
        try:
            handle=self.api.invoke('open',str(Path(path).resolve()),0x80000000,1,None,3,0x80,None)
            if handle==INVALID:raise ct.WinError(ct.get_last_error())
            self._state.file=handle;self._state.state=1
            length=ct.c_int64();self.api.invoke('file_size',handle,ct.byref(length))
            with Path(path).open('rb') as source:
                header=source.read(PAGE)
                if len(header)!=PAGE or header[:4]!=b'P4AL':raise ValueError('P4AL头错误')
                version,page,pages,unique,metadata,pool_offset,kind=struct.unpack_from('<7I',header,4)
                if (version,page,pages,kind)!=(1,PAGE,PAGES,self._state.reserved) or not 1<=unique<=PAGES or any(header[96:3040]):raise ValueError('P4AL固定参数错误')
                if self.mode=='alias':
                    if metadata!=16384 or pool_offset!=20480 or length.value!=pool_offset+unique*PAGE:raise ValueError('alias尺寸错误')
                    raw=source.read(metadata)
                    if len(raw)!=metadata:raise ValueError('pageID截断')
                    identifiers=struct.unpack('<4096I',raw)
                    if any(value>=unique for value in identifiers):raise ValueError('pageID越pool')
                    del raw
                else:
                    if unique!=PAGES or metadata or pool_offset!=PAGE or length.value!=DATA_SPAN:raise ValueError('aligned尺寸错误')
                    identifiers=None
            old=header[3040:]
            if old[:4]!=b'M16D' or struct.unpack_from('<3I',old,4)[:2]!=(1,0) or struct.unpack_from('<I',old,16)[0]!=(1<<24) or any(struct.unpack_from('<3I',old,20)):raise ValueError('原linear头错误')
            expected_id=header[32:64].hex();expected_rom=header[64:96].hex()
            self.startup['file_metadata_seconds']=time.perf_counter()-started;mapping_start=time.perf_counter()
            self._state.section=self.api.invoke('section',self._state.file,None,2,0,0,None);self._state.state=2
            self._state.base=self.api.invoke('reserve',self.api.process,None,RESERVE_SPAN,0x42000,1,None,0);self._state.span=RESERVE_SPAN;self._state.state=3
            base=self._state.base
            if base%PAGE:raise AssertionError('API保留地址非页对齐')
            split_count=PAGES+1 if self.mode=='alias' else 1
            for index in range(split_count):
                address=base+index*PAGE if self.mode=='alias' else base;extent=PAGE if self.mode=='alias' else DATA_SPAN;self._bounded(address,extent)
                self.api.invoke('split',address,extent,0x8002,index=index);self._state.split_pages+=1
            self._state.state=4
            for index in range(PAGES+1 if self.mode=='alias' else 1):
                address=base+index*PAGE if self.mode=='alias' else base;extent=PAGE if self.mode=='alias' else DATA_SPAN;offset=(0 if index==0 else pool_offset+identifiers[index-1]*PAGE) if self.mode=='alias' else 0
                self._bounded(address,extent)
                info=query(address)
                if info['State']!=0x2000:raise AssertionError('待替换区域不是保留placeholder')
                result=self.api.invoke('map',self._state.section,self.api.process,address,offset,extent,0x4000,2,None,0,index=index)
                if result!=address:raise AssertionError('替换placeholder返回了其它地址')
                self._state.mapped_pages+=1
                for position in (address,address+extent-1):
                    info=query(position)
                    if info['State']!=0x1000 or info['Protect']!=2 or info['Type']!=0x40000:raise AssertionError('实际view并非只读文件映射')
            del identifiers
            guard=query(base+DATA_SPAN)
            if guard['State']!=0x2000:raise AssertionError('末页guard被替换')
            self.startup['section_reserve_split_map_seconds']=time.perf_counter()-mapping_start;verify_start=time.perf_counter()
            blob=base+3040;canonical=(ct.c_uint8*MODEL_BYTES).from_address(blob);table=(ct.c_uint8*(1<<24)).from_address(base+PAGE)
            if hashlib.sha256(canonical).hexdigest()!=expected_rom or hashlib.sha256(table).hexdigest()!=expected_id:raise ValueError('虚拟canonical/ID摘要不同')
            del canonical,table
            self.startup['canonical_validation_seconds']=time.perf_counter()-verify_start;prepare_start=time.perf_counter()
            if self.api.hook:self.api.hook('prepare',None)
            if d.jshc_mem_prepare(ct.byref(self.model),blob,MODEL_BYTES):raise ValueError('原native prepare拒绝')
            self.startup['native_prepare_seconds']=time.perf_counter()-prepare_start;self.startup['owner_open_total_seconds']=time.perf_counter()-started
            self._state.state=5;return self
        except BaseException as error:
            cleanup=None
            try:self.close()
            except BaseException as secondary:cleanup=secondary
            raise AliasFailure(self,error,cleanup) from error
    def close(self):
        ct.memset(ct.byref(self.model),0,ct.sizeof(self.model))
        if self.closed:self._state.state=7;return
        self._state.state=6
        try:
            if self._state.base:
                while self._state.mapped_pages:
                    index=self._state.mapped_pages-1;address=self._state.base+index*PAGE if self.mode=='alias' else self._state.base;extent=PAGE if self.mode=='alias' else DATA_SPAN;self._bounded(address,extent)
                    self.api.invoke('unmap',self.api.process,address,2,index=index);self._state.mapped_pages-=1
                if self._state.split_pages:
                    self.api.invoke('coalesce',self._state.base,self._state.span,0x8001);self._state.split_pages=0
                self.api.invoke('release',self._state.base,0,0x8000);self._state.base=None;self._state.span=0
            for field,name in (('section','close_section'),('file','close_file')):
                handle=getattr(self._state,field)
                if handle:self.api.invoke(name,handle);setattr(self._state,field,None)
            self._state.state=7
        except BaseException as error:raise AliasFailure(self,error) from error
    def __enter__(self):
        if self._state.state!=5:raise RuntimeError('尚未成功open')
        return self
    def __exit__(self,kind,error,trace):
        try:self.close()
        except BaseException as cleanup:
            if error is None:raise
            error.add_note('退出同时清理失败：'+str(cleanup));error.alias_owner=self
        return False
    def describe(self):return dict(mode=self.mode,owner_bytes=ct.sizeof(self._state),model_bytes=ct.sizeof(self.model),state={name:int(getattr(self._state,name) or 0) for name,_ in self._state._fields_},new_api_resolution=self.api.resolved)

def open_with_fallback(alias_path,original_path,d,api=None):
    api=api or NewAPI()
    if not api.available:
        owner=FileView(original_path,'readonly');model=owner.prepare(d)
        return dict(mode='fallback-linear-readonly',owner=owner,model=model,missing=list(api.missing),capacity=Path(original_path).stat().st_size+ct.sizeof(Model))
    owner=AliasView('alias',api).open(alias_path,d)
    return dict(mode='alias',owner=owner,model=owner.model,missing=[],capacity=Path(alias_path).stat().st_size+ct.sizeof(OwnerState)+ct.sizeof(Model))
