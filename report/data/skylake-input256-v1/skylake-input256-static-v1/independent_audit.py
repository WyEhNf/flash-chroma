"""81独立对象审计：逐节字节、输入字节标签、四ID与真实spill；不执行候选。"""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
BUILD=ROOT/'artifacts/skylake-input256-linux-build-v1'
OBJECTS=BUILD/'CMakeFiles/jshc_skylake_input256.dir'
OLD=ROOT/'artifacts/skylake-pair48-linux-build-v1/CMakeFiles/jshc_skylake_pair48.dir'
PRIOR=ROOT/'artifacts/skylake-pair48-static-v1/independent_audit.py'
spec=importlib.util.spec_from_file_location('prior_parser',PRIOR)
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
sha,read,args,canon,gpr,compact=prior.sha,prior.read,prior.args,prior.canon,prior.gpr,prior.compact


def elf_sections(path):
    data=path.read_bytes()
    assert data[:6]==b'\x7fELF\x02\x01'
    start=struct.unpack_from('<Q',data,40)[0];stride,count,names_index=struct.unpack_from('<HHH',data,58)
    raw=[struct.unpack_from('<IIQQQQIIQQ',data,start+i*stride) for i in range(count)]
    names=data[raw[names_index][4]:raw[names_index][4]+raw[names_index][5]]
    return [{'name':names[s[0]:].split(b'\0',1)[0].decode(),'data':data[s[4]:s[4]+s[5]],'raw':s} for s in raw]


def constants(path,ops):
    sections=elf_sections(path);result={}
    for section in sections:
        if section['raw'][1]!=4 or sections[section['raw'][7]]['name']!='.text':continue
        symbols=sections[section['raw'][6]];strings=sections[symbols['raw'][6]]['data']
        for pos in range(0,len(section['data']),24):
            offset,info,addend=struct.unpack_from('<QQq',section['data'],pos)
            if info&0xffffffff!=2:continue
            name,_,_,index,value,size=struct.unpack_from('<IBBHQQ',symbols['data'],(info>>32)*24)
            if not index or index>=len(sections) or not sections[index]['name'].startswith('.rodata'):continue
            ins=next((o for o in ops if o['section']=='.text' and o['a']<=offset<o['a']+len(o['raw'])),None)
            if ins is None:continue
            # PC32相对位移字段；RIP为本指令末地址，显式加回其与重定位位置之差。
            target=value+addend+ins['a']+len(ins['raw'])-offset
            width=32 if '%ymm' in ins['arg'] else 16
            blob=sections[index]['data'][target:target+width]
            result[ins['a']]={'symbol':strings[name:].split(b'\0',1)[0].decode(),'bytes':list(blob),'section':sections[index]['name'],'offset':target}
    return result


def vreg(s):
    return re.fullmatch(r'%[xy]mm\d+',s) is not None


def vk(s):
    return s.replace('%xmm','v').replace('%ymm','v')


def find_regions(ops):
    regions=[]
    for branch in ops:
        if branch['op'] not in ('jae','ja','jne','jb','jbe'):continue
        m=re.match(r'([0-9a-f]+)\b',branch['arg'])
        if not m or int(m[1],16)>=branch['a']:continue
        start=int(m[1],16)
        body=[o for o in ops if o['section']==branch['section'] and o['function']==branch['function'] and start<=o['a']<=branch['a']]
        loads=[o for o in body if o['op']=='vpermd' and '(' in args(o['arg'])[0] and '%rip' not in o['arg'] and '%rsp' not in o['arg']]
        if len(loads) in (4,8):regions.append((len(loads)*8,start,branch['a']))
    return regions


