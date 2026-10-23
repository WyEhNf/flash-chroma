"""96原始数组的50位十进制离线复算；不加载DLL、不修改执行源。"""
import argparse
from decimal import Decimal, getcontext
import hashlib
import json
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    a = p.parse_args()
    getcontext().prec = 50
    read = lambda f: json.loads(f.read_text(encoding='utf-8'), parse_float=Decimal)
    result = read(a.source / 'results.json')
    plan = read(a.source / 'executed-plan.json')
    workers = {(i, t): read(a.source / f'worker{i}-t{t}.json') for i in range(4) for t in (1, 4)}
    rows = {(i, t): {(r['block'], r['model'], r['role'], r['boundary']): r for r in w['records']}
        for (i, t), w in workers.items()}
    errors = []

    def median(values):
        s = sorted(values)
        n = len(s)
        return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2

    def value(row):
        return median(row['measured']['seconds'])

    def aa(row):
        return median(row['control']['seconds']) / value(row)

    def check(x, y):
        difference = abs(x - y)
        errors.append(difference)
        assert difference < Decimal('1e-14'), (str(x), str(y), str(difference))

    for kind in ('role_pairs', 'policy_pairs', 'interactions'):
        for row in result[kind]:
            ratios, controls = [], []
            for i in range(4):
                items = rows[i, row['threads']]
                if kind == 'role_pairs':
                    for b, policy in enumerate(plan['policy_orders'][i]):
                        if policy == row['policy']:
                            c, d = [items[b, row['model'], r, row['boundary']]
                                for r in ('candidate', row['denominator'])]
                            ratios.append(value(c) / value(d))
                            controls += [aa(c), aa(d)]
                else:
                    for blocks in ((0, 1), (2, 3)):
                        slots = {plan['policy_orders'][i][b]: b for b in blocks}
                        if kind == 'policy_pairs':
                            u, pin = [items[slots[q], row['model'], row['role'], row['boundary']]
                                for q in ('U', 'P')]
                            ratios.append(value(pin) / value(u))
                            controls += [aa(u), aa(pin)]
                        else:
                            c = {q: items[slots[q], row['model'], 'candidate', row['boundary']] for q in ('U', 'P')}
                            d = {q: items[slots[q], row['model'], row['denominator'], row['boundary']] for q in ('U', 'P')}
                            ratios.append((value(c['P']) / value(d['P'])) / (value(c['U']) / value(d['U'])))
                            controls += [aa(c['U']), aa(d['U']), aa(c['P']), aa(d['P'])]
            assert len(ratios) == 8
            for x, y in zip(ratios, row['ratios' if kind == 'interactions' else 'time_ratios']):
                check(x, y)
            for x, y in zip(controls, row['controls']):
                check(x, y)
            valid = all(Decimal('.85') <= x <= Decimal('1.15') for x in controls)
            assert valid == row['control_valid']
            if kind == 'interactions':
                check(median(ratios), row['median_interaction'])
                means = [median(ratios[2 * i:2 * i + 2]) for i in range(4)]
                for x, y in zip(means, row['worker_medians']):
                    check(x, y)
                assert row['supported_improvement'] == (valid and median(ratios) <= Decimal('.90') and sum(x < 1 for x in means) >= 3)
                assert row['supported_regression'] == (valid and median(ratios) >= Decimal('1.10') and sum(x > 1 for x in means) >= 3)
            else:
                check(median(ratios), row['median_time_ratio'])
                retained = 1 / max(ratios)
                check(retained, row['worst_throughput_retained'])
                assert row['grades'] == {str(g): valid and retained >= Decimal(g) / 100 for g in plan['grades']}
                assert row['no_obvious_slowdown'] == (valid and median(ratios) <= Decimal('1.05') and max(ratios) <= Decimal('1.10'))
    receipt = {'precision_digits': 50, 'statistic_sets': 72, 'scalar_checks': len(errors),
        'maximum_absolute_difference': str(max(errors)), 'tolerance': '1e-14',
        'all_grades_controls_interests_recomputed': True, 'performance_calls': 0,
        'audit_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'performance_results_sha256': hashlib.sha256((a.source / 'results.json').read_bytes()).hexdigest()}
    output = a.source / 'decimal-audit.json'
    if output.exists():
        raise FileExistsError('96十进制复算原件不覆盖')
    output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == '__main__':
    main()
