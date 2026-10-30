"""静态保存四方向体对角线的完整失败证据，不重新计算像素或计时。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖四方向精简证据')
    args.output.mkdir(parents=True)
    measured = ROOT/'artifacts/velvia-body-diagonals-v1'
    manifest = json.loads((measured/'manifest.json').read_text(encoding='utf-8'))
    for name, expected in manifest['files'].items():
        if digest(measured/name) != expected:
            raise ValueError('测量文件已改变')
        shutil.copyfile(measured/name, args.output/name)
    with zipfile.ZipFile(args.output/'baseline-model.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        path = args.cache_root/'artifacts/velvia-channel-coordinates-v1/channel-coordinates.npz'
        if digest(path) != '3e5f8fd94e8dc9b97dbfea2823896b8dffb6e014b5e6056ab5c10b58a69af3d0':
            raise ValueError('基线模型不是冻结版本')
        archive.write(path, 'channel-coordinates.npz')
    shutil.copyfile(Path(__file__), args.output/'archive-source.py')
    manifest['files'] = {p.name: digest(p) for p in args.output.iterdir() if p.is_file()}
    manifest['purpose'] = __doc__
    manifest['numeric_or_performance_calls_during_archive'] = 0
    (args.output/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'archived_files': len(manifest['files']), 'new_default': False}), flush=True)


if __name__ == '__main__':
    main()
