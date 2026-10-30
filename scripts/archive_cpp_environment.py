"""封存自动环境探测和题定构建/运行验证；原始证据只读，不收大型工具链/EXE。"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'report/data/p16-cpp-environment-20261030'
SOURCES = ('include/flash_chroma.hpp', 'src/flash_chroma_cpp.inc', 'scripts/generate_flash_chroma_header.py',
           'scripts/install_framework.py', 'scripts/validate_cpp_submission.py', 'scripts/archive_cpp_environment.py',
           'single_header/CMakeLists.txt', 'single_header/embedded_example.cpp',
           'tests/framework_auto_detection_contract.cpp', 'tests/framework_embedded_cpp_contract.cpp',
           'tests/test_framework_auto_detection.py', 'tests/test_framework_embedded_cpp.py',
           'docs/framework-quickstart.md', 'docs/single-header-runtime.md')


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify():
    manifest = json.loads((DEST / 'manifest.json').read_text(encoding='utf-8'))
    names = set()
    for item in manifest['files']:
        path = (DEST / item['path']).resolve()
        if not path.is_relative_to(DEST.resolve()) or item['path'] in names:
            raise ValueError('归档路径无效或重复')
        names.add(item['path'])
        if path.stat().st_size != item['bytes'] or digest(path) != item['sha256']:
            raise ValueError('原字节核验失败：' + item['path'])
    actual = {p.relative_to(DEST).as_posix() for p in DEST.rglob('*') if p.is_file()}
    if actual != names | {'.gitattributes', 'manifest.json'}:
        raise ValueError('归档集合不符')
    return {'passed': True, 'files': len(names), 'bytes': sum(x['bytes'] for x in manifest['files'])}


def archive(contest, embedded):
    if DEST.exists():
        raise FileExistsError('拒绝覆盖证据，使用--verify只读核验')
    DEST.mkdir(parents=True)
    (DEST / '.gitattributes').write_bytes(b'* -text whitespace=-blank-at-eol,-blank-at-eof,space-before-tab,cr-at-eol\n')
    records = []

    def copy(source, relative):
        target = DEST / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        before = digest(source)
        shutil.copyfile(source, target)
        if digest(source) != before or digest(target) != before:
            raise ValueError('复制期间源内容改变')
        records.append({'path': relative.as_posix(), 'source': str(source), 'sha256': before, 'bytes': target.stat().st_size})

    for name in SOURCES:
        copy(ROOT / name, Path('sources') / name)
    evidence = ROOT / 'artifacts/framework-auto-detection-20261030'
    for path in sorted(evidence.iterdir()):
        if path.is_file() and path.suffix in ('.json', '.log', '.md'):
            copy(path, Path('evidence') / path.name)
    for name in ('contest-generation.json', 'contest-build-gcc15.log', 'contest-run-gcc15.log'):
        copy(ROOT / 'artifacts/framework-embedded-cpp-20261030' / name, Path('evidence/initial-exact-command') / name)
    for label, folder in (('contest', contest), ('embedded', embedded)):
        for path in sorted(folder.iterdir()):
            if not path.is_file() or path.suffix not in ('.cpp', '.hpp'):
                raise ValueError('纯C++交付含额外文件：' + str(path))
            copy(path, Path('delivery') / label / path.name)
    (DEST / 'manifest.json').write_text(json.dumps({'schema': 'cpp-environment-archive-v1', 'files': records,
        'scope': '最终自动环境探测、题定O2/C++17命令、真实四图及仅C++交付；不收EXE/大型LUT/图片或不完整工具链'},
        ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return verify()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--contest', type=Path)
    parser.add_argument('--embedded', type=Path)
    args = parser.parse_args()
    if not args.verify and (args.contest is None or args.embedded is None):
        parser.error('首次归档需--contest和--embedded目录')
    print(json.dumps(verify() if args.verify else archive(args.contest.resolve(), args.embedded.resolve()), ensure_ascii=False))
