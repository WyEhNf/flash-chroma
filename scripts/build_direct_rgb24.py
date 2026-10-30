"""冻结292实际构建闭包并唯一-j1构建；反查编译依赖，不执行像素。"""
from __future__ import annotations
import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'artifacts/p16-direct-rgb24-build-v1'
FROZEN = ROOT / 'artifacts/p16-direct-rgb24-build-frozen-v1'
BIN = Path('E:/mingw64/bin')
CMAKE = Path('C:/Program Files (x86)/CMake/bin/cmake.exe')


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    if path.exists():
        raise FileExistsError('不覆盖构建证据：' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    if BUILD.exists() or FROZEN.exists():
        raise FileExistsError('不覆盖292构建或冻结')
    generated_path = ROOT / 'artifacts/p16-direct-rgb24-source-v1/generated.json'
    generated = json.loads(generated_path.read_text(encoding='utf-8'))
    for name, expected in generated['outputs'].items():
        assert sha(ROOT / 'experiments/p16-direct-rgb24-runtime' / name) == expected, name
    paths = {ROOT / 'CMakeLists.txt', ROOT / 'AGENTS.md', Path(__file__), ROOT / 'scripts/generate_direct_rgb24.py',
             ROOT / 'experiments/p16-direct-rgb24-plan-v1.md'}
    for folder in ['cpp', 'portable', 'experiments/p16-direct-rgb24-runtime',
                   'experiments/skylake-andn-normal-runtime', 'experiments/skylake-domain-isolated-runtime',
                   'experiments/skylake-exception-runtime', 'experiments/skylake-suffix-cache-runtime', 'experiments/channel-runtime']:
        paths.update(path for path in (ROOT / folder).rglob('*') if path.is_file() and
                     (path.suffix in ['.c', '.cpp', '.h', '.hpp'] or path.name == 'CMakeLists.txt'))
    for path in paths:
        if path.suffix == '.py':
            ast.parse(path.read_bytes().decode('utf-8-sig'), filename=str(path))
    env = os.environ.copy()
    env['PATH'] = str(BIN) + os.pathsep + env['PATH']
    tools = {name: BIN / name for name in ['gcc.exe', 'g++.exe', 'mingw32-make.exe', 'libgomp-1.dll', 'libstdc++-6.dll', 'libgcc_s_seh-1.dll']}
    tools['cmake.exe'] = CMAKE
    versions = {}
    for name, command in {'g++': [str(BIN / 'g++.exe'), '--version'], 'target': [str(BIN / 'g++.exe'), '-dumpmachine'],
                          'cmake': [str(CMAKE), '--version'], 'cc1plus': [str(BIN / 'g++.exe'), '-print-prog-name=cc1plus']}.items():
        response = subprocess.run(command, capture_output=True, cwd=ROOT, env=env, check=True)
        versions[name] = response.stdout.decode('utf-8', 'replace')
    tools['cc1plus'] = Path(versions['cc1plus'].strip()).resolve()
    assert tools['cc1plus'].is_file()
    rows = {}
    for path in sorted(paths):
        name = path.relative_to(ROOT).as_posix()
        snapshot = FROZEN / 'sources' / name
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(path.read_bytes())
        rows[name] = {'sha256': sha(path), 'bytes': path.stat().st_size}
    configure = [str(CMAKE), '-S', str(ROOT / 'experiments/p16-direct-rgb24-runtime'), '-B', str(BUILD), '-G', 'MinGW Makefiles',
                 '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_EXPORT_COMPILE_COMMANDS=ON',
                 f'-DCMAKE_C_COMPILER={BIN/"gcc.exe"}', f'-DCMAKE_CXX_COMPILER={BIN/"g++.exe"}', f'-DCMAKE_MAKE_PROGRAM={BIN/"mingw32-make.exe"}']
    build = [str(CMAKE), '--build', str(BUILD), '--target', 'jshc_direct_rgb24', 'p16_direct_rgb24_contracts', '--parallel', '1']
    save(FROZEN / 'frozen.json', {'purpose': '292单次-j1构建；未执行像素合同', 'utc': datetime.now(timezone.utc).isoformat(),
                                  'sources': rows, 'generated_sha256': sha(generated_path), 'toolchain': {name: {'path': str(path), 'sha256': sha(path)} for name, path in tools.items()},
                                  'versions': versions, 'python': sys.version, 'platform': platform.platform(),
                                  'configure_command': configure, 'build_command': build, 'performance_calls': 0})
    BUILD.mkdir(parents=True)
    for name, command in [('configure', configure), ('build', build)]:
        result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, check=False)
        (BUILD / (name + '-stdout.txt')).write_bytes(result.stdout)
        (BUILD / (name + '-stderr.txt')).write_bytes(result.stderr)
        save(BUILD / (name + '-receipt.json'), {'returncode': result.returncode, 'command': command, 'performance_calls': 0})
        if result.returncode:
            raise RuntimeError(name + '失败；保留原件，不重建覆盖')
    dependencies = {}
    depfiles = list(BUILD.rglob('*.obj.d'))
    assert depfiles
    for path in depfiles:
        for line in path.read_text(encoding='utf-8').splitlines()[1:]:
            token = line.strip()
            if token.endswith(' \\'):
                token = token[:-2].rstrip()
            if not token:
                continue
            value = Path(token)
            if not value.is_absolute():
                value = BUILD / value
            value = value.resolve()
            try:
                name = value.relative_to(ROOT).as_posix()
            except ValueError:
                continue
            assert name in rows and sha(value) == rows[name]['sha256'], name
            dependencies[name] = sha(value)
    commands = json.loads((BUILD / 'compile_commands.json').read_text(encoding='utf-8'))
    used = [row for row in commands if 'jshc_direct_rgb24.dir' in row['command'] or 'p16_direct_rgb24_contracts.dir' in row['command']]
    assert used
    for row in used:
        lower = row['command'].lower()
        assert not any(flag in lower for flag in ['-mavx512', '-march=native', '-march=x86-64-v4'])
        name = Path(row['file']).resolve().relative_to(ROOT).as_posix()
        assert name in dependencies, name
    for name, row in rows.items():
        assert sha(ROOT / name) == row['sha256'], name
    dll = BUILD / 'libjshc_direct_rgb24.dll'
    contract = BUILD / 'p16_direct_rgb24_contracts.exe'
    assert dll.is_file() and contract.is_file()
    save(BUILD / 'build-check.json', {'passed': True, 'frozen_sha256': sha(FROZEN / 'frozen.json'),
                                      'frozen_source_count': len(rows), 'actual_repository_dependencies_sha256': dependencies,
                                      'compile_command_count': len(used), 'dll_sha256': sha(dll), 'contract_sha256': sha(contract),
                                      'performance_calls': 0, 'pixel_contracts_executed': False})
    print(json.dumps({'passed': True, 'sources': len(rows), 'actual_repository_dependencies': len(dependencies),
                      'dll_sha256': sha(dll), 'contract_sha256': sha(contract), 'performance_calls': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
