"""只读复算91全部冷/热配对、A/A、实际末轮输出及独立RSS，不追加测量。"""
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
    plan, result = read('executed-plan.json'), read('results.json')
    quality_bytes = z.read('quality/correctness.json') if z else Path(plan['quality_proof']['path']).read_bytes()
    assert hashlib.sha256(quality_bytes).hexdigest() == plan['quality_proof']['sha256']
    quality = json.loads(quality_bytes.decode('utf-8'))
    assert quality['passed'] and len(quality['contracts']) == 8 and len(quality['photos']) == 8
    assert all(v['colors'] == 1 << 24 and v['byte_mismatches'] == 0 for v in quality['full'].values())
    assert all(len(set(v['streams'].values())) == 1 for v in quality['full'].values())
    assert quality['finite_cases'] == {'ordinary': 1008, 'ordinary_reject': 11, 'anchor': 1008, 'anchor_reject': 11}
    assert quality['states']['ordinary']['candidate']['model_bytes'] - quality['states']['ordinary']['reference']['model_bytes'] == 1 << 24
    assert quality['states']['anchor']['candidate']['model_bytes'] == quality['states']['anchor']['reference']['model_bytes']
    for case in quality['contracts']:
        assert case['byte_mismatches'] == 0 and case['oracle_pixels'] == 8200 and case['backend_comparisons'] == 8
        assert bool(case['state']['candidate']['direct']['enabled']) == case['expected_direct']
        if not case['expected_direct']:
            assert case['state']['reference']['model_bytes'] == case['state']['candidate']['model_bytes']
        if case['case'] == 'over255_palette':
            assert case['over255_cache_unique_count'] == 6350
    expected = {(r['role'], r['images']): r['output_sha256'] for r in plan['photo_expected']}
    workers = [read(f'worker{i}.json') for i in range(4)]
    assert result['worker_sha256'] == [hashlib.sha256(raw(f'worker{i}.json')).hexdigest() for i in range(4)]
    checks = 0
    for w in workers:
        assert len(w['records']) == 48 and len(w['cold_records']) == 12
        assert w['source_sha256'] == plan['source_sha256'] and w['environment']['affinity'] == plan['cpus']
        for r in w['records']:
            for name in ('warmup', 'measured', 'control'):
                g = r[name]
                assert len(g['seconds']) == (plan['warmup'] if name == 'warmup' else plan['repeats'][str(r['images'])])
                assert all(0 < v < 60 for v in g['seconds']) and g['actual_output_sha256'] == expected[r['model'], r['images']]
                if r['boundary'] == 'apply':
                    assert len(g['copy_apply_seconds']) == len(g['seconds'])
                    assert all(x >= y for x, y in zip(g['copy_apply_seconds'], g['seconds']))
                checks += 1
        for r in w['cold_records']:
            for name in ('samples', 'control'):
                assert len(r[name]) == 5
                for g in r[name]:
                    assert g['actual_output_sha256'] == expected[r['model'], r['images']]
                    assert 0 < g['prepare_seconds'] < g['create_to_first_wall_seconds'] < 60
                    assert 0 < g['first_outplace4_seconds'] < g['create_to_first_wall_seconds']
                    checks += 1
    assert len(result['hot']) == 24 and len(result['cold']) == 6

    def verify(q, values, controls):
        ratios = [x / y for x, y in zip(values['candidate'], values['reference'])]
        valid = all(plan['control_min'] <= v <= plan['control_max'] for v in controls)
        assert q['time_ratios'] == ratios and q['median_time_ratio'] == st.median(ratios)
        assert q['controls'] == controls and q['control_valid'] == valid and q['worst_throughput_retained'] == 1 / max(ratios)
        assert q['grades'] == {str(g): valid and 1 / max(ratios) >= g / 100 for g in plan['grades']}
        assert q['no_obvious_slowdown'] == (valid and st.median(ratios) <= plan['no_obvious_median_max']
            and max(ratios) <= plan['no_obvious_any_max'])

    for row in result['hot']:
        pairs = [{r['role']: r for r in w['records'] if
            (r['model'], r['images'], r['threads'], r['boundary']) ==
            (row['model'], row['images'], row['threads'], row['boundary'])} for w in workers]
        values = {n: [st.median(m[n]['measured']['seconds']) for m in pairs] for n in ('reference', 'candidate')}
        controls = [st.median(m[n]['control']['seconds']) / st.median(m[n]['measured']['seconds'])
                    for m in pairs for n in ('reference', 'candidate')]
        verify(row, values, controls)
        assert row['ms_per_image'] == {n: [v * 1000 / row['images'] for v in a] for n, a in values.items()}
    for row in result['cold']:
        pairs = [{r['role']: r for r in w['cold_records'] if
            (r['model'], r['images']) == (row['model'], row['images'])} for w in workers]
        for key, q in row['metrics'].items():
            values = {n: [st.median(x[key] for x in m[n]['samples']) for m in pairs] for n in ('reference', 'candidate')}
            controls = [st.median(x[key] for x in m[n]['control']) / st.median(x[key] for x in m[n]['samples'])
                        for m in pairs for n in ('reference', 'candidate')]
            verify(q, values, controls)
            assert q['milliseconds'] == {n: [v * 1000 for v in a] for n, a in values.items()}
    for model in ('ordinary', 'anchor'):
        for role in ('reference', 'candidate'):
            rss = read(f'rss-{model}-{role}.json')
            assert rss['role'] == role and rss['model'] == model
            assert rss['rss_delta_bytes'] == rss['after']['rss'] - rss['before']['rss']
            assert rss['state']['model_bytes'] == quality['states'][model][role]['model_bytes']
    if z:
        z.close()
    print(json.dumps({'workers': 4, 'hot_records': 192, 'cold_records': 48,
        'actual_group_output_sha256_checks': checks, 'hot_comparisons': 24, 'cold_metric_comparisons': 18,
        'independent_rss_processes': 4, 'all_pair_statistics_recomputed': True}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
