"""离线封存逐TID控制的两次失败及成功质量；不构建、不执行模型或计时。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    'experiments/p16-omp-affinity-control-v1/control.cpp',
    'experiments/p16-omp-affinity-control-v1/plan.md',
    'experiments/p16-omp-affinity-control-v1/plan-v2.md',
    'scripts/build_omp_affinity_control.py', 'scripts/build_omp_affinity_control_v2.py',
    'scripts/check_omp_affinity_control.py', 'scripts/check_omp_affinity_control_v2.py',
    'scripts/archive_omp_affinity_control.py', 'scripts/audit_omp_affinity_control_git.py',
    'experiments/channel-runtime/channel_native.py',
]


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def zip_files(path, members):
    identities = {name: sha(source) for name, source in members.items()}
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, source in sorted(members.items()):
            archive.write(source, name)
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(identities) and set(archive.namelist()) == set(identities)
        for name, expected in identities.items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == expected
    return identities


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖线程控制证据封存')
    directories = {name: ROOT / ('artifacts/p16-omp-affinity-control-' + name)
                   for name in ('build-v1', 'build-v2', 'quality-v1', 'quality-v2')}
    closures = {}
    for name, directory in directories.items():
        frozen = read(directory / 'frozen.json')
        identities = frozen.get('sources_sha256', frozen.get('source_sha256'))
        assert identities
        for path, expected in identities.items():
            assert sha(path) == expected, path
            closures[str(Path(path).resolve().relative_to(ROOT).as_posix())] = Path(path)
        if name.startswith('build-'):
            assert sha(frozen['compiler']) == frozen['compiler_sha256']
            assert sha(frozen['libgomp']) == frozen['libgomp_sha256']
        else:
            assert sha(frozen['helper']) == frozen['helper_sha256']
            for path, expected in frozen['models_sha256'].items():
                assert sha(path) == expected
            assert sha(frozen['oracle']) == frozen['oracle_sha256']
            for role in frozen['target_libraries'].values():
                assert sha(role['path']) == role['sha256']
    failed_build = read(directories['build-v1'] / 'failure.json')
    failed_quality = read(directories['quality-v1'] / 'failure.json')
    assert failed_build['python_exit_code'] == 1 and not failed_build['compiler_exit_code_recorded']
    assert failed_quality['python_exit_code'] == 1 and not failed_quality['native_output_recorded']
    assert failed_quality['performance_calls'] == 0
    old_partial = read(directories['quality-v1'] / 'partial.json')
    assert len(old_partial) == 4 and all(row['return_code'] == 0 for row in old_partial)
    old_tids = [row['os_tid'] for row in old_partial[1]['team']]
    assert [row['os_tid'] for row in old_partial[2]['team']] == old_tids
    assert [row['os_tid'] for row in old_partial[3]['team']] != old_tids
    receipt = read(directories['build-v2'] / 'build-receipt.json')
    assert receipt['return_code'] == 0 and receipt['sources_unchanged']
    assert receipt['pe_exit_code'] == 0 and receipt['imports_libgomp'] and receipt['imports_thread_mask_api']
    assert receipt['performance_calls'] == 0
    assert sha(directories['build-v2'] / 'libp16_omp_affinity.dll') == receipt['library_sha256']
    quality = read(directories['quality-v2'] / 'results.json')
    assert quality['passed'] and quality['rejections'] == 6 and quality['performance_calls'] == 0
    assert quality['frozen_sha256'] == sha(directories['quality-v2'] / 'frozen.json')
    records = quality['records']
    assert records == read(directories['quality-v2'] / 'partial.json') and len(records) == 12
    tids = [row['os_tid'] for row in records[0]['team']]
    assert len(set(tids)) == 4
    assert [row['action'] for row in records] == [0, 1] + [0] * 8 + [2, 0]
    for index, record in enumerate(records):
        assert record['return_code'] == 0
        assert [row['os_tid'] for row in record['team']] == tids
        for tid, row in enumerate(record['team']):
            assert row['version'] == 1 and row['omp_tid'] == tid and row['team_size'] == 4
            assert row['query_before_ok'] and row['query_after_ok']
            assert row['group_before'] == row['group_after'] == 0
            if index in (0, 10, 11):
                assert row['mask_after'] == 0x55
            else:
                assert row['mask_after'] == (1 << (2 * tid)) and row['cpu_after'] == 2 * tid
            if index == 1:
                assert row['previous_mask'] == 0x55
    assert len(quality['outputs']) == 4
    assert {(row['revision'], row['repeat']) for row in quality['outputs']} == {(r, t) for r in (87, 94) for t in (0, 1)}
    assert all(row['mismatches'] == 0 for row in quality['outputs'])
    assert len({row['output_sha256'] for row in quality['outputs']}) == 1
    assert len(quality['actual_libgomp_paths']) == 1
    assert sha(quality['actual_libgomp_paths'][0]) == quality['libgomp_sha256']
    args.output.mkdir(parents=True)
    for label, directory, name in (
        ('build-failure.json', 'build-v1', 'failure.json'),
        ('quality-failure.json', 'quality-v1', 'failure.json'),
        ('build.json', 'build-v2', 'build-receipt.json'),
        ('quality.json', 'quality-v2', 'results.json'),
        ('quality-frozen.json', 'quality-v2', 'frozen.json'),
    ):
        shutil.copyfile(directories[directory] / name, args.output / label)
    for name in SOURCES:
        closures[name] = ROOT / name
    raw = {directory.name + '/' + path.relative_to(directory).as_posix(): path
           for directory in directories.values() for path in directory.rglob('*') if path.is_file()}
    zip_members = {
        'source.zip': zip_files(args.output / 'source.zip', closures),
        'raw.zip': zip_files(args.output / 'raw.zip', raw),
    }
    audit = {'passed': True, 'quality_team_snapshots': 12, 'quality_actual_outputs': 4,
             'argument_rejections': 6, 'preserved_failed_builds': 1, 'preserved_failed_quality_runs': 1,
             'performance_calls': 0, 'quality_reruns_by_archive': 0, 'zip_members_sha256': zip_members,
             'source_sha256': {name: sha(path) for name, path in closures.items()},
             'scope': '离线核记录和原字节；封存脚本不是构建前源。旧失败不改写，输入模型仅按旧冻结SHA核身份，不重复拟合或正式性能。'}
    write(args.output / 'independent-check.json', audit)
    write(args.output / 'manifest.json', {'files': {p.name: sha(p) for p in args.output.iterdir()},
          'source_sha256': audit['source_sha256'], 'scope': '基准控制工具质量证据，无性能授档或旧资格恢复。'})
    print(json.dumps({'passed': True, 'source_members': len(closures), 'raw_members': len(raw),
                      'team_snapshots': 12, 'outputs': 4, 'rejections': 6, 'performance_calls': 0}))


if __name__ == '__main__':
    main()
