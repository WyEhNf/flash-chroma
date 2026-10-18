"""以独立逐级整数映射核对后缀保持损失与节点收益，不执行完整精度测试。"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'python'))
import numba
import numpy as np
from lutlab import error_analysis as ea, fit, interp, io, rounded_grid, suffix_objective
from run_cinema_rounded import checked, load_inputs, read


def main():
    numba.set_num_threads(4)
    plan = read(ROOT/'experiments/cinema-prefix-stage1-v1.json')
    models, tables, _ = load_inputs(plan)
    parent = ROOT/'artifacts/cinema-prefix-stage1-v1'
    record = read(parent/'training.json')
    path = checked({'path': str(parent/'envelope-suffix.npy'),
                    'sha256': record['artifact_sha256']['envelope-suffix.npy']})
    cache = np.load(path, mmap_mode='r')
    rng = np.random.default_rng(2026101905)
    pool = fit.stratified_points(2026101802)
    points = pool[rng.choice(len(pool), 4096, replace=False)]
    targets = ea.source_apply(tables[0], points)
    indices, weights, acc, squared, colours = rounded_grid.prepare(models[0], points, targets)
    mass = rng.uniform(.2, 2., len(points)); mass /= mass.sum()
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64))
    rho = root+.02*np.maximum(root-6., 0.)**2
    objective = suffix_objective.SuffixObjective(cache, targets, 1.)
    def suffix(rgb):
        for model in models[1:]:
            rgb = interp.apply_tetra_q16(model, rgb)
        return rgb
    terminal_targets = suffix(targets)
    np.testing.assert_array_equal(objective.targets, terminal_targets)
    def independent(nodes):
        model = io.SparseLut(models[0].grid.copy(), nodes, *models[0].tables())
        output = suffix(interp.apply_tetra_q16(model, points))
        error = output.astype(np.int32)-terminal_targets.astype(np.int32)
        return float(mass@rho[np.sum(error*error, axis=1, dtype=np.int32)])
    initial = independent(models[0].nodes)
    initial_error = abs(initial-objective.loss(acc, mass, rho))
    maximum_error, changes, nonzero = initial_error, 0, 0
    for colour in range(8):
        for channel in range(3):
            gains = objective.gains(indices, weights, acc, mass, colours, colour, channel, rho, 4)
            support = np.unique(indices[weights > 0])
            for node in support[colours[support] == colour][:2]:
                for direction, delta in enumerate((1, -1)):
                    value = int(models[0].nodes.reshape(-1, 3)[node, channel])+delta
                    if not 0 <= value <= 255:
                        continue
                    nodes = models[0].nodes.copy(); nodes.reshape(-1, 3)[node, channel] = value
                    expected = independent(nodes)-initial
                    maximum_error = max(maximum_error, abs(float(gains[direction, node])-expected))
                    changes += 1; nonzero += int(abs(expected) > 1e-12)
    if maximum_error > 1e-11 or not nonzero:
        raise AssertionError('后缀节点收益与独立逐级整数映射不一致，或缺少非零变化覆盖')
    colour, channel = 5, 0
    gains = objective.gains(indices, weights, acc, mass, colours, colour, channel, rho, 4)
    nodes = models[0].nodes.reshape(-1, 3).copy()
    gains[0, nodes[:, channel] == 255] = np.inf
    gains[1, nodes[:, channel] == 0] = np.inf
    move = np.where((gains[0] < -1e-12) & (gains[0] <= gains[1]), 1,
                    np.where(gains[1] < -1e-12, -1, 0)).astype(np.int32)
    move[colours != colour] = 0
    predicted = sum(float(gains[0 if d == 1 else 1, i]) for i, d in enumerate(move) if d)
    rounded_grid._apply(indices, weights, acc, squared, targets, colours, colour, channel, move)
    nodes[:, channel] = nodes[:, channel].astype(np.int32)+move
    actual = independent(nodes.reshape(models[0].nodes.shape))-initial
    batch_error = max(abs(actual-predicted), abs(objective.loss(acc, mass, rho)-initial-actual))
    if batch_error > 1e-11:
        raise AssertionError('后缀损失在同色批量更新后的总变化不正确')
    bad = targets.copy(); bad[0, 0] ^= 1
    try:
        objective.validate(bad)
    except ValueError:
        pass
    else:
        raise AssertionError('不同标签不应通过本级身份绑定')
    print(json.dumps({'passed': 3, 'pixels': len(points), 'node_changes': changes, 'nonzero_changes': nonzero,
        'maximum_gain_error': maximum_error, 'batched_moves': int(np.count_nonzero(move)),
        'batch_error': batch_error, 'scope': '本级标签/后缀度量节点收益和批量合同；非完整终验或性能结果'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
