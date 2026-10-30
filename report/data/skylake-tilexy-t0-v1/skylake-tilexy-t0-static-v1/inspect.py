"""73像素对象静态检查；不执行像素或性能。"""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; HERE=Path(__file__).resolve().parent
base=ROOT/'artifacts/skylake-tilexy-t0-linux-build-v1/CMakeFiles/jshc_skylake_tilexy_t0.dir'
rows=[]
for role,object_path in [('linear',base/'channel_avx2.cpp.o'),('tilexy',base/'tilexy/channel_avx2.cpp.o')]:
    asm=subprocess.check_output(['objdump','--no-show-raw-insn','-d','-C',str(object_path)],text=True)
    (HERE/(role+'.asm.txt')).write_text(asm,encoding='utf-8')
    ops=[]
    for line in asm.splitlines():
        m=re.match(r'\s*([0-9a-f]+):\s+(\S+)\s*(.*)$',line)
        if m: ops.append({'offset':int(m[1],16),'mnemonic':m[2],'operands':m[3]})
    forbidden=[op for op in ops if op['mnemonic'].startswith('call') or op['mnemonic'] in ('pext','pdep') or 'gather' in op['mnemonic'] or re.search(r'%[zk][0-9]|%[xy]mm(?:1[6-9]|2[0-9]|3[01])',op['operands'])]
    assert not forbidden,forbidden
    loops=[]
    for op in ops:
        if op['mnemonic'].startswith('j'):
            m=re.match(r'([0-9a-f]+)\b',op['operands'])
            if m and int(m[1],16)<op['offset']-100:
                start=int(m[1],16); body=[p for p in ops if start<=p['offset']<=op['offset']]
                loops.append({'start':hex(start),'end':hex(op['offset']),'instructions':len(body),'stack_references':[p for p in body if '%rsp' in p['operands'] or '%rbp' in p['operands']]})
    if role=='tilexy': assert not any(x['mnemonic'] in ('sfence','vmovntdq','movntdq','prefetchnta') for x in ops)
    rows.append({'role':role,'object_sha256':hashlib.sha256(object_path.read_bytes()).hexdigest(),'instructions':len(ops),'loops':loops,'forbidden':forbidden})
with (HERE/'results.json').open('x',encoding='utf-8') as f: json.dump({'purpose':__doc__,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'objects':rows,'pixel_calls':0,'performance_calls':0},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(rows,ensure_ascii=False))