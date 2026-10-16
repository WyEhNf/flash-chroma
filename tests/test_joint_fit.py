"""有界候选与有限联合选择的阶段合同，不展开研究数据或性能扫描。"""
import numpy as np
import pytest
pytest.importorskip("numba", reason="联合拟合研究使用可选Numba环境")
from lutlab import error_analysis as ea, interp, io, joint_fit


def test_bank_uses_own_labels_and_feasible_box():
    axis = np.array([0, 32, 64, 96, 128, 160, 192, 224, 255], np.uint8)
    points = np.stack(np.meshgrid(axis, axis, axis, indexing="ij"), -1).reshape(-1, 3)
    grid = io.uniform_grid(3)
    model = io.SparseLut(grid, np.full((3, 3, 3, 3), 128, np.uint8))
    before = model.nodes.copy()
    observed = []
    def own_source(rgb):
        observed.append(rgb.copy())
        return np.clip((rgb.astype(np.int32)-64)*2, 0, 255).astype(np.uint8)
    info = {}
    bank = joint_fit.fit_bank(own_source, model, points, points[::-1], irls_rounds=2, diagnostics=info)
    np.testing.assert_array_equal(observed[0], np.concatenate((points, points[::-1])))
    np.testing.assert_array_equal(model.nodes, before)
    assert info["raw_components_outside_box"] > 0
    assert info["box_components_outside_box"] == 0
    assert info["continuous_box_vs_clamped_change"] < 0
    assert all(r["after"] <= r["before"]+1e-8 for r in info["irls"])
    for candidate in bank.values():
        io.validate_sparse(candidate)
        np.testing.assert_array_equal(candidate.tables()[1], model.tables()[1])


def test_joint_guard_rejects_distribution_tradeoff_and_finds_combined_gain():
    def row(key, u, p, tail=4.):
        metrics = lambda mean: dict(mean=mean, rms=2., p99=3., max=tail)
        return dict(key=key, metrics=dict(uniform=metrics(u),
            photo={**metrics(p), "worst_image_mean": 2., "worst_image_p99": 3.}, hotspot=metrics(2.)))
    baseline = ["baseline", "baseline"]
    records = [row(baseline, 1., 1.), row(["mean", "baseline"], .8, 1.1),
        row(["baseline", "mean"], 1.1, .8), row(["mean", "mean"], .85, .85),
        row(["tail", "tail"], .7, .7, tail=5.)]
    assert joint_fit.choose(records, baseline)["winner"] == ["mean", "mean"]
    assert joint_fit.choose(records[:3], baseline)["winner"] == baseline
    assert joint_fit.choose(records, baseline, measures=("uniform",))["winner"] == ["mean", "baseline"]


def test_enumeration_matches_independent_integer_chain():
    rng = np.random.default_rng(2026101711)
    grid = io.uniform_grid(3)
    banks = [{name: io.SparseLut(grid, rng.integers(0, 256, (3, 3, 3, 3), dtype=np.uint8))
              for name in ("baseline", "candidate")} for _ in range(4)]
    points = rng.integers(0, 256, (97, 3), dtype=np.uint8)
    sets = {"uniform": dict(points=points, truth=points)}
    records = joint_fit.enumerate_bank(banks, sets)
    assert len(records) == 16
    for row in records:
        predicted = points.copy()
        for stage, key in zip(banks, row["key"]):
            predicted = interp.apply_tetra_q16(stage[key], predicted)
        assert row["metrics"]["uniform"] == ea.metrics(predicted, points)
