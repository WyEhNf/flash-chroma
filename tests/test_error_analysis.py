"""用可解释的整数链核对归因恒等式与后级跳变；不拟合研究数据。"""
import numpy as np
import pytest
pytest.importorskip("numba", reason="误差研究使用独立可选Numba环境")
from lutlab import error_analysis as ea, error_certificate, io


def test_decomposition_and_exact_stage_replacement():
    rng = np.random.default_rng(2026101641)
    grid = io.uniform_grid(3)
    models = [io.SparseLut(grid, rng.integers(0, 256, (3, 3, 3, 3), dtype=np.uint8)) for _ in range(2)]
    tables = [lambda x: x.copy(), lambda x: 255-x]
    points = rng.integers(0, 256, (101, 3), dtype=np.uint8)
    result = ea.stage_attribution(tables, models, points)
    for stage in result["stages"]:
        np.testing.assert_allclose(stage["sse_total"], stage["sse_local"] + stage["sse_propagated"] + stage["sse_interaction"], atol=1e-9)
    direct = ea.metrics(ea.Operator([models[1]])(points), 255-points)
    assert result["stages"][0]["replace_this_stage_exact"] == direct
    error = ea.Operator(models)(points).astype(float) - (255-points).astype(float)
    np.testing.assert_allclose(result["baseline"]["p99"], np.percentile(np.linalg.norm(error, axis=1), 99))
    diagnostics = ea.rounding_diagnostics(tables[0], models[0], points,
        models[0].nodes.astype(float), models[0].nodes.astype(float))
    assert diagnostics["output_rounding_change"]["max"] <= np.sqrt(3) / 2 + 1e-12


def test_reference_threshold_jump_is_measured_separately():
    def threshold(x):
        return np.where(x >= 128, 255, 0).astype(np.uint8)
    points = np.array([[127, 3, 4], [32, 3, 4], [255, 3, 4]], np.uint8)
    np.testing.assert_array_equal(ea.suffix_sensitivity([threshold], points), [255., 0., 0.])
    baseline = dict(mean=1., rms=2., p99=3., max=4.)
    assert not ea.promoted({**baseline, "mean": .5, "max": 5.}, baseline)
    assert ea.promoted({**baseline, "max": 3.}, baseline)
    model = io.SparseLut(io.uniform_grid(2), np.zeros((2, 2, 2, 3), np.uint8))
    inputs = np.array([[0, 0, 0], [127, 0, 0], [254, 0, 0]], np.uint8)
    labels = np.array([[0, 0, 0], [255, 0, 0], [255, 0, 0]], np.uint8)
    certificate = error_certificate.three_point_bound(model, inputs, labels)
    assert certificate["rgb_l2_max_lower_bound"] == 64
    assert certificate["reference_second_difference"] == [-255, 0, 0]
