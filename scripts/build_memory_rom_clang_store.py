"""只用Clang21重编译原严格C99 store，原GCC核心/OMP/AVX2对象原字节链接。"""
import argparse
from pathlib import Path
import shutil
import subprocess
import re
from study_memory_rom import ROOT,read,save,sha

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();plan=ROOT/'experiments/memory-rom-clang-store-v1.json';frozen=read(plan);out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    for name,value in frozen['source_sha256'].items():
        if sha(ROOT/name)!=value:raise AssertionError('冻结源码变化：'+name)
    for name,value in frozen['input_sha256'].items():
        if sha(name)!=value:raise AssertionError('冻结输入变化：'+name)
    clang=frozen['clang'];gcc=frozen['gcc'];cpp=frozen['gxx'];source=ROOT/'experiments/memory-rom/memory_rom_store.c';obj=out/'memory_store_clang.o';records=[]
    def run(command):
        r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace');records.append(dict(command=command,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));save(out/'commands.json',records)
        if r.returncode:raise RuntimeError(r.stderr)
        return r.stdout
    run([clang,'--target=x86_64-w64-windows-gnu','--sysroot=E:/mingw64','-isystem','E:/mingw64/x86_64-w64-mingw32/include','-std=c99','-pedantic-errors','-O3','-Wall','-Wextra','-march=x86-64','-mtune=generic','-mno-avx','-mno-avx2','-mno-avx512f','-fstack-usage','-c',str(source),'-o',str(obj)])
    objects=[str(obj) if Path(name).name=='memory_store.o' else name for name in frozen['old_link_objects']]
    run([cpp,'-shared','-O3','-fopenmp',*objects,'-o',str(out/'jshc_memory_clang_store.dll')])
    core=next(name for name in frozen['old_link_objects'] if Path(name).name=='memory_c.o');run([gcc,'-shared',core,str(obj),'-o',str(out/'jshc_memory_c99.dll')])
    old=Path(frozen['old_build'])
    for name in ('jshc_memory_ref78.dll','libgcc_s_seh-1.dll','libstdc++-6.dll','libwinpthread-1.dll','libgomp-1.dll'):shutil.copyfile(old/name,out/name)
    assembly=run(['E:/mingw64/bin/objdump.exe','-d','-Mintel','--no-show-raw-insn',str(obj)]);(out/'clang-store-assembly.txt').write_text(assembly,encoding='utf-8')
    mnemonics=re.findall(r'^\s*[0-9a-f]+:\s+([a-z0-9]+)',assembly,re.M);forbidden=[n for n in mnemonics if n.startswith('v') or n in ('pdep','pext','shlx','shrx','sarx','andn','mulx','bzhi','bextr','blsi','blsr','blsmsk','tzcnt','lzcnt','popcnt','crc32')]
    if not mnemonics or forbidden:raise AssertionError('非通用x64指令或空机器码：'+str(forbidden))
    version=run([clang,'--version']);save(out/'build.json',dict(purpose=__doc__,plan_sha256=sha(plan),source_sha256=frozen['source_sha256'],input_sha256=frozen['input_sha256'],commands=records,compiler_version=version,clang_object_sha256=sha(obj),reused_objects={name:sha(name) for name in frozen['old_link_objects'] if Path(name).name!='memory_store.o'},libraries={x.name:sha(x) for x in out.glob('*.dll')},generic_x64_mnemonics=sorted(set(mnemonics)),forbidden_mnemonics=forbidden,scope='唯一新编译的映射对象是相同C99 store源；原GCC验证/准备、OMP适配器、旧AVX2/ANDN对象与链接顺序均复用，不用native或AVX512。'))
    print(out)
if __name__=='__main__':main()
