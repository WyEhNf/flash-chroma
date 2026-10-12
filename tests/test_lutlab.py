"""End-to-end Python + C++ parity and accuracy unit tests."""
from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np

from lutlab import cascade, fit as fit_mod, interp, io, metrics

ROOT = Path(__file__).resolve().parents[1]
JSHC = ROOT / "build" / "jshc"


def test_python_cpp_bit_exact(tmp_path: Path):
    """Verify Python's `apply_tetra_q16` is 100% bit-exact with C++ `jshc apply` (both
    scalar and AVX2) on random images and non-uniform grids across multiple m."""
    rng = np.random.default_rng(42)
    img = rng.integers(0, 256, (64, 96, 3), dtype=np.uint8)
    in_p = tmp_path / "in.png"
    io.save_image(in_p, img)

    for m in (17, 25, 33):
        # Create a non-uniform grid to stress-test axis_tables & Q16 fractions
        g = np.linspace(0, 1, m) ** 1.15 * 255.0
        g[0], g[-1] = 0.0, 255.0
        grid = np.stack([g, np.linspace(0, 255, m), g])
        nodes = rng.integers(0, 256, (m, m, m, 3), dtype=np.uint8)
        slut = io.SparseLut(grid, nodes)
        slut_p = tmp_path / f"lut_{m}.slut"
        io.save_sparse(slut_p, slut)

        py_out = interp.apply_tetra_q16(slut, img)
        for k in ("tetra_scalar", "tetra_avx2"):
            out_p = tmp_path / f"out_{m}_{k}.png"
            subprocess.run([str(JSHC), "apply", "-i", str(in_p), "-o", str(out_p), "-k", k, str(slut_p)], check=True)
            cpp_out = io.load_image(out_p)
            assert np.array_equal(py_out, cpp_out), f"mismatch for m={m}, kernel={k}"


def test_fitting_monotonic_improvement():
    """Verify that least-squares + integer refinement beats naive sampling on a known smooth LUT."""
    v = np.linspace(0, 1, 256, dtype=np.float32)
    rr, gg, bb = np.meshgrid(v, v, v, indexing="ij")
    # Smooth non-linear colour curve
    y = np.stack([
        np.power(rr, 0.85) * 0.9 + 0.1 * gg,
        np.power(gg, 1.15),
        0.5 * bb + 0.5 * (bb * bb),
    ], axis=-1)
    T = np.clip(np.floor(y * 255.0 + 0.5), 0, 255).astype(np.uint8)

    rng = np.random.default_rng(7)
    probe_img = rng.integers(0, 256, (128, 128, 3), dtype=np.uint8)
    gt = io.apply_full(T, probe_img)

    n_samp, g_samp, _ = fit_mod.fit(T, 17, "sample")
    n_ls, g_ls, _ = fit_mod.fit(T, 17, "ls_tetra_int")

    de_samp = metrics.delta_e_map(interp.apply_tetra_q16(io.SparseLut(g_samp, n_samp), probe_img), gt).mean()
    de_ls = metrics.delta_e_map(interp.apply_tetra_q16(io.SparseLut(g_ls, n_ls), probe_img), gt).mean()
    assert de_ls < de_samp, f"expected ls_tetra_int ({de_ls}) < sample ({de_samp})"
    assert de_ls < 0.6


def test_separable_bases_and_tucker():
    """Smoke test for B-spline, Lagrange, polynomial, and Tucker routes."""
    v = np.linspace(0, 1, 256, dtype=np.float32)
    rr, gg, bb = np.meshgrid(v, v, v, indexing="ij")
    T = np.clip(np.floor(np.stack([rr, gg, bb], -1) * 255.0 + 0.5), 0, 255).astype(np.uint8)
    grid = io.uniform_grid(17)
    for kind in ("hat", "bspline2", "bspline3", "lagrange3"):
        X = fit_mod.fit_ls_sep(T, grid, kind)
        assert X.shape == (17, 17, 17, 3)
    slut, info = cascade.fit_tucker_lut(T, 17, rank=6)
    assert slut.nodes.shape == (17, 17, 17, 3)
    assert info["tucker_params"] > 0
