"""Comprehensive multi-route sweep across Naive, Classic, Modern, and Frontier methods.

Evaluates accuracy (mean ΔE, p95 ΔE, p99 ΔE, max ΔE, pass rates across scenarios and
m in {17, 25, 33}), fitting cost, memory footprint, and C++ runtime throughput.
Writes structured JSON to `experiments/route_sweep.json` and logs the entire run in the
independent `logs/` git repository.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from . import cascade, data, fit as fit_mod, interp, io, luts, metrics
from .runlog import Run

ROOT = Path(__file__).resolve().parents[2]
EXP_DIR = ROOT / "experiments"


def _eval_chain_fast(chain: list[io.SparseLut], imgs: list[np.ndarray], gts: list[np.ndarray], kernel: str = "tetra") -> dict:
    if kernel == "tetra":
        def pred_fn(batch):
            x = batch
            for s in chain:
                x = interp.apply_tetra_q16(s, x)
            return x
    elif kernel == "tri":
        stages = [
            np.clip(np.floor(fit_mod.synth_sep(s.nodes.astype(np.float32), s.grid, "hat") + 0.5), 0, 255).astype(np.uint8)
            for s in chain
        ]
        def pred_fn(batch):
            x = batch
            for S in stages:
                x = S[x[..., 0], x[..., 1], x[..., 2]]
            return x
    else:
        raise ValueError(kernel)
    return _eval_preloaded(pred_fn, imgs, gts)


def _eval_preloaded(pred_fn, imgs: list[np.ndarray], gts: list[np.ndarray]) -> dict:
    batch_in = np.stack(imgs, axis=0)
    batch_gt = np.stack(gts, axis=0)
    batch_pred = pred_fn(batch_in)
    diff = batch_pred.astype(np.float32) - batch_gt.astype(np.float32)
    de = np.sqrt(np.sum(diff * diff, axis=-1))  # (B, H, W)
    flat = de.reshape(len(imgs), -1)
    means = flat.mean(axis=1)
    p95s = np.percentile(flat, 95, axis=1)
    p99s = np.percentile(flat, 99, axis=1)
    maxs = flat.max(axis=1)
    return {
        "n_images": len(imgs),
        "mean_de": round(float(np.mean(means)), 4),
        "worst_img_mean_de": round(float(np.max(means)), 4),
        "mean_p95_de": round(float(np.mean(p95s)), 4),
        "mean_p99_de": round(float(np.mean(p99s)), 4),
        "max_pixel_de": round(float(np.max(maxs)), 4),
        "pass_rate_mean_le_1_0": round(float(np.mean(means <= 1.0)), 4),
        "pass_rate_mean_le_2_0": round(float(np.mean(means <= 2.0)), 4),
        "pass_rate_p99_le_3_0": round(float(np.mean(p99s <= 3.0)), 4),
    }


def _eval_sep_basis_chain(tables: list[np.ndarray], m: int, kind: str, imgs: list[np.ndarray], gts: list[np.ndarray]) -> tuple[dict, float]:
    """Fit 4 stages using separable higher-order basis (`bspline2`, `bspline3`, `lagrange3`)
    with quantized uint8 coefficients, and evaluate 4-stage sequential mapping."""
    t0 = time.perf_counter()
    grid = io.uniform_grid(m)
    B = [fit_mod.basis_matrix(grid[a], kind) for a in range(3)]
    stages = []
    for T in tables:
        X = fit_mod.quantize(fit_mod.fit_ls_sep(T, grid, kind))
        Y = np.clip(np.floor(fit_mod.contract(X, *B) + 0.5), 0, 255).astype(np.uint8)
        stages.append(Y)
    fit_s = round(time.perf_counter() - t0, 3)

    def pred_fn(img):
        x = img
        for S in stages:
            x = S[x[..., 0], x[..., 1], x[..., 2]]
        return x

    return _eval_preloaded(pred_fn, imgs, gts), fit_s


def run_all(scenarios: list[str] | None = None, ms: tuple[int, ...] = (17, 25, 33)):
    EXP_DIR.mkdir(parents=True, exist_ok=True)
    if scenarios is None:
        scenarios = luts.DEFAULT_SCENARIOS

    with Run("routes-sweep", {"scenarios": scenarios, "ms": list(ms)}) as run:
        # 1. Ensure dataset and scenarios exist
        if not (data.DATA / "eval.txt").exists():
            data.build_images(seed=0)
        for sid in scenarios:
            data.build_scenario(sid)

        eval_img_paths = (data.DATA / "eval.txt").read_text().splitlines()
        sub_img_paths = [p for p in eval_img_paths if "syn_" in Path(p).name] + [
            p for p in eval_img_paths if "kodim" in Path(p).name
        ][:5]
        all_imgs = [io.load_image(p) for p in eval_img_paths]
        sub_imgs = [io.load_image(p) for p in sub_img_paths]

        results = {"lattice_routes": [], "non_lattice_routes": [], "cpp_benchmarks": [], "full_eval_spotchecks": []}

        # 2. Lattice routes across scenarios and m in {17, 25, 33}
        lattice_configs = [
            ("R1_naive_sample_tri", "seq", "sample", False, "tri", "Naive"),
            ("R2_naive_sample_tetra", "seq", "sample", False, "tetra", "Naive"),
            ("R3_subpixel_sample_tetra", "seq", "sample_interp", False, "tetra", "Naive"),
            ("R4_box_filter_tetra", "seq", "box", False, "tetra", "Classic"),
            ("R5_ls_separable_tri", "seq", "ls_tri", False, "tri", "Classic"),
            ("R6_ls_separable_tetra", "seq", "ls_tri", False, "tetra", "Modern"),
            ("R7_ls_tetra_exact", "seq", "ls_tetra", False, "tetra", "Modern"),
            ("R8_ls_tetra_int_refine", "seq", "ls_tetra_int", False, "tetra", "Modern"),
            ("R9_irls_lp_minimax", "seq", "irls_tetra", False, "tetra", "Modern"),
            ("R10_adaptive_grid_int", "seq", "ls_tetra_int", True, "tetra", "Frontier"),
            ("R11_cascade_residual_4stage", "residual", "ls_tetra_int", False, "tetra", "Frontier"),
            ("R12_cascade_residual_adaptive", "residual", "ls_tetra_int", True, "tetra", "Frontier"),
            ("R13_composite_1stage_equiv", "composite", "ls_tetra_int", False, "tetra", "Frontier"),
            ("R14_composite_1stage_adaptive", "composite", "ls_tetra_int", True, "tetra", "Frontier"),
        ]

        for sid in scenarios:
            sdir = data.scenario_dir(sid)
            tables = [io.load_full(sdir / f"lut{k}.lut256") for k in range(1, 5)]
            comp = io.load_full(sdir / "composite.lut256")
            sub_gts = [io.apply_full(comp, img) for img in sub_imgs]
            print(f"\n=== Scenario: {sid} ===")

            for m in ms:
                if m == 25 and sid not in ("isp-0", "film-0", "stress-0"):
                    continue
                for rname, mode, method, adaptive, kern, family in lattice_configs:
                    if method == "irls_tetra" and sid not in ("isp-0", "stress-0"):
                        continue
                    if adaptive and sid not in ("isp-0", "film-0", "clip-0", "stress-0"):
                        continue
                    if mode == "seq":
                        chain, info = cascade.fit_cascade_sequential(tables, m, method, use_adaptive_grid=adaptive)
                    elif mode == "residual":
                        chain, info = cascade.fit_cascade_residual(tables, m, use_adaptive_grid=adaptive)
                    elif mode == "composite":
                        chain, info = cascade.fit_composite_single(tables, m, method, use_adaptive_grid=adaptive)
                    else:
                        raise ValueError(mode)

                    ev = _eval_chain_fast(chain, sub_imgs, sub_gts, kernel=kern)
                    mem_bytes = len(chain) * (m ** 3 * 3)
                    rec = {
                        "route": rname, "family": family, "scenario": sid, "m": m,
                        "mode": mode, "method": method, "adaptive": adaptive, "kernel": kern,
                        "stages": len(chain), "lut_bytes": mem_bytes,
                        "compression_ratio_vs_4x256": round((4 * 256 ** 3 * 3) / mem_bytes, 1),
                        "fit_s": info["fit_s"], **ev,
                    }
                    results["lattice_routes"].append(rec)
                    print(
                        f"  [{sid} m={m:2d}] {rname:<30} mean_dE={ev['mean_de']:.4f} "
                        f"p99={ev['mean_p99_de']:.4f} max={ev['max_pixel_de']:.2f} fit={info['fit_s']:.2f}s"
                    )

        # 3. Higher-order basis & non-lattice routes (Lagrange, B-spline, Polynomial, Tucker, RBF, MLP, SIREN)
        for sid in ("isp-0", "film-0", "stress-0"):
            sdir = data.scenario_dir(sid)
            tables = [io.load_full(sdir / f"lut{k}.lut256") for k in range(1, 5)]
            comp = io.load_full(sdir / "composite.lut256")
            sub_gts = [io.apply_full(comp, img) for img in sub_imgs]
            print(f"\n=== Non-lattice & Higher-Order Basis Routes ({sid}) ===")

            for m in (17, 33):
                for kind, label in [
                    ("lagrange3", "B1_lagrange_cubic_tensor"),
                    ("bspline2", "B2_bspline_quadratic_tensor"),
                    ("bspline3", "B3_bspline_cubic_tensor"),
                ]:
                    ev, fit_s = _eval_sep_basis_chain(tables, m, kind, sub_imgs, sub_gts)
                    rec = {
                        "route": label, "family": "Classic-Basis", "scenario": sid, "m": m,
                        "fit_s": fit_s, "lut_bytes": 4 * (m ** 3 * 3), **ev,
                    }
                    results["non_lattice_routes"].append(rec)
                    print(f"  [{sid} m={m}] {label:<28} mean_dE={ev['mean_de']:.4f} p99={ev['mean_p99_de']:.4f} max={ev['max_pixel_de']:.2f}")

                for rank in (6, 10):
                    t0 = time.perf_counter()
                    t_chain = []
                    t_bytes = 0
                    for T in tables:
                        slut, tinfo = cascade.fit_tucker_lut(T, m, rank=rank)
                        t_chain.append(slut)
                        t_bytes += tinfo["tucker_bytes_fp16"]
                    fit_s = round(time.perf_counter() - t0, 3)
                    ev = _eval_chain_fast(t_chain, sub_imgs, sub_gts, kernel="tetra")
                    rec = {
                        "route": f"B4_tucker_hosvd_r{rank}", "family": "Low-Rank", "scenario": sid, "m": m,
                        "rank": rank, "fit_s": fit_s, "lut_bytes": t_bytes, **ev,
                    }
                    results["non_lattice_routes"].append(rec)
                    print(f"  [{sid} m={m}] B4_tucker_hosvd_r{rank:<11} mean_dE={ev['mean_de']:.4f} p99={ev['mean_p99_de']:.4f} bytes={t_bytes}")

            for deg in (3, 5):
                t0 = time.perf_counter()
                coefs = [cascade.eval_polynomial(T, deg=deg) for T in tables]
                fit_s = round(time.perf_counter() - t0, 3)

                def poly_fn(img, coefs=coefs):
                    x = img
                    for c, info in coefs:
                        x = cascade.apply_polynomial(c, info["exps"], x)
                    return x

                ev_s = _eval_preloaded(poly_fn, sub_imgs, sub_gts)
                rec = {
                    "route": f"B5_poly3d_deg{deg}", "family": "Classic-Fit", "scenario": sid,
                    "fit_s": fit_s, "lut_bytes": sum(i["bytes"] for _, i in coefs), **ev_s,
                }
                results["non_lattice_routes"].append(rec)
                print(f"  [{sid}] B5_poly3d_deg{deg:<15} mean_dE={ev_s['mean_de']:.4f} max={ev_s['max_pixel_de']:.2f}")

            t0 = time.perf_counter()
            rbfs = [cascade.fit_rbf(T, n_centers=512) for T in tables]
            fit_s = round(time.perf_counter() - t0, 3)

            def rbf_fn(img, rbfs=rbfs):
                x = img
                for m_rbf, _ in rbfs:
                    x = cascade.apply_rbf(m_rbf, x)
                return x

            ev_s = _eval_preloaded(rbf_fn, sub_imgs, sub_gts)
            rec = {
                "route": "B6_rbf_512centers", "family": "ML-Kernel", "scenario": sid,
                "fit_s": fit_s, "lut_bytes": sum(i["bytes"] for _, i in rbfs), **ev_s,
            }
            results["non_lattice_routes"].append(rec)
            print(f"  [{sid}] B6_rbf_512centers           mean_dE={ev_s['mean_de']:.4f} max={ev_s['max_pixel_de']:.2f}")

            try:
                import torch  # noqa: F401
                for siren, tag in [(False, "DL1_mlp_gelu_3x32"), (True, "DL2_siren_3x32")]:
                    t0 = time.perf_counter()
                    mlps = [cascade.fit_mlp_lut(T, hidden=32, layers=3, steps=400, siren=siren) for T in tables]
                    fit_s = round(time.perf_counter() - t0, 3)

                    t_inf0 = time.perf_counter()

                    def mlp_fn(img, mlps=mlps):
                        x = img
                        for m_mlp, _ in mlps:
                            x = cascade.apply_mlp_lut(m_mlp, x)
                        return x

                    ev_s = _eval_preloaded(mlp_fn, sub_imgs, sub_gts)
                    inf_ms = (time.perf_counter() - t_inf0) * 1000.0 / len(sub_imgs)
                    rec = {
                        "route": tag, "family": "DL-Implicit", "scenario": sid,
                        "fit_s": fit_s, "infer_ms_py": round(inf_ms, 2),
                        "lut_bytes": sum(i["bytes_fp32"] for _, i in mlps), **ev_s,
                    }
                    results["non_lattice_routes"].append(rec)
                    print(f"  [{sid}] {tag:<27} mean_dE={ev_s['mean_de']:.4f} max={ev_s['max_pixel_de']:.2f} py_ms={inf_ms:.1f}")
            except ImportError:
                print("  [skip DL routes: torch not installed in this environment]")

        # 4. Full 29-image spot-check on key routes (isp-0 and stress-0)
        for sid in ("isp-0", "stress-0"):
            sdir = data.scenario_dir(sid)
            tables = [io.load_full(sdir / f"lut{k}.lut256") for k in range(1, 5)]
            comp = io.load_full(sdir / "composite.lut256")
            all_gts = [io.apply_full(comp, img) for img in all_imgs]
            for m in (17, 25, 33):
                for mode, method, adaptive in [
                    ("seq", "sample", False),
                    ("seq", "ls_tetra_int", False),
                    ("residual", "ls_tetra_int", True),
                    ("composite", "ls_tetra_int", True),
                ]:
                    if mode == "seq":
                        chain, _ = cascade.fit_cascade_sequential(tables, m, method, use_adaptive_grid=adaptive)
                    elif mode == "residual":
                        chain, _ = cascade.fit_cascade_residual(tables, m, use_adaptive_grid=adaptive)
                    else:
                        chain, _ = cascade.fit_composite_single(tables, m, method, use_adaptive_grid=adaptive)
                    ev = _eval_chain_fast(chain, all_imgs, all_gts, kernel="tetra")
                    results["full_eval_spotchecks"].append({
                        "scenario": sid, "m": m, "mode": mode, "method": method, "adaptive": adaptive, **ev
                    })

        # 5. C++ Performance Benchmarks across kernels, thread counts, m={17,25,33}, and stages={4,1}
        print("\n=== C++ Throughput Benchmarks (100x 1024x768 RGB images) ===")
        sdir = data.scenario_dir("isp-0")
        tables = [io.load_full(sdir / f"lut{k}.lut256") for k in range(1, 5)]
        bench_dir = data.DATA / "models" / "bench_models"
        bench_dir.mkdir(parents=True, exist_ok=True)

        for m in (17, 25, 33):
            chain4, _ = cascade.fit_cascade_sequential(tables, m, "ls_tetra_int")
            paths4 = []
            for idx, s in enumerate(chain4, 1):
                p = bench_dir / f"m{m}_s{idx}.slut"
                io.save_sparse(p, s)
                paths4.append(p)
            paths1 = [paths4[0]]

            for stages_paths, stage_tag in [(paths4, "4stage"), (paths1, "1stage_equiv")]:
                for kern in ("tri_float", "tetra_scalar", "tetra_avx2"):
                    for th in (1, 4, 8, 0):  # 0 = all hardware threads (20)
                        if kern == "tri_float" and th not in (1, 0):
                            continue
                        if m == 25 and th not in (1, 0):
                            continue
                        b = metrics.run_cpp_bench(
                            stages_paths,
                            data.DATA / "bench.txt",
                            kernel=kern,
                            threads=th,
                            reps=7,
                        )
                        b["stage_mode"] = stage_tag
                        results["cpp_benchmarks"].append(b)
                        print(
                            f"  [{stage_tag:<12} m={m:2d} {kern:<12} th={b['threads']:2d}] "
                            f"apply_mean={b['apply_ms_mean']:.4f} ms/img "
                            f"(100 imgs best={b['set_ms_best_rep']:.2f} ms, {b['mpix_per_s']:.1f} MPix/s)"
                        )

        # Also measure end-to-end with PNG write enabled on best 4-stage & 1-stage configs
        for stages_paths, stage_tag in [(paths4, "4stage_m33"), (paths1, "1stage_m33")]:
            b = metrics.run_cpp_bench(
                stages_paths,
                data.DATA / "bench.txt",
                kernel="tetra_avx2",
                threads=0,
                reps=3,
                write_dir=data.DATA / "bench_out",
            )
            b["stage_mode"] = stage_tag + "_with_png_io"
            results["cpp_benchmarks"].append(b)

        out_path = EXP_DIR / "route_sweep.json"
        out_path.write_text(json.dumps(results, indent=2))
        (run.dir / "route_sweep.json").write_text(json.dumps(results, indent=2))
        run.metrics["n_lattice_runs"] = len(results["lattice_routes"])
        run.metrics["n_non_lattice_runs"] = len(results["non_lattice_routes"])
        run.metrics["n_cpp_benchmarks"] = len(results["cpp_benchmarks"])
        print(f"\n[routes] saved complete sweep results to {out_path}")


if __name__ == "__main__":
    run_all()
