"""77独立静态审计：显式覆盖64回环及最多一次的32直线尾部，保留初次回边识别结果。"""
import hashlib
import json
import re
import struct
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(reg):
    short={'eax':'rax','ebx':'rbx','ecx':'rcx','edx':'rdx','esi':'rsi','edi':'rdi','ebp':'rbp','esp':'rsp'}
    name=reg.removeprefix('%')
    return short.get(name,re.sub(r'^(r\d+)d$',r'\1',name))


def split(text):
    return re.split(r',\s*(?![^()]*\))',text)


def main():
    ops=[]
    for line in (HERE/'andn.asm.txt').read_text(encoding='utf-8').splitlines():
        m=re.match(r'\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9]*)\s*(.*)$',line)
        if m:ops.append(dict(address=int(m[1],16),raw=bytes.fromhex(m[2]),name=m[3],args=m[4].split('#')[0].strip()))
    rows=[]
    # 32区段从首条ANDN至第三次96B输出的末条store，掩码初始化另列在区段之前。
    for mode,width,first,last,mask_at,reference in [('inplace',64,0xe0,0x6c6,0xb8,321),('inplace',32,0x705,0x9e4,0x700,170),('outplace',64,0x1138,0x171b,0x1110,322),('outplace',32,0x1771,0x1a5d,0x176c,171)]:
        body=[o for o in ops if first<=o['address']<=last]
        andn=[o for o in body if o['name']=='andn']
        stack=[dict(address=hex(o['address']),instruction=o['name']+' '+o['args']) for o in body if '%rsp' in o['args'] or '%rbp' in o['args']]
        ids=[];versions={};palette=[]
        for o in body:
            parts=split(o['args'])
            if o['name']=='movzbl' and re.fullmatch(r'\(%rdi,%[a-z0-9]+,1\)',parts[0]):
                versions[canonical(parts[-1])]=len(ids);ids.append(o['address'])
            m=re.search(r'\(%rsi,(%[a-z0-9]+),4\)',o['args'])
            if m:
                generation=versions.get(canonical(m[1]))
                palette.append(dict(address=hex(o['address']),generation=generation,completed_ids=len(ids),ready=generation is not None and len(ids)>=generation//4*4+4))
        stores=[o for o in body if o['name'].startswith('vmov') and '(' in split(o['args'])[-1]]
        mask_regs={split(o['args'])[1] for o in andn}
        initializers=[o for o in ops if o['address']<first and o['name']=='mov' and o['args'] in {'$0xff000000,'+r for r in mask_regs}]
        init=initializers[-1] if initializers else None
        # mask_at以实际最近常量为准，并记录地址；不能只按预估地址宣称提升。
        correct=[]
        for o in andn:
            parts=split(o['args'])
            correct.append(len(parts)==3 and bool(re.fullmatch(r'(?:-?0x[0-9a-f]+)?\(%r[a-z0-9]+\)',parts[0])) and
                           all(re.fullmatch(r'%(?:e[a-z]{2}|r(?:[89]|1[0-5])d)',r) for r in parts[1:]) and
                           o['raw'][0]==0xc4 and not(o['raw'][2]&0x80))
        mask_writes=[o for o in body if split(o['args'])[-1] in mask_regs and o['name'] not in ('cmp','test')]
        rows.append(dict(mode=mode,width=width,kind='backedge_loop' if width==64 else 'at_most_once_straightline',
                         start=hex(first),end=hex(last),instructions=len(body),reference_instructions=reference,
                         andn_count=len(andn),mem32_base_disp=all(correct),id_count=len(ids),palette_count=len(palette),
                         four_id_before_palette=len(ids)==width and len(palette)==width and all(x['ready'] for x in palette),
                         palette_dependencies=palette,stack_references=stack,
                         mask_initializer=hex(init['address']) if init else None,mask_registers=sorted(mask_regs),
                         mask_once_before_body=bool(init) and not mask_writes,
                         self_moves=sum(o['name']=='mov' and len(split(o['args']))==2 and split(o['args'])[0]==split(o['args'])[1] for o in body),
                         stores=len(stores),all_reads_before_first_store=bool(stores) and max(int(x['address'],16) for x in palette)<stores[0]['address']))
    raw=(ROOT/'artifacts/skylake-andn-cursor-linux-build-v1/CMakeFiles/jshc_skylake_andn_cursor.dir/andn/channel_avx2.cpp.o').read_bytes()
    offset=struct.unpack_from('<Q',raw,40)[0];stride,count,names_index=struct.unpack_from('<HHH',raw,58)
    sections=[struct.unpack_from('<IIQQQQIIQQ',raw,offset+i*stride) for i in range(count)]
    ns=sections[names_index];names=raw[ns[4]:ns[4]+ns[5]]
    text=next(raw[s[4]:s[4]+s[5]] for s in sections if names[s[0]:].split(b'\0',1)[0]==b'.text')
    byte_match=all(text[o['address']:o['address']+len(o['raw'])]==o['raw'] for o in ops)
    forbidden=[]
    for o in ops:
        pos=0
        while pos<len(o['raw']) and (o['raw'][pos] in (0x66,0x67,0x2e,0x36,0x3e,0x26,0x64,0x65,0xf2,0xf3,0xf0) or 0x40<=o['raw'][pos]<=0x4f):pos+=1
        if o['name'].startswith('call') or 'gather' in o['name'] or o['name'] in ('pext','pdep','mulx','bzhi','rorx','shlx','shrx','sarx','bextr','blsi','blsr','blsmsk') or re.search(r'%(?:zmm\d+|k[0-7])\b|%[xy]mm(?:1[6-9]|2[0-9]|3[01])\b|\{',o['args']) or pos<len(o['raw']) and o['raw'][pos]==0x62:
            forbidden.append(hex(o['address']))
    prior=json.loads((HERE/'results.json').read_text(encoding='utf-8'))
    plan=json.loads((ROOT/'experiments/skylake-andn-cursor-v1.json').read_text(encoding='utf-8'))
    mismatch=[k for k,v in plan['source_sha256'].items() if digest(ROOT/k)!=v]
    expected={('inplace',64),('inplace',32),('outplace',64),('outplace',32)}
    accepted=(len(rows)==4 and {(r['mode'],r['width']) for r in rows}==expected and byte_match and not forbidden and not mismatch and
              all(x['pass_check'] for x in prior['compile_isa_scope']) and all(r['andn_count']==r['width'] and r['mem32_base_disp'] and
              r['four_id_before_palette'] and r['mask_once_before_body'] and not r['stack_references'] and r['instructions']<r['reference_instructions'] and r['all_reads_before_first_store'] for r in rows))
    result=dict(purpose=__doc__,accepted=accepted,script_sha256=digest(__file__),initial_results_sha256=digest(HERE/'results.json'),
                sections=rows,disassembly_bytes_verified=byte_match,forbidden=forbidden,source_hash_mismatches=mismatch,
                compile_isa_scope=prior['compile_isa_scope'],
                straightline_proof='64循环退出后remaining<72；32尾只在remaining>=40执行，减32后remaining<40，因此最多执行一次。GCC把32循环化直线并继续有限展开8尾，不应要求不存在的回边，也不能省略该实际可达32区段。',
                guards={'inplace':['0x6f6/0x6fa：remaining与39比较；<=39跳过32区段','0x1004/0x1008：未进入64主体的同一32入口条件'],
                        'outplace':['0x1762/0x1766：remaining与39比较；<=39跳过32区段','0x2091/0x2095：未进入64主体的同一32入口条件']},
                exact_tail='read函数逐字节保持76；32后至少8像素所以首个24B尾无需再次条件，后续按剩余数判断；原地0x9ea、分离0x1a64处均先读0/8/16三词。',
                decision='原地64循环remaining位于真实rsp槽（0xe0比较、0x6ba递减、0x6c0比较），仍违反冻结无栈门槛，77停止像素与性能；其他区段通过不会覆盖失败',
                pixel_calls=0,performance_calls=0,candidate_library_loads=0,compiler_calls=0)
    with (HERE/'independent-audit.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'accepted':accepted,'sections':[{k:r[k] for k in ('mode','width','instructions','andn_count','four_id_before_palette','stack_references')} for r in rows],
                      'sha256':digest(HERE/'independent-audit.json')},ensure_ascii=False))


if __name__=='__main__':main()
