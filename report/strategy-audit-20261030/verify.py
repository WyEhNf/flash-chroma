"""仅核验静态审计文件、源码身份和文档链接；不执行数值或性能测试。"""

from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
from urllib.parse import unquote


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    manifest = json.loads((HERE / 'manifest.json').read_text(encoding='utf-8'))
    failures = []
    for item in manifest['files']:
        path = ROOT / item['path']
        if not path.is_file() or digest(path.read_bytes()) != item['sha256']:
            failures.append('文件身份不匹配：' + item['path'])

    base = manifest['base_commit']
    for item in manifest['source_identity']:
        content = subprocess.run(
            ['git', 'show', f"{base}:{item['path']}"], cwd=ROOT,
            capture_output=True, check=True).stdout
        if digest(content) != item['sha256']:
            failures.append('基线源码身份不匹配：' + item['path'])
        if digest((ROOT / item['path']).read_bytes()) != item['sha256']:
            failures.append('当前源码与审计基线不同：' + item['path'])

    link_count = 0
    for item in manifest['files']:
        path = ROOT / item['path']
        if path.suffix != '.md':
            continue
        for target in re.findall(r'\]\(([^)\n]+)\)', path.read_text(encoding='utf-8')):
            if target.startswith(('https://', 'http://', '#')):
                continue
            name = unquote(target.split('#', 1)[0]).strip('<>')
            if not (path.parent / name).resolve().exists():
                failures.append(f'链接缺失：{item["path"]} -> {target}')
            link_count += 1

    result = {
        'scope': '静态文件/源码身份与相对Markdown链接，无数值/性能执行',
        'base_commit': base,
        'files_checked': len(manifest['files']),
        'source_files_checked': len(manifest['source_identity']),
        'relative_links_checked': link_count,
        'passed': not failures,
        'failures': failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == '__main__':
    sys.exit(main())
