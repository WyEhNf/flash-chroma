"""同场比较相同8bit ROM的GCC/Clang C99 store及固定78/80，四worker各五完整百图。"""
import ctypes as ct
from pathlib import Path
import sys
import bench_memory_rom as bench
from study_memory_rom import ROOT,read,save,sha,romlib,loadrom,U8,Model

original_setup=bench.setup
def setup(a,label):
    if label in ('ref78','ref80'):return original_setup(a,label)
    plan=read(ROOT/'experiments/memory-rom-clang-store-v1.json');path=Path(plan['old_build'])/'jshc_memory_rom.dll' if label=='gcc_store' else a.build/'jshc_memory_clang_store.dll';d=romlib(path);m,keep=loadrom(d,a.roms/'rom-0.bin')
    get=ct.windll.kernel32.GetModuleFileNameW;get.argtypes=[ct.c_void_p,ct.c_wchar_p,ct.c_uint32];buffer=ct.create_unicode_buffer(32768)
    if not get(d._handle,buffer,len(buffer)) or Path(buffer.value).resolve()!=path.resolve():raise AssertionError('实际载入模块路径不符')
    def apply(source,target,n,threads,mode):return d.jshc_mem_apply_parallel(ct.byref(m),target if mode=='inplace' else source,target,n,0,threads)
    return apply,(d,m,keep),(a.roms/'rom-0.bin').stat().st_size+ct.sizeof(Model),str(Path(buffer.value)),sha(path)

if __name__=='__main__':
    plan=ROOT/'experiments/memory-rom-clang-store-v1.json';frozen=read(plan)
    if any(sha(ROOT/n)!=v for n,v in frozen['source_sha256'].items()):raise AssertionError('冻结源码不同')
    module=Path(bench.__file__);bench.labels=lambda:['ref78','ref80','gcc_store','clang_store'];bench.setup=setup;bench.__file__=__file__;bench.main()
    output=Path(sys.argv[sys.argv.index('--output')+1]);save(output/'driver.json',dict(purpose=__doc__,plan_sha256=sha(plan),script_sha256=sha(__file__),benchmark_module_sha256=sha(module)))
