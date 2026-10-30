"""页别名前置的三个fresh观察与真实API/回收/格式合同；不运行图像或吞吐。"""
import argparse
from collections import Counter
import ctypes as ct
import gc
import hashlib
import json
from pathlib import Path
import struct
import sys
import time
START=time.perf_counter()
from page_alias_runtime import AliasView,AliasFailure,NewAPI,BASE,FileView,Model,OwnerState,library,query,sha,read,save,env,open_with_fallback,PAGE,PAGES,MODEL_BYTES,DATA_SPAN,RESERVE_SPAN
from bench_memory_rom import Counters
from win_readonly_rom import snapshot,touch
from export_page_alias import ROOT,PLAN

class WorkingPage(ct.Structure):
    _fields_=[('address',ct.c_void_p),('attributes',ct.c_size_t)]
PSAPI=ct.WinDLL('psapi',use_last_error=True)
GET_COUNTERS=PSAPI.GetProcessMemoryInfo;GET_COUNTERS.argtypes=[ct.c_void_p,ct.c_void_p,ct.c_uint32];GET_COUNTERS.restype=ct.c_int
GET_WS=PSAPI.QueryWorkingSetEx;GET_WS.argtypes=[ct.c_void_p,ct.c_void_p,ct.c_uint32];GET_WS.restype=ct.c_int
FAILED_OWNER=None
ACTIVE_OWNER=None
def tracked(owner):
    global ACTIVE_OWNER
    ACTIVE_OWNER=owner;return owner
def checked():
    plan=read(PLAN)
    if any(sha(ROOT/name)!=value for name,value in plan['source_sha256'].items()) or any(sha(name)!=value for name,value in plan['input_sha256'].items()):raise AssertionError('前置冻结源/输入不同')
    return plan
def account():
    result=snapshot();value=Counters();value.cb=ct.sizeof(value)
    if not GET_COUNTERS(BASE.process(),ct.byref(value),ct.sizeof(value)):raise ct.WinError(ct.get_last_error())
    result['all_process_counters']={name:int(getattr(value,name)) for name,_ in value._fields_ if name!='cb'}
    return result
def python_layout(owner):
    # shallow只作透明账目，不与ctypes buffer重复相加后冒称深层全部内存。
    return dict(owner_object_shallow_bytes=sys.getsizeof(owner),owner_dict_shallow_bytes=sys.getsizeof(owner.__dict__),owner_attributes=list(owner.__dict__),model_python_object_shallow_bytes=sys.getsizeof(owner.model) if isinstance(owner,AliasView) else None,state_python_object_shallow_bytes=sys.getsizeof(owner._state) if isinstance(owner,AliasView) else None,api_object_shallow_bytes=sys.getsizeof(owner.api),api_dict_shallow_bytes=sys.getsizeof(owner.api.__dict__),api_attributes=list(owner.api.__dict__),scope='Python浅层对象不是48B必要native状态，不能当深层total；ctypes原生buffer单列；fresh PrivateUsage/WS包含解释器/表/对象及统计，不扣成纯模型RAM。')
def regions(base,span):
    cursor=base;end=base+span;rows=[]
    while cursor<end:
        value=query(cursor);rows.append(value);cursor=value['BaseAddress']+value['RegionSize']
        if cursor<=value['BaseAddress']:raise AssertionError('VirtualQuery没有前进')
    return rows
def pages(address,length):
    count=(length+PAGE-1)//PAGE;values=(WorkingPage*count)()
    for index in range(count):values[index].address=address+index*PAGE
    if not GET_WS(BASE.process(),values,ct.sizeof(values)):raise ct.WinError(ct.get_last_error())
    flags=[int(value.attributes) for value in values];histogram=Counter()
    for value in flags:
        histogram[(value&1,(value>>1)&7,(value>>4)&2047,(value>>15)&1)]+=1
    return dict(address=address,pages=count,raw_attributes=flags,histogram=[dict(valid=k[0],share_count_processes=k[1],win32_protection=k[2],shared=k[3],pages=v) for k,v in sorted(histogram.items())],scope='ShareCount为进程数而非同进程别名数；没有PFN；不能由这些字段计算唯一物理RAM。')
