"""以赛方main注释中的原构建/启动参数验证纯C++交付；不发布性能加速结论。"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess

from check_framework_delivery import parse_output


def identity(path):
    path = Path(path)
    with path.open('rb') as stream:
        sha = hashlib.file_digest(stream, 'sha256').hexdigest()
    return {'path': str(path.resolve()), 'bytes': path.stat().st_size, 'sha256': sha}


def validate(source, compiler, data, output, receipt):
    source, compiler, data, output = (p.resolve() for p in (source, compiler, data, output))
    output.mkdir(parents=True, exist_ok=False)
    for name in ('main.cpp', 'flash_chroma_framework.hpp'):
        shutil.copyfile(source / name, output / name)
    assert sorted(p.suffix for p in output.iterdir()) == ['.cpp', '.hpp']
    inputs = [source / 'main.cpp', source / 'flash_chroma_framework.hpp',
              output / 'main.cpp', output / 'flash_chroma_framework.hpp',
              *(data / 'LUT' / f'Test{i}.3DL' for i in range(1, 5)),
              *(data / 'image' / f'{i}.bin' for i in range(1, 5))]
    before = [identity(p) for p in inputs]
    env = os.environ.copy()
    env['PATH'] = str(compiler.parent) + os.pathsep + env.get('PATH', '')
    started = datetime.now(timezone.utc).isoformat()
    version = subprocess.run([str(compiler), '--version'], env=env, capture_output=True, check=True).stdout.decode('utf-8', 'replace')
    command = [str(compiler), '-O2', '-std=c++17', '-o', 'lut3d', 'main.cpp']
    built = subprocess.run(command, cwd=output, env=env, capture_output=True)
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.with_suffix('.build.log').write_bytes(built.stdout + built.stderr)
    if built.returncode:
        raise RuntimeError('按原指令编译失败：' + str(receipt.with_suffix('.build.log')))
    executable = output / ('lut3d.exe' if os.name == 'nt' else 'lut3d')
    exe_before = identity(executable)
    run_command = [str(executable), os.path.relpath(data, output)]
    ran = subprocess.run(run_command, cwd=output, env=env, capture_output=True)
    receipt.with_suffix('.stdout.log').write_bytes(ran.stdout)
    receipt.with_suffix('.stderr.log').write_bytes(ran.stderr)
    text = ran.stdout.decode('utf-8', 'replace')
    images = parse_output(text, 4) if ran.returncode == 0 else []
    match = re.search(r'FlashChroma compiled=(\d+) available=(\d+) actual_backend=(\d+) representation=(\d+) threads=(\d+)', text)
    actual = dict(zip(('compiled', 'available', 'backend', 'representation', 'threads'), map(int, match.groups()))) if match else None
    after, exe_after = [identity(p) for p in inputs], identity(executable)
    # 此四图数值来自此前同四表FrameworkStep33/chain_ls，避免把参考风格变化当近似误差。
    expected_delta = [1.467711, 1.562505, 1.592951, 1.303775]
    verified = (ran.returncode == 0 and before == after and exe_before == exe_after and actual is not None and
                actual['threads'] == 1 and actual['backend'] == (2 if actual['available'] & 2 else 1) and
                [r['candidate_delta'] for r in images] == expected_delta)
    result = {'passed': verified, 'scope': '题定O2/C++17构建与仅data启动；真实四表四图、运行后端与源/输入/EXE身份；不是稳定性能比较',
              'started_utc': started, 'platform': platform.platform(), 'compiler_version': version.splitlines()[0],
              'build_command': command, 'run_command': run_command, 'cwd': str(output),
              'build_returncode': built.returncode, 'run_returncode': ran.returncode,
              'before': before, 'after': after, 'executable_before': exe_before, 'executable_after': exe_after,
              'actual': actual, 'images': images, 'delta_matches_prior_same_model': [r['candidate_delta'] for r in images] == expected_delta}
    with receipt.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'compiler', 'data', 'output', 'receipt'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    result = validate(args.source, args.compiler, args.data, args.output, args.receipt)
    print(json.dumps({'passed': result['passed'], 'compiler': result['compiler_version'], 'actual': result['actual'],
                      'images': len(result['images'])}, ensure_ascii=False))
    raise SystemExit(0 if result['passed'] else 1)
