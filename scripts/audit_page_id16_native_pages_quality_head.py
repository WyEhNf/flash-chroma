"""针对实际HEAD核所有冻结原字节；未冻结attrs/docs规范化另列。"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def digest(value):
    return hashlib.sha256(value).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('HEAD审计不覆盖')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    assert head.startswith('6434cc8'), '本次针对6434cc8实际交付，不偷换HEAD'
    assert not subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=ROOT)
    plans = [ROOT / 'experiments' / name for name in (
        'page-id16-native-pages-build-v1.json', 'page-id16-native-pages-observer-v2.json',
        'page-id16-native-pages-finite-v1.json', 'page-id16-native-pages-finite-v2.json',
        'page-id16-native-pages-full-v1.json')]
    expected = {}
    paths = set(subprocess.check_output(['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', head], cwd=ROOT).decode().splitlines())
    for plan in plans:
        paths.add(plan.relative_to(ROOT).as_posix())
        for name, value in json.loads(plan.read_text(encoding='utf-8'))['source_sha256'].items():
            if name in expected:
                assert expected[name] == value
            expected[name] = value
            paths.add(name)
    request = ''.join(head + ':' + name + '\n' for name in sorted(paths)).encode()
    stream = io.BytesIO(subprocess.check_output(['git', 'cat-file', '--batch'], input=request, cwd=ROOT))
    blobs = {}
    canonical = []
    for name in sorted(paths):
        header = stream.readline().split()
        assert len(header) == 3, (name, header)
        data = stream.read(int(header[2]))
        assert stream.read(1) == b'\n'
        work = (ROOT / name).read_bytes()
        if name == '.gitattributes' or name.startswith('docs/'):
            assert name not in expected and data == work.replace(b'\r\n', b'\n'), name
            canonical.append(dict(path=name, head_sha256=digest(data), worktree_sha256=digest(work),
                                  normalization='未冻结文本CRLF→LF；不用于原始执行源SHA'))
        else:
            assert data == work, '实际HEAD原字节不同：' + name
        if name in expected:
            assert digest(data) == expected[name], '实际HEAD冻结SHA不同：' + name
        blobs[name] = data
    prefix = 'report/data/p16-page-native-pages-quality-v1/'
    manifest = json.loads(blobs[prefix + 'manifest.json'])
    for name, item in manifest['files'].items():
        assert len(blobs[prefix + name]) == item['bytes'] and digest(blobs[prefix + name]) == item['sha256']
    members = 0
    with zipfile.ZipFile(io.BytesIO(blobs[prefix + 'frozen-source.zip'])) as archive:
        assert archive.testzip() is None
        members += len(archive.infolist())
        for name, value in expected.items():
            assert digest(archive.read(name)) == value and archive.read(name) == blobs[name]
        for plan in plans:
            name = plan.relative_to(ROOT).as_posix()
            assert archive.read(name) == blobs[name]
    with zipfile.ZipFile(io.BytesIO(blobs[prefix + 'experiment-raw.zip'])) as archive:
        assert archive.testzip() is None
        members += len(archive.infolist())
        copies = {
            'build-result.json': 'p16-page-native-pages-observer-v2/build/build.json',
            'finite-audit.json': 'p16-page-native-pages-finite-v2/independent-audit-v3.json',
            'full-result.json': 'p16-page-native-pages-full-v1/quality/results.json',
            'full-audit.json': 'p16-page-native-pages-full-v1/independent-audit.json',
        }
        for name, member in copies.items():
            assert archive.read(member) == blobs[prefix + name]
    assert members == 92
    result = dict(passed=True, purpose=__doc__, audited_head=head, script_sha256=digest(Path(__file__).read_bytes()),
        checked_paths=len(paths), frozen_sources=len(expected), frozen_plans=len(plans), zip_members=members,
        frozen_sha256=expected, canonical_unfrozen_files=canonical,
        previous_gate_failure='前次泛化原字节检查在未冻结.gitattributes正常规范化处STOP；错误地继续commit已发生，历史6434cc8保持。本次只核HEAD，不native重采或改frozen源；没有发现冻结原字节被Git转换，故无需renormalize修源。',
        scope='实际6434cc8 HEAD逐原字节/SHA、全部五计划/46执行源、源ZIP和发布件/CRC闭环；未冻结文本规范化单列。此审计源/结果作为后续补记，不声称已在被审HEAD中。')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(dict(passed=True, head=head, paths=len(paths), sources=len(expected), plans=5,
               zip_members=members, output_sha256=digest(args.output.read_bytes())), flush=True)


if __name__ == '__main__':
    main()
