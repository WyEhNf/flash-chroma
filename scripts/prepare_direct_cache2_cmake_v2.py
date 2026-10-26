"""保留294配置失败原件，另立仅修正CMake源文件名的机械v2及执行入口；不构建或运行像素。"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    old = ROOT / 'experiments/p16-direct-rgb24-cache2-runtime'
    new = ROOT / 'experiments/p16-direct-rgb24-cache2-v2-runtime'
    frozen = ROOT / 'artifacts/p16-direct-rgb24-cache2-v2-source-v1'
    if new.exists() or frozen.exists():
        raise FileExistsError('不覆盖294 CMake机械修复')
    failed = ROOT / 'artifacts/p16-direct-rgb24-cache2-build-v1'
    receipt = failed / 'configure-receipt.json'
    assert json.loads(receipt.read_text(encoding='utf-8'))['returncode'] == 1
    assert not (failed / 'build-check.json').exists()
    sources = sorted(p for p in old.iterdir() if p.is_file()) + [Path(__file__), receipt,
        failed / 'configure-stdout.txt', failed / 'configure-stderr.txt',
        ROOT / 'scripts/build_direct_cache2.py', ROOT / 'scripts/observe_direct_cache2.py',
        ROOT / 'scripts/check_direct_cache2_contracts.py']
    new.mkdir(parents=True)
    outputs = {}
    for path in old.iterdir():
        if not path.is_file():
            continue
        raw = path.read_bytes()
        if path.name == 'CMakeLists.txt':
            text = raw.decode('utf-8')
            assert text.count('direct_rgb24_cache2_avx2.cpp') == 3
            raw = text.replace('direct_rgb24_cache2_avx2.cpp', 'direct_rgb24_avx2.cpp').encode('utf-8')
        (new / path.name).write_bytes(raw)
        outputs[path.name] = {'sha256': sha(new / path.name), 'bytes': len(raw), 'identical_to_failed_v1': raw == path.read_bytes()}
    assert sum(not r['identical_to_failed_v1'] for r in outputs.values()) == 1
    generated = {}
    for before, after in [('build_direct_cache2.py', 'build_direct_cache2_cmake_v2.py'),
                          ('observe_direct_cache2.py', 'observe_direct_cache2_cmake_v2.py'),
                          ('check_direct_cache2_contracts.py', 'check_direct_cache2_contracts_cmake_v2.py')]:
        source = ROOT / 'scripts' / before
        target = ROOT / 'scripts' / after
        if target.exists():
            raise FileExistsError('不覆盖新入口')
        text = source.read_text(encoding='utf-8')
        marker = "name = a.variant + '-cache2'"
        assert text.count(marker) == 1
        text = text.replace(marker, "assert a.variant == 'rgb24', '机械v2仅修复294构建文件名'\n    name = 'rgb24-cache2-v2'", 1)
        if before.startswith('build_'):
            marker = "ROOT / 'scripts/generate_direct_cache2.py', ROOT / 'experiments/p16-direct-cache2-plan-v1.md'"
            assert text.count(marker) == 1
            text = text.replace(marker, "ROOT / 'scripts/generate_direct_cache2.py', ROOT / 'scripts/prepare_direct_cache2_cmake_v2.py', ROOT / 'experiments/p16-direct-cache2-plan-v1.md'", 1)
        target.write_text(text, encoding='utf-8', newline='\n')
        generated[after] = sha(target)
    identities = {}
    for path in sources:
        name = path.relative_to(ROOT).as_posix()
        snapshot = frozen / 'sources' / name
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(path.read_bytes())
        identities[name] = {'sha256': sha(path), 'bytes': path.stat().st_size}
    save = lambda name, value: (frozen / name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    save('frozen.json', {'purpose': __doc__, 'sources': identities,
         'old_failure_receipt_sha256': sha(receipt), 'new_revision': 294,
         'mechanical_change': '仅三个CMake源文件名，C++全部原字节、预算/模型/算法/flags不变',
         'generated_scripts_sha256': generated, 'pixel_apply_calls': 0, 'performance_calls': 0})
    save('generated.json', {'outputs': outputs, 'frozen_sha256': sha(frozen / 'frozen.json'),
                          'pixel_apply_calls': 0, 'performance_calls': 0})
    print(json.dumps({'passed': True, 'cpp_changes': 0, 'cmake_filename_replacements': 3,
                      'new_revision': 294, 'new_scripts': generated, 'native_calls': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
