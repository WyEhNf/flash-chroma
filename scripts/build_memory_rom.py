"""构建C99借用ROM、固定块字典AVX2及原修订78对照；一次只使用一个编译进程。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(path,data):Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--data-root',type=Path,required=True)
    p.add_argument('--compiler',default='E:/mingw64/bin/g++.exe')
    p.add_argument('--c-compiler',default='E:/mingw64/bin/gcc.exe')
    a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    core=a.data_root/'build-channel-research/libjshc_core.a'
    if sha(core)!='64abb6eb38d929dc81c07b5a34be1408bbadecfee76fd31801cdfe94a0916ef6':raise ValueError('静态核心身份不同')
    common=['-O3','-DNDEBUG','-fopenmp','-fstack-usage','-std=c++17','-I'+str(ROOT/'experiments/channel-runtime'),'-I'+str(ROOT/'cpp/include')]
    records=[];sources={};objects=[]
    def run(command):
        r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
        records.append(dict(command=command,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
        save(out/'commands.json',records)
        if r.returncode:raise RuntimeError(r.stderr)
    def compile(source,name,flags=(),compiler=None):
        source=Path(source);sources[str(source)]=sha(source);obj=out/(name+'.o')
        run([compiler or a.compiler,*common,*flags,'-c',str(source),'-o',str(obj)])
        return obj
    runtime=ROOT/'experiments/skylake-andn-split-runtime'
    baseline=[]
    for name,source,flags in [
        ('runtime',runtime/'channel_runtime.cpp',['-DJSHC_CC_HAVE_AVX2=1']),
        ('outplace',runtime/'outplace_bench.cpp',[]),
        ('linear',runtime/'channel_avx2.cpp',['-mavx2','-mtune=skylake','-ffp-contract=off']),
        ('andn_in',runtime/'andn_inplace/channel_avx2.cpp',['-mavx2','-mbmi','-mtune=skylake','-ffp-contract=off']),
        ('andn_out',runtime/'andn_outplace/channel_avx2.cpp',['-mavx2','-mbmi','-mtune=skylake','-ffp-contract=off']),
        ('exception',ROOT/'experiments/skylake-exception-runtime/channel_avx2.cpp',['-mavx2','-mtune=skylake','-ffp-contract=off']),
        ('domain',ROOT/'experiments/skylake-domain-isolated-runtime/channel_avx2.cpp',['-mavx2','-mtune=skylake','-ffp-contract=off']),
        ('suffix',ROOT/'experiments/skylake-suffix-cache-runtime/channel_avx2.cpp',['-mavx2','-mtune=skylake','-ffp-contract=off'])]:
        baseline.append(compile(source,'ref_'+name,flags))
    ref=out/'jshc_memory_ref78.dll'
    run([a.compiler,'-shared','-O3','-fopenmp',*[str(x) for x in baseline],str(core),'-lwinpthread','-o',str(ref)])
    csource=ROOT/'experiments/memory-rom/memory_rom.c'
    cobj=out/'memory_c.o';sources[str(csource)]=sha(csource)
    run([a.c_compiler,'-std=c99','-pedantic-errors','-O3','-fstack-usage','-Wall','-Wextra','-c',str(csource),'-o',str(cobj)])
    # 真正独立C99库：没有C++、OpenMP、AVX2或核心依赖。
    run([a.c_compiler,'-shared',str(cobj),'-o',str(out/'jshc_memory_c99.dll')])
    objects=[cobj,compile(ROOT/'experiments/memory-rom/memory_parallel.cpp','memory_parallel',['-DJSHC_MEM_AVX2=1'])]
    original=(runtime/'channel_avx2.cpp').read_text(encoding='utf-8')
    # 保留78普通线性循环与边界；只有ID函数及命名空间按固定块宽专门化。
    for bits in (0,4,6,8,10):
        text=original.replace('#include "suffix_cache.hpp"','#include <cstdint>')
        text=text.replace('namespace jshc_channel {','namespace jshc_mem_'+str(bits)+' {')
        text=text.replace('const uint32_t* table','const uint8_t* table')
        helper='''inline __attribute__((always_inline)) uint32_t lookup_id(const uint8_t* table,uint32_t code) {
'''
        if bits:
            helper+=f'  uint32_t offset;std::memcpy(&offset,table+4*(code>>{bits}),4);return table[offset+(code&{(1<<bits)-1})];\n'
        else:helper+='  return table[code];\n'
        helper+='}\n'
        text=text.replace('namespace {','namespace {\n'+helper,1)
        text=text.replace('reinterpret_cast<const uint8_t*>(table)[code]','lookup_id(table,code)')
        text=text.replace('return bytes[code&0xffffff];','return lookup_id(bytes,code&0xffffff);')
        source=out/f'memory_avx2_{bits}.cpp';source.write_text(text,encoding='utf-8')
        objects.append(compile(source,'memory_avx2_'+str(bits),['-mavx2','-mtune=skylake','-ffp-contract=off']))
    lib=out/'jshc_memory_rom.dll'
    run([a.compiler,'-shared','-O3','-fopenmp',*[str(x) for x in objects],'-o',str(lib)])
    for name in ('libgcc_s_seh-1.dll','libstdc++-6.dll','libwinpthread-1.dll','libgomp-1.dll'):
        source=Path(a.compiler).parent/name;shutil.copyfile(source,out/name)
    sources[str(ROOT/'experiments/memory-rom/memory_rom.h')]=sha(ROOT/'experiments/memory-rom/memory_rom.h')
    save(out/'build.json',dict(purpose=__doc__,sources=sources,compiler_sha256=sha(a.compiler),
        c_compiler_sha256=sha(a.c_compiler),static_core_sha256=sha(core),commands=records,
        libraries={x.name:sha(x) for x in out.glob('*.dll')},compiler=subprocess.check_output([a.compiler,'--version'],text=True)))
    print(json.dumps({'output':str(out),'build_sha256':sha(out/'build.json')},ensure_ascii=False))
if __name__=='__main__':main()
