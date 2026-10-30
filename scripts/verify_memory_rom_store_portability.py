"""独立验证新C99组内存储核的wasm32执行与三个目标对象。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import platform
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--roms', type=Path, required=True)
    parser.add_argument('--cube', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--clang', default='C:/Program Files/LLVM/bin/clang.exe')
    parser.add_argument('--node', default='C:/Program Files/nodejs/node.exe')
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    core = ROOT / 'experiments/memory-rom'
    common = ROOT / 'experiments/memory-rom-wasm'
    support = ROOT / 'experiments/memory-rom-store-portability'
    wrapper = support / 'harness.c'
    sources = [core / 'memory_rom.c', core / 'memory_rom.h', core / 'memory_rom_store.c',
               core / 'memory_rom_store.h', common / 'harness.c', common / 'minilib.c',
               common / 'include/string.h', common / 'verify.cjs', wrapper, support / 'minilib.c',
               support / 'include/string.h', Path(__file__)]
    metadata = dict(purpose=__doc__, platform=platform.platform(), python=sys.version,
                    source_sha256={str(path.relative_to(ROOT)): sha(path) for path in sources},
                    commands=[], cross_objects=[])

    def save():
        (out / 'run.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    def run(command, label):
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace')
        (out / (label + '.log')).write_text(result.stdout + result.stderr, encoding='utf-8')
        metadata['commands'].append(dict(label=label, command=command, returncode=result.returncode))
        save()
        result.check_returncode()

    metadata['compiler'] = subprocess.run([args.clang, '--version'], capture_output=True, text=True).stdout
    base = [args.clang, '-std=c99', '-O3', '-ffreestanding', '-fno-builtin', '-pedantic-errors',
            '-Wall', '-Wextra', '-Werror', '-I' + str(support / 'include'), '-I' + str(core)]
    wasm = out / 'memory_rom_store.wasm'
    run([*base, '--target=wasm32', '-nostdlib', str(core / 'memory_rom.c'), str(core / 'memory_rom_store.c'),
         str(wrapper), str(support / 'minilib.c'), '-Wl,--no-entry', '-Wl,--export-all',
         '-Wl,--initial-memory=33554432', '-Wl,--max-memory=33554432', '-Wl,-z,stack-size=65536',
         '-o', str(wasm)], 'wasm-build')
    run([args.node, str(common / 'verify.cjs'), str(wasm), str(args.roms.resolve()),
         str(args.cube.resolve()), str(out / 'wasm-results.json')], 'wasm-execute')
    targets = [('cortex-m3', 'armv7m-none-eabi', ['-mcpu=cortex-m3', '-mthumb'], 1, 1, 40),
               ('rv32im', 'riscv32-none-elf', ['-march=rv32im', '-mabi=ilp32'], 1, 1, 243),
               ('aarch64-be', 'aarch64_be-none-elf', [], 2, 2, 183)]
    for label, triple, options, elf_class, endian, machine in targets:
        for source in [core / 'memory_rom.c', core / 'memory_rom_store.c']:
            name = label + '-' + source.stem
            obj = out / (name + '.o')
            run([*base, '--target=' + triple, *options, '-fstack-usage', '-c', str(source), '-o', str(obj)], name)
            data = obj.read_bytes()
            assert data[:4] == b'\x7fELF' and data[4] == elf_class and data[5] == endian
            assert struct.unpack_from('<H' if endian == 1 else '>H', data, 18)[0] == machine
            metadata['cross_objects'].append(dict(label=name, object_bytes=len(data), object_sha256=sha(obj),
                                                 elf_class=elf_class, elf_endian=endian, elf_machine=machine))
    metadata.update(passed=True, wasm_sha256=sha(wasm),
                    limits='wasm32实际执行五ROM各完整RGB域；三个架构仅ELF对象编译，不代表链接、实板速度、功耗或部署验收。没有OpenMP、AVX2或运行时imports。')
    save()
    print('新存储C99核wasm32全域执行及六个跨目标对象通过')


if __name__ == '__main__':
    main()
