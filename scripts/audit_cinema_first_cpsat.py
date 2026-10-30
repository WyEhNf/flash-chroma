"""只读独立复算CP整数见证、gcd舍入、状态/字节身份与失败门，不追加求解。"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖CP整数审计')
    problem_path = ROOT/'artifacts/cinema-first-cpsat-problem-v1.json'; problem = read(problem_path)
    solution_path = ROOT/'artifacts/cinema-first-cpsat-solution-v1.json'; solution = read(solution_path)
    env_path = ROOT/'artifacts/cinema-first-cpsat-environment-v1.json'; env = read(env_path)
    wheels = read(ROOT/'artifacts/cinema-first-cpsat-wheels-public-v1.json')
    accept = read(ROOT/'artifacts/cinema-first-cpsat-accept-v1/summary.json')
    preflight = read(ROOT/'artifacts/cinema-first-cpsat-preflight-v1.json')
    assert solution['problem_sha256'] == preflight['problem_sha256'] == sha(problem_path)
    assert solution['environment_lock_sha256'] == problem['environment_lock_sha256'] == sha(env_path)
    assert preflight['model_proto_sha256'] == solution['model_proto_sha256'] == sha(ROOT/'artifacts/cinema-first-cpsat-solution-v1-model.pb')
    assert wheels['pass'] and {r['filename']: r['sha256'] for r in wheels['wheels']} == env['wheel_sha256']
    for name, expected in problem['source_sha256'].items():
        if sha(ROOT/name) != expected: raise ValueError('求解实际源字节已变：'+name)
    assert solution['source_sha256'] == sha(ROOT/'scripts/solve_cinema_first_cpsat.py')
    assert solution['feasible'] and solution['status'] == accept['status'] == 'OPTIMAL'
    values = solution['variables']; assert len(values) == len(problem['variables']) == 606
    for value, domain in zip(values, problem['variables']):
        assert type(value) is int and domain['lower'] <= value <= domain['upper']
    for row in problem['rows']:
        divisor = math.gcd(*(abs(coefficient) for _, coefficient in row['raw_terms']))
        assert divisor == row['gcd']
        assert row['lower'] == (row['raw_lower']+divisor-1)//divisor and row['upper'] == row['raw_upper']//divisor
        assert row['terms'] == [[index, coefficient//divisor] for index, coefficient in row['raw_terms']]
        lhs = sum(coefficient*values[index] for index, coefficient in row['raw_terms'])
        assert row['raw_lower'] <= lhs <= row['raw_upper']
        assert row['lower'] <= lhs//divisor <= row['upper']
    for point in problem['points']:
        delta = []
        for c in range(3):
            acc = point['original_acc'][c]+sum(weight*values[index] for index, weight in point['node_terms'][c])
            z = (acc+32768)//65536-point['original_rgb'][c]
            assert z == values[point['z_indices'][c]]; delta.append(z)
        assert delta in point['allowed_deltas']
    failures = [label+'_'+metric for label, after, before in (('uniform', accept['after_uniform'], accept['before_uniform']),
        ('training', accept['after_training'], accept['before_training'])) for metric in ('mean', 'rms', 'p99', 'cvar_1pct') if after[metric] > before[metric]+1e-12]
    if accept['point_cap_violations']: failures.append('fixed_point_caps')
    if accept['after_uniform']['max_squared'] > 49: failures.append('strict_max49')
    assert failures == accept['failures'] and not accept['eligible_for_independent_final_checks']
    assert accept['hotspot_max_squared'] == 34 and accept['point_cap_violations'] == 285
    assert sha(ROOT/'artifacts/cinema-first-cpsat-accept-v1/candidate/model.npz') == accept['candidate_npz_sha256']
    result = {'pass': True, 'source_sha256': sha(__file__), 'variables_checked': len(values), 'q16_integer_rows_checked': len(problem['rows']),
              'allowed_tables_checked': len(problem['points']), 'official_wheel_sha_checked': len(wheels['wheels']),
              'hotspots_feasible': True, 'full_support_accepted': False, 'failures': failures,
              'scope': '只读复算全部整数/gcd/AllowedAssignments、原始模型PB与环境/源字节及完整支撑失败判定；原fresh u64验收已执行，不额外求解/重跑像素或放宽门槛。'}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__': main()
