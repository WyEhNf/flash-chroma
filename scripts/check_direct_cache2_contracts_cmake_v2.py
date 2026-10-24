"""唯一运行293/294各自链接的有限合同，保存原始输出；不计性能。"""
import argparse
import json
from pathlib import Path
import subprocess
from build_direct_cache2 import ROOT, sha, save


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--variant', choices=['u16', 'rgb24'], required=True)
    a = p.parse_args()
    assert a.variant == 'rgb24', '机械v2仅修复294构建文件名'
    name = 'rgb24-cache2-v2'
    product = 'direct_' + a.variant + '_cache2'
    build = ROOT / f'artifacts/p16-direct-{name}-build-v1'
    out = ROOT / f'artifacts/p16-direct-{name}-contracts-v1'
    if out.exists():
        raise FileExistsError('不覆盖有限合同')
    checked = json.loads((build / 'build-check.json').read_text(encoding='utf-8'))
    frozen = ROOT / f'artifacts/p16-direct-{name}-build-frozen-v1/frozen.json'
    assert checked['passed'] and checked['frozen_sha256'] == sha(frozen)
    sources = json.loads(frozen.read_text(encoding='utf-8'))['sources']
    for filename, row in sources.items():
        assert sha(ROOT / filename) == row['sha256'], filename
    exe = build / ('p16_' + product + '_contracts.exe')
    dll = build / ('libjshc_' + product + '.dll')
    assert sha(exe) == checked['contract_sha256'] and sha(dll) == checked['dll_sha256']
    out.mkdir(parents=True)
    protocol = {'purpose': __doc__, 'variant': a.variant, 'driver_sha256': sha(Path(__file__)),
                'build_frozen_sha256': sha(frozen), 'build_check_sha256': sha(build / 'build-check.json'),
                'exe_sha256': sha(exe), 'dll_sha256': sha(dll), 'performance_calls': 0}
    save(out / 'protocol.json', protocol)
    response = subprocess.run([str(exe)], cwd=ROOT, capture_output=True, check=False)
    (out / 'stdout.txt').write_bytes(response.stdout)
    (out / 'stderr.txt').write_bytes(response.stderr)
    save(out / 'execution.json', {'returncode': response.returncode, 'command': [str(exe)],
                                 'protocol_sha256': sha(out / 'protocol.json')})
    if response.returncode:
        raise RuntimeError('有限合同失败，保留并停止')
    native = json.loads(response.stdout.decode('utf-8'))
    assert native['passed'] and native['guard_bytes'] == 4 and native['performance_calls'] == 0
    if a.variant == 'u16':
        assert native['palette_boundary_cases'] == 6 and native['compile_id_cases'] == 5
        assert native['guarded_cases'] == (88 if native['bmi_supported'] else 22)
    else:
        assert native['compile_color_cases'] == 7
        assert native['guarded_cases'] == 152
    for filename, row in sources.items():
        assert sha(ROOT / filename) == row['sha256']
    assert sha(exe) == protocol['exe_sha256'] and sha(dll) == protocol['dll_sha256']
    save(out / 'results.json', {'passed': True, 'native': native,
         'protocol_sha256': sha(out / 'protocol.json'), 'sources_unchanged': len(sources), 'performance_calls': 0})
    print(json.dumps({'passed': True, 'variant': a.variant, 'native': native}, ensure_ascii=False))


if __name__ == '__main__':
    main()
