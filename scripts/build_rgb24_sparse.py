"""编译独立RGB24稀疏句柄及仅供保护页探针使用的AVX2库。"""
import argparse
from pathlib import Path
import shutil
import subprocess
from study_memory_rom import ROOT,read,save,sha

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--compiler',default='E:/mingw64/bin/g++.exe');a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    plan=ROOT/'experiments/rgb24-sparse-v1.json';frozen=read(plan)
    if any(sha(ROOT/n)!=v for n,v in frozen['source_sha256'].items()):raise ValueError('冻结源码不同')
    core=a.data_root/'build-channel-research/libjshc_core.a';baseline=a.data_root/'artifacts/channel-native-specialized-v1/jshc_channel_specialized.dll'
    for label,path in [('core',core),('specialized',baseline)]:
        if sha(path)!=frozen['inputs'][label]['sha256']:raise ValueError('冻结输入不同：'+label)
    directory=ROOT/'experiments/rgb24-sparse-runtime';flags=['-O3','-DNDEBUG','-std=c++17','-fopenmp','-fstack-usage','-I'+str(ROOT/'experiments/channel-runtime'),'-I'+str(ROOT/'cpp/include')];commands=[]
    commands.append([a.compiler,*flags,'-DJSHC_CC_HAVE_AVX2=1','-c',str(directory/'channel_runtime.cpp'),'-o',str(out/'runtime.o')])
    commands.append([a.compiler,*flags,'-mavx2','-ffp-contract=off','-c',str(directory/'channel_avx2.cpp'),'-o',str(out/'avx2.o')])
    commands.append([a.compiler,'-O3','-fopenmp','-shared',str(out/'runtime.o'),str(out/'avx2.o'),str(core),'-lwinpthread','-o',str(out/'jshc_compact_sparse.dll')])
    commands.append([a.compiler,*flags,'-mavx2','-ffp-contract=off','-DJSHC_RGB24_PROBE=1','-shared',str(directory/'channel_avx2.cpp'),'-o',str(out/'rgb24_probe.dll')])
    records=[]
    for command in commands:
        r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace');records.append(dict(command=command,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));save(out/'commands.json',records)
        if r.returncode:raise RuntimeError(r.stderr)
    for name in ('jshc_channel_specialized.dll','libgcc_s_seh-1.dll','libstdc++-6.dll','libwinpthread-1.dll','libgomp-1.dll'):shutil.copyfile(baseline.parent/name,out/name)
    save(out/'build.json',dict(purpose=__doc__,plan_sha256=sha(plan),source_sha256=frozen['source_sha256'],inputs=frozen['inputs'],compiler_sha256=sha(a.compiler),commands=records,libraries={p.name:sha(p) for p in out.glob('*.dll')},abi=1,revisions=dict(specialized=2,compact=1002),scope='RGB24 AVX2只编译像素TU；dispatcher baseline ISA，节点owned storage含guardword；probe库不用于性能。'))
    print(out)
if __name__=='__main__':main()
