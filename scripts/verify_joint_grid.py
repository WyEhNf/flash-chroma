"""集中核对连续解析梯度、仿射数学预期与权威表序列化边界。"""
from pathlib import Path
import json
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'python'))
import numba
import numpy as np
from lutlab import interp, io, joint_grid as jg


def main():
    numba.set_num_threads(4)
    rng = np.random.default_rng(2026101803)
    grid = io.uniform_grid(17)
    grid[:, 1:-1] += rng.uniform(-1., 1., (3, 15))
    points = rng.integers(1, 255, (257, 3), dtype=np.uint8)
    nodes = rng.uniform(10., 240., (17**3, 3))
    targets = rng.integers(0, 256, points.shape, dtype=np.uint8)
    mass = rng.uniform(.1, 1., len(points)); mass /= mass.sum()
    value, gradient = jg.objective(points, targets, mass, nodes, grid)
    ids, _ = interp.tetra_weights(points, *io.axis_tables(grid), 17)
    active = np.unique(ids)
    checks = list((3 * rng.choice(active, 12) + rng.integers(0, 3, 12)).astype(int))
    checks += [nodes.size + a * 17 + k for a, k in ((0, 5), (0, 10), (1, 8), (1, 13), (2, 4), (2, 11))]
    physical = np.concatenate((nodes.ravel(), grid.ravel()))
    errors = []
    for index in checks:
        step = 1e-5
        left, right = physical.copy(), physical.copy()
        left[index] -= step; right[index] += step
        def evaluate(v):
            return jg.objective(points, targets, mass, v[:nodes.size].reshape(-1, 3), v[nodes.size:].reshape(3, 17))[0]
        numerical = (evaluate(right) - evaluate(left)) / (2 * step)
        error = abs(numerical - gradient[index]) / max(1., abs(numerical))
        errors.append(error)
        if error > 2e-7:
            raise AssertionError(f'解析梯度差异：{index} {gradient[index]} {numerical}')
    # 独立仿射预期：四面体应精确重现任意仿射RGB函数，不依赖其内部划分。
    cart = np.stack(np.meshgrid(*grid, indexing='ij'), -1).reshape(-1, 3)
    matrix = np.array([[.5, .1, .05], [.05, .6, .02], [.02, .1, .5]])
    offset = np.array([10., 15., 20.])
    affine = cart @ matrix + offset
    truth = points @ matrix + offset
    err = truth - targets.astype(float)
    norm = np.sqrt(np.sum(err * err, axis=1) + .25**2)
    expected = float(mass @ (norm - .25 + .02 * np.maximum(norm - 6., 0.)**2))
    actual, _ = jg.objective(points, targets, mass, affine, grid)
    if abs(actual - expected) > 1e-10:
        raise AssertionError('连续四面体未重现独立仿射数学预期')
    # 非仿射独立Q16设计：步长16使所有整数输入的分数精确可表达。
    exact_grid = np.tile(np.arange(17) * 16., (3, 1))
    ordered = np.array([[15, 10, 5], [15, 5, 10], [10, 15, 5], [5, 15, 10],
                        [10, 5, 15], [5, 10, 15], [0, 0, 0], [255, 255, 255],
                        [16, 16, 16], [10, 10, 5], [5, 10, 10]], np.uint8)
    random_nodes = rng.uniform(0., 255., (17**3, 3))
    design_ids, design_w = interp.tetra_weights(ordered, *io.axis_tables(exact_grid), 17)
    prediction = np.einsum('nk,nkc->nc', design_w, random_nodes[design_ids])
    zero = np.zeros_like(ordered)
    uniform = np.full(len(ordered), 1. / len(ordered))
    norm2 = np.sqrt(np.sum(prediction * prediction, axis=1) + .25**2)
    independent = float(np.mean(norm2 - .25 + .02 * np.maximum(norm2 - 6., 0.)**2))
    computed, _ = jg.objective(ordered, zero, uniform, random_nodes, exact_grid)
    if abs(computed - independent) > 1e-10:
        raise AssertionError('连续提议与独立非仿射四面体设计不同')
    # 全局间隔参数化的独立差分，核对链式法则并检查端点/顺序。
    logits = np.log(np.diff(grid, axis=1) - .5)
    recovered = jg.grid_from_logits(logits)
    np.testing.assert_allclose(recovered, grid, rtol=0, atol=1e-12)
    gradient_grid = gradient[nodes.size:].reshape(3, 17)
    converted = jg.spacing_gradient(gradient_grid, logits)
    spacing_errors = []
    for axis, knot in ((0, 3), (0, 11), (1, 1), (1, 12), (2, 6), (2, 14)):
        left, right = logits.copy(), logits.copy()
        left[axis, knot] -= 1e-6; right[axis, knot] += 1e-6
        a = jg.objective(points, targets, mass, nodes, jg.grid_from_logits(left))[0]
        b = jg.objective(points, targets, mass, nodes, jg.grid_from_logits(right))[0]
        numerical = (b-a) / 2e-6
        error = abs(numerical-converted[axis, knot]) / max(1., abs(numerical))
        spacing_errors.append(error)
        if error > 2e-6:
            raise AssertionError('全局间隔链式梯度不同')
    # 新轴按保存后的float32坐标生成Q16，旧轴对照保留其原权威表。
    candidate = jg.quantized_model(nodes, grid)
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / 'model.slut'
        io.save_sparse(path, candidate)
        loaded = io.load_sparse(path, competition=True)
        for a, b in zip(loaded.tables(), io.axis_tables(loaded.grid)):
            np.testing.assert_array_equal(a, b)
        np.testing.assert_array_equal(interp.apply_tetra_q16(candidate, points), interp.apply_tetra_q16(loaded, points))
        old_tables = io.axis_tables(grid)
        fixed = jg.quantized_model(nodes, grid, tables=old_tables)
        io.save_sparse(path, fixed)
        loaded = io.load_sparse(path)
        for a, b in zip(old_tables, loaded.tables()):
            np.testing.assert_array_equal(a, b)
    print(json.dumps({'contracts': 5, 'status': '通过', 'finite_difference_coordinates': len(checks),
        'max_normalized_gradient_error': max(errors), 'affine_objective_error': abs(actual-expected),
        'nonaffine_design_error': abs(computed-independent), 'max_spacing_gradient_error': max(spacing_errors),
        'numba_threads': numba.get_num_threads(), 'scope': '连续提议数学与序列化合同，不代替完整RGB8精度/原生验收'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
