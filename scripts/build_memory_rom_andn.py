"""增量构建线性ROM的原地/分离ANDN入口；字典像素对象沿用首阶段已验版本。"""
import argparse
from pathlib import Path
import shutil
import subprocess
from study_memory_rom import ROOT,sha,read,save

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base-build',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--compiler',default='E:/mingw64/bin/g++.exe');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    plan=ROOT/'experiments/memory-rom-andn-v1.json'
    if any(sha(ROOT/n)!=v for n,v in read(plan)['source_sha256'].items()):raise ValueError('冻结源码变化')
    base=read(a.base_build/'build.json');sources={};records=[];out=a.output
    if sha(a.compiler)!=base['compiler_sha256']:raise ValueError('编译器不同')
    def run(cmd):
        r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace');records.append(dict(command=cmd,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));save(out/'commands.json',records)
        if r.returncode:raise RuntimeError(r.stderr)
    common=['-O3','-DNDEBUG','-fopenmp','-fstack-usage','-std=c++17']
    # Windows导出宏未变；重新构建C99对象让新头文件身份明确。
    cc=str(Path(a.compiler).with_name('gcc.exe'));csource=ROOT/'experiments/memory-rom/memory_rom.c';sources[str(csource)]=sha(csource)
    run([cc,'-std=c99','-pedantic-errors','-O3','-fstack-usage','-Wall','-Wextra','-c',str(csource),'-o',str(out/'memory_c.o')])
    run([cc,'-shared',str(out/'memory_c.o'),'-o',str(out/'jshc_memory_c99.dll')])
    objects=[out/'memory_c.o']
    source=ROOT/'experiments/memory-rom/memory_parallel.cpp';sources[str(source)]=sha(source)
    run([a.compiler,*common,'-DJSHC_MEM_AVX2=1','-DJSHC_MEM_ANDN=1','-c',str(source),'-o',str(out/'memory_parallel.o')]);objects.append(out/'memory_parallel.o')
    for bits in (0,4,6,8,10):
        obj=a.base_build/f'memory_avx2_{bits}.o';shutil.copyfile(obj,out/obj.name);objects.append(out/obj.name)
    for mode in ('inplace','outplace'):
        source=ROOT/'experiments/skylake-andn-split-runtime'/('andn_'+mode)/'channel_avx2.cpp';sources[str(source)]=sha(source)
        text=source.read_text(encoding='utf-8').replace('#include "../suffix_cache.hpp"','#include <cstdint>')
        text=text.replace('namespace jshc_channel {','namespace jshc_mem_andn {').replace('const uint32_t* table','const uint8_t* table')
        generated=out/f'andn_{mode}.cpp';generated.write_text(text,encoding='utf-8');sources[str(generated)]=sha(generated)
        obj=out/f'andn_{mode}.o';run([a.compiler,*common,'-mavx2','-mbmi','-mtune=skylake','-ffp-contract=off','-c',str(generated),'-o',str(obj)]);objects.append(obj)
    run([a.compiler,'-shared','-O3','-fopenmp',*[str(x) for x in objects],'-o',str(out/'jshc_memory_rom.dll')])
    for name in ('jshc_memory_ref78.dll','libgcc_s_seh-1.dll','libstdc++-6.dll','libwinpthread-1.dll','libgomp-1.dll'):shutil.copyfile(a.base_build/name,out/name)
    sources[str(ROOT/'experiments/memory-rom/memory_rom.h')]=sha(ROOT/'experiments/memory-rom/memory_rom.h')
    save(out/'build.json',dict(purpose=__doc__,plan_sha256=sha(plan),base_build=dict(path=str(a.base_build),sha256=sha(a.base_build/'build.json')),sources=sources,commands=records,compiler_sha256=sha(a.compiler),libraries={p.name:sha(p) for p in out.glob('*.dll')},reused_object_sha256={p.name:sha(p) for p in objects if p.name.startswith('memory_avx2_')}))
    print(sha(out/'build.json'))
if __name__=='__main__':main()
