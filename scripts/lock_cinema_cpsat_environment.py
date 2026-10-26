"""锁隔离CP-SAT环境和十份wheel原件，记录原环境版本而不修改它。"""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys


def sha(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--wheelhouse', type=Path, required=True)
    p.add_argument('--original-python', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖隔离依赖锁')
    packages = {d.metadata['Name']: d.version for d in importlib.metadata.distributions()}
    record_sha = {}
    for distribution in importlib.metadata.distributions():
        for f in distribution.files or []:
            if str(f).endswith('.dist-info/RECORD'):
                record_sha[distribution.metadata['Name']] = sha(distribution.locate_file(f))
    original = subprocess.check_output([str(args.original_python), '-c', 'import importlib.metadata as m,json;print(json.dumps({n:m.version(n) for n in ("numpy","numba","scipy")}))'], text=True)
    wheels = {p.name: sha(p) for p in args.wheelhouse.glob('*.whl')}
    if len(wheels) != 10 or packages.get('ortools') != '9.15.6755': raise ValueError('不是冻结十wheel隔离环境')
    value = {'python': sys.version, 'executable': sys.executable, 'python_executable_sha256': sha(sys.executable),
             'packages': packages, 'installed_record_sha256': record_sha, 'wheel_sha256': wheels,
             'original_environment_python': str(args.original_python), 'original_environment_versions': json.loads(original),
             'scope': '仅新venv离线安装全部指定wheel；未对原error-study环境执行pip安装，原版本只读记录。'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__': main()
