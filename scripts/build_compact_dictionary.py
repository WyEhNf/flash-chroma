"""单编译进程构建M16P零堆C99及两个固定索引宽度AVX2桌面后端。"""
import argparse
from pathlib import Path
import shutil
import subprocess
from study_memory_rom import ROOT,read,save,sha

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--compiler',default='E:/mingw64/bin/g++.exe');p.add_argument('--c-compiler',default='E:/mingw64/bin/gcc.exe');a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    plan=ROOT/'experiments/compact-dictionary-v1.json';frozen=read(plan)
    if any(sha(ROOT/n)!=v for n,v in frozen['source_sha256'].items()):raise ValueError('冻结源变化')
    base=ROOT/'experiments/compact-dictionary-runtime';commands=[];objects=[]
    flags=['-O3','-DNDEBUG','-std=c++17','-fopenmp','-fstack-usage']
    cobj=out/'memory_c.o';commands.append([a.c_compiler,'-O3','-std=c99','-pedantic-errors','-Wall','-Wextra','-fstack-usage','-c',str(base/'memory_rom.c'),'-o',str(cobj)])
    commands.append([a.c_compiler,'-shared',str(cobj),'-o',str(out/'jshc_dict_c99.dll')]);objects.append(cobj)
    for name,extra in [('memory_parallel',['-DJSHC_MEM_AVX2=1']),('channel_avx2_17',['-mavx2','-mtune=skylake','-ffp-contract=off']),('channel_avx2_24',['-mavx2','-mtune=skylake','-ffp-contract=off'])]:
        obj=out/(name+'.o');commands.append([a.compiler,*flags,*extra,'-c',str(base/(name+'.cpp')),'-o',str(obj)]);objects.append(obj)
    commands.append([a.compiler,'-shared','-O3','-fopenmp',*[str(x) for x in objects],'-lwinpthread','-o',str(out/'jshc_memory_rom.dll')]);records=[]
    for command in commands:
        r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace');records.append(dict(command=command,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));save(out/'commands.json',records)
        if r.returncode:raise RuntimeError(r.stderr)
    for name in ('libgcc_s_seh-1.dll','libstdc++-6.dll','libwinpthread-1.dll','libgomp-1.dll'):shutil.copyfile(Path(a.compiler).parent/name,out/name)
    reference=Path(frozen['reference78']['path'])
    if sha(reference)!=frozen['reference78']['sha256']:raise ValueError('78参考身份变化')
    shutil.copyfile(reference,out/'jshc_memory_ref78.dll')
    save(out/'build.json',dict(purpose=__doc__,source_sha256=frozen['source_sha256'],plan_sha256=sha(plan),compiler_sha256=sha(a.compiler),c_compiler_sha256=sha(a.c_compiler),commands=records,libraries={x.name:sha(x) for x in out.glob('*.dll')},scope='C99库无C++/OpenMP/AVX2依赖；桌面后端仅两个像素TU启用AVX2。旧ROM/快基线不重编译。'))
    print(out)
if __name__=='__main__':main()
