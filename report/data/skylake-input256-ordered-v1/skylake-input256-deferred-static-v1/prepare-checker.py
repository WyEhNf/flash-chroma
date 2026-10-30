"""冻结82完整区段筛查：按实际图像地址验证分阶段读写，不执行原生。"""
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
old=(ROOT/'artifacts/skylake-input256-static-v1/check-v2.py').read_text(encoding='utf-8')
old=old.replace('input256','input256_deferred').replace('skylake-input256_deferred','skylake-input256-deferred')
old=old.replace("'input256_deferred_inplace/channel_avx2.cpp.o'","'deferred_inplace/channel_avx2.cpp.o'")
old=old.replace("HERE/'results-v2.json'","HERE/'results.json'")
old=old.replace("assert asm.read_text(encoding='utf-8')==text, '原反汇编不得改变'","with asm.open('x',encoding='utf-8') as stream:stream.write(text)")
old=old.replace("initial_checker_sha256=sha(HERE/'check.py'),initial_result_sha256=sha(HERE/'results.json'),classifier_correction='初版把栈spill存储计为图像写入，连带输出门槛误报；v2仅分类非栈输出，无栈门槛仍失败，不改源/对象或执行原生。',",'')
start=old.index('def vector_regions(');end=old.index('\ndef main():',start)
region=r'''def vector_regions(ops,h):
    rows=[]
    for branch in ops:
        target=re.match(r'([0-9a-f]+)\b',branch['operands'])
        if not branch['mnemonic'].startswith('j') or not target or int(target[1],16)>=branch['offset']-100:continue
        start,end=int(target[1],16),branch['offset']
        body=[o for o in ops if o['function']==branch['function'] and start<=o['offset']<=end]
        barrier=h.id_barrier(body);width=barrier['id_loads']
        if width not in (32,64):continue
        frame=any(o['function']==branch['function'] and o['offset']<start and o['mnemonic']=='mov' and o['operands']=='%rsp,%rbp' for o in ops)
        stack=[o for o in body if '%rsp' in o['operands'] or frame and '%rbp' in o['operands']]
        constants=[o for o in body if '(%rip)' in o['operands']]
        inputs=[o for o in body if o['mnemonic'] in ('vmovdqu','vpermd') and '(' in h.operands(o['operands'])[0] and '(%rip)' not in o['operands'] and '%rsp' not in o['operands']]
        stores=[o for o in body if o['mnemonic'].startswith('vmov') and '(' in h.operands(o['operands'])[-1] and '%rsp' not in o['operands'] and not(frame and '%rbp' in o['operands'])]
        palettes=[o for o in body if '(%rsi,' in o['operands']]
        ids=[o for o in body if o['mnemonic']=='movzbl' and re.fullmatch(r'\(%rdi,%[a-z0-9]+,1\)',h.operands(o['operands'])[0])]
        def memory(text):return re.fullmatch(r'(-?0x[0-9a-f]+)?\((%r[a-z0-9]+)\)',text)
        first=memory(h.operands(inputs[0]['operands'])[0]) if inputs else None
        state={h.canonical(first[2]):0} if first else {}
        input_offsets=[];store_offsets=[]
        for o in body:
            p=h.operands(o['operands']);before=dict(state)
            if o in inputs or o in stores:
                m=memory(p[0] if o in inputs else p[-1]);base=before.get(h.canonical(m[2])) if m else None
                off=base+int(m[1] or '0',16) if m and base is not None else None
                (input_offsets if o in inputs else store_offsets).append(off)
            if not p or not re.fullmatch(r'%(?:r[a-z0-9]+|e[a-z]+)',p[-1]) or o['mnemonic'] in ('test','cmp','push') or o['mnemonic'].startswith(('j','nop')):continue
            dest=h.canonical(p[-1]);state.pop(dest,None)
            if o['mnemonic']=='mov' and p[0].startswith('%') and h.canonical(p[0]) in before:state[dest]=before[h.canonical(p[0])]
            elif o['mnemonic'] in ('add','sub') and p[0].startswith('$') and dest in before:state[dest]=before[dest]+int(p[0][1:],0)*(1 if o['mnemonic']=='add' else -1)
            elif o['mnemonic']=='lea':
                m=memory(p[0])
                if m and h.canonical(m[2]) in before:state[dest]=before[h.canonical(m[2])]+int(m[1] or '0',16)
        checks={'no_stack':not stack,'no_loop_constant_load':not constants,
            'one_load32_per8':len(inputs)==width//8 and sorted(x for x in input_offsets if x is not None)==list(range(0,width*3,24)),
            'four_id':barrier['four_id_before_palette'] and barrier['palette_loads']==width,
            'store_coverage':len(stores)==width*3//32 and sorted(x for x in store_offsets if x is not None)==list(range(0,width*3,32)),
            'nt64_normal32':all(o['mnemonic']==('vmovntdq' if width==64 else 'vmovdqu') for o in stores)}
        if width==64 and len(inputs)==8 and len(stores)==6 and len(palettes)==len(ids)==64:
            checks.update(first_group_reads_before_first_nt=max(o['offset'] for o in inputs[:4]+palettes[:32]+ids[:32])<stores[0]['offset'],
                first_two_nt_are_complete_first_line=store_offsets[:2]==[0,32],
                first_two_nt_before_second_group=stores[1]['offset']<inputs[4]['offset'],
                second_group_reads_before_remaining_nt=max(o['offset'] for o in inputs[4:]+palettes[32:]+ids[32:])<stores[2]['offset'],
                second_group_no_read_of_written_line=None not in input_offsets[4:] and min(input_offsets[4:])>=96,
                last_four_nt_order=store_offsets[2:]==[64,96,128,160])
        elif width==32 and stores and inputs and palettes and ids:
            checks['all_reads_before_first_store']=max(o['offset'] for o in inputs+palettes+ids)<stores[0]['offset']
        else:checks['complete_group_structure']=False
        rows.append(dict(width=width,start=hex(start),end=hex(end),instructions=len(body),checks=checks,
            input_loads=inputs,input_byte_offsets=input_offsets,maximum_input_bytes=max((x for x in input_offsets if x is not None),default=-32)+32,
            image_store_byte_offsets=store_offsets,stores=stores,stack_references=stack,loop_constant_loads=constants,barrier=barrier))
    return rows
'''
old=old[:start]+region+old[end:]
old=old.replace('81静态筛查','82静态筛查').replace('完整宽区段的输入载荷、四ID、常量、栈与ISA','分阶段NT的实际读写地址、四ID、常量、栈与ISA')
with (HERE/'check.py').open('x',encoding='utf-8') as stream:stream.write(old)
print('82静态门槛已准备，未执行候选。')
