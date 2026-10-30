"""独立复算97同场87/95两分母、全部AA/1584实际SHA和12RSS；不重测。"""
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
    assert plan['threshold_pixels'] == 1 << 26 and plan['images'] == [1, 10, 100]
    assert plan['hot_images'] == [1, 10, 100]
    assert plan['default_images'] == [1] and plan['denominators'] == ['reference', 'previous']
    assert quality['passed'] and len(quality['contracts']) == 2 and len(quality['photos']) == 32
    dictionary = quality['dictionary_contract']
    assert dictionary['passed'] and dictionary['finite_cases'] == 13
    assert dictionary['fixed_array_bytes'] == 3580 and dictionary['scratch_object_bytes'] == 3584
    assert dictionary['worst_same_bucket_distinct_keys'] == 256 and dictionary['whole_cache_hole_boundary']
    private = quality['private_kernel_contract']
    assert private['passed'] and private['cases'] == 150 and private['production_c_abi_changes'] == 0
    assert len(quality['table_cases']) == 4 and len(quality['contract_tables']) == 16
    for row in quality['table_cases'] + quality['contract_tables']:
        assert row['byte_mismatches'] == 0 and row['previous_sha256'] == row['candidate_sha256']
        assert row['table_bytes'] == (1 << 24 if row['enabled'] else 0)
        assert row['cache_entries'] >= 0 and len(row['cache_sha256']) == 64
    for model, modes in quality['full'].items():
        assert set(modes) == {'default', 'high'}
        for name, versions in modes.items():
            assert set(versions) == {'previous', 'candidate'}
            for version, v in versions.items():
                assert v['colors'] == 1 << 24 and v['byte_mismatches'] == 0 and len(set(v['streams'].values())) == 1
                expected_direct = model == 'anchor' or name == 'high'
                snapshot = quality['states'][model][name][version]
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
        assert len(w['records']) == 72 and len(w['cold_records']) == 18
        assert {(v['model'],v['images'],v['role'],v['threads'],v['boundary']) for v in w['records']} == {(m,n,r,t,b) for m in ('ordinary','anchor') for n in (1,10,100) for r in ('reference','previous','candidate') for t in (1,4) for b in ('apply','outplace')}
        assert {(v['model'],v['images'],v['role']) for v in w['cold_records']} == {(m,n,r) for m in ('ordinary','anchor') for n in plan['images'] for r in ('reference','previous','candidate')}
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
            expected_direct = r['model'] == 'anchor' or (r['role'] != 'reference' and r['images'] * 786432 >= 1 << 26)
            assert bool(r['state']['direct']['enabled']) == expected_direct
            expected_capacity = (18579204 if r['model'] == 'anchor' else 1852824 + (16777216 if expected_direct else 0))
            assert r['state']['model_bytes'] == expected_capacity
            for name in ('samples', 'control'):
                assert len(r[name]) == 5
                for g in r[name]:
                    expected_default = r['role'] == 'reference' or r['images'] == 1
                    assert g['used_default_create'] == expected_default
                    assert g['expected_pixels'] == (None if expected_default else r['images'] * 786432)
                    assert g['actual_output_sha256'] == expected[r['model'], r['images']]
                    assert 0 < g['prepare_seconds'] < g['create_to_first_wall_seconds'] < 60
                    assert 0 < g['first_outplace4_seconds'] < g['create_to_first_wall_seconds']
                    checks += 1
        for model in ('ordinary', 'anchor'):
            for images in plan['images']:
                rows = [r for r in w['records'] + w['cold_records'] if r['model'] == model and r['images'] == images]
                assert len({r['work_address'] for r in rows}) == len({r['source_address'] for r in rows}) == 1
    assert len(result['hot']) == 48 and len(result['cold']) == 12

    def verify(q, values, controls):
        ratios = [x / y for x, y in zip(values['candidate'], values['reference'])]
        valid = all(plan['control_min'] <= v <= plan['control_max'] for v in controls)
        assert q['time_ratios'] == ratios and q['median_time_ratio'] == st.median(ratios)
        assert q['controls'] == controls and q['control_valid'] == valid and q['worst_throughput_retained'] == 1 / max(ratios)
        assert q['grades'] == {str(g): valid and 1 / max(ratios) >= g / 100 for g in plan['grades']}
        assert q['no_obvious_slowdown'] == (valid and st.median(ratios) <= plan['no_obvious_median_max']
            and max(ratios) <= plan['no_obvious_any_max'])

    for row in result['hot']:
        denominator = row['denominator']
        roles = (denominator, 'candidate')
        pairs = [{r['role']: r for r in w['records'] if
            (r['model'], r['images'], r['threads'], r['boundary']) ==
            (row['model'], row['images'], row['threads'], row['boundary'])} for w in workers]
        values = {n: [st.median(m[n]['measured']['seconds']) for m in pairs] for n in roles}
        controls = [st.median(m[n]['control']['seconds']) / st.median(m[n]['measured']['seconds'])
                    for m in pairs for n in roles]
        verify(row, {'candidate': values['candidate'], 'reference': values[denominator]}, controls)
        assert row['ms_per_image'] == {n: [v * 1000 / row['images'] for v in a] for n, a in values.items()}
    for row in result['cold']:
        denominator = row['denominator']
        roles = (denominator, 'candidate')
        pairs = [{r['role']: r for r in w['cold_records'] if
            (r['model'], r['images']) == (row['model'], row['images'])} for w in workers]
        for key, q in row['metrics'].items():
            values = {n: [st.median(x[key] for x in m[n]['samples']) for m in pairs] for n in roles}
            controls = [st.median(x[key] for x in m[n]['control']) / st.median(x[key] for x in m[n]['samples'])
                        for m in pairs for n in roles]
            verify(q, {'candidate': values['candidate'], 'reference': values[denominator]}, controls)
            assert q['milliseconds'] == {n: [v * 1000 for v in a] for n, a in values.items()}
    for model in ('ordinary', 'anchor'):
        for role in ('reference', 'previous', 'candidate'):
            for images in (1, 100):
                rss = read(f'rss-{model}-{role}-{images}.json')
                assert rss['role'] == role and rss['model'] == model and rss['images'] == images
                assert rss['rss_delta_bytes'] == rss['after']['rss'] - rss['before']['rss']
                expected_direct = model == 'anchor' or (role != 'reference' and images == 100)
                expected_capacity = 18579204 if model == 'anchor' else 1852824 + ((1 << 24) if expected_direct else 0)
                assert rss['state']['model_bytes'] == expected_capacity
    if z:
        z.close()
    assert checks == 1584
    print(json.dumps({'workers': 4, 'hot_records': 288, 'cold_records': 72,
        'actual_group_output_sha256_checks': checks, 'hot_comparisons': 48, 'cold_metric_comparisons': 36,
        'independent_rss_processes': 12, 'all_pair_statistics_recomputed': True}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
