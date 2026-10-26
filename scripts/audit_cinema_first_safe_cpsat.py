"""只读复算完整危险表整数见证、原八预算及直方图，不再求解或插值。"""
from __future__ import annotations
import argparse
import bisect
import hashlib
import itertools
import json
import math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8'))


def metrics(hist):
    if any(v < 0 for v in hist) or sum(hist) <= 0: raise AssertionError('非法整数直方图')
    n = sum(hist); cumulative = list(itertools.accumulate(hist)); rank, remainder = divmod(99*(n-1), 100)
    lo = bisect.bisect_right(cumulative, rank); hi = bisect.bisect_right(cumulative, rank+int(remainder != 0))
    tail = (n+99)//100; left = tail; terms = []
    for i in range(len(hist)-1, -1, -1):
        count = min(left, hist[i]); terms.append(count*math.sqrt(i)); left -= count
        if not left: break
    return {'n': n, 'mean': math.fsum(v*math.sqrt(i) for i, v in enumerate(hist))/n,
        'rms': math.sqrt(sum(v*i for i, v in enumerate(hist))/n),
        'p99': math.sqrt(lo)+remainder/100*(math.sqrt(hi)-math.sqrt(lo)),
        'max_squared': max(i for i, v in enumerate(hist) if v), 'cvar_1pct': math.fsum(terms)/tail}


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖完整危险表整数审计')
    problem_path = ROOT/'artifacts/cinema-first-safe-cpsat-problem-v2.json'; problem = read(problem_path)
    solution_path = ROOT/'artifacts/cinema-first-safe-cpsat-solution-v2.json'; solution = read(solution_path)
    preflight_path = ROOT/'artifacts/cinema-first-safe-cpsat-preflight-v2.json'; preflight = read(preflight_path)
    accept_folder = ROOT/'artifacts/cinema-first-safe-cpsat-accept-v2'; accept = read(accept_folder/'summary.json')
    assert problem['preflight_revision'] == 2
    assert solution['problem_sha256'] == preflight['problem_sha256'] == sha(problem_path)
    assert solution['preflight_sha256'] == sha(preflight_path)
    assert solution['model_proto_sha256'] == preflight['model_proto_sha256'] == sha(ROOT/'artifacts/cinema-first-safe-cpsat-solution-v2-model.pb')
    assert solution['environment_lock_sha256'] == problem['environment_lock_sha256'] == sha(ROOT/'artifacts/cinema-first-cpsat-environment-v1.json')
    for name, expected in {**problem['source_sha256'], **problem['frozen_risk_sha256']}.items():
        if sha(ROOT/name) != expected: raise ValueError('冻结原件已变：'+name)
    assert solution['source_sha256'] == sha(ROOT/'scripts/solve_cinema_first_safe_cpsat.py')
    rows_checked = tables_checked = 0; histogram_checked = False; failures = []
    if solution['feasible']:
        assert solution['status'] in ('FEASIBLE', 'OPTIMAL') and solution['status'] == accept['status']
        values = solution['variables']; assert len(values) == len(problem['variables']) == 6930
        for value, domain in zip(values, problem['variables']):
            assert type(value) is int and domain['lower'] <= value <= domain['upper']
        count = problem['n_node_variables']; assert count == 258
        assert solution['abs_variables'] == [abs(v) for v in values[:count]]
        assert solution['l1_objective_integer'] == sum(solution['abs_variables'])
        for row in problem['rows']:
            divisor = math.gcd(*(abs(c) for _, c in row['raw_terms']))
            assert divisor == row['gcd'] and row['lower'] == (row['raw_lower']+divisor-1)//divisor
            assert row['upper'] == row['raw_upper']//divisor
            assert row['terms'] == [[i, c//divisor] for i, c in row['raw_terms']]
            lhs = sum(c*values[i] for i, c in row['raw_terms'])
            assert row['raw_lower'] <= lhs <= row['raw_upper'] and row['lower'] <= lhs//divisor <= row['upper']
            rows_checked += 1
        for point in problem['points']:
            delta = []
            for c in range(3):
                acc = point['original_acc'][c]+sum(weight*values[i] for i, weight in point['node_terms'][c])
                z = (acc+32768)//65536-point['original_rgb'][c]
                assert z == values[point['z_indices'][c]]; delta.append(z)
            assert delta in point['allowed_deltas']; tables_checked += 1
        import numpy as np
        with np.load(accept_folder/'replay.npz') as data: replay = {k: data[k] for k in data.files}
        keys, first, square, training = [replay[k] for k in ('keys', 'first_rgb', 'squared', 'training_counts')]
        suffix = np.load(ROOT/'artifacts/cinema-first-hotspot-v1/suffix.npy', mmap_mode='r')
        gold = np.load(problem['inputs']['reference']['path'], mmap_mode='r')
        baseline = np.memmap(problem['inputs']['cube']['path'], dtype=np.uint8, mode='r', shape=(16777216, 3))
        first_key = (first[:, 0].astype(np.uint32)<<16)|(first[:, 1].astype(np.uint32)<<8)|first[:, 2]
        error = suffix[first_key].astype(np.int64)-gold[keys].astype(np.int64)
        np.testing.assert_array_equal(np.sum(error*error, axis=1), square)
        old_error = baseline[keys].astype(np.int64)-gold[keys].astype(np.int64); old_square = np.sum(old_error*old_error, axis=1)
        old_hist = [int(v) for v in replay['before_hist']]; old_train = [int(v) for v in replay['before_training_hist']]
        after_hist, after_train = old_hist.copy(), old_train.copy()
        assert len(keys) == 70571 and len(first) == len(square) == len(training) == len(keys)
        assert all(type(int(v)) is int and v >= 0 for v in training)
        for before, after, mass in zip(old_square, square, training):
            a, b, w = int(before), int(after), int(mass); after_hist[a] -= 1; after_hist[b] += 1
            after_train[a] -= w; after_train[b] += w
        assert after_hist == replay['after_hist'].tolist() and after_train == replay['after_training_hist'].tolist()
        for name, hist in (('before_uniform', old_hist), ('before_training', old_train), ('after_uniform', after_hist), ('after_training', after_train)):
            actual = metrics(hist)
            for key, value in actual.items(): assert abs(value-accept[name][key]) <= 1e-12, (name, key)
        assert sum(old_hist) == sum(after_hist) == 16777216 and sum(old_train) == sum(after_train) == 47185920
        assert max(int(v) for v in square) == accept['full70571_max_squared'] <= 49
        assert accept['point_cap_violations'] == 0
        failures = [label+'_'+metric for label, after, before in (('uniform', accept['after_uniform'], accept['before_uniform']),
            ('training', accept['after_training'], accept['before_training'])) for metric in ('mean', 'rms', 'p99', 'cvar_1pct')
            if after[metric] > before[metric]+1e-12]
        if accept['after_uniform']['max_squared'] > 49: failures.append('strict_max49')
        assert failures == accept['failures'] and accept['eligible_for_independent_final_checks'] == (not failures)
        assert sha(accept_folder/'candidate/model.npz') == accept['candidate_npz_sha256']; histogram_checked = True
    else:
        assert not accept['feasible'] and not accept['eligible_for_independent_final_checks']
    result = {'pass': True, 'source_sha256': sha(__file__), 'q16_rows_checked': rows_checked, 'tables_checked': tables_checked,
        'integer_histograms_checked': histogram_checked, 'status': solution['status'], 'failures': failures,
        'full_support_accepted': accept['eligible_for_independent_final_checks'],
        'scope': '只读核全部整数/gcd/表/abs及完整直方图预算；复用一次freshu64回放，不新增求解或节点插值。'}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print({'pass': True, 'rows': rows_checked, 'tables': tables_checked, 'accepted': result['full_support_accepted']}, flush=True)


if __name__ == '__main__': main()
