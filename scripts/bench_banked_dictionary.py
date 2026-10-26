"""只比较唯一选定4bank与78/80/原32/3B/17bit，四worker各五完整百图。"""
import ctypes as ct
import copy
from pathlib import Path
import sys
import bench_memory_rom as bench
import bench_compact_dictionary as old
from banked_dictionary_support import BankModel,banklib,loadbank
from study_memory_rom import ROOT,sha,read,save

original_setup=bench.setup

def actual(d,path):
    get=ct.windll.kernel32.GetModuleFileNameW;get.argtypes=[ct.c_void_p,ct.c_wchar_p,ct.c_uint32];buffer=ct.create_unicode_buffer(32768)
    if not get(d._handle,buffer,len(buffer)) or Path(buffer.value).resolve()!=path.resolve():raise AssertionError('实际DLL载入路径不同')

def setup(a,label):
    plan=read(ROOT/'experiments/banked-dictionary-native-v1.json')
    if label in ('ref78','ref80'):return original_setup(a,label)
    if label in ('dict32','avx2_24','avx2_17'):
        args=copy.copy(a);args.build=Path(plan['old_build']);args.roms=Path(plan['old_roms']);result=old.setup(args,label);actual(result[1][0],Path(result[3]));return result
    path=a.build/'jshc_memory_bank.dll';d=banklib(path);actual(d,path);m,keep=loadbank(d,a.roms/'rom-4.bin')
    def apply(source,target,n,threads,mode):return d.jshc_mem_apply_parallel(ct.byref(m),target if mode=='inplace' else source,target,n,1 if label=='avx2_bank' else 0,threads)
    return apply,(d,m,keep),(a.roms/'rom-4.bin').stat().st_size+ct.sizeof(BankModel),str(path),sha(path)

if __name__=='__main__':
    path=ROOT/'experiments/banked-dictionary-native-v1.json';plan=read(path)
    if any(sha(ROOT/n)!=v for n,v in plan['source_sha256'].items()) or any(sha(n)!=v for n,v in plan['input_sha256'].items()):raise AssertionError('冻结源/输入不同')
    if '--repeats' in sys.argv and int(sys.argv[sys.argv.index('--repeats')+1])!=5:raise ValueError('必须完整五轮')
    module=Path(bench.__file__);bench.labels=lambda:['ref78','ref80','dict32','avx2_24','avx2_17','avx2_bank','c99_bank'];bench.setup=setup;bench.__file__=__file__;bench.main()
    output=Path(sys.argv[sys.argv.index('--output')+1]);summary=output/'summary.json'
    if summary.exists():
        data=read(summary)
        for key,control in data['controls'].items():
            if not control['pass_']:data['tiers'][key]={str(t):None for t in (100,90,80,70,60,50)}
        data['native_plan_sha256']=sha(path);save(summary,data)
    save(output/'driver.json',dict(purpose=__doc__,plan_sha256=sha(path),script_sha256=sha(__file__),benchmark_module_sha256=sha(module),preflight='study_memory_rom.sha使用hashlib.file_digest流式预检；RSS分支未构造照片数组，峰值包括相同导入群和输入预检。'))
