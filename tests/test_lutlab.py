"""End-to-end Python + C++ parity and accuracy unit tests."""
from __future__ import annotations

import subprocess
from types import SimpleNamespace
from pathlib import Path

import numpy as np

from lutlab import cascade, cli, fit as fit_mod, interp, io, metrics

ROOT = Path(__file__).resolve().parents[1]
JSHC = ROOT / "build" / "jshc"


def test_python_cpp_bit_exact(tmp_path: Path):
    """Verify Python's loaded .slut tables agree with scalar, C++26 and Zig kernels."""
    rng = np.random.default_rng(42)
    img = rng.integers(0, 256, (64, 96, 3), dtype=np.uint8)
    in_p = tmp_path / "in.png"

    for m in (17, 25, 33):
        # Create a non-uniform grid to stress-test axis_tables & Q16 fractions
        g = np.linspace(0, 1, m) ** 1.15 * 255.0
        g[0], g[-1] = 0.0, 255.0
        grid = np.stack([g, np.linspace(0, 255, m), g])
        nodes = rng.integers(0, 256, (m, m, m, 3), dtype=np.uint8)
        slut = io.SparseLut(grid, nodes)
        slut_p = tmp_path / f"lut_{m}.slut"
        io.save_sparse(slut_p, slut)
        loaded = io.load_sparse(slut_p)
        for before, after in zip(slut.tables(), loaded.tables()):
            assert np.array_equal(before, after)
        if m == 17:
            # Float32 grid serialization changes the Q16 fraction for channel value 73.
            assert np.any(loaded.frac != io.axis_tables(loaded.grid)[1])
            img[:32, :, 0] = 73

        io.save_image(in_p, img)
        py_out = interp.apply_tetra_q16(loaded, img)
        for k in ("tetra_scalar", "tetra_cpp_simd", "tetra_zig_simd4", "tetra_zig_simd8",
                  "tetra_zig_simd", "tetra_zig_simd16"):
            out_p = tmp_path / f"out_{m}_{k}.png"
            subprocess.run([str(JSHC), "apply", "-i", str(in_p), "-o", str(out_p), "-k", k, str(slut_p)], check=True)
            cpp_out = io.load_image(out_p)
            assert np.array_equal(py_out, cpp_out), f"mismatch for m={m}, kernel={k}"


def test_sparse_reader_rejects_truncated_files(tmp_path: Path):
    p = tmp_path / "bad.slut"
    p.write_bytes(b"SLUT")
    try:
        io.load_sparse(p)
    except ValueError:
        pass
    else:
        raise AssertionError("Python accepted a truncated sparse LUT")
    img = tmp_path / "in.png"
    io.save_image(img, np.zeros((1, 1, 3), np.uint8))
    result = subprocess.run([str(JSHC), "apply", "-i", str(img), "-o", str(tmp_path / "out.png"), str(p)], capture_output=True)
    assert result.returncode == 1
    assert b"truncated slut" in result.stderr


def test_adaptive_models_use_a_separate_cache(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(cli.data, "DATA", tmp_path)
    args = SimpleNamespace(scenario="isp-0", mode="seq", method="ls_tetra_int", m=33, adaptive=False)
    standard = cli.model_dir(args)
    args.adaptive = True
    adaptive = cli.model_dir(args)
    assert standard != adaptive
    assert adaptive.name.endswith("_adaptive")
    standard.mkdir(parents=True)
    (standard / "stage1.slut").write_bytes(b"incomplete")
    calls = []

    def finish_fit(fit_args):
        calls.append(fit_args)
        for stage in (2, 3, 4):
            (standard / f"stage{stage}.slut").write_bytes(b"placeholder")

    monkeypatch.setattr(cli, "cmd_fit", finish_fit)
    args.adaptive = False
    assert len(cli.model_paths(args)) == 4
    assert calls == [args]


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
