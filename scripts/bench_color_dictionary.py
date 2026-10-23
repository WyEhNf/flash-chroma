"""唯一RGB32块版本与同场78/80/旧3B比较；四worker各五完整百图。"""
import ctypes as ct
import copy
from pathlib import Path
import sys
import bench_memory_rom as bench
import bench_compact_dictionary as old
from color_dictionary_support import ColorModel,colorlib,loadcolor
from study_memory_rom import ROOT,sha,read,save

original_setup=bench.setup

def actual(d,path):
    get=ct.windll.kernel32.GetModuleFileNameW;get.argtypes=[ct.c_void_p,ct.c_wchar_p,ct.c_uint32];buffer=ct.create_unicode_buffer(32768)
    if not get(d._handle,buffer,len(buffer)) or Path(buffer.value).resolve()!=path.resolve():raise AssertionError('实际DLL载入路径不同')

def setup(a,label):
    plan=read(ROOT/'experiments/color-dictionary-v1.json')
    if label in ('ref78','ref80'):
        result=original_setup(a,label);actual(result[1][0],Path(result[3]));return result
    if label=='avx2_24':
        args=copy.copy(a);args.build=Path(plan['old_build']);args.roms=Path(plan['old_roms']);result=old.setup(args,label);actual(result[1][0],Path(result[3]));return result
    path=a.build/'jshc_memory_color_dict.dll';d=colorlib(path);actual(d,path);m,keep=loadcolor(d,a.roms/'rom-24.bin')
    def apply(source,target,n,threads,mode):return d.jshc_mem_apply_parallel(ct.byref(m),target if mode=='inplace' else source,target,n,1 if label=='avx2_color' else 0,threads)
    return apply,(d,m,keep),(a.roms/'rom-24.bin').stat().st_size+ct.sizeof(ColorModel),str(path),sha(path)

if __name__=='__main__':
    path=ROOT/'experiments/color-dictionary-v1.json';plan=read(path)
    if any(sha(ROOT/n)!=v for n,v in plan['source_sha256'].items()) or any(sha(n)!=v for n,v in plan['input_sha256'].items()):raise AssertionError('冻结源/输入不同')
    if '--repeats' in sys.argv and int(sys.argv[sys.argv.index('--repeats')+1])!=5:raise ValueError('必须完整五轮')
    module=Path(bench.__file__);bench.labels=lambda:['ref78','ref80','avx2_24','avx2_color','c99_color'];bench.setup=setup;bench.__file__=__file__;bench.main()
    output=Path(sys.argv[sys.argv.index('--output')+1]);summary=output/'summary.json'
    if summary.exists():
        data=read(summary)
        for key,control in data['controls'].items():
            if not control['pass_']:data['tiers'][key]={str(t):None for t in (100,90,80,70,60,50)}
        data['native_plan_sha256']=sha(path);save(summary,data)
    save(output/'driver.json',dict(purpose=__doc__,plan_sha256=sha(path),script_sha256=sha(__file__),benchmark_module_sha256=sha(module),preflight='file_digest流式输入预检；独立RSS进程不构造照片数组，包含Python/NumPy/库/导入基线。C99角色使用桌面OMP适配器，不冒充纯C99 DLL四线程性能。'))
