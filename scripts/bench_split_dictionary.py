"""同场七角色比较M16S与冻结32/24/17字典，四worker各五完整百图。"""
import ctypes as ct
import copy
from pathlib import Path
import sys
import bench_memory_rom as bench
import bench_compact_dictionary as old
from study_memory_rom import ROOT,sha,read,save,romlib,loadrom,Model

original_setup=bench.setup

def actual_library(d,path):
    get=ct.windll.kernel32.GetModuleFileNameW;get.argtypes=[ct.c_void_p,ct.c_wchar_p,ct.c_uint32];buffer=ct.create_unicode_buffer(32768)
    if not get(d._handle,buffer,len(buffer)) or Path(buffer.value).resolve()!=path.resolve():raise AssertionError('实际载入DLL路径不同')

def setup(a,label):
    plan=read(ROOT/'experiments/split-dictionary-v1.json')
    if label in ('ref78','ref80'):return original_setup(a,label)
    if label in ('dict32','avx2_24','avx2_17'):
        args=copy.copy(a);args.build=Path(plan['old_build']);args.roms=Path(plan['old_roms']);result=old.setup(args,label);actual_library(result[1][0],Path(result[3]));return result
    path=a.build/'jshc_memory_split.dll';d=romlib(path);actual_library(d,path);m,keep=loadrom(d,a.roms/'rom-17.bin')
    def apply(source,target,n,threads,mode):return d.jshc_mem_apply_parallel(ct.byref(m),target if mode=='inplace' else source,target,n,1 if label=='avx2_split' else 0,threads)
    return apply,(d,m,keep),(a.roms/'rom-17.bin').stat().st_size+ct.sizeof(Model),str(path),sha(path)

if __name__=='__main__':
    path=ROOT/'experiments/split-dictionary-v1.json';plan=read(path)
    if any(sha(ROOT/n)!=v for n,v in plan['source_sha256'].items()) or any(sha(n)!=v for n,v in plan['input_sha256'].items()):raise AssertionError('冻结源/控制不同')
    module=Path(bench.__file__);bench.labels=lambda:['ref78','ref80','dict32','avx2_24','avx2_17','avx2_split','c99_split'];bench.setup=setup;bench.__file__=__file__;bench.main()
    output=Path(sys.argv[sys.argv.index('--output')+1]);save(output/'driver.json',dict(purpose=__doc__,plan_sha256=sha(path),script_sha256=sha(__file__),benchmark_module_sha256=sha(module)))
