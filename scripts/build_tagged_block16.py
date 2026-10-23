"""单进程构建唯一M16T C99与普通条件AVX2，保留旧32/3B控制。"""
import argparse
from pathlib import Path
import shutil
import subprocess
from study_memory_rom import ROOT,read,save,sha
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();planpath=ROOT/'experiments/tagged-block16-native-v1.json';plan=read(planpath)
    if any(sha(ROOT/n)!=v for n,v in plan['source_sha256'].items()):raise AssertionError('冻结源变化')
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);base=ROOT/'experiments/tagged-block16-runtime';gcc='E:/mingw64/bin/gcc.exe';gxx='E:/mingw64/bin/g++.exe';commands=[[gcc,'-O3','-std=c99','-pedantic-errors','-Wall','-Wextra','-fstack-usage','-c',str(base/'memory_rom.c'),'-o',str(out/'memory_c.o')],[gcc,'-shared',str(out/'memory_c.o'),'-o',str(out/'jshc_tag16_c99.dll')]]
    for name,extra in [('memory_parallel',['-DJSHC_MEM_AVX2=1']),('channel_avx2_tag',['-mavx2','-mtune=skylake','-ffp-contract=off'])]:commands.append([gxx,'-O3','-DNDEBUG','-std=c++17','-fopenmp','-fstack-usage',*extra,'-c',str(base/(name+'.cpp')),'-o',str(out/(name+'.o'))])
    commands.append([gxx,'-shared','-O3','-fopenmp',*[str(out/(n+'.o')) for n in ('memory_c','memory_parallel','channel_avx2_tag')],'-lwinpthread','-o',str(out/'jshc_memory_tag16.dll')]);records=[]
    for command in commands:
        r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace');records.append(dict(command=command,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));save(out/'commands.json',records)
        if r.returncode:raise RuntimeError(r.stderr)
    for name in ('libgcc_s_seh-1.dll','libstdc++-6.dll','libwinpthread-1.dll','libgomp-1.dll'):shutil.copyfile(Path(gxx).parent/name,out/name)
    reference=Path(plan['reference78']['path'])
    if sha(reference)!=plan['reference78']['sha256']:raise AssertionError('78身份不同')
    shutil.copyfile(reference,out/'jshc_memory_ref78.dll');save(out/'build.json',dict(purpose=__doc__,plan_sha256=sha(planpath),source_sha256=plan['source_sha256'],compiler_sha256={n:sha(n) for n in (gcc,gxx)},commands=records,libraries={x.name:sha(x) for x in out.glob('*.dll')},scope='C99零堆；桌面像素仅AVX2，无masked gather/native/AVX512，旧32/3B及fast控制不重编译。'))
    print(out)
if __name__=='__main__':main()