def assert_cleared(owner,base=None):
    if not owner.closed or any(bytes(owner.model)) or owner._state.state!=7:raise AssertionError('owner未关闭/Model未清零/终态不同')
    if base and query(base)['State']!=0x10000:raise AssertionError('自有VA未释放')
    try:owner.blob
    except RuntimeError:pass
    else:raise AssertionError('关闭后仍暴露blob')
    owner.close()
def fresh(mode,out,plan):
    d=library(plan['library']);api=NewAPI();gc.collect();account();before=account();phases={'before':before};owner=None;model=None;started=time.perf_counter();base=None
    try:
        if mode=='original':
            owner=tracked(FileView(plan['original_rom'],'readonly'));base=owner.address;address=base;model=owner.prepare(d);span=owner.length;startup={'whole_owner_prepare_seconds':time.perf_counter()-started};capacity=owner.length+ct.sizeof(Model);mapping_regions=regions(base,span);guard=None
        else:
            owner=tracked(AliasView(mode,api)).open(out.parent/'export'/(mode+'.bin'),d);base=owner._state.base;address=owner.blob;model=owner.model;span=RESERVE_SPAN;startup=owner.startup;capacity=(out.parent/'export'/(mode+'.bin')).stat().st_size+48+1056;mapping_regions=regions(base,span);guard=query(base+DATA_SPAN)
        phases['opened']=account();open_time=time.perf_counter()-started
        if hashlib.sha256((ct.c_uint8*MODEL_BYTES).from_address(address)).hexdigest()!=plan['original_rom_sha256']:raise AssertionError('实际虚拟blob身份不同')
        protected=[query(address),query(address+MODEL_BYTES-1)]
        if any(value['Protect']!=2 or value['Type']!=0x40000 for value in protected):raise AssertionError('头尾实际不是只读映射')
        touch_start=time.perf_counter();touched=touch(address,MODEL_BYTES);touch_time=time.perf_counter()-touch_start;phases['all_pages_read']=account();working=pages(base,DATA_SPAN if mode!='original' else MODEL_BYTES)
        observed=dict(canonical_sha256=plan['original_rom_sha256'],blob=address,table=int(ct.cast(model.table,ct.c_void_p).value),view_base=base,view_span=span,model_bytes=ct.sizeof(model),owner_bytes=48 if mode!='original' else None,capacity=capacity,python_layout=python_layout(owner),protected_ends=protected,guard=guard,virtual_regions=mapping_regions,working_set_pages=working,touch=touched,startup=startup,open_observation_seconds=open_time,page_read_seconds=touch_time)
    finally:
        close_start=time.perf_counter()
        if owner:owner.close()
        close_time=time.perf_counter()-close_start
    phases['closed']=account()
    if any(bytes(model)) or not owner.closed or query(base)['State']!=0x10000:raise AssertionError('fresh关闭后Model/VA合同失败')
    if phases['before']['process_handles']!=phases['closed']['process_handles']:raise AssertionError('fresh句柄未回到基线')
    observed.update(mode=mode,passed=True,phases=phases,close_seconds=close_time,new_api_resolution=api.resolved,missing=api.missing,process_to_result_seconds=time.perf_counter()-START,environment=env(),plan_sha256=sha(PLAN),scope='同imports各一次fresh setup观察；完整SHA和进程启动另列，不是稳定吞吐/冷启动资格；WS按虚拟页计，无PFN/内核VAD/PTE精确归因。')
    save(out/'results.json',observed);print(dict(mode=mode,passed=True,capacity=capacity,regions=len(mapping_regions)),flush=True)

class Injected(RuntimeError):pass
class Hook:
    def __init__(self,triggers=()):self.triggers=list(triggers);self.counts=Counter();self.tail=[];self.used=[]
    def __call__(self,name,index):
        self.counts[name]+=1;self.tail.append([name,index]);self.tail=self.tail[-24:]
        if (name,index) in self.triggers:
            self.triggers.remove((name,index));self.used.append([name,index]);raise Injected('预注册调用前失败：'+name+':'+str(index))
    def report(self):return dict(counts=dict(self.counts),last_events=self.tail,used=self.used,unconsumed=self.triggers)
