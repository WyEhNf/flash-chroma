"""按冻结输入同时构建Skylake调度的参考库与独立候选，不覆盖既有构建。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cmake', default='cmake')
    parser.add_argument('--compiler', default='g++')
    parser.add_argument('--c-compiler', default='gcc')
    parser.add_argument('--generator')
    args = parser.parse_args()
    args.plan = args.plan.resolve(); out = args.output.resolve(); plan = read(args.plan)
    if out.exists():
        raise ValueError('构建输出必须为新目录')
    sources = plan['source_sha256']
    for name, sha in sources.items():
        if digest(ROOT/name) != sha:
            raise ValueError('冻结源码不同：'+name)
    compiler = subprocess.check_output([args.compiler, '--version'], text=True, encoding='utf-8')
    if 'local_compiler' in plan and platform.system() == 'Windows':
        if digest(args.compiler) != plan['local_compiler']['sha256']:
            raise ValueError('本机编译器不是冻结版本')
    out.mkdir(parents=True)
    configure = [args.cmake, '-S', str(ROOT/plan.get('cmake_project', 'experiments/skylake-runtime')), '-B', str(out),
        '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_EXPORT_COMPILE_COMMANDS=ON',
        '-DCMAKE_CXX_COMPILER='+args.compiler, '-DCMAKE_C_COMPILER='+args.c_compiler]
    if args.generator:
        configure += ['-G', args.generator]
    commands = [configure, [args.cmake, '--build', str(out), '--config', 'Release', '--parallel', '4',
        '--target', *plan.get('cmake_targets', ['jshc_skylake_reference', 'jshc_skylake_packed'])]]
    records = []
    for command in commands:
        proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
        records.append({'command': command, 'returncode': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr})
        (out/'build-log.json').write_text(json.dumps(records, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        if proc.returncode:
            raise RuntimeError(proc.stdout+'\n'+proc.stderr)
    libraries = read(out/'libraries-Release.json')
    for name, sha in sources.items():
        if digest(ROOT/name) != sha:
            raise ValueError('构建期间源码改变：'+name)
    compile_commands = read(out/'compile_commands.json')
    for item in compile_commands:
        command = item['command']; name = Path(item['file']).name
        if any(flag in command for flag in ('-march=', '-mavx512', '-mfma', '-ffast-math', '-Ofast')):
            raise ValueError('不得通过全局架构/AVX512/FMA/fast-math绕过本阶段显式ISA边界')
        if name != 'lut_simd_avx2.cpp' and name != 'channel_avx2.cpp' and '-mavx2' in command:
            raise ValueError('AVX2泄漏到标量/dispatcher翻译单元')
        if name in ('lut_simd_avx2.cpp', 'channel_avx2.cpp') and '-mtune=skylake' not in command:
            raise ValueError('AVX2编译单元未使用Skylake调度')
    files = {k: {'path': str(Path(v).resolve()), 'sha256': digest(v)} for k, v in libraries.items()}
    main_paths = {Path(p).resolve() for p in libraries.values()}
    dependencies = {p.name: digest(p) for p in out.glob('*.dll') if p.resolve() not in main_paths}
    with zipfile.ZipFile(out/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in sources:
            archive.write(ROOT/name, name)
        archive.write(args.plan, args.plan.relative_to(ROOT).as_posix())
    record = {'purpose': __doc__, 'plan_sha256': digest(args.plan), 'compiler': compiler,
        'environment': {'platform': platform.platform(), 'python': sys.version},
        'source_sha256': sources, 'libraries': files, 'dependencies': dependencies,
        'compile_commands_sha256': digest(out/'compile_commands.json'),
        'commands': records, 'abi': 1, 'revisions': plan.get('revisions', {'reference': 2, 'candidate': 3}),
        'scope': '只完成构建与编译参数核对；尚无新增整数正确性、全色域或性能结论。'}
    (out/'build.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'libraries': files, 'build_sha256': digest(out/'build.json')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
