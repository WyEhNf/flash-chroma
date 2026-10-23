"""纯Python整数的首级节点分量盒到RGB8输出包围盒；只给必要下界。"""
from __future__ import annotations


def scalar_basis(model, point, channel):
    base = (int(model.idx[0, point[0]])*model.m+int(model.idx[1, point[1]]))*model.m+int(model.idx[2, point[2]])
    fractions = [int(model.channel_frac[channel, a, point[a]]) for a in range(3)]
    strides = [model.m**2, model.m, 1]
    for a, b in ((0, 1), (1, 2), (0, 1)):
        if fractions[a] < fractions[b]:
            fractions[a], fractions[b], strides[a], strides[b] = fractions[b], fractions[a], strides[b], strides[a]
    indices = [base, base+strides[0], base+strides[0]+strides[1], base+sum(strides)]
    weights = [65536-fractions[0], fractions[0]-fractions[1], fractions[1]-fractions[2], fractions[2]]
    if sum(weights) != 65536 or min(weights) < 0: raise AssertionError('标量权重守恒或非负失败')
    return [(node, weight) for node, weight in zip(indices, weights) if weight > 0]


def point_box(model, point, selected, step=2):
    if step != 2: raise ValueError('本阶段仅允许冻结分量±2盒')
    selected = set(map(int, selected)); nodes = model.nodes.reshape(-1, 3)
    lower, upper, channels = [], [], []
    for channel in range(3):
        weights = scalar_basis(model, point, channel)
        low_acc, high_acc, baseline_acc = 0, 0, 0
        coefficients = []
        for node, weight in weights:
            value = int(nodes[node, channel])
            low, high = (max(0, value-step), min(255, value+step)) if node in selected else (value, value)
            low_acc += weight*low; high_acc += weight*high; baseline_acc += weight*value
            coefficients.append({'physical_node': node, 'weight_q16': weight, 'original_value': value,
                                 'lower_value': low, 'upper_value': high, 'variable': node in selected})
        lo, hi = (low_acc+32768)//65536, (high_acc+32768)//65536
        if not 0 <= lo <= hi <= 255 or hi-lo > 4: raise AssertionError('RGB8分量±2包围盒界失败')
        lower.append(lo); upper.append(hi)
        channels.append({'output_channel': channel, 'baseline_acc': baseline_acc,
                         'lower_acc': low_acc, 'upper_acc': high_acc, 'coefficients': coefficients})
    return {'lower_rgb': lower, 'upper_rgb': upper, 'channels': channels}
