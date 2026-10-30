"""集中核对Cinema实际稀疏前缀及重复到达测度，不执行精度终验或性能测试。"""
from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'python'))
import numba
import numpy as np
from lutlab import error_analysis as ea, fit, interp
from run_cinema_rounded import add_counts, arrival_mass, load_inputs, read, rgb_keys


def main():
    numba.set_num_threads(4)
    plan = read(ROOT / 'experiments/cinema-rounded-v1.json')
    models, _, _ = load_inputs(plan)
    pool = fit.stratified_points(2026101802)
    rgb = pool[np.random.default_rng(2026101901).choice(len(pool), 4088, replace=False)]
    corners = np.array([[r, g, b] for r in (0, 255) for g in (0, 255) for b in (0, 255)], np.uint8)
    rgb = np.concatenate([rgb, corners])
    integer = rgb.copy()
    for model in models[:3]:
        integer = interp.apply_tetra_q16(model, integer)
    np.testing.assert_array_equal(integer, ea.Operator(models[:3])(rgb))
    # 对非恒等、量化且会重复的真实前缀，另用Counter核频数；不拿bincount验自己。
    repeated = np.concatenate([rgb[:79], rgb[:31], rgb[:7]])
    expected_rgb = repeated.copy()
    for model in models[:3]:
        expected_rgb = interp.apply_tetra_q16(model, expected_rgb)
    expected = Counter((int(r) << 16) | (int(g) << 8) | int(b) for r, g, b in expected_rgb)
    frequency = np.zeros(256**3, np.uint32)
    add_counts(frequency, ea.Operator(models[:3])(repeated))
    actual = {int(i): int(frequency[i]) for i in np.flatnonzero(frequency)}
    if actual != expected or int(frequency.sum(dtype=np.uint64)) != 117:
        raise AssertionError('重复像素或颜色编码频数错误')
    np.testing.assert_array_equal(rgb_keys(np.array([[255, 255, 255], [1, 2, 3]], np.uint8)),
                                  [16777215, 66051])
    # 独立按每种测度逐次列举的期望，核合并后目标；不是核实现内部损失缓存。
    cube = np.array([0, 1, 1, 1, 3, 4, 7, 7], np.int64)
    photos = np.array([2, 2, 2, 3, 4, 4, 6, 7, 7, 7], np.int64)
    f_cube = np.array([sum(cube == i) for i in range(8)], np.uint32)
    f_photo = np.array([sum(photos == i) for i in range(8)], np.uint32)
    allocation = plan['training']['mass']
    mass = arrival_mass(f_cube, f_photo, allocation)
    loss = np.sqrt(np.array([0, 1, 3, 7, 14, 29, 47, 72], np.float64))
    expected_loss = (allocation['own_uniform'] * loss.mean()
        + allocation['cube_arrival'] * np.mean([loss[i] for i in cube])
        + allocation['photo_arrival'] * np.mean([loss[i] for i in photos]))
    error = abs(float(mass @ loss) - expected_loss)
    if error > 1e-14:
        raise AssertionError('合并质量改变了各测度的重复权重')
    print(json.dumps({'passed': 3, 'prefix_integer_oracle_pixels': len(rgb),
        'repeated_pixels': 117, 'frequency_total': int(frequency.sum(dtype=np.uint64)),
        'weighted_objective_error': error,
        'scope': '4096真实前缀整数合同、独立重复计数与混合测度合同；非完整精度或性能结果'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
