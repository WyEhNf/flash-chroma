"""唯一-j1构建新页指针核并只调用布局元数据；有限native另待复核。"""
import argparse
import ctypes as ct
import os
from pathlib import Path
import re
import shutil
import subprocess
from page_id16_native_pages_build_common import ROOT, PLAN, checked_plan, save, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    plan = checked_plan()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    records = []

    def run(command):
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True,
                                encoding='utf-8', errors='replace')
        records.append(dict(command=command, returncode=result.returncode,
                            stdout=result.stdout, stderr=result.stderr))
        save(output / 'commands.json', records)
        if result.returncode:
            raise RuntimeError('native-pages唯一构建失败STOP：' + result.stderr)
        return result.stdout

    tool = plan['toolchain']
    source = ROOT / 'experiments/page-id16-native-pages-runtime/page_native_pages.c'
    adapter = ROOT / 'experiments/page-id16-native-pages-runtime/page_native_pages_parallel.cpp'
    core = Path(plan['old_core'])
    common = ['-O3', '-Wall', '-Wextra', '-ffp-contract=off', '-fstack-usage',
              '-march=x86-64', '-mtune=generic', '-mno-avx', '-mno-avx2', '-mno-avx512f']
    run([tool['clang'], '--target=x86_64-w64-windows-gnu', '--sysroot=E:/mingw64',
         '-isystem', 'E:/mingw64/x86_64-w64-mingw32/include', '-std=c99', '-pedantic-errors',
         *common, '-c', str(source), '-o', str(output / 'page_native_pages.o')])
    assembly = run([tool['objdump'], '-d', '-Mintel', '--no-show-raw-insn',
                    '--disassemble=jshc_p4_pages_apply', str(output / 'page_native_pages.o')])
    (output / 'apply-assembly.txt').write_text(assembly, encoding='utf-8')
    full_assembly = run([tool['objdump'], '-d', '-Mintel', '--no-show-raw-insn',
                         str(output / 'page_native_pages.o')])
    (output / 'all-assembly.txt').write_text(full_assembly, encoding='utf-8')
    pointer_reads = re.findall(r'^\s*([0-9a-f]+):\s+mov\s+([a-z0-9]+),QWORD PTR (\[[^\]\r\n]*\*8[^\]\r\n]*\])\s*$', assembly, re.M)
    old_shift12 = re.findall(r'^\s*[0-9a-f]+:\s+shl\s+[^,\r\n]+,0xc\s*$', assembly, re.M)
    mnemonics = re.findall(r'^\s*[0-9a-f]+:\s+([a-z0-9]+)', assembly, re.M)
    forbidden = [name for name in mnemonics if name.startswith('v') or name in
                 ('pdep', 'pext', 'shlx', 'shrx', 'sarx', 'andn', 'mulx', 'bzhi',
                  'bextr', 'blsi', 'blsr', 'blsmsk', 'tzcnt', 'lzcnt', 'popcnt', 'crc32')]
    gate = dict(passed=bool(pointer_reads) and not old_shift12 and not forbidden and bool(mnemonics),
                native_pointer_reads=[dict(offset=address, destination=register, operand=operand)
                                      for address, register, operand in pointer_reads],
                old_hot_shift12=old_shift12, forbidden_mnemonics=forbidden,
                scope='只查新apply符号：至少一个真实scale8 QWORD页指针读且旧每像素pageID shl12消失；prepare仍需离线shift12，不检查整个对象禁它。仍有页指针→pool byte→palette DWORD三级依赖，不是速度证据。')
    save(output / 'machine-code-gate.json', gate)
    if not gate['passed']:
        raise AssertionError('唯一页指针机制未落入预定机器码，保留原件STOP')
    run([tool['gpp'], '-std=c++17', *common, '-fopenmp', '-c', str(adapter),
         '-o', str(output / 'page_native_pages_parallel.o')])
    run([tool['gpp'], '-shared', '-O3', '-fopenmp', str(core),
         str(output / 'page_native_pages.o'), str(output / 'page_native_pages_parallel.o'),
         '-o', str(output / 'jshc_page_native_pages.dll')])
    run([tool['gcc'], '-shared', str(core), str(output / 'page_native_pages.o'),
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
        raise AssertionError('实际ABI不等于冻结flat x64布局，保留STOP')
    metadata['rom_bytes'] = Path(plan['page_rom']).stat().st_size
    metadata['actual_capacity'] = metadata['rom_bytes'] + metadata['slots_bytes'] + metadata['view_bytes']
    metadata['increase_over_original_p4'] = metadata['slots_bytes'] + metadata['view_bytes'] - 40
    metadata['saving_vs_linear_capacity'] = 16779328 - metadata['actual_capacity']
    files = {path.name: dict(bytes=path.stat().st_size, sha256=sha(path))
             for path in output.iterdir() if path.suffix in ('.dll', '.o', '.su')}
    versions = {name: run([tool[name], '--version']) for name in ('clang', 'gcc', 'gpp')}
    checked_plan()
    save(output / 'build.json', dict(
        purpose=__doc__, plan_sha256=sha(PLAN), machine_code_gate=gate,
        actual_layout=metadata, reused_core=dict(path=str(core), sha256=sha(core)),
        outputs=files, versions=versions, metadata_native_calls=4, model_native_calls=0,
        scope='实际sizeof/offsetof与表跨度；容量不含代码/宿主/OS或进程峰。只调用4个layout元数据；prepare/apply/clear/validate与有限/full/photos/性能/WASM均未执行。'))
    print(dict(built=True, plan_sha256=sha(PLAN), actual_layout=metadata,
               pointer_reads=len(pointer_reads), main_sha256=sha(output / 'jshc_page_native_pages.dll'),
               standalone_sha256=sha(output / 'jshc_page_native_pages_c99.dll')), flush=True)


if __name__ == '__main__':
    main()
