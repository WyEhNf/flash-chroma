"""101只读实际object/汇编/栈门，不执行native或计时。"""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
build=ROOT/'artifacts/p16-early-index-build-v1';obj=build/'CMakeFiles/jshc_early_index.dir/compile_index_avx2.cpp.obj';su=obj.with_suffix('.su')
target=ROOT/'artifacts/p16-early-index-assembly-audit-v1.json'
if target.exists():raise FileExistsError('101实际汇编门不覆盖')
def command(executable,*args):
    run=subprocess.run([str(Path('E:/mingw64/bin')/executable),*args,str(obj)],capture_output=True,text=True,encoding='utf-8',errors='replace')
    assert run.returncode==0,run.stderr
    return run.stdout
assembly=command('objdump.exe','-Cdr');symbols=command('nm.exe','-C');undefined=command('nm.exe','-Cu')
asm_path=ROOT/'artifacts/p16-early-index-disassembly-v1.txt';sym_path=ROOT/'artifacts/p16-early-index-symbols-v1.txt'
asm_path.write_text(assembly,encoding='utf-8');sym_path.write_text(symbols,encoding='utf-8')
functions=[];current=None
for line in assembly.splitlines():
    match=re.match(r'^([0-9a-f]+) <(.+)>:$',line)
    if match:
        current={'symbol':match.group(2),'gathers':0,'calls':[],'aligned_ymm_rsp_stores':[]};functions.append(current)
    if current:
        current['gathers']+=len(re.findall(r'\bvpgatherdd\b',line))
        if re.search(r'\bcall\w*\s',line):current['calls'].append(line)
        if re.search(r'\bvmov(?:aps|apd|dqa)\s+%ymm[^\n]*\(%rsp\)',line):current['aligned_ymm_rsp_stores'].append(line)
private_undefined=[line for line in undefined.splitlines() if line.strip()]
unexpected=[line for line in private_undefined if 'jshc_channel::avx2_compile_direct_scanline(' not in line]
calls=[line for f in functions for line in f['calls']];aligned=[line for f in functions for line in f['aligned_ymm_rsp_stores']]
result={'purpose':'101实际对象静态机器码门，非native或性能','passed':not unexpected and not calls and not aligned and sum(f['gathers'] for f in functions)==14,
    'object':{'path':str(obj),'sha256':sha(obj)},'stack_usage':{'path':str(su),'sha256':sha(su),'text':su.read_text(encoding='utf-8')},
    'disassembly':{'path':str(asm_path),'sha256':sha(asm_path)},'symbols':{'path':str(sym_path),'sha256':sha(sym_path)},
    'functions':functions,'undefined_symbols':private_undefined,'unexpected_undefined_symbols':unexpected,
    'call_instructions':len(calls),'aligned_ymm_rsp_stores':len(aligned),
    'scope':'新void入口内部helper强制inline，只允许父100 void fallback符号；总14 gather仍需按分支人工确认5/9，不将frame数当spill代价或速度。'}
target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
assert result['passed'],'101机器码门首错STOP保留，不改已冻结源重建'
