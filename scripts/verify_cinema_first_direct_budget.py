"""原环境fresh整数重放窄域/旧完整支撑，独立核真实误差与八项预算。"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import channel_coordinates as cc, channel_hotspot_support as hs, io, study_provenance
from run_channel_tail_nodes import digest, load_model, save
from run_cinema_first_hotspot import squared, train_counts, TOTAL
from verify_channel_coordinates import integer_oracle
from cinema_first_direct_budget_model import BUDGETS, validate_direct_problem
from prepare_cinema_first_direct_budget import coefficients


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--problem', type=Path, required=True)
    p.add_argument('--solution', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖直接预算唯一完整支撑验解')
    problem = json.loads(args.problem.read_text(encoding='utf-8')); solution = json.loads(args.solution.read_text(encoding='utf-8'))
    validate_direct_problem(problem)
    if solution['problem_sha256'] != digest(args.problem) or not solution['feasible'] or solution['status'] not in ('FEASIBLE', 'OPTIMAL'):
        raise ValueError('只允许验此冻结问题的实际整数incumbent')
    for name, h in {**problem['source_sha256'], **problem['frozen_evidence_sha256']}.items():
        if digest(ROOT/name) != h: raise ValueError('直接预算实际源或完整成本原件已变：'+name)
    for spec in [*problem['inputs'].values(), problem['witness']]:
        if digest(spec['path']) != spec['sha256']: raise ValueError('固定模型、数据或窄域见证已变')
    values = solution['variables']; count = problem['n_node_variables']
    if len(values) != len(problem['variables']) or any(type(v) is not int for v in values): raise ValueError('不是完整整数incumbent')
    for v, domain in zip(values, problem['variables']):
        if not domain['lower'] <= v <= domain['upper']: raise AssertionError('实际解超出原逐分量窄域')
    for row in problem['rows']:
        raw, reduced = sum(c*values[i] for i, c in row['raw_terms']), sum(c*values[i] for i, c in row['terms'])
        if not row['raw_lower'] <= raw <= row['raw_upper'] or not row['lower'] <= reduced <= row['upper']:
            raise AssertionError('解违反原始Q16或gcd舍入行')
    actual_encoded_cost = []
    for row in problem['budget_rows']:
        value = row['constant']+sum(c*values[i] for i, c in row['terms']); actual_encoded_cost.append(value)
        if value > row['limit']: raise AssertionError('返回解违反完整精度预算')
    original = load_model(problem['inputs']['first']['path']); nodes = original.nodes.copy(); flat = nodes.reshape(-1, 3)
    changed = np.zeros(flat.shape, bool)
    for i in range(count):
        domain = problem['variables'][i]; node, c = domain['physical_node'], domain['channel']
        if int(flat[node, c]) != domain['original_value']: raise AssertionError('原节点值不同')
        result = int(flat[node, c])+values[i]
        if not 0 <= result <= 255: raise AssertionError('节点越RGB8界')
        flat[node, c] = result; changed[node, c] = True
    np.testing.assert_array_equal(flat[~changed], original.nodes.reshape(-1, 3)[~changed])
    candidate = cc.ChannelLut(original.grid, nodes, original.idx, original.channel_frac)
    prior = ROOT/'artifacts/cinema-first-hotspot-v1'; stage = ROOT/'artifacts/cinema-first-narrow-cost-census-v1'
    if digest(prior/'suffix.npy') != problem['suffix_sha256'] or digest(prior/'support-index.npz') != problem['support_index_sha256']:
        raise ValueError('完整固定后缀或旧正支撑已变')
    with np.load(stage/'census.npz') as data: census = {k: data[k] for k in data.files}
    with np.load(prior/'support-index.npz') as data: old_keys, hotspots = data['union_keys'], data['hotspot_keys']
    keys, points = census['keys'], hs.rgb(census['keys'])
    fresh_new = integer_oracle(candidate, points)
    fresh_old = integer_oracle(candidate, hs.rgb(old_keys)); fresh_hot = integer_oracle(candidate, hs.rgb(hotspots))
    np.testing.assert_array_equal(cc.predict(candidate, hs.rgb(old_keys)), fresh_old)
    new_in_old, hot_in_old = np.searchsorted(old_keys, keys), np.searchsorted(old_keys, hotspots)
    np.testing.assert_array_equal(old_keys[new_in_old], keys); np.testing.assert_array_equal(old_keys[hot_in_old], hotspots)
    np.testing.assert_array_equal(fresh_old[new_in_old], fresh_new); np.testing.assert_array_equal(fresh_old[hot_in_old], fresh_hot)
    if np.any(fresh_new < census['lower_rgb']) or np.any(fresh_new > census['upper_rgb']): raise AssertionError('实际输出超已认证窄域端点')
    positions = np.flatnonzero(census['retained']); expected_keys = np.array([p['source_key'] for p in problem['points']], np.uint32)
    np.testing.assert_array_equal(keys[positions], expected_keys)
    expected = np.array([[p['original_rgb'][c]+values[p['z_indices'][c]] for c in range(3)] for p in problem['points']], np.uint8)
    np.testing.assert_array_equal(fresh_new[positions], expected)
    suffix = np.load(prior/'suffix.npy', mmap_mode='r'); gold = np.load(problem['inputs']['reference']['path'], mmap_mode='r')
    baseline = np.memmap(problem['inputs']['cube']['path'], np.uint8, 'r', shape=(TOTAL, 3))
    square_new, square_old = squared(suffix[hs.key(fresh_new)], gold[keys]), squared(suffix[hs.key(fresh_old)], gold[old_keys])
    square_hot = squared(suffix[hs.key(fresh_hot)], gold[hotspots])
    if int(square_new.max()) > 49 or int(square_old.max()) > 49: raise AssertionError('完整表/恒安全证书与真实cap重放矛盾')
    np.testing.assert_array_equal(square_new[~census['retained']], census['original_squared'][~census['retained']])
    for j, point in enumerate(problem['points']):
        q = int(square_new[positions[j]]); z = [values[i] for i in point['z_indices']]
        if [*z, q] not in point['allowed_error_rows']: raise AssertionError('实际误差不在安全联合表')
        if point['q_index'] is None:
            if q != point['q_constant']: raise AssertionError('固定q不同于真实误差')
        else:
            if values[point['q_index']] != q or sum(values[i] for _, i in point['selector_indices']) != 1:
                raise AssertionError('误差选择器不是真实one-hot')
            if sum(a*values[i] for a, i in point['selector_indices']) != q: raise AssertionError('选择器未绑定实际q')
    mass = np.load(problem['inputs']['mass']['path'], mmap_mode='r'); mass_sum = float(mass.sum(dtype=np.float64))
    training_new, _ = train_counts(mass[keys], mass_sum); training_old, _ = train_counts(mass[old_keys], mass_sum)
    np.testing.assert_array_equal(training_new, census['training_counts'])
    original_new = squared(baseline[keys], gold[keys]); original_old = squared(baseline[old_keys], gold[old_keys])
    np.testing.assert_array_equal(original_new, census['original_squared'])
    # 对实际全部新正支撑按(q,q0)聚合，再用第二整数根差算法计算成本。
    pairs, training_pairs = Counter(), Counter()
    for q, q0, w in zip(square_new, original_new, training_new):
        pair = int(q), int(q0); pairs[pair] += 1; training_pairs[pair] += int(w)
    uniform_threshold = int(problem['points'][0]['uniform_threshold_squared'])
    training_threshold = int(problem['points'][0]['training_threshold_squared'])
    exact_cost = [0]*8
    for (q, q0), number in sorted(pairs.items()):
        current = coefficients(q, q0, training_pairs[q, q0], uniform_threshold, training_threshold, independent=True)
        for b, value in enumerate(current): exact_cost[b] += value*(number if b % 2 == 0 else 1)
    if exact_cost != actual_encoded_cost: raise AssertionError('第二整数算法实际全支撑成本不同于CP返回预算')
    if any(a > b for a, b in zip(exact_cost, problem['budget_limits'])): raise AssertionError('实际全支撑整数成本超预算')
    before_hist, before_training = census['baseline_hist'], census['baseline_training_hist']
    outside = before_hist-hs.histogram(original_old); outside_training = before_training-hs.histogram(original_old, training_old)
    if np.any(outside < 0) or np.any(outside_training < 0) or np.flatnonzero(outside)[-1] > 49:
        raise AssertionError('旧完整并集外部固定域不符')
    after_hist = outside+hs.histogram(square_old); after_training = outside_training+hs.histogram(square_old, training_old)
    before, before_train = hs.metrics(before_hist), hs.metrics(before_training)
    if before != problem['baseline_uniform'] or before_train != problem['baseline_training']:
        raise AssertionError('实际预算不是原max_first')
    after, after_train = hs.metrics(after_hist), hs.metrics(after_training)
    failures = [label+'_'+metric for label, observed, initial in (('uniform', after, before), ('training', after_train, before_train))
        for metric in ('mean', 'rms', 'p99', 'cvar_1pct') if observed[metric] > initial[metric]+1e-12]
    if after['max_squared'] > 49: failures.append('strict_max49')
    args.output.mkdir(parents=True); folder = args.output/'candidate'; folder.mkdir()
    with np.load(problem['inputs']['first']['path']) as data: content = {k: data[k] for k in data.files}
    content['nodes'] = nodes; np.savez_compressed(folder/'model.npz', **content)
    io.save_sparse(folder/'candidate-base.slut', io.SparseLut(candidate.grid, candidate.nodes, candidate.idx, candidate.channel_frac[0]))
    for name, filename in (('sidecar', 'channel-frac.bin'), ('stage2', 'stage2.slut'), ('stage4', 'stage4.slut')):
        shutil.copyfile(problem['inputs'][name]['path'], folder/filename)
    np.savez_compressed(args.output/'replay.npz', keys=old_keys, first_rgb=fresh_old, squared=square_old, training_counts=training_old,
        new_keys=keys, new_first_rgb=fresh_new, new_squared=square_new, before_hist=before_hist,
        before_training_hist=before_training, after_hist=after_hist, after_training_hist=after_training)
    save(args.output/'summary.json', {'status': solution['status'], 'feasible': True, 'failures': failures,
        'fresh_new_support_rows': len(keys), 'fresh_old_support_rows': len(old_keys), 'fresh_hotspot_rows': len(hotspots),
        'full_support_max_squared': int(square_old.max()), 'old116_max_squared': int(square_hot.max()),
        'outside_support_max_squared': int(np.flatnonzero(outside)[-1]), 'u64_numba_mismatches': 0,
        'before_uniform': before, 'before_training': before_train, 'after_uniform': after, 'after_training': after_train,
        'actual_integer_costs': dict(zip(BUDGETS, exact_cost)), 'integer_budget_limits': dict(zip(BUDGETS, problem['budget_limits'])),
        'candidate_npz_sha256': digest(folder/'model.npz'), 'eligible_for_independent_final_checks': not failures,
        'overall_upgrade': False, 'environment': study_provenance.environment_fingerprint(),
        'scope': '一次fresh uint64重放47013/70571/116，独立实际八预算与原基线复核；未执行完整原生/100图/性能，任何综合升级另验。'})
    print({'failures': failures, 'max_squared': after['max_squared'], 'eligible': not failures}, flush=True)


if __name__ == '__main__': main()
