"""每种原COW/WinAPI-COW/WinAPI-RO仅一个fresh提交观察，不计吞吐。"""
import argparse
import ctypes as ct
from pathlib import Path
import study_memory_rom as study
from win_readonly_rom import PLAN,FileView,Model,library,checked_plan,snapshot,touch,sha,save,env
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mode',choices=['original_cow','cow','readonly'],required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();plan=checked_plan();a.output.mkdir(parents=True,exist_ok=False)
    d=library(plan['library']);phases={'before':snapshot()};owner=None;keep=None;model=None;address=None;length=0
    def mapped(pointer,size):
        nonlocal address,length
        address=pointer;length=size;phases['mapped_untouched']=snapshot(pointer,size)
    try:
        if a.mode=='original_cow':
            original=study.mmap.mmap
            def observed(*args,**kwargs):
                mapping=original(*args,**kwargs);view=(ct.c_uint8*len(mapping)).from_buffer(mapping)
                mapped(ct.addressof(view),len(mapping));del view
                return mapping
            study.mmap.mmap=observed
            try:model,keep=study.loadrom(d,Path(plan['rom']))
            finally:study.mmap.mmap=original
        else:
            owner=FileView(plan['rom'],a.mode,on_mapped=mapped);model=owner.prepare(d)
        phases['prepared']=snapshot(address,length);touched=touch(address,length);phases['all_pages_read']=snapshot(address,length)
    finally:
        if owner:owner.close()
        if keep:
            ct.memset(ct.byref(model),0,ct.sizeof(model));stream,mapping,view=keep;keep=None;del view;mapping.close();stream.close()
    phases['closed']=snapshot();closed_model_zero=not any(bytes(model))
    if not closed_model_zero:raise AssertionError('close后model未失效')
    expected=2 if a.mode=='readonly' else 8
    for phase in ('mapped_untouched','prepared','all_pages_read'):
        if any(phases[phase]['view'][point]['Protect']!=expected or phases[phase]['view'][point]['Type']!=0x40000 for point in ('first','last')):raise AssertionError('实际页保护/文件映射类型不同')
    save(a.output/'results.json',dict(passed=True,purpose=__doc__,mode=a.mode,environment=env(),plan_sha256=sha(PLAN),library_sha256=sha(plan['library']),rom_sha256=sha(plan['rom']),model_bytes=ct.sizeof(Model),resident=ct.sizeof(Model)+length,phases=phases,touch=touched,closed_model_zero=closed_model_zero,scope='SHA和DLL加载在before之前；原loadrom仅观察构造器返回，源不变。系统commit有其它进程噪声；WS与capacity不由commit推断。'))
    print(a.mode)
if __name__=='__main__':main()
