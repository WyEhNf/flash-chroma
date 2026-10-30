"""97只修合同target缺头路径，保留v1失败并复用其生产DLL，不重建模型后端。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    frozen_path = ROOT / 'experiments/p16-shared-proven-repair-v2.json'
    plan = json.loads(frozen_path.read_text(encoding='utf-8'))
    for row in plan['sources']:
        assert digest(Path(row['path'])) == row['sha256'], row['path']
    if a.output.exists():
        raise FileExistsError('97机械合同修复不覆盖')
    a.output.mkdir(parents=True)
    environment = dict(os.environ)
    environment['PATH'] = 'E:/mingw64/bin' + os.pathsep + environment.get('PATH', '')
    cmake = 'C:/Program Files (x86)/CMake/bin/cmake.exe'
    commands = [[cmake, '-S', str(ROOT / 'experiments/p16-shared-proven-contract-v2'), '-B', str(a.output),
        '-G', 'MinGW Makefiles', '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_CXX_COMPILER=E:/mingw64/bin/g++.exe'],
        [cmake, '--build', str(a.output), '--target', 'p16_shared_proven_contract', 'p16_palette_contract', '-j', '1']]
    logs, codes = [], []
    for command in commands:
        run = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True, text=True, encoding='utf-8', errors='replace')
        codes.append(run.returncode);logs.append(run.stdout + run.stderr)
        if run.returncode:
            break
    (a.output / 'build.log').write_text('\n'.join(logs), encoding='utf-8')
    unchanged = all(digest(Path(r['path'])) == r['sha256'] for r in plan['sources'])
    receipt = {'return_code': next((c for c in codes if c), 0), 'sources_unchanged': unchanged,
        'commands': commands, 'source_freeze_sha256': digest(frozen_path), 'quality_calls': 0, 'performance_calls': 0,
        'production_dll_rebuilt': False, 'production_library': plan['production_library'],
        'v1_build_failure_preserved': True, 'repair': '仅为合同target补通用channel-runtime头路径；其他编译选项沿v1。'}
    for name in ('p16_shared_proven_contract.exe', 'p16_palette_contract.exe'):
        path = a.output / name
        if path.exists():
            receipt[name] = digest(path)
    (a.output / 'build-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    assert receipt['return_code'] == 0 and unchanged
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == '__main__':
    main()
