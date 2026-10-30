"""单进程构建独立7bit C99及AVX2 ROM；原78外循环只替换随机ID读取。"""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import subprocess
from profile_palette_bitpack import sha,save

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-build',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    cc='E:/mingw64/bin/gcc.exe';cxx='E:/mingw64/bin/g++.exe'
    core=ROOT/'experiments/palette-bitpack'
    original=ROOT/'experiments/skylake-andn-split-runtime/channel_avx2.cpp'
    inputs=[core/'memory_bitpack.c',core/'parallel.cpp',ROOT/'experiments/memory-rom/memory_rom.c',
            ROOT/'experiments/memory-rom/memory_rom.h',original,Path(__file__)]
    frozen={str(path.relative_to(ROOT)):sha(path) for path in inputs}
    save(args.output/'frozen-source.json',frozen)
    records=[]

    def run(command):
        result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',errors='replace')
        records.append(dict(command=command,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr))
        save(args.output/'commands.json',records);result.check_returncode()

    source=original.read_text(encoding='utf-8').replace('#include "suffix_cache.hpp"','#include <cstdint>')
    source=source.replace('namespace jshc_channel {','namespace jshc_pal7 {').replace('const uint32_t* table','const uint8_t* table')
    helper='''inline __attribute__((always_inline)) uint32_t lookup_id(const uint8_t* table,uint32_t code) {
  const uint32_t bit=code*7u;uint16_t word;std::memcpy(&word,table+(bit>>3),2);
  return (uint32_t(word)>>(bit&7u))&127u;
}
'''
    source=source.replace('namespace {','namespace {\n'+helper,1)
    assert 'reinterpret_cast<const uint8_t*>(table)[code]' in source and 'return bytes[code&0xffffff];' in source
    source=source.replace('reinterpret_cast<const uint8_t*>(table)[code]','lookup_id(table,code)')
    source=source.replace('return bytes[code&0xffffff];','return lookup_id(bytes,code&0xffffff);')
    generated=args.output/'palette_avx2.cpp';generated.write_text(source,encoding='utf-8')
    run([cc,'-std=c99','-pedantic-errors','-O3','-Wall','-Wextra','-fstack-usage','-c',str(core/'memory_bitpack.c'),'-o',str(args.output/'core.o')])
    run([cc,'-shared',str(args.output/'core.o'),'-o',str(args.output/'jshc_memory_c99.dll')])
    run([cxx,'-std=c++17','-O3','-fopenmp','-fstack-usage','-c',str(core/'parallel.cpp'),'-o',str(args.output/'parallel.o')])
    run([cxx,'-std=c++17','-O3','-mavx2','-mtune=skylake','-ffp-contract=off','-fstack-usage','-c',str(generated),'-o',str(args.output/'avx2.o')])
    run([cxx,'-shared','-O3','-fopenmp',*[str(args.output/name) for name in ['core.o','parallel.o','avx2.o']],'-o',str(args.output/'jshc_memory_rom.dll')])
    for name in ['libgcc_s_seh-1.dll','libstdc++-6.dll','libwinpthread-1.dll','libgomp-1.dll','jshc_memory_ref78.dll']:
        shutil.copyfile(args.base_build/name,args.output/name)
    assert all(sha(ROOT/name)==value for name,value in frozen.items())
    save(args.output/'build.json',dict(purpose=__doc__,source_sha256=frozen,generated_sha256=sha(generated),commands=records,
        compiler_sha256=sha(cxx),c_compiler_sha256=sha(cc),libraries={path.name:sha(path) for path in args.output.glob('*.dll')},
        scope='C99核心无ISA；仅AVX2 TU使用-mavx2，无AVX512/BMI；生成代码借用78外循环与边界'))
    print(sha(args.output/'jshc_memory_rom.dll'))


if __name__=='__main__':main()
