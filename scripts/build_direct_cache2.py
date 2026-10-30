"""冻结293/294的实际构建闭包，单次-j1构建并反查依赖；不运行像素。"""
import argparse
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
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--variant', choices=['u16', 'rgb24'], required=True)
    a = p.parse_args()
    name = a.variant + '-cache2'
    product = 'direct_' + a.variant + '_cache2'
    build = ROOT / f'artifacts/p16-direct-{name}-build-v1'
    frozen = ROOT / f'artifacts/p16-direct-{name}-build-frozen-v1'
    generated_path = ROOT / f'artifacts/p16-direct-{name}-source-v1/generated.json'
    generated = json.loads(generated_path.read_text(encoding='utf-8'))
    runtime = ROOT / f'experiments/p16-direct-{name}-runtime'
    if build.exists() or frozen.exists():
        raise FileExistsError('不覆盖缓存版本构建')
    for filename, row in generated['outputs'].items():
        assert sha(runtime / filename) == row['sha256'], filename
    paths = {ROOT / 'CMakeLists.txt', ROOT / 'AGENTS.md', Path(__file__),
             ROOT / 'scripts/generate_direct_cache2.py', ROOT / 'experiments/p16-direct-cache2-plan-v1.md'}
    for folder in ['cpp', 'portable', f'experiments/p16-direct-{name}-runtime',
                   'experiments/skylake-andn-normal-runtime', 'experiments/skylake-domain-isolated-runtime',
                   'experiments/skylake-exception-runtime', 'experiments/skylake-suffix-cache-runtime',
                   'experiments/channel-runtime']:
        paths.update(path for path in (ROOT / folder).rglob('*') if path.is_file() and
                     (path.suffix in ['.c', '.cpp', '.h', '.hpp'] or path.name == 'CMakeLists.txt'))
    for path in paths:
        if path.suffix == '.py':
            ast.parse(path.read_bytes().decode('utf-8-sig'), filename=str(path))
    environment = os.environ.copy()
    environment['PATH'] = str(BIN) + os.pathsep + environment['PATH']
    tools = {n: BIN / n for n in ['gcc.exe', 'g++.exe', 'mingw32-make.exe', 'libgomp-1.dll',
                                  'libstdc++-6.dll', 'libgcc_s_seh-1.dll']}
    tools['cmake.exe'] = CMAKE
    versions = {}
    for key, command in {'g++': [str(BIN / 'g++.exe'), '--version'],
                         'target': [str(BIN / 'g++.exe'), '-dumpmachine'],
                         'cmake': [str(CMAKE), '--version'],
                         'cc1plus': [str(BIN / 'g++.exe'), '-print-prog-name=cc1plus']}.items():
        response = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True, check=True)
        versions[key] = response.stdout.decode('utf-8', 'replace')
    tools['cc1plus'] = Path(versions['cc1plus'].strip()).resolve()
    assert tools['cc1plus'].is_file()
    identities = {}
    for path in sorted(paths):
        filename = path.relative_to(ROOT).as_posix()
        snapshot = frozen / 'sources' / filename
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(path.read_bytes())
        identities[filename] = {'sha256': sha(path), 'bytes': path.stat().st_size}
    configure = [str(CMAKE), '-S', str(runtime), '-B', str(build), '-G', 'MinGW Makefiles',
                 '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_EXPORT_COMPILE_COMMANDS=ON',
                 f'-DCMAKE_C_COMPILER={BIN/"gcc.exe"}', f'-DCMAKE_CXX_COMPILER={BIN/"g++.exe"}',
                 f'-DCMAKE_MAKE_PROGRAM={BIN/"mingw32-make.exe"}']
    compile_command = [str(CMAKE), '--build', str(build), '--target', 'jshc_' + product,
                       'p16_' + product + '_contracts', '--parallel', '1']
    save(frozen / 'frozen.json', {'purpose': __doc__, 'variant': a.variant,
         'utc': datetime.now(timezone.utc).isoformat(), 'sources': identities,
         'generated_sha256': sha(generated_path), 'toolchain': {n: {'path': str(v), 'sha256': sha(v)} for n, v in tools.items()},
         'versions': versions, 'python': sys.version, 'platform': platform.platform(),
         'configure_command': configure, 'build_command': compile_command,
         'pixel_apply_calls': 0, 'performance_calls': 0})
    build.mkdir(parents=True)
    for label, command in [('configure', configure), ('build', compile_command)]:
        response = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True, check=False)
        (build / (label + '-stdout.txt')).write_bytes(response.stdout)
        (build / (label + '-stderr.txt')).write_bytes(response.stderr)
        save(build / (label + '-receipt.json'), {'returncode': response.returncode, 'command': command})
        if response.returncode:
            raise RuntimeError(label + '失败，保留原件')
    dependencies = {}
    depfiles = list(build.rglob('*.obj.d'))
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
                value = build / value
            value = value.resolve()
            try:
                filename = value.relative_to(ROOT).as_posix()
            except ValueError:
                continue
            assert filename in identities and sha(value) == identities[filename]['sha256'], filename
            dependencies[filename] = sha(value)
    commands = json.loads((build / 'compile_commands.json').read_text(encoding='utf-8'))
    used = [row for row in commands if ('jshc_' + product + '.dir') in row['command'] or
            ('p16_' + product + '_contracts.dir') in row['command']]
    assert used
    for row in used:
        assert not any(flag in row['command'].lower() for flag in ['-mavx512', '-march=native', '-march=x86-64-v4'])
        filename = Path(row['file']).resolve().relative_to(ROOT).as_posix()
        assert filename in dependencies
    for filename, row in identities.items():
        assert sha(ROOT / filename) == row['sha256'], filename
    dll, contract = build / ('libjshc_' + product + '.dll'), build / ('p16_' + product + '_contracts.exe')
    assert dll.is_file() and contract.is_file()
    result = {'passed': True, 'variant': a.variant, 'frozen_sha256': sha(frozen / 'frozen.json'),
              'frozen_source_count': len(identities), 'actual_repository_dependencies_sha256': dependencies,
              'compile_command_count': len(used), 'dll_sha256': sha(dll), 'contract_sha256': sha(contract),
              'pixel_contracts_executed': False, 'performance_calls': 0}
    save(build / 'build-check.json', result)
    print(json.dumps({k: v for k, v in result.items() if k != 'actual_repository_dependencies_sha256'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
