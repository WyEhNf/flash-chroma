"""冻结copy4唯一源码与旧ROM/40B ABI/对象，先机器码门后九模式质量，不计时。"""
import ast
from pathlib import Path
from study_memory_rom import ROOT,sha,read,save

def main():
    output=ROOT/'experiments/page-id16-copy4-runtime-v1.json'
    if output.exists():raise FileExistsError('copy4协议不能覆盖')
    old_plan=ROOT/'experiments/page-id16-runtime-v1.json'
    old=read(old_plan)
    if sha(old_plan)!='b41c503e0d8164bac0a685c1035349ce41e04532eaf60dced61cfe87928dd515' or any(sha(ROOT/name)!=value for name,value in old['source_sha256'].items()):raise AssertionError('原P4冻结源不同')
    names=list(old['source_sha256'])+['experiments/page-id16-copy4-design-v1.md',*['experiments/page-id16-copy4-runtime/'+name for name in ('page_copy4.c','page_copy4.h','page_copy4_parallel.cpp')],*['scripts/'+name for name in ('page_id16_copy4_common.py','build_page_id16_copy4.py','verify_page_id16_copy4.py','freeze_page_id16_copy4.py','run_page_id16_copy4_quality.py')]]
    for name in names:
        if name.endswith('.py'):ast.parse((ROOT/name).read_text(encoding='utf-8'),filename=name)
    toolchain=dict(clang='C:/Program Files/LLVM/bin/clang.exe',gcc='E:/mingw64/bin/gcc.exe',gpp='E:/mingw64/bin/g++.exe',objdump='E:/mingw64/bin/objdump.exe')
    toolchain={key:str(Path(value)) for key,value in toolchain.items()}
    build=ROOT/'artifacts/p16-page-id16-runtime-v1/build'
    objects=dict(core=str(build/'page_core.o'),avx=str(build/'page_avx2.o'))
    expected={'core':'4c6b215a054708a6803628bbfa9ea419a262b9447a18ddec658be53b45260216','avx':'4385fe648dd618daa11de9c4760f8253f84eacc7d6d317513a5bd36b1f539dd9'}
    if any(sha(objects[name])!=value for name,value in expected.items()):raise AssertionError('原对象不是已测P4版本')
    dependencies={name:str(build/name) for name in ('libgcc_s_seh-1.dll','libgomp-1.dll','libstdc++-6.dll','libwinpthread-1.dll')}
    rom=ROOT/'artifacts/p16-page-id16-runtime-v1/rom/page-id16.bin'
    if sha(rom)!='a953eef0d1a70763a4bca053d4d70dc00dae6e40cc8eecdd1ac48648dfa15173':raise AssertionError('原ROM改变')
    paths=[old_plan,rom,rom.parent/'export.json',ROOT/'artifacts/p16-page-id16-runtime-v1/quality/results.json',*[Path(value) for value in toolchain.values()],*[Path(value) for value in objects.values()],*[Path(value) for value in dependencies.values()]]
    inputs={str(Path(name)):value for name,value in old['input_sha256'].items()}
    inputs.update({str(path):sha(path) for path in paths})
    value=dict(purpose=__doc__,source_sha256={name:sha(ROOT/name) for name in names},input_sha256=inputs,original_quality_plan_sha256=sha(old_plan),original_rom=str(Path(old['original_rom'])),page_rom=str(rom),photos=str(Path(old['photos'])),photos_sha256=old['photos_sha256'],quality=old['quality'],toolchain=toolchain,old_objects=objects,dependencies=dependencies,protocol='只有逐RGB3B读取加置零改为memcpy4；8输入先读/8颜色先求/前7重叠4B写末3B/短尾/prepare/validate不变；先唯一-j1构建与前7palette单DWORD机制门，再独立新符号九完整域/九百图逐图u64、890有限、113 IO拒绝、21格式拒绝、180图像guard、36ROMguard和72非对齐。首次失败STOP不修后重采，不运行性能或WASM。',scope='原core/AVX对象和P4 ROM/40B ABI保持；新OMP C99分支明确调用apply_copy4，所有调用记录新符号地址/计数。AVX原点不替新C99速度背书，后续正式另冻结与明确grant。')
    save(output,value)
    print(dict(plan=str(output),sha256=sha(output),sources=len(names),inputs=len(inputs)),flush=True)

if __name__=='__main__':main()
