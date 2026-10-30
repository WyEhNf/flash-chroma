"""仅一次观察v1停止前8例，首count偏移STOP；不撤销v1或授资格。"""
import argparse
import csv
import ctypes as ct
import gc
import hashlib
import json
from pathlib import Path
import time
import page_alias_runtime as runtime
from page_alias_runtime import AliasView,AliasFailure,NewAPI,BASE,FileView,library,query,sha,read,save,MODEL_BYTES
from page_alias_front import account,Injected

ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'experiments/page-alias-handle-observer-v1.json'
NAMES=['marker','open','file_size','section','reserve','split','map','unmap','coalesce','release','close_section','close_file','legacy_open','legacy_size','legacy_section','legacy_map','legacy_unmap','legacy_close']
class Event(ct.Structure):
    _fields_=[*[(name,ct.c_uint32) for name in ('sequence','case','operation','index','status','before_count','after_count','last_error')],*[(name,ct.c_uint64) for name in ('arg0','arg1','result')],*[(prefix+name,ct.c_uint64) for prefix in ('before_','after_') for name in ('file','section','base','span')],*[(prefix+name,ct.c_uint32) for prefix in ('before_','after_') for name in ('mapped','split','state','model_zero')]]
def count():
    old=ct.get_last_error();value=ct.c_uint32();ok=BASE.handles(BASE.process(),ct.byref(value));error=ct.get_last_error();ct.set_last_error(old)
    if not ok:raise ct.WinError(error)
    return value.value
class Observer:
    def __init__(self):self.events=(Event*32768)();self.used=0;self.case=0;self.owner=None;self.markers=[];self.errors=[]
    def state(self):
        owner=self.owner
        if isinstance(owner,AliasView):
            s=owner._state;return [int(s.file or 0),int(s.section or 0),int(s.base or 0),int(s.span),int(s.mapped_pages),int(s.split_pages),int(s.state),int(not any(bytes(owner.model)))]
        if isinstance(owner,FileView):
            models=getattr(owner,'models',[]);return [int(getattr(owner,'file',0) or 0),int(getattr(owner,'mapping',0) or 0),int(getattr(owner,'_address',0) or 0),int(getattr(owner,'length',0)),int(bool(getattr(owner,'_address',0))),0,7 if getattr(owner,'closed',False) else 1,int(all(not any(bytes(model)) for model in models))]
        return [0,0,0,0,0,0,0,1]
    def record(self,name,index,status,before,after,bstate,astate,arg0=0,arg1=0,result=0,error=0):
        if self.used==len(self.events):raise AssertionError('预分配事件数组用尽，STOP不扩容')
        row=self.events[self.used];row.sequence=self.used;row.case=self.case;row.operation=NAMES.index(name);row.index=0xffffffff if index is None else index;row.status=status;row.before_count=before;row.after_count=after;row.last_error=error;row.arg0=arg0;row.arg1=arg1;row.result=result
        for prefix,values in (('before_',bstate),('after_',astate)):
            for key,value in zip(('file','section','base','span','mapped','split','state','model_zero'),values):setattr(row,prefix+key,value)
        self.used+=1
    def mark(self,label,details=None):
        number=count();state=self.state();self.record('marker',None,0,number,number,state,state);self.markers.append(dict(sequence=self.used-1,label=label,details=details));return number
    def call(self,name,index,args,invoke):
        before=count();bstate=self.state();ct.set_last_error(0)
        arg0=int(args[0] or 0) if args and isinstance(args[0],(int,type(None))) else 0;arg1=int(args[1] or 0) if len(args)>1 and isinstance(args[1],(int,type(None))) else 0
        try:result=invoke()
        except BaseException as failure:
            error=ct.get_last_error();after=count();self.record(name,index,2 if isinstance(failure,Injected) else 3,before,after,bstate,self.state(),arg0,arg1,0,error);self.errors.append(dict(sequence=self.used-1,type=type(failure).__name__,message=str(failure)));ct.set_last_error(error);raise
        error=ct.get_last_error();after=count();self.record(name,index,1,before,after,bstate,self.state(),arg0,arg1,int(result or 0),error);ct.set_last_error(error);return result
    def export(self,out):
        fields=[name for name,_ in Event._fields_];size=ct.sizeof(Event);(out/'events.bin').write_bytes(ct.string_at(ct.addressof(self.events),self.used*size))
        with (out/'events.csv').open('w',encoding='utf-8',newline='') as stream:
            writer=csv.writer(stream);writer.writerow(fields)
            for index in range(self.used):writer.writerow([int(getattr(self.events[index],name)) for name in fields])
        save(out/'event-schema.json',dict(record_bytes=size,records=self.used,capacity_records=32768,allocated_bytes=ct.sizeof(self.events),fields=[dict(name=name,offset=getattr(Event,name).offset,bytes=ct.sizeof(kind)) for name,kind in Event._fields_],operations=NAMES,status=dict(marker=0,real_call_returned=1,injected_before_call=2,exception=3),index_none=0xffffffff,markers=self.markers,errors=self.errors,scope='实际owned字段before/after为原函数清字段之前的边界；返回后由runtime清字段，再由下个API/marker复核。GetProcessHandleCount不递归记录；日志文件在测量区结束后才打开。'))
