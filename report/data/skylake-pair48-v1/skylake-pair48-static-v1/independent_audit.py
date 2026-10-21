"""79独立静态审计：解析对象字节并追踪双像素解码，不加载候选、不执行像素。"""
import ast
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BUILD = ROOT / 'artifacts/skylake-pair48-linux-build-v1'
OBJECTS = BUILD / 'CMakeFiles/jshc_skylake_pair48.dir'
MASK = 0xffff000000000000


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return Path(p).read_text(encoding='utf-8')


def args(s):
    return re.split(r',\s*(?![^()]*\))', s)


def canon(s):
    n = s.lstrip('%')
    names = dict(eax='rax', ebx='rbx', ecx='rcx', edx='rdx', esi='rsi', edi='rdi', ebp='rbp', esp='rsp')
    return names.get(n, re.sub(r'^(r\d+)d$', r'\1', n))


def gpr(s):
    return bool(re.fullmatch(r'%(?:r(?:ax|bx|cx|dx|si|di|bp|sp|[89]|1[0-5])|e(?:ax|bx|cx|dx|si|di|bp|sp)|r(?:[89]|1[0-5])d)', s))


def reg64(s):
    return bool(re.fullmatch(r'%r(?:ax|bx|cx|dx|si|di|bp|sp|[89]|1[0-5])', s))


def parse(p):
    rows = []
    section = function = None
    for line in read(p).splitlines():
        m = re.match(r'Disassembly of section (.+):', line)
        if m:
            section = m[1]
        m = re.match(r'^([0-9a-f]+) <(.+)>:$', line)
        if m:
            function = m[2]
        m = re.match(r'\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9]*)\s*(.*)$', line)
        if m:
            rows.append(dict(a=int(m[1], 16), raw=bytes.fromhex(m[2]), op=m[3], arg=m[4].split('#')[0].strip(), section=section, function=function))
    return rows


def executable_sections(p):
    data = Path(p).read_bytes()
    assert data[:6] == b'\x7fELF\x02\x01'
    start = struct.unpack_from('<Q', data, 40)[0]
    size, count, names_index = struct.unpack_from('<HHH', data, 58)
    sections = [struct.unpack_from('<IIQQQQIIQQ', data, start + i * size) for i in range(count)]
    ns = sections[names_index]
    names = data[ns[4]:ns[4] + ns[5]]
    return {names[s[0]:].split(b'\0', 1)[0].decode(): data[s[4]:s[4] + s[5]] for s in sections if s[2] & 4}


def compact(o):
    return dict(address=hex(o['a']), instruction=o['op'] + ' ' + o['arg'])


def forbidden(o, role):
    raw = o['raw']
    i = 0
    while i < len(raw) and (raw[i] in (0x66, 0x67, 0x2e, 0x36, 0x3e, 0x26, 0x64, 0x65, 0xf2, 0xf3, 0xf0) or 0x40 <= raw[i] <= 0x4f):
        i += 1
    return (role != 'dispatcher' and o['op'].startswith('call') or 'gather' in o['op'] or
            o['op'] in ('pext', 'pdep', 'mulx', 'bzhi', 'rorx', 'shlx', 'shrx', 'sarx', 'bextr', 'blsi', 'blsr', 'blsmsk') or
            o['op'] == 'andn' and not role.startswith('andn_') or
            bool(re.search(r'%(?:zmm\d+|k[0-7])\b|%[xy]mm(?:1[6-9]|2\d|3[01])\b|\{', o['arg'])) or
            i < len(raw) and raw[i] == 0x62 or role == 'dispatcher' and o['op'].startswith('v'))


