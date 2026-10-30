"""冻结并生成293/294独立缓存预算版本；只改预算、修订号和产品名，不构建或运行像素。"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    if path.exists():
        raise FileExistsError('不覆盖新版本证据：' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--variant', choices=['u16', 'rgb24'], required=True)
    a = p.parse_args()
    if a.variant == 'u16':
        old_name, new_name, old_revision, new_revision = 'u16-ilp', 'u16-cache2', 288, 293
        old_product, new_product = 'direct_u16_ilp', 'direct_u16_cache2'
    else:
        old_name, new_name, old_revision, new_revision = 'rgb24', 'rgb24-cache2', 292, 294
        old_product, new_product = 'direct_rgb24', 'direct_rgb24_cache2'
        prerequisite = ROOT / 'artifacts/p16-direct-u16-cache2-observer-v1/results.json'
        proof = json.loads(prerequisite.read_text(encoding='utf-8'))
        assert proof['passed'] and proof['max41_eligible'], '293资格前置未通过'
    old = ROOT / f'experiments/p16-direct-{old_name}-runtime'
    target = ROOT / f'experiments/p16-direct-{new_name}-runtime'
    frozen = ROOT / f'artifacts/p16-direct-{new_name}-source-v1'
    if target.exists() or frozen.exists():
        raise FileExistsError('不覆盖生成版本')
    files = sorted(path for path in old.iterdir() if path.is_file())
    sources = files + [Path(__file__), ROOT / 'AGENTS.md', ROOT / 'experiments/p16-direct-cache2-plan-v1.md']
    identities = {}
    for path in sources:
        name = path.relative_to(ROOT).as_posix()
        snapshot = frozen / 'sources' / name
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(path.read_bytes())
        identities[name] = {'sha256': sha(path), 'bytes': path.stat().st_size}
    save(frozen / 'frozen.json', {'purpose': __doc__, 'sources': identities, 'variant': a.variant,
         'base_revision': old_revision, 'new_revision': new_revision, 'cache_budget_bytes': 2097152,
         'pixel_apply_calls': 0, 'performance_calls': 0})
    target.mkdir()
    outputs = {}
    for path in files:
        raw = path.read_bytes()
        if path.name == 'channel_runtime.cpp':
            text = raw.decode('utf-8')
            for before, after in [('constexpr size_t budget=1024*1024;', 'constexpr size_t budget=2*1024*1024;'),
                                  (f'return {old_revision};', f'return {new_revision};')]:
                assert text.count(before) == 1, before
                text = text.replace(before, after, 1)
            raw = text.encode('utf-8')
        elif path.name == 'CMakeLists.txt':
            text = raw.decode('utf-8')
            assert old_product in text
            raw = text.replace(old_product, new_product).encode('utf-8')
        output = target / path.name
        output.write_bytes(raw)
        outputs[path.name] = {'sha256': sha(output), 'bytes': output.stat().st_size,
                              'identical_to_base': raw == path.read_bytes()}
    assert sum(not row['identical_to_base'] for row in outputs.values()) == 2
    save(frozen / 'generated.json', {'outputs': outputs, 'frozen_sha256': sha(frozen / 'frozen.json'),
                                    'pixel_apply_calls': 0, 'performance_calls': 0})
    print(json.dumps({'variant': a.variant, 'new_revision': new_revision, 'files': len(outputs),
                      'changed_files': [name for name, row in outputs.items() if not row['identical_to_base']],
                      'pixel_apply_calls': 0, 'performance_calls': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
