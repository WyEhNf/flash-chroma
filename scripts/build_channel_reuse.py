"""单独构建地址复用候选；保留既有CMake/已验收运行时源码与二进制。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve()
    if out.exists():raise ValueError('不覆盖冻结构建')
    compiler=Path('E:/mingw64/bin/g++.exe');core=ROOT/'build-channel-research/libjshc_core.a'
    deps=ROOT/'artifacts/channel-native-runtime-v3'
    sources=['scripts/build_channel_reuse.py','experiments/channel-runtime-reuse/channel_avx2.cpp',
        'experiments/channel-runtime/channel_runtime.cpp','experiments/channel-runtime/channel_runtime.h',
        'experiments/channel-runtime/channel_views.hpp','cpp/include/jshc/lut.hpp']
    hashes={name:digest(ROOT/name) for name in sources}
    core_sha=digest(core);out.mkdir(parents=True)
    common=[str(compiler),'-DJSHC_CC_HAVE_AVX2=1','-Djshc_channel_research_EXPORTS',
        '-I'+str(ROOT/'experiments/channel-runtime'),'-I'+str(ROOT/'cpp/include'),
        '-O3','-DNDEBUG','-std=c++17','-fopenmp']
    commands=[common+['-c',str(ROOT/'experiments/channel-runtime/channel_runtime.cpp'),'-o',str(out/'runtime.o')],
        common+['-mavx2','-c',str(ROOT/'experiments/channel-runtime-reuse/channel_avx2.cpp'),'-o',str(out/'avx2.o')],
        [str(compiler),'-O3','-DNDEBUG','-fopenmp','-shared','-o',str(out/'jshc_channel_reuse.dll'),
         str(out/'runtime.o'),str(out/'avx2.o'),str(core),'-lwinpthread']]
    logs=[]
    for cmd in commands:
        result=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
        logs.append({'command':cmd,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
        if result.returncode:
            (out/'failed-build.json').write_text(json.dumps(logs,ensure_ascii=False,indent=2),encoding='utf-8')
            raise RuntimeError(result.stderr)
    dlls=['libgcc_s_seh-1.dll','libgomp-1.dll','libstdc++-6.dll','libwinpthread-1.dll']
    for name in dlls:shutil.copyfile(deps/name,out/name)
    if any(digest(ROOT/n)!=h for n,h in hashes.items()) or digest(core)!=core_sha:raise ValueError('构建输入变化')
    with zipfile.ZipFile(out/'measured-source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for n in hashes:z.write(ROOT/n,n)
    version=subprocess.check_output([str(compiler),'--version'],text=True,encoding='utf-8')
    result={'purpose':'仅构建一个同包内点地址复用AVX2候选，未执行正确性或性能测试',
        'compiler':version,'compiler_sha256':digest(compiler),'source_sha256':hashes,
        'static_core_path':str(core),'static_core_sha256':core_sha,'commands':logs,
        'binary_sha256':{n:digest(out/n) for n in ['jshc_channel_reuse.dll',*dlls]},
        'abi':1,'revision':2,'revision_note':'ABI/revision复用既有标量壳；候选身份由独立DLL文件名及SHA明确区分。',
        'scope':'未改原CMake/原运行时；仅本候选TU -mavx2，其他编译单元保持运行时CPUID+OS派发。复用已验收GCC15.2 Release静态核心，链接其实际字节SHA。'}
    (out/'build.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'library_sha256':result['binary_sha256']['jshc_channel_reuse.dll'],'build_sha256':digest(out/'build.json')},ensure_ascii=False))

if __name__=='__main__':main()
