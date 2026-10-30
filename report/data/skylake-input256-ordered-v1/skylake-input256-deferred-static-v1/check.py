"""82静态筛查：分阶段NT的实际读写地址、四ID、常量、栈与ISA；不加载候选。"""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BUILD=ROOT/'artifacts/skylake-input256-deferred-linux-build-v1'
OBJECTS=BUILD/'CMakeFiles/jshc_skylake_input256_deferred.dir'
OLD=ROOT/'artifacts/skylake-pair48-linux-build-v1/CMakeFiles/jshc_skylake_pair48.dir'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def module(name):
    spec=importlib.util.spec_from_file_location(name,HERE/(name+'.py'))
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
def save(path,value):
    with path.open('x',encoding='utf-8') as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')

def vector_regions(ops,h):
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

def main():
    assert not(HERE/'results.json').exists(),'不得覆盖静态原件'
    h,p=module('single_support'),module('pair_support')
    rows=[];failures=[]
    for role,relative in [('linear','channel_avx2.cpp.o'),('pair_inplace','andn_inplace/channel_avx2.cpp.o'),('pair_outplace','andn_outplace/channel_avx2.cpp.o'),('input256_deferred','deferred_inplace/channel_avx2.cpp.o')]:
        obj=OBJECTS/relative;asm=HERE/(role+'.asm.txt')
        text=subprocess.check_output(['objdump','-d','--insn-width=15','-C',str(obj)],text=True,encoding='utf-8')
        with asm.open('x',encoding='utf-8') as stream:stream.write(text)
        ops=h.read_ops(asm);raw=h.text_section(obj)
        bytes_ok=all(raw[o['offset']:o['offset']+len(o['bytes'])]==bytes.fromhex(' '.join(o['bytes'])) for o in ops)
        bad=[o for o in ops if h.forbidden(o,'andn_inplace' if role.startswith('pair_') else 'linear')]
        preserved=raw==h.text_section(OLD/relative) if role!='input256_deferred' else None
        regions=vector_regions(ops,h) if role=='input256_deferred' else []
        if role.startswith('pair_'):
            hr='andn_inplace' if role=='pair_inplace' else 'andn_outplace'
            regions=p.regions_for(ops,hr)
            for r in regions:
                r['mask_invariants']=p.mask_lifetime(ops,r);r['pair_decode']=p.paired_decode(ops,r)
        hints={n:sum(o['mnemonic']==n for o in ops) for n in ('prefetchnta','prefetcht0','prefetchw','vmovntdq','sfence')}
        row=dict(role=role,object_sha256=sha(obj),asm_sha256=sha(asm),text_sha256=hashlib.sha256(raw).hexdigest(),bytes_verified=bytes_ok,
            text_equal79=preserved,forbidden=bad,hints=hints,regions=regions)
        rows.append(row)
        if not bytes_ok or bad or preserved is False:failures.append(role+'字节、ISA或保留对象不符')
        if role=='input256_deferred':
            if len(regions)!=2 or {r['width'] for r in regions}!={32,64}:failures.append('未识别两个完整向量宽区段')
            for r in regions:
                failures.extend('input256_deferred/'+str(r['width'])+'/'+k for k,v in r['checks'].items() if not v)
            if not hints['prefetchnta'] or not hints['vmovntdq'] or not hints['sfence'] or hints['prefetcht0'] or hints['prefetchw']:failures.append('向量路径缓存提示/NT发布不符')
    plan_path=ROOT/'experiments/skylake-input256-deferred-v1.json';plan=read(plan_path)
    mismatches=[n for n,v in plan['source_sha256'].items() if sha(ROOT/n)!=v]
    if mismatches:failures.append('冻结源改变')
    flags=[]
    for e in read(BUILD/'compile_commands.json'):
        expected=any('/skylake-input256-deferred-runtime/'+d+'/' in e['file'] for d in ('andn_inplace','andn_outplace'))
        cmd=e['command'].split();bmi='-mbmi' in cmd
        pixel=e['file'].endswith('/channel_avx2.cpp')
        flags.append(dict(file=e['file'],bmi_expected=expected,bmi_present=bmi,pass_check=expected==bmi and (not pixel or all(f in cmd for f in ('-mavx2','-mtune=skylake','-ffp-contract=off')))))
    if sum(r['bmi_present'] for r in flags)!=2 or not all(r['pass_check'] for r in flags):failures.append('ISA编译许可隔离不符')
    result=dict(purpose=__doc__,accepted=not failures,script_sha256=sha(__file__),plan_sha256=sha(plan_path),build_sha256=sha(BUILD/'build.json'),
        support_sha256={n:sha(HERE/n) for n in ('single_support.py','pair_support.py')},objects=rows,compile_isa_scope=flags,
        failure_reason=failures,source_hash_mismatches=mismatches,candidate_library_loads=0,pixel_calls=0,performance_calls=0,
        scope='本筛查通过仍须独立输入语义/完整对象/分派审计及完整域；失败立即停止，不进入像素或性能。')
    save(HERE/'results.json',result)
    print(json.dumps({'accepted':result['accepted'],'failure_reason':failures,'vector_regions':rows[-1]['regions']},ensure_ascii=False))
    return 0 if result['accepted'] else 1

if __name__=='__main__':raise SystemExit(main())
