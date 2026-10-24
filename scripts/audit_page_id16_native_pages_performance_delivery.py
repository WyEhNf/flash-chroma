"""独立核index或指定HEAD的冻结字节与发布ZIP；不重新调用native或重算速度。"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PLAN_NAME = 'experiments/page-id16-native-pages-performance-v1.json'
PLAN_SHA = '3a78b8c93efdfcb2649955b924888f647a35f0e1f8631a217e75faa55f3ae606'
SUMMARY_SHA = '7148d9e1368b27196412cccaa041feb6cd0f07599d6731eb06fbccb8cb44f7fa'
PREFIX = 'report/data/p16-page-native-pages-performance-v1/'
SUPPORT = (
    'scripts/archive_page_id16_native_pages_performance.py',
    'scripts/audit_page_id16_native_pages_performance_delivery.py',
    'experiments/page-id16-native-pages-wasm-design-v1.md',
)
TEXT = {'.gitattributes', 'docs/stages/2026-10-24-memory-page-native-pages.md',
        'docs/stages/2026-10-24-memory-evidence-overview.md'}


def digest(value):
    return hashlib.sha256(value).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tree', required=True, help='index或实际40位HEAD')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), '交付审计输出不覆盖'
    plan = json.loads((ROOT / PLAN_NAME).read_text(encoding='utf-8'))
    assert digest((ROOT / PLAN_NAME).read_bytes()) == PLAN_SHA
    frozen = plan['source_sha256']
    manifest_path = ROOT / PREFIX / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    paths = set(frozen) | {PLAN_NAME} | set(SUPPORT) | TEXT
    paths |= {PREFIX + name for name in manifest['files']} | {PREFIX + 'manifest.json'}
    if args.tree == 'index':
        staged = set(subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=ROOT).decode().splitlines())
        assert staged <= paths, '禁止混入其它暂存路径：' + str(sorted(staged - paths))
        required = set(SUPPORT) | {PLAN_NAME} | TEXT | {PREFIX + name for name in manifest['files']} | {PREFIX + 'manifest.json'}
        assert required <= staged, '本阶段交付未全部显式暂存：' + str(sorted(required - staged))
        tree = ':'
    else:
        actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
        assert args.tree == actual and len(actual) == 40, '仅审计实际HEAD，不偷换commit'
        assert not subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=ROOT)
        tree = actual + ':'
    ordered = sorted(paths)
    request = ''.join(tree + name + '\n' for name in ordered).encode()
    stream = io.BytesIO(subprocess.check_output(['git', 'cat-file', '--batch'], input=request, cwd=ROOT))
    blobs, canonical = {}, []
    for name in ordered:
        header = stream.readline().split()
        assert len(header) == 3 and header[1] == b'blob', (name, header)
        raw = stream.read(int(header[2]))
        assert stream.read(1) == b'\n'
        work = (ROOT / name).read_bytes()
        if name in TEXT:
            assert name not in frozen and raw == work.replace(b'\r\n', b'\n'), name
            canonical.append(dict(path=name, tree_sha256=digest(raw), worktree_sha256=digest(work)))
        else:
            assert raw == work, '冻结或交付原字节不同：' + name
        if name in frozen:
            assert digest(raw) == frozen[name], '冻结源码SHA不同：' + name
        blobs[name] = raw
    assert stream.read() == b'', 'Git batch输出存在未消费内容'
    assert digest(blobs[PLAN_NAME]) == PLAN_SHA
    assert json.loads(blobs[PREFIX + 'manifest.json']) == manifest
    for name, item in manifest['files'].items():
        raw = blobs[PREFIX + name]
        assert len(raw) == item['bytes'] and digest(raw) == item['sha256'], name
    members = 0
    with zipfile.ZipFile(io.BytesIO(blobs[PREFIX + 'frozen-source.zip'])) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(set(archive.namelist()))
        members += len(archive.infolist())
        assert set(archive.namelist()) == set(frozen) | {PLAN_NAME} | set(SUPPORT)
        for name, expected in frozen.items():
            assert archive.read(name) == blobs[name] and digest(archive.read(name)) == expected
        assert archive.read(PLAN_NAME) == blobs[PLAN_NAME]
        for name in SUPPORT:
            assert archive.read(name) == blobs[name]
            assert digest(blobs[name]) == manifest['support_sources'][name]['sha256']
    with zipfile.ZipFile(io.BytesIO(blobs[PREFIX + 'experiment-raw.zip'])) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(set(archive.namelist()))
        members += len(archive.infolist())
        assert set(archive.namelist()) == set(manifest['raw_members'])
        roles = ['ref78', 'ref80', 'linear_c99', 'copy4_c99', 'p4_avx', 'pages_c99']
        assert plan['roles'] == roles
        raw_expected = {'performance/driver.json', 'performance/summary.json',
                        'process-preflight.json', 'invocation.json', 'invocation.log'}
        raw_expected.update(f'performance/worker{worker}/{name}' for worker in range(4)
                            for name in ('calls.jsonl', 'environment-end.json', 'partial.json', 'results.json'))
        raw_expected.update(f'performance/rss-{role}/{name}' for role in roles
                            for name in ('environment-end.json', 'rss.json'))
        assert len(raw_expected) == 33 and set(archive.namelist()) == raw_expected
        for name, item in manifest['raw_members'].items():
            raw = archive.read(name)
            assert len(raw) == item['bytes'] and digest(raw) == item['sha256'], name
        for name, member in {'performance-summary.json': 'performance/summary.json',
                             'driver.json': 'performance/driver.json',
                             'process-preflight.json': 'process-preflight.json',
                             'invocation.json': 'invocation.json'}.items():
            assert archive.read(member) == blobs[PREFIX + name]
        summary_raw = archive.read('performance/summary.json')
        assert digest(summary_raw) == manifest['summary_sha256'] == SUMMARY_SHA
        summary = json.loads(summary_raw)
        assert summary['audit_passed'] and summary['plan_sha256'] == PLAN_SHA
        assert summary['global_tier'] is None and len(summary['valid_low50_main_examples']) == 3
        driver = json.loads(archive.read('performance/driver.json'))
        labels = [f'worker{worker}' for worker in range(4)] + ['rss-' + role for role in roles]
        assert driver['passed'] and driver['plan_sha256'] == PLAN_SHA
        assert [job['label'] for job in driver['jobs']] == labels
        assert all(job['returncode'] == 0 for job in driver['jobs'])
        for worker in range(4):
            value = json.loads(archive.read(f'performance/worker{worker}/results.json'))
            assert value['passed'] and value['worker'] == worker and value['plan_sha256'] == PLAN_SHA
            assert len(value['rows']) == 480 and len(value['input_identities']) == 22
            assert sum(row['hash_checked'] for row in value['rows']) == 120
            assert all(row['returncode'] == 0 for row in value['rows'])
            assert set(value['identities']) == set(roles)
            assert all(value['identities'][role]['capacity'] == plan['capacities'][role] for role in roles)
        for label in labels:
            ended = json.loads(archive.read('performance/' + label + '/environment-end.json'))
            assert ended['matches'] and ended['actual'] == ended['expected'] == plan['required_environment']
        for role in roles:
            value = json.loads(archive.read(f'performance/rss-{role}/rss.json'))
            assert value['role'] == role and value['plan_sha256'] == PLAN_SHA
            assert value['identity']['capacity'] == plan['capacities'][role]
        invocation = json.loads(archive.read('invocation.json'))
        assert invocation['exit_code'] == 0 and invocation['plan_sha256'] == PLAN_SHA
    result = dict(passed=True, tree=args.tree, plan_sha256=PLAN_SHA, checked_paths=len(paths),
                  frozen_sources=len(frozen), input_identities=len(plan['input_sha256']), zip_members=members,
                  canonical_unfrozen_files=canonical,
                  scope='只读取index/实际HEAD原字节、冻结SHA、源ZIP与原raw副本/manifest/CRC。审计结果写在ZIP之外，不冒称自包含于被审tree；没有native重采、没有恢复旧资格。')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(dict(passed=True, tree=args.tree, paths=len(paths), sources=len(frozen), zip_members=members), flush=True)


if __name__ == '__main__':
    main()
