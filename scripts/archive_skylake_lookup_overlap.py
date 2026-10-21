"""保存查表等待诊断和59单次组合筛查的原始证据；不重新运行像素。"""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'report/data/skylake-lookup-overlap-v1'
SOURCES = [
    'artifacts/skylake-lookup-diagnostics-v1',
    'artifacts/skylake-vectorpack-linux-build-v1',
    'artifacts/skylake-vectorpack-linux-static-v1',
    'artifacts/skylake-vectorpack-linux-full-v1',
    'artifacts/skylake-vectorpack-pmu-v1',
]


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    if OUT.exists():
        raise ValueError('不得覆盖现有归档')
    OUT.mkdir(parents=True)
    for name in SOURCES:
        source = ROOT / name
        target = OUT / source.name
        for path in sorted(source.rglob('*')):
            if not path.is_file() or path.suffix not in ('.json', '.zip', '.asm', '.log', '.txt'):
                continue
            if path.stat().st_size > 10 * 2**20:
                raise ValueError('意外大文件：' + str(path))
            item = target / path.relative_to(source)
            item.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, item)
    build = ROOT / SOURCES[1]
    with zipfile.ZipFile(OUT / 'candidate-binaries-and-objects.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        files = [p for p in build.rglob('*') if p.is_file() and p.suffix in ('.so', '.o')]
        for path in sorted(files):
            archive.write(path, path.relative_to(build).as_posix())
    with zipfile.ZipFile(OUT / 'diagnostic-generators.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in ('artifacts/prepare_lookup_diagnostic.py', 'artifacts/profile_swap_layout_locality.py'):
            archive.write(ROOT / name, name)
    items = {p.relative_to(OUT).as_posix(): {'bytes': p.stat().st_size, 'sha256': digest(p)}
             for p in sorted(OUT.rglob('*')) if p.is_file()}
    save(OUT / 'manifest.json', {'purpose': __doc__, 'files': items, 'self_included': False,
                                 'later_documents_included': False})
    print('归档', len(items), '份', sum(x['bytes'] for x in items.values()), '字节')


if __name__ == '__main__':
    main()
