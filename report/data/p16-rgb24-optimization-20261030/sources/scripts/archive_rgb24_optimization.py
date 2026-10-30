"""按字节封存RGB24优化的源码、失败/成功实测及单头交付身份。"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT/'report/data/p16-rgb24-optimization-20261030'
SOURCES = ('src/flash_chroma_direct.inc', 'include/flash_chroma.hpp', 'single_header/CMakeLists.txt',
           'framework/rgb24_regression.cpp', 'scripts/bench_rgb24_regression.py',
           'scripts/compare_framework_kernels.py', 'scripts/archive_rgb24_optimization.py',
           'tests/single_header_rgb24_contract.cpp', 'tests/test_rgb24_regression_reporting.py',
           'scripts/generate_flash_chroma_header.py', 'scripts/install_framework.py')
TEXT = {'.json', '.log', '.txt', '.cpp', '.hpp', '.inc', '.py', '.md', '.ps1'}


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def archive(delivery):
    if DEST.exists():
        raise FileExistsError('拒绝覆盖原始归档；使用--verify只读核验')
    records = []

    def copy(source, relative, kind):
        if not source.is_file(): return
        target = DEST/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        before = digest(source)
        shutil.copyfile(source, target)
        if digest(source) != before or digest(target) != before:
            raise RuntimeError('复制期间内容改变：'+str(source))
        records.append(dict(path=target.relative_to(DEST).as_posix(), bytes=target.stat().st_size,
                            sha256=before, source=str(source), kind=kind))

    for name in SOURCES: copy(ROOT/name, Path('sources')/name, 'source')
    for entry in sorted((ROOT/'artifacts').glob('rgb24-*')):
        paths = [entry] if entry.is_file() else sorted(entry.rglob('*'))
        for path in paths:
            if path.is_file() and path.suffix.lower() in TEXT:
                if path.stat().st_size > 5*1024*1024:
                    raise ValueError('意外的大型文本，先审查：'+str(path))
                copy(path, Path('evidence')/path.relative_to(ROOT/'artifacts'), 'evidence')
    for path in sorted(delivery.iterdir()):
        if path.is_file() and path.suffix.lower() in TEXT:
            copy(path, Path('delivery')/path.name, 'delivery')
    manifest = dict(schema='rgb24_optimization_archive_v1', files=records,
                    scope='保留全部小型回执及源码；LUT、图片、RGB24表、模型与EXE留本地，以SHA绑定。不删除失败场次。')
    (DEST/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return verify()


def verify():
    manifest = json.loads((DEST/'manifest.json').read_text(encoding='utf-8'))
    names = set()
    for row in manifest['files']:
        path = (DEST/row['path']).resolve()
        if not path.is_relative_to(DEST.resolve()) or row['path'] in names:
            raise ValueError('归档路径非法或重复')
        names.add(row['path'])
        if path.stat().st_size != row['bytes'] or digest(path) != row['sha256']:
            raise ValueError('归档内容改变：'+row['path'])
    actual = {p.relative_to(DEST).as_posix() for p in DEST.rglob('*') if p.is_file()}
    if actual != names | {'manifest.json'}: raise ValueError('归档文件集合不符')
    return dict(passed=True, files=len(names), bytes=sum(r['bytes'] for r in manifest['files']),
                manifest_sha256=digest(DEST/'manifest.json'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--delivery', type=Path)
    args = parser.parse_args()
    if not args.verify and args.delivery is None: parser.error('首次归档需要--delivery')
    print(json.dumps(verify() if args.verify else archive(args.delivery.resolve()), ensure_ascii=False, indent=2))
