"""固定8像素C99组内重叠写候选；不改ANDN或字典AVX2像素对象。"""
import argparse
from pathlib import Path
import shutil
import subprocess
from study_memory_rom import ROOT,sha,read,save

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base-build',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--compiler',default='E:/mingw64/bin/g++.exe');a=p.parse_args();out=a.output;out.mkdir(parents=True,exist_ok=False)
    plan=ROOT/'experiments/memory-rom-store-v1.json'
    if any(sha(ROOT/n)!=v for n,v in read(plan)['source_sha256'].items()):raise ValueError('冻结源码变化')
    cc=str(Path(a.compiler).with_name('gcc.exe'));records=[];sources={}
    def run(cmd):
        r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace');records.append(dict(command=cmd,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));save(out/'commands.json',records)
        if r.returncode:raise RuntimeError(r.stderr)
    objs=[]
    for source,name in ((ROOT/'experiments/memory-rom/memory_rom.c','memory_c'),(ROOT/'experiments/memory-rom/memory_rom_store.c','memory_store')):
        sources[str(source)]=sha(source);obj=out/(name+'.o');run([cc,'-std=c99','-pedantic-errors','-O3','-fstack-usage','-Wall','-Wextra','-c',str(source),'-o',str(obj)]);objs.append(obj)
    run([cc,'-shared',*[str(x) for x in objs],'-o',str(out/'jshc_memory_c99.dll')])
    source=ROOT/'experiments/memory-rom/memory_parallel.cpp';sources[str(source)]=sha(source)
    run([a.compiler,'-O3','-DNDEBUG','-std=c++17','-fopenmp','-fstack-usage','-DJSHC_MEM_AVX2=1','-DJSHC_MEM_ANDN=1','-Djshc_mem_apply=jshc_mem_apply_store','-c',str(source),'-o',str(out/'memory_parallel.o')]);objs.append(out/'memory_parallel.o')
    reused={}
    for path in list(a.base_build.glob('memory_avx2_*.o'))+list(a.base_build.glob('andn_*.o')):
        shutil.copyfile(path,out/path.name);objs.append(out/path.name);reused[path.name]=sha(path)
    run([a.compiler,'-shared','-O3','-fopenmp',*[str(x) for x in objs],'-o',str(out/'jshc_memory_rom.dll')])
    for name in ('jshc_memory_ref78.dll','libgcc_s_seh-1.dll','libstdc++-6.dll','libwinpthread-1.dll','libgomp-1.dll'):shutil.copyfile(a.base_build/name,out/name)
    save(out/'build.json',dict(purpose=__doc__,plan_sha256=sha(plan),base_build_sha256=sha(a.base_build/'build.json'),sources=sources,reused_objects=reused,commands=records,compiler_sha256=sha(a.compiler),libraries={p.name:sha(p) for p in out.glob('*.dll')}))
    print(sha(out/'build.json'))
if __name__=='__main__':main()
