"""回原环境一次独立u64重放完整危险表解及70571支撑，保护原八预算。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import channel_coordinates as cc, channel_hotspot_support as hs, io, study_provenance
from run_channel_tail_nodes import load_model, digest, save
from run_cinema_first_hotspot import squared, train_counts, TOTAL, BLOCK, TRAINING_PIXELS
from verify_channel_coordinates import integer_oracle
from cinema_first_safe_cpsat_model import validate_safe_problem


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--problem', type=Path, required=True)
    p.add_argument('--solution', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖唯一完整危险表验解')
    problem = json.loads(args.problem.read_text(encoding='utf-8')); solution = json.loads(args.solution.read_text(encoding='utf-8'))
    validate_safe_problem(problem)
    if solution['problem_sha256'] != digest(args.problem): raise ValueError('求解不属于冻结完整危险表')
    for name, expected in {**problem['source_sha256'], **problem['frozen_risk_sha256']}.items():
        if digest(ROOT/name) != expected: raise ValueError('冻结源/风险证据已变：'+name)
    args.output.mkdir(parents=True)
    if not solution['feasible']:
        save(args.output/'summary.json', {'status': solution['status'], 'feasible': False,
            'eligible_for_independent_final_checks': False, 'scope': '没有整数incumbent，按冻结停止；UNKNOWN非无解。'})
        return
    values = solution['variables']; count = problem['n_node_variables']
    if len(values) != len(problem['variables']) or any(type(v) is not int for v in values): raise ValueError('不是完整真整数解')
    for value, domain in zip(values, problem['variables']):
        if not domain['lower'] <= value <= domain['upper']: raise AssertionError('整数解超域')
    if solution['abs_variables'] != [abs(v) for v in values[:count]] or solution['l1_objective_integer'] != sum(abs(v) for v in values[:count]):
        raise AssertionError('abs辅助值或整数L1不符')
    for row in problem['rows']:
        raw = sum(c*values[i] for i, c in row['raw_terms']); reduced = sum(c*values[i] for i, c in row['terms'])
        if not row['raw_lower'] <= raw <= row['raw_upper'] or not row['lower'] <= reduced <= row['upper']:
            raise AssertionError('解违反原始或gcd舍入区间')
    for point in problem['points']:
        if [values[i] for i in point['z_indices']] not in point['allowed_deltas']: raise AssertionError('解违反危险安全表')
    for spec in problem['inputs'].values():
        if digest(spec['path']) != spec['sha256']: raise ValueError('原模型或数据已变')
    original = load_model(problem['inputs']['first']['path']); nodes = original.nodes.copy(); flat = nodes.reshape(-1, 3)
    for i in range(count):
        v = problem['variables'][i]; node, channel = v['physical_node'], v['channel']
        if int(flat[node, channel]) != v['original_value']: raise AssertionError('节点原值不符')
        flat[node, channel] = v['original_value']+values[i]
    candidate = cc.ChannelLut(original.grid, nodes, original.idx, original.channel_frac)
    prior = ROOT/'artifacts/cinema-first-hotspot-v1'; risk = ROOT/'artifacts/cinema-first-risk-v1'
    if digest(prior/'suffix.npy') != problem['suffix_sha256'] or digest(prior/'support-index.npz') != problem['support_index_sha256']:
        raise ValueError('固定完整后缀或正支撑已变')
    with np.load(prior/'support-index.npz') as data: keys, selected, old_hotspots = data['union_keys'], data['selected_nodes'], data['hotspot_keys']
    with np.load(risk/'screen.npz') as data:
        risk_keys, lower, upper, danger_rows = data['keys'], data['lower_rgb'], data['upper_rgb'], data['dangerous_rows']
    np.testing.assert_array_equal(keys, risk_keys)
    if len(keys) != 70571 or len(selected) != 86 or len(old_hotspots) != 116: raise ValueError('冻结正支撑尺寸不符')
    selected_actual = sorted({problem['variables'][i]['physical_node'] for i in range(count)})
    np.testing.assert_array_equal(np.array(selected_actual), selected)
    fixed = np.ones(len(flat), bool); fixed[selected] = False
    np.testing.assert_array_equal(flat[fixed], original.nodes.reshape(-1, 3)[fixed])
    fresh = integer_oracle(candidate, hs.rgb(keys))
    np.testing.assert_array_equal(cc.predict(candidate, hs.rgb(keys)), fresh)
    if np.any(fresh < lower) or np.any(fresh > upper): raise AssertionError('实际首级输出不在已认证节点AABB')
    expected = np.array([[p['original_rgb'][c]+values[p['z_indices'][c]] for c in range(3)] for p in problem['points']], np.uint8)
    np.testing.assert_array_equal(keys[danger_rows], np.array([p['source_key'] for p in problem['points']]))
    np.testing.assert_array_equal(fresh[danger_rows], expected)
    suffix = np.load(prior/'suffix.npy', mmap_mode='r')
    gold_full = np.load(problem['inputs']['reference']['path'], mmap_mode='r')
    baseline = np.memmap(problem['inputs']['cube']['path'], dtype=np.uint8, mode='r', shape=(TOTAL, 3))
    mass = np.load(problem['inputs']['mass']['path'], mmap_mode='r'); total_mass = float(mass.sum(dtype=np.float64))
    training, _ = train_counts(mass[keys], total_mass)
    hist, train_hist = np.zeros(51, np.int64), np.zeros(51, np.int64); training_total = 0
    for start in range(0, TOTAL, BLOCK):
        square = squared(baseline[start:start+BLOCK], gold_full[start:start+BLOCK]); counts, _ = train_counts(mass[start:start+BLOCK], total_mass)
        if square.max() > 50: raise AssertionError('原max_first基线max改变')
        hist += hs.histogram(square); train_hist += hs.histogram(square, counts); training_total += int(counts.sum())
    if training_total != TRAINING_PIXELS: raise AssertionError('原60图整数频数总量不符')
    before, before_train = hs.metrics(hist), hs.metrics(train_hist)
    prior_summary = json.loads((prior/'summary.json').read_text(encoding='utf-8'))
    if before != prior_summary['baseline_uniform'] or before_train != prior_summary['baseline_training']:
        raise AssertionError('八预算不是原max_first绝对基线')
    original_square = squared(baseline[keys], gold_full[keys])
    outside = hist-hs.histogram(original_square); outside_train = train_hist-hs.histogram(original_square, training)
    if np.any(outside < 0) or np.any(outside_train < 0) or np.flatnonzero(outside)[-1] > 49:
        raise AssertionError('支撑外并非固定全部≤49')
    square = squared(suffix[hs.key(fresh)], gold_full[keys])
    if square.max() > 49: raise AssertionError('危险表/恒安全证书与真实u64重放矛盾')
    old_rows = np.searchsorted(keys, old_hotspots); np.testing.assert_array_equal(keys[old_rows], old_hotspots)
    after_hist = outside+hs.histogram(square, size=51)
    after_train_hist = outside_train+hs.histogram(square, training, size=51)
    after, after_train = hs.metrics(after_hist), hs.metrics(after_train_hist)
    failures = [label+'_'+metric for label, observed, initial in (('uniform', after, before), ('training', after_train, before_train))
        for metric in ('mean', 'rms', 'p99', 'cvar_1pct') if observed[metric] > initial[metric]+1e-12]
    if after['max_squared'] > 49: failures.append('strict_max49')
    folder = args.output/'candidate'; folder.mkdir()
    with np.load(problem['inputs']['first']['path']) as data: content = {name: data[name] for name in data.files}
    content['nodes'] = nodes; np.savez_compressed(folder/'model.npz', **content)
    io.save_sparse(folder/'candidate-base.slut', io.SparseLut(candidate.grid, candidate.nodes, candidate.idx, candidate.channel_frac[0]))
    for name, filename in (('sidecar', 'channel-frac.bin'), ('stage2', 'stage2.slut'), ('stage4', 'stage4.slut')):
        shutil.copyfile(problem['inputs'][name]['path'], folder/filename)
    np.savez_compressed(args.output/'replay.npz', keys=keys, first_rgb=fresh, squared=square, training_counts=training,
        before_hist=hist, before_training_hist=train_hist, after_hist=after_hist, after_training_hist=after_train_hist)
    save(args.output/'summary.json', {'status': solution['status'], 'feasible': True,
        'l1_objective_integer': solution['l1_objective_integer'], 'old116_max_squared': int(square[old_rows].max()),
        'danger2224_max_squared': int(square[danger_rows].max()), 'full70571_max_squared': int(square.max()),
        'outside_support_max_squared': int(np.flatnonzero(outside)[-1]), 'point_cap_violations': int(np.count_nonzero(square > 49)),
        'before_uniform': before, 'before_training': before_train, 'after_uniform': after, 'after_training': after_train,
        'failures': failures, 'fresh_union_rows': len(keys), 'u64_numba_mismatches': 0,
        'candidate_npz_sha256': digest(folder/'model.npz'), 'eligible_for_independent_final_checks': not failures,
        'environment': study_provenance.environment_fingerprint(),
        'scope': '唯一minL1整数incumbent，一次完整支撑freshu64及原八预算验解；L1不代替精度门槛，失败即STOP。'})


if __name__ == '__main__': main()
