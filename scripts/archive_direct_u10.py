"""封存289质量、六fresh RSS与八角色正式性能；只离线复算，不重跑映射或计时。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def zip_files(path, members):
    if len(members) != len(set(members)):
        raise ValueError('重复ZIP成员')
    identity = {}
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, source in sorted(members.items()):
            archive.write(source, name)
            identity[name] = sha(source)
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None and set(archive.namelist()) == set(identity)
        for name, expected in identity.items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == expected
    return identity


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖289证据封存')
    build = ROOT / 'artifacts/p16-direct-u10-build-v1'
    build_frozen = ROOT / 'artifacts/p16-direct-u10-frozen-v1/frozen.json'
    quality_dir = ROOT / 'artifacts/p16-direct-u10-quality-v1'
    quality_frozen = ROOT / 'artifacts/p16-direct-u10-quality-frozen-v1/frozen.json'
    rss_dir = ROOT / 'artifacts/p16-direct-u10-rss-v1'
    perf_dir = ROOT / 'artifacts/p16-direct-u10-perf-v1'
    frozen = read(quality_frozen)
    result = read(quality_dir / 'results.json')
    assert result['passed'] and result['performance_calls'] == 0 and result['frozen_sha256'] == sha(quality_frozen)
    configurations = {(n, k, t, p) for n in ('max_first', 'p99_first', 'old_best', '87_old_best')
                      for k, t in [('scalar', 1), ('avx2', 1), ('avx2', 4)] for p in ('inplace', 'to')}
    seen = set()
    for row in result['full_matrix']:
        key = (row['model'], row['kernel'], row['threads'], row['path'])
        assert key not in seen
        seen.add(key)
        spec = frozen['models']['old_best' if row['model'] == '87_old_best' else row['model']]
        assert row['mismatches'] == 0 and row['sha256'] == spec['oracle_sha256']
    assert seen == configurations
    photos = {(r['image'], r['model'], r['path']): r for r in result['photo_matrix']}
    assert len(photos) == len(result['photo_matrix']) == 600 and len({k[0] for k in photos}) == 100
    for (image, model, path), row in photos.items():
        assert row['mismatches'] == 0 and row['sha256'] == photos[image, model, 'inplace']['sha256'] == photos[image, model, 'to']['sha256']
    for name in ('max_first', 'p99_first'):
        row = result['288_layout_identity'][name]
        assert row['ids_equal'] and row['palette_equal'] and row['guard_zero']
        assert row['decoded_entries'] == (1 << 24) and row['capacity_saved_bytes'] == 12_582_912
        assert row['max_id'] < row['palette_size']
    assert result['288_layout_identity']['old_best'] == {'old8_table_equal': True, 'capacity_equal': True}
    assert result['contract']['short_pattern_backend_cases'] == 729 and result['contract']['diagnostic_rejections'] == 8
    assert all(x == 11 for x in result['outplace_rejections'].values())
    assert result['guard_contract']['guarded_cases'] == 88 and result['guard_contract']['compile_id_cases'] == 7
    assert [r['wide']['reason'] for r in result['synthetic']] == [1, 0, 3, 2]
    build_state = read(build_frozen)
    sources = {}
    for name, row in build_state['sources'].items():
        assert sha(ROOT / name) == row['sha256']
        snapshot = build_frozen.parent / 'sources' / name
        assert sha(snapshot) == row['sha256']
        sources[name] = ROOT / name
    deps = read(build / 'dependency-audit-v2.json')
    assert deps['passed'] and deps['frozen_sha256'] == sha(build_frozen) and deps['actual_repository_dependency_count'] == 35
    for name, expected in deps['actual_repository_dependencies_sha256'].items():
        assert name in sources and sha(sources[name]) == expected
    for path, expected in frozen['files_sha256'].items():
        assert sha(path) == expected
    names = ['scripts/check_direct_u10_native.py', 'scripts/audit_direct_u10_dependencies.py',
        'scripts/inspect_direct_u10_rss.py', 'scripts/run_direct_u10_perf.py', 'scripts/freeze_direct_u10_perf.py',
        'scripts/prepare_direct_u10_perf_audit.py', 'scripts/check_direct_u10_perf.py', 'scripts/archive_direct_u10.py',
        'experiments/p16-direct-u10-quality-plan-v1.md', 'experiments/p16-direct-u10-perf-v1.json']
    for name in names:
        sources[name] = ROOT / name
    perf_identity = read(perf_dir / 'identity.json')
    perf = read(perf_dir / 'results.json')
    perf_audit = read(perf_dir / 'independent-check.json')
    assert perf_audit['pass'] and perf_audit['raw_groups'] == 256 and perf_audit['AA_checks'] == 192
    assert perf_audit['comparisons'] == 624 and perf_audit['candidate_gates'] == perf['candidate_gates']
    plan = perf_identity['plan']
    assert perf_identity['plan_sha256'] == sha(ROOT / 'experiments/p16-direct-u10-perf-v1.json')
    for name, expected in plan['source_sha256'].items():
        assert sha(ROOT / name) == expected
        sources[name] = ROOT / name
    actual_sha = 0
    for worker in range(4):
        raw = read(perf_dir / ('worker' + str(worker)) / 'results.json')
        assert raw['worker'] == worker and len(raw['groups']) == 64 and len(raw['prepare']) == 8
        assert raw['plan_sha256'] == perf_identity['plan_sha256'] and raw['driver_sha256'] == perf_identity['driver_sha256']
        assert sorted(raw['allowed_logical_cpus']) == [0, 2, 4, 6] and raw['thread_pinning'] is False
        for row in raw['groups']:
            assert row['output_sha256'] == raw['expected_output_sha256'][row['role']] and row['source_readonly']
            assert row['main_cpu_before'] in (0, 2, 4, 6) and row['main_cpu_after'] in (0, 2, 4, 6)
            actual_sha += 1
        for row in raw['prepare']:
            assert row['output_sha256'] == raw['expected_output_sha256'][row['role']]
            actual_sha += 1
    rss = []
    for role in ('288', '289'):
        for model in ('max_first', 'p99_first', 'old_best'):
            row = read(rss_dir / (role + '-' + model + '.json'))
            assert row['model'] == model and row['revision'] == int(role)
            assert row['performance_calls'] == row['apply_calls'] == 0 and row['frozen_sha256'] == sha(quality_frozen)
            assert row['driver_sha256'] == sha(ROOT / 'scripts/inspect_direct_u10_rss.py')
            assert row['model_bytes'] == (result['capacity'][model]['model_bytes'] if role == '289' else
                result['288_layout_identity'][model].get('old_model_bytes', result['capacity'][model]['model_bytes']))
            rss.append(row)
    args.output.mkdir(parents=True)
    for name, path in [('quality.json', quality_dir / 'results.json'), ('quality-frozen.json', quality_frozen),
        ('build-frozen.json', build_frozen), ('perf.json', perf_dir / 'results.json'),
        ('perf-independent-check.json', perf_dir / 'independent-check.json'),
        ('plan.md', ROOT / 'experiments/p16-direct-u10-plan-v1.md'),
        ('quality-plan.md', ROOT / 'experiments/p16-direct-u10-quality-plan-v1.md'),
        ('perf-plan.json', ROOT / 'experiments/p16-direct-u10-perf-v1.json')]:
        shutil.copyfile(path, args.output / name)
    previous = ROOT / 'report/data/p16-direct-u16-ilp-native-20261024'
    assert read(previous / 'frozen.json')['models'] == frozen['models']
    shutil.copyfile(previous / 'models.zip', args.output / 'models.zip')
    zip_members = {}
    zip_members['source.zip'] = zip_files(args.output / 'source.zip', sources)
    raw_members = {}
    for directory in (quality_dir, rss_dir, perf_dir):
        for path in directory.rglob('*'):
            if path.is_file():
                raw_members[directory.name + '/' + path.relative_to(directory).as_posix()] = path
    for name in ('build-receipt.json', 'dependency-audit-v2.json', 'configure.log', 'build.log', 'contracts.log',
                 'CMakeCache.txt', 'libraries-Release.json', 'libjshc_direct_u10.dll', 'p16_direct_u10_contracts.exe'):
        raw_members['build/' + name] = build / name
    for path in build.rglob('*'):
        if path.is_file() and (path.suffix == '.su' or path.name.endswith('.obj.d')):
            raw_members['build/' + path.relative_to(build).as_posix()] = path
    for attempt in ('p16-direct-u10-generation-attempt-v1', 'p16-direct-u10-generation-attempt-v2'):
        for path in (ROOT / 'artifacts' / attempt).iterdir():
            if path.is_file():
                raw_members[attempt + '/' + path.name] = path
    for name in ('p16-direct-u10-generated-v1.json', 'p16-direct-u10-perf-audit-generated-v1.json'):
        raw_members[name] = ROOT / 'artifacts' / name
    zip_members['raw.zip'] = zip_files(args.output / 'raw.zip', raw_members)
    audit = {'pass': True, 'full_configs': 24, 'photo_configs': 600, 'short_groups': 729,
        'guard_cases': 88, 'prefrozen_cpp_dependencies': 35, 'prefrozen_build_sources': len(build_state['sources']),
        'formal_groups': 256, 'actual_formal_output_sha_checks': actual_sha, 'RSS_fresh_processes': len(rss),
        'AA_failures': len(perf_audit['AA_failures']), 'candidate_gates': perf['candidate_gates'],
        'performance_reruns': 0, 'discarded_workers': 0, 'zip_members_sha256': zip_members,
        'source_sha256': {name: sha(path) for name, path in sources.items()},
        'scope': '完整原件、两生成失败和早期不完整依赖收据均保留；静态额外归档源不冒充早于构建冻结。OS RSS与逻辑容量不同，AA无效不授档。'}
    write(args.output / 'independent-check.json', audit)
    write(args.output / 'manifest.json', {'files': {p.name: sha(p) for p in args.output.iterdir()},
        'source_sha256': audit['source_sha256'], 'scope': '质量/六fresh RSS/八角色正式性能的原字节封存，不切默认。'})
    print(json.dumps({'pass': True, 'source_members': len(sources), 'raw_members': len(raw_members),
        'AA_failures': audit['AA_failures'], 'candidate_gates': perf['candidate_gates']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
