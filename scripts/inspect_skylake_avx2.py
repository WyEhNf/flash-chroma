"""只用标准库检查AVX2对象的热循环及可选MCA模型；不加载候选或运行像素/性能。"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def functions(assembly):
    result = []; current = None
    for line in assembly.splitlines():
        match = re.match(r'^([0-9a-f]+) <(.+)>:$', line)
        if match:
            current = {'function': match[2], 'instructions': []}; result.append(current)
            continue
        parts = line.strip().split('\t')
        if current is None or len(parts) < 3 or not parts[0].endswith(':'):
            continue
        try:
            address = int(parts[0][:-1], 16)
        except ValueError:
            continue
        text = parts[2].strip()
        if text:
            op = text.split()[0]; current['instructions'].append((address, op, text[len(op):].strip()))
    return result


def loops(function):
    result = []
    for end, op, operands in function['instructions']:
        match = re.match(r'([0-9a-f]+)\s+<', operands)
        if not op.startswith('j') or op == 'jmp' or not match or int(match[1], 16) >= end:
            continue
        start = int(match[1], 16)
        seq = [x for x in function['instructions'] if start <= x[0] <= end]
        histogram = collections.Counter(x[1] for x in seq)
        result.append({'function': function['function'], 'start': hex(start), 'end': hex(end), 'span_bytes': end-start,
            'instructions': len(seq), 'gathers': sum(v for k, v in histogram.items() if k.startswith('vpgather')),
            'vpmulld': histogram['vpmulld'], 'rsp_operands': sum('%rsp' in x[2] for x in seq),
            'calls': sum(x[1].startswith('call') for x in seq),
            'branches': sum(x[1].startswith('j') for x in seq),
            'gpr_memory_loads': sum(x[1].startswith('mov') and '(' in x[2].split(',')[0]
                and '%xmm' not in x[2] and '%ymm' not in x[2] for x in seq),
            'mnemonics': dict(histogram), 'seq': seq})
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('plan', 'build', 'output'):
        p.add_argument('--'+name, type=Path, required=True)
    p.add_argument('--objdump', default='objdump')
    p.add_argument('--mca')
    p.add_argument('--reference-gathers', type=int, required=True)
    p.add_argument('--candidate-gathers', type=int, required=True)
    args = p.parse_args(); plan = read(args.plan); build = read(args.build/'build.json')
    if build['plan_sha256'] != digest(args.plan) or build['source_sha256'] != plan['source_sha256']:
        raise ValueError('构建与冻结计划不同')
    for name, sha in plan['source_sha256'].items():
        if digest(ROOT/name) != sha:
            raise ValueError('静态检查前源码变化：'+name)
    out = args.output.resolve()
    if out.exists():
        raise ValueError('静态输出必须是新目录')
    out.mkdir(parents=True); variants = {}; commands = []
    targets = dict(zip(('reference', 'candidate'), plan['cmake_targets']))
    for role, target in targets.items():
        candidates = [path for path in args.build.rglob('channel_avx2.cpp.*')
                      if path.suffix in ('.obj', '.o') and target+'.dir' in path.parts]
        if len(candidates) != 1:
            raise ValueError('不能唯一选择AVX2对象：'+role)
        obj = candidates[0]; command = [args.objdump, '-d', '-C', str(obj)]
        proc = subprocess.run(command, capture_output=True, check=True); commands.append(command)
        (out/f'{role}.asm').write_bytes(proc.stdout)
        all_loops = [loop for function in functions(proc.stdout.decode('utf-8', errors='replace')) for loop in loops(function)]
        count = args.reference_gathers if role == 'reference' else args.candidate_gathers
        eligible = [loop for loop in all_loops if loop['gathers'] == count and loop['calls'] == 0 and loop['branches'] == 1]
        record = {'object': str(obj.resolve()), 'object_sha256': digest(obj),
            'all_loops': [{k: v for k, v in loop.items() if k != 'seq'} for loop in all_loops]}
        if eligible:
            selected = max(eligible, key=lambda x: x['span_bytes'])
            record['selected'] = {k: v for k, v in selected.items() if k != 'seq'}
            text = ['.text', '.Lloop:']
            for address, op, operands in selected['seq']:
                text.append(op+' .Lloop' if op.startswith('j') else op+' '+operands.split('#')[0].strip())
            source = out/f'{role}-hot.s'; source.write_text('\n'.join(text)+'\n', encoding='ascii')
            if args.mca:
                command = [args.mca, '-mcpu=skylake', '-iterations=100', '-resource-pressure', str(source)]
                proc = subprocess.run(command, capture_output=True); commands.append(command)
                (out/f'{role}-mca.stdout.log').write_bytes(proc.stdout)
                (out/f'{role}-mca.stderr.log').write_bytes(proc.stderr)
                if proc.returncode:
                    raise RuntimeError('MCA解析失败，原始stderr已保留')
                text = proc.stdout.decode('utf-8', errors='replace')
                record['mca'] = {key: float(re.search(r'^'+re.escape(key)+r':\s*([0-9.]+)', text, re.M)[1])
                                for key in ('Total Cycles', 'Total uOps', 'Block RThroughput')}
        else:
            record['selection_failure'] = '没有满足预指定gather数、零循环内调用、单后向分支的平坦循环'
        variants[role] = record
        print(role, {k: v for k, v in record.get('selected', {}).items() if k != 'mnemonics'}, record.get('mca'), flush=True)
    for name, sha in plan['source_sha256'].items():
        if digest(ROOT/name) != sha:
            raise ValueError('静态分析期间源码变化：'+name)
    save(out/'results.json', {'purpose': __doc__, 'source_sha256': plan['source_sha256'],
        'analysis_script_sha256': digest(__file__), 'plan_sha256': digest(args.plan),
        'build_sha256': digest(args.build/'build.json'), 'variants': variants, 'commands': commands,
        'tools': {str(path): {'sha256': digest(path), 'version': subprocess.check_output([str(path), '--version'], text=True).splitlines()[:4]}
                  for path in (args.objdump, args.mca) if path and Path(path).is_file()},
        'environment': {'platform': platform.platform(), 'processor': platform.processor(), 'python': sys.version},
        'native_calls': 0, 'performance_calls': 0, 'scope': '静态计数与模型预测，不是Skylake实测或整数正确性验收。'})
    (out/'analysis-script.py').write_bytes(Path(__file__).read_bytes())


if __name__ == '__main__':
    main()
