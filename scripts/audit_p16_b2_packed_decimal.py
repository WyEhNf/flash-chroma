"""99事后50位十进制独立复算126冷热统计集；不加载DLL或重测。"""
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
    read = lambda name: json.loads((a.source / name).read_text(encoding='utf-8'), parse_float=Decimal)
    plan, result = read('executed-plan.json'), read('results.json')
    workers = [read(f'worker{i}.json') for i in range(4)]
    hot = [{(r['model'], r['images'], r['role'], r['threads'], r['boundary']): r for r in w['records']} for w in workers]
    cold = [{(r['model'], r['images'], r['role']): r for r in w['cold_records']} for w in workers]
    differences, sets = [], 0

    def median(values):
        values = sorted(values)
        n = len(values)
        return values[n // 2] if n % 2 else (values[n // 2 - 1] + values[n // 2]) / 2

    def check(x, y):
        difference = abs(x - y)
        assert difference < Decimal('1e-14'), (str(x), str(y), str(difference))
        differences.append(difference)

    def verify(row, measured, controls):
        nonlocal sets
        ratios = [candidate / denominator for candidate, denominator in measured]
        valid = all(Decimal('.85') <= v <= Decimal('1.15') for v in controls)
        for x, y in zip(ratios, row['time_ratios']):
            check(x, y)
        for x, y in zip(controls, row['controls']):
            check(x, y)
        retained = 1 / max(ratios)
        check(median(ratios), row['median_time_ratio'])
        check(retained, row['worst_throughput_retained'])
        assert row['control_valid'] == valid
        assert row['grades'] == {str(g): valid and retained >= Decimal(g) / 100 for g in plan['grades']}
        assert row['no_obvious_slowdown'] == (valid and median(ratios) <= Decimal('1.05') and max(ratios) <= Decimal('1.10'))
        sets += 1

    for row in result['hot']:
        measured, controls = [], []
        for worker in hot:
            pair = {role: worker[row['model'], row['images'], role, row['threads'], row['boundary']]
                for role in (row['denominator'], 'candidate')}
            values = {role: median(item['measured']['seconds']) for role, item in pair.items()}
            measured.append((values['candidate'], values[row['denominator']]))
            controls += [median(pair[role]['control']['seconds']) / values[role] for role in (row['denominator'], 'candidate')]
        verify(row, measured, controls)
    for row in result['cold']:
        for metric, item in row['metrics'].items():
            measured, controls = [], []
            for worker in cold:
                pair = {role: worker[row['model'], row['images'], role] for role in (row['denominator'], 'candidate')}
                values = {role: median(g[metric] for g in record['samples']) for role, record in pair.items()}
                measured.append((values['candidate'], values[row['denominator']]))
                controls += [median(g[metric] for g in pair[role]['control']) / values[role]
                    for role in (row['denominator'], 'candidate')]
            verify(item, measured, controls)
    assert sets == 126 and len(differences) == 1764
    receipt = {'precision_digits': 50, 'statistic_sets': sets, 'scalar_checks': len(differences),
        'maximum_absolute_difference': str(max(differences)), 'tolerance': '1e-14',
        'all_controls_grades_no_obvious_recomputed': True, 'performance_calls': 0,
        'postprocessing_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'results_sha256': hashlib.sha256((a.source / 'results.json').read_bytes()).hexdigest()}
    output = a.source / 'decimal-audit.json'
    if output.exists():
        raise FileExistsError('99十进制原始回执不覆盖')
    output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == '__main__':
    main()
