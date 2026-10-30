"""74三像素对象静态检查；不执行像素或性能。"""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; HERE=Path(__file__).resolve().parent
base=ROOT/'artifacts/skylake-prefetchw-linux-build-v1/CMakeFiles/jshc_skylake_prefetchw.dir'
rows=[]
for role,object_path in [('linear',base/'channel_avx2.cpp.o'),('t0',base/'t0/channel_avx2.cpp.o'),('prefetchw',base/'prefetchw/channel_avx2.cpp.o')]:
    asm=subprocess.check_output(['objdump','-d','--insn-width=15','-C',str(object_path)],text=True)
    (HERE/(role+'.asm.txt')).write_text(asm,encoding='utf-8')
    ops=[]
    for line in asm.splitlines():
        m=re.match(r'\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9]*)\s*(.*)$',line)
        if m: ops.append({'offset':int(m[1],16),'bytes':m[2].split(),'mnemonic':m[3],'operands':m[4].split('#')[0].strip()})
    forbidden=[]
    for op in ops:
        raw=[int(b,16) for b in op['bytes']];pos=0
        while pos<len(raw) and (raw[pos] in (0x66,0x67,0x2e,0x36,0x3e,0x26,0x64,0x65,0xf2,0xf3,0xf0) or 0x40<=raw[pos]<=0x4f):pos+=1
        if (op['mnemonic'].startswith('call') or op['mnemonic'] in ('pext','pdep','mulx','bzhi','rorx','shlx','shrx','sarx') or 'gather' in op['mnemonic'] or re.search(r'%zmm\d+|%k[0-7]\b|%[xy]mm(?:1[6-9]|2[0-9]|3[01])\b',op['operands']) or pos<len(raw) and raw[pos]==0x62): forbidden.append(op)
    assert not forbidden,forbidden
    loops=[]
    for op in ops:
        if op['mnemonic'].startswith('j'):
            m=re.match(r'([0-9a-f]+)\b',op['operands'])
            if m and int(m[1],16)<op['offset']-100:
                start=int(m[1],16); body=[p for p in ops if start<=p['offset']<=op['offset']]
                loops.append({'start':hex(start),'end':hex(op['offset']),'instructions':len(body),'stack_references':[p for p in body if '%rsp' in p['operands'] or '%rbp' in p['operands']]})
    hints={h:sum(x['mnemonic']==h for x in ops) for h in ('prefetchw','prefetcht0','prefetchnta','sfence','vmovntdq')}
    if role!='linear':
        assert hints['sfence']==hints['vmovntdq']==hints['prefetchnta']==0
        assert hints['prefetchw' if role=='prefetchw' else 'prefetcht0']==5
        assert hints['prefetcht0' if role=='prefetchw' else 'prefetchw']==0
    rows.append({'role':role,'object_sha256':hashlib.sha256(object_path.read_bytes()).hexdigest(),'instructions':len(ops),'hints':hints,'loops':loops,'forbidden':forbidden})
commands=json.loads((base.parents[1]/'compile_commands.json').read_text())
for entry in commands:
    has='-mprfchw' in entry['command']; expected='/skylake-prefetchw-runtime/prefetchw/' in entry['file']; assert has==expected,entry['file']
with (HERE/'results.json').open('x',encoding='utf-8') as f:json.dump({'purpose':__doc__,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'objects':rows,'compile_isa_scope_checked':True,'pixel_calls':0,'performance_calls':0},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(rows,ensure_ascii=False))