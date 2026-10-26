"""首级正支撑紧凑变动设计；外部顶点权重必须为零，原始累加保留。"""
from __future__ import annotations
import numpy as np
from . import channel_hotspot_support as hs


def compact_design(model, points, selected):
    raw_indices, raw_weights, baseline_acc = hs.basis(model, points)
    mapping = np.full(model.m**3, -1, np.int32)
    mapping[selected] = np.arange(len(selected), dtype=np.int32)
    mapped = mapping[raw_indices]
    active = mapped >= 0
    weights = np.where(active, raw_weights, 0).astype(np.int32)
    indices = np.where(active, mapped, 0).astype(np.int32)
    if np.any(weights[~active] != 0) or np.any(indices < 0) or np.any(indices >= len(selected)):
        raise AssertionError('紧凑变动设计的外节点零权重或合法占位失败')
    return indices, weights, baseline_acc


def apply_accumulator(indices, weights, baseline_acc, moves):
    result = baseline_acc.copy()
    for channel in range(3):
        result[:, channel] += np.sum(weights[channel].astype(np.int64)*moves[indices[channel], channel], axis=1, dtype=np.int64)
    return result


def node_support(indices, weights, compact_node):
    weight = np.sum(np.where(indices == compact_node, weights, 0), axis=2, dtype=np.int64).T
    rows = np.flatnonzero(np.any(weight > 0, axis=1))
    return rows, weight[rows]


def choose(acc, weight, gold, training, old_square, caps, global_hist, global_training_hist,
           initial_uniform, initial_training, node_rgb, lookup):
    """单节点52项与零移动比较；所有预算均相对不可变的原始基线。"""
    remainder = global_hist-hs.histogram(old_square)
    training_remainder = global_training_hist-hs.histogram(old_square, training)
    before_uniform, before_training = hs.metrics(global_hist), hs.metrics(global_training_hist)
    mean_sum = before_uniform['mean']+before_training['mean']
    best_rank = (int(global_hist[50]), mean_sum, before_uniform['cvar_1pct']+before_training['cvar_1pct'], -1)
    best, entries = None, []
    for direction, delta in enumerate(hs.DIRECTIONS):
        entry = {'direction': direction, 'delta': delta.tolist()}
        moved = node_rgb.astype(np.int32)+delta
        if np.any(moved < 0) or np.any(moved > 255):
            entries.append({**entry, 'rejected': '节点RGB8越界'}); continue
        first_output = ((acc+weight*delta+32768)>>16).astype(np.uint8)
        output = lookup(first_output); error = output.astype(np.int32)-gold.astype(np.int32)
        square = np.sum(error*error, axis=1, dtype=np.int32)
        if np.any(square > caps):
            entries.append({**entry, 'rejected': '原始固定逐点cap', 'violating_rows': int(np.count_nonzero(square > caps))}); continue
        hist = remainder+hs.histogram(square); train_hist = training_remainder+hs.histogram(square, training)
        uniform, train_metrics = hs.metrics(hist), hs.metrics(train_hist)
        failures = [label+'_'+metric for label, after, before in
                    (('uniform', uniform, initial_uniform), ('training', train_metrics, initial_training))
                    for metric in ('mean', 'rms', 'p99', 'cvar_1pct') if after[metric] > before[metric]+1e-12]
        entry.update(uniform=uniform, training=train_metrics, max50_rows=int(hist[50]), failures=failures)
        entries.append(entry)
        rank = (int(hist[50]), uniform['mean']+train_metrics['mean'], uniform['cvar_1pct']+train_metrics['cvar_1pct'], direction)
        if failures or rank[0] > int(global_hist[50]): continue
        if rank[0] == int(global_hist[50]) and rank[1] >= mean_sum-1e-12: continue
        if rank < best_rank:
            best_rank = rank
            best = {'delta': delta.copy(), 'direction': direction, 'square': square,
                    'hist': hist, 'training_hist': train_hist, 'uniform': uniform, 'training': train_metrics}
    for entry in entries:
        entry['accepted_for_node'] = best is not None and entry['direction'] == best['direction']
        if entry['accepted_for_node']: continue
        if 'rejected' in entry:
            entry['selection_rejection'] = entry['rejected']
        elif entry['failures']:
            entry['selection_rejection'] = '超过原max_first初始八预算'
        elif entry['max50_rows'] > int(global_hist[50]):
            entry['selection_rejection'] = 'max50计数增加'
        elif entry['max50_rows'] == int(global_hist[50]) and entry['uniform']['mean']+entry['training']['mean'] >= mean_sum-1e-12:
            entry['selection_rejection'] = 'max50计数相同时mean之和未严格下降'
        else:
            entry['selection_rejection'] = '固定优先序选择了更优方向'
    return best, entries
