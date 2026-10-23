"""完整70571点只读误差成本规模普查，超门停止，不建CP或求解。"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import channel_hotspot_support as hs, integer_error_cost as cost, study_provenance
from run_channel_tail_nodes import digest, save
from run_cinema_first_hotspot import squared, train_counts, TOTAL, BLOCK, TRAINING_PIXELS


def tail_threshold(hist):
    n = int(hist.sum()); k = (n+99)//100; high_rank = (99*(n-1)+99)//100
    low_rank, remainder = divmod(99*(n-1), 100)
    cumulative = hist.cumsum(); high = int(np.searchsorted(cumulative, high_rank, side='right'))
    low = int(np.searchsorted(cumulative, low_rank, side='right'))
    if remainder and low != high: raise ValueError('当前提案只保护基线p99恰为单一平方根的目标')
    if high_rank != n-k: raise AssertionError('整数尾大小与上端分位秩关系错误')
    count = int(hist[high+1:].sum())
    if count > n-1-high_rank: raise AssertionError('基线p99自身未过计数充分门')
    return {'threshold_squared': high, 'tail_count': k, 'high_rank': high_rank, 'above_count_cap': n-1-high_rank,
        'baseline_above_count': count}


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--contract', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖唯一完整成本规模普查')
    contract = json.loads(args.contract.read_text(encoding='utf-8'))
    if not contract['pass']: raise ValueError('整数成本有限合同未通过')
    for name, expected in contract['source_sha256'].items():
        if digest(ROOT/name) != expected: raise ValueError('有限合同源已变：'+name)
    risk = ROOT/'artifacts/cinema-first-risk-v1'; prior = ROOT/'artifacts/cinema-first-hotspot-v1'
    run = json.loads((risk/'run.json').read_text(encoding='utf-8')); risk_summary = json.loads((risk/'summary.json').read_text(encoding='utf-8'))
    audit_path = ROOT/'artifacts/cinema-first-risk-independent-v1.json'; audit = json.loads(audit_path.read_text(encoding='utf-8'))
    if not audit['pass'] or audit['summary_sha256'] != digest(risk/'summary.json') or audit['screen_sha256'] != digest(risk/'screen.npz'):
        raise ValueError('不是已认证的完整AABB筛查')
    for name, expected in run['source_sha256'].items():
        if digest(ROOT/name) != expected: raise ValueError('实际AABB筛查源已变：'+name)
    for spec in run['inputs'].values():
        if digest(spec['path']) != spec['sha256']: raise ValueError('原max_first/原数据已变')
    if digest(prior/'suffix.npy') != run['suffix_sha256'] or digest(prior/'support-index.npz') != run['support_index_sha256']:
        raise ValueError('原完整后缀或正支撑已变')
    with np.load(risk/'screen.npz') as data: screen = {name: data[name] for name in data.files}
    keys = screen['keys']; lower = screen['lower_rgb']; upper = screen['upper_rgb']
    if len(keys) != 70571 or len(screen['selected_nodes']) != 86: raise ValueError('不是冻结70571/86设计')
    baseline = np.memmap(run['inputs']['cube']['path'], np.uint8, 'r', shape=(TOTAL, 3))
    gold = np.load(run['inputs']['reference']['path'], mmap_mode='r'); mass = np.load(run['inputs']['mass']['path'], mmap_mode='r')
    total_mass = float(mass.sum(dtype=np.float64)); training, _ = train_counts(mass[keys], total_mass)
    hist, train_hist = np.zeros(51, np.int64), np.zeros(51, np.int64); total_training = 0
    for start in range(0, TOTAL, BLOCK):
        q = squared(baseline[start:start+BLOCK], gold[start:start+BLOCK]); counts, _ = train_counts(mass[start:start+BLOCK], total_mass)
        if q.max() > 50: raise AssertionError('原max_first最大误差改变')
        hist += hs.histogram(q); train_hist += hs.histogram(q, counts); total_training += int(counts.sum())
    if total_training != TRAINING_PIXELS: raise AssertionError('原60图完整整数频数不符')
    origin = squared(baseline[keys], gold[keys]); outside = hist-hs.histogram(origin); outside_train = train_hist-hs.histogram(origin, training)
    if np.any(outside < 0) or np.any(outside_train < 0) or np.flatnonzero(outside)[-1] != 48:
        raise AssertionError('原固定外部域证据不符')
    baseline_summary = json.loads((prior/'summary.json').read_text(encoding='utf-8'))
    if hs.metrics(hist) != baseline_summary['baseline_uniform'] or hs.metrics(train_hist) != baseline_summary['baseline_training']:
        raise AssertionError('当前预算不是原max_first')
    uniform_tail, training_tail = tail_threshold(hist), tail_threshold(train_hist)
    qt_u, qt_t = uniform_tail['threshold_squared'], training_tail['threshold_squared']
    pools = np.array([[cost.costs(a, b, qt_u, qt_t) for b in range(51)] for a in range(50)], dtype=np.int64)
    danger = screen['maximum_squared'] > 49
    retained = danger | (screen['minimum_squared'] != origin) | (screen['maximum_squared'] != origin)
    distinct = np.zeros(len(keys), np.uint8); safe_rows = np.zeros(len(keys), np.uint8)
    selectors = q_variables = queries = 0; constant_cost = [0]*8; selector_abs_sum = [0]*8; coefficient_max = [0]*8
    suffix = np.load(prior/'suffix.npy', mmap_mode='r'); max_chunk_queries = 0; zero_mass_retained = 0
    visible_chunk_payload_peak = 0
    for start in range(0, len(keys), 512):
        stop = min(start+512, len(keys)); lo = lower[start:stop].astype(np.int64)
        width = upper[start:stop].astype(np.int64)-lo+1; counts = np.prod(width, axis=1, dtype=np.int64)
        begins = np.r_[0, np.cumsum(counts, dtype=np.int64)]
        rows = np.repeat(np.arange(stop-start), counts); local = np.arange(int(begins[-1]))-np.repeat(begins[:-1], counts)
        blue = local%width[rows, 2]; divided = local//width[rows, 2]
        rgb = (lo[rows]+np.column_stack((divided//width[rows, 1], divided%width[rows, 1], blue))).astype(np.uint8)
        error = suffix[hs.key(rgb)].astype(np.int32)-gold[keys[start:stop]][rows].astype(np.int32)
        square = np.sum(error*error, axis=1, dtype=np.int32); safe = square <= 49
        visible_chunk_payload_peak = max(visible_chunk_payload_peak, sum(v.nbytes for v in
            (lo, width, counts, begins, rows, local, blue, divided, rgb, error, square, safe)))
        np.testing.assert_array_equal(np.minimum.reduceat(square, begins[:-1]), screen['minimum_squared'][start:stop])
        np.testing.assert_array_equal(np.maximum.reduceat(square, begins[:-1]), screen['maximum_squared'][start:stop])
        np.testing.assert_array_equal(np.add.reduceat(safe.astype(np.int64), begins[:-1]), screen['safe_count'][start:stop])
        queries += len(rgb); max_chunk_queries = max(max_chunk_queries, len(rgb))
        for j in range(stop-start):
            index = start+j; options = np.unique(square[begins[j]:begins[j+1]][safe[begins[j]:begins[j+1]]])
            if not len(options): raise AssertionError('已有筛查无空表，完整成本普查却空表')
            distinct[index] = len(options); safe_rows[index] = int(np.count_nonzero(safe[begins[j]:begins[j+1]]))
            if not retained[index]:
                if danger[index] or options.tolist() != [int(origin[index])] or np.any(pools[int(options[0]), int(origin[index])] != 0):
                    raise AssertionError('被删点没有严格恒零成本')
                continue
            if training[index] == 0: zero_mass_retained += 1
            multiple = len(options) > 1; q_variables += int(multiple); selectors += len(options) if multiple else 0
            weight = int(training[index]); old = int(origin[index])
            for q in options:
                mean, rms, p99_u, p99_t, cvar_u, cvar_t = (int(v) for v in pools[int(q), old])
                coefficients = (mean, weight*mean, rms, weight*rms, p99_u, weight*p99_t, cvar_u, weight*cvar_t)
                for b, coefficient in enumerate(coefficients):
                    if multiple: selector_abs_sum[b] += abs(coefficient)
                    else: constant_cost[b] += coefficient
                    coefficient_max[b] = max(coefficient_max[b], abs(coefficient))
    if queries != 1187079 or queries != risk_summary['aabb_queries_first_pass']: raise AssertionError('未完整覆盖唯一成本普查')
    safe_table_rows = int(safe_rows[retained].sum(dtype=np.int64)); retained_count = int(np.count_nonzero(retained))
    plan = json.loads((ROOT/'experiments/p16-cinema-first-cost-census-v1.json').read_text(encoding='utf-8'))
    gate = retained_count <= plan['gate']['retained_points_max'] and safe_table_rows <= plan['gate']['safe_table_rows_max'] and selectors <= plan['gate']['selectors_max']
    bound = [a+abs(c) for a, c in zip(selector_abs_sum, constant_cost)]
    if any(v > (1 << 62)-1 for v in bound+coefficient_max): raise AssertionError('实际成本系数/绝对总界溢出')
    args.output.mkdir(parents=True)
    source_names = set(run['source_sha256']) | set(contract['source_sha256'])
    save(args.output/'run.json', {'source_sha256': {name: digest(ROOT/name) for name in sorted(source_names)},
        'inputs': run['inputs'], 'contract_sha256': digest(args.contract), 'risk_run_sha256': digest(risk/'run.json'),
        'risk_screen_sha256': digest(risk/'screen.npz'), 'environment': study_provenance.environment_fingerprint(), 'plan': plan,
        'cp_model_built': False, 'cp_solver_called': False})
    np.savez_compressed(args.output/'census.npz', keys=keys, original_squared=origin, training_counts=training,
        retained=retained, safe_table_rows=safe_rows, distinct_safe_squared=distinct, cost_pool=pools,
        baseline_hist=hist, baseline_training_hist=train_hist, outside_hist=outside, outside_training_hist=outside_train)
    budgets = ('uniform_mean', 'training_mean', 'uniform_rms', 'training_rms', 'uniform_p99', 'training_p99', 'uniform_cvar', 'training_cvar')
    record = {'complete_support_rows': len(keys), 'complete_aabb_states': queries, 'retained_points': retained_count,
        'omitted_universally_safe_zero_cost_points': len(keys)-retained_count, 'safe_table_rows': safe_table_rows,
        'cost_selectors': selectors, 'q_variables': q_variables, 'predicted_variables_without_abs': 258+3*retained_count+q_variables+selectors,
        'predicted_rounding_rows': 3*retained_count, 'within_frozen_resource_gate': bool(gate),
        'uniform_tail': uniform_tail, 'training_tail': training_tail, 'outside_support_max_squared': 48,
        'uniform_before': hs.metrics(hist), 'training_before': hs.metrics(train_hist),
        'retained_zero_training_mass_points': zero_mass_retained, 'maximum_chunk_queries': max_chunk_queries,
        'saved_array_payload_bytes': sum(v.nbytes for v in (keys, origin, training, retained, safe_rows, distinct, pools, hist, train_hist, outside, outside_train)),
        'input_screen_array_payload_bytes': sum(v.nbytes for v in screen.values()),
        'visible_chunk_array_payload_peak_bytes': visible_chunk_payload_peak,
        'mapped_input_payload_bytes': {name: value.nbytes for name, value in (('baseline', baseline), ('reference', gold), ('mass', mass), ('suffix', suffix))},
        'memory_scope': '数组有效载荷及当前可见分块数组和；不含解释器/分配器、已释放表达式暂态或OS页缓存，不是进程RSS峰值。未来CP仍须独立资源监测。',
        'coefficient_int64_audit': {name: {'maximum_coefficient_abs': coefficient_max[i], 'constant_cost': constant_cost[i],
            'selector_coefficient_abs_sum': selector_abs_sum[i], 'total_abs_bound': bound[i], 'pass': True} for i, name in enumerate(budgets)},
        'cp_model_built': False, 'cp_solver_called': False,
        'scope': '唯一完整只读成本规模普查；门内也不建CP，超门STOP不删样、不调预算；没有新候选、RSS或速度结论。'}
    save(args.output/'summary.json', record)
    print({k: record[k] for k in ('retained_points', 'safe_table_rows', 'cost_selectors', 'within_frozen_resource_gate', 'cp_model_built')}, flush=True)


if __name__ == '__main__': main()
