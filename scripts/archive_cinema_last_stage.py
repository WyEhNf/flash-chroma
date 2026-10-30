"""只读复算逐图代价和试验严格max门槛，并归档冻结末级候选。"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import shutil
import zipfile
ROOT = Path(__file__).resolve().parents[1]
METRICS = ('mean', 'rms', 'p99', 'max', 'cvar_1pct')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--performance-root', type=Path)
    parser.add_argument('--performance-commit')
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖终验归档')
    args.output.mkdir(parents=True)
    accept = ROOT/'artifacts/cinema-last-stage-accept-v1/results.json'
    fit = ROOT/'artifacts/cinema-last-stage-v2'
    prior_path = args.cache_root/'artifacts/cinema-current-anchor-accept-v1/results.json'
    result, prior = read(accept), read(prior_path)
    candidate = result['variants']['candidate']
    if not candidate['passed_aggregate'] or candidate['cube']['max'] >= result['baseline']['max']:
        raise ValueError('聚合或严格max门禁未过')
    if len(set(candidate['sha256'][n] for n in ('oracle', 'scalar', 'avx2'))) != 1:
        raise ValueError('完整原生/整数流身份不同')
    rows = {'a399': prior['photos']['per_image'], 'severe_first': result['baseline_photos']['per_image'],
            'last_stage': candidate['photos']['per_image']}
    ids = [r['image'] for r in rows['last_stage']]
    if any([r['image'] for r in value] != ids for value in rows.values()):
        raise ValueError('逐图次序或覆盖不同')
    comparisons, regressions = {}, []
    for baseline in ('a399', 'severe_first'):
        changes = {}
        for metric in METRICS:
            counts = {'better': 0, 'equal': 0, 'worse': 0}
            for old, new in zip(rows[baseline], rows['last_stage']):
                delta = new[metric]-old[metric]
                key = 'better' if delta < -1e-12 else 'worse' if delta > 1e-12 else 'equal'
                counts[key] += 1
                if key == 'worse':
                    regressions.append([baseline, new['image'], metric, old[metric], new[metric], delta])
            changes[metric] = counts
        comparisons[baseline] = changes
    thresholds = []
    for threshold in (4., 5., 6., 7., 7.5, 7.7, 8., 8.2):
        thresholds.append({'experimental_T': threshold,
            **{name: sum(r['max'] < threshold for r in value) for name, value in rows.items()}})
    groups = []
    for label, spec in result['partition'].items():
        if label == 'audit_ids':
            selected, label = set(spec), 'audit'
        elif isinstance(spec, dict) and 'images' in spec:
            selected = {r['id'] for r in spec['images']}
        else:
            continue
        for name, value in rows.items():
            members = [r for r in value if r['image'] in selected]
            if len(members) != len(selected):
                raise ValueError('分组图像不齐')
            groups.append({'group': label, 'variant': name, 'n_images': len(members),
                'mean': sum(r['mean'] for r in members)/len(members),
                'rms': math.sqrt(sum(r['rms']**2 for r in members)/len(members)),
                'worst_image_p99': max(r['p99'] for r in members), 'max': max(r['max'] for r in members)})
    save(args.output/'comparisons.json', {'per_image_changes': comparisons, 'strict_max_T_pass_counts': thresholds,
        'groups': groups, 'threshold_scope': '非官方试验T，逐图严格max<T，等于T不计通过。仅同100历史图。'})
    with (args.output/'regressions.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.writer(stream); writer.writerow(['对照', '图像', '指标', '旧值', '新值', '差值']); writer.writerows(regressions)
    with (args.output/'thresholds.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.writer(stream); writer.writerow(['试验T_非官方_严格max小于T', *rows.keys()])
        for row in thresholds:
            writer.writerow([row['experimental_T'], *[row[k] for k in rows]])
    for name, source in [('accuracy-results.json', accept), ('fit-run.json', fit/'run.json'), ('fit-summary.json', fit/'summary.json'),
        ('runtime-eligibility.json', ROOT/'artifacts/cinema-last-stage-eligibility-v1/results.json')]:
        shutil.copyfile(source, args.output/name)
    with zipfile.ZipFile(args.output/'models.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for p in sorted((fit/'candidate').iterdir()):
            archive.write(p, p.name)
        for k in (2, 3):
            path = args.cache_root/'artifacts/cinema-envelope-v1/stage4_sweep004'/f'selected-stage{k}.slut'
            archive.write(path, path.name)
    with zipfile.ZipFile(args.output/'fit-evidence.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.write(fit/'progress.json', 'progress.json')
        for name in ('run.json', 'progress.json'):
            archive.write(ROOT/'artifacts/cinema-last-stage-v1'/name, 'failed_v1/'+name)
    sources = ['python/lutlab/'+n for n in ('channel_tail_nodes.py', 'channel_max_nodes.py', 'channel_coordinates.py',
        'channel_global_nodes.py', 'channel_joint_nodes.py', 'io.py', 'interp.py', 'study_provenance.py')]+['scripts/'+n for n in
        ('run_cinema_last_stage.py', 'accept_channel_tail_nodes.py', 'verify_channel_coordinates.py', 'accept_channel_coordinates.py',
         'inspect_tail_runtime_eligibility.py', 'archive_cinema_last_stage.py')]+['experiments/channel-runtime/channel_native.py']
    with zipfile.ZipFile(args.output/'source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in sources:
            archive.write(ROOT/name, name)
    performance = None
    if args.performance_root is not None:
        if not args.performance_commit:
            raise ValueError('速度证据必须绑定提交')
        speed_manifest = read(args.performance_root/'manifest.json')
        expected = next(r['sha256'] for r in speed_manifest['files'] if r['path'] == 'results.json')
        if digest(args.performance_root/'results.json') != expected:
            raise ValueError('速度原件SHA与其manifest不同')
        performance = read(args.performance_root/'results.json')
        for old, new in [('results.json', 'performance-results.json'), ('manifest.json', 'performance-manifest.json')]:
            shutil.copyfile(args.performance_root/old, args.output/new)
    save(args.output/'manifest.json', {'baseline_a399_results_sha256': digest(prior_path), 'source_sha256': {n: digest(ROOT/n) for n in sources},
        'files': {p.name: digest(p) for p in args.output.iterdir()}, 'accuracy_accepted': True, 'speed_gate_pending': performance is None,
        'performance_source_commit': args.performance_commit, 'performance_source_manifest': 'performance-manifest.json' if performance else None,
        'meets_50_percent_speed_floor': performance['meets_50_percent_speed_floor'] if performance else None,
        'worst_throughput_retained': performance['worst_throughput_retained'] if performance else None,
        'no_obvious_slowdown': performance['no_obvious_slowdown'] if performance else None,
        'failed_v1': 'run_cinema_last_stage v1首批fresh后print缺json import退出；补import后v2原策略从正式severe_first完整重跑。',
        'new_default': False, 'full_stream_sha256': candidate['sha256']['oracle'],
        'scope': '87全域/历史100图与独立四级uint64一致；逐图代价和末级独立源退化单列。未生成官方成绩或盲测结论。'})
    print(json.dumps({'changes': comparisons, 'thresholds': thresholds, 'regressions': regressions, 'groups': groups}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
