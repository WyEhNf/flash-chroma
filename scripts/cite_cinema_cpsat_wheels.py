"""读取官方PyPI元数据，核十个已下载wheel SHA并保存公开直接下载链接。"""
from __future__ import annotations
import argparse
import email
import hashlib
import json
from pathlib import Path
import urllib.parse
import urllib.request
import zipfile


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--wheelhouse', type=Path, required=True)
    p.add_argument('--environment-lock', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖官方wheel引用')
    lock = json.loads(args.environment_lock.read_text(encoding='utf-8')); result = []
    for filename, expected in sorted(lock['wheel_sha256'].items()):
        path = args.wheelhouse/filename
        with path.open('rb') as stream: actual = hashlib.file_digest(stream, 'sha256').hexdigest()
        if actual != expected: raise ValueError('下载wheel字节已变')
        with zipfile.ZipFile(path) as archive:
            names = [n for n in archive.namelist() if n.endswith('.dist-info/METADATA')]
            if len(names) != 1: raise ValueError('wheel元数据不唯一')
            metadata = email.message_from_bytes(archive.read(names[0]))
        name, version = metadata['Name'], metadata['Version']
        api = 'https://pypi.org/pypi/'+urllib.parse.quote(name)+'/'+urllib.parse.quote(version)+'/json'
        with urllib.request.urlopen(api, timeout=20) as response: value = json.load(response)
        files = [f for f in value['urls'] if f['filename'] == filename]
        if len(files) != 1 or files[0]['digests']['sha256'] != actual: raise ValueError('官方PyPI wheel SHA不同')
        result.append({'package': name, 'version': version, 'filename': filename, 'sha256': actual,
                       'metadata_url': api, 'download_url': files[0]['url'], 'size_bytes': path.stat().st_size})
    if len(result) != 10: raise ValueError('不是冻结十wheel')
    args.output.write_text(json.dumps({'pass': True, 'wheels': result,
        'scope': '全部官方PyPI元数据SHA与本次实际wheel匹配，只归档公开链接和锁，不把venv或大wheel放Git。'}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'pass': True, 'official_wheels': len(result)}), flush=True)


if __name__ == '__main__': main()
