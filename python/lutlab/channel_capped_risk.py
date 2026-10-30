"""任意整数cap的完整AABB风险统计与固定直方图的严格整数根上界。"""
from __future__ import annotations
import itertools
import math
import numpy as np
from . import channel_hotspot_support as hs
SCALE = 1 << 32
SAFE = (1 << 62)-1


def enumerate_stats(lower, upper, gold, lookup, cap):
    if type(cap) is not int or cap < 0 or np.any(upper < lower) or np.any(upper.astype(np.int16)-lower > 4):
        raise ValueError('需要合法cap与每轴≤5值的RGB8盒')
    minimum = np.full(len(lower), 195076, np.int32); maximum = np.zeros(len(lower), np.int32)
    count = np.zeros(len(lower), np.uint8); safe = np.zeros(len(lower), np.uint8)
    safe_maximum = np.full(len(lower), -1, np.int32); span = upper.astype(np.int16)-lower
    for offset in itertools.product(range(5), repeat=3):
        rows = np.flatnonzero(np.all(span >= np.array(offset, np.int16), axis=1))
        if not len(rows): continue
        rgb = (lower[rows].astype(np.int16)+offset).astype(np.uint8)
        error = lookup(rgb).astype(np.int32)-gold[rows].astype(np.int32); q = np.sum(error*error, axis=1, dtype=np.int32)
        minimum[rows] = np.minimum(minimum[rows], q); maximum[rows] = np.maximum(maximum[rows], q); count[rows] += 1
        good = q <= cap; safe[rows] += good.astype(np.uint8)
        safe_maximum[rows[good]] = np.maximum(safe_maximum[rows[good]], q[good])
    np.testing.assert_array_equal(count.astype(np.int32), np.prod(span+1, axis=1, dtype=np.int32))
    return minimum, maximum, count, safe, safe_maximum


def collect_allowed(lower, upper, gold, lookup, cap):
    rows_parts, rgb_parts = [], []; span = upper.astype(np.int16)-lower
    for offset in itertools.product(range(5), repeat=3):
        rows = np.flatnonzero(np.all(span >= np.array(offset, np.int16), axis=1))
        if not len(rows): continue
        rgb = (lower[rows].astype(np.int16)+offset).astype(np.uint8)
        error = lookup(rgb).astype(np.int32)-gold[rows].astype(np.int32)
        good = np.sum(error*error, axis=1, dtype=np.int32) <= cap
        rows_parts.append(rows[good].astype(np.uint32)); rgb_parts.append(rgb[good])
    rows = np.concatenate(rows_parts) if rows_parts else np.empty(0, np.uint32)
    rgb = np.concatenate(rgb_parts) if rgb_parts else np.empty((0, 3), np.uint8)
    order = np.lexsort((hs.key(rgb), rows)); rows, rgb = rows[order], rgb[order]
    return np.r_[0, np.cumsum(np.bincount(rows, minlength=len(lower)), dtype=np.int64)], rgb


def root_interval(hist):
    lower = upper = 0
    for q in np.flatnonzero(hist):
        number = int(hist[q]); value = int(q)*SCALE*SCALE; floor = math.isqrt(value)
        lower += number*floor; upper += number*(floor+int(floor*floor != value))
    if not 0 <= lower <= upper <= SAFE: raise OverflowError('根和证书超保守int64界')
    return lower, upper


def radical_signature(hist):
    terms = {}
    for q in np.flatnonzero(hist):
        if q == 0: continue
        factor = next(v for v in range(math.isqrt(int(q)), 0, -1) if int(q) % (v*v) == 0)
        base = int(q)//(factor*factor); terms[base] = terms.get(base, 0)+int(hist[q])*factor
    return terms


def tail_histogram(hist):
    remaining = (int(hist.sum())+99)//100; result = np.zeros(len(hist), np.int64)
    for q in np.flatnonzero(hist)[::-1]:
        take = min(remaining, int(hist[q])); result[q] = take; remaining -= take
        if remaining == 0: break
    if remaining: raise AssertionError('CVaR尾质量不足')
    return result


def percentile_histogram(hist):
    n = int(hist.sum()); lo, remainder = divmod(99*(n-1), 100)
    cumulative = hist.cumsum(); a, b = [int(np.searchsorted(cumulative, v, side='right')) for v in (lo, lo+int(remainder != 0))]
    result = np.zeros(len(hist), np.int64); result[a] += 100-remainder; result[b] += remainder
    return result, {'lower_squared': a, 'upper_squared': b, 'remainder_percent': remainder}


def root_comparison(worst, baseline):
    lo_w, hi_w = root_interval(worst); lo_b, hi_b = root_interval(baseline)
    equal = radical_signature(worst) == radical_signature(baseline)
    protected = equal or hi_w <= lo_b
    return {'automatically_protected': protected, 'exact_equal_radical_sum': equal,
        'worst_lower_scaled': lo_w, 'worst_upper_scaled': hi_w,
        'baseline_lower_scaled': lo_b, 'baseline_upper_scaled': hi_b,
        'strict_bound_status': 'protected' if protected else ('upper_bound_exceeds' if lo_w > hi_b else 'root_interval_unresolved')}


def compare_histograms(worst, baseline):
    if int(worst.sum()) != int(baseline.sum()) or int(worst.sum()) <= 0: raise ValueError('两完整直方图质量必须相等且为正')
    w, b = hs.metrics(worst), hs.metrics(baseline)
    sq_w = sum(int(n)*i for i, n in enumerate(worst)); sq_b = sum(int(n)*i for i, n in enumerate(baseline))
    p_w, ranks_w = percentile_histogram(worst); p_b, ranks_b = percentile_histogram(baseline)
    certificates = {'mean': root_comparison(worst, baseline),
        'rms': {'automatically_protected': sq_w <= sq_b, 'worst_sum_squared': sq_w, 'baseline_sum_squared': sq_b},
        'p99': {**root_comparison(p_w, p_b), 'worst_ranks': ranks_w, 'baseline_ranks': ranks_b},
        'max': {'automatically_protected': w['max_squared'] <= b['max_squared'],
            'worst_squared': w['max_squared'], 'baseline_squared': b['max_squared']},
        'cvar_1pct': root_comparison(tail_histogram(worst), tail_histogram(baseline))}
    return {'worst_safe_bound_metrics': w, 'baseline_metrics': b, 'root_scale': SCALE, 'certificates': certificates,
        'all_five_automatically_protected': all(v['automatically_protected'] for v in certificates.values()),
        'user_mean_p99_max_automatically_protected': all(certificates[k]['automatically_protected'] for k in ('mean', 'p99', 'max'))}
