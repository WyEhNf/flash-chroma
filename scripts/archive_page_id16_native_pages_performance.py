"""只封存既有native页指针1920调用及六RSS；不运行模型或重新审计速度。"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / 'experiments/page-id16-native-pages-performance-v1.json'
PLAN_SHA = '3a78b8c93efdfcb2649955b924888f647a35f0e1f8631a217e75faa55f3ae606'
SUMMARY_SHA = '7148d9e1368b27196412cccaa041feb6cd0f07599d6731eb06fbccb8cb44f7fa'
RAW = ROOT / 'artifacts/p16-page-native-pages-performance-v1'
EXTRAS = {
    'process-preflight.json': ROOT / 'artifacts/p16-page-native-pages-process-preflight-v1.json',
    'invocation.json': ROOT / 'artifacts/p16-page-native-pages-performance-invocation-v1.json',
    'invocation.log': ROOT / 'artifacts/p16-page-native-pages-performance-invocation-v1.log',
}
SUPPORT = (
    'scripts/archive_page_id16_native_pages_performance.py',
    'scripts/audit_page_id16_native_pages_performance_delivery.py',
    'experiments/page-id16-native-pages-wasm-design-v1.md',
)


def digest(value):
    return hashlib.sha256(value).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def package(path, items):
    with zipfile.ZipFile(path, 'x', zipfile.ZIP_DEFLATED) as archive:
        for name, source in sorted(items.items()):
            archive.write(source, name)
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        assert len(names) == len(set(names)) == len(items) and set(names) == set(items)
        assert archive.testzip() is None
        for name, source in items.items():
            assert archive.read(name) == source.read_bytes(), name


def checked_raw(plan):
    roles = ['ref78', 'ref80', 'linear_c99', 'copy4_c99', 'p4_avx', 'pages_c99']
    assert plan['roles'] == roles
    expected = {'driver.json', 'summary.json'}
    expected.update(f'worker{worker}/{name}' for worker in range(4)
                    for name in ('calls.jsonl', 'environment-end.json', 'partial.json', 'results.json'))
    expected.update(f'rss-{role}/{name}' for role in roles
                    for name in ('environment-end.json', 'rss.json'))
    actual = {p.relative_to(RAW).as_posix() for p in RAW.rglob('*') if p.is_file()}
    assert actual == expected and len(actual) == 30, (actual - expected, expected - actual)
    driver = read(RAW / 'driver.json')
    labels = [f'worker{worker}' for worker in range(4)] + ['rss-' + role for role in roles]
    assert driver['passed'] and driver['plan_sha256'] == PLAN_SHA
    assert [job['label'] for job in driver['jobs']] == labels
    assert all(job['returncode'] == 0 for job in driver['jobs'])
    for worker in range(4):
        value = read(RAW / f'worker{worker}/results.json')
        assert value['passed'] and value['worker'] == worker and value['plan_sha256'] == PLAN_SHA
        assert len(value['rows']) == 480 and len(value['input_identities']) == 22
        assert sum(row['hash_checked'] for row in value['rows']) == 120
        assert all(row['returncode'] == 0 for row in value['rows'])
        assert set(value['identities']) == set(roles)
        assert all(value['identities'][role]['capacity'] == plan['capacities'][role] for role in roles)
    for label in labels:
        ended = read(RAW / label / 'environment-end.json')
        assert ended['matches'] and ended['actual'] == ended['expected'] == plan['required_environment']
    for role in roles:
        value = read(RAW / ('rss-' + role) / 'rss.json')
        assert value['role'] == role and value['plan_sha256'] == PLAN_SHA
        assert value['identity']['capacity'] == plan['capacities'][role]
    return {'performance/' + name: RAW / name for name in sorted(expected)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert digest(PLAN.read_bytes()) == PLAN_SHA
    plan = read(PLAN)
    assert len(plan['source_sha256']) == 55 and len(plan['input_sha256']) == 76
    for name, expected in plan['source_sha256'].items():
        assert digest((ROOT / name).read_bytes()) == expected, name
    assert digest((RAW / 'summary.json').read_bytes()) == SUMMARY_SHA
    summary = read(RAW / 'summary.json')
    assert summary['audit_passed'] and summary['plan_sha256'] == PLAN_SHA
    assert (summary['calls'], summary['timed'], summary['output_sha_checks'],
            summary['input_sha_checks'], len(summary['controls']), len(summary['pair_metrics'])) == (1920, 1600, 480, 88, 240, 120)
    assert summary['global_tier'] is None and len(summary['valid_low50_main_examples']) == 3
    invocation = read(EXTRAS['invocation.json'])
    assert invocation['exit_code'] == 0 and invocation['plan_sha256'] == PLAN_SHA
    assert (ROOT / invocation['output']).resolve() == RAW.resolve()
    assert (ROOT / invocation['log']).resolve() == EXTRAS['invocation.log'].resolve()
    raw = checked_raw(plan)
    args.output.mkdir(parents=True, exist_ok=False)
    raw.update(EXTRAS)
    package(args.output / 'experiment-raw.zip', raw)
    sources = {name: ROOT / name for name in plan['source_sha256']}
    sources[PLAN.relative_to(ROOT).as_posix()] = PLAN
    for name in SUPPORT:
        sources[name] = ROOT / name
    package(args.output / 'frozen-source.zip', sources)
    copies = {'performance-summary.json': RAW / 'summary.json',
              'driver.json': RAW / 'driver.json',
              'process-preflight.json': EXTRAS['process-preflight.json'],
              'invocation.json': EXTRAS['invocation.json']}
    for name, source in copies.items():
        (args.output / name).write_bytes(source.read_bytes())
    manifest = dict(purpose=__doc__, plan_sha256=PLAN_SHA,
        summary_sha256=SUMMARY_SHA, fixed_formal_raw_files=30, expected_driver_processes=10,
        files={path.name: dict(bytes=path.stat().st_size, sha256=digest(path.read_bytes()))
               for path in sorted(args.output.iterdir())},
        raw_members={name: dict(bytes=source.stat().st_size, sha256=digest(source.read_bytes()))
                     for name, source in sorted(raw.items())},
        frozen_sources=plan['source_sha256'],
        support_sources={name: dict(sha256=digest((ROOT / name).read_bytes()),
                                   scope='交付或静态移植方案；不属于正式性能执行闭包。') for name in SUPPORT},
        references='原P4 ROM/DLL/55执行源/76输入身份沿冻结计划及quality包，不重新导出或编译。保存全部四worker和六RSS、三时点实际模块、早0x55/版本/env/末环境、UTC与进程预检。36自身AA/13主pair失效、三个有效低50反例全部保留，全36格不给资格。WASM仅文本未执行，不能继承旧WASM或旧linear速度资格。')
    (args.output / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(dict(passed=True, output=str(args.output), raw_members=len(raw),
               source_members=len(sources), bytes=sum(path.stat().st_size for path in args.output.iterdir())), flush=True)


if __name__ == '__main__':
    main()