def fixture_header(old,pool,identifiers):
    logical=hashlib.sha256();canonical=hashlib.sha256(old)
    for value in identifiers:logical.update(pool[value]);canonical.update(pool[value])
    header=bytearray(PAGE);header[:32]=b'P4AL'+struct.pack('<7I',1,PAGE,PAGES,len(pool),16384,20480,0);header[32:64]=logical.digest();header[64:96]=canonical.digest();header[3040:]=old;return header
def contracts(out,plan):
    d=library(plan['library']);api=NewAPI()
    if not api.available:raise RuntimeError('真实API不支持alias，STOP；仅fallback合同不能授alias资格')
    gc.collect();account();baseline=account()['process_handles'];rows=[];alias=out.parent/'export/alias.bin';aligned=out.parent/'export/aligned.bin'
    def settle(owner,base=None):
        assert_cleared(owner,base);gc.collect()
        if account()['process_handles']!=baseline:raise AssertionError('合同后句柄未回基线')
    for mode,path in (('alias',alias),('aligned',aligned)):
        owner=tracked(AliasView(mode,api)).open(path,d);base=owner._state.base;description=owner.describe()
        if owner.blob!=base+3040 or ct.cast(owner.model.table,ct.c_void_p).value!=base+PAGE or query(base+DATA_SPAN)['State']!=0x2000:raise AssertionError('对齐/原ABI/尾guard不同')
        writer=BASE.create_file(str(path.resolve()),0x40000000,1,None,3,0x80,None);code=ct.get_last_error()
        if writer not in (None,(1<<64)-1):BASE.close(writer);raise AssertionError('活跃owner允许外部写共享')
        if code!=32:raise AssertionError('写共享拒绝不是ERROR_SHARING_VIOLATION')
        owner.close();settle(owner,base)
        try:owner.open(path,d)
        except RuntimeError:pass
        else:raise AssertionError('终态owner被重开')
        if not d.jshc_mem_apply_parallel(ct.byref(owner.model),None,None,0,0,1):raise AssertionError('清零Model未被旧库拒绝')
        rows.append(dict(kind='success-close',description=description,closed_model_zero=True,va_free=True,write_share_error=code,reopen_rejected=True))
    for missing in ('VirtualAlloc2','MapViewOfFile3','UnmapViewOfFile2'):
        hook=Hook();disabled=NewAPI(disabled=(missing,),hook=hook);fallback=open_with_fallback(alias,plan['original_rom'],d,disabled);owner=tracked(fallback['owner']);address=owner.address
        if fallback['mode']!='fallback-linear-readonly' or fallback['capacity']!=16779328 or missing not in fallback['missing'] or hook.counts or hashlib.sha256((ct.c_uint8*MODEL_BYTES).from_address(address)).hexdigest()!=plan['original_rom_sha256']:raise AssertionError('缺符号没有明确原RO fallback')
        owner.close();gc.collect()
        if not owner.closed or any(bytes(fallback['model'])) or account()['process_handles']!=baseline:raise AssertionError('fallback回收失败')
        rows.append(dict(kind='missing-symbol-fallback',missing=missing,actual_mode=fallback['mode'],capacity=fallback['capacity'],new_api_calls=dict(hook.counts)))
    # 所有注入都发生在预定调用之前；已成功部分是真实OS资源，不用模拟指针冒充回收。
    for name,indices in (('open',(None,)),('file_size',(None,)),('section',(None,)),('reserve',(None,)),('split',(0,1,2048,4096)),('map',(0,1,2048,4096)),('prepare',(None,))):
        for index in indices:
            hook=Hook(((name,index),));owner=tracked(AliasView('alias',NewAPI(hook=hook)))
            try:owner.open(alias,d)
            except AliasFailure as error:
                if not isinstance(error.cause,Injected) or error.cleanup is not None or hook.triggers:raise
                settle(owner)
            else:raise AssertionError('预注册构造失败未传播')
            rows.append(dict(kind='open-failure',stage=name,index=index,events=hook.report(),closed=owner.describe()))
    for name,index in (('unmap',4096),('coalesce',None),('release',None),('close_section',None),('close_file',None)):
        hook=Hook(((name,index),));owner=tracked(AliasView('alias',NewAPI(hook=hook))).open(alias,d);base=owner._state.base
        try:owner.close()
        except AliasFailure as error:
            if not isinstance(error.cause,Injected) or owner.closed or any(bytes(owner.model)) or hook.triggers:raise
            retained=owner.describe();owner.close();settle(owner,base)
        else:raise AssertionError('清理失败未显式保留')
        rows.append(dict(kind='close-failure-explicit-retry',stage=name,index=index,retained=retained,events=hook.report(),retry_closed=True))
    hook=Hook((('map',2048),('unmap',2047)));owner=tracked(AliasView('alias',NewAPI(hook=hook)))
    try:owner.open(alias,d)
    except AliasFailure as error:
        if not isinstance(error.cause,Injected) or not isinstance(error.cleanup,AliasFailure) or owner.closed or any(bytes(owner.model)) or hook.triggers:raise
        retained=owner.describe();base=owner._state.base;owner.close();settle(owner,base)
    else:raise AssertionError('构造+清理双失败未传播')
    rows.append(dict(kind='open-and-cleanup-failure-explicit-retry',retained=retained,events=hook.report(),retry_closed=True))
    # 两个固定通用格式夹具仅验Model/ROM，不执行图像；count256包含全部合法槽与末ID255。
    fixtures=out/'fixtures';fixtures.mkdir();good=[]
    for count in (1,256):
        old=bytearray(1056);old[:32]=b'M16D'+struct.pack('<7I',1,0,count,1<<24,0,0,0)
        for item in range(count):struct.pack_into('<I',old,32+4*item,(item*0x10101) if count==256 else 0x030201)
        pool=[bytes(range(256))*16 if count==256 else bytes(PAGE)];ids=[0]*PAGES;header=fixture_header(old,pool,ids);content=header+struct.pack('<4096I',*ids)+pool[0];path=fixtures/('count'+str(count)+'.bin');path.write_bytes(content)
        owner=tracked(AliasView('alias',api)).open(path,d);base=owner._state.base
        if owner.model.palette_size!=count or any(owner.model.palette[item]!=struct.unpack_from('<I',old,32+4*item)[0] for item in range(256)) or owner.model.table[(1<<24)-1]!=(255 if count==256 else 0):raise AssertionError('全部palette/末ID通用合同失败')
        owner.close();settle(owner,base);good.append(dict(count=count,bytes=len(content),sha256=sha(path),all_palette_slots=256,last_id=255 if count==256 else 0))
    base_content=bytearray((fixtures/'count1.bin').read_bytes());mutations=[]
    def mutate(label,offset,raw):
        content=bytearray(base_content);content[offset:offset+len(raw)]=raw;mutations.append((label,content))
    for label,offset,value in (('version',4,2),('page',8,2048),('pages',12,4095),('zero-unique',16,0),('large-unique',16,4097),('metadata',20,16380),('pool-offset',24,20481),('kind',28,1),('first-id',4096,1),('last-id',4096+4095*4,1),('old-version',3044,2),('old-bits',3048,4),('old-length',3056,(1<<24)-1),('old-flags',3060,1)):
        mutate(label,offset,struct.pack('<I',value))
    mutate('magic',0,b'X');mutate('reserved',96,b'\x01');mutate('old-magic',3040,b'X');mutate('id-digest',32,b'X');mutate('canonical-digest',64,b'X');mutations.extend((('truncated',base_content[:-1]),('extra-byte',base_content+b'X'),('zero-file',b'')))
    for count in (0,257):
        content=bytearray(base_content);old=bytearray(content[3040:4096]);struct.pack_into('<I',old,12,count);content[:4096]=fixture_header(old,[bytes(PAGE)],[0]*PAGES);mutations.append(('native-count'+str(count),content))
    rejected=[]
    for label,content in mutations:
        path=fixtures/('bad-'+label+'.bin');path.write_bytes(content);owner=tracked(AliasView('alias',api))
        try:owner.open(path,d)
        except AliasFailure as error:
            if error.cleanup is not None:raise
            cause=dict(type=type(error.cause).__name__,message=str(error.cause));settle(owner)
        else:raise AssertionError('畸形容器未拒绝：'+label)
        rejected.append(dict(label=label,bytes=len(content),sha256=sha(path),cause=cause))
    owner=tracked(AliasView('alias',api))
    try:owner.open(fixtures/'missing.bin',d)
    except AliasFailure as error:
        if not isinstance(error.cause,OSError) or error.cleanup is not None:raise
        settle(owner);rejected.append(dict(label='missing-file',cause=str(error.cause)))
    else:raise AssertionError('缺失文件未拒绝')
    result=dict(passed=True,plan_sha256=sha(PLAN),environment=env(),new_api_resolution=api.resolved,api_missing=api.missing,lifecycle=rows,format_fixtures=good,format_rejections=rejected,handle_baseline=baseline,handle_final=account()['process_handles'],owner_bytes=ct.sizeof(OwnerState),model_bytes=ct.sizeof(Model),owner_offsets={name:getattr(OwnerState,name).offset for name,_ in OwnerState._fields_},virtual_model_span=DATA_SPAN,reserved_span=RESERVE_SPAN,guard_va_bytes=PAGE,mandatory_fields=[name for name,_ in OwnerState._fields_],scope='唯一部署API/生命周期/格式前置；无像素完整域/百图/速度。QueryWorkingSetEx无PFN，内核PTE/VAD成本未知；Python外壳/统计元数据不能隐去。')
    save(out/'results.json',result);print(dict(passed=True,lifecycle=len(rows),format_fixtures=len(good),format_rejections=len(rejected),handles=baseline),flush=True)