class ObservedNewAPI(NewAPI):
    def __init__(self,observer,**kwargs):self.observer=observer;super().__init__(**kwargs)
    def invoke(self,name,*args,index=None):return self.observer.call(name,index,args,lambda:NewAPI.invoke(self,name,*args,index=index))
class LegacyAPI:
    def __init__(self,observer):self.observer=observer
    def __getattr__(self,name):
        target=getattr(BASE,name);label={'create_file':'legacy_open','size':'legacy_size','create_mapping':'legacy_section','map_view':'legacy_map','unmap':'legacy_unmap','close':'legacy_close'}.get(name)
        return (lambda *args:self.observer.call(label,None,args,lambda:target(*args))) if label else target
class OneFailure:
    def __init__(self,name):self.name=name;self.used=False
    def __call__(self,name,index):
        if name==self.name and not self.used:self.used=True;raise Injected('固定调用前失败：'+name)
def run(out,plan,observer):
    observer.mark('imports完成，未加载旧DLL');d=library(plan['library']);observer.mark('旧DLL加载后');api=ObservedNewAPI(observer);observer.mark('新API符号解析后',dict(resolved=api.resolved,missing=api.missing))
    if not api.available:raise RuntimeError('真实API缺失，不运行本固定前缀')
    observer.mark('v1既有gc前');gc.collect();observer.mark('v1既有gc后');observer.mark('v1既有第1次account前');account();observer.mark('v1既有第1次account后');before=account();baseline=before['process_handles'];observer.mark('v1既有第2次account/固定基线',baseline)
    rows=[];alias=Path(plan['alias']);aligned=Path(plan['aligned'])
    def settle(owner,base=None):
        observer.mark('settle开始')
        zero=not any(bytes(owner.model)) if isinstance(owner,AliasView) else all(not any(bytes(model)) for model in owner.models)
        if not owner.closed or not zero:raise AssertionError('owned资源未关闭或Model未清零')
        if isinstance(owner,AliasView):
            if owner._state.state!=7:raise AssertionError('终态不同')
            try:owner.blob
            except RuntimeError:pass
            else:raise AssertionError('close后暴露blob')
            owner.close()
        state=query(base) if base else None
        if state and state['State']!=0x10000:raise AssertionError('原自有VA未MEM_FREE')
        observer.mark('Model清零/VA释放receipt',dict(zero=zero,virtual_query=state));observer.mark('v1每例既有gc前');gc.collect();observer.mark('v1每例既有gc后');after=account();observer.mark('v1每例account实际总数',dict(baseline=baseline,actual=after['process_handles']))
        if after['process_handles']!=baseline:raise AssertionError('全进程count首漂移：baseline='+str(baseline)+' actual='+str(after['process_handles']))
    for mode,path in (('alias',alias),('aligned',aligned)):
        observer.case+=1;observer.mark('固定案例开始',mode);owner=AliasView(mode,api);observer.owner=owner;observer.mark('open前');owner.open(path,d);base=owner._state.base;observer.mark('READY/prepare后');owner.close();settle(owner,base)
        observer.mark('终态重开拒绝前')
        try:owner.open(path,d)
        except RuntimeError:pass
        else:raise AssertionError('终态重开未拒绝')
        observer.mark('终态重开拒绝后');observer.mark('旧native拒绝零Model前')
        if not d.jshc_mem_apply_parallel(ct.byref(owner.model),None,None,0,0,1):raise AssertionError('零Model未拒绝')
        observer.mark('旧native拒绝零Model后');rows.append(dict(case=observer.case,mode=mode,passed=True))
    original_class=runtime.FileView
    class ObservedFileView(FileView):
        def __init__(self,*args,**kwargs):observer.owner=self;kwargs['_api']=LegacyAPI(observer);super().__init__(*args,**kwargs)
    runtime.FileView=ObservedFileView
    try:
        for missing in ('VirtualAlloc2','MapViewOfFile3','UnmapViewOfFile2'):
            observer.case+=1;observer.mark('固定案例开始',missing);disabled=ObservedNewAPI(observer,disabled=(missing,));observer.mark('缺符号解析后',disabled.missing);fallback=runtime.open_with_fallback(alias,plan['original_rom'],d,disabled);owner=fallback['owner'];observer.mark('fallback prepare后')
            if fallback['mode']!='fallback-linear-readonly' or hashlib.sha256((ct.c_uint8*MODEL_BYTES).from_address(owner.address)).hexdigest()!=plan['original_rom_sha256']:raise AssertionError('fallback路径/摘要不同')
            owner.close();settle(owner);rows.append(dict(case=observer.case,missing=missing,mode=fallback['mode'],passed=True))
    finally:runtime.FileView=original_class
    for stage in ('open','file_size','section'):
        observer.case+=1;observer.mark('固定案例开始',stage);failure=OneFailure(stage);owner=AliasView('alias',ObservedNewAPI(observer,hook=failure));observer.owner=owner;observer.mark('注入open前')
        try:owner.open(alias,d)
        except AliasFailure as error:
            observer.mark('收到预期注入异常',dict(cause=str(error.cause),cleanup=str(error.cleanup)))
            if not isinstance(error.cause,Injected) or error.cleanup is not None or not failure.used:raise
            settle(owner)
        else:raise AssertionError('预期注入未传播')
        rows.append(dict(case=observer.case,stage=stage,passed=True))
    observer.mark('固定8例到此结束，不继续原suite');return dict(observation_completed=True,cases=rows,baseline=baseline,final_count=count(),scope='没有复现也不能撤销v1；本次不授资格，全部后续仍未执行。')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();plan=read(PLAN)
    if any(sha(ROOT/name)!=value for name,value in plan['source_sha256'].items()) or any(sha(name)!=value for name,value in plan['input_sha256'].items()):raise AssertionError('观察前冻结源/输入不同，启动前STOP')
    a.output.mkdir(parents=True,exist_ok=False);observer=Observer();result=None;failed=None;started=time.perf_counter()
    try:result=run(a.output,plan,observer)
    except BaseException as error:
        failed=error;result=dict(observation_completed=False,type=type(error).__name__,message=str(error),case=observer.case,actual_count=count(),owned_state=observer.state(),scope='首失败原样STOP，不重跑、不撤销v1或授资格。')
        owner=error.owner if isinstance(error,AliasFailure) else observer.owner
        if owner is not None and not owner.closed:
            observer.mark('意外owned仍在，先保存后等显式回收');observer.export(a.output);save(a.output/'results.json',result);print(result,flush=True);print('STOP：owner存活，status/retry显式命令；成功也不恢复资格。',flush=True)
            while not owner.closed:
                command=input().strip()
                if command=='status':print(observer.state(),flush=True)
                elif command=='retry':
                    try:owner.close();print('显式回收成功',flush=True)
                    except BaseException as secondary:print(str(secondary),flush=True)
    observer.mark('计数区结束');observer.export(a.output);result.update(plan_sha256=sha(PLAN),records=observer.used,event_bytes=ct.sizeof(observer.events),observation_wall_seconds=time.perf_counter()-started,raw_files={name:sha(a.output/name) for name in ('events.bin','events.csv','event-schema.json')});save(a.output/'results.json',result);print(result,flush=True)
    if failed:raise failed
if __name__=='__main__':main()
