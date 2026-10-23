"""静态归档自由cell方向的精度收益及不连续性，保留全部逐图退化。"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖自由场归档')
    args.output.mkdir(parents=True)
    probe = ROOT/'artifacts/velvia-cell-feasibility-v1'
    accept = ROOT/'artifacts/velvia-cell-accept-v1'
    for target, source in [('probe-run.json', probe/'run.json'), ('probe-results.json', probe/'results.json'),
        ('cell-statistics.npz', probe/'cell-statistics.npz'), ('run.json', accept/'run.json'), ('results.json', accept/'results.json'),
        ('exact-faces.json', accept/'exact-faces.json'), ('rgb8-boundaries.json', accept/'rgb8-boundaries.json'),
        ('cell-orientation.bin', accept/'cell-orientation.bin'),
        ('baseline-model.zip', ROOT/'report/data/velvia-body-diagonals-20261024/baseline-model.zip')]:
        shutil.copyfile(source, args.output/target)
    result = read(accept/'results.json')
    baseline = {r['image']: r for r in result['baseline_photos']['per_image']}
    ratios, regressions = [], []
    for row in result['photos']['per_image']:
        for metric in ('mean', 'rms', 'p99', 'max', 'cvar_1pct'):
            old, new = baseline[row['image']][metric], row[metric]
            ratio = old/new if new else 1.
            ratios.append([row['image'], metric, old, new, ratio])
            if new > old+1e-12:
                regressions.append([row['image'], metric, old, new, new-old, ratio])
    for name, header, rows in [('error-ratios.csv', ['图像', '指标', '旧值', '新值', '旧误差除以新误差'], ratios),
        ('regressions.csv', ['图像', '指标', '旧值', '新值', '差值', '旧误差除以新误差'], regressions)]:
        with (args.output/name).open('w', encoding='utf-8-sig', newline='') as stream:
            writer = csv.writer(stream); writer.writerow(header); writer.writerows(rows)
    sources = ['scripts/'+n for n in ('probe_velvia_cell_diagonals.py', 'accept_velvia_cell_diagonals.py',
        'archive_velvia_cell_diagonals.py', 'study_velvia_body_diagonals.py', 'run_channel_tail_nodes.py',
        'accept_channel_tail_nodes.py', 'accept_channel_coordinates.py')]+['python/lutlab/'+n for n in
        ('channel_coordinates.py', 'io.py', 'study_provenance.py')]
    for name in ('probe_velvia_cell_diagonals.py', 'accept_velvia_cell_diagonals.py'):
        record = read(probe/'run.json' if name.startswith('probe') else accept/'run.json')
        if record['source_sha256']['scripts/'+name] != digest(ROOT/'scripts'/name):
            raise ValueError('测量源码已改变')
    with zipfile.ZipFile(args.output/'source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in sources:
            archive.write(ROOT/name, name)
    manifest = {'source_sha256': {name: digest(ROOT/name) for name in sources},
        'files': {p.name: digest(p) for p in args.output.iterdir()},
        'candidate_stream_sha256': result['sha256'], 'numeric_or_performance_calls_during_archive': 0,
        'scope': '聚合准确性通过但面不连续及逐图退化明确存在；不是可直接替换的生产模型，无原生/速度/额外运行内存验收。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'files': len(manifest['files']), 'regressions': len(regressions),
        'minimum_old_error_over_new_error': min(r[-1] for r in ratios), 'new_default': False}), flush=True)


if __name__ == '__main__':
    main()
