"""逐Git blob核对本轮证据manifest，并独立核对源码ZIP的测量字节。"""
from __future__ import annotations
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
    parser.add_argument('--git-ref', default='HEAD')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    folders = ['channel-tail-nodes-20261023', 'channel-tail-extensions-20261024', 'cinema-last-stage-20261024']
    checks, failures = [], []
    for folder in folders:
        relative = 'report/data/'+folder
        manifest = json.loads(subprocess.check_output(['git', 'show', args.git_ref+':'+relative+'/manifest.json'], cwd=ROOT))
        for name, expected in manifest['files'].items():
            path = relative+'/'+name
            blob = subprocess.check_output(['git', 'show', args.git_ref+':'+path], cwd=ROOT)
            result = {'kind': 'git_blob', 'path': path, 'expected_sha256': expected, 'actual_sha256': digest(blob)}
            result['pass'] = result['expected_sha256'] == result['actual_sha256']
            checks.append(result)
            if not result['pass']:
                failures.append(result)
        source = subprocess.check_output(['git', 'show', args.git_ref+':'+relative+'/source.zip'], cwd=ROOT)
        with zipfile.ZipFile(io.BytesIO(source)) as archive:
            for name, expected in manifest['source_sha256'].items():
                actual = digest(archive.read(name))
                result = {'kind': 'measured_source_zip', 'path': relative+'/source.zip!/'+name,
                          'expected_sha256': expected, 'actual_sha256': actual, 'pass': actual == expected}
                checks.append(result)
                if not result['pass']:
                    failures.append(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    record = {'pass': not failures, 'git_ref': args.git_ref, 'checked_commit': subprocess.check_output(
        ['git', 'rev-parse', args.git_ref], cwd=ROOT, text=True).strip(), 'checks': checks, 'failures': failures,
        'scope': 'raw证据按实际Git blob字节验SHA；源码SHA按该阶段冻结source.zip字节核，不要求后续修改过的HEAD源码等于历史快照。没有重新运行数值或计时。'}
    args.output.write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'pass': record['pass'], 'checks': len(checks), 'failures': failures}, ensure_ascii=False), flush=True)
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
