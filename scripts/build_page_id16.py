"""单版P4核：Clang严格C99 generic，GCC15.2可选AVX2/OMP，不编译旧库。"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import time
from page_id16_common import ROOT,PLAN,checked_plan,sha,save
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();plan=checked_plan();a.output.mkdir(parents=True,exist_ok=False)
    source=ROOT/'experiments/page-id16-runtime';clang=plan['tools']['clang'];gcc=plan['tools']['gcc'];gpp=plan['tools']['gpp'];rows=[]
    def run(args):
        started=time.perf_counter();value=subprocess.run([str(x) for x in args],cwd=ROOT,text=True,capture_output=True);rows.append(dict(command=list(map(str,args)),returncode=value.returncode,stdout=value.stdout,stderr=value.stderr,seconds=time.perf_counter()-started));save(a.output/'commands.json',rows)
        if value.returncode:raise RuntimeError('单版构建失败，原件STOP不重试')
        return value.stdout
    versions={name:run([value,'--version']) for name,value in plan['tools'].items()}
    common=['-O3','-Wall','-Wextra','-ffp-contract=off','-fstack-usage']
    run([clang,'--target=x86_64-w64-windows-gnu','--sysroot=E:/mingw64','-isystem','E:/mingw64/x86_64-w64-mingw32/include','-std=c99','-pedantic-errors',*common,'-march=x86-64','-mtune=generic','-mno-avx','-mno-avx2','-mno-avx512f','-c',source/'page_id16.c','-o',a.output/'page_core.o'])
    run([gpp,'-std=c++17',*common,'-march=x86-64','-mtune=generic','-mno-avx','-mno-avx2','-mno-avx512f','-fopenmp','-c',source/'page_parallel.cpp','-o',a.output/'page_parallel.o'])
    run([gpp,'-std=c++17',*common,'-mavx2','-mno-avx512f','-mtune=skylake','-c',source/'page_avx2.cpp','-o',a.output/'page_avx2.o'])
    run([gcc,'-shared',a.output/'page_core.o','-o',a.output/'jshc_page_id16_c99.dll'])
    run([gpp,'-shared','-fopenmp',a.output/'page_core.o',a.output/'page_parallel.o',a.output/'page_avx2.o','-o',a.output/'jshc_page_id16.dll'])
    for name in ('libgcc_s_seh-1.dll','libgomp-1.dll','libstdc++-6.dll','libwinpthread-1.dll'):shutil.copyfile(Path(plan['dependency_dir'])/name,a.output/name)
    save(a.output/'build.json',dict(purpose=__doc__,plan_sha256=sha(PLAN),versions=versions,source_sha256={name:value for name,value in plan['source_sha256'].items() if name.startswith('experiments/page-id16-runtime/')},outputs={path.name:dict(bytes=path.stat().st_size,sha256=sha(path)) for path in a.output.iterdir() if path.is_file() and path.name not in ('commands.json','build.json')},stack_usage={path.name:path.read_text(encoding='utf-8') for path in a.output.glob('*.su')},scope='所有命令串行一次，不-march=native/AVX512；静态.su不是OMP/调用链栈总峰；旧DLL/ROM不重编。'))
    print(dict(build=str(a.output),library_sha256=sha(a.output/'jshc_page_id16.dll')))
if __name__=='__main__':main()
