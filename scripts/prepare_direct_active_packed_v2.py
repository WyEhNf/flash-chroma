"""保留V1冻结FileNotFound原件，只修四依赖实际目录并独立命名。"""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
original = ROOT / 'scripts/census_direct_active_packed.py'
output = ROOT / 'scripts/census_direct_active_packed_v2.py'
assert not output.exists()
assert not (ROOT / 'artifacts/p16-direct-active-packed-v1').exists()
source = original.read_text(encoding='utf-8')
changes = {
    'artifacts/p16-direct-active-packed-v1': 'artifacts/p16-direct-active-packed-v2',
    "Path(library['path']).parent / name": "Path('E:/mingw64/bin') / name",
    "for name in ['scripts/census_direct_active_packed.py',":
        "for name in ['scripts/census_direct_active_packed_v2.py', 'scripts/prepare_direct_active_packed_v2.py',\n"
        "                 'experiments/p16-direct-active-packed-mechanical-v2.md', 'scripts/census_direct_active_packed.py',",
}
for before, after in changes.items():
    assert source.count(before) == 1, before
    source = source.replace(before, after)
output.write_bytes(source.encode('utf-8'))
print({'prepared_v2': str(output), 'mechanical_changes': len(changes), 'algorithm_changes': 0})
