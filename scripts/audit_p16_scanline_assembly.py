"""100读取实际独立object/符号/栈回执；不执行native或计时。"""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
build=ROOT/'artifacts/p16-scanline-prepare-build-v1'
obj=build/'CMakeFiles/jshc_scanline_prepare.dir/compile_scanline_avx2.cpp.obj'
su=obj.with_suffix('.su')
target=ROOT/'artifacts/p16-scanline-prepare-assembly-audit-v1.json'
if target.exists():raise FileExistsError('100实际汇编审计不覆盖')
def command(executable,*args):
    run=subprocess.run([str(Path('E:/mingw64/bin')/executable),*args,str(obj)],capture_output=True,text=True,encoding='utf-8',errors='replace')
    assert run.returncode==0,run.stderr
    return run.stdout
assembly=command('objdump.exe','-Cdr')
symbols=command('nm.exe','-C')
undefined=command('nm.exe','-Cu')
asm_path=ROOT/'artifacts/p16-scanline-prepare-disassembly-v1.txt'
sym_path=ROOT/'artifacts/p16-scanline-prepare-symbols-v1.txt'
asm_path.write_text(assembly,encoding='utf-8');sym_path.write_text(symbols,encoding='utf-8')
functions=[]
current=None
for line in assembly.splitlines():
    match=re.match(r'^([0-9a-f]+) <(.+)>:$',line)
    if match:
        current={'symbol':match.group(2),'gathers':0,'calls':[],'aligned_ymm_rsp_stores':[]}
        functions.append(current)
    if current:
        current['gathers']+=len(re.findall(r'\bvpgatherdd\b',line))
        if re.search(r'\bcall\w*\s',line):current['calls'].append(line)
        if re.search(r'\bvmov(?:aps|apd|dqa)\s+%ymm[^\n]*\(%rsp\)',line):current['aligned_ymm_rsp_stores'].append(line)
stack=su.read_text(encoding='utf-8')
private_undefined=[line for line in undefined.splitlines() if line.strip()]
unexpected_undefined=[line for line in private_undefined if 'jshc_channel::avx2_compile_direct(' not in line]
all_calls=[line for function in functions for line in function['calls']]
all_aligned=[line for function in functions for line in function['aligned_ymm_rsp_stores']]
result={'purpose':'100实际object静态审计，不替代运行时或性能','passed':not unexpected_undefined and not all_calls and not all_aligned,
    'object':{'path':str(obj),'sha256':sha(obj)},'stack_usage':{'path':str(su),'sha256':sha(su),'text':stack},
    'disassembly':{'path':str(asm_path),'sha256':sha(asm_path)},'symbols':{'path':str(sym_path),'sha256':sha(sym_path)},
    'functions':functions,'undefined_symbols':private_undefined,'unexpected_undefined_symbols':unexpected_undefined,
    'call_instructions':len(all_calls),'aligned_ymm_rsp_stores':len(all_aligned),
    'scope':'生产源所有跨TU入口void，内部向量helper强制inline；实object只允许旧void入口的外部符号且不允许call/对齐YMM rsp存储。'}
target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
assert result['passed'],'100汇编首审失败原件保留STOP，不能直接改已冻结生产源'
