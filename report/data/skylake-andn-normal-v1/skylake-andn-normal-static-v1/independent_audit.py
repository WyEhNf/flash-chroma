"""80独立静态审计：逐节复核对象字节、四ID依赖和普通写；不执行候选。"""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
BUILD=ROOT/'artifacts/skylake-andn-normal-linux-build-v1'
OBJECTS=BUILD/'CMakeFiles/jshc_skylake_andn_normal.dir'
OLD=ROOT/'artifacts/skylake-pair48-linux-build-v1/CMakeFiles/jshc_skylake_pair48.dir'
PRIOR=ROOT/'artifacts/skylake-pair48-static-v1/independent_audit.py'
spec=importlib.util.spec_from_file_location('prior_independent',PRIOR)
prior=importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
sha,read,args,canon,gpr,reg64,compact=prior.sha,prior.read,prior.args,prior.canon,prior.gpr,prior.reg64,prior.compact


def normal_region(ops,width,start,end):
    body=[o for o in ops if o['section']=='.text' and start<=o['a']<=end]
    andns=[o for o in body if o['op']=='andn']
    mask_names={canon(args(o['arg'])[1]) for o in andns}
    assert len(mask_names)==1
    mask=next(iter(mask_names))
    definitions=[o for o in ops if o['section']=='.text' and o['a']<start and o['op']=='mov'
        and args(o['arg'])[0]=='$0xff000000' and canon(args(o['arg'])[-1])==mask]
    definition=definitions[-1]
    pre_writes=[compact(o) for o in ops if definition['a']<o['a']<start and o['section']=='.text'
        and gpr(args(o['arg'])[-1]) and canon(args(o['arg'])[-1])==mask
        and o['op'] not in ('cmp','test','push') and not o['op'].startswith('j')]
    source=re.fullmatch(r'(?:0x[0-9a-f]+)?\((%r[a-z0-9]+)\)',args(andns[0]['arg'])[0])[1]
    state={canon(source):('base','input',0),'rdi':('base','id',0),'rsi':('base','palette',0),mask:('constant',0xff000000)}
    inputs,ids,palettes,stores,mask_uses,mask_writes=[],[],[],[],[],[]
    seen=set()
    for o in body:
        p=args(o['arg']); old=dict(state)
        dest=canon(p[-1]) if p and gpr(p[-1]) else None
        writes=dest and o['op'] not in ('cmp','test','push') and not o['op'].startswith(('j','nop'))
        if writes:
            state.pop(dest,None)
            if dest==mask:mask_writes.append(compact(o))
        pal=re.search(r'\(%rsi,(%[a-z0-9]+),4\)',o['arg'])
        if pal:
            value=old.get(canon(pal[1]))
            group=set(range(value[1]//12*12,value[1]//12*12+12,3)) if value and value[0]=='id' else set()
            palettes.append({'address':hex(o['a']),'pixel_offset':value[1] if value else None,
                'four_ids_ready':bool(group) and group<=seen and old.get('rsi')==('base','palette',0)})
        if o['op']=='andn':
            m=re.fullmatch(r'(0x[0-9a-f]+)?\((%r[a-z0-9]+)\)',p[0])
            base=old.get(canon(m[2])) if m else None
            valid=bool(m) and gpr(p[1]) and not reg64(p[1]) and gpr(p[2]) and not reg64(p[2])
            valid=valid and o['raw'][0]==0xc4 and not(o['raw'][2]&0x80) and o['raw'][3]==0xf2
            off=int(m[1] or '0',16) if m else -1
            inputs.append({'address':hex(o['a']),'byte_offset':off,'valid':bool(valid) and base==('base','input',0)})
            mask_uses.append({'address':hex(o['a']),'correct':old.get(canon(p[1]))==('constant',0xff000000)})
            state[dest]=('pixel24',off)
        elif o['op']=='movzbl' and re.fullmatch(r'\(%rdi,%[a-z0-9]+,1\)',p[0]):
            index=re.fullmatch(r'\(%rdi,(%[a-z0-9]+),1\)',p[0])[1]
            value=old.get(canon(index));valid=value and value[0]=='pixel24' and old.get('rdi')==('base','id',0)
            ids.append({'address':hex(o['a']),'pixel_offset':value[1] if value else None,'correct':bool(valid)})
            if valid:state[dest]=('id',value[1]);seen.add(value[1])
        elif o['op']=='mov' and len(p)==2 and gpr(p[0]) and dest:
            value=old.get(canon(p[0]))
            if value:state[dest]=value
        elif o['op']=='add' and dest and p[0].startswith('$'):
            value=old.get(dest)
            if value and value[0]=='base':state[dest]=(value[0],value[1],value[2]+int(p[0][1:],0))
        if o['op'].startswith('vmov') and len(p)==2 and '(' in p[-1]:
            m=re.fullmatch(r'(-?0x[0-9a-f]+)?\((%r[a-z0-9]+)\)',p[-1])
            base=old.get(canon(m[2])) if m else None
            relative=base[2]+int(m[1] or '0',16) if m and base and base[0:2]==('base','input') else None
            stores.append({'address':hex(o['a']),'instruction':o['op']+' '+o['arg'],'relative_byte':relative,
                'normal_32byte':o['op']==('vmovdqa' if width==64 else 'vmovdqu') and bool(re.fullmatch(r'%ymm\d+',p[0]))})
    frame=any(o['section']=='.text' and o['a']<start and o['op']=='mov' and o['arg']=='%rsp,%rbp' for o in ops)
    stack=[compact(o) for o in body if '%rsp' in o['arg'] or frame and '%rbp' in o['arg']]
    checks={'complete_range':body[0]['a']==start and body[-1]['a']==end,
        'input_offsets':sorted(x['byte_offset'] for x in inputs)==list(range(0,width*3,3)),
        'all_mem32_andn':len(inputs)==width and all(x['valid'] for x in inputs),
        'mask_outside':not pre_writes and not mask_writes and all(x['correct'] for x in mask_uses),
        'all_ids':len(ids)==width and all(x['correct'] for x in ids) and seen==set(range(0,width*3,3)),
        'all_palette':len(palettes)==width and {x['pixel_offset'] for x in palettes}==set(range(0,width*3,3)),
        'four_id_barrier':all(x['four_ids_ready'] for x in palettes),'no_stack':not stack,
        'all_reads_before_stores':max(int(x['address'],16) for x in inputs+ids+palettes)<min(int(x['address'],16) for x in stores),
        'normal_store_coverage':len(stores)==width*3//32 and all(x['normal_32byte'] for x in stores)
            and sorted(x['relative_byte'] for x in stores)==list(range(0,width*3,32)),
        'loop_backedge':body[-1]['op']=='jae' and int(body[-1]['arg'].split()[0],16)==start,
        'no_loop_constant_load':not any('(%rip)' in o['arg'] for o in body)}
    return {'role':'normal_inplace','width':width,'start':hex(start),'end':hex(end),'instructions':len(body),
        'maximum_input_bytes':max(x['byte_offset'] for x in inputs)+4,'checks':checks,
        'mask_initializer':compact(definition),'mask_uses':mask_uses,'mask_writes':mask_writes,
        'inputs':inputs,'ids':ids,'palette':palettes,'stores':stores,'stack_references':stack}


def main():
    assert not(HERE/'independent-audit.json').exists()
    objdump='E:/mingw64/bin/objdump.exe'
    specs={'andn_inplace':[('inplace',64,0xf8,0x7b4,321,True),('inplace',32,0x7f0,0xb60,170,True)],
        'andn_outplace':[('outplace',64,0x100,0x7c2,319,True),('outplace',32,0x81d,0xb81,168,False)]}
    objects,regions=[],[]
    for role,relative in [('linear','channel_avx2.cpp.o'),('andn_inplace','andn_inplace/channel_avx2.cpp.o'),
        ('andn_outplace','andn_outplace/channel_avx2.cpp.o'),('normal_inplace','normal_inplace/channel_avx2.cpp.o'),('dispatcher','channel_runtime.cpp.o')]:
        obj=OBJECTS/relative;asm=HERE/('independent-'+role+'.asm.txt')
        if not asm.exists():
            text=subprocess.check_output([objdump,'-dr','--insn-width=15','-C',str(obj)],text=True,encoding='utf-8')
            with asm.open('x',encoding='utf-8') as f:f.write(text)
        ops,sections=prior.parse(asm),prior.executable_sections(obj)
        covered={k:set() for k in sections};bytes_ok=True
        for o in ops:
            bytes_ok &= sections[o['section']][o['a']:o['a']+len(o['raw'])]==o['raw']
            covered[o['section']].update(range(o['a'],o['a']+len(o['raw'])))
        complete=all(covered[k]==set(range(len(v))) for k,v in sections.items())
        isa_role='andn_inplace' if role=='normal_inplace' else role
        bad=[compact(o) for o in ops if prior.forbidden(o,isa_role)]
        same=sections['.text']==prior.executable_sections(OLD/relative)['.text'] if role in ('linear','andn_inplace','andn_outplace') else None
        hint_counts={h:sum(o['op']==h for o in ops) for h in ('prefetchnta','prefetcht0','prefetchw','vmovntdq','sfence')}
        rows={'role':role,'object_sha256':sha(obj),'asm_sha256':sha(asm),'text_equal79':same,
            'parsed_instructions':len(ops),'instruction_bytes_match':bytes_ok,'complete_executable_byte_coverage':complete,
            'executable_sections':{k:len(v) for k,v in sections.items()},'forbidden':bad,'hints':hint_counts}
        objects.append(rows)
        for s in specs.get(role,[]):regions.append(prior.audit_region(ops,*s))
        if role=='normal_inplace':
            regions.extend(normal_region(ops,*s) for s in [(64,0xf0,0x6dd),(32,0x710,0xa08)])
            rows['ordinary_only']=hint_counts==dict(prefetchnta=0,prefetcht0=5,prefetchw=0,vmovntdq=0,sfence=0)
    plan_path=ROOT/'experiments/skylake-andn-normal-v1.json';plan=json.loads(read(plan_path));build=json.loads(read(BUILD/'build.json'))
    mismatch=[k for k,v in plan['source_sha256'].items() if sha(ROOT/k)!=v]
    formal=json.loads(read(HERE/'results-v2.json'))
    identity={'plan_matches_build':build['plan_sha256']==sha(plan_path),'sources_match_build':build['source_sha256']==plan['source_sha256'],
        'formal_accepted':formal['accepted'],'formal_plan':formal['plan_sha256']==sha(plan_path),'formal_build':formal['build_sha256']==sha(BUILD/'build.json')}
    flags=[]
    for e in json.loads(read(BUILD/'compile_commands.json')):
        cmd=e['command'].split();bmi='-mbmi' in cmd
        expected=any('/skylake-andn-normal-runtime/'+d+'/' in e['file'] for d in ('andn_inplace','andn_outplace','normal_inplace'))
        pixel=e['file'].endswith('/channel_avx2.cpp')
        required=all(x in cmd for x in ('-mavx2','-mtune=skylake','-ffp-contract=off')) if pixel else True
        flags.append({'file':e['file'],'bmi':bmi,'expected_bmi':expected,'pass':bmi==expected and required})
    source=ROOT/'experiments/skylake-andn-normal-runtime';old=ROOT/'experiments/skylake-pair48-runtime'
    exact={p:sha(source/p)==sha(old/p) for p in ('channel_avx2.cpp','andn_inplace/channel_avx2.cpp','andn_outplace/channel_avx2.cpp')}
    runtime=read(source/'channel_runtime.cpp')
    normalized=runtime.replace('andn_normal','pair48').replace('return 80;','return 79;')
    # 删除本次唯一新增的分派分支后，另逐段复核非OMP workers与只读getter文字；不声称自动证明完整CFG。
    dispatch={'one_time_bmi_detection':runtime.count('__builtin_cpu_supports("bmi")')==1,
        'effective_workers':re.search(r'const int workers=omp_in_parallel\(\)\?1:static_cast<int>\(std::min\(blocks,static_cast<size_t>\(threads\)\)\);',runtime) is not None,
        'non_openmp_one': '#else\n  const int workers=1;\n#endif' in runtime,
        'normal_only_workers_gt1':'if(workers>1)jshc_channel::avx2_chain_andn_normal_mt(' in runtime,
        'single_pair48':'else jshc_channel::avx2_chain_pair48(' in runtime,
        'outplace_pair48':'if(h.andn_normal_supported)jshc_channel::avx2_chain_pair48_to(' in runtime,
        'fallback_linear':'else jshc_channel::avx2_chain_adaptive_linear(' in runtime and 'else jshc_channel::avx2_chain_adaptive_linear_to(' in runtime,
        'static_contiguous':runtime.count('schedule(static)')==2 and 'schedule(static,1)' not in runtime,
        'getter_capability':'return h.andn_normal_supported && !h.direct_index.empty()?1u:0u;' in runtime,
        'same_address_delegates_apply':'if(source==destination) {apply(h,destination,bytes,kernel,threads);return;}' in runtime}
    verifier=ROOT/'scripts/verify_skylake_andn_normal_linux.py';tree=ast.parse(read(verifier))
    fixture={'source_sha256':sha(verifier),'ast_parses':isinstance(tree,ast.Module),'pixels':65793,'blocks':2,'vector_pixels_per_block':[65536,256],
        'alignment_address':'((raw+63)&~63)+offset，offset严格0..63；最多消耗126字节前缀，+255分配保证双侧哨兵',
        'expected':'直接按原RGB坐标读取独立cube，非调用候选生成','full_chunk_pixels':262144,
        'scope':'新增64次仅候选四级AVX2请求4线程；源码workers=2选择normal；旧矩阵不变。未运行本夹具。'}
    passed=all(identity.values()) and not mismatch and all(exact.values()) and all(dispatch.values()) and all(x['pass'] for x in flags) and sum(x['bmi'] for x in flags)==3
    passed &= len(regions)==6 and all(all(r['checks'].values()) for r in regions)
    passed &= all(x['instruction_bytes_match'] and x['complete_executable_byte_coverage'] and not x['forbidden'] and x['text_equal79'] is not False and x.get('ordinary_only',True) for x in objects)
    result={'purpose':__doc__,'accepted':bool(passed),'script_sha256':sha(__file__),'prior_parser_sha256':sha(PRIOR),
        'plan_sha256':sha(plan_path),'build_sha256':sha(BUILD/'build.json'),'formal_result_sha256':sha(HERE/'results-v2.json'),
        'objects':objects,'regions':regions,'identity':identity,'compile_flags':flags,'source_hash_mismatches':mismatch,'unchanged_sources':exact,
        'dispatch_source_checks':dispatch,'verification_fixture_review':fixture,
        'bounds':'normal:64/32入口p+72/40，最大输入读取193/97字节，小于216/120；精确24字节尾不变。64B标量前缀后每次增加192字节，六条vmovdqa地址均保持32B对齐。',
        'stack_scope':'仅六个64/32热区无栈；normal序言保存源指针，初始预取及区段入口读取栈地址，未声称整函数无栈。',
        'limitations':['不加载库或执行像素；静态通过仅允许后续完整正确性验证。','不是无BMI/非OpenMP/嵌套OpenMP实际运行验证；这些分支按源码和编译ISA审计。','复用79独立解析器和pair追踪函数，normal另行逐条追踪所有GPR失效；未使用root静态支持模块。'],
        'candidate_library_loads':0,'pixel_calls':0,'performance_calls':0,'compiler_calls':0}
    with (HERE/'independent-audit.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'accepted':bool(passed),'regions':[{'width':r['width'],'start':r['start'],'instructions':r['instructions'],'checks':r['checks']} for r in regions],
        'objects':objects,'sha256':sha(HERE/'independent-audit.json')},ensure_ascii=False))


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
