"""静态封存固定κ=2的612色局部负例，保留两max点整数平台。"""
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
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖κ=2局部负例')
    args.output.mkdir(parents=True)
    path = ROOT/'artifacts/velvia-bubble-probe-v1.json'
    measured = json.loads(path.read_text(encoding='utf-8'))
    if measured['source_sha256']['scripts/probe_velvia_bubble.py'] != digest(ROOT/'scripts/probe_velvia_bubble.py'):
        raise ValueError('冻结探针源码发生改变')
    shutil.copyfile(path, args.output/'results.json')
    sources = ['scripts/'+name for name in ('probe_velvia_bubble.py', 'archive_velvia_bubble_probe.py', 'run_channel_tail_nodes.py',
        'accept_channel_tail_nodes.py', 'accept_channel_coordinates.py')]+['python/lutlab/'+name for name in
        ('channel_coordinates.py', 'io.py', 'study_provenance.py')]
    with zipfile.ZipFile(args.output/'source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in sources:
            archive.write(ROOT/name, name)
    manifest = {'source_sha256': {name: digest(ROOT/name) for name in sources}, 'files': {p.name: digest(p) for p in args.output.iterdir()},
        'purpose': __doc__, 'numeric_or_performance_calls_during_archive': 0,
        'scope': '只检查612色必要条件，κ=2整数平台失败；没有全域选择/拟合/面邻接终验/原生/性能。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'files': len(manifest['files']), 'new_default': False}), flush=True)


if __name__ == '__main__':
    main()
