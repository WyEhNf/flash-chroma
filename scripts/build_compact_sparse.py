"""构建通用冻结稀疏句柄，逐字节复用原specialized AVX2对象。"""
import argparse
from pathlib import Path
import shutil
import subprocess
from study_memory_rom import ROOT,sha,read,save

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--compiler',default='E:/mingw64/bin/g++.exe');a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    plan=ROOT/'experiments/compact-sparse-v1.json'
    if any(sha(ROOT/n)!=v for n,v in read(plan)['source_sha256'].items()):raise ValueError('冻结源码不同')
    core=a.data_root/'build-channel-research/libjshc_core.a';obj=a.data_root/'artifacts/channel-native-specialized-v1/avx2.o';baseline=a.data_root/'artifacts/channel-native-specialized-v1/jshc_channel_specialized.dll'
    for label,path in [('core',core),('avx2_object',obj),('specialized',baseline)]:
        if sha(path)!=read(plan)['inputs'][label]['sha256']:raise ValueError('冻结输入不同：'+label)
    source=ROOT/'experiments/compact-sparse-runtime/channel_runtime.cpp';records=[]
    commands=[[a.compiler,'-O3','-DNDEBUG','-std=c++17','-fopenmp','-fstack-usage','-DJSHC_CC_HAVE_AVX2=1','-I'+str(ROOT/'experiments/channel-runtime'),'-I'+str(ROOT/'cpp/include'),'-c',str(source),'-o',str(out/'runtime.o')],
        [a.compiler,'-O3','-fopenmp','-shared',str(out/'runtime.o'),str(obj),str(core),'-lwinpthread','-o',str(out/'jshc_compact_sparse.dll')]]
    for cmd in commands:
        r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace');records.append(dict(command=cmd,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));save(out/'commands.json',records)
        if r.returncode:raise RuntimeError(r.stderr)
    for name in ('jshc_channel_specialized.dll','libgcc_s_seh-1.dll','libstdc++-6.dll','libwinpthread-1.dll','libgomp-1.dll'):shutil.copyfile(baseline.parent/name,out/name)
    save(out/'build.json',dict(purpose=__doc__,plan_sha256=sha(plan),source_sha256=read(plan)['source_sha256'],inputs=read(plan)['inputs'],compiler_sha256=sha(a.compiler),commands=records,libraries={p.name:sha(p) for p in out.glob('*.dll')},abi=1,revisions=dict(specialized=2,compact=1001),scope='只编译baseline ISA的C++17 dispatcher；原specialized AVX2对象原字节链接，没有像素TU改动。'))
    print(sha(out/'build.json'))
if __name__=='__main__':main()
