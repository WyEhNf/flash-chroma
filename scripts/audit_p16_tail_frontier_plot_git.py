"""独立核图阶段Git对象、ZIP CRC/逐成员SHA及十二组源指标，无native。"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = 'report/data/p16-tail-frontier-plot-20261024/'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scope', choices=('index', 'head'))
    args = parser.parse_args()
    prefix = ':' if args.scope == 'index' else 'HEAD:'
    def blob(name):
        return subprocess.check_output(['git', '-c', 'gc.auto=0', '-c', 'maintenance.auto=false',
            'show', prefix + name], cwd=ROOT)
    whitelist = json.loads(blob(BASE + 'git-whitelist.json'))['files']
    for name, expected in whitelist.items():
        raw = blob(name)
        assert len(raw) == expected['bytes'] and sha(raw) == expected['sha256'], name
    manifest = json.loads(blob(BASE + 'manifest.json'))
    members = 0
    raw_map = {}
    for filename, spec in manifest['zip_files'].items():
        raw = blob(BASE + filename)
        assert sha(raw) == spec['sha256']
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            assert archive.testzip() is None and set(archive.namelist()) == set(spec['members'])
            for name, expected in spec['members'].items():
                value = archive.read(name)
                assert len(value) == expected['bytes'] and sha(value) == expected['sha256']
                raw_map[name] = value
                members += 1
    data = json.loads(blob(BASE + 'data.json'))
    assert data == json.loads(raw_map['artifacts/p16-tail-frontier-plot-v1/data.json'])
    assert data == json.loads(raw_map['artifacts/p16-tail-frontier-plot-v2/data.json'])
    current = json.loads(raw_map['report/data/p16-cinema-current-full-quality-20261024/results-v2.json'])
    max48 = json.loads(raw_map['report/data/p16-cinema-max48-pareto-quality-20261024/results.json'])
    for label, document, role in [('a399', current, 'a399'), ('373a', current, 'best'),
            ('max48', max48, 'candidate'), ('max41', current, 'candidate')]:
        for population in ('cube', 'photos'):
            for field in data['source_fields']:
                assert data['roles'][label][population][field] == document[population][role][field]
    for label in ('max_first', 'p99_first'):
        document = json.loads(raw_map['report/data/p16-cinema-second-nodes-v1/' + label + '-accuracy.json'])
        for population in ('cube', 'photos'):
            for field in data['source_fields']:
                assert data['roles'][label][population][field] == document[population][field]
    output = ROOT / ('artifacts/p16-tail-frontier-plot-' + args.scope + '-audit-v1.json')
    if output.exists():
        raise FileExistsError('不覆盖图阶段独立审计')
    result = dict(passed=True, scope=args.scope, files=len(whitelist) + 1,
        zip_members=members, exact_source_population_rows=12, native_calls=0, performance_samples=0)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
