"""修订75冻结对象静态门槛；只反汇编/解析，不加载候选库或执行像素。"""
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
BUILD = ROOT/'artifacts/skylake-andn-load-linux-build-v1'
OBJECTS = BUILD/'CMakeFiles/jshc_skylake_andn_load.dir'


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
            reg = parts[-1].removesuffix('d')
            versions[reg] = len(loads)
            loads.append(op['offset'])
        palette = re.search(r'\(%rsi,(%[a-z0-9]+),4\)', op['operands'])
        if palette:
            generation = versions.get(palette[1])
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
        width = len(andn) if role == 'andn' else len(masks)
        if width not in (32, 64):
            continue
        same_moves = [x for x in body if x['mnemonic'] == 'mov' and
                      len(operands(x['operands'])) == 2 and
                      operands(x['operands'])[0] == operands(x['operands'])[1]]
        stack = [x for x in body if re.search(r'%(?:rsp|rbp)\b', x['operands'])]
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
                          self_move_instructions=same_moves, stack_references=stack,
                          bad_andn_operands=bad_andn, mask_invariants=invariant_mask,
                          loop_rip_constants=[x for x in body if '%rip' in x['operands']],
                          barrier=id_barrier(body),
                          all_palette_reads_before_first_store=bool(stores) and max(x['offset'] for x in palette_ops) < stores[0]['offset']))
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--objdump', default=shutil.which('objdump') or 'E:/mingw64/bin/objdump.exe')
    args = parser.parse_args()
    if (HERE/'results.json').exists():
        raise ValueError('不覆盖既有静态回执')
    rows = []
    for role, relative in [('linear', 'channel_avx2.cpp.o'), ('andn', 'andn/channel_avx2.cpp.o')]:
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
                         hints={h:sum(x['mnemonic'] == h for x in ops) for h in ('prefetchnta', 'prefetchw', 'prefetcht0', 'vmovntdq', 'sfence')},
                         wide_loops=loops_for(ops, role)))
    old = {(x['mode'], x['width']):x for x in rows[0]['wide_loops']}
    checks = []
    for row in rows[1]['wide_loops']:
        reference = old[(row['mode'], row['width'])]
        check = dict(mode=row['mode'], width=row['width'], reference_instructions=reference['instructions'],
                     candidate_instructions=row['instructions'], fewer_instructions=row['instructions'] < reference['instructions'],
                     no_stack=not row['stack_references'], correct_andn=len(row['bad_andn_operands']) == 0 and row['andn_count'] == row['width'],
                     mask_outside=all(x['pass_check'] for x in row['mask_invariants']),
                     four_id=row['barrier']['four_id_before_palette'],
                     all_reads_before_stores=row['all_palette_reads_before_first_store'])
        checks.append(check)
    commands = json.loads((BUILD/'compile_commands.json').read_text())
    scope = []
    for entry in commands:
        expected = '/skylake-andn-load-runtime/andn/' in entry['file']
        actual = bool(re.search(r'(?:^|\s)-mbmi(?:\s|$)', entry['command']))
        scope.append(dict(file=entry['file'], bmi_expected=expected, bmi_present=actual, pass_check=expected == actual))
    plan_path = ROOT/'experiments/skylake-andn-load-v1.json'
    plan = json.loads(plan_path.read_text())
    mismatches = [key for key, value in plan['source_sha256'].items() if sha(ROOT/key) != value]
    accepted = (len(checks) == 4 and not mismatches and all(row['disassembly_bytes_verified'] and not row['forbidden'] for row in rows) and
                all(x['pass_check'] for x in scope) and all(all(c[k] for k in ('fewer_instructions', 'no_stack', 'correct_andn', 'mask_outside', 'four_id', 'all_reads_before_stores')) for c in checks))
    result = dict(purpose=__doc__, accepted=accepted, script_sha256=sha(__file__),
                  plan_sha256=sha(plan_path), build_sha256=sha(BUILD/'build.json'),
                  objects=rows, loop_gate=checks, compile_isa_scope=scope, source_hash_mismatches=mismatches,
                  failure_reason='uint32_t不透明asm输出后出现逐像素自MOV零扩展，输入指令数未减少；分离输出宽循环访问栈上循环上界，违反预先冻结的无spill门槛' if not accepted else None,
                  decision='静态门槛失败，停止修订75，不执行像素、精度或性能' if not accepted else '静态通过，可由主流程安排精度验证',
                  pixel_calls=0, candidate_library_loads=0, performance_calls=0)
    save_new(HERE/'results.json', result)
    print(json.dumps(dict(accepted=accepted, loop_gate=checks, result_sha256=sha(HERE/'results.json')), ensure_ascii=False))
    return 0 if accepted else 1


if __name__ == '__main__':
    raise SystemExit(main())
