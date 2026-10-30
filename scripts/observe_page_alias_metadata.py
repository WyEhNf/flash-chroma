"""最后一次固定8例metadata reader观察，首漂移STOP，不授资格。"""
import argparse
import ctypes as ct
import json
import msvcrt
import os
from pathlib import Path
import time
import observe_page_alias_handles as old
from page_alias_runtime import AliasFailure,BASE,sha,read,save
ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'experiments/page-alias-metadata-observer-v1.json'
GET_HANDLE_INFO=ct.WinDLL('kernel32',use_last_error=True).GetHandleInformation;GET_HANDLE_INFO.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint32)];GET_HANDLE_INFO.restype=ct.c_int
def key(path):return os.path.normcase(os.path.normpath(str(path)))
def handle_info(handle):
    prior=ct.get_last_error();ct.set_last_error(0);flags=ct.c_uint32();result=GET_HANDLE_INFO(handle,ct.byref(flags));error=ct.get_last_error();ct.set_last_error(prior);return dict(result=int(result),last_error=error,flags=flags.value)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();plan=read(PLAN)
    if any(sha(ROOT/name)!=value for name,value in plan['source_sha256'].items()) or any(sha(name)!=value for name,value in plan['input_sha256'].items()):raise AssertionError('冻结源/输入不同，启动前STOP')
    a.output.mkdir(parents=True,exist_ok=False);observer=old.Observer();metadata=[];paths={key(plan['alias']):'alias',key(plan['aligned']):'aligned'};original=Path.open;failed=None;result=None;started=time.perf_counter()
    def record(label,reader,kind,fd,handle,extra=None):
        raw=getattr(reader,'raw',None);value=dict(label=label,case=observer.case,kind=kind,count=old.count(),fd=fd,winhandle=handle,reader_closed=bool(reader.closed),raw_closed=None if raw is None else bool(raw.closed),closefd=None if raw is None else bool(raw.closefd),handle_info=handle_info(handle),extra=extra)
        metadata.append(value);observer.mark('metadata:'+label,value)
    class Context:
        def __init__(self,reader,kind,fd,handle):self.reader=reader;self.kind=kind;self.fd=fd;self.handle=handle
        def __enter__(self):
            record('enter前',self.reader,self.kind,self.fd,self.handle);value=self.reader.__enter__();record('enter后',self.reader,self.kind,self.fd,self.handle)
            if value is not self.reader:raise AssertionError('原__enter__没有返回原reader')
            return value
        def __exit__(self,*args):
            record('exit前',self.reader,self.kind,self.fd,self.handle,dict(exception_type=None if args[0] is None else args[0].__name__))
            try:return self.reader.__exit__(*args)
            finally:record('exit后',self.reader,self.kind,self.fd,self.handle)
    def observed(path,*args,**kwargs):
        kind=paths.get(key(path))
        if kind is None:return original(path,*args,**kwargs)
        before=old.count();reader=original(path,*args,**kwargs);fd=reader.fileno();handle=msvcrt.get_osfhandle(fd);record('open返回',reader,kind,fd,handle,dict(before_count=before,after_count=old.count(),mode=reader.mode));return Context(reader,kind,fd,handle)
    Path.open=observed
    try:result=old.run(a.output,plan,observer)
    except BaseException as error:
        failed=error;result=dict(observation_completed=False,type=type(error).__name__,message=str(error),case=observer.case,actual_count=old.count(),owned_state=observer.state(),scope='最后一次观察原样STOP，不撤销先前结果/不授资格。')
        owner=error.owner if isinstance(error,AliasFailure) else observer.owner
        if owner is not None and not owner.closed:
            Path.open=original;observer.export(a.output);save(a.output/'metadata.json',metadata);save(a.output/'results.json',result);print(result,flush=True);print('STOP：owner存活，status/retry显式命令；成功不恢复资格。',flush=True)
            while not owner.closed:
                command=input().strip()
                if command=='status':print(observer.state(),flush=True)
                elif command=='retry':
                    try:owner.close();print('显式回收成功',flush=True)
                    except BaseException as secondary:print(str(secondary),flush=True)
    finally:Path.open=original
    observer.mark('最终计数区结束');observer.export(a.output);save(a.output/'metadata.json',metadata);result.update(plan_sha256=sha(PLAN),records=observer.used,metadata_records=len(metadata),event_bytes=ct.sizeof(observer.events),observation_wall_seconds=time.perf_counter()-started,raw_files={name:sha(a.output/name) for name in ('events.bin','events.csv','event-schema.json','metadata.json')});save(a.output/'results.json',result);print(result,flush=True)
    if failed:raise failed
if __name__=='__main__':main()
