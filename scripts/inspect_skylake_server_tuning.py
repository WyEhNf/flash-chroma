"""冻结同一AVX2翻译单元，仅比较Skylake客户端/服务器调度；不加载对象或执行像素。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

from inspect_skylake_avx2 import functions
from inspect_skylake_preweight import linear_loops

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    plan = read(args.plan); out = args.output.resolve()
    if out.exists():
        raise ValueError('不覆盖既有调度研究')
    for name, expected in plan['source_sha256'].items():
        if digest(ROOT/name) != expected:
            raise ValueError('冻结源不同：'+name)
    compiler = plan['compiler']; objdump = plan['objdump']
    for tool in (compiler, objdump):
        if digest(tool['path']) != tool['sha256']:
            raise ValueError('工具不同')
    old = ROOT/plan['reference_build']
    response = old/plan['include_response']
    if digest(response) != plan['include_response_sha256']:
        raise ValueError('冻结包含路径不同')
    out.mkdir(parents=True); records = {}; commands = []
    for role, tune in (('reference', 'skylake'), ('candidate', 'skylake-avx512')):
        obj = out/(role+'.obj')
        command = [compiler['path'], *plan['common_flags'], '@'+str(response),
                   '-mavx2', '-mtune='+tune, '-ffp-contract=off', '-o', str(obj),
                   '-c', str(ROOT/plan['translation_unit'])]
        proc = subprocess.run(command, cwd=old, capture_output=True)
        (out/(role+'-compile.stdout.log')).write_bytes(proc.stdout)
        (out/(role+'-compile.stderr.log')).write_bytes(proc.stderr)
        commands.append({'argv': command, 'cwd': str(old), 'returncode': proc.returncode})
        save(out/'commands.json', commands)
        if proc.returncode:
            raise RuntimeError('编译失败，保留日志，不重试')
        command = [objdump['path'], '-d', '-C', str(obj)]
        raw = subprocess.check_output(command); (out/(role+'.asm')).write_bytes(raw)
        commands.append({'argv': command, 'returncode': 0})
        parsed = functions(raw.decode('utf-8'))
        inventory = [{k:v for k,v in loop.items() if k != 'seq'}
                     for fn in parsed for loop in linear_loops(fn)]
        # 保留每个函数的完整字节反汇编及解析指令，不只比较热循环或指令数量。
        save(out/(role+'-functions.json'), parsed)
        records[role] = {'tune': tune, 'object_sha256': digest(obj),
                         'parsed_functions_sha256': digest(out/(role+'-functions.json')),
                         'function_count': len(parsed), 'loops': inventory}
        print(role, records[role]['object_sha256'], flush=True)
    same_object = records['reference']['object_sha256'] == records['candidate']['object_sha256']
    same_instructions = read(out/'reference-functions.json') == read(out/'candidate-functions.json')
    reference_matches = records['reference']['object_sha256'] == plan['reference_object_sha256']
    if not reference_matches:
        raise ValueError('参考对象未复现，不能沿用旧执行身份')
    for name, expected in plan['source_sha256'].items():
        if digest(ROOT/name) != expected:
            raise ValueError('编译期间源改变')
    save(out/'commands.json', commands)
    value = {'purpose': __doc__, 'plan_sha256': digest(args.plan),
             'environment': {'platform': platform.platform(), 'python': sys.version,
                             'compiler': subprocess.check_output([compiler['path'], '--version'], text=True)},
             'variants': records, 'reference_matches_prior_object': reference_matches,
             'objects_byte_identical': same_object, 'parsed_instructions_identical': same_instructions,
             'decision': '对象逐字节相同，无新内核可测速，停止此调度配置' if same_object else
                         '对象存在变化；尚未证明完整路径成本收益，禁止直接测速',
             'project_native_calls': 0, 'performance_calls': 0,
             'scope': '仅本机MinGW GCC15.2目标代码比较；-mtune不启用AVX512，未链接/加载候选；不代表Linux GCC或Skylake实测。'}
    save(out/'results.json', value)
    print(json.dumps({k:value[k] for k in ('reference_matches_prior_object', 'objects_byte_identical',
                                         'parsed_instructions_identical', 'decision')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
