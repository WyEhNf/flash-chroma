"""单版Clang严格C99与GCC AVX2/OMP构建，不扫描编译器/loop。"""
import argparse
from pathlib import Path
import re
import shutil
import subprocess
from rgb3d7_support import ROOT,PLAN,read,save,sha
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();plan=read(PLAN)
    if any(sha(ROOT/n)!=v for n,v in plan['source_sha256'].items()):raise AssertionError('冻结源变化')
    if any(sha(n)!=v for n,v in plan['input_sha256'].items()):raise AssertionError('冻结输入或编译器变化')
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);base=ROOT/'experiments/rgb3d-palette7-runtime';clang=plan['clang'];gxx='E:/mingw64/bin/g++.exe';gcc='E:/mingw64/bin/gcc.exe';commands=[]
    def run(command):
        r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace');commands.append(dict(command=command,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));save(out/'commands.json',commands)
        if r.returncode:raise RuntimeError(r.stderr)
        return r.stdout
    run([clang,'--target=x86_64-w64-windows-gnu','--sysroot=E:/mingw64','-isystem','E:/mingw64/x86_64-w64-mingw32/include','-std=c99','-pedantic-errors','-O3','-Wall','-Wextra','-march=x86-64','-mtune=generic','-mno-avx','-mno-avx2','-mno-avx512f','-fstack-usage','-c',str(base/'memory_rom.c'),'-o',str(out/'memory_c.o')])
    run([gcc,'-shared',str(out/'memory_c.o'),'-o',str(out/'jshc_rgb3d7_c99.dll')])
    for name,extra in (('memory_parallel',[]),('channel_avx2_rgb3d7',['-mavx2','-mtune=skylake','-ffp-contract=off'])):run([gxx,'-O3','-DNDEBUG','-std=c++17','-fopenmp','-fstack-usage',*extra,'-c',str(base/(name+'.cpp')),'-o',str(out/(name+'.o'))])
    run([gxx,'-shared','-O3','-fopenmp',*[str(out/(name+'.o')) for name in ('memory_c','memory_parallel','channel_avx2_rgb3d7')],'-o',str(out/'jshc_rgb3d7.dll')])
    for name in ('libgcc_s_seh-1.dll','libstdc++-6.dll','libwinpthread-1.dll','libgomp-1.dll'):shutil.copyfile(Path(gxx).parent/name,out/name)
    ref=Path(plan['reference78']['path'])
    if sha(ref)!=plan['reference78']['sha256']:raise AssertionError('78身份不同')
    shutil.copyfile(ref,out/'jshc_memory_ref78.dll');assembly=run(['E:/mingw64/bin/objdump.exe','-d','-Mintel','--no-show-raw-insn',str(out/'memory_c.o')]);(out/'c99-assembly.txt').write_text(assembly,encoding='utf-8');mnemonics=re.findall(r'^\s*[0-9a-f]+:\s+([a-z0-9]+)',assembly,re.M);bad=[n for n in mnemonics if n.startswith('v') or n in ('pdep','pext','andn','shlx','shrx','sarx','mulx','bzhi','bextr','blsi','blsr','blsmsk','tzcnt','lzcnt','popcnt','crc32')]
    if not mnemonics or bad:raise AssertionError('C99含非generic x64 ISA：'+str(bad))
    save(out/'build.json',dict(purpose=__doc__,plan_sha256=sha(PLAN),source_sha256=plan['source_sha256'],commands=commands,compiler_sha256={n:sha(n) for n in (clang,gcc,gxx)},libraries={x.name:sha(x) for x in out.glob('*.dll')},c99_mnemonics=sorted(set(mnemonics)),c99_forbidden=bad,scope='唯一Clang通用x64 C99，无AVX/BMI；独立GCC AVX2 TU无新增BMI/native/AVX512；全部源/数据冻结，旧控制不重编译。'))
    print(out)
if __name__=='__main__':main()
