"""检查源格式轴序、Q16一致性、色差分位数及边界政策。"""
from io import StringIO
import numpy as np
import pytest
pytest.importorskip("numba", reason="本地适配度研究使用独立的可选Numba环境")
pytest.importorskip("tifffile", reason="源TIFF读取是本地研究的可选依赖")
import tifffile
from lutlab import io, interp, source_lut
from lutlab import study_kernels as kernels


def test_real_study_identity_binds_environment(monkeypatch):
    from types import SimpleNamespace
    from lutlab import compatibility, study_provenance
    import numba
    numba.set_num_threads(1)
    args = SimpleNamespace(sizes=[17, 33], screen_pixels=4096, threads=1, reps=3, extended=True)
    monkeypatch.setattr(study_provenance, "environment_fingerprint", lambda: {"cpu_name": "cpu-a"})
    first = compatibility.environment(args)
    monkeypatch.setattr(study_provenance, "environment_fingerprint", lambda: {"cpu_name": "cpu-b"})
    second = compatibility.environment(args)
    assert first["identity_sha256"] != second["identity_sha256"]
    assert "numpy_build" in first["identity"]["environment"]


@pytest.mark.parametrize("kind", [0, 1, 2, 3, 4])
def test_constant_and_boundaries(kind):
    points = np.array([[0, 0, 0], [255, 255, 255], [255, 0, 255], [70, 83, 122]], np.uint8)
    nodes = np.full((17 ** 3, 3), 73., np.float64)
    idx, frac = io.axis_tables(io.uniform_grid(17))
    output = kernels.map_pixels(points, nodes, idx.astype(np.int32), frac / io.ONE, 17, kind)
    np.testing.assert_array_equal(output, 73)


def test_q16_against_existing_oracle():
    rng = np.random.default_rng(42)
    grid = np.stack([np.r_[0., np.sort(rng.choice(np.arange(1, 255), 15, replace=False)), 255.]] * 3)
    model = io.SparseLut(grid, rng.integers(0, 256, (17, 17, 17, 3), dtype=np.uint8))
    points = rng.integers(0, 256, (12000, 3), dtype=np.uint8)
    points[:256] = np.arange(256)[:, None]
    idx, frac = model.tables()
    actual = kernels.map_pixels(points, model.nodes.reshape(-1, 3).astype(float), idx.astype(np.int32), frac/io.ONE, 17, 0)
    np.testing.assert_array_equal(actual, interp.apply_tetra_q16(model, points))
    tri = kernels.map_pixels(points, model.nodes.reshape(-1, 3).astype(float), idx.astype(np.int32), frac/io.ONE, 17, 1)
    expected = np.clip(np.floor(interp.eval_float(model.nodes, grid, points, "tri")+.5), 0, 255).astype(np.uint8)
    np.testing.assert_array_equal(tri, expected)


@pytest.mark.parametrize("fmt", ["cube", "hald_tiff", "3dl"])
def test_source_channel_rotation(tmp_path, fmt):
    n = 4
    g = np.linspace(0, 1, n)
    rgb = np.stack(np.meshgrid(g, g, g, indexing="ij"), -1)
    mapped = rgb[..., [2, 0, 1]]
    metadata = {"grid_size": n, "format": fmt, "domain_min": [0]*3, "domain_max": [1]*3}
    path = tmp_path / "source"
    if fmt == "cube":
        buffer = StringIO()
        buffer.write("LUT_3D_SIZE 4\n")
        np.savetxt(buffer, mapped.transpose(2, 1, 0, 3).reshape(-1, 3), fmt="%.9f")
        path.write_text(buffer.getvalue())
    elif fmt == "hald_tiff":
        tifffile.imwrite(path, np.rint(mapped.transpose(2, 1, 0, 3).reshape(8, 8, 3)*255).astype(np.uint8), photometric="rgb")
    else:
        buffer = StringIO()
        buffer.write("0 341 682 1023\n")
        np.savetxt(buffer, np.rint(mapped.reshape(-1, 3)*4095), fmt="%d")
        path.write_text(buffer.getvalue())
    nodes, grid, policy = source_lut.load_source(path, metadata)
    idx, frac = source_lut.source_axes(grid)
    points = np.random.default_rng(3).integers(0, 256, (4096, 3), dtype=np.uint8)
    out = kernels.map_pixels(points, nodes, idx, frac, n, 1)
    np.testing.assert_array_equal(out, points[:, [2, 0, 1]])


def test_metrics_against_numpy():
    rng = np.random.default_rng(33)
    points = rng.integers(0, 256, (2, 101, 3), dtype=np.uint8)
    model = io.SparseLut(io.uniform_grid(17), rng.integers(0, 256, (17, 17, 17, 3), dtype=np.uint8))
    idx, frac = model.tables()
    truth = np.zeros((256**3, 3), np.uint8)
    summary = kernels.image_metrics(points, truth, model.nodes.reshape(-1, 3).astype(float), idx.astype(np.int32), frac/io.ONE, 17, 0)
    for j in range(2):
        mapped = interp.apply_tetra_q16(model, points[j]).astype(np.int32)
        distances = np.linalg.norm(mapped, axis=1)
        np.testing.assert_allclose(summary[j, :4], [distances.mean(), np.sqrt(np.mean(distances**2)), np.percentile(distances, 99), distances.max()], atol=1e-10)


def test_hold_preserves_upper_endpoint():
    grid = io.uniform_grid(17)
    nodes = np.zeros((17, 17, 17, 3), np.float64)
    nodes[-1, -1, -1] = 255
    idx, frac = io.axis_tables(grid)
    out = kernels.map_pixels(np.array([[255, 255, 255]], np.uint8), nodes.reshape(-1, 3), idx.astype(np.int32), frac/io.ONE, 17, 3)
    np.testing.assert_array_equal(out, 255)


def test_prism_against_independent_six_vertex_formula():
    rng = np.random.default_rng(117)
    nodes = rng.integers(0,256,(2,2,2,3)).astype(np.float64)
    points = rng.integers(0,256,(1000,3),dtype=np.uint8)
    idx = np.zeros((3,256),np.int32)
    frac = np.stack([np.arange(256)/255]*3)
    actual = kernels.map_pixels(points,nodes.reshape(-1,3),idx,frac,2,4)
    expected = []
    for r,g,b in points.astype(float)/255:
        if r >= g:
            bottom = (1-r)*nodes[0,0,0]+(r-g)*nodes[1,0,0]+g*nodes[1,1,0]
            top = (1-r)*nodes[0,0,1]+(r-g)*nodes[1,0,1]+g*nodes[1,1,1]
        else:
            bottom = (1-g)*nodes[0,0,0]+(g-r)*nodes[0,1,0]+r*nodes[1,1,0]
            top = (1-g)*nodes[0,0,1]+(g-r)*nodes[0,1,1]+r*nodes[1,1,1]
        expected.append(np.floor((1-b)*bottom+b*top+.5).astype(np.uint8))
    np.testing.assert_array_equal(actual,expected)
