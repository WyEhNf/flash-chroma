"""封存赛事偏好入口源码、功能核验与交付身份，保留全部失败回执。"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'report/data/p16-framework-preferences-20261030'
SOURCES = ('framework/preference_selection.hpp', 'scripts/install_framework.py',
           'scripts/validate_framework_preferences.py', 'scripts/archive_framework_preferences.py',
           'tests/framework_preference_contract.cpp', 'tests/test_framework_preferences.py',
           'single_header/CMakeLists.txt', 'docs/framework-quickstart.md')
TEXT = {'.json', '.log', '.txt', '.cpp', '.hpp', '.inc', '.py', '.md', '.ps1'}


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify():
    manifest = json.loads((DEST / 'manifest.json').read_text(encoding='utf-8'))
    names = set()
    for row in manifest['files']:
        path = (DEST / row['path']).resolve()
        if not path.is_relative_to(DEST.resolve()) or row['path'] in names:
            raise ValueError('归档路径重复或超出目录')
        names.add(row['path'])
        if path.stat().st_size != row['bytes'] or digest(path) != row['sha256']:
            raise ValueError('归档内容不符：' + row['path'])
    actual = {p.relative_to(DEST).as_posix() for p in DEST.rglob('*') if p.is_file()}
    if actual != names | {'manifest.json', '.gitattributes'}:
        raise ValueError('归档文件集合不符')
    return {'passed': True, 'files': len(names), 'bytes': sum(r['bytes'] for r in manifest['files']),
            'manifest_sha256': digest(DEST / 'manifest.json')}


def archive(delivery):
    if DEST.exists():
        raise FileExistsError('拒绝覆盖归档；使用--verify只读核验')
    DEST.mkdir(parents=True)
    (DEST / '.gitattributes').write_bytes(b'* -text whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol\n')
    rows = []

    def copy(source, target, kind):
        if not source.is_file():
            raise FileNotFoundError(source)
        before = digest(source)
        dest = DEST / target
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
        if digest(source) != before or digest(dest) != before:
            raise ValueError('复制期间来源改变：' + str(source))
        rows.append({'path': target.as_posix(), 'source': str(source), 'kind': kind,
                     'bytes': dest.stat().st_size, 'sha256': before})

    for name in SOURCES:
        copy(ROOT / name, Path('sources') / name, 'source')
    evidence = ROOT / 'artifacts/framework-preferences-20261030'
    for path in sorted(evidence.rglob('*')):
        if path.is_file() and path.suffix.lower() in TEXT:
            if path.stat().st_size > 5 * 1024 * 1024:
                raise ValueError('意外大型文本，需先审查：' + str(path))
            copy(path, Path('evidence') / path.relative_to(evidence), 'evidence')
    for path in sorted(delivery.iterdir()):
        if path.is_file() and path.suffix.lower() in TEXT:
            copy(path, Path('delivery') / path.name, 'delivery')
    manifest = {'schema': 'framework-preferences-archive-v1', 'files': rows,
                'scope': '源码及小型原始回执按原字节保存；LUT/图片/EXE本机保留，以运行前后SHA绑定；非受控优化性能比较'}
    (DEST / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return verify()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--delivery', type=Path)
    args = parser.parse_args()
    if not args.verify and args.delivery is None:
        parser.error('首次归档需要--delivery')
    print(json.dumps(verify() if args.verify else archive(args.delivery.resolve()), ensure_ascii=False, indent=2))
