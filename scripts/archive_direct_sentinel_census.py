"""离线核固定top255普查并封存实际ID/cache原件，不再次prepare或计时。"""
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


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def zip_files(path, members):
    identities = {name: sha(source) for name, source in members.items()}
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, source in sorted(members.items()):
            archive.write(source, name)
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None and len(archive.namelist()) == len(identities)
        assert set(archive.namelist()) == set(identities)
        for name, expected in identities.items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == expected
    return identities


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖哨兵普查封存')
    frozen_path = ROOT / 'artifacts/p16-sentinel-census-frozen-v1/frozen.json'
    raw_dir = ROOT / 'artifacts/p16-sentinel-census-v1'
    frozen, result = read(frozen_path), read(raw_dir / 'results.json')
    assert result['passed'] and result['frozen_sha256'] == sha(frozen_path)
    assert result['performance_calls'] == result['apply_calls'] == result['gold_or_photo_reads'] == 0
    assert set(result['models']) == {'max_first', 'p99_first'}
    sources = {}
    models = {}
    for name, expected in frozen['source_sha256'].items():
        assert sha(ROOT / name) == expected
        sources[name] = ROOT / name
    for spec in frozen['models'].values():
        for path, expected in spec['input_sha256'].items():
            assert sha(path) == expected
            models['models/' + expected + Path(path).suffix] = Path(path)
    for name, row in result['models'].items():
        assert read(raw_dir / name / 'results.json') == row
        for filename, expected in row['files_sha256'].items():
            assert sha(raw_dir / name / filename) == expected
        assert row['independent_python_integer_check'] and row['performance_calls'] == row['apply_calls'] == 0
        assert sum(row['domain_counts']) == 1 << 24
        assert sum(row['cache_counts']) == row['cache_geometry']['entries']
        for ranking in row['rankings'].values():
            assert len(ranking['palette_ids']) == len(set(ranking['palette_ids'])) == 255
            assert ranking['hits'] + ranking['misses'] == 1 << 24
            for field in ('physical_miss_lanes_histogram', 'canonical_miss_lanes_histogram'):
                histogram = ranking[field]
                assert len(histogram) == 9 and sum(histogram) == 1 << 21
                assert sum(i * n for i, n in enumerate(histogram)) == ranking['misses']
    assert sha(frozen['library']) == frozen['library_sha256']
    assert sha(frozen['metadata_source']) == frozen['metadata_sha256']
    for name in ('scripts/archive_direct_sentinel_census.py', 'scripts/audit_direct_sentinel_census_git.py'):
        sources[name] = ROOT / name
    args.output.mkdir(parents=True)
    shutil.copyfile(frozen_path, args.output / 'frozen.json')
    shutil.copyfile(raw_dir / 'results.json', args.output / 'results.json')
    shutil.copyfile(ROOT / 'experiments/p16-sentinel-census-plan-v1.json', args.output / 'plan.json')
    raw = {path.relative_to(raw_dir).as_posix(): path for path in raw_dir.rglob('*') if path.is_file()}
    raw['baseline-288-frozen.json'] = Path(frozen['metadata_source'])
    zip_members = {'raw.zip': zip_files(args.output / 'raw.zip', raw),
                   'source.zip': zip_files(args.output / 'source.zip', sources),
                   'models.zip': zip_files(args.output / 'models.zip', models)}
    audit = {'passed': True, 'frozen_sha256': sha(frozen_path), 'two_fixed_models': True,
             'rankings_per_model': 2, 'independent_integer_census_passed': True,
             'performance_calls': 0, 'prepare_reruns_by_archive': 0,
             'source_sha256': {name: sha(path) for name, path in sources.items()},
             'zip_members_sha256': zip_members,
             'scope': '普查数据的离线完整性；原288构建证据沿既有u16-ilp阶段，不把本封存脚本冒充执行前冻结。'}
    save(args.output / 'independent-check.json', audit)
    save(args.output / 'manifest.json', {'files': {p.name: sha(p) for p in args.output.iterdir()},
         'source_sha256': audit['source_sha256'], 'scope': '固定top255整域/包率必要普查；不是native哨兵后端、吞吐资格或官方许可。'})
    print(json.dumps({'passed': True, 'source_members': len(sources), 'raw_members': len(raw), 'model_members': len(models), 'performance_calls': 0}))


if __name__ == '__main__':
    main()
