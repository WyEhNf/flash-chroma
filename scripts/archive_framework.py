"""保留框架阶段的小型原始证据与源码快照，不提交图片、LUT、模型或可执行文件。"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'report/data/p16-framework-20261029'
EXTENSIONS = {'.json', '.log', '.txt', '.md', '.cpp', '.hpp', '.py', '.ps1'}


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def archive(delivery):
    if DEST.exists():
        raise FileExistsError('归档已存在；只读--verify可重新检查，禁止覆盖证据')
    sources = sorted((ROOT/'framework').glob('*'))
    sources += [ROOT/'include/flash_chroma.hpp', ROOT/'single_header/CMakeLists.txt']
    sources += sorted((ROOT/'scripts').glob('*framework*.py'))
    sources += sorted((ROOT/'tests').glob('*framework*'))
    entries = []

    def copy(source, target, scope):
        if not source.is_file():
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        before = sha(source)
        shutil.copyfile(source, target)
        if sha(source) != before or sha(target) != before:
            raise RuntimeError('复制期间内容改变：' + str(source))
        entries.append({'path': target.relative_to(DEST).as_posix(), 'sha256': before,
                        'bytes': target.stat().st_size, 'source': str(source), 'scope': scope})

    for source in sources:
        copy(source, DEST/'sources'/source.relative_to(ROOT), '当前实现源码')
    for item in sorted((ROOT/'artifacts').glob('framework*')):
        paths = [item] if item.is_file() else sorted(item.rglob('*'))
        for source in paths:
            if source.is_file() and source.suffix.lower() in EXTENSIONS:
                if source.stat().st_size > 5 * 1024 * 1024:
                    raise ValueError('意外的大型文本文件，先审核：' + str(source))
                copy(source, DEST/'evidence'/source.relative_to(ROOT/'artifacts'), '原始证据，含失败与历史源码快照')
    for source in sorted(Path(delivery).iterdir()):
        if source.is_file() and source.suffix.lower() in EXTENSIONS:
            copy(source, DEST/'delivery'/source.name, '实际交付源码与清单；EXE留本地')
    manifest = {'schema': 'framework_evidence_archive_v1', 'files': entries,
                'scope': '小型原始回执按字节复制；大表/图片/模型/EXE留本地，通过回执SHA核验。旧失败没有覆盖。'}
    (DEST/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return verify()


def verify():
    manifest = json.loads((DEST/'manifest.json').read_text(encoding='utf-8'))
    names = set()
    for row in manifest['files']:
        path = (DEST/row['path']).resolve()
        if not path.is_relative_to(DEST.resolve()) or row['path'] in names:
            raise ValueError('非法或重复归档路径')
        names.add(row['path'])
        if path.stat().st_size != row['bytes'] or sha(path) != row['sha256']:
            raise ValueError('归档字节不匹配：' + row['path'])
    actual = {p.relative_to(DEST).as_posix() for p in DEST.rglob('*') if p.is_file()}
    if actual != names | {'manifest.json'}:
        raise ValueError('归档文件集合与清单不匹配')
    return {'passed': True, 'files': len(names), 'bytes': sum(r['bytes'] for r in manifest['files']),
            'manifest_sha256': sha(DEST/'manifest.json')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--delivery', type=Path)
    args = parser.parse_args()
    if not args.verify and args.delivery is None:
        parser.error('首次归档必须提供--delivery')
    print(json.dumps(verify() if args.verify else archive(args.delivery), ensure_ascii=False, indent=2))
