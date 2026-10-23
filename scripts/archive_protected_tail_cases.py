"""归档普通四SLUT与Velvia单级的同支撑方法边界；不重新映射像素。"""
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
    parser.add_argument('--cache-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖跨案例证据')
    args.output.mkdir(parents=True)
    regressions, summary, paths = [], {}, {}
    for case, name in [('cinema_shared', 'cinema-shared'), ('velvia', 'velvia')]:
        fit = ROOT/f'artifacts/protected-tail-{name}-v1'
        accept = ROOT/f'artifacts/protected-tail-{name}-accept-v1/results.json'
        result = read(accept)
        value = result['variants']['candidate']
        if not value['passed_aggregate'] or len(set(value['sha256'][n] for n in ('oracle', 'scalar', 'avx2'))) != 1:
            raise ValueError('聚合或实际原生恒等未通过')
        folder = args.output/case; folder.mkdir()
        for target, source in [('fit-run.json', fit/'run.json'), ('fit-summary.json', fit/'summary.json'), ('results.json', accept)]:
            shutil.copyfile(source, folder/target)
        old_rows = {r['image']: r for r in result['baseline_photos']['per_image']}
        for row in value['photos']['per_image']:
            for metric in ('mean', 'rms', 'p99', 'max', 'cvar_1pct'):
                old = old_rows[row['image']][metric]
                if row[metric] > old+1e-12:
                    regressions.append([case, row['image'], metric, old, row[metric], row[metric]-old])
        strict_tail = any(value[g][k] < result['baseline' if g == 'cube' else 'baseline_photos'][k]-1e-12
                          for g in ('cube', 'photos') for k in ('p99', 'max'))
        summary[case] = {'baseline_cube': result['baseline'], 'candidate_cube': value['cube'],
            'baseline_photos': {k: result['baseline_photos'][k] for k in ('mean', 'rms', 'p99', 'max', 'cvar_1pct')},
            'candidate_photos': {k: value['photos'][k] for k in ('mean', 'rms', 'p99', 'max', 'cvar_1pct')},
            'per_image_changes': value['photos']['changes'], 'model_accounting_bytes_87': value['model_accounting_bytes'],
            'sha256': value['sha256'], 'strict_p99_or_max_improvement': strict_tail,
            'sidecar_bytes': read(fit/'summary.json')['sidecar_bytes'], 'new_default': False, 'speed_gate_passed': None}
        with zipfile.ZipFile(folder/'models.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
            for p in sorted((fit/'candidate').iterdir()):
                archive.write(p, p.name)
            if case == 'cinema_shared':
                for k in (2, 3, 4):
                    path = args.cache_root/'artifacts/cinema-envelope-v1/stage4_sweep004'/f'selected-stage{k}.slut'
                    archive.write(path, path.name)
        paths[case] = fit
    with (args.output/'regressions.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.writer(stream); writer.writerow(['案例', '图像', '指标', '旧值', '新值', '差值']); writer.writerows(regressions)
    with zipfile.ZipFile(args.output/'fit-evidence.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for case, path in paths.items():
            archive.write(path/'progress.json', case+'/progress.json')
    (args.output/'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    sources = ['scripts/'+n for n in ('run_protected_tail_case.py', 'accept_channel_tail_nodes.py', 'archive_protected_tail_cases.py',
        'verify_channel_coordinates.py', 'accept_channel_coordinates.py')]+['python/lutlab/'+n for n in
        ('channel_tail_nodes.py', 'channel_coordinates.py', 'channel_joint_nodes.py', 'channel_global_nodes.py', 'io.py', 'interp.py')]
    with zipfile.ZipFile(args.output/'source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in sources:
            archive.write(ROOT/name, name)
    manifest = {'source_sha256': {n: digest(ROOT/n) for n in sources},
        'files': {p.relative_to(args.output).as_posix(): digest(p) for p in args.output.rglob('*') if p.is_file()},
        'purpose': __doc__, 'numeric_or_performance_calls': 0, 'new_default': False,
        'scope': '普通共享轴无侧表四SLUT与Velvia分输出侧表单级分别列示；已全域/百图/原生准确性，但没有速度底线结论。Velvia没有p99/max实质改善。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
