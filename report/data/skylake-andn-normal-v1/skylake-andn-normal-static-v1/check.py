"""80三专用对象静态门槛：保留79对象字节、新普通写mem32及分派隔离；无原生调用。"""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BUILD=ROOT/'artifacts/skylake-andn-normal-linux-build-v1'
OBJECTS=BUILD/'CMakeFiles/jshc_skylake_andn_normal.dir'
OLD=ROOT/'artifacts/skylake-pair48-linux-build-v1/CMakeFiles/jshc_skylake_pair48.dir'


def load(name):
    spec=importlib.util.spec_from_file_location(name,HERE/(name+'.py'))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    if (HERE/'results.json').exists():
        raise ValueError('不得覆盖静态原件')
    single,pair=load('single_support'),load('pair_support')
    rows,checks,failures=[],[],[]
    for role,folder,helper,helper_role in [('pair_inplace','andn_inplace',pair,'andn_inplace'),
        ('pair_outplace','andn_outplace',pair,'andn_outplace'),('normal_inplace','normal_inplace',single,'andn_inplace')]:
        obj=OBJECTS/folder/'channel_avx2.cpp.o'
        target=HERE/(role+'.asm.txt')
        text=subprocess.check_output(['objdump','-d','--insn-width=15','-C',str(obj)],text=True,encoding='utf-8')
        with target.open('x',encoding='utf-8') as stream:
            stream.write(text)
        ops=helper.read_ops(target)
        raw=helper.text_section(obj)
        bytes_ok=all(raw[o['offset']:o['offset']+len(o['bytes'])]==bytes.fromhex(' '.join(o['bytes'])) for o in ops)
        bad=[o for o in ops if helper.forbidden(o,helper_role)]
        regions=helper.regions_for(ops,helper_role)
        hint_counts={name:sum(o['mnemonic']==name for o in ops) for name in ('prefetchnta','prefetcht0','prefetchw','vmovntdq','sfence')}
        preserved=helper.text_section(OLD/folder/'channel_avx2.cpp.o')==raw if role.startswith('pair_') else None
        row={'role':role,'object_sha256':sha(obj),'asm_sha256':sha(target),'bytes_verified':bytes_ok,
             'text_sha256':hashlib.sha256(raw).hexdigest(),'forbidden':bad,'hints':hint_counts,
             'text_equal79':preserved,'regions':regions}
        rows.append(row)
        if not bytes_ok or bad or preserved is False:
            failures.append(role+'字节、ISA或79保留对象不符')
        if len(regions)!=2 or {r['width'] for r in regions}!={32,64}:
            failures.append(role+'未完整识别两个宽区段')
        if role=='normal_inplace' and (hint_counts['prefetchnta'] or hint_counts['prefetchw'] or hint_counts['vmovntdq'] or hint_counts['sfence'] or not hint_counts['prefetcht0']):
            failures.append('新普通写提示或发布指令不符')
        for region in regions:
            region['mask_invariants']=helper.mask_lifetime(ops,region)
            decode_ok=True
            if role.startswith('pair_'):
                region['pair_decode']=pair.paired_decode(ops,region)
                d=region['pair_decode']
                decode_ok=d['one_source_base'] and d['correct_pixel_indices'] and d['paired_offsets'] and d['maximum_input_bytes']==region['width']*3+2
            check={'role':role,'width':region['width'],'instructions':region['instructions'],
                'no_stack':not region['stack_references'],'andn_valid':not region['bad_andn_operands'] and region['andn_count']*(2 if role.startswith('pair_') else 1)==region['width'],
                'mask_valid':all(item['pass_check'] for item in region['mask_invariants']) and bool(region['mask_invariants']),
                'four_id':region['barrier']['four_id_before_palette'] and region['barrier']['id_loads']==region['barrier']['palette_loads']==region['width'],
                'all_reads_before_store':region['all_palette_reads_before_first_store'],'pair_decode_valid':decode_ok,
                'complete_region':region['kind']!='at_most_once_straightline' or bool(region['straightline_guards']) and region['no_internal_branches']}
            checks.append(check)
            if not all(v for k,v in check.items() if k not in ('role','width','instructions')):
                failures.append(role+'/'+str(region['width'])+'宽区段门槛失败')
    # 泛型分派对象不能带入专用ISA；其调用目标/条件另外做源码独立审计。
    dispatcher=OBJECTS/'channel_runtime.cpp.o'
    target=HERE/'dispatcher.asm.txt'
    with target.open('x',encoding='utf-8') as stream:
        stream.write(subprocess.check_output(['objdump','-d','--insn-width=15','-C',str(dispatcher)],text=True,encoding='utf-8'))
    dispatch_ops=single.read_ops(target)
    dispatch_raw=single.text_section(dispatcher)
    dispatch_bad=[o for o in dispatch_ops if (single.forbidden(o,'linear') and not o['mnemonic'].startswith('call')) or o['mnemonic'].startswith('v')]
    dispatch_bytes=all(dispatch_raw[o['offset']:o['offset']+len(o['bytes'])]==bytes.fromhex(' '.join(o['bytes'])) for o in dispatch_ops)
    if dispatch_bad or not dispatch_bytes:
        failures.append('分派器ISA或字节不符')
    plan_path=ROOT/'experiments/skylake-andn-normal-v1.json'
    plan=read(plan_path)
    mismatches=[p for p,h in plan['source_sha256'].items() if sha(ROOT/p)!=h]
    if mismatches:
        failures.append('冻结源改变')
    scope=[]
    for entry in read(BUILD/'compile_commands.json'):
        expected=any('/skylake-andn-normal-runtime/'+folder+'/' in entry['file'] for folder in ('andn_inplace','andn_outplace','normal_inplace'))
        present=bool(re.search(r'(?:^|\s)-mbmi(?:\s|$)',entry['command']))
        flags_ok=all(flag in entry['command'].split() for flag in ('-mavx2','-mtune=skylake','-ffp-contract=off')) if entry['file'].endswith('/channel_avx2.cpp') else True
        scope.append({'file':entry['file'],'bmi_expected':expected,'bmi_present':present,'pass':expected==present and flags_ok})
    if sum(r['bmi_present'] for r in scope)!=3 or not all(r['pass'] for r in scope):
        failures.append('三个专用TU的ISA范围不符')
    result={'purpose':__doc__,'accepted':not failures,'script_sha256':sha(Path(__file__)),
        'support_sha256':{name:sha(HERE/name) for name in ('single_support.py','pair_support.py')},
        'plan_sha256':sha(plan_path),'build_sha256':sha(BUILD/'build.json'),'objects':rows,'loop_gate':checks,
        'dispatcher':{'bytes_verified':dispatch_bytes,'forbidden':dispatch_bad,'object_sha256':sha(dispatcher)},
        'compile_isa_scope':scope,'source_hash_mismatches':mismatches,'failure_reason':failures,
        'pixel_calls':0,'candidate_library_loads':0,'performance_calls':0}
    with (HERE/'results.json').open('x',encoding='utf-8') as stream:
        json.dump(result,stream,ensure_ascii=False,indent=2)
        stream.write('\n')
    print(json.dumps({'accepted':result['accepted'],'loops':checks,'failure_reason':failures},ensure_ascii=False))
    return 0 if result['accepted'] else 1


if __name__=='__main__':
    raise SystemExit(main())