def retain_failure(error,out):
    global FAILED_OWNER
    owner=error.owner if isinstance(error,AliasFailure) else ACTIVE_OWNER
    cleanup=None
    if owner is not None and not owner.closed and not isinstance(error,AliasFailure):
        try:owner.close()
        except BaseException as secondary:cleanup=str(secondary)
    data=dict(passed=False,type=type(error).__name__,message=str(error),notes=getattr(error,'__notes__',[]),cleanup_error=cleanup,owner=owner.describe() if isinstance(owner,AliasView) else None)
    save(out/'failure.json',data);print(data,flush=True)
    if owner is not None and not owner.closed:
        FAILED_OWNER=owner;print('STOP：资源仍由本进程owner持有；输入status查看，retry仅显式重试回收，成功也不恢复本阶段资格。',flush=True)
        while not owner.closed:
            command=input().strip()
            if command=='status':print(owner.describe() if isinstance(owner,AliasView) else dict(closed=owner.closed),flush=True)
            elif command=='retry':
                try:owner.close();save(out/'explicit-recovery.json',dict(closed=owner.closed,owner=owner.describe() if isinstance(owner,AliasView) else None));print('显式回收成功；本阶段仍失败。',flush=True)
                except BaseException as secondary:print(str(secondary),flush=True)
    raise error
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mode',choices=['original','aligned','alias','contracts'],required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    try:
        plan=checked();receipt=read(a.output.parent/'export/export.json')
        if receipt['plan_sha256']!=sha(PLAN) or any(sha(a.output.parent/'export'/name)!=value['sha256'] or (a.output.parent/'export'/name).stat().st_size!=value['bytes'] for name,value in receipt['outputs'].items()):raise AssertionError('唯一导出receipt/文件不同')
        if a.mode=='contracts':contracts(a.output,plan)
        else:fresh(a.mode,a.output,plan)
    except BaseException as error:retain_failure(error,a.output)
if __name__=='__main__':main()
