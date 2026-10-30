"""不加载DLL，逐组检查三模型原始轮次、实际输出和全部配对统计。"""
import argparse
import hashlib
import json
from pathlib import Path
import statistics as st
import zipfile


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    a = p.parse_args()
    z = zipfile.ZipFile(a.source) if a.source.is_file() else None
    raw = lambda n: z.read(n) if z else (a.source / n).read_bytes()
    read = lambda n: json.loads(raw(n).decode('utf-8'))
    plan = read('executed-plan.json')
    pre = read('preflight.json')
    results = read('results.json')
    workers = [read(f'worker{i}.json') for i in range(4)]
    assert results['worker_sha256'] == [hashlib.sha256(raw(f'worker{i}.json')).hexdigest() for i in range(4)]
    group_count = 0
    for i, w in enumerate(workers):
        assert w['environment']['affinity'] == plan['cpus']
        assert w['source_sha256'] == pre['source_sha256']
        assert [r['role'] for r in w['constructions']] == plan['orders'][i]
        assert len(w['records']) == 12 and len(w['constructions']) == 3
        for r in w['records']:
            expected = pre['oracle_photo_outputs'][r['role']]['whole_sha256']
            for kind in ('warmup', 'measured', 'control'):
                group = r[kind]
                assert len(group['seconds']) == (plan['warmup'] if kind == 'warmup' else plan['repeats'])
                assert all(0 < v < 60 for v in group['seconds'])
                assert group['actual_output_sha256'] == expected
                if r['boundary'] == 'apply':
                    assert len(group['copy_apply_seconds']) == len(group['seconds'])
                    assert all(t >= v for t, v in zip(group['copy_apply_seconds'], group['seconds']))
                group_count += 1
        for r in w['constructions']:
            assert r['prepare_seconds'] > 0
            assert r['first_outplace4']['actual_output_sha256'] == pre['oracle_photo_outputs'][r['role']]['whole_sha256']
            assert r['prepare_plus_first100_seconds'] == r['prepare_seconds'] + r['first_outplace4']['seconds'][0]
    assert len(results['comparisons']) == 3
    for comparison in results['comparisons']:
        before, after = comparison['before'], comparison['after']
        all_controls, retained = [], []
        assert len(comparison['summary']) == 4
        for r in comparison['summary']:
            pairs = [{x['role']: x for x in w['records'] if
                (x['threads'], x['boundary']) == (r['threads'], r['boundary'])} for w in workers]
            ratios = [st.median(m[after]['measured']['seconds']) / st.median(m[before]['measured']['seconds']) for m in pairs]
            controls = {n: [st.median(m[n]['control']['seconds']) / st.median(m[n]['measured']['seconds']) for m in pairs]
                        for n in (before, after)}
            assert r['time_ratios'] == ratios and r['median_time_ratio'] == st.median(ratios)
            assert r['controls'] == controls and r['worst_throughput_retained'] == 1 / max(ratios)
            assert r['ms_per_image'] == {n: [st.median(m[n]['measured']['seconds']) * 10 for m in pairs] for n in (before, after)}
            all_controls.extend(v for values in controls.values() for v in values)
            retained.extend(1 / v for v in ratios)
        constructions = [{r['role']: r for r in w['constructions']} for w in workers]
        assert comparison['construction_time_ratios'] == {k: [m[after][k] / m[before][k] for m in constructions]
            for k in ('prepare_seconds', 'prepare_plus_first100_seconds')}
        gates = plan['gates']
        valid = all(gates['control_any_min'] <= v <= gates['control_any_max'] for v in all_controls)
        assert comparison['control_valid'] == valid and comparison['worst_throughput_retained'] == min(retained)
        assert comparison['grades'] == {str(g): valid and min(retained) >= g / 100 for g in plan['grades']}
        assert comparison['no_obvious_slowdown'] == (valid and all(
            r['median_time_ratio'] <= gates['no_obvious_median_time_ratio_max'] and
            max(r['time_ratios']) <= gates['no_obvious_any_time_ratio_max'] for r in comparison['summary']))
    if z:
        z.close()
    print(json.dumps({'workers': 4, 'steady_records': 48, 'actual_steady_group_sha256_checks': group_count,
        'first100_output_sha256_checks': 12, 'all_three_pair_statistics_recomputed': True}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
