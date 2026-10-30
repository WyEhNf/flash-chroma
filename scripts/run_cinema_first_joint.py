"""在已认证70571行完整正支撑上单扫首级86节点，保护原max_first绝对八预算。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import sys
import time
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import channel_coordinates as cc, channel_first_joint as fj, channel_hotspot_support as hs, io, study_provenance
from run_channel_tail_nodes import digest, save, load_model
from run_cinema_first_hotspot import train_counts, squared, TOTAL, TRAINING_PIXELS, BLOCK
from verify_channel_coordinates import integer_oracle


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--contract', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖首级单次八色研究')
    plan_path = ROOT/'experiments/p16-cinema-first-joint-v1.json'
    contract = json.loads(args.contract.read_text(encoding='utf-8'))
    if not contract['pass']: raise ValueError('紧凑设计独立合同未通过')
    for name, sha in contract['source_sha256'].items():
        if digest(ROOT/name) != sha: raise ValueError('有限合同源已变：'+name)
    prior = ROOT/'artifacts/cinema-first-hotspot-v1'
    old = json.loads((prior/'run.json').read_text(encoding='utf-8'))
    independent_path = ROOT/'artifacts/cinema-first-hotspot-independent-v1.json'
    independent = json.loads(independent_path.read_text(encoding='utf-8'))
    if not independent['pass'] or independent['summary_sha256'] != digest(prior/'summary.json') or independent['support_index_sha256'] != digest(prior/'support-index.npz'):
        raise ValueError('完整正支撑前置证书缺失或变化')
    for name, sha in old['sources_sha256'].items():
        if digest(ROOT/name) != sha: raise ValueError('完整正支撑执行源已变：'+name)
    for spec in old['inputs'].values():
        if digest(spec['path']) != spec['sha256']: raise ValueError('原max_first/后缀/金标准/原60频数已变')
    summary = json.loads((prior/'summary.json').read_text(encoding='utf-8'))
    if digest(prior/'suffix.npy') != summary['suffix_sha256']: raise ValueError('904e/95cb/5b8完整后缀字节不同')
    sources = set(old['sources_sha256']) | {'experiments/p16-cinema-first-joint-v1.json', 'python/lutlab/channel_first_joint.py',
               'scripts/check_cinema_first_joint.py', 'scripts/run_cinema_first_joint.py', 'scripts/audit_cinema_first_hotspot.py'}
    args.output.mkdir(parents=True); started = time.perf_counter()
    save(args.output/'run.json', {'sources_sha256': {name: digest(ROOT/name) for name in sorted(sources)},
         'initial_run_sha256': digest(prior/'run.json'), 'initial_summary_sha256': digest(prior/'summary.json'),
         'support_index_sha256': digest(prior/'support-index.npz'), 'suffix_sha256': summary['suffix_sha256'],
         'contract': {'path': str(args.contract.resolve()), 'sha256': digest(args.contract)},
         'independent_support_certificate_sha256': digest(independent_path), 'inputs': old['inputs'],
         'plan': json.loads(plan_path.read_text(encoding='utf-8')), 'environment': study_provenance.environment_fingerprint(),
         'test_type': '完整受影响域的单次八色质量研究；共享主机，无性能测试'})
    model = load_model(old['inputs']['first']['path'])
    gold_full = np.load(old['inputs']['reference']['path'], mmap_mode='r')
    mass = np.load(old['inputs']['mass']['path'], mmap_mode='r'); total_mass = float(mass.sum(dtype=np.float64))
    baseline = np.memmap(old['inputs']['cube']['path'], np.uint8, 'r', shape=(TOTAL, 3))
    suffix = np.load(prior/'suffix.npy', mmap_mode='r')
    with np.load(prior/'support-index.npz') as data:
        keys, selected, support_keys, offsets = [data[k] for k in ('union_keys', 'selected_nodes', 'support_keys', 'offsets')]
    if len(keys) != 70571 or len(selected) != 86: raise ValueError('不是已证70571行/86节点')
    source = hs.rgb(keys); gold = np.asarray(gold_full[keys]); training, _ = train_counts(mass[keys], total_mass)
    baseline_hist = np.zeros(51, np.int64); baseline_train_hist = np.zeros(51, np.int64); count_total = 0
    for start in range(0, TOTAL, BLOCK):
        stop = start+BLOCK; square = squared(baseline[start:stop], gold_full[start:stop])
        counts, _ = train_counts(mass[start:stop], total_mass); count_total += int(counts.sum())
        if np.max(square) > 50: raise AssertionError('起点max50发生变化')
        baseline_hist += hs.histogram(square); baseline_train_hist += hs.histogram(square, counts)
    if count_total != TRAINING_PIXELS: raise AssertionError('原60图总整数频数不符')
    initial_uniform, initial_training = hs.metrics(baseline_hist), hs.metrics(baseline_train_hist)
    if initial_uniform != summary['baseline_uniform'] or initial_training != summary['baseline_training']:
        raise AssertionError('起点八项指标不是原max_first')
    indices, weights, baseline_acc = fj.compact_design(model, source, selected)
    fresh = integer_oracle(model, source)
    np.testing.assert_array_equal(((baseline_acc+32768)>>16).astype(np.uint8), fresh)
    np.testing.assert_array_equal(suffix[hs.key(fresh)], baseline[keys])
    original_square = squared(baseline[keys], gold); caps = np.maximum(49, original_square)
    outside_hist = baseline_hist-hs.histogram(original_square)
    outside_train_hist = baseline_train_hist-hs.histogram(original_square, training)
    if np.any(outside_hist < 0) or np.any(outside_train_hist < 0): raise AssertionError('固定支撑外直方图非负失败')
    if outside_hist[50] != 0 or outside_train_hist[50] != 0:
        raise AssertionError('116个原始max50输入没有全部包含在固定完整支撑内')
    row_sets, node_weights = [], []
    coords = np.column_stack(np.unravel_index(selected, (model.m,)*3))
    colours = (coords[:, 0]&1)*4+(coords[:, 1]&1)*2+(coords[:, 2]&1)
    for node in range(len(selected)):
        rows, node_weight = fj.node_support(indices, weights, node)
        np.testing.assert_array_equal(keys[rows], support_keys[offsets[node]:offsets[node+1]])
        row_sets.append(rows); node_weights.append(node_weight)
    for colour in range(8):
        count = np.zeros(len(keys), np.uint8)
        for node in np.flatnonzero(colours == colour): count[row_sets[node]] += 1
        if np.any(count > 1): raise AssertionError('同色节点完整正支撑重叠')
    save(args.output/'profile.json', {'selected_nodes': len(selected), 'complete_union_rows': len(keys), 'outside_uniform_pixels': int(outside_hist.sum()),
         'outside_training_pixels': int(outside_train_hist.sum()), 'compact_design_bytes': indices.nbytes+weights.nbytes,
         'baseline_acc_bytes': baseline_acc.nbytes, 'all_node_weights_bytes': sum(w.nbytes for w in node_weights),
         'initial_uniform': initial_uniform, 'initial_training': initial_training,
         'original_square_hist': hs.histogram(original_square).tolist(), 'fixed_cap_max': int(caps.max()),
         'outside_nodes_have_zero_delta_weights': True, 'same_colour_support_overlaps': 0})
    original_nodes = model.nodes.reshape(-1, 3)[selected].copy(); total_moves = np.zeros((len(selected), 3), np.int32)
    current_acc = baseline_acc.copy(); current_square = original_square.copy()
    current_hist, current_training_hist = baseline_hist.copy(), baseline_train_hist.copy()
    colour_records, node_records, direction_records = [], [], []
    lookup = lambda a: suffix[hs.key(a)]
    for colour in range(8):
        for node in np.flatnonzero(colours == colour):
            rows, node_weight = row_sets[node], node_weights[node]
            best, entries = fj.choose(current_acc[rows], node_weight, gold[rows], training[rows], current_square[rows], caps[rows],
                current_hist, current_training_hist, initial_uniform, initial_training, original_nodes[node], lookup)
            direction_records.append({'colour': colour, 'physical_node': int(selected[node]), 'proposals': entries})
            record = {'colour': colour, 'physical_node': int(selected[node]), 'accepted': best is not None,
                      'max50_before': int(current_hist[50])}
            if best is not None:
                total_moves[node] = best['delta']; current_acc[rows] += node_weight*best['delta']
                current_square[rows] = best['square']; current_hist = best['hist']; current_training_hist = best['training_hist']
                record.update(delta=best['delta'].tolist(), direction=best['direction'], uniform=best['uniform'], training=best['training'])
            else:
                record['rejection'] = '52项均未同时满足固定cap、原八预算及严格优先序；保留零移动'
            record['max50_after'] = int(current_hist[50]); node_records.append(record)
        nodes = model.nodes.copy(); nodes.reshape(-1, 3)[selected] = original_nodes.astype(np.int32)+total_moves
        current_model = cc.ChannelLut(model.grid, nodes, model.idx, model.channel_frac)
        independent_first = integer_oracle(current_model, source)
        np.testing.assert_array_equal(independent_first, ((current_acc+32768)>>16).astype(np.uint8))
        np.testing.assert_array_equal(current_acc, fj.apply_accumulator(indices, weights, baseline_acc, total_moves))
        independent_square = squared(lookup(independent_first), gold)
        np.testing.assert_array_equal(independent_square, current_square)
        np.testing.assert_array_equal(current_hist, outside_hist+hs.histogram(independent_square))
        np.testing.assert_array_equal(current_training_hist, outside_train_hist+hs.histogram(independent_square, training))
        uniform, train = hs.metrics(current_hist), hs.metrics(current_training_hist)
        if np.any(independent_square > caps) or any(after[k] > before[k]+1e-12 for after, before in
            ((uniform, initial_uniform), (train, initial_training)) for k in ('mean', 'rms', 'p99', 'cvar_1pct')):
            raise AssertionError('每色fresh固定cap或初始绝对八预算失败')
        record = {'colour': colour, 'uniform': uniform, 'training': train, 'max50_rows': int(current_hist[50]),
                  'fresh_union_rows': len(keys), 'fresh_mismatches': 0, 'accepted_nodes_total': int(np.count_nonzero(np.any(total_moves != 0, axis=1))),
                  'seconds': time.perf_counter()-started}
        colour_records.append(record); save(args.output/'colours.json', colour_records)
        print(record, flush=True)
    save(args.output/'nodes.json', node_records); save(args.output/'directions.json', direction_records)
    np.savez_compressed(args.output/'final-state.npz', physical_nodes=selected, moves=total_moves,
                        uniform_hist=current_hist, training_hist=current_training_hist, union_square=current_square)
    candidate = args.output/'candidate'; candidate.mkdir()
    original_npz = Path(old['inputs']['first']['path'])
    with np.load(original_npz) as data: content = {k: data[k] for k in data.files}
    content['nodes'] = current_model.nodes; np.savez_compressed(candidate/'model.npz', **content)
    io.save_sparse(candidate/'candidate-base.slut', io.SparseLut(current_model.grid, current_model.nodes, current_model.idx, current_model.channel_frac[0]))
    for name, filename in (('sidecar', 'channel-frac.bin'), ('stage2', 'stage2.slut'), ('stage4', 'stage4.slut')):
        shutil.copyfile(old['inputs'][name]['path'], candidate/filename)
    result = {'before_uniform': initial_uniform, 'before_training': initial_training, 'after_uniform': uniform, 'after_training': train,
              'max50_before': int(baseline_hist[50]), 'max50_after': int(current_hist[50]), 'rounds': 1, 'colours': 8,
              'accepted_nodes': int(np.count_nonzero(np.any(total_moves != 0, axis=1))), 'proposals': len(selected)*52,
              'fresh_union_mismatches': 0, 'outside_uniform_pixels_unchanged': int(outside_hist.sum()),
              'candidate_npz_sha256': digest(candidate/'model.npz'), 'candidate_slut_sha256': digest(candidate/'candidate-base.slut'),
              'eligible_for_independent_final_checks': bool(uniform['max_squared'] <= 49), 'seconds': time.perf_counter()-started,
              'scope': '一次八色贪心及精确完整支撑质量；若max仍50则不晋级，不自动加轮；无新全四级/native/百图/性能验收'}
    save(args.output/'summary.json', result); print(result, flush=True)


if __name__ == '__main__': main()
