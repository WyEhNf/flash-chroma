"""复用唯一已编译核心；独立观察等价scale1地址，不改v1失败或重编核心。"""
import argparse
import ctypes as ct
import os
from pathlib import Path
import re
import shutil
import subprocess
from page_id16_native_pages_build_common import ROOT, PLAN, checked_plan, read, save, sha

OBSERVER_PLAN = ROOT / 'experiments/page-id16-native-pages-observer-v2.json'
ORIGINAL = ROOT / 'artifacts/p16-page-native-pages-v1/build'
OBJECT_SHA = 'ac60efa6170af82cf9d285697f3b2a82123a32a908be8e29a4e680d0aedbb6bd'
ASSEMBLY_SHA = '4a780e1cfa496b69555e432b28f776c4cab3cbdea548eb149df49e144475d99d'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    observer = read(OBSERVER_PLAN)
    if any(sha(ROOT / name) != expected for name, expected in observer['source_sha256'].items()):
        raise AssertionError('观察器执行源改变')
    if any(sha(name) != expected for name, expected in observer['input_sha256'].items()):
        raise AssertionError('观察器冻结输入改变')
    plan = checked_plan()
    if sha(PLAN) != '65838f3968302872b8fbd7dfb734cb3d8ca7a1cd2410f02c9885a8e5bb41a997':
        raise AssertionError('不是原唯一构建计划')
    core = ORIGINAL / 'page_native_pages.o'
    assembly_path = ORIGINAL / 'apply-assembly.txt'
    if sha(core) != OBJECT_SHA or sha(assembly_path) != ASSEMBLY_SHA:
        raise AssertionError('唯一核心对象或原实码不同')
    if read(ORIGINAL / 'machine-code-gate.json')['passed']:
        raise AssertionError('原v1 STOP事实被改变')
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    assembly = assembly_path.read_text(encoding='utf-8')
    lines = {address: re.sub(r'\s+', ' ', instruction).strip()
             for address, instruction in re.findall(r'^\s*([0-9a-f]+):\s+([^\r\n]+)', assembly, re.M)}
    # 只核固定原实码数据流，不把任意QWORD读误认页指针。
    evidence = {
        '3a3': 'mov r8,QWORD PTR [rcx+0x28]',
        '3a7': 'shr esi,0x9', '3aa': 'and esi,0x7ff8',
        '3b0': 'mov rcx,QWORD PTR [r8+rsi*1]',
        '3bb': 'movzx r9d,BYTE PTR [rcx+r9*1]',
        '3d6': 'mov rsi,QWORD PTR [r8+r14*1]',
        '3f4': 'mov r14,QWORD PTR [r8+rbp*1]',
        '419': 'mov r12,QWORD PTR [r8+r13*1]',
        '438': 'mov rcx,QWORD PTR [r8+rcx*1]',
        '45e': 'mov r10,QWORD PTR [r8+rbp*1]',
        '47c': 'mov r13,QWORD PTR [r8+r13*1]',
        '4a5': 'mov r8,QWORD PTR [r8+r13*1]',
        '4bd': 'mov r9d,DWORD PTR [rsi+r9*4]',
        '56f': 'mov r10,QWORD PTR [r14+0x28]',
        '573': 'shr r8d,0x9', '577': 'and r8d,0x7ff8',
        '57e': 'mov r8,QWORD PTR [r10+r8*1]',
        '58b': 'movzx ecx,BYTE PTR [r8+rdx*1]',
    }
    old_shift = re.findall(r'^\s*[0-9a-f]+:\s+shl\s+[^,\r\n]+,0xc\s*$', assembly, re.M)
    mismatched = {address: dict(expected=text, actual=lines.get(address))
                  for address, text in evidence.items() if lines.get(address) != text}
    gate = dict(passed=not mismatched and not old_shift, evidence=evidence,
                mismatched=mismatched, old_hot_shift12=old_shift,
                original_object_sha256=sha(core), original_assembly_sha256=sha(assembly_path),
                original_gate_passed=False,
                explanation='原scale8字面规则机械误拒绝；Clang把8*(code>>12)折成(code>>9)&0x7ff8并以scale1读QWORD。固定8主lane及1尾部lane均从view+40页表读pointer，之后仍pool byte和palette；不改核心/优化/结果。')
    save(output / 'observer-machine-code-gate.json', gate)
    if not gate['passed']:
        raise AssertionError('独立固定实码观察失败，STOP')
    records = []

    def run(command):
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True,
                                encoding='utf-8', errors='replace')
        records.append(dict(command=command, returncode=result.returncode,
                            stdout=result.stdout, stderr=result.stderr))
        save(output / 'commands.json', records)
        if result.returncode:
            raise RuntimeError('观察器后续胶水或链接首次失败STOP：' + result.stderr)
        return result.stdout

    tool = plan['toolchain']
    adapter = ROOT / 'experiments/page-id16-native-pages-runtime/page_native_pages_parallel.cpp'
    common = ['-O3', '-Wall', '-Wextra', '-ffp-contract=off', '-fstack-usage',
              '-march=x86-64', '-mtune=generic', '-mno-avx', '-mno-avx2', '-mno-avx512f']
    run([tool['gpp'], '-std=c++17', *common, '-fopenmp', '-c', str(adapter),
         '-o', str(output / 'page_native_pages_parallel.o')])
    run([tool['gpp'], '-shared', '-O3', '-fopenmp', plan['old_core'], str(core),
         str(output / 'page_native_pages_parallel.o'), '-o', str(output / 'jshc_page_native_pages.dll')])
    run([tool['gcc'], '-shared', plan['old_core'], str(core),
         '-o', str(output / 'jshc_page_native_pages_c99.dll')])
    for name, path in plan['dependencies'].items():
        shutil.copyfile(path, output / name)
    metadata = {}
    with os.add_dll_directory(str(output)):
        library = ct.CDLL(str(output / 'jshc_page_native_pages_c99.dll'))
        for key, symbol in [('view_bytes', 'jshc_p4_pages_view_size'),
                            ('pointer_alignment', 'jshc_p4_pages_pointer_alignment'),
                            ('view_alignment', 'jshc_p4_pages_view_alignment'),
                            ('slots_bytes', 'jshc_p4_pages_slots_bytes')]:
            function = getattr(library, symbol)
            function.argtypes = []
            function.restype = ct.c_size_t
            metadata[key] = int(function())
    if metadata != dict(view_bytes=48, pointer_alignment=8, view_alignment=8, slots_bytes=32768):
        save(output / 'unexpected-layout.json', metadata)
        raise AssertionError('独立观察器实际布局不匹配，STOP')
    metadata['rom_bytes'] = Path(plan['page_rom']).stat().st_size
    metadata['actual_capacity'] = metadata['rom_bytes'] + metadata['slots_bytes'] + metadata['view_bytes']
    metadata['increase_over_original_p4'] = metadata['slots_bytes'] + metadata['view_bytes'] - 40
    metadata['saving_vs_linear_capacity'] = 16779328 - metadata['actual_capacity']
    checked_plan()
    save(output / 'build.json', dict(
        purpose=__doc__, original_plan_sha256=sha(PLAN), observer_plan_sha256=sha(OBSERVER_PLAN),
        machine_code_gate=gate, actual_layout=metadata,
        reused_new_core=dict(path=str(core), sha256=sha(core)),
        reused_old_core=dict(path=plan['old_core'], sha256=sha(plan['old_core'])),
        outputs={path.name: dict(bytes=path.stat().st_size, sha256=sha(path))
                 for path in output.iterdir() if path.suffix in ('.dll', '.o', '.su')},
        metadata_native_calls=4, model_native_calls=0,
        scope='原v1机械误拒绝永久保留；只复用唯一Clang对象，首次编OMP胶水并链接新DLL，只4个布局元数据；没有prepare/apply/有限/full/photos/性能/WASM。容量不含代码/宿主/OS，未测RSS。'))
    print(dict(built=True, observer_plan_sha256=sha(OBSERVER_PLAN), actual_layout=metadata,
               main_sha256=sha(output / 'jshc_page_native_pages.dll'),
               standalone_sha256=sha(output / 'jshc_page_native_pages_c99.dll')), flush=True)


if __name__ == '__main__':
    main()
