"""只读复算90独立31轮镜像确认，不加载DLL、不改控制资格。"""
import argparse
import hashlib
import json
import math
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
    expected = {r['scale']: r['output_sha256'] for r in quality['photos'] if r['role'] == 'direct' and r['images'] == 100}
    workers = [read(f'worker{i}.json') for i in range(4)]
    assert results['worker_sha256'] == [hashlib.sha256(raw(f'worker{i}.json')).hexdigest() for i in range(4)]
    group_count = 0
    for i, w in enumerate(workers):
        assert len(w['records']) == 9 and w['source_full_sha256'] == plan['source_sha256']
        assert w['environment']['affinity'] == plan['cpus']
        for r in w['records']:
            scene = next(x for x in plan['scenes'] if x['id'] == r['scene'])
            assert len(r['warmup']['seconds']) == 2 and r['warmup']['actual_output_sha256'] == expected[scene['scale']]
            assert len(r['occurrences']) == 2
            assert [x['sequence_position'] for x in r['occurrences']] == [j for j, v in enumerate(plan['sequences'][i]) if v == r['variant']]
            for g in [r['warmup']] + r['occurrences']:
                assert len(g['seconds']) == (2 if g is r['warmup'] else 31)
                assert all(0 < v < 60 for v in g['seconds']) and g['actual_output_sha256'] == expected[scene['scale']]
                group_count += 1
    for row in results['summary']:
        matched = [{r['variant']: r for r in w['records'] if r['scene'] == row['scene']['id']} for w in workers]
        assert all(set(m) == {0, 1, 2} for m in matched)
        controls = {str(v): [st.median(m[v]['occurrences'][1]['seconds']) / st.median(m[v]['occurrences'][0]['seconds'])
                            for m in matched] for v in (0, 1, 2)}
        estimates = [{v: math.sqrt(st.median(m[v]['occurrences'][0]['seconds']) * st.median(m[v]['occurrences'][1]['seconds']))
                      for v in (0, 1, 2)} for m in matched]
        assert row['controls'] == controls
        assert row['geomean_ms_per_image'] == {str(v): [e[v] * 10 for e in estimates] for v in (0, 1, 2)}
        for before, after in ((0, 2), (1, 2), (0, 1)):
            q = row['comparisons'][f'{after}_over_{before}']
            ratios = [e[after] / e[before] for e in estimates]
            valid = all(plan['control_min'] <= v <= plan['control_max'] for v in controls[str(before)] + controls[str(after)])
            assert q['time_ratios'] == ratios and q['median_time_ratio'] == st.median(ratios)
            assert q['worst_throughput_retained'] == 1 / max(ratios) and q['control_valid'] == valid
            assert q['grades'] == {str(g): valid and 1 / max(ratios) >= g / 100 for g in plan['grades']}
    if z:
        z.close()
    print(json.dumps({'workers': 4, 'records': 36, 'scenarios': 3, 'actual_group_output_sha256_checks': group_count,
        'pair_statistics_recomputed': 9, 'all_source_and_output_identity_checks_passed': True}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
