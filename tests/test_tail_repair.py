"""局部整数重放、颜色上限交集与受保护节点选择的必要合同。"""
import numpy as np
import pytest
pytest.importorskip("numba", reason="尾部修复研究使用可选Numba环境")
from lutlab import error_analysis as ea, interp, io, tail_repair as tr


def test_caps_use_strictest_image_for_shared_colours():
    caps = np.full(256**3, np.iinfo(np.uint32).max, np.uint32)
    tr.update_caps(caps, np.array([[1, 2, 3], [1, 2, 3], [4, 5, 6]], np.uint8), 25)
    tr.update_caps(caps, np.array([[1, 2, 3], [9, 8, 7]], np.uint8), 9)
    assert caps[tr.encode(np.array([[1, 2, 3]], np.uint8))[0]] == 9
    assert caps[tr.encode(np.array([[4, 5, 6]], np.uint8))[0]] == 25


def test_local_trial_matches_independent_whole_chain_and_rolls_back():
    rng = np.random.default_rng(2026101721)
    models = [io.SparseLut(io.uniform_grid(3), rng.integers(0, 256, (3, 3, 3, 3), dtype=np.uint8)) for _ in range(4)]
    points = rng.integers(0, 256, (389, 3), dtype=np.uint8)
    state = tr.State(models, points, points)
    for stage in range(4):
        move = tr.Move(stage, int(state.indices[stage][0, 0]), (0, 255, 128))
        original = [model.nodes.copy() for model in models]
        rows, output, squared = state.trial(move)
        altered = tr.clone(models)
        altered[stage].nodes.reshape(-1, 3)[move.node] = move.value
        expected = points.copy()
        for model in altered:
            expected = interp.apply_tetra_q16(model, expected)
        actual = state.prediction.copy()
        actual[rows] = output
        np.testing.assert_array_equal(actual, expected)
        assert state.trial_metrics(rows, squared) == ea.metrics(expected, points)
        for model, old in zip(models, original):
            np.testing.assert_array_equal(model.nodes, old)
    endpoint = tr.State([models[0]], np.zeros((1, 3), np.uint8), np.zeros((1, 3), np.uint8))
    assert not len(endpoint.trial(tr.Move(0, 13, (1, 2, 3)))[0])


def test_guarded_repair_reaches_feasible_nodes_without_mutating_inputs():
    grid = io.uniform_grid(2)
    model = io.SparseLut(grid, np.full((2, 2, 2, 3), 100, np.uint8))
    alternative = io.SparseLut(grid, np.full((2, 2, 2, 3), 99, np.uint8))
    points = np.stack(np.meshgrid(*([np.array([0, 255], np.uint8)]*3), indexing="ij"), -1).reshape(-1, 3)
    truth = np.full_like(points, 99)
    spec = dict(points=points, truth=truth, caps=np.zeros(len(points), np.uint32))
    models, info = tr.repair([model], [{"baseline": alternative}], spec,
        {"uniform": dict(points=points, truth=truth)}, {"uniform": dict(mean=2., rms=2., p99=2., max=2.)}, steps=9)
    assert info["stop"] == "active_constraints_satisfied"
    assert len(info["accepted"]) == 8
    np.testing.assert_array_equal(models[0].nodes, alternative.nodes)
    assert np.all(model.nodes == 100)
