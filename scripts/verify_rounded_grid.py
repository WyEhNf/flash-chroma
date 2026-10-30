"""集中核对整数节点收益、同色批量更新及权威表保持。"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'python'))
import numba
import numpy as np
from lutlab import interp, io, rounded_grid as rg


def actual(model, points, targets, mass, rho):
    prediction = interp.apply_tetra_q16(model, points)
    delta = prediction.astype(np.int32) - targets.astype(np.int32)
    squared = np.sum(delta * delta, axis=1, dtype=np.int32)
    return float(mass @ rho[squared]), prediction, squared


def main():
    numba.set_num_threads(4)
    rng = np.random.default_rng(2026101804)
    grid = io.uniform_grid(17)
    points = np.concatenate((rng.integers(0, 256, (389, 3), dtype=np.uint8),
                             np.array([[0,0,0],[255,255,255],[16,16,16],[32,32,8]], np.uint8)))
    nodes = rng.integers(0, 256, (17,17,17,3), dtype=np.uint8)
    idx, frac = io.axis_tables(grid)
    frac[0, 16] += 1
    model = io.SparseLut(grid, nodes, idx, frac)
    target = rng.integers(0, 256, points.shape, dtype=np.uint8)
    mass = rng.uniform(.1, 1., len(points)); mass /= mass.sum()
    root = np.sqrt(np.arange(3*255**2+1, dtype=float))
    rho = root + .02*np.maximum(root-6., 0.)**2
    indices, weights, acc, squared, colours = rg.prepare(model, points, target)
    old_loss, old_prediction, old_squared = actual(model, points, target, mass, rho)
    np.testing.assert_array_equal((acc+io.ONE//2)>>io.Q, old_prediction)
    np.testing.assert_array_equal(squared, old_squared)
    max_error = 0.
    checks = 0
    for colour, channel in ((0,0),(3,1),(7,2)):
        gain, forbidden = rg._gains(indices, weights, acc, squared, target, mass,
            nodes.reshape(-1,3), colours, colour, channel, rho, 3*255**2, 4)
        mask = (colours[indices] == colour) & (weights > 0)
        if np.any(mask.sum(axis=1) > 1):
            raise AssertionError('同色节点正支撑重叠')
        active = np.unique(indices[mask])[:6]
        for node in active:
            for direction, delta in enumerate((1,-1)):
                value = int(nodes.reshape(-1,3)[node,channel]) + delta
                if not 0 <= value <= 255:
                    continue
                trial = nodes.copy(); trial.reshape(-1,3)[node,channel] = value
                candidate = io.SparseLut(grid, trial, idx, frac)
                loss, _, _ = actual(candidate, points, target, mass, rho)
                error = abs((loss-old_loss)-gain[direction,node]); max_error = max(max_error,error)
                if error > 5e-12:
                    raise AssertionError('逐节点真实损失变化与独立整数oracle不同')
                checks += 1
        move = np.zeros(len(colours), np.int32)
        for node in active:
            value = int(nodes.reshape(-1,3)[node,channel])
            move[node] = 1 if value < 255 else -1
        trial = nodes.copy()
        trial.reshape(-1,3)[:,channel] = (trial.reshape(-1,3)[:,channel].astype(int)+move).astype(np.uint8)
        current_acc, current_sq = acc.copy(), squared.copy()
        rg._apply(indices, weights, current_acc, current_sq, target, colours, colour, channel, move)
        _, predicted, reference_sq = actual(io.SparseLut(grid,trial,idx,frac), points,target,mass,rho)
        np.testing.assert_array_equal((current_acc+io.ONE//2)>>io.Q, predicted)
        np.testing.assert_array_equal(current_sq, reference_sq)
    # 最坏颜色的节点必须在任何新误差超过固定cap时被禁止，比较独立全样本结果。
    cap = int(squared.max())
    worst = int(np.argmax(squared))
    vertex = int(np.flatnonzero(weights[worst] > 0)[0])
    node = int(indices[worst,vertex])
    colour = int(colours[node])
    cap_checks = 0
    for channel in range(3):
        _, forbidden = rg._gains(indices,weights,acc,squared,target,mass,nodes.reshape(-1,3),
            colours,colour,channel,rho,cap,4)
        for direction,delta in enumerate((1,-1)):
            value = int(nodes.reshape(-1,3)[node,channel])+delta
            if not 0 <= value <= 255:
                continue
            trial = nodes.copy();trial.reshape(-1,3)[node,channel]=value
            _, _, reference = actual(io.SparseLut(grid,trial,idx,frac),points,target,mass,rho)
            if bool(forbidden[direction,node]) != (int(reference.max()) > cap):
                raise AssertionError('完整max禁止位与独立oracle不同')
            cap_checks += 1
    candidates, report = rg.propose(model, points, target, mass, sweeps=2)
    for _, candidate in candidates:
        for a,b in zip(candidate.tables(), model.tables()):
            np.testing.assert_array_equal(a,b)
    final_loss, _, _ = actual(candidates[-1][1], points, target, mass, rho)
    if final_loss > old_loss+1e-10 or abs(final_loss-report['after_weighted_objective'])>1e-10:
        raise AssertionError('整扫目标回执与独立整数oracle不同')
    print(json.dumps({'contracts':4,'status':'通过','independent_node_changes':checks,'cap_changes':cap_checks,
        'max_loss_delta_error':max_error,'weighted_loss_before':old_loss,'weighted_loss_after':final_loss,
        'accepted_sweeps':report['accepted_sweeps'],'scope':'小型确定性整数精化合同，不代替完整精度/原生终验'},ensure_ascii=False))


if __name__=='__main__':
    main()
