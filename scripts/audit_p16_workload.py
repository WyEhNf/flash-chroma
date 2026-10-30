"""只读复算92固定阈值的全部冷/热配对、A/A、1760实际输出及RSS。"""
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
    assert plan['threshold_pixels'] == 1 << 26 and plan['images'] == [1, 10, 85, 86, 100]
    assert plan['pixels_per_image'] * 85 < plan['threshold_pixels'] < plan['pixels_per_image'] * 86
    assert quality['passed'] and len(quality['contracts']) == 2 and len(quality['photos']['actual']) == 40
    for model, modes in quality['full'].items():
        assert set(modes) == {'default', 'below', 'at'}
        for name, v in modes.items():
            assert v['colors'] == 1 << 24 and v['byte_mismatches'] == 0 and len(set(v['streams'].values())) == 1
            expected_direct = model == 'anchor' or name == 'at'
            snapshot = quality['states'][model][name]
            assert bool(snapshot['direct']['enabled']) == expected_direct
            expected_capacity = (18579204 if model == 'anchor' else 1852824 + (16777216 if expected_direct else 0))
            assert snapshot['model_bytes'] == expected_capacity
        assert len(quality['finite_cases'][model]) == 5
        for hint, v in quality['finite_cases'][model].items():
            assert v['comparisons'] == 1008 and v['rejects'] == 11
            assert bool(v['state']['direct']['enabled']) == (model == 'anchor' or int(hint) >= 1 << 26)
    for mode, cases in quality['contracts'].items():
        assert len(cases) == 8
        for case in cases:
            assert case['byte_mismatches'] == 0 and case['oracle_pixels'] == 8200 and case['backend_comparisons'] == 8
            assert bool(case['state']['candidate']['direct']['enabled']) == case['expected_direct']
            if mode == 'low':
                assert not case['expected_direct']
            if not case['expected_direct']:
                assert case['state']['reference']['model_bytes'] == case['state']['candidate']['model_bytes']
            if case['case'] == 'over255_palette':
                assert case['over255_cache_unique_count'] == 6350
    assert len(quality['arguments']['typed_rejects']) == 10
    assert len(quality['arguments']['native_unsigned_invalid_arguments']) == 10
    expected = {(r['role'], r['images']): r['output_sha256'] for r in plan['photo_expected']}
    workers = [read(f'worker{i}.json') for i in range(4)]
    assert result['worker_sha256'] == [hashlib.sha256(raw(f'worker{i}.json')).hexdigest() for i in range(4)]
    checks = 0
    for w in workers:
        assert len(w['records']) == 80 and len(w['cold_records']) == 20
        assert w['source_sha256'] == plan['source_sha256'] and w['environment']['affinity'] == plan['cpus']
        for r in w['records']:
            assert r['expected_pixels'] == r['images'] * plan['pixels_per_image']
            for name in ('warmup', 'measured', 'control'):
                g = r[name]
                assert len(g['seconds']) == (plan['warmup'] if name == 'warmup' else plan['repeats'][str(r['images'])])
                assert all(0 < v < 60 for v in g['seconds']) and g['actual_output_sha256'] == expected[r['model'], r['images']]
                if r['boundary'] == 'apply':
                    assert len(g['copy_apply_seconds']) == len(g['seconds'])
                    assert all(x >= y for x, y in zip(g['copy_apply_seconds'], g['seconds']))
                checks += 1
        for r in w['cold_records']:
            assert r['expected_pixels'] == r['images'] * plan['pixels_per_image']
            expected_direct = r['model'] == 'anchor' or (r['role'] == 'candidate' and r['expected_pixels'] >= 1 << 26)
            assert bool(r['state']['direct']['enabled']) == expected_direct
            expected_capacity = (18579204 if r['model'] == 'anchor' else 1852824 + (16777216 if expected_direct else 0))
            assert r['state']['model_bytes'] == expected_capacity
            for name in ('samples', 'control'):
                assert len(r[name]) == 5
                for g in r[name]:
                    assert g['actual_output_sha256'] == expected[r['model'], r['images']]
                    assert 0 < g['prepare_seconds'] < g['create_to_first_wall_seconds'] < 60
                    assert 0 < g['first_outplace4_seconds'] < g['create_to_first_wall_seconds']
                    checks += 1
    assert len(result['hot']) == 40 and len(result['cold']) == 10

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
            for images in (1, 100):
                rss = read(f'rss-{model}-{role}-{images}.json')
                assert rss['role'] == role and rss['model'] == model and rss['images'] == images
                assert rss['rss_delta_bytes'] == rss['after']['rss'] - rss['before']['rss']
                mode = 'at' if images == 100 and role == 'candidate' else 'default'
                assert rss['state']['model_bytes'] == quality['states'][model][mode]['model_bytes']
    if z:
        z.close()
    assert checks == 1760
    print(json.dumps({'workers': 4, 'hot_records': 320, 'cold_records': 80,
        'actual_group_output_sha256_checks': checks, 'hot_comparisons': 40, 'cold_metric_comparisons': 30,
        'independent_rss_processes': 8, 'all_pair_statistics_recomputed': True}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
