"""单进程构建M16B C99与AVX2桌面适配器；不重编译旧三个字典控制。"""
import argparse
from pathlib import Path
import shutil
import subprocess
from study_memory_rom import ROOT,sha,save,read

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();plan=read(ROOT/'experiments/banked-dictionary-native-v1.json')
    if any(sha(ROOT/n)!=v for n,v in plan['source_sha256'].items()):raise ValueError('冻结源码变化')
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);base=ROOT/'experiments/banked-dictionary-runtime';gcc='E:/mingw64/bin/gcc.exe';gxx='E:/mingw64/bin/g++.exe';commands=[]
    commands.append([gcc,'-O3','-std=c99','-pedantic-errors','-Wall','-Wextra','-fstack-usage','-c',str(base/'memory_rom.c'),'-o',str(out/'memory_c.o')])
    commands.append([gcc,'-shared',str(out/'memory_c.o'),'-o',str(out/'jshc_bank_c99.dll')])
    for name,extra in [('memory_parallel',['-DJSHC_MEM_AVX2=1']),('channel_avx2_bank',['-mavx2','-mtune=skylake','-ffp-contract=off'])]:
        commands.append([gxx,'-O3','-DNDEBUG','-std=c++17','-fopenmp','-fstack-usage',*extra,'-c',str(base/(name+'.cpp')),'-o',str(out/(name+'.o'))])
    commands.append([gxx,'-shared','-O3','-fopenmp',*[str(out/(n+'.o')) for n in ('memory_c','memory_parallel','channel_avx2_bank')],'-lwinpthread','-o',str(out/'jshc_memory_bank.dll')]);records=[]
    for command in commands:
        r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace');records.append(dict(command=command,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));save(out/'commands.json',records)
        if r.returncode:raise RuntimeError(r.stderr)
    for name in ('libgcc_s_seh-1.dll','libstdc++-6.dll','libwinpthread-1.dll','libgomp-1.dll'):shutil.copyfile(Path(gxx).parent/name,out/name)
    reference=Path(plan['reference78']['path'])
    if sha(reference)!=plan['reference78']['sha256']:raise ValueError('78参考不同')
    shutil.copyfile(reference,out/'jshc_memory_ref78.dll')
    save(out/'build.json',dict(purpose=__doc__,source_sha256=plan['source_sha256'],plan_sha256=sha(ROOT/'experiments/banked-dictionary-native-v1.json'),compiler_sha256={n:sha(n) for n in (gcc,gxx)},commands=records,libraries={x.name:sha(x) for x in out.glob('*.dll')},scope='严格C99无堆核心；仅桌面像素TU启用AVX2，适配器OpenMP。旧32/24/17控制直接载入冻结原DLL，不重新构建。'))
    print(out)
if __name__=='__main__':main()
