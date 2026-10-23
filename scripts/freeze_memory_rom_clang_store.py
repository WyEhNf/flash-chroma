"""预冻结同一C99源的Clang通用x64编译器试验，不执行构建或性能。"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--old-build',type=Path,required=True);p.add_argument('--clang',default='C:/Program Files/LLVM/bin/clang.exe');a=p.parse_args();old=a.old_build.resolve();metadata=json.loads((old/'build.json').read_text(encoding='utf-8'));link=next(r['command'] for r in metadata['commands'] if r['command'][-1].endswith('jshc_memory_rom.dll'));objects=[str((ROOT/Path(x)).resolve()) for x in link if x.endswith('.o')]
    if sum(Path(x).name=='memory_store.o' for x in objects)!=1:raise AssertionError('旧链接未唯一定位store对象')
    names=['experiments/memory-rom/'+n for n in ('memory_rom.h','memory_rom.c','memory_rom_store.h','memory_rom_store.c','memory_parallel.cpp')]
    names+=['scripts/'+n for n in ('build_memory_rom_clang_store.py','bench_memory_rom_clang_store.py','freeze_memory_rom_clang_store.py','study_memory_rom.py','verify_memory_rom_store.py','verify_memory_rom_contract.py','bench_memory_rom.py')]
    inputs=[*objects,str(old/'jshc_memory_rom.dll'),str(old/'build.json'),a.clang,'E:/mingw64/bin/gcc.exe','E:/mingw64/bin/g++.exe'];plan=dict(purpose=__doc__,source_sha256={n:sha(ROOT/n) for n in names},input_sha256={str(Path(n).resolve()):sha(n) for n in inputs},clang=a.clang,gcc='E:/mingw64/bin/gcc.exe',gxx='E:/mingw64/bin/g++.exe',old_build=str(old),old_link_objects=objects,protocol='新Clang object+原GCC对象原顺序链接；原完整五ROM/纯C99/保护页合同先行，再同一8bit ROM四角色GCC/Clang store与78/80、四新worker、双接口1/4线程预热1+5百图及独立RSS。',gate='精度全域及逐图逐字节不变；固定同场最快78/80为分母、四worker最差吞吐按100/90/80/70/60/50；同场GCC/Clang配对比另列；80 A/A单对0.8..1.25且中位1/1.1..1.1，不跨场拼比。',isa='严格C99，x86_64-w64-windows-gnu，-march=x86-64 -mtune=generic -mno-avx -mno-avx2 -mno-avx512f；无native/LTO/算法改写；仅C99对象机器码另核无AVX/BMI。',reference='https://clang.llvm.org/docs/CrossCompilation.html')
    path=ROOT/'experiments/memory-rom-clang-store-v1.json'
    if path.exists():raise FileExistsError(path)
    path.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(sha(path))
if __name__=='__main__':main()
