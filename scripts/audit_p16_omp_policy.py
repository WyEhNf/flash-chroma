"""96静态独立审计草稿；只读原数组/线程状态，不加载DLL。"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics as st


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    a = p.parse_args()
    read = lambda n: json.loads((a.source / n).read_text(encoding='utf-8'))
    plan, result = read('executed-plan.json'), read('results.json')
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest() == plan['audit_sha256']
    assert plan['policy_orders'] == [['U', 'P', 'P', 'U'], ['P', 'U', 'U', 'P'],
        ['U', 'P', 'P', 'U'], ['P', 'U', 'U', 'P']]
    assert plan['orders'] == [['reference', 'previous', 'candidate'], ['candidate', 'previous', 'reference'],
        ['previous', 'reference', 'candidate'], ['candidate', 'reference', 'previous']]
    assert len(plan['process_order']) == 8 and {(v['worker'], v['threads']) for v in plan['process_order']} == {
        (i, t) for i in range(4) for t in (1, 4)}
    assert plan['warmup'] == 2 and plan['repeats'] == (1 if plan['mode'] == 'quality' else 63)
    assert plan['control_min'] == .85 and plan['control_max'] == 1.15 and plan['cpus'] == [0, 2, 4, 6]
    expected = {v['role']: v['output_sha256'] for v in plan['photo_expected'] if v['images'] == 1}
    workers, hashes, checks = {}, [], 0

    def team(snapshot, w, policy=None):
        assert snapshot['return_code'] == 0
        values = snapshot['team']
        n = 1 if snapshot['scope'] in ('main', 'main_setup') else 4
        assert len(values) == n
        assert [v['os_tid'] for v in values] == (w['control']['tids'][:1] if n == 1 else w['control']['tids'])
        for t, v in enumerate(values):
            assert v['version'] == 1 and v['omp_tid'] == t and v['team_size'] == n
            assert v['query_before_ok'] and v['query_after_ok'] and v['group_before'] == v['group_after'] == 0
            assert v['mask_after'] in (0x55, 1 << (2 * t))
            if snapshot['action'] in (1, 2):
                assert v['set_attempted'] and not v['set_error'] and v['previous_mask']
                assert not (v['previous_mask'] & ~0x55)
                assert v['mask_after'] == (1 << (2 * t) if snapshot['action'] == 1 else 0x55)
                assert snapshot['action'] != 1 or v['cpu_after'] == 2 * t
            if policy is not None:
                desired = 0x55 if policy == 'U' else 1 << (2 * t)
                assert snapshot['action'] == 0 and v['mask_before'] == v['mask_after'] == desired
                assert policy != 'P' or v['cpu_after'] == 2 * t

    for item in plan['process_order']:
        i, t = item['worker'], item['threads']
        name = f'worker{i}-t{t}.json'
        w = read(name);workers[i, t] = w
        hashes.append(hashlib.sha256((a.source / name).read_bytes()).hexdigest())
        assert w['worker'] == i and w['threads'] == t and w['mode'] == plan['mode']
        assert w['source_sha256'] == plan['first_source_sha256'] and w['environment']['affinity'] == plan['cpus']
        assert w['table_addresses'] is None and len(w['records']) == 48 and len(w['prewarm']) == 6
        assert len(set(w['control']['tids'])) == t and w['control']['healthy'] and w['control']['policy'] == 'U'
        for snapshot in w['control']['snapshots']:
            team(snapshot, w)
        team(w['control']['snapshots'][-1], w, 'U')
        if t == 4:
            saved = w['control']['snapshots'][w['control']['saved_pin_snapshot']]
            assert saved['action'] == 1 and saved['context'] == 'original_pin_previous55'
            assert all(v['previous_mask'] == 0x55 for v in saved['team'])
        else:
            assert w['control']['saved_pin_snapshot'] is None
            assert all(v['scope'] == 'main' for v in w['control']['snapshots'])
        assert w['actual_libgomp_paths_before'] == w['actual_libgomp_paths_after'] and len(w['actual_libgomp_paths_before']) == 1
        assert w['actual_libgomp_paths_before'][0].lower() == str(Path(plan['libgomp']['path']).resolve()).lower()
        assert {(v['model'], v['role']) for v in w['prewarm']} == {(m, r) for m in ('ordinary', 'anchor')
            for r in ('reference', 'previous', 'candidate')}
        handles = {(v['model'], v['role']): v['handle_address'] for v in w['prewarm']}
        for v in w['prewarm']:
            assert v['actual_output_sha256'] == expected[v['model']]
            checks += 1
        assert {(v['block'], v['model'], v['role'], v['boundary']) for v in w['records']} == {
            (b, m, r, edge) for b in range(4) for m in ('ordinary', 'anchor')
            for r in ('reference', 'previous', 'candidate') for edge in ('apply', 'outplace')}
        for row in w['records']:
            assert row['threads'] == t and row['policy'] == plan['policy_orders'][i][row['block']]
            assert row['handle_address'] == handles[row['model'], row['role']]
            assert row['source_address'] == w['source_address'] and row['work_address'] == w['work_address']
            for phase in ('warmup', 'measured', 'control'):
                v = row[phase];n = plan['warmup'] if phase == 'warmup' else plan['repeats']
                assert v['actual_output_sha256'] == expected[row['model']]
                if plan['mode'] == 'quality':
                    assert v['seconds'] == [] and v['quality_apply_calls'] == n
                else:
                    assert len(v['seconds']) == n and all(0 < x < 60 for x in v['seconds'])
                    if row['boundary'] == 'apply':
                        assert len(v['copy_apply_seconds']) == n and all(x >= y
                            for x, y in zip(v['copy_apply_seconds'], v['seconds']))
                for key in ('before_control_index', 'after_control_index'):
                    team(w['control']['snapshots'][v[key]], w, row['policy'])
                checks += 1
        if plan['mode'] == 'quality':
            assert w['setup_wall_seconds_descriptive'] is None
        else:
            assert w['setup_wall_seconds_descriptive'] > 0
    assert checks == 1200 == result['actual_output_sha_checks'] and hashes == result['raw_worker_sha256']
    if plan['mode'] == 'quality':
        assert result['quality_only'] and result['performance_calls'] == 0
        print(json.dumps({'quality_only': True, 'workers': 8, 'actual_sha_checks': checks,
            'all_endpoint_masks_tids_restores_verified': True, 'performance_calls': 0}, ensure_ascii=False))
        return
    indexed = {(i, t): {(v['block'], v['model'], v['role'], v['boundary']): v for v in w['records']}
        for (i, t), w in workers.items()}
    median = lambda row: st.median(row['measured']['seconds'])
    aa = lambda row: st.median(row['control']['seconds']) / median(row)
    close = lambda x, y: math.isclose(x, y, rel_tol=1e-12, abs_tol=1e-14)

    def verify(row, ratios, controls):
        valid = all(.85 <= x <= 1.15 for x in controls)
        assert len(ratios) == 8 and len(controls) == 16 and all(close(x, y) for x, y in zip(row['time_ratios'], ratios))
        assert row['controls'] == controls and row['control_valid'] == valid
        assert close(row['median_time_ratio'], st.median(ratios)) and close(row['worst_throughput_retained'], 1 / max(ratios))
        assert row['grades'] == {str(g): valid and 1 / max(ratios) >= g / 100 for g in plan['grades']}
        assert row['no_obvious_slowdown'] == (valid and st.median(ratios) <= 1.05 and max(ratios) <= 1.10)

    assert len(result['role_pairs']) == 32 and len(result['policy_pairs']) == 24 and len(result['interactions']) == 16
    for row in result['role_pairs']:
        ratios, controls = [], []
        for i in range(4):
            for b, policy in enumerate(plan['policy_orders'][i]):
                if policy != row['policy']:
                    continue
                items = indexed[i, row['threads']]
                c, d = [items[b, row['model'], r, row['boundary']] for r in ('candidate', row['denominator'])]
                ratios.append(median(c) / median(d));controls += [aa(c), aa(d)]
        verify(row, ratios, controls)
    for row in result['policy_pairs']:
        ratios, controls = [], []
        for i in range(4):
            for blocks in ((0, 1), (2, 3)):
                slots = {plan['policy_orders'][i][b]: b for b in blocks}
                items = indexed[i, row['threads']]
                u, p = [items[slots[policy], row['model'], row['role'], row['boundary']] for policy in ('U', 'P')]
                ratios.append(median(p) / median(u));controls += [aa(u), aa(p)]
        verify(row, ratios, controls)
    for row in result['interactions']:
        ds, controls = [], []
        for i in range(4):
            for blocks in ((0, 1), (2, 3)):
                slots = {plan['policy_orders'][i][b]: b for b in blocks}
                items = indexed[i, row['threads']]
                c = {p: items[slots[p], row['model'], 'candidate', row['boundary']] for p in ('U', 'P')}
                d = {p: items[slots[p], row['model'], row['denominator'], row['boundary']] for p in ('U', 'P')}
                ds.append((median(c['P']) / median(d['P'])) / (median(c['U']) / median(d['U'])))
                controls += [aa(c['U']), aa(d['U']), aa(c['P']), aa(d['P'])]
        valid = all(.85 <= x <= 1.15 for x in controls)
        means = [st.median(ds[2 * i:2 * i + 2]) for i in range(4)]
        assert len(ds) == 8 and len(controls) == 32 and row['controls'] == controls and row['control_valid'] == valid
        assert all(close(x, y) for x, y in zip(row['ratios'], ds)) and close(row['median_interaction'], st.median(ds))
        assert row['worker_medians'] == means
        assert row['supported_improvement'] == (valid and st.median(ds) <= .90 and sum(x < 1 for x in means) >= 3)
        assert row['supported_regression'] == (valid and st.median(ds) >= 1.10 and sum(x > 1 for x in means) >= 3)
    counts = {p: {'passed': 0, 'total': 0} for p in ('U', 'P')}
    for w in workers.values():
        for row in w['records']:
            counts[row['policy']]['total'] += 1
            counts[row['policy']]['passed'] += .85 <= aa(row) <= 1.15
    assert counts == result['aa_counts']
    print(json.dumps({'workers': 8, 'actual_sha_checks': checks, 'role_pairs': 32, 'policy_pairs': 24,
        'interactions': 16, 'all_pair_statistics_recomputed': True, 'all_binding_snapshots_verified': True}, ensure_ascii=False))


if __name__ == '__main__':
    main()
