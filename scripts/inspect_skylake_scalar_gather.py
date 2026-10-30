"""静态检查完整软件gather、全部四级调用及固定坐标排序；不加载库或运行像素/MCA/性能。"""
from __future__ import annotations
import argparse
import re
import struct
import subprocess
from pathlib import Path
from inspect_skylake_avx2 import ROOT, read, save, digest, functions, loops


def object_file(folder, target, name):
    found = [p for p in folder.rglob(name) if target+'.dir' in p.parts]
    if len(found) != 1:
        raise ValueError('对象不唯一：'+target+'/'+name)
    return found[0]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('plan', 'build', 'prior-build', 'output'):
        p.add_argument('--'+name, type=Path, required=True)
    p.add_argument('--objdump', required=True); args = p.parse_args()
    plan = read(args.plan); build = read(args.build/'build.json'); out = args.output.resolve()
    if out.exists() or build['plan_sha256'] != digest(args.plan) or build['source_sha256'] != plan['source_sha256']:
        raise ValueError('输出必须新建，构建须匹配冻结计划')
    for name, sha in plan['source_sha256'].items():
        if digest(ROOT/name) != sha:
            raise ValueError('冻结源字节不同：'+name)
    out.mkdir(); variants = {}; parsed = {}; commands = []
    for role, target in zip(('reference', 'candidate'), plan['cmake_targets']):
        obj = object_file(args.build, target, 'channel_avx2.cpp.obj')
        command = [args.objdump, '-d', '-C', str(obj)]; commands.append(command)
        asm = subprocess.check_output(command); (out/(role+'.asm')).write_bytes(asm)
        fs = functions(asm.decode('utf-8')); parsed[role] = fs
        variants[role] = {'object_sha256': digest(obj),
            'whole_simd_tu_gathers': sum(op.startswith('vpgather') for f in fs for _, op, _ in f['instructions']),
            'functions': {f['function']: len(f['instructions']) for f in fs},
            'all_loops': [{k: v for k, v in l.items() if k != 'seq'} for f in fs for l in loops(f)]}
    if variants['candidate']['whole_simd_tu_gathers'] != 0:
        raise ValueError('软件读取对象仍有硬件gather')
    reference = [l for l in variants['reference']['all_loops'] if l['branches'] == 1 and l['calls'] == 0 and l['gathers'] in (35, 38)]
    if len(reference) != 2 or {l['gathers'] for l in reference} != {35, 38}:
        raise ValueError('参考两个固定循环不符')
    by_address = {f['instructions'][0][0]: f for f in parsed['candidate'] if f['instructions']}
    expanded = []
    for f in parsed['candidate']:
        for l in loops(f):
            if l['branches'] != 1 or l['calls'] != 4:
                continue
            callees = []
            for address, op, operands in l['seq']:
                if not op.startswith('call'):
                    continue
                match = re.match(r'([0-9a-f]+)', operands)
                callee = by_address.get(int(match[1], 16)) if match else None
                if not callee or any(op.startswith('call') for _, op, _ in callee['instructions']):
                    raise ValueError('调用目标未知或出现未处理的嵌套调用')
                callees.append({'address': hex(address), 'function': callee['function'], 'instructions': len(callee['instructions']),
                                'rsp_operands': sum('%rsp' in operands for _, _, operands in callee['instructions'])})
            expanded.append({'start': l['start'], 'loop_instructions': l['instructions'], 'callees': callees,
                'static_instruction_budget': l['instructions']+sum(c['instructions'] for c in callees),
                'static_rsp_operand_budget': l['rsp_operands']+sum(c['rsp_operands'] for c in callees),
                'scope': '按每函数完整反汇编和调用次数求和，含序言/尾声/填充；不是动态指令或周期'})
    if len(expanded) != 2:
        raise ValueError('应有且只有两个四调用固定循环')
    proof = {}
    for name in ('channel_avx2.cpp.obj', 'channel_runtime.cpp.obj'):
        old = object_file(args.prior_build, 'jshc_skylake_delta16', name)
        new = object_file(args.build, plan['cmake_targets'][0], name)
        proof[name] = {'prior_sha256': digest(old), 'reference_sha256': digest(new), 'byte_equal': old.read_bytes() == new.read_bytes()}
        if not proof[name]['byte_equal']:
            raise ValueError('参考对象不等于已验坐标差对象')
    side = ROOT/plan['fixed_inputs']['sidecar']['path']
    if digest(side) != plan['fixed_inputs']['sidecar']['sha256']:
        raise ValueError('固定侧表不同')
    words = struct.unpack('<2304I', side.read_bytes())
    frac = [[words[(c*3+a)*256:(c*3+a+1)*256] for a in range(3)] for c in range(3)]; geometry = []
    for c, d in ((0, 1), (0, 2), (1, 2)):
        pairs = []
        for a, b in ((0, 1), (0, 2), (1, 2)):
            reverse = ties = 0; example = None
            for i in range(256):
                for j in range(256):
                    u = frac[c][a][i]-frac[c][b][j]; v = frac[d][a][i]-frac[d][b][j]
                    reverse += u*v < 0; ties += (u == 0) != (v == 0)
                    if u*v < 0 and example is None:
                        example = {'codes': [i, j], 'fractions': [[frac[c][a][i], frac[c][b][j]], [frac[d][a][i], frac[d][b][j]]]}
            pairs.append({'axes': [a, b], 'strict_reversals': reverse, 'tie_mismatches': ties, 'first_reversal': example})
        geometry.append({'channels': [c, d], 'identical_axes': [frac[c][a] == frac[d][a] for a in range(3)], 'axis_pairs': pairs})
    rgb = (1, 210, 0); probe = [[frac[c][a][rgb[a]] for a in range(3)] for c in range(3)]
    save(out/'results.json', {'purpose': __doc__, 'static_check_pass': True, 'plan_sha256': digest(args.plan),
        'build_sha256': digest(args.build/'build.json'), 'analysis_sources': {n: digest(ROOT/n) for n in
            ('scripts/inspect_skylake_scalar_gather.py', 'scripts/inspect_skylake_avx2.py')},
        'commands': commands, 'variants': variants, 'reference_fixed_loops': reference, 'candidate_fixed_loops': expanded,
        'reference_object_proof': proof, 'coordinate_sidecar_sha256': digest(side), 'geometry_axis_code_pair_comparisons': 589824,
        'geometry_channel_pairs': geometry, 'ordering_probe': {'rgb': rgb, 'fractions': probe,
            'maximum_axes': [max(range(3), key=lambda a: f[a]) for f in probe]},
        'decision': '静态停止；消除gather却打破融合且增加静态预算。目标GDS未确定，不在AMD追加运行验收，也不证明Skylake更慢。',
        'scope': 'SIMD对象零gather不表示整个库；无侧表仍委托既有core。排序反例只否定无条件共用前提，未测共享错误输出。',
        'native_calls': 0, 'performance_calls': 0, 'mca_calls': 0})
    print('静态检查完成；两个固定循环预算：', [r['static_instruction_budget'] for r in expanded], '；未运行像素或性能。')


if __name__ == '__main__':
    main()
