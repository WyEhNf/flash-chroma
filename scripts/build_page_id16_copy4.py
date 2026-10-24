"""单次串行构建copy4与可选路由，原core/AVX对象原字节链接，实际DWORD机器码门先行。"""
import argparse
from pathlib import Path
import re
import shutil
import subprocess
from page_id16_copy4_common import ROOT,PLAN,checked_plan,sha,save

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    plan=checked_plan()
    output=args.output.resolve()
    output.mkdir(parents=True,exist_ok=False)
    records=[]
    def run(command):
        result=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,encoding='utf-8',errors='replace')
        records.append(dict(command=command,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr))
        save(output/'commands.json',records)
        if result.returncode:raise RuntimeError('copy4唯一构建失败：'+result.stderr)
        return result.stdout
    clang=plan['toolchain']['clang']
    gcc=plan['toolchain']['gcc']
    cpp=plan['toolchain']['gpp']
    source=ROOT/'experiments/page-id16-copy4-runtime/page_copy4.c'
    adapter=ROOT/'experiments/page-id16-copy4-runtime/page_copy4_parallel.cpp'
    core=Path(plan['old_objects']['core'])
    avx=Path(plan['old_objects']['avx'])
    common=['-O3','-Wall','-Wextra','-ffp-contract=off','-fstack-usage','-march=x86-64','-mtune=generic','-mno-avx','-mno-avx2','-mno-avx512f']
    run([clang,'--target=x86_64-w64-windows-gnu','--sysroot=E:/mingw64','-isystem','E:/mingw64/x86_64-w64-mingw32/include','-std=c99','-pedantic-errors',*common,'-c',str(source),'-o',str(output/'page_copy4.o')])
    assembly=run([plan['toolchain']['objdump'],'-d','-Mintel','--no-show-raw-insn',str(output/'page_copy4.o')])
    (output/'copy4-assembly.txt').write_text(assembly,encoding='utf-8')
    dword_reads=re.findall(r'^\s*([0-9a-f]+):\s+(?:mov|movd|movss)\s+([a-z0-9]+),DWORD PTR (\[[^\]\r\n]*\*4[^\]\r\n]*\])\s*$',assembly,re.M)
    mnemonics=re.findall(r'^\s*[0-9a-f]+:\s+([a-z0-9]+)',assembly,re.M)
    forbidden=[name for name in mnemonics if name.startswith('v') or name in ('pdep','pext','shlx','shrx','sarx','andn','mulx','bzhi','bextr','blsi','blsr','blsmsk','tzcnt','lzcnt','popcnt','crc32')]
    gate=dict(passed=len(dword_reads) in (7,8) and not forbidden and bool(mnemonics),palette_dword_reads=[dict(offset=address,destination=register,operand=operand) for address,register,operand in dword_reads],forbidden_mnemonics=forbidden,scope='P4 map是LE16、pool是byte，唯一scale4 DWORD表为palette；固定八项主组要求至少前7项单DWORD读取，末3B允许只读3B。仅机器码机制门，不是速度证据。')
    save(output/'machine-code-gate.json',gate)
    if not gate['passed']:raise AssertionError('copy4未实现预定DWORD读取机制，保留原件STOP')
    run([cpp,'-std=c++17',*common,'-fopenmp','-c',str(adapter),'-o',str(output/'page_copy4_parallel.o')])
    run([cpp,'-shared','-O3','-fopenmp',str(core),str(output/'page_copy4.o'),str(output/'page_copy4_parallel.o'),str(avx),'-o',str(output/'jshc_page_id16_copy4.dll')])
    run([gcc,'-shared',str(core),str(output/'page_copy4.o'),'-o',str(output/'jshc_page_id16_copy4_c99.dll')])
    for name,path in plan['dependencies'].items():shutil.copyfile(path,output/name)
    files={path.name:dict(bytes=path.stat().st_size,sha256=sha(path)) for path in output.iterdir() if path.suffix in ('.dll','.o','.su')}
    versions={name:run([plan['toolchain'][name],'--version']) for name in ('clang','gcc','gpp')}
    if any(sha(path)!=plan['input_sha256'][path] for path in plan['old_objects'].values()):raise AssertionError('原core/AVX对象在构建期间改变')
    save(output/'build.json',dict(purpose=__doc__,plan_sha256=sha(PLAN),machine_code_gate=gate,reused_objects={name:dict(path=path,sha256=sha(path)) for name,path in plan['old_objects'].items()},outputs=files,versions=versions,scope='只新增copy4 C99与路由对象；原P4 core/AVX原字节复用，无导出ROM/参数扫描/AVX512，不授新C99速度。'))
    print(dict(built=True,palette_dword_reads=len(dword_reads),machine_code_gate=gate['passed'],main_sha256=sha(output/'jshc_page_id16_copy4.dll')),flush=True)

if __name__=='__main__':main()
