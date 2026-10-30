"""只读复算90分段三角色36场景，保留全部控制失败与实际末轮输出证据。"""
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
    plan, results = read('executed-plan.json'), read('results.json')
    quality_bytes = z.read('quality/correctness.json') if z else Path(plan['quality_proof']['path']).read_bytes()
    assert hashlib.sha256(quality_bytes).hexdigest() == plan['quality_proof']['sha256']
    quality = json.loads(quality_bytes.decode('utf-8'))
    assert quality['passed'] and len(quality['photos']) == 9
    assert all(v['colors'] == 1 << 24 and v['byte_mismatches'] == 0 for v in quality['full'].values())
    expected = {(r['role'], r['scale'], r['images']): r['output_sha256'] for r in quality['photos']}
    workers = [read(f'worker{i}.json') for i in range(4)]
    assert results['worker_sha256'] == [hashlib.sha256(raw(f'worker{i}.json')).hexdigest() for i in range(4)]
    checks = 0
    for w in workers:
        assert len(w['records']) == 108 and w['environment']['affinity'] == plan['cpus']
        assert w['source_full_sha256'] == plan['source_sha256']
        for r in w['records']:
            reference = None
            for kind in ('warmup', 'measured', 'control'):
                g = r[kind]
                assert len(g['seconds']) == (plan['warm_repeats'] if kind == 'warmup' else plan['repeats'][str(r['images'])])
                assert all(0 < v < 60 for v in g['seconds'])
                reference = reference or g['actual_output_sha256']
                assert g['actual_output_sha256'] == reference
                assert reference == expected[r['model'], r['scale'], r['images']]
                checks += 1
    assert len(results['summary']) == 36
    for r in results['summary']:
        pairs = [{x['variant']: x for x in w['records'] if
            (x['model'], x['scale'], x['images'], x['layout'], x['threads']) ==
            (r['model'], r['scale'], r['images'], r['layout'], r['threads'])} for w in workers]
        assert all(set(m) == {0, 1, 2} for m in pairs)
        assert len({x['source_sha256'] for m in pairs for x in m.values()}) == 1
        assert len({x['measured']['actual_output_sha256'] for m in pairs for x in m.values()}) == 1
        controls = {str(v): [st.median(m[v]['control']['seconds']) / st.median(m[v]['measured']['seconds'])
                            for m in pairs] for v in (0, 1, 2)}
        assert r['controls'] == controls
        assert r['ms_per_image'] == {str(v): [st.median(m[v]['measured']['seconds']) * 1000 / r['images']
                                            for m in pairs] for v in (0, 1, 2)}
        for before, after in ((0, 2), (1, 2), (0, 1)):
            q = r['comparisons'][f'{after}_over_{before}']
            ratios = [st.median(m[after]['measured']['seconds']) / st.median(m[before]['measured']['seconds']) for m in pairs]
            assert q['time_ratios'] == ratios and q['median_time_ratio'] == st.median(ratios)
            assert q['worst_throughput_retained'] == 1 / max(ratios)
            aa = controls[str(before)] + controls[str(after)]
            valid = all(plan['control_min'] <= v <= plan['control_max'] for v in aa)
            assert q['control_valid'] == valid
            assert q['grades'] == {str(g): valid and 1 / max(ratios) >= g / 100 for g in plan['grades']}
            assert q['no_obvious_slowdown'] == (valid and st.median(ratios) <= plan['no_obvious_median_max']
                and max(ratios) <= plan['no_obvious_any_max'])
    if z:
        z.close()
    print(json.dumps({'workers': 4, 'records': 432, 'actual_group_output_sha256_checks': checks,
        'scenarios': 36, 'pair_statistics_recomputed': 108,
        'new_vs_loop_valid': sum(r['comparisons']['2_over_0']['control_valid'] for r in results['summary']),
        'new_vs_bulk_valid': sum(r['comparisons']['2_over_1']['control_valid'] for r in results['summary']),
        'new_vs_loop_50': sum(r['comparisons']['2_over_0']['grades']['50'] for r in results['summary']),
        'new_vs_bulk_50': sum(r['comparisons']['2_over_1']['grades']['50'] for r in results['summary'])}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
