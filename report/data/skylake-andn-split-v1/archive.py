"""保存75/76/77静态失败及78完整色域与受控长批次首次系列，独立复算且拒绝覆盖。"""
import hashlib
import json
from pathlib import Path
import shutil
import statistics
import zipfile

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = ROOT/'artifacts/skylake-andn-split-linux-build-v1'
    target = HERE/source.name
    if target.exists():
        raise ValueError('不得覆盖已有构建档案')
    target.mkdir()
    chosen = ['build-log.json', 'build.json', 'compile_commands.json',
        'libraries-Release.json', 'measured-source.zip', *sorted(p.name for p in source.glob('libjshc*.so'))]
    for name in chosen:
        shutil.copy2(source/name, target/name)
    with zipfile.ZipFile(target/'build-intermediates.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(source.rglob('*')):
            if p.is_file() and p.name not in chosen:
                z.write(p, p.relative_to(source).as_posix())
    paths = [p for p in target.rglob('*') if p.is_file()]
    for name in ('skylake-andn-split-linux-full-v1', 'skylake-andn-split-long-perf-v1'):
        source, target = ROOT/'artifacts'/name, HERE/name
        if target.exists():
            raise ValueError('不得覆盖已有完整域或墙钟档案')
        shutil.copytree(source, target)
        paths.extend(p for p in target.rglob('*') if p.is_file())
    decision = HERE/'confirmation-decision.json'
    if decision.exists():
        raise ValueError('不得覆盖确认决定')
    shutil.copy2(ROOT/'artifacts/skylake-andn-split-confirmation-decision-v1.json', decision)
    paths.append(decision)
    for name in ('skylake-andn-split-static-v1', 'skylake-andn-split-preflight-v1'):
        source, target = ROOT/'artifacts'/name, HERE/name
        if target.exists(): raise ValueError('不得覆盖静态或策略生成原件')
        shutil.copytree(source, target)
        paths.extend(p for p in target.rglob('*') if p.is_file())
    for prefix in ('skylake-andn-load', 'skylake-andn-zext', 'skylake-andn-cursor'):
        source, target = ROOT/'artifacts'/(prefix+'-linux-build-v1'), HERE/(prefix+'-linux-build-v1')
        if target.exists(): raise ValueError('不得覆盖静态失败构建原件')
        target.mkdir()
        chosen = ['build-log.json', 'build.json', 'compile_commands.json', 'libraries-Release.json', 'measured-source.zip', *sorted(p.name for p in source.glob('libjshc*.so'))]
        for name in chosen: shutil.copy2(source/name,target/name)
        with zipfile.ZipFile(target/'build-intermediates.zip','w',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(source.rglob('*')):
                if p.is_file() and p.name not in chosen:z.write(p,p.relative_to(source).as_posix())
        paths.extend(p for p in target.rglob('*') if p.is_file())
        for suffix in ('-static-v1', '-preflight-v1'):
            source, target = ROOT/'artifacts'/(prefix+suffix), HERE/(prefix+suffix)
            if not source.exists(): continue
            if target.exists():raise ValueError('不得覆盖静态失败证据')
            shutil.copytree(source,target);paths.extend(p for p in target.rglob('*') if p.is_file())
    files = {p.relative_to(HERE).as_posix(): {'bytes': p.stat().st_size, 'sha256': digest(p)} for p in sorted(paths)}
    (HERE/'manifest.json').write_text(json.dumps({'schema': 1, 'files': files}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    base = HERE/'skylake-andn-split-long-perf-v1'
    workers = [read(base/f'worker{i}.json') for i in range(4)]
    perf = read(base/'results.json')
    full = read(HERE/'skylake-andn-split-linux-full-v1/results.json')
    assert all(w['measurement_completed'] for w in workers)
    rows, controls = [], []
    for threads in (1, 4):
        ratios = {mode: [] for mode in ('apply', 'outplace', 'copy_apply')}
        control = []
        for worker in workers:
            by = {r['variant']: r for r in worker['records'] if r['requested_threads'] == threads}
            for mode, key in (('apply', 'apply_seconds'), ('outplace', 'outplace_seconds'),
                    ('copy_apply', 'legacy_copy_apply_seconds')):
                ratios[mode].append(statistics.mean(by['candidate'][key])/statistics.mean(by['reference'][key]))
            aa = {r['label']: r for r in worker['control_records'] if r['requested_threads'] == threads}
            control.append(statistics.mean(aa['B']['apply_seconds'])/statistics.mean(aa['A']['apply_seconds']))
            for record in worker['control_records'] + [b for r in worker['records'] for b in r['batches'].values()]:
                assert record['batch_final_output_sha256'] == 'f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528'
                assert record['source_unchanged'] and record['sentinels_unchanged']
        ratios['prepare_outplace'] = []
        for worker in workers:
            by = {r['variant']: r for r in worker['records'] if r['requested_threads'] == threads}
            ratios['prepare_outplace'].append(by['candidate']['prepare_plus_first_100_outplace_seconds']/by['reference']['prepare_plus_first_100_outplace_seconds'])
        reported = next(r for r in perf['paired'] if r['requested_threads'] == threads)
        for mode, key in (('apply', 'median_apply_ratio'), ('outplace', 'median_outplace_ratio'),
                ('copy_apply', 'median_legacy_copy_apply_ratio'), ('prepare_outplace', 'median_prepare_plus_100_outplace_ratio')):
            assert abs(statistics.median(ratios[mode])-reported[key]) < 1e-14
        rows.append({'threads': threads, 'process_ratios': ratios,
            'median_ratios': {k: statistics.median(v) for k, v in ratios.items()},
            'throughput_multipliers': {k: 1/statistics.median(v) for k, v in ratios.items()}})
        controls.append({'threads': threads, 'paired_B_over_A': control,
            'median': statistics.median(control), 'all_pass': min(control) >= 1/1.25 and max(control) <= 1.25
                and 1/1.10 <= statistics.median(control) <= 1.10})
    count = sum(len(r['apply_seconds']) if r['mode'] == 'legacy' else len(r['outplace_seconds'])
        for w in workers for r in [*w['control_records'], *[b for x in w['records'] for b in x['batches'].values()]])
    assert count == 1920
    for w in workers:
        for phase in ('before', 'after'):
            pages = w['handles']['candidate'][phase]['paged_info']
            assert pages['fully_huge'] and pages['bytes'] == pages['smaps']['mapping_bytes'] == 2**24
            assert w['handles']['candidate'][phase]['andn_split_enabled'] == 1
        for r in [*w['control_records'], *[b for x in w['records'] for b in x['batches'].values()]]:
            expected = 'andn_split' if r['variant'] == 'candidate' else 'reference23'
            assert r['layout'] == expected
    assert full['andn_split_enabled'] == {'single': 0, 'chain': 1}
    assert full['model_accounting_bytes']['candidate']['chain'] == 28046644
    assert perf['measurement_control_valid'] == all(c['all_pass'] for c in controls)
    d = read(decision)
    assert not perf['accepted_on_this_host'] and not d['confirmation_executed']
    audit = {'full_rgb8_pass': full['pass'], 'independent_colors': full['independent_table_colors'],
        'recomputed': rows, 'controls': controls, 'inner_rounds': count,
        'reported_control_valid': perf['measurement_control_valid'], 'accepted': perf['accepted_on_this_host'],
        'failed_gates': perf['failed_gates'], 'confirmation_skipped': True,
        'note': '全部原始数组均保留，先批内均值再四配对中位；首次失败按冻结规则跳过确认，未重测择优。'}
    (HERE/'audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'files': len(files), 'audit': audit}, ensure_ascii=False))


if __name__ == '__main__':
    main()
