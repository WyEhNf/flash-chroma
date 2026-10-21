"""修订78冻结对象静态门槛；只反汇编/解析，不加载候选库或执行像素。"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
import struct
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD = ROOT/'artifacts/skylake-andn-split-linux-build-v1'
OBJECTS = BUILD/'CMakeFiles/jshc_skylake_andn_split.dir'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_new(path, value):
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')


def text_section(path):
    data = path.read_bytes()
    assert data[:6] == b'\x7fELF\x02\x01', '只接受ELF64小端对象'
    offset = struct.unpack_from('<Q', data, 40)[0]
    stride, count, names_index = struct.unpack_from('<HHH', data, 58)
    sections = [struct.unpack_from('<IIQQQQIIQQ', data, offset+i*stride) for i in range(count)]
    names = sections[names_index]
    strings = data[names[4]:names[4]+names[5]]
    for section in sections:
        name = strings[section[0]:].split(b'\0', 1)[0]
        if name == b'.text':
            return data[section[4]:section[4]+section[5]]
    raise ValueError('对象缺少.text')


def operands(text):
    return re.split(r',\s*(?![^()]*\))', text)


def read_ops(path):
    ops = []
    function = None
    for line in path.read_text(encoding='utf-8').splitlines():
        label = re.match(r'^([0-9a-f]+) <(.+)>:$', line)
        if label:
            function = label[2]
        m = re.match(r'\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9]*)\s*(.*)$', line)
        if m:
            ops.append(dict(offset=int(m[1], 16), bytes=m[2].split(), mnemonic=m[3],
                            operands=m[4].split('#')[0].strip(), function=function))
    return ops


def forbidden(op, role):
    mnemonic, args = op['mnemonic'], op['operands']
    raw = bytes.fromhex(' '.join(op['bytes']))
    pos = 0
    while pos < len(raw) and (raw[pos] in (0x66, 0x67, 0x2e, 0x36, 0x3e, 0x26, 0x64, 0x65, 0xf2, 0xf3, 0xf0) or 0x40 <= raw[pos] <= 0x4f):
        pos += 1
    return (mnemonic.startswith('call') or 'gather' in mnemonic or
            mnemonic in ('pext', 'pdep', 'mulx', 'bzhi', 'rorx', 'shlx', 'shrx', 'sarx', 'bextr', 'blsi', 'blsr', 'blsmsk') or
            role == 'linear' and mnemonic == 'andn' or
            bool(re.search(r'%(?:zmm\d+|k[0-7])\b|%[xy]mm(?:1[6-9]|2[0-9]|3[01])\b|\{', args)) or
            pos < len(raw) and raw[pos] == 0x62)


def id_barrier(body):
    # 当前两对象ID基址为rdi、palette基址为rsi；跟踪寄存器最近的ID版本。
    versions, loads, checks = {}, [], []
    for op in body:
        parts = operands(op['operands'])
        m = re.fullmatch(r'\(%rdi,%[a-z0-9]+,1\)', parts[0]) if parts else None
        if op['mnemonic'] == 'movzbl' and m:
            reg = canonical(parts[-1])
            versions[reg] = len(loads)
            loads.append(op['offset'])
        palette = re.search(r'\(%rsi,(%[a-z0-9]+),4\)', op['operands'])
        if palette:
            generation = versions.get(canonical(palette[1]))
            ready = generation is not None and len(loads) >= generation//4*4+4
            checks.append(dict(palette_offset=hex(op['offset']), id_generation=generation,
                               completed_ids=len(loads), group_ready=ready))
    return dict(id_loads=len(loads), palette_loads=len(checks),
                four_id_before_palette=bool(checks) and all(c['group_ready'] for c in checks), checks=checks)


def loops_for(ops, role):
    found = []
    for op in ops:
        if op['mnemonic'] not in ('jae', 'jbe', 'jb', 'ja', 'jne'):
            continue
        m = re.match(r'([0-9a-f]+)\b', op['operands'])
        if not m or int(m[1], 16) >= op['offset']-100:
            continue
        start = int(m[1], 16)
        body = [x for x in ops if start <= x['offset'] <= op['offset'] and x['function'] == op['function']]
        if any(x['mnemonic'].startswith('ret') for x in body):
            continue
        andn = [x for x in body if x['mnemonic'] == 'andn']
        masks = [x for x in body if x['mnemonic'] == 'and' and x['operands'].startswith('$0xffffff,')]
        width = len(masks) if role == 'linear' else len(andn)
        if width not in (32, 64):
            continue
        same_moves = [x for x in body if x['mnemonic'] == 'mov' and
                      len(operands(x['operands'])) == 2 and
                      operands(x['operands'])[0] == operands(x['operands'])[1]]
        # rbp只有在本函数建立帧指针后才按栈解释；普通基址寄存器不能误判spill。
        frame_pointer = any(x['function'] == op['function'] and x['offset'] < start and
                            x['mnemonic'] == 'mov' and x['operands'] == '%rsp,%rbp' for x in ops)
        stack = [x for x in body if '%rsp' in x['operands'] or frame_pointer and '%rbp' in x['operands']]
        mask_args = sorted({operands(x['operands'])[1] for x in andn})
        bad_andn = []
        for x in andn:
            parts = operands(x['operands'])
            raw = bytes.fromhex(' '.join(x['bytes']))
            if len(parts) != 3 or not re.fullmatch(r'(?:-?0x[0-9a-f]+)?\(%r[a-z0-9]+\)', parts[0]) or not re.fullmatch(r'%(?:e[a-z]{2}|r(?:[89]|1[0-5])d)', parts[1]) or not re.fullmatch(r'%(?:e[a-z]{2}|r(?:[89]|1[0-5])d)', parts[2]) or raw[0] != 0xc4 or raw[2] & 0x80:
                bad_andn.append(x)
        invariant_mask = []
        for reg in mask_args:
            initializers = [x for x in ops if x['function'] == op['function'] and x['offset'] < start and x['mnemonic'] == 'mov' and x['operands'] == '$0xff000000,'+reg]
            writes = [x for x in body if operands(x['operands'])[-1] == reg and x['mnemonic'] not in ('cmp', 'test')]
            invariant_mask.append(dict(register=reg, initializer=hex(initializers[-1]['offset']) if initializers else None,
                                       loop_writes=writes, pass_check=bool(initializers) and not writes))
        palette_ops = [x for x in body if '(%rsi,' in x['operands']]
        stores = [x for x in body if x['mnemonic'].startswith('vmov') and '(' in operands(x['operands'])[-1]]
        found.append(dict(mode='outplace' if '_to(' in op['function'] else 'inplace', width=width,
                          start=hex(start), end=hex(op['offset']), instructions=len(body),
                          andn_count=len(andn), input_and_count=len(masks), self_moves=len(same_moves),
                          self_move_instructions=same_moves, frame_pointer_established=frame_pointer, stack_references=stack,
                          bad_andn_operands=bad_andn, mask_invariants=invariant_mask,
                          loop_rip_constants=[x for x in body if '%rip' in x['operands']],
                          barrier=id_barrier(body),
                          all_palette_reads_before_first_store=bool(stores) and max(x['offset'] for x in palette_ops) < stores[0]['offset']))
    return found


def canonical(reg):
    aliases = dict(eax='rax', ebx='rbx', ecx='rcx', edx='rdx', esi='rsi', edi='rdi', ebp='rbp', esp='rsp')
    name = reg.removeprefix('%')
    return aliases.get(name, re.sub(r'^(r\d+)d$', r'\1', name))


def regions_for(ops, role):
    rows = loops_for(ops, role)
    for row in rows:
        row['kind'] = 'backedge_loop'
    if role == 'linear':
        return rows
    mode = 'inplace' if role == 'andn_inplace' else 'outplace'
    if any(row['width'] == 32 for row in rows):
        return rows
    # GCC可把32尾变成最多一次的直线代码；不以缺失回边省略审计。
    occupied = [(int(r['start'], 16), int(r['end'], 16)) for r in rows]
    left = [o for o in ops if o['mnemonic'] == 'andn' and not any(a <= o['offset'] <= b for a, b in occupied)]
    if len(left) != 32 or len({o['function'] for o in left}) != 1:
        return rows
    first, last = left[0]['offset'], left[-1]['offset']
    function = left[0]['function']
    stores = []
    for o in ops:
        if o['function'] != function or o['offset'] <= last:
            continue
        if o['mnemonic'].startswith(('j', 'ret')):
            break
        parts = operands(o['operands'])
        if o['mnemonic'].startswith('vmov') and len(parts) == 2 and '(' in parts[-1] and '%ymm' in parts[0]:
            stores.append(o)
            if len(stores) == 3:
                break
    if len(stores) != 3:
        return rows
    end = stores[-1]['offset']
    body = [o for o in ops if first <= o['offset'] <= end and o['function'] == function]
    # 复用相同区段检查器，仅合成识别用回边；它不会进入保存/统计的真实body。
    marker = dict(offset=end, bytes=[], mnemonic='jne', operands=f'{first:x}', function=function)
    lifted = [o for o in ops if not (o['function'] == function and o['offset'] == end)] + [marker]
    # 原末store必须计入：临时地址+1仅用于生成回边，随后剔除人工节点并恢复检查。
    marker['offset'] = end + 1
    lifted = ops + [marker]
    synthesized = [r for r in loops_for(lifted, role) if r['start'] == hex(first) and r['end'] == hex(end+1)]
    assert len(synthesized) == 1, '32直线区段不能完整解析'
    row = synthesized[0]
    row.update(kind='at_most_once_straightline', end=hex(end), instructions=len(body), mode=mode)
    guards = []
    previous = [o for o in ops if o['function'] == function and o['offset'] < first]
    for i, o in enumerate(previous[:-1]):
        nxt = previous[i+1]
        if o['mnemonic'] == 'cmp' and o['operands'].startswith('$0x27,') and nxt['mnemonic'] in ('jbe','ja'):
            guards.append(dict(compare=hex(o['offset']), instruction=o['operands'], branch=hex(nxt['offset']), target=nxt['operands']))
    row['straightline_guards'] = guards
    row['straightline_proof'] = '64退出remaining<72；32入口remaining>=40，减32后<40，所以最多一次；实际入口cmp39/条件跳转另行核对'
    row['no_internal_branches'] = not any(o['mnemonic'].startswith(('j','ret')) for o in body)
    rows.append(row)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--objdump', default=shutil.which('objdump') or 'E:/mingw64/bin/objdump.exe')
    args = parser.parse_args()
    if (HERE/'results.json').exists():
        raise ValueError('不覆盖既有静态回执')
    rows = []
    for role, relative in [('linear', 'channel_avx2.cpp.o'), ('andn_inplace', 'andn_inplace/channel_avx2.cpp.o'), ('andn_outplace', 'andn_outplace/channel_avx2.cpp.o')]:
        obj = OBJECTS/relative
        asm = HERE/(role+'.asm.txt')
        if not asm.exists():
            text = subprocess.check_output([args.objdump, '-d', '--insn-width=15', '-C', str(obj)], text=True)
            with asm.open('x', encoding='utf-8') as f:
                f.write(text)
        ops, raw_text = read_ops(asm), text_section(obj)
        bytes_ok = all(raw_text[x['offset']:x['offset']+len(x['bytes'])] == bytes.fromhex(' '.join(x['bytes'])) for x in ops)
        bad = [x for x in ops if forbidden(x, role)]
        rows.append(dict(role=role, object_path=str(obj.relative_to(ROOT)), object_sha256=sha(obj),
                         asm_sha256=sha(asm), text_sha256=hashlib.sha256(raw_text).hexdigest(),
                         disassembly_bytes_verified=bytes_ok, instructions=len(ops), forbidden=bad,
                         functions=sorted({o['function'] for o in ops}),
                         hints={h:sum(x['mnemonic'] == h for x in ops) for h in ('prefetchnta', 'prefetchw', 'prefetcht0', 'vmovntdq', 'sfence')},
                         wide_loops=regions_for(ops, role)))
    old = {(x['mode'], x['width']):x for x in rows[0]['wide_loops']}
    checks = []
    for row in [r for obj in rows[1:] for r in obj['wide_loops']]:
        reference = old[(row['mode'], row['width'])]
        check = dict(mode=row['mode'], width=row['width'], kind=row['kind'],
                     reference_instructions=reference['instructions'], candidate_instructions=row['instructions'],
                     fewer_instructions=row['instructions'] < reference['instructions'], no_stack=not row['stack_references'],
                     correct_andn=not row['bad_andn_operands'] and row['andn_count'] == row['width'],
                     no_extra_zext=row['self_moves'] == 0,
                     mask_outside=bool(row['mask_invariants']) and all(x['pass_check'] for x in row['mask_invariants']),
                     four_id=row['barrier']['four_id_before_palette'] and row['barrier']['id_loads']==row['width'] and row['barrier']['palette_loads']==row['width'],
                     all_reads_before_stores=row['all_palette_reads_before_first_store'],
                     straightline_complete=row['kind']!='at_most_once_straightline' or bool(row['straightline_guards']) and row['no_internal_branches'])
        checks.append(check)
    commands = json.loads((BUILD/'compile_commands.json').read_text(encoding='utf-8'))
    scope = []
    for entry in commands:
        expected = any('/skylake-andn-split-runtime/'+folder+'/' in entry['file'] for folder in ('andn_inplace','andn_outplace'))
        actual = bool(re.search(r'(?:^|\s)-mbmi(?:\s|$)', entry['command']))
        pixel = entry['file'].endswith('/channel_avx2.cpp')
        pixel_flags = all(re.search(r'(?:^|\s)'+re.escape(flag)+r'(?:\s|$)',entry['command']) for flag in ('-mavx2','-mtune=skylake','-ffp-contract=off')) if pixel else True
        scope.append(dict(file=entry['file'], bmi_expected=expected, bmi_present=actual,
                          pixel_flags_valid=bool(pixel_flags), pass_check=expected == actual and bool(pixel_flags)))
    plan_path = ROOT/'experiments/skylake-andn-split-v1.json'
    plan = json.loads(plan_path.read_text(encoding='utf-8'))
    mismatches = [key for key, value in plan['source_sha256'].items() if sha(ROOT/key) != value]
    failures = []
    expected_regions = {('inplace',64),('inplace',32),('outplace',64),('outplace',32)}
    if len(checks)!=4 or {(r['mode'],r['width']) for r in checks}!=expected_regions:
        failures.append('未完整识别原地/分离64/32四个实际可达宽区段')
    if len(old)!=4 or set(old)!=expected_regions:
        failures.append('原线性比较区段缺失')
    if mismatches:
        failures.append('冻结源哈希不一致：'+','.join(mismatches))
    for row in rows:
        if not row['disassembly_bytes_verified']:
            failures.append(row['role']+'反汇编字节与ELF.text不符')
        if row['forbidden']:
            failures.append(row['role']+'出现禁止调用/ISA')
        if row['role']!='linear' and len(row['functions'])!=1:
            failures.append(row['role']+'不止一个可达入口')
    if not all(x['pass_check'] for x in scope) or sum(x['bmi_present'] for x in scope)!=2:
        failures.append('BMI编译选项范围或像素AVX2/skylake选项不符')
    labels = dict(fewer_instructions='指令数未减少', no_stack='出现真实栈引用', correct_andn='ANDN内存/宽度/次数不符',
                  no_extra_zext='出现多余逐像素零扩展', mask_outside='掩码未在区段外保持不变', four_id='四ID先行未成立',
                  all_reads_before_stores='全部查表读取未先于输出', straightline_complete='32直线区段入口或完整性不符')
    for check in checks:
        for key,label in labels.items():
            if not check[key]: failures.append(f"{check['mode']}/{check['width']}：{label}")
    accepted = not failures
    result = dict(purpose=__doc__, accepted=accepted, script_sha256=sha(__file__),
                  plan_sha256=sha(plan_path), build_sha256=sha(BUILD/'build.json'),
                  objects=rows, loop_gate=checks, compile_isa_scope=scope, source_hash_mismatches=mismatches,
                  failure_reason=failures, decision='静态门槛失败，停止修订78，不执行像素、精度或性能' if not accepted else '静态通过，可由主流程安排精度验证',
                  pixel_calls=0,candidate_library_loads=0,performance_calls=0)
    save_new(HERE/'results.json',result)
    print(json.dumps(dict(accepted=accepted,loop_gate=checks,result_sha256=sha(HERE/'results.json')),ensure_ascii=False))
    return 0 if accepted else 1


if __name__ == '__main__':
    raise SystemExit(main())
