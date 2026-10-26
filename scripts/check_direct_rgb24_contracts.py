"""292独立有限合同唯一执行；先冻结exe/DLL/源，不替代真实模型全域质量。"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'artifacts/p16-direct-rgb24-build-v1'
OUT = ROOT / 'artifacts/p16-direct-rgb24-contracts-v1'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    if path.exists():
        raise FileExistsError('不覆盖有限合同：' + str(path))
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    if OUT.exists():
        raise FileExistsError('不覆盖292有限执行目录')
    build = json.loads((BUILD / 'build-check.json').read_text(encoding='utf-8'))
    assert build['passed'] and not build['pixel_contracts_executed']
    frozen = json.loads((ROOT / 'artifacts/p16-direct-rgb24-build-frozen-v1/frozen.json').read_text(encoding='utf-8'))
    for name, row in frozen['sources'].items():
        assert sha(ROOT / name) == row['sha256'], name
    exe = BUILD / 'p16_direct_rgb24_contracts.exe'
    dll = BUILD / 'libjshc_direct_rgb24.dll'
    assert sha(exe) == build['contract_sha256'] and sha(dll) == build['dll_sha256']
    OUT.mkdir(parents=True)
    protocol = {'purpose': '完整RGB24值与精确src/dst/末table guard；不拟合、不性能',
                'sources': {name: row['sha256'] for name, row in frozen['sources'].items()},
                'driver_sha256': sha(Path(__file__)), 'exe_sha256': sha(exe), 'dll_sha256': sha(dll),
                'expected_compile_color_cases': 7, 'expected_guarded_cases': 152, 'performance_calls': 0}
    save(OUT / 'protocol.json', protocol)
    result = subprocess.run([str(exe)], capture_output=True, check=False, cwd=ROOT)
    (OUT / 'stdout.txt').write_bytes(result.stdout)
    (OUT / 'stderr.txt').write_bytes(result.stderr)
    save(OUT / 'execution.json', {'returncode': result.returncode, 'command': [str(exe)], 'protocol_sha256': sha(OUT / 'protocol.json')})
    if result.returncode:
        raise RuntimeError('292有限native失败，保留原输出并STOP')
    native = json.loads(result.stdout.decode('utf-8'))
    assert native['passed'] and native['compile_color_cases'] == 7 and native['guarded_cases'] == 152
    assert native['guard_bytes'] == 4 and native['performance_calls'] == 0
    for name, expected in protocol['sources'].items():
        assert sha(ROOT / name) == expected, name
    assert sha(exe) == protocol['exe_sha256'] and sha(dll) == protocol['dll_sha256']
    save(OUT / 'results.json', {'passed': True, 'native': native, 'protocol_sha256': sha(OUT / 'protocol.json'),
                               'sources_unchanged': len(protocol['sources']), 'performance_calls': 0})
    print(json.dumps({'passed': True, 'native': native, 'sources_unchanged': len(protocol['sources'])}, ensure_ascii=False))


if __name__ == '__main__':
    main()
