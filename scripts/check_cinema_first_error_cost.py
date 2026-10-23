"""完整有限整数根差矩阵及加权mean/RMS/p99/CVaR预算保护合同。"""
from __future__ import annotations
import argparse
import itertools
import math
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
from lutlab import integer_error_cost as cost


def radical_sign(terms):
    """独立按平方因子归一，再用有理根区间判代数和符号。"""
    normalized = {}
    for q, coefficient in terms:
        if q == 0 or coefficient == 0: continue
        factor = next(v for v in range(math.isqrt(q), 0, -1) if q%(v*v) == 0)
        root = q//(factor*factor); normalized[root] = normalized.get(root, 0)+coefficient*factor
    normalized = {q: v for q, v in normalized.items() if v}
    if not normalized: return 0
    for bits in (16, 32, 64, 128, 256):
        denominator = 1 << bits; lower = upper = 0
        for q, coefficient in normalized.items():
            target = q*denominator**2; a = math.isqrt(target); b = a+int(a*a != target)
            lower += coefficient*(a if coefficient > 0 else b)
            upper += coefficient*(b if coefficient > 0 else a)
        if lower > 0: return 1
        if upper < 0: return -1
    raise ArithmeticError('有限代数和符号未被证明，禁止浮点推测')


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖直接误差成本有限合同')
    from run_channel_tail_nodes import digest, save
    matrix = {}
    for a, b in itertools.product(range(51), repeat=2):
        interval = cost.sqrt_difference_interval(a, b); square = cost.sqrt_difference_squared(a, b)
        if interval != square: raise AssertionError('两种纯整数ceil不等')
        if cost.compare_scaled_difference(a, b, interval) > 0 or cost.compare_scaled_difference(a, b, interval-1) <= 0:
            raise AssertionError('ceil整数边界不成立')
        if a == b and interval != 0: raise AssertionError('零扰动出现取整税')
        matrix[a, b] = interval
    excess = {}
    for t, a, b in itertools.product(range(51), repeat=3):
        first = cost.excess_difference(a, b, t); second = cost.excess_difference(a, b, t, method=cost.sqrt_difference_squared)
        if first != second: raise AssertionError('CVaR两方法成本不等')
        terms = ([] if a <= t else [(a, cost.SCALE), (t, -cost.SCALE)])
        terms += ([] if b <= t else [(b, -cost.SCALE), (t, cost.SCALE)])
        if radical_sign(terms+[(1, -first)]) > 0 or radical_sign(terms+[(1, 1-first)]) <= 0:
            raise AssertionError('独立代数和未证CVaR成本ceil')
        if a == b and first != 0: raise AssertionError('CVaR零扰动成本非零')
        excess[t, a, b] = first
    for scale in (1, 3, 8):
        for a, b in itertools.product((0, 1, 2, 4, 9, 50), repeat=2):
            if cost.sqrt_difference_interval(a, b, scale) != cost.sqrt_difference_squared(a, b, scale):
                raise AssertionError('小尺度正负ceil边界不等')
    values = (0, 2, 9, 12, 50); vectors = list(itertools.product(values, repeat=3))
    guards = {'mean': 0, 'rms': 0, 'p99': 0, 'cvar': 0}; pairs = 0
    for weights in ((1, 1, 99), (1, 2, 198), (0, 1, 100)):
        n = sum(weights); k = (n+99)//100; high_rank = (99*(n-1)+99)//100
        for old, new in itertools.product(vectors, repeat=2):
            old_full = sorted(q for q, w in zip(old, weights) for _ in range(w))
            new_full = sorted(q for q, w in zip(new, weights) for _ in range(w))
            threshold = old_full[-k]
            if threshold != old_full[high_rank]: raise AssertionError('所选有限N不满足精确p99秩合同')
            terms = [(a, w) for a, w in zip(new, weights)]+[(b, -w) for b, w in zip(old, weights)]
            if sum(w*matrix[a, b] for a, b, w in zip(new, old, weights)) <= 0:
                if radical_sign(terms) > 0: raise AssertionError('保守mean退款不能保证真实mean')
                guards['mean'] += 1
            square_delta = sum(w*(a-b) for a, b, w in zip(new, old, weights))
            if (square_delta <= 0) != (sum(new_full) <= sum(old_full)): raise AssertionError('平方和/RMS预算不等价')
            guards['rms'] += 1
            if sum(w*int(a > threshold) for a, w in zip(new, weights)) <= n-1-high_rank:
                if new_full[high_rank] > threshold: raise AssertionError('p99计数充分条件未保护上端秩')
                guards['p99'] += 1
            old_tail = [(q, 1) for q in old_full[-k:]]; new_tail = [(q, 1) for q in new_full[-k:]]
            origin_excess = [(threshold, k)]
            bound_excess = [(threshold, k)]
            for q, w in zip(old, weights):
                if q > threshold: origin_excess.extend(((q, w), (threshold, -w)))
            for q, w in zip(new, weights):
                if q > threshold: bound_excess.extend(((q, w), (threshold, -w)))
            if radical_sign(origin_excess+[(q, -w) for q, w in old_tail]) != 0:
                raise AssertionError('基线固定阈值未取到CVaR等式')
            if radical_sign(bound_excess+[(q, -w) for q, w in new_tail]) < 0:
                raise AssertionError('固定阈值表达式不是候选CVaR上界')
            if sum(w*excess[threshold, a, b] for a, b, w in zip(new, old, weights)) <= 0:
                if radical_sign(new_tail+[(q, -w) for q, w in old_tail]) > 0:
                    raise AssertionError('CVaR保守退款不能保证真实尾均值')
                guards['cvar'] += 1
            pairs += 1
    names = ['python/lutlab/integer_error_cost.py', 'scripts/check_cinema_first_error_cost.py',
        'scripts/census_cinema_first_error_cost.py', 'experiments/p16-cinema-first-cost-census-v1.json']
    save(args.output, {'pass': True, 'sqrt_matrix_entries': len(matrix), 'cvar_matrix_entries': len(excess),
        'finite_weighted_pairs': pairs, 'guard_cases': guards, 'scale': cost.SCALE,
        'source_sha256': {name: digest(ROOT/name) for name in names},
        'scope': '0..50完整根差/CVaR整数成本与有限原始加权全枚举合同，不建真实CP或求解器。'})
    print({'pass': True, 'matrix': len(matrix), 'cvar': len(excess), 'weighted_pairs': pairs}, flush=True)


if __name__ == '__main__': main()