def audit_region(ops,constant_map,width,start,end):
    body=[o for o in ops if o['section']=='.text' and start<=o['a']<=end]
    vectors={};definitions={}
    for o in ops:
        if o['section']!='.text' or o['a']>=start:continue
        p=args(o['arg'])
        if p and vreg(p[-1]):
            vectors.pop(vk(p[-1]),None);definitions.pop(vk(p[-1]),None)
            if o['a'] in constant_map:
                vectors[vk(p[-1])]=constant_map[o['a']]['bytes'];definitions[vk(p[-1])]=hex(o['a'])
    first=next(o for o in body if o['op']=='vpermd' and '(' in args(o['arg'])[0])
    source=re.fullmatch(r'(?:0x[0-9a-f]+)?\((%r[a-z0-9]+)\)',args(first['arg'])[0])[1]
    state={canon(source):('base','input',0),'rdi':('base','id',0),'rsi':('base','palette',0)}
    inputs,ids,palettes,extracts,store_ops=[],[],[],[],[]
    seen=set();constant_uses=[]
    for o in body:
        p=args(o['arg']);old=dict(state);old_v=dict(vectors)
        dest=canon(p[-1]) if p and gpr(p[-1]) else None
        if dest and o['op'] not in ('cmp','test','push') and not o['op'].startswith(('j','nop')):state.pop(dest,None)
        if p and vreg(p[-1]):vectors.pop(vk(p[-1]),None)
        pal=re.search(r'\(%rsi,(%[a-z0-9]+),4\)',o['arg'])
        if pal:
            value=old.get(canon(pal[1]));group=set(range(value[1]//12*12,value[1]//12*12+12,3)) if value and value[0]=='id' else set()
            palettes.append({'address':hex(o['a']),'pixel_offset':value[1] if value else None,'four_ids_ready':bool(group) and group<=seen})
        if o['op']=='vpermd' and '(' in p[0] and '%rip' not in p[0] and '%rsp' not in p[0]:
            m=re.fullmatch(r'(0x[0-9a-f]+)?\((%r[a-z0-9]+)\)',p[0]);offset=int(m[1] or '0',16) if m else -1
            mask=old_v.get(vk(p[1]));valid=bool(m) and old.get(canon(m[2]))==('base','input',0)
            correct=mask==list(struct.pack('<8I',0,1,2,3,3,4,5,6))
            inputs.append({'address':hex(o['a']),'offset':offset,'bytes':32,'memory_base_valid':valid,'permd_mask_correct':correct})
            constant_uses.append({'address':hex(o['a']),'register':p[1],'initializer':definitions.get(vk(p[1])),'correct':correct})
            if correct:
                indexes=struct.unpack('<8I',bytes(mask));vectors[vk(p[-1])]=[('input',offset+4*i+j) for i in indexes for j in range(4)]
        elif o['op']=='vpshufb':
            mask=old_v.get(vk(p[0]));value=old_v.get(vk(p[1]))
            if value and any(isinstance(x,tuple) and x[0]=='input' for x in value):
                expected=[0,1,2,255,3,4,5,255,6,7,8,255,9,10,11,255]*2
                correct=mask==expected
                constant_uses.append({'address':hex(o['a']),'register':p[0],'initializer':definitions.get(vk(p[0])),'correct':correct})
                if correct:vectors[vk(p[-1])]=[0 if m&128 else value[i//16*16+(m&15)] for i,m in enumerate(mask)]
        elif o['op']=='vextracti128' and p[0]=='$0x1':
            value=old_v.get(vk(p[1]))
            if value:vectors[vk(p[-1])]=value[16:32]+[0]*16
        elif (o['op']=='vmovd' and vreg(p[0]) and dest) or (o['op']=='vpextrd' and dest):
            value=old_v.get(vk(p[0] if o['op']=='vmovd' else p[1]));index=0 if o['op']=='vmovd' else int(p[0][1:],0)
            chunk=value[index*4:index*4+4] if value else None
            valid=bool(chunk) and len(chunk)==4 and chunk[3]==0 and all(isinstance(x,tuple) and x[0]=='input' for x in chunk[:3])
            valid=valid and [x[1] for x in chunk[:3]]==list(range(chunk[0][1],chunk[0][1]+3)) and not prior.reg64(p[-1])
            extracts.append({'address':hex(o['a']),'zero_extended_rgb24':bool(valid),'pixel_offset':chunk[0][1] if valid else None})
            if valid:state[dest]=('pixel24',chunk[0][1])
        elif o['op']=='movzbl' and re.fullmatch(r'\(%rdi,%[a-z0-9]+,1\)',p[0]):
            index=re.fullmatch(r'\(%rdi,(%[a-z0-9]+),1\)',p[0])[1];value=old.get(canon(index))
            valid=value is not None and value[0]=='pixel24'
            ids.append({'address':hex(o['a']),'correct':valid,'pixel_offset':value[1] if valid else None})
            if valid:state[dest]=('id',value[1]);seen.add(value[1])
        elif o['op']=='mov' and len(p)==2 and gpr(p[0]) and dest:
            if canon(p[0]) in old:state[dest]=old[canon(p[0])]
        elif o['op']=='add' and dest and p[0].startswith('$'):
            value=old.get(dest)
            if value and value[0]=='base':state[dest]=(value[0],value[1],value[2]+int(p[0][1:],0))
        if o['op'].startswith('vmov') and len(p)==2 and '(' in p[-1]:store_ops.append(o)
    frame=any(o['section']=='.text' and o['a']<start and o['op']=='mov' and o['arg']=='%rsp,%rbp' for o in ops)
    stack=[o for o in body if '%rsp' in o['arg'] or frame and '%rbp' in o['arg']]
    image=[o for o in store_ops if '%rsp' not in o['arg'] and not(frame and '%rbp' in o['arg'])]
    reads=inputs+ids+palettes
    checks={'complete_body':body[0]['a']==start and body[-1]['a']==end,
        'one_input32_per8':len(inputs)==width//8 and sorted(x['offset'] for x in inputs)==list(range(0,width*3,24)) and all(x['memory_base_valid'] for x in inputs),
        'exact_vector_masks':len(constant_uses)==width//4 and all(x['correct'] and x['initializer'] for x in constant_uses),
        'zero_extended_indices':len(extracts)==width and all(x['zero_extended_rgb24'] for x in extracts),
        'exact_id_loads':len(ids)==width and all(x['correct'] for x in ids) and seen==set(range(0,width*3,3)),
        'exact_palette_loads':len(palettes)==width and {x['pixel_offset'] for x in palettes}==set(range(0,width*3,3)),
        'four_id_before_palette':all(x['four_ids_ready'] for x in palettes),
        'all_reads_before_image_store':bool(image) and max(int(x['address'],16) for x in reads)<image[0]['a'],
        'image_store_count':len(image)==width*3//32,
        'image_store_kind':all(o['op']==('vmovntdq' if width==64 else 'vmovdqu') and '%ymm' in args(o['arg'])[0] for o in image),
        'no_stack':not stack,'no_loop_constant_load':not any('%rip' in o['arg'] for o in body)}
    return {'width':width,'start':hex(start),'end':hex(end),'instructions':len(body),'checks':checks,'input32':inputs,
        'constant_uses':constant_uses,'extracts':extracts,'ids':ids,'palette':palettes,'stack_references':[compact(o) for o in stack],
        'image_stores':[compact(o) for o in image],'maximum_input_bytes':max(x['offset'] for x in inputs)+32,
        'instruction_counts':{m:sum(o['op']==m for o in body) for m in ('vpermd','vpshufb','vextracti128','vpextrd','vmovd','vmovntdq','vmovdqa','vmovdqu')}}


def main():
    assert not(HERE/'independent_results.json').exists()
    objects=[];regions=[]
    for role,relative in [('linear','channel_avx2.cpp.o'),('andn_inplace','andn_inplace/channel_avx2.cpp.o'),('andn_outplace','andn_outplace/channel_avx2.cpp.o'),
        ('input256','input256_inplace/channel_avx2.cpp.o'),('dispatcher','channel_runtime.cpp.o')]:
        obj=OBJECTS/relative;asm=HERE/('independent_'+role+'.asm.txt')
        if not asm.exists():
            with asm.open('x',encoding='utf-8') as f:
                f.write(subprocess.check_output(['E:/mingw64/bin/objdump.exe','-dr','--insn-width=15','-C',str(obj)],text=True,encoding='utf-8'))
        ops=prior.parse(asm);sections=prior.executable_sections(obj);covered={k:set() for k in sections};correct=True
        for o in ops:
            correct &= sections[o['section']][o['a']:o['a']+len(o['raw'])]==o['raw'];covered[o['section']].update(range(o['a'],o['a']+len(o['raw'])))
        complete=all(covered[k]==set(range(len(v))) for k,v in sections.items())
        bad=[compact(o) for o in ops if prior.forbidden(o,'linear' if role=='input256' else role)]
        same=sections['.text']==prior.executable_sections(OLD/relative)['.text'] if role in ('linear','andn_inplace','andn_outplace') else None
        objects.append({'role':role,'object_sha256':sha(obj),'asm_sha256':sha(asm),'instruction_bytes_match':correct,
            'complete_executable_byte_coverage':complete,'executable_sections':{k:len(v) for k,v in sections.items()},'forbidden':bad,'text_equal79':same})
        if role=='input256':
            const=constants(obj,ops)
            regions=[audit_region(ops,const,*r) for r in find_regions(ops)]
            constant_records={hex(a):v for a,v in const.items()}
            hints={m:sum(o['op']==m for o in ops) for m in ('prefetchnta','prefetcht0','prefetchw','sfence')}
    plan_path=ROOT/'experiments/skylake-input256-v1.json';plan=json.loads(read(plan_path));build=json.loads(read(BUILD/'build.json'))
    mismatch=[p for p,h in plan['source_sha256'].items() if sha(ROOT/p)!=h]
    identity={'plan_build_match':build['plan_sha256']==sha(plan_path),'source_build_match':build['source_sha256']==plan['source_sha256']}
    flags=[]
    for e in json.loads(read(BUILD/'compile_commands.json')):
        cmd=e['command'].split();bmi='-mbmi' in cmd
        expected=any('/skylake-input256-runtime/'+d+'/' in e['file'] for d in ('andn_inplace','andn_outplace'))
        required=all(x in cmd for x in ('-mavx2','-mtune=skylake','-ffp-contract=off')) if e['file'].endswith('/channel_avx2.cpp') else True
        flags.append({'file':e['file'],'bmi':bmi,'expected_bmi':expected,'pass':bmi==expected and required})
    new=ROOT/'experiments/skylake-input256-runtime';old=ROOT/'experiments/skylake-pair48-runtime'
    exact={p:(new/p).read_bytes()==(old/p).read_bytes() for p in ('channel_avx2.cpp','andn_inplace/channel_avx2.cpp','andn_outplace/channel_avx2.cpp')}
    current=read(new/'channel_runtime.cpp');previous=read(old/'channel_runtime.cpp')
    exact['handle']=current[current.index('struct Handle {'):current.index('static_assert')]==previous[previous.index('struct Handle {'):previous.index('static_assert')]
    exact['true_outplace']=current[current.index('void apply_to('):current.index('void prepare_palette(')]==previous[previous.index('void apply_to('):previous.index('void prepare_palette(')]
    dispatch={'effective_workers':'const int workers=omp_in_parallel()?1:static_cast<int>(std::min(blocks,static_cast<size_t>(threads)));' in current,
        'non_openmp_one':'#else\n  const int workers=1;\n#endif' in current,
        'no_bmi_requirement_mt':'if(workers>1)jshc_channel::avx2_chain_input256_mt(' in current,
        'pair48_single':'else if(h.pair48_supported)jshc_channel::avx2_chain_pair48(' in current,
        'new_getter_capability_only':'return (jshc_cc_capabilities()&2) && !h.direct_index.empty()?1u:0u;' in current,
        'old_getter_preserved':'return h.pair48_supported && !h.direct_index.empty()?1u:0u;' in current}
    failures=[]
    if len(regions)!=2 or {r['width'] for r in regions}!={32,64}:failures.append('两个宽区段没有完整识别')
    for r in regions:
        for name,value in r['checks'].items():
            if not value:failures.append(str(r['width'])+'像素区段/'+name)
    if not all(identity.values()) or mismatch or not all(exact.values()) or not all(dispatch.values()):failures.append('身份或源分派核对失败')
    if not all(x['pass'] for x in flags) or sum(x['bmi'] for x in flags)!=2:failures.append('ISA许可范围失败')
    if not all(o['instruction_bytes_match'] and o['complete_executable_byte_coverage'] and not o['forbidden'] and o['text_equal79'] is not False for o in objects):failures.append('对象字节或ISA核对失败')
    result={'purpose':__doc__,'accepted':not failures,'failure_reason':failures,'decision':'静态门槛失败时停止本候选，禁止像素/性能；不调参重编',
        'script_sha256':sha(__file__),'parser_sha256':sha(PRIOR),'plan_sha256':sha(plan_path),'build_sha256':sha(BUILD/'build.json'),
        'identity':identity,'source_hash_mismatches':mismatch,'objects':objects,'regions':regions,'resolved_rodata_constants':constant_records,
        'hints':hints,'compile_flags':flags,'unchanged_sources':exact,'dispatch_source_checks':dispatch,
        'bounds_review':'输入200/104B受216/120B宽窗口保护；24B精确尾和run除入口名外沿78；完整验证未运行。',
        'spill_classification':'rsp/frame内存操作单列；图像store只计非栈目标，不能把中间YMM保存当作输出提前写。',
        'limitations':['只审计对象与源，不执行完整RGB8；静态字节标签只追踪输入到ID/palette，不模拟最终RGB打包所有指令。',
            '旧pair与linear对象.text逐字节等79，沿用其已验语义；本次未重跑旧性能。','无BMI/嵌套/非OMP路径只做源级核对，未伪造运行覆盖。'],
        'root_results_used_as_conclusion':False,'compiler_calls':0,'candidate_library_loads':0,'pixel_calls':0,'performance_calls':0}
    with (HERE/'independent_results.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'accepted':not failures,'failure_reason':failures,'regions':[{'width':r['width'],'start':r['start'],'end':r['end'],
        'instructions':r['instructions'],'checks':r['checks'],'stack':r['stack_references']} for r in regions],
        'sha256':sha(HERE/'independent_results.json')},ensure_ascii=False))


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
