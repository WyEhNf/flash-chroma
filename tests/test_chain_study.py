"""用独立的既有Q16实现核对四级融合与统计。"""
import numpy as np
import pytest
pytest.importorskip("numba", reason="四级研究内核使用可选Numba环境")
pytest.importorskip("tifffile", reason="本地研究的可选源文件依赖")
pytest.importorskip("psutil", reason="研究内存采样使用可选依赖")
from lutlab import io, interp, study_chains
from lutlab.compatibility import model_args


def test_fused_chain_has_integer_stage_boundaries():
    rng = np.random.default_rng(71)
    models = [io.SparseLut(io.uniform_grid(17), rng.integers(0,256,(17,17,17,3),dtype=np.uint8)) for _ in range(4)]
    args = [model_args(model) for model in models]
    points = rng.integers(0,256,(5000,3),dtype=np.uint8)
    expected = points.copy()
    for model in models:
        expected = interp.apply_tetra_q16(model, expected)
    actual = study_chains.map_chain(points, np.stack([a[0] for a in args]), np.stack([a[1] for a in args]), np.stack([a[2] for a in args]), 17, 0)
    np.testing.assert_array_equal(actual, expected)
    summary = study_chains.compare_images(actual[None], np.zeros_like(actual)[None])[0]
    distances = np.linalg.norm(actual.astype(np.float64), axis=1)
    np.testing.assert_allclose(summary, [distances.mean(), np.sqrt(np.mean(distances**2)), np.percentile(distances,99), distances.max()], atol=1e-10)
