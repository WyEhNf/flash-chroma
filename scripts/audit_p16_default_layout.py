"""独立只读复算93全部cell/交互/地址/CPU端点/实际SHA，不加载DLL或重测。"""
import argparse
import hashlib
import itertools
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
    workers = [read(f'worker{i}.json') for i in range(4)]
    assert plan['rounds_per_role_per_phase'] == 63 and plan['chunk_repeats'] == 7
    assert plan['control_min'] == .85 and plan['control_max'] == 1.15
    assert result['worker_sha256'] == [hashlib.sha256(raw(f'worker{i}.json')).hexdigest() for i in range(4)]
    combos = set(itertools.product(('ABBA', 'BAAB'), (0, 1), (0, 64), ('blocked', 'interleaved')))
    output_checks = rounds = 0
    all_cpu = []
    for w in workers:
        assert len(w['records']) == 16 and w['source_sha256'] == plan['source_sha256']
        assert w['environment']['affinity'] == plan['cpus']
        assert {(r['construction'], r['pair'], r['work_offset'], r['schedule']) for r in w['records']} == combos
        addresses = {offset: {r['work_address'] for r in w['records'] if r['work_offset'] == offset} for offset in (0, 64)}
        assert len(addresses[0]) == len(addresses[64]) == 1
        assert next(iter(addresses[64])) - next(iter(addresses[0])) == 64
        assert all(v['cache_pointer_available_by_public_ABI'] is False and v['cache_table_mod64'] is None
            and v['model_bytes'] == 1852824 and not v['direct']['enabled']
            for allocation in w['allocations'] for v in allocation['handles'])
        for r in w['records']:
            assert r['work_mod64'] == 0 and r['work_mod4096'] == r['work_address'] % 4096
            assert len(r['warmup']) == 2 and len(r['measured']) == len(r['control']) == 18
            for phase in ('warmup', 'measured', 'control'):
                chunks = r[phase]
                for c in chunks:
                    wanted = 2 if phase == 'warmup' else 7
                    assert c['repeats'] == len(c['apply_seconds']) == len(c['copy_apply_seconds']) == wanted
                    assert c['actual_output_sha256'] == plan['expected_output_sha256']
                    assert c['wall_seconds'] == (c['wall_end_ns'] - c['wall_begin_ns']) * 1e-9
                    assert all(0 < b <= t for b, t in zip(c['apply_seconds'], c['copy_apply_seconds']))
                    assert c['caller_cpu_begin'] in plan['cpus'] and c['caller_cpu_end'] in plan['cpus']
                    output_checks += 1
                    rounds += wanted
                    all_cpu.append((c['caller_cpu_begin'], c['caller_cpu_end']))
                if phase != 'warmup':
                    if r['schedule'] == 'blocked':
                        assert [c['role'] for c in chunks] == [r['role_order'][0]] * 9 + [r['role_order'][1]] * 9
                    else:
                        wanted_roles = [role for block in range(9) for role in
                            (r['role_order'] if block % 2 == 0 else list(reversed(r['role_order'])))]
                        assert [c['role'] for c in chunks] == wanted_roles
    assert output_checks == 2432 and rounds == 16384

    def values(r, phase, role):
        out = [v for c in r[phase] if c['role'] == role for v in c['apply_seconds']]
        assert len(out) == 63
        return out

    assert len(result['cells']) == 16 and len(result['interactions']) == 24
    for row in result['cells']:
        key = tuple(row[k] for k in ('construction', 'pair', 'work_offset', 'schedule'))
        records = [next(r for r in w['records'] if tuple(r[k] for k in
            ('construction', 'pair', 'work_offset', 'schedule')) == key) for w in workers]
        ratios = [st.median(values(r, 'measured', 'candidate')) / st.median(values(r, 'measured', 'reference')) for r in records]
        controls = [st.median(values(r, 'control', role)) / st.median(values(r, 'measured', role))
            for r in records for role in ('reference', 'candidate')]
        valid = all(.85 <= v <= 1.15 for v in controls)
        assert row['time_ratios'] == ratios and row['median_time_ratio'] == st.median(ratios)
        assert row['controls'] == controls and row['control_valid'] == valid
        assert row['worst_throughput_retained'] == 1 / max(ratios)
        assert row['grades'] == {str(g): valid and 1 / max(ratios) >= g / 100 for g in plan['grades']}
        assert row['no_obvious_slowdown'] == (valid and st.median(ratios) <= 1.05 and max(ratios) <= 1.1)
    levels = {'schedule': ('blocked', 'interleaved'), 'work_offset': (0, 64), 'construction': ('ABBA', 'BAAB')}
    for q in result['interactions']:
        lo, hi = [next(c for c in result['cells'] if c[q['dimension']] == level and
            all(c[k] == v for k, v in q['fixed'].items())) for level in levels[q['dimension']]]
        ratios = [a / b for a, b in zip(hi['time_ratios'], lo['time_ratios'])]
        valid = lo['control_valid'] and hi['control_valid']
        direction = 'increase' if st.median(ratios) >= 1.1 and sum(v >= 1.1 for v in ratios) >= 3 else (
            'decrease' if st.median(ratios) <= .9 and sum(v <= .9 for v in ratios) >= 3 else 'unresolved')
        assert q['ratios'] == ratios and q['median_ratio'] == st.median(ratios) and q['control_valid'] == valid
        assert q['diagnostic_direction'] == (direction if valid else 'invalid')
    if z:
        z.close()
    print(json.dumps({'workers': 4, 'all_cells': 64, 'paired_comparisons': 16, 'interactions': 24,
        'actual_group_output_sha256_checks': output_checks, 'native_image_inner_rounds': rounds,
        'caller_endpoint_cpu_changes': sum(a != b for a, b in all_cpu),
        'all_statistics_recomputed': True, 'restore92_qualification': False}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
