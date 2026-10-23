"""静态归档连续stripe方向场两起点固定预算失败，不重跑几何或选择。"""
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
        raise ValueError('不覆盖stripe负结果证据')
    args.output.mkdir(parents=True)
    measured = ROOT/'artifacts/velvia-stripe-diagonals-v1'
    for name in ('run.json', 'face-contract.json', 'single-slabs.json', 'results.json'):
        shutil.copyfile(measured/name, args.output/name)
    run = json.loads((measured/'run.json').read_text(encoding='utf-8'))
    if run['source_sha256']['scripts/study_velvia_stripe_diagonals.py'] != digest(ROOT/'scripts/study_velvia_stripe_diagonals.py'):
        raise ValueError('冻结源码发生改变')
    stats = ROOT/'report/data/velvia-cell-diagonals-20261024/cell-statistics.npz'
    manifest = {'reused_cell_statistics': {'path': 'report/data/velvia-cell-diagonals-20261024/cell-statistics.npz', 'sha256': digest(stats)},
        'purpose': __doc__, 'numeric_or_performance_calls_during_archive': 0,
        'scope': '面相容代数证明和17/33有限采样通过；两起点各两扫均值预算失败，不是不可行性证明；没有全域新流/照片/原生/性能候选。'}
    if digest(stats) != next(iter(run['input_sha256'].values())):
        raise ValueError('复用cell统计不是原冻结输入')
    sources = ['scripts/'+n for n in ('study_velvia_stripe_diagonals.py', 'archive_velvia_stripe_diagonals.py',
        'accept_velvia_cell_diagonals.py', 'study_velvia_body_diagonals.py', 'run_channel_tail_nodes.py',
        'accept_channel_tail_nodes.py', 'accept_channel_coordinates.py')]+['python/lutlab/'+n for n in
        ('channel_coordinates.py', 'io.py', 'study_provenance.py')]
    with zipfile.ZipFile(args.output/'source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in sources:
            archive.write(ROOT/name, name)
    manifest['source_sha256'] = {name: digest(ROOT/name) for name in sources}
    manifest['files'] = {p.name: digest(p) for p in args.output.iterdir()}
    (args.output/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'files': len(manifest['files']), 'new_default': False}), flush=True)


if __name__ == '__main__':
    main()
