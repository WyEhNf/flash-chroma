"""回原NumPy1.26环境，精确验CP-SAT整数解、116点及完整70571支撑八预算。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import channel_coordinates as cc, channel_hotspot_support as hs, io
from run_channel_tail_nodes import load_model, digest, save
from run_cinema_first_hotspot import squared, train_counts, TOTAL, BLOCK, TRAINING_PIXELS
from verify_channel_coordinates import integer_oracle


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--problem', type=Path, required=True)
    p.add_argument('--solution', type=Path, required=True); p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖唯一整数解完整支撑验收')
    problem = json.loads(args.problem.read_text(encoding='utf-8')); solution = json.loads(args.solution.read_text(encoding='utf-8'))
    if solution['problem_sha256'] != digest(args.problem): raise ValueError('求解不属于冻结问题')
    for name, sha in problem['source_sha256'].items():
        if digest(ROOT/name) != sha: raise ValueError('冻结整数桥源已变：'+name)
    args.output.mkdir(parents=True)
    if not solution['feasible']:
        save(args.output/'summary.json', {'status': solution['status'], 'feasible': False,
             'eligible_for_independent_final_checks': False, 'scope': '未有可验整数incumbent；UNKNOWN非无解，局部INFEASIBLE没有独立形式证明不升级全局结论。'})
        return
    values = solution['variables']
    if len(values) != len(problem['variables']) or any(type(v) is not int for v in values): raise ValueError('解不是完整真整数变量')
    for value, domain in zip(values, problem['variables']):
        if not domain['lower'] <= value <= domain['upper']: raise AssertionError('整数解超变量域')
    for row in problem['rows']:
        raw = sum(coefficient*values[index] for index, coefficient in row['raw_terms'])
        normalized = sum(coefficient*values[index] for index, coefficient in row['terms'])
        if not row['raw_lower'] <= raw <= row['raw_upper'] or not row['lower'] <= normalized <= row['upper']:
            raise AssertionError('CP解违反原始或gcd约简闭区间')
    for point in problem['points']:
        if [values[i] for i in point['z_indices']] not in point['allowed_deltas']: raise AssertionError('CP解不属AllowedAssignments')
    original = load_model(problem['inputs']['first']['path']); nodes = original.nodes.copy()
    for index in range(problem['n_node_variables']):
        variable = problem['variables'][index]; node, channel = variable['physical_node'], variable['channel']
        if int(nodes.reshape(-1, 3)[node, channel]) != variable['original_value']: raise AssertionError('节点原值已变')
        nodes.reshape(-1, 3)[node, channel] = variable['original_value']+values[index]
    candidate = cc.ChannelLut(original.grid, nodes, original.idx, original.channel_frac)
    prior = ROOT/'artifacts/cinema-first-hotspot-v1'; suffix = np.load(prior/'suffix.npy', mmap_mode='r')
    if digest(prior/'suffix.npy') != problem['suffix_sha256']: raise ValueError('固定后缀字节已变')
    hotspot_keys = np.array([p['source_key'] for p in problem['points']], np.uint32)
    hot_first = integer_oracle(candidate, hs.rgb(hotspot_keys))
    expected_first = np.array([[p['original_rgb'][c]+values[p['z_indices'][c]] for c in range(3)] for p in problem['points']], np.uint8)
    np.testing.assert_array_equal(hot_first, expected_first)
    hot_gold = np.array([p['gold_rgb'] for p in problem['points']], np.uint8)
    hot_square = squared(suffix[hs.key(hot_first)], hot_gold)
    if np.any(hot_square > 49): raise AssertionError('116点真实整数后缀未达49')
    with np.load(prior/'support-index.npz') as data: keys = data['union_keys']
    baseline = np.memmap(problem['inputs']['cube']['path'], dtype=np.uint8, mode='r', shape=(TOTAL, 3))
    gold_full = np.load(problem['inputs']['reference']['path'], mmap_mode='r'); mass = np.load(problem['inputs']['mass']['path'], mmap_mode='r')
    total_mass = float(mass.sum(dtype=np.float64)); training, _ = train_counts(mass[keys], total_mass)
    hist, train_hist = np.zeros(51, np.int64), np.zeros(51, np.int64); training_total = 0
    for start in range(0, TOTAL, BLOCK):
        square = squared(baseline[start:start+BLOCK], gold_full[start:start+BLOCK]); count, _ = train_counts(mass[start:start+BLOCK], total_mass)
        hist += hs.histogram(square); train_hist += hs.histogram(square, count); training_total += int(count.sum())
    assert training_total == TRAINING_PIXELS
    initial, initial_train = hs.metrics(hist), hs.metrics(train_hist)
    original_square = squared(baseline[keys], gold_full[keys]); caps = np.maximum(49, original_square)
    outside, outside_train = hist-hs.histogram(original_square), train_hist-hs.histogram(original_square, training)
    assert outside[50] == outside_train[50] == 0
    fresh = integer_oracle(candidate, hs.rgb(keys)); square = squared(suffix[hs.key(fresh)], gold_full[keys]); size = max(51, int(square.max())+1)
    after_hist = np.pad(outside, (0, size-51))+hs.histogram(square, size=size)
    after_train_hist = np.pad(outside_train, (0, size-51))+hs.histogram(square, training, size=size)
    after, after_train = hs.metrics(after_hist), hs.metrics(after_train_hist)
    failures = [label+'_'+metric for label, observed, before in (('uniform', after, initial), ('training', after_train, initial_train))
                for metric in ('mean', 'rms', 'p99', 'cvar_1pct') if observed[metric] > before[metric]+1e-12]
    violating = int(np.count_nonzero(square > caps))
    if violating: failures.append('fixed_point_caps')
    if after['max_squared'] > 49: failures.append('strict_max49')
    folder = args.output/'candidate'; folder.mkdir()
    with np.load(problem['inputs']['first']['path']) as data: content = {name: data[name] for name in data.files}
    content['nodes'] = nodes; np.savez_compressed(folder/'model.npz', **content)
    io.save_sparse(folder/'candidate-base.slut', io.SparseLut(candidate.grid, candidate.nodes, candidate.idx, candidate.channel_frac[0]))
    for name, filename in (('sidecar', 'channel-frac.bin'), ('stage2', 'stage2.slut'), ('stage4', 'stage4.slut')):
        shutil.copyfile(problem['inputs'][name]['path'], folder/filename)
    save(args.output/'summary.json', {'status': solution['status'], 'feasible': True, 'hotspot_max_squared': int(hot_square.max()),
         'before_uniform': initial, 'before_training': initial_train, 'after_uniform': after, 'after_training': after_train,
         'point_cap_violations': violating, 'failures': failures, 'fresh_union_rows': len(keys),
         'candidate_npz_sha256': digest(folder/'model.npz'), 'eligible_for_independent_final_checks': not failures,
         'scope': '只一次CP整数incumbent，fresh u64核116与完整70571支撑和八预算；未通过则STOP，不新增热点/补跑/新native或百图。'})


if __name__ == '__main__': main()
