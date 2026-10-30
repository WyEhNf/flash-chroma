"""静态保存固定κ3两cell完整质量验收及全部局部跳变代价。"""
from __future__ import annotations
import argparse
import csv
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
    if args.output.exists(): raise ValueError('不覆盖κ3完整验收归档')
    args.output.mkdir(parents=True)
    measured = ROOT/'artifacts/velvia-bubble-accept-v1'
    run = json.loads((measured/'run.json').read_text(encoding='utf-8'))
    for name, sha in run['source_sha256'].items():
        if digest(ROOT/name) != sha: raise ValueError('验收后改过冻结数值源码')
    for name in ('run.json', 'cube.json', 'results.json', 'faces.json', 'adjacency.json'):
        shutil.copyfile(measured/name, args.output/name)
    model_path = Path(run['input_paths']['model'])
    if digest(model_path) != run['input_sha256']['model']: raise ValueError('原3e5模型变更')
    shutil.copyfile(model_path, args.output/'baseline-model.npz')
    shutil.copyfile(ROOT/'experiments/velvia-bubble-accept-v1.json', args.output/'candidate.json')
    result = json.loads((measured/'results.json').read_text(encoding='utf-8'))
    if digest(measured/'candidate.rgb') != result['sha256']: raise ValueError('50MB完整流SHA不符')
    baseline = {r['image']: r for r in result['baseline_photos']['per_image']}
    ratios, regressions = [], []
    for row in result['photos']['per_image']:
        for metric in ('mean', 'rms', 'p99', 'max', 'cvar_1pct'):
            old, new = baseline[row['image']][metric], row[metric]
            ratio = old/new if new else 1.
            ratios.append([row['image'], metric, old, new, ratio])
            if new > old+1e-12: regressions.append([row['image'], metric, old, new, new-old, ratio])
    for name, header, rows in [('photo-ratios.csv', ['图像', '指标', '旧值', '新值', '旧误差除以新误差'], ratios),
        ('photo-regressions.csv', ['图像', '指标', '旧值', '新值', '差值', '旧误差除以新误差'], regressions)]:
        with (args.output/name).open('w', encoding='utf-8-sig', newline='') as stream:
            writer = csv.writer(stream); writer.writerow(header); writer.writerows(rows)
    sources = ['scripts/'+n for n in ('accept_velvia_bubble.py', 'archive_velvia_bubble_accept.py', 'probe_velvia_bubble.py',
        'verify_channel_coordinates.py', 'run_channel_tail_nodes.py', 'accept_channel_tail_nodes.py', 'accept_channel_coordinates.py')]
    sources += ['python/lutlab/'+n for n in ('bubble_tetra.py', 'channel_coordinates.py', 'io.py', 'study_provenance.py')]
    sources += ['experiments/velvia-bubble-accept-v1.json']
    with zipfile.ZipFile(args.output/'source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in sources: archive.write(ROOT/name, name)
    manifest = {'source_sha256': {n: digest(ROOT/n) for n in sources}, 'files': {p.name: digest(p) for p in args.output.iterdir()},
        'candidate_stream_sha256': result['sha256'], 'numeric_or_performance_calls_during_archive': 0,
        'scope': '固定κ3两cell原3e5模型；16M/100图/全部真实共享面/全部RGB8邻接已验。相邻点跳变有局部代价；新表示非stock SLUT，无native/性能/容量结论。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'files': len(manifest['files']), 'photo_metric_regressions': len(regressions), 'minimum_photo_accuracy_retention': min(r[-1] for r in ratios),
        'quality_gate_passed': result['quality_gate_passed'], 'new_default': False}), flush=True)


if __name__ == '__main__': main()
