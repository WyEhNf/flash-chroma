"""逐blob核本阶段显式白名单与ZIP成员，区分index与HEAD；不改Git或重跑数值。"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DATA = 'report/data/p16-direct-cache2-20261024'


def git_blob(mode, name):
    ref = ':' + name if mode == 'index' else 'HEAD:' + name
    return subprocess.run(['git', '-c', 'gc.auto=0', 'show', ref], cwd=ROOT, check=True, capture_output=True).stdout


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['index', 'HEAD'])
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError('不覆盖Git核验')
    paths = json.loads((ROOT / DATA / 'git-whitelist.json').read_text(encoding='utf-8'))['paths']
    assert len(paths) == len(set(paths)) and 'AGENTS.md' not in paths
    if a.mode == 'index':
        staged = subprocess.run(['git', 'diff', '--cached', '--name-only', '-z'], cwd=ROOT, check=True, capture_output=True).stdout.decode('utf-8').split('\0')
        assert set(paths) == set(filter(None, staged))
    blobs = {}
    for name in paths:
        raw = git_blob(a.mode, name)
        assert raw == (ROOT / name).read_bytes(), name
        blobs[name] = hashlib.sha256(raw).hexdigest()
    check = json.loads(git_blob(a.mode, DATA + '/independent-check.json'))
    members = 0
    for name, expected in check['zip_members_sha256'].items():
        with zipfile.ZipFile(io.BytesIO(git_blob(a.mode, DATA + '/' + name))) as archive:
            assert archive.testzip() is None and set(archive.namelist()) == set(expected)
            for member, wanted in expected.items():
                assert hashlib.sha256(archive.read(member)).hexdigest() == wanted, member
                members += 1
    result = {'passed': True, 'mode': a.mode, 'blob_sha256': blobs, 'zip_members': members,
              'native_calls': 0, 'performance_calls': 0}
    a.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'passed': True, 'mode': a.mode, 'blobs': len(blobs), 'zip_members': members}, ensure_ascii=False))


if __name__ == '__main__':
    main()
