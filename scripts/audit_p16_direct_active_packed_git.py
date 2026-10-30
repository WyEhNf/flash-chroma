"""独立核离线9位阶段的Git原字节与全部ZIP；无模型/计时调用。"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = 'report/data/p16-direct-active-packed-20261024/'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scope', choices=('index', 'head'))
    args = parser.parse_args()
    output = ROOT / ('artifacts/p16-direct-active-packed-' + args.scope + '-audit-v1.json')
    if output.exists():
        raise FileExistsError('Git核原件不可覆盖')
    prefix = ':' if args.scope == 'index' else 'HEAD:'
    def blob(name):
        return subprocess.check_output(['git', '-c', 'gc.auto=0', '-c', 'maintenance.auto=false', 'show', prefix + name], cwd=ROOT)
    whitelist = json.loads(blob(BASE + 'git-whitelist.json'))['files']
    for name, expected in whitelist.items():
        raw = blob(name)
        assert len(raw) == expected['bytes'] and sha(raw) == expected['sha256'], name
    manifest = json.loads(blob(BASE + 'manifest.json'))
    all_raw = {}
    for filename, spec in manifest['zip_files'].items():
        raw = blob(BASE + filename)
        assert sha(raw) == spec['sha256']
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            assert archive.testzip() is None and set(archive.namelist()) == set(spec['members'])
            assert len(archive.namelist()) == len(spec['members'])
            for name, expected in spec['members'].items():
                value = archive.read(name)
                assert len(value) == expected['bytes'] and sha(value) == expected['sha256']
                if name in all_raw:
                    assert all_raw[name] == value
                all_raw[name] = value
    for name in ('frozen.json', 'results.json', 'independent.json'):
        assert blob(BASE + name) == all_raw['artifacts/p16-direct-active-packed-v2/' + name]
    frozen = json.loads(blob(BASE + 'frozen.json'))
    result = json.loads(blob(BASE + 'results.json'))
    independent = json.loads(blob(BASE + 'independent.json'))
    assert result['passed'] and independent['passed']
    for name, expected in result['artifacts'].items():
        raw = all_raw['artifacts/p16-direct-active-packed-v2/' + name]
        assert len(raw) == expected['bytes'] and sha(raw) == expected['sha256'], name
    assert independent['script_sha256'] == sha(all_raw['scripts/audit_direct_active_packed.py'])
    assert independent['frozen_sha256'] == sha(blob(BASE + 'frozen.json'))
    assert independent['results_sha256'] == sha(blob(BASE + 'results.json'))
    source_map = frozen['sources_sha256'] if 'sources_sha256' in frozen else frozen['source_sha256']
    for name, expected in source_map.items():
        assert sha(all_raw[name]) == expected
    assert sha(blob(BASE + 'frozen.json')) == 'ba77cb94813346b1906f696c30637933be7b62d738221331d725af34142268d4'
    assert sha(blob(BASE + 'results.json')) == '728165235480fb336ef39ec4ce6ffb801c33d59a3c19676c62aa063ba249dc7e'
    value = dict(passed=True, scope=args.scope, files=len(whitelist) + 1,
        zip_members=sum(len(row['members']) for row in manifest['zip_files'].values()),
        frozen_sources=len(source_map), native_calls=0, performance_samples=0,
        scope_limit='Git/ZIP原字节核；完整16M语义核来自已封存独立审计，不在此重复执行。')
    output.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(value, ensure_ascii=False))


if __name__ == '__main__':
    main()