def audit_region(ops, mode, width, lo, hi, expected_count, is_loop):
    body = [o for o in ops if o['section'] == '.text' and lo <= o['a'] <= hi]
    andns = [o for o in body if o['op'] == 'andn']
    assert body[0]['a'] == lo and body[-1]['a'] == hi and len(body) == expected_count
    assert len(andns) == width // 2
    masks = {canon(args(o['arg'])[1]) for o in andns}
    assert len(masks) == 1
    mask = next(iter(masks))
    defs = [o for o in ops if o['section'] == '.text' and o['a'] < lo and o['op'] == 'movabs' and args(o['arg'])[0] == '$0xffff000000000000' and canon(args(o['arg'])[-1]) == mask]
    assert defs
    definition = defs[-1]
    # 掩码定义到入口之间不能有隐含改写；向量常量和地址调整不算掩码写入。
    pre_writes = [compact(o) for o in ops if definition['a'] < o['a'] < lo and o['section'] == '.text' and args(o['arg']) and gpr(args(o['arg'])[-1]) and canon(args(o['arg'])[-1]) == mask and o['op'] not in ('cmp', 'test') and not o['op'].startswith('j')]
    source_match = re.fullmatch(r'(?:0x[0-9a-f]+)?\((%r[a-z0-9]+)\)', args(andns[0]['arg'])[0])
    assert source_match
    source = canon(source_match[1])
    state = {source: ('base', 'input', 0), 'rdi': ('base', 'id_table', 0), 'rsi': ('base', 'palette', 0), mask: ('constant', MASK)}
    loads, ids, palettes, mask_uses, mask_writes, problems = [], [], [], [], [], []
    seen_pixels = set()
    for o in body:
        p = args(o['arg'])
        old = dict(state)
        dest = canon(p[-1]) if p and gpr(p[-1]) else None
        # 任何普通GPR写入都使旧ID版本失效，避免把已复用寄存器误认为旧ID。
        writes = dest is not None and o['op'] not in ('cmp', 'test', 'push') and not o['op'].startswith('j') and not o['op'].startswith('nop')
        if writes:
            state.pop(dest, None)
            if dest == mask:
                mask_writes.append(compact(o))
        pal = re.search(r'\(%rsi,(%[a-z0-9]+),4\)', o['arg'])
        if pal:
            v = old.get(canon(pal[1]))
            group = set(range((v[1] // 12) * 12, (v[1] // 12) * 12 + 12, 3)) if v and v[0] == 'id' else set()
            ok = bool(group) and group.issubset(seen_pixels) and old.get('rsi') == ('base', 'palette', 0)
            palettes.append(dict(address=hex(o['a']), pixel_offset=v[1] if v else None, four_ids_ready=ok))
        if o['op'] == 'andn':
            m = re.fullmatch(r'(0x[0-9a-f]+)?\((%r[a-z0-9]+)\)', p[0])
            valid = bool(m) and reg64(p[1]) and reg64(p[2]) and o['raw'][0] == 0xc4 and o['raw'][2] & 0x80 and o['raw'][3] == 0xf2
            base = old.get(canon(m[2])) if m else None
            value = old.get(canon(p[1]))
            mask_uses.append(dict(address=hex(o['a']), correct=value == ('constant', MASK), operand_valid=bool(valid)))
            if not valid or base != ('base', 'input', 0):
                problems.append(dict(address=hex(o['a']), reason='输入基址或64位内存ANDN不符', base=base))
            offset = int(m[1] or '0', 16) if m else -1
            loads.append(dict(address=hex(o['a']), byte_offset=offset))
            state[dest] = ('pair48', offset)
        elif o['op'] == 'mov' and len(p) == 2 and gpr(p[0]) and dest:
            v = old.get(canon(p[0]))
            if v and v[0] == 'pair48' and not reg64(p[-1]):
                v = ('pair_low32', v[1])
            if v:
                state[dest] = v
        elif o['op'] == 'and' and p[0] == '$0xffffff' and dest:
            v = old.get(dest)
            if v and v[0] in ('pair48', 'pair_low32'):
                state[dest] = ('pixel24', v[1])
        elif o['op'] == 'shr' and p[0] == '$0x18' and dest and reg64(p[-1]):
            v = old.get(dest)
            if v and v[0] == 'pair48':
                state[dest] = ('pixel24', v[1] + 3)
        elif o['op'] == 'movzbl' and re.fullmatch(r'\(%rdi,%[a-z0-9]+,1\)', p[0]):
            index = re.fullmatch(r'\(%rdi,(%[a-z0-9]+),1\)', p[0])[1]
            v = old.get(canon(index))
            ok = v is not None and v[0] == 'pixel24' and old.get('rdi') == ('base', 'id_table', 0)
            ids.append(dict(address=hex(o['a']), pixel_offset=v[1] if v else None, correct=ok))
            if ok:
                state[dest] = ('id', v[1])
                seen_pixels.add(v[1])
        # 循环末游标加法不再参与本轮输入，但明确记录其变化，不能跨修改继续当原基址。
        elif o['op'] == 'add' and dest and p[0].startswith('$'):
            v = old.get(dest)
            if v and v[0] == 'base':
                state[dest] = (v[0], v[1], v[2] + int(p[0][1:], 0))
    frame = any(o['a'] < lo and o['section'] == '.text' and o['op'] == 'mov' and o['arg'] == '%rsp,%rbp' for o in ops)
    stack = [compact(o) for o in body if '%rsp' in o['arg'] or frame and '%rbp' in o['arg']]
    stores = [o for o in body if o['op'].startswith('vmov') and '(' in args(o['arg'])[-1]]
    last_andn = andns[-1]['a']
    dead_reuse = not is_loop and all(int(w['address'], 16) >= last_andn for w in mask_writes) and not any(o['section'] == '.text' and o['a'] > hi and o['op'] == 'andn' for o in ops)
    checks = dict(exact_instruction_count=len(body) == expected_count, input_loads=len(loads) == width // 2,
                  input_offsets=[v['byte_offset'] for v in loads] == list(range(0, width * 3, 6)),
                  exact_ids=len(ids) == width and all(v['correct'] for v in ids) and seen_pixels == set(range(0, width * 3, 3)),
                  exact_palette=len(palettes) == width and {v['pixel_offset'] for v in palettes} == set(range(0, width * 3, 3)),
                  four_id_barrier=all(v['four_ids_ready'] for v in palettes),
                  mem64_andn_and_mask=all(v['correct'] and v['operand_valid'] for v in mask_uses),
                  mask_outside=not pre_writes and (not mask_writes or dead_reuse),
                  no_stack=not stack, no_unexplained_input=not problems,
                  all_reads_before_stores=bool(stores) and max(int(v['address'], 16) for v in palettes) < stores[0]['a'] and last_andn < stores[0]['a'],
                  expected_output_stores=len(stores) == (6 if width == 64 else 3),
                  no_loop_constant_load=not any('(%rip)' in o['arg'] for o in body),
                  loop_or_straight=(body[-1]['op'] in ('jae', 'ja') and int(body[-1]['arg'].split()[0], 16) == lo) if is_loop else not any(o['op'].startswith('j') for o in body))
    return dict(mode=mode, width=width, start=hex(lo), end=hex(hi), instructions=len(body), andn_count=len(andns),
                maximum_input_bytes=max(v['byte_offset'] for v in loads) + 8, checks=checks,
                mask_initializer=compact(definition), mask_uses=mask_uses, mask_writes=mask_writes,
                dead_mask_reuse=bool(mask_writes) and dead_reuse, inputs=loads, ids=ids, palettes=palettes, stack_references=stack, problems=problems)


def main():
    assert not (HERE / 'independent-audit.json').exists()
    objects, regions = [], []
    specs = {'andn_inplace': [('inplace', 64, 0xf8, 0x7b4, 321, True), ('inplace', 32, 0x7f0, 0xb60, 170, True)],
             'andn_outplace': [('outplace', 64, 0x100, 0x7c2, 319, True), ('outplace', 32, 0x81d, 0xb81, 168, False)]}
    for role, rel in [('linear', 'channel_avx2.cpp.o'), ('andn_inplace', 'andn_inplace/channel_avx2.cpp.o'), ('andn_outplace', 'andn_outplace/channel_avx2.cpp.o'), ('dispatcher', 'channel_runtime.cpp.o')]:
        obj, asm = OBJECTS / rel, HERE / (role + '.asm.txt')
        ops, sections = parse(asm), executable_sections(obj)
        coverage = {name: set() for name in sections}
        bytes_ok = True
        for o in ops:
            bytes_ok &= sections[o['section']][o['a']:o['a'] + len(o['raw'])] == o['raw']
            coverage[o['section']].update(range(o['a'], o['a'] + len(o['raw'])))
        coverage_ok = all(coverage[k] == set(range(len(v))) for k, v in sections.items())
        bad = [compact(o) for o in ops if forbidden(o, role)]
        objects.append(dict(role=role, object_sha256=sha(obj), asm_sha256=sha(asm), parsed_instructions=len(ops), instruction_bytes_match=bytes_ok,
                            complete_executable_byte_coverage=coverage_ok, executable_sections={k: len(v) for k, v in sections.items()}, forbidden=bad))
        for spec in specs.get(role, []):
            regions.append(audit_region(ops, *spec))
    plan_path = ROOT / 'experiments/skylake-pair48-v1.json'
    plan, build = json.loads(read(plan_path)), json.loads(read(BUILD / 'build.json'))
    mismatches = [k for k, v in plan['source_sha256'].items() if sha(ROOT / k) != v]
    identity = dict(build_plan=build['plan_sha256'] == sha(plan_path), build_sources=build['source_sha256'] == plan['source_sha256'])
    commands = json.loads(read(BUILD / 'compile_commands.json'))
    flags = []
    for e in commands:
        bmi = '-mbmi' in e['command'].split()
        expected = any('/skylake-pair48-runtime/' + d + '/' in e['file'] for d in ('andn_inplace', 'andn_outplace'))
        pixels = e['file'].endswith('/channel_avx2.cpp')
        required = all(f in e['command'].split() for f in ('-mavx2', '-mtune=skylake', '-ffp-contract=off')) if pixels else True
        flags.append(dict(file=e['file'], bmi=bmi, expected_bmi=expected, correct=bmi == expected and required))
    source = ROOT / 'experiments/skylake-pair48-runtime'
    old = ROOT / 'experiments/skylake-andn-split-runtime'
    exact = dict(linear=sha(source / 'channel_avx2.cpp') == sha(old / 'channel_avx2.cpp'),
                 dispatcher=read(source / 'channel_runtime.cpp') == read(old / 'channel_runtime.cpp').replace('andn_split', 'pair48').replace('return 78;', 'return 79;'))
    for d in ('andn_inplace', 'andn_outplace'):
        new, previous = read(source / d / 'channel_avx2.cpp'), read(old / d / 'channel_avx2.cpp').replace('andn_split', 'pair48')
        def outside(s):
            start = s.rfind('//', 0, s.index('inline __attribute__((always_inline)) __m256i read_wide'))
            end = s.index('inline __attribute__((always_inline)) void output(')
            return s[:start], s[end:]
        exact[d + '_outside_read_wide'] = outside(new) == outside(previous)
    # 验证入口的可执行语法树归一身份后保持不变；文档字符串不参与功能等价判断。
    def syntax(p, normalize=False):
        text = read(p)
        if normalize:
            text = text.replace('pair48', 'andn_split').replace('79', '78')
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                node.body.pop(0)
        return ast.dump(tree, include_attributes=False)
    verifier = syntax(ROOT / 'scripts/verify_skylake_pair48_linux.py', True) == syntax(ROOT / 'scripts/verify_skylake_andn_split_linux.py')
    formal = json.loads(read(HERE / 'results-v2.json'))
    identity['formal_result'] = formal['accepted'] and formal['plan_sha256'] == sha(plan_path) and formal['build_sha256'] == sha(BUILD / 'build.json')
    passed = all(identity.values()) and not mismatches and all(exact.values()) and verifier and all(f['correct'] for f in flags) and sum(f['bmi'] for f in flags) == 2 and all(o['instruction_bytes_match'] and o['complete_executable_byte_coverage'] and not o['forbidden'] for o in objects) and len(regions) == 4 and all(all(r['checks'].values()) for r in regions)
    result = dict(purpose=__doc__, accepted=passed, script_sha256=sha(__file__), plan_sha256=sha(plan_path), build_sha256=sha(BUILD / 'build.json'),
                  first_results_sha256=sha(HERE / 'results.json'), formal_results_sha256=sha(HERE / 'results-v2.json'),
                  objects=objects, sections=regions, compile_options=flags, source_hash_mismatches=mismatches, identity_checks=identity,
                  source_exact_comparison=exact, verifier_normalized_ast_equal=verifier,
                  boundary_review='原地72/40边界及分离remaining>=72/40保持78源码；本轮最大宽读194/98B，分别小于216/120B，精确24B尾部不变。分离32入口0x809 cmp39，0x80d jbe跳过；64退出remaining<72，故32最多一次。',
                  mask_review='分离32的0xa9f最后一次消费rax中的掩码后将其覆盖为pair48；0xaae SHR解码高24位，之后无ANDN。逐条追踪每次消费前的掩码，不要求死掩码寄存器永久不变。',
                  stack_scope='四热区无rsp/真实frame引用；序言保存和分离64结束0x7c8..0x7d2的三个循环外状态恢复仍存在，不声明全函数无栈。',
                  limitations=['独立解析覆盖全部可执行对象字节及显式寄存器ISA；不模拟完整x86控制流或ABI。', '源码分派与78归一身份后相同，构造检测bmi且只有两专用TU使用-mbmi；本审计没有在无BMI机器上运行。', '静态通过不等于RGB8精度或性能达标；完整域与受控性能仍由主流程独立执行。'],
                  candidate_library_loads=0, pixel_calls=0, performance_calls=0, compiler_calls=0)
    with (HERE / 'independent-audit.json').open('x', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps(dict(accepted=passed, identity=identity, source_exact=exact, verifier=verifier, objects=objects, sections=[dict(mode=r['mode'], width=r['width'], instructions=r['instructions'], checks=r['checks']) for r in regions], sha256=sha(HERE / 'independent-audit.json')), ensure_ascii=False))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
