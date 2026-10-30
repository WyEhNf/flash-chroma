"""83独立静态审计：ELF字节、RGB标签、两组读写与pending；不执行候选。"""
import importlib.util
import json
from pathlib import Path
import re
import struct
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
BUILD=ROOT/'artifacts/skylake-input256-ordered-linux-build-v1'
OBJECTS=BUILD/'CMakeFiles/jshc_skylake_input256_ordered.dir'
OLD79=ROOT/'artifacts/skylake-pair48-linux-build-v1/CMakeFiles/jshc_skylake_pair48.dir'
OLD81=ROOT/'artifacts/skylake-input256-linux-build-v1/CMakeFiles/jshc_skylake_input256.dir'
BASE=ROOT/'artifacts/skylake-input256-static-v1/independent_audit.py'
module=importlib.util.spec_from_file_location('independent81',BASE)
base=importlib.util.module_from_spec(module);module.loader.exec_module(base)
prior=base.prior
sha,read,args,canon,gpr,compact=base.sha,base.read,base.args,base.canon,base.gpr,base.compact
vreg,vk=base.vreg,base.vk


def vector_output_trace(ops,constants,region):
    """只使用独立输入/调色板标签，逐条解释向量打包和内存地址，不读取root结果。"""
    start,end=int(region['start'],16),int(region['end'],16)
    body=[o for o in ops if o['section']=='.text' and start<=o['a']<=end]
    vectors={}
    for o in ops:
        if o['section']!='.text' or o['a']>=start:continue
        p=args(o['arg'])
        if p and vreg(p[-1]):
            vectors.pop(vk(p[-1]),None)
            if o['a'] in constants:vectors[vk(p[-1])]=constants[o['a']]['bytes']
    first=next(o for o in body if o['op']=='vpermd' and '(' in args(o['arg'])[0])
    source=re.fullmatch(r'(?:0x[0-9a-f]+)?\((%r[a-z0-9]+)\)',args(first['arg'])[0])[1]
    addresses={canon(source):0};scalar_values={}
    palette={int(x['address'],16):x['pixel_offset'] for x in region['palette']}
    inputs={int(x['address'],16):x['offset'] for x in region['input32']}
    store_addresses={int(x['address'],16) for x in region['image_stores']}
    stores=[];unsupported=[];snapshots=[];results_ready=None

    def memory_offset(operand,state):
        m=re.fullmatch(r'(-?0x[0-9a-f]+)?\((%r[a-z0-9]+)(?:,(%r[a-z0-9]+),(1|2|4|8))?\)',operand)
        if not m or canon(m[2]) not in state:return None
        result=state[canon(m[2])]+int(m[1] or '0',16)
        if m[3]:
            if canon(m[3]) not in state:return None
            result+=state[canon(m[3])]*int(m[4])
        return result

    def width_of(reg):return 32 if reg.startswith('%ymm') else 16

    def store_vector(reg,value):
        if value is None:return
        n=width_of(reg)
        vectors[vk(reg)]=list(value[:n])+([0]*16 if n==16 else [])

    def expected(offset,count=32):return [('rgb',i) for i in range(offset,offset+count)]

    for o in body:
        p=args(o['arg']);old=dict(vectors);old_a=dict(addresses);old_s=dict(scalar_values)
        dest=p[-1] if p else ''
        if gpr(dest) and o['op'] not in ('cmp','test','push') and not o['op'].startswith(('j','nop')):
            addresses.pop(canon(dest),None);scalar_values.pop(canon(dest),None)
        if vreg(dest):vectors.pop(vk(dest),None)
        value=None;handled=False
        color=None
        if o['a'] in palette:
            pixel=palette[o['a']]
            color=[('rgb',pixel+i) for i in range(3)]+[('padding',pixel)] if pixel is not None else None
        if o['a'] in inputs:
            mask=old.get(vk(p[1]));offset=inputs[o['a']]
            if mask is not None:
                indexes=struct.unpack('<8I',bytes(mask))
                value=[('input',offset+4*i+j) for i in indexes for j in range(4)]
            handled=True
        elif o['op'] in ('vmovdqa','vmovdqu','vmovaps','vmovups') and len(p)==2 and vreg(dest):
            value=old.get(vk(p[0])) if vreg(p[0]) else constants.get(o['a'],{}).get('bytes');handled=True
        elif o['op']=='vmovd' and vreg(dest):
            value=color if color is not None else old_s.get(canon(p[0])) if gpr(p[0]) else None
            if value is not None:value=value[:4]+[0]*28
            handled=True
        elif o['op']=='vmovq' and vreg(dest):
            value=old.get(vk(p[0])) if vreg(p[0]) else old_s.get(canon(p[0])) if gpr(p[0]) else None
            if value is not None:value=value[:8]+[0]*24
            handled=True
        elif o['op']=='vpinsrd':
            value=old.get(vk(p[2]));part=color if color is not None else old_s.get(canon(p[1])) if gpr(p[1]) else None
            if value is not None and part is not None:
                value=value[:];index=int(p[0][1:],0)*4;value[index:index+4]=part[:4]
            else:value=None
            handled=True
        elif o['op']=='vinserti128':
            low=old.get(vk(p[1]));value=old.get(vk(p[2]))
            if value is not None and low is not None:
                value=value[:];index=int(p[0][1:],0)*16;value[index:index+16]=low[:16]
            else:value=None
            handled=True
        elif o['op']=='vextracti128':
            part=old.get(vk(p[1]));index=int(p[0][1:],0)*16
            value=part[index:index+16] if part is not None else None;handled=True
        elif o['op']=='vpshufb':
            mask=old.get(vk(p[0]));part=old.get(vk(p[1]))
            if mask is not None and part is not None:
                n=width_of(dest);value=[0 if m&128 else part[i//16*16+(m&15)] for i,m in enumerate(mask[:n])]
            handled=True
        elif o['op']=='vpermd':
            part=old.get(vk(p[0]));mask=old.get(vk(p[1]))
            if part is not None and mask is not None:
                value=[part[(i&7)*4+j] for i in struct.unpack('<8I',bytes(mask)) for j in range(4)]
            handled=True
        elif o['op'] in ('vpblendd','vblendps'):
            a,b=old.get(vk(p[1])),old.get(vk(p[2]));imm=int(p[0][1:],0)
            if a is not None and b is not None:value=[(a if imm&(1<<(i//4)) else b)[i] for i in range(width_of(dest))]
            handled=True
        elif o['op'] in ('vperm2i128','vperm2f128'):
            a,b=old.get(vk(p[1])),old.get(vk(p[2]));imm=int(p[0][1:],0)
            if a is not None and b is not None:
                lanes=[b[:16],b[16:32],a[:16],a[16:32]]
                value=([0]*16 if imm&8 else lanes[imm&3])+([0]*16 if imm&128 else lanes[(imm>>4)&3])
            handled=True
        elif o['op'] in ('vpunpckldq','vpunpckhdq','vpunpcklqdq','vpunpckhqdq','vunpcklps','vunpckhps','vunpcklpd','vunpckhpd'):
            a,b=old.get(vk(p[0])),old.get(vk(p[1]));element=8 if 'qdq' in o['op'] or o['op'].endswith('pd') else 4
            high=o['op'] in ('vpunpckhdq','vpunpckhqdq','vunpckhps','vunpckhpd')
            if a is not None and b is not None:
                value=[]
                for lane in range(0,width_of(dest),16):
                    for i in range(lane+(8 if high else 0),lane+(16 if high else 8),element):value+=b[i:i+element]+a[i:i+element]
            handled=True
        elif o['op']=='vpalignr':
            a,b=old.get(vk(p[1])),old.get(vk(p[2]));imm=int(p[0][1:],0)
            if a is not None and b is not None:
                value=[]
                for lane in range(0,width_of(dest),16):value+=(a[lane:lane+16]+b[lane:lane+16]+[0]*32)[imm:imm+16]
            handled=True
        elif o['op'] in ('vpslldq','vpsrldq'):
            a=old.get(vk(p[1]));imm=min(int(p[0][1:],0),16)
            if a is not None:
                value=[]
                for lane in range(0,width_of(dest),16):
                    value+=([0]*imm+a[lane:lane+16-imm]) if o['op']=='vpslldq' else (a[lane+imm:lane+16]+[0]*imm)
            handled=True
        elif o['op'] in ('vpor','vorps'):
            a,b=old.get(vk(p[0])),old.get(vk(p[1]))
            if a is not None and b is not None:value=[y if x==0 else x if y==0 or x==y else None for x,y in zip(a,b)]
            handled=True
        if vreg(dest):
            store_vector(dest,value)
            if not handled:unsupported.append(compact(o))
        if color is not None and gpr(dest):scalar_values[canon(dest)]=color
        if o['op']=='mov' and len(p)==2 and gpr(p[0]) and gpr(dest):
            if canon(p[0]) in old_a:addresses[canon(dest)]=old_a[canon(p[0])]
            if canon(p[0]) in old_s:scalar_values[canon(dest)]=old_s[canon(p[0])]
        elif o['op']=='lea' and gpr(dest):
            address=memory_offset(p[0],old_a)
            if address is not None:addresses[canon(dest)]=address
        elif o['op'] in ('add','sub') and p[0].startswith('$') and gpr(dest):
            if canon(dest) in old_a:addresses[canon(dest)]=old_a[canon(dest)]+int(p[0][1:],0)*(1 if o['op']=='add' else -1)
        if o['a'] in store_addresses:
            offset=memory_offset(p[-1],old_a);value=old.get(vk(p[0]));n=width_of(p[0])
            if not stores:
                results_ready={str(i):[k for k,v in old.items() if v==expected(i)] for i in (0,32,64)}
            stores.append({'address':hex(o['a']),'offset':offset,'bytes':n,'instruction':o['op']+' '+o['arg'],
                'output_tags_exact':offset is not None and value is not None and value[:n]==expected(offset,n)})
        snapshots.append({'address':hex(o['a']),'pending_registers':[k for k,v in vectors.items() if v==expected(64)]})
    checks={'all_output_byte_tags_exact':len(stores)==region['width']*3//32 and all(x['output_tags_exact'] for x in stores),
        'output_offsets_exact':sorted(x['offset'] for x in stores if x['offset'] is not None)==list(range(0,region['width']*3,32)),
        'output_interpreter_complete':not unsupported}
    pending_trace=[]
    if region['width']==64:
        first=stores[0] if stores else None;pending_store=next((s for s in stores if s['offset']==64),None)
        if first and pending_store:
            pending_trace=[s for s in snapshots if int(first['address'],16)<=int(s['address'],16)<int(pending_store['address'],16)]
        checks['three_results_before_first_nt']=bool(results_ready) and all(results_ready[str(i)] for i in (0,32,64))
        checks['pending_continuously_in_vector_register']=bool(pending_trace) and all(s['pending_registers'] for s in pending_trace)
    return {'checks':checks,'stores':stores,'three_result_registers_before_first_store':results_ready,
        'pending_lifetime':pending_trace,'unsupported_vector_writes':unsupported}


def audit_region(ops,constants,width,start,end):
    region=base.audit_region(ops,constants,width,start,end)
    output=vector_output_trace(ops,constants,region)
    region['output_trace']=output;region['checks'].update(output['checks'])
    if width==64:
        region['checks'].pop('all_reads_before_image_store')
        first_inputs=[x for x in region['input32'] if x['offset']<96]
        last_inputs=[x for x in region['input32'] if x['offset']>=96]
        first_reads=first_inputs+[x for name in ('ids','palette') for x in region[name] if x['pixel_offset'] is not None and x['pixel_offset']<96]
        last_reads=last_inputs+[x for name in ('ids','palette') for x in region[name] if x['pixel_offset'] is not None and x['pixel_offset']>=96]
        stores=output['stores'];early=stores[:2];late=stores[2:]
        stamp=lambda rows:[int(x['address'],16) for x in rows]
        region['checks'].update(
            first_group_reads_before_first_nt=bool(early) and len(first_reads)==68 and max(stamp(first_reads))<min(stamp(early)),
            first_two_nt_only_complete_first_line=len(early)==2 and {x['offset'] for x in early}=={0,32},
            second_input_after_two_nt=len(last_inputs)==4 and len(early)==2 and min(stamp(last_inputs))>max(stamp(early)),
            second_input_no_first_line=sorted(x['offset'] for x in last_inputs)==[96,120,144,168] and all(x['offset']//64>0 for x in last_inputs),
            all_second_reads_before_remaining_nt=bool(late) and len(last_reads)==68 and max(stamp(last_reads))<min(stamp(late)),
            remaining_nt_offsets=len(late)==4 and {x['offset'] for x in late}=={64,96,128,160})
        region['group_evidence']={'first_group_reads':len(first_reads),'second_group_reads':len(last_reads),
            'early_stores':early,'late_stores':late,'physical_second_range_inclusive':[96,199],
            'consumed_second_range_inclusive':[96,191],'first_written_range_inclusive':[0,63]}
    return region


def main():
    assert not(HERE/'independent_results.json').exists(), '不覆盖首次独立结果'
    objects=[];regions=[]
    for role,relative in [('linear','channel_avx2.cpp.o'),('andn_inplace','andn_inplace/channel_avx2.cpp.o'),
        ('andn_outplace','andn_outplace/channel_avx2.cpp.o'),('ordered','ordered_inplace/channel_avx2.cpp.o'),('dispatcher','channel_runtime.cpp.o')]:
        obj=OBJECTS/relative;asm=HERE/('independent_'+role+'.asm.txt')
        assert obj.exists(), '构建完成通知之后才执行此独立审计'
        if not asm.exists():
            with asm.open('x',encoding='utf-8') as f:
                f.write(subprocess.check_output(['E:/mingw64/bin/objdump.exe','-dr','--insn-width=15','-C',str(obj)],text=True,encoding='utf-8'))
        ops=prior.parse(asm);sections=prior.executable_sections(obj);covered={k:set() for k in sections};correct=True
        for o in ops:
            correct &= sections[o['section']][o['a']:o['a']+len(o['raw'])]==o['raw'];covered[o['section']].update(range(o['a'],o['a']+len(o['raw'])))
        equal={str(year):sections['.text']==prior.executable_sections(old/relative)['.text']
            for year,old in ((79,OLD79),(81,OLD81))} if role in ('linear','andn_inplace','andn_outplace') else {}
        forbidden=[compact(o) for o in ops if prior.forbidden(o,'linear' if role=='ordered' else role) or re.match(r'v(?:fm|fnm)',o['op'])]
        objects.append({'role':role,'object_sha256':sha(obj),'asm_sha256':sha(asm),'instruction_bytes_match':correct,
            'complete_executable_byte_coverage':all(covered[k]==set(range(len(v))) for k,v in sections.items()),
            'executable_sections':{k:len(v) for k,v in sections.items()},'forbidden':forbidden,'text_equal_prior':equal})
        if role=='ordered':
            constants=base.constants(obj,ops);regions=[audit_region(ops,constants,*r) for r in base.find_regions(ops)]
            constant_records={hex(a):v for a,v in constants.items()}
            hints={m:sum(o['op']==m for o in ops) for m in ('prefetchnta','prefetcht0','prefetchw','sfence')}
    plan_path=ROOT/'experiments/skylake-input256-ordered-v1.json';plan=json.loads(read(plan_path));build=json.loads(read(BUILD/'build.json'))
    mismatch=[p for p,h in plan['source_sha256'].items() if sha(ROOT/p)!=h]
    identity={'plan_build_match':build['plan_sha256']==sha(plan_path),'source_build_match':build['source_sha256']==plan['source_sha256']}
    flags=[]
    for e in json.loads(read(BUILD/'compile_commands.json')):
        cmd=e['command'].split();bmi='-mbmi' in cmd
        expected=any('/skylake-input256-ordered-runtime/'+d+'/' in e['file'] for d in ('andn_inplace','andn_outplace'))
        required=all(x in cmd for x in ('-mavx2','-mtune=skylake','-ffp-contract=off')) if e['file'].endswith('/channel_avx2.cpp') else True
        flags.append({'file':e['file'],'bmi':bmi,'expected_bmi':expected,'pass':bmi==expected and required})
    new=ROOT/'experiments/skylake-input256-ordered-runtime';old=ROOT/'experiments/skylake-input256-runtime'
    exact={p:(new/p).read_bytes()==(old/p).read_bytes() for p in ('channel_avx2.cpp','andn_inplace/channel_avx2.cpp','andn_outplace/channel_avx2.cpp')}
    current=read(new/'channel_runtime.cpp');previous=read(old/'channel_runtime.cpp')
    exact['runtime_identity_only']=current.replace('input256_ordered','input256').replace('return 83;','return 81;')==previous
    exact['header_identity_only']=read(new/'suffix_cache.hpp').replace('input256_ordered','input256')==read(old/'suffix_cache.hpp')
    tu=read(new/'ordered_inplace/channel_avx2.cpp');old_tu=read(old/'input256_inplace/channel_avx2.cpp')
    exact['read_wide_and_pack_before_loop']=tu[:tu.index('    // 前32像素')]==old_tu[:old_tu.index('    // 全部64像素')]
    tail='  // 在普通尾部、调用方读取和OpenMP barrier之前发布非临时写入。'
    exact['sfence_and_exact_tail']=tu[tu.index(tail):].replace('avx2_chain_input256_ordered_mt','avx2_chain_input256_mt')==old_tu[old_tu.index(tail):]
    old82=ROOT/'experiments/skylake-input256-deferred-runtime/deferred_inplace/channel_avx2.cpp'
    added='    // 阻止第二组输入被编译器前移到首行两次NT之间；这不是硬件栅栏。\n    asm volatile("" : : : "memory");\n'
    exact['only_memory_barrier_after82']=tu.count(added)==1 and tu.replace(added,'').replace('avx2_chain_input256_ordered_mt','avx2_chain_input256_deferred_mt')==read(old82)
    exact['three_result_barrier_retained']='asm volatile("" : : "x"(s0),"x"(s1),"x"(pending) : "memory");' in tu
    exact['memory_barrier_count']=tu.count('asm volatile')==4
    dispatch={'effective_workers':'const int workers=omp_in_parallel()?1:static_cast<int>(std::min(blocks,static_cast<size_t>(threads)));' in current,
        'non_openmp_one':'#else\n  const int workers=1;\n#endif' in current,
        'no_bmi_requirement_mt':'if(workers>1)jshc_channel::avx2_chain_input256_ordered_mt(' in current,
        'pair48_single':'else if(h.pair48_supported)jshc_channel::avx2_chain_pair48(' in current,
        'new_getter_capability_only':'return (jshc_cc_capabilities()&2) && !h.direct_index.empty()?1u:0u;' in current,
        'old_getter_preserved':'return h.pair48_supported && !h.direct_index.empty()?1u:0u;' in current}
    failures=[]
    if len(regions)!=2 or {r['width'] for r in regions}!={32,64}:failures.append('两个宽区段没有完整识别')
    for r in regions:
        failures.extend(str(r['width'])+'像素区段/'+name for name,value in r['checks'].items() if not value)
    if not all(identity.values()) or mismatch or not all(exact.values()) or not all(dispatch.values()):failures.append('身份或源分派核对失败')
    if not all(x['pass'] for x in flags) or sum(x['bmi'] for x in flags)!=2:failures.append('ISA许可范围失败')
    if not all(o['instruction_bytes_match'] and o['complete_executable_byte_coverage'] and not o['forbidden'] and all(o['text_equal_prior'].values()) for o in objects):failures.append('对象字节或ISA核对失败')
    if hints!={'prefetchnta':5,'prefetcht0':0,'prefetchw':0,'sfence':1}:failures.append('预取/SFENCE数量改变')
    result={'purpose':__doc__,'accepted':not failures,'failure_reason':failures,
        'decision':'静态失败立即停止本候选；不加载、像素、性能或调参重编',
        'script_sha256':sha(__file__),'base_parser_sha256':sha(BASE),'elf_parser_sha256':sha(base.PRIOR),
        'plan_sha256':sha(plan_path),'build_sha256':sha(BUILD/'build.json'),'identity':identity,'source_hash_mismatches':mismatch,
        'objects':objects,'regions':regions,'resolved_rodata_constants':constant_records,'hints':hints,'compile_flags':flags,
        'unchanged_sources':exact,'dispatch_source_checks':dispatch,
        'bounds_review':'64最大200B≤216B，32最大104B≤120B；64B对齐与192B推进/精确24B尾原字节保留；先写0..63后组物理读取96..199无首行重叠。',
        'limitations':['只核对静态对象及源，完整RGB8/有限/guard/多块实际对齐尚未执行。',
            '无BMI/嵌套/非OMP分派仅源级核对，不冒称真实运行覆盖。','输出标签验证打包与写地址，不据宏指令或寄存器数预测性能。'],
        'root_results_used_as_conclusion':False,'compiler_calls':0,'candidate_library_loads':0,'pixel_calls':0,'performance_calls':0}
    with (HERE/'independent_results.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'accepted':not failures,'failure_reason':failures,
        'regions':[{'width':r['width'],'start':r['start'],'end':r['end'],'instructions':r['instructions'],'checks':r['checks']} for r in regions],
        'sha256':sha(HERE/'independent_results.json')},ensure_ascii=False))


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
