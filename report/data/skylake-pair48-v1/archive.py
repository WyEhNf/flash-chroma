"""归档79新候选证据并从原始批内数组独立复算；不加载原生库。"""
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


def copy_folder(name):
    source, target = ROOT/'artifacts'/name, HERE/name
    if target.exists():
        raise ValueError('不得覆盖已有档案')
    shutil.copytree(source, target, ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    return [p for p in target.rglob('*') if p.is_file()]


def archive_build():
    source = ROOT/'artifacts/skylake-pair48-linux-build-v1'
    target = HERE/source.name
    target.mkdir(exist_ok=False)
    chosen = ['build-log.json','build.json','compile_commands.json','libraries-Release.json',
              'measured-source.zip',*sorted(p.name for p in source.glob('libjshc*.so'))]
    for name in chosen:
        shutil.copy2(source/name, target/name)
    with zipfile.ZipFile(target/'build-intermediates.zip','w',zipfile.ZIP_DEFLATED) as stream:
        for path in sorted(source.rglob('*')):
            if path.is_file() and path.name not in chosen:
                stream.write(path,path.relative_to(source).as_posix())
    return [p for p in target.rglob('*') if p.is_file()]


def recompute(base):
    result = read(base/'results.json')
    workers = [read(base/f'worker{i}.json') for i in range(4)]
    assert all(w['measurement_completed'] for w in workers)
    rows, controls = [], []
    all_batches = [r for w in workers for r in [*w['control_records'],
                   *[b for x in w['records'] for b in x['batches'].values()]]]
    assert len(all_batches) == 48
    for batch in all_batches:
        assert batch['batch_final_output_sha256'] == 'f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528'
        assert batch['warmup_output_sha256'] == batch['batch_final_output_sha256']
        assert batch['source_unchanged'] and batch['sentinels_unchanged']
        assert batch['layout'] == ('pair48' if batch['variant']=='candidate' else 'reference23')
    for w in workers:
        for phase in ('before','after'):
            handle = w['handles']['candidate'][phase]
            pages = handle['paged_info']
            assert handle['pair48_enabled'] == 1
            assert pages['fully_huge'] and pages['aligned_2m']
            assert pages['bytes'] == pages['smaps']['mapping_bytes'] == 2**24
    for threads in (1,4):
        ratios = {key: [] for key in ('apply','outplace','copy_apply','prepare_outplace')}
        aa_ratios = []
        for worker in workers:
            by = {r['variant']:r for r in worker['records'] if r['requested_threads']==threads}
            for mode,key in (('apply','apply_seconds'),('outplace','outplace_seconds'),('copy_apply','legacy_copy_apply_seconds')):
                ratios[mode].append(statistics.mean(by['candidate'][key])/statistics.mean(by['reference'][key]))
            ratios['prepare_outplace'].append(by['candidate']['prepare_plus_first_100_outplace_seconds']/by['reference']['prepare_plus_first_100_outplace_seconds'])
            aa = {r['label']:r for r in worker['control_records'] if r['requested_threads']==threads}
            aa_ratios.append(statistics.mean(aa['B']['apply_seconds'])/statistics.mean(aa['A']['apply_seconds']))
        reported = next(r for r in result['paired'] if r['requested_threads']==threads)
        medians = {k:statistics.median(v) for k,v in ratios.items()}
        for mode,key in (('apply','median_apply_ratio'),('outplace','median_outplace_ratio'),('copy_apply','median_legacy_copy_apply_ratio'),('prepare_outplace','median_prepare_plus_100_outplace_ratio')):
            assert abs(medians[mode]-reported[key]) < 1e-14
        rows.append({'threads':threads,'process_ratios':ratios,'median_ratios':medians,
                     'throughput_multipliers':{k:1/v for k,v in medians.items()}})
        controls.append({'threads':threads,'paired_B_over_A':aa_ratios,'median':statistics.median(aa_ratios),
                         'all_pass':min(aa_ratios)>=.8 and max(aa_ratios)<=1.25 and 1/1.10<=statistics.median(aa_ratios)<=1.10})
    rounds = sum(len(r['apply_seconds']) if r['mode']=='legacy' else len(r['outplace_seconds']) for r in all_batches)
    assert rounds == 1920
    control_valid = all(c['all_pass'] for c in controls)
    assert result['measurement_control_valid'] == control_valid
    gate_valid = all(r['median_ratios']['apply']<=1/3 and r['median_ratios']['outplace']<=1/3 and
                     r['median_ratios']['prepare_outplace']<=1 and max(r['process_ratios']['apply'])<=.9 for r in rows)
    assert result['accepted_on_this_host'] == (control_valid and gate_valid)
    return {'pass':True,'recomputed':rows,'controls':controls,'inner_rounds':rounds,
            'accepted':result['accepted_on_this_host'],'reported_failed_gates':result['failed_gates']}


def main():
    decision = read(ROOT/'artifacts/skylake-pair48-confirmation-decision-v1.json')
    paths = archive_build()
    names = ['skylake-pair48-static-v1','skylake-pair48-preflight-v1',
             'skylake-pair48-linux-full-v1','skylake-pair48-long-perf-v1']
    if decision['confirmation_executed']:
        names.append('skylake-pair48-long-confirm-v1')
    for name in names:
        paths.extend(copy_folder(name))
    copied_decision = HERE/'confirmation-decision.json'
    shutil.copy2(ROOT/'artifacts/skylake-pair48-confirmation-decision-v1.json',copied_decision)
    paths.append(copied_decision)
    for source in ('prepare_pair48_checks.py','prepare_pair48_perf_glue.py'):
        target = HERE/'skylake-pair48-preflight-v1'/('root-'+source)
        shutil.copy2(ROOT/'artifacts'/source,target)
        paths.append(target)
    files = {p.relative_to(HERE).as_posix():{'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(paths)}
    (HERE/'manifest.json').write_text(json.dumps({'schema':1,'files':files},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    full = read(HERE/'skylake-pair48-linux-full-v1/results.json')
    assert full['pass'] and full['pair48_enabled']=={'single':0,'chain':1}
    first = recompute(HERE/'skylake-pair48-long-perf-v1')
    audit = {'purpose':__doc__,'full_rgb8_pass':True,'first_series':first,
             'confirmation_executed':decision['confirmation_executed'],'candidate_calls':0}
    if decision['confirmation_executed']:
        assert first['accepted']
        audit['confirmation_series'] = recompute(HERE/'skylake-pair48-long-confirm-v1')
    else:
        assert not first['accepted']
    (HERE/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'files':len(files),'audit':audit},ensure_ascii=False))


if __name__ == '__main__':
    main()
