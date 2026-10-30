"""固定首级分输出几何，真实本级+非线性后缀目标的一次26方向联合节点提议。"""
from __future__ import annotations
import time
import numpy as np
from numba import njit, prange
from . import axis_calibration as ac, channel_coordinates as cc, channel_global_nodes as cg
from . import channel_joint_nodes as cj, channel_suffix_coordinates as cs, io

DIRECTIONS = cj.DIRECTIONS


@njit(cache=True, parallel=True)
def gains(indices, weights, acc, squared, targets, terminal, reference, caps, suffix,
          mass, nodes, colours, colour, rho, parts):
    """各方向先求完整RGB8 p，再直接查S(p)和双项cost/cap，不线性组合后缀。"""
    size = len(nodes)
    changes = np.zeros((parts, 26, size), np.float64)
    forbidden = np.zeros((parts, 26, size), np.int64)
    legal = np.ones((26, size), np.uint8)
    invalid = np.zeros(parts, np.int64)
    for node in prange(size):
        for d in range(26):
            for c in range(3):
                if not 0 <= np.int64(nodes[node, c])+DIRECTIONS[d, c] <= 255: legal[d, node] = 0
    for part in prange(parts):
        values = np.empty((3, 3), np.int32)
        for p in range(len(targets)*part//parts, len(targets)*(part+1)//parts):
            node = -1
            own_squared = 0
            for c in range(3):
                selected_weight, channel_node = 0, -1
                for v in range(4):
                    n, w = indices[c, p, v], weights[c, p, v]
                    if w > 0 and colours[n] == colour:
                        if channel_node >= 0: invalid[part] += 1
                        selected_weight, channel_node = w, n
                if channel_node >= 0:
                    if node >= 0 and node != channel_node: invalid[part] += 1
                    node = channel_node
                for step in range(3):
                    values[c, step] = (np.int64(acc[p, c])+(step-1)*selected_weight+io.ONE//2) >> io.Q
                error = np.int64(values[c, 1])-np.int64(targets[p, c])
                own_squared += error*error
            if node < 0: continue
            before, old_cap_d2 = ac._cost(values[0, 1], values[1, 1], values[2, 1],
                targets[p], terminal[p], reference[p], suffix, rho, 1.)
            if own_squared != squared[p] or old_cap_d2 > caps[p]: invalid[part] += 1
            for direction in range(26):
                if not legal[direction, node]: continue
                d = DIRECTIONS[direction]
                cost, d2 = ac._cost(values[0, d[0]+1], values[1, d[1]+1], values[2, d[2]+1],
                    targets[p], terminal[p], reference[p], suffix, rho, 1.)
                changes[part, direction, node] += mass[p]*(cost-before)
                forbidden[part, direction, node] += int(d2 > caps[p])
    change, bad = changes.sum(axis=0), forbidden.sum(axis=0)
    for node in prange(size):
        for d in range(26):
            if not legal[d, node]:
                change[d, node] = np.inf
                bad[d, node] += 1
    return change, bad, invalid.sum()


def propose(model, points, targets, terminal, mass, *, reference, caps, suffix,
            expected_initial_loss, parts=4, progress=None):
    """从aed几何固定起点，8色各一次；af974仍为唯一完整验收基线。"""
    cc.validate(model)
    if (points.dtype != np.uint8 or points.shape != (256**3, 3)
            or targets.dtype != np.uint8 or targets.shape != points.shape
            or terminal.dtype != np.uint8 or terminal.shape != points.shape
            or reference.dtype != np.uint8 or reference.shape != points.shape
            or suffix.dtype != np.uint8 or suffix.shape != points.shape
            or np.shape(mass) != (len(points),) or np.any(mass < 0) or not np.all(np.isfinite(mass))
            or abs(float(mass.sum())-1.) > 1e-10 or parts != 4
            or np.shape(caps) != (len(points),) or np.asarray(caps).dtype.kind not in 'iu'
            or np.any(caps < 0) or np.any(caps > 3*255**2) or not np.isfinite(expected_initial_loss)):
        raise ValueError('本轮需要冻结首级全域、独立T1/S(T1)、原质量/整链cap及有限初始目标')
    for start in range(0, len(points), 1 << 18):
        rows = points[start:start+(1 << 18)].astype(np.int64)
        if not np.array_equal(rows@np.array([65536, 256, 1], np.int64), np.arange(start, start+len(rows))):
            raise ValueError('首级原色行不是规范恒等映射')
        target = targets[start:start+len(rows)].astype(np.int64)
        if not np.array_equal(terminal[start:start+len(rows)], suffix[target@np.array([65536, 256, 1], np.int64)]):
            raise ValueError('标签不是S(T1)')
    started = time.perf_counter()
    indices, weights = cg.design(model, points)
    nodes = model.nodes.reshape(-1, 3).copy()
    acc, squared = cj.accumulate(indices, weights, nodes, targets)
    output = ((acc+io.ONE//2) >> io.Q).astype(np.uint8)
    np.testing.assert_array_equal(output, cc.predict(model, points))
    root = np.sqrt(np.arange(3*255**2+1, dtype=np.float64)); rho = root+.02*np.maximum(root-6., 0.)**2
    current, bad = cs.measure(output, targets, terminal, reference, caps, suffix, mass, rho, parts)
    if bad or abs(float(current)-expected_initial_loss) > 1e-8:
        raise ValueError('aed起点的旧双项目标/完整整链cap不符')
    colours = cj.parity(model.m)
    report = {'before_weighted_objective': float(current), 'groups': [], 'parts': parts,
        'directions': DIRECTIONS.tolist(), 'requested_sweeps': 1,
        'offline_design_bytes': indices.nbytes+weights.nbytes,
        'objective': 'rho(p-T1)+rho(S(p)-S(T1))；reference只cap，不作复合/残差标签',
        'geometry_proof': 'shared idx同cube八角parity互异；各输出正支撑为同一角，weight可不同/为0'}
    for colour in range(8):
        change, forbidden, invalid = gains(indices, weights, acc, squared, targets, terminal, reference, caps,
            suffix, mass, nodes, colours, colour, rho, parts)
        if invalid: raise AssertionError('共享cube几何/当前本级d2/整链cap不一致')
        moves, predicted, count, joint = cj.select(change, forbidden, colours, colour)
        cj.apply(indices, weights, acc, squared, targets, moves)
        values = nodes.astype(np.int32)+moves
        if values.min() < 0 or values.max() > 255: raise AssertionError('联合节点越界')
        nodes = values.astype(np.uint8)
        output = ((acc+io.ONE//2) >> io.Q).astype(np.uint8)
        measured, bad = cs.measure(output, targets, terminal, reference, caps, suffix, mass, rho, parts)
        if bad or abs(float(measured)-current-predicted) > 1e-10 or measured > current+1e-11:
            raise AssertionError('非线性后缀联合收益/硬cap不符')
        entry = {'colour': colour, 'changed_nodes': count, 'joint_channel_moves': joint,
            'before_weighted_objective': float(current), 'after_weighted_objective': float(measured),
            'predicted_change': predicted, 'measured_change': float(measured)-current,
            'prediction_error': abs(float(measured)-current-predicted),
            'geometry_errors': int(invalid), 'cap_violations': int(bad), 'seconds': time.perf_counter()-started}
        current = float(measured); report['groups'].append(entry)
        if progress: progress(entry)
    candidate = cc.ChannelLut(model.grid.copy(), nodes.reshape(model.nodes.shape), model.idx.copy(), model.channel_frac.copy())
    checked_acc, checked_squared = cj.accumulate(indices, weights, nodes, targets)
    fresh = cc.predict(candidate, points)
    fresh_loss, bad = cs.measure(fresh, targets, terminal, reference, caps, suffix, mass, rho, parts)
    if (not np.array_equal(checked_acc, acc) or not np.array_equal(checked_squared, squared)
            or not np.array_equal(fresh, output) or not np.array_equal(cg.squared_error(fresh, targets), squared)
            or bad or abs(float(fresh_loss)-current) > 1e-10):
        raise AssertionError('整扫fresh本级缓存/双项loss/最终cap不符')
    report.update(after_weighted_objective=current, training_cap_violations=0, cache_recompute_mismatches=0,
        geometry_errors=0, changed_node_components=int(np.count_nonzero(candidate.nodes != model.nodes)),
        changed_nodes=int(np.count_nonzero(np.any(candidate.nodes != model.nodes, axis=3))),
        joint_channel_moves=sum(r['joint_channel_moves'] for r in report['groups']),
        seconds=time.perf_counter()-started, scope='aed几何下8色26方向一次；有限耦合提议，非全局最优/完整验收')
    return candidate, report
