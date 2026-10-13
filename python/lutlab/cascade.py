"""Cascade-aware & non-lattice route implementations.

Includes:
1. Residual compensation (sequential cascade error-absorber): fits stage k against
   (actual inputs produced by stage 1..k-1) -> (true target after stage k), or pulls
   remaining multi-stage error into the final stage.
2. Composite 1-pass equivalence: merges 4x 256^3 LUTs into 1x 256^3 LUT, then fits one
   sparse m^3 LUT.
3. Classical basis / polynomial / RBF / low-rank Tucker approximations.
4. ML / DL routes: MLP (SIREN / ReLU neural implicit LUT) and Tiny Basis Network in PyTorch.
"""
from __future__ import annotations

import time
import numpy as np

from . import fit as fit_mod
from . import interp, io


# ================================================================ 1. Cascade fitting
def _grid_for(T: np.ndarray, m: int, use_adaptive_grid: bool, grid_mode: str | None) -> np.ndarray:
    mode = grid_mode or ("curvature" if use_adaptive_grid else "uniform")
    if mode == "curvature":
        return fit_mod.adaptive_grid(T, m)
    if mode == "error":
        return fit_mod.adaptive_error_grid(T, m)
    if mode == "uniform":
        return io.uniform_grid(m)
    raise ValueError(f"unknown grid mode: {mode}")


def fit_cascade_sequential(
    tables: list[np.ndarray],
    m: int,
    base_method: str = "ls_tetra_int",
    use_adaptive_grid: bool = False,
    grid_mode: str | None = None,
) -> tuple[list[io.SparseLut], dict]:
    """Fit 4 stages sequentially without cross-stage compensation."""
    t0 = time.perf_counter()
    chain = []
    stage_times = []
    for k, T in enumerate(tables):
        grid = _grid_for(T, m, use_adaptive_grid, grid_mode)
        nodes, grid, info = fit_mod.fit(T, m, base_method, grid=grid)
        chain.append(io.SparseLut(grid, nodes))
        stage_times.append(info["fit_s"])
    return chain, {"fit_s": round(time.perf_counter() - t0, 3), "stage_s": stage_times}


def fit_cascade_residual(
    tables: list[np.ndarray],
    m: int,
    stride: int = 4,
    use_adaptive_grid: bool = False,
    tail_beta: float = 0.0,
    grid_mode: str | None = None,
) -> tuple[list[io.SparseLut], dict]:
    """Cascade-aware fitting: each stage k is fitted on the *actual* output distribution
    of stages 1..k-1 against the *exact* stage-k target applied to the true intermediate
    (or final stage against the exact 4-stage composite).

    Specifically:
    - Stages 1..3: fit with `ls_tetra_int` (plus optional adaptive grid).
    - Propagate a subgrid (stride=4 -> 64^3 = 262k points) through stages 1..3
      using exact Q16 tetrahedral interpolation, and also compute the exact 4-stage
      composite target Y_true(x) for every original point x.
    - Stage 4: fit a weighted least-squares problem mapping x^{(3)} -> Y_true(x), blended
      with a regulariser towards the uniform stage-4 fit so unvisited cells stay
      well-behaved, followed by integer coordinate refinement.
    """
    t0 = time.perf_counter()
    chain: list[io.SparseLut] = []
    # Fit stages 0..2 normally
    for k in range(len(tables) - 1):
        T = tables[k]
        grid = _grid_for(T, m, use_adaptive_grid, grid_mode)
        nodes, grid, _ = fit_mod.fit(T, m, "ls_tetra_int", grid=grid)
        chain.append(io.SparseLut(grid, nodes))

    # Build subgrid of input RGB cube and exact 4-stage targets
    v = np.round(np.linspace(0, 255, 256 // stride)).astype(np.uint8)
    pts0 = np.stack(np.meshgrid(v, v, v, indexing="ij"), -1).reshape(-1, 3)
    y_true = pts0.copy()
    for T in tables:
        y_true = T[y_true[:, 0], y_true[:, 1], y_true[:, 2]]

    # Propagate through stages 0..2 using exact Q16 kernel
    x_cur = pts0.copy()
    for s in chain:
        x_cur = interp.apply_tetra_q16(s, x_cur)

    # Prior for stage 3: standard fit on tables[-1]
    T_last = tables[-1]
    grid_last = _grid_for(T_last, m, use_adaptive_grid, grid_mode)
    x0_float, H_prior, b_prior = fit_mod.fit_ls_tetra(T_last, grid_last, stride=stride)

    # Normal equations on actual propagated coordinates x_cur -> y_true
    weights = None
    if tail_beta > 0:
        pilot = io.SparseLut(grid_last, fit_mod.quantize(x0_float))
        y_pilot = interp.apply_tetra_q16(pilot, x_cur)
        err = np.linalg.norm(y_pilot.astype(np.float32) - y_true.astype(np.float32), axis=1)
        scale = max(float(np.percentile(err, 90)), 0.25)
        weights = np.minimum(1.0 + tail_beta * (err / scale) ** 2, 16.0)
    H_data, b_data = fit_mod.normal_equations(x_cur, y_true, weights, grid_last)
    # Blend with a light prior weight (0.05) so cells with few hits remain smooth
    alpha = 0.05
    H_tot = H_data + alpha * H_prior
    b_tot = b_data + alpha * b_prior
    x_sol = fit_mod.solve_spd(H_tot, b_tot, x0_float.reshape(-1, 3), lam=1e-5)
    x_int = fit_mod.int_refine(x_sol, H_tot, b_tot, sweeps=4)
    chain.append(io.SparseLut(grid_last, fit_mod.quantize(x_int.reshape(m, m, m, 3))))
    return chain, {"fit_s": round(time.perf_counter() - t0, 3), "tail_beta": tail_beta}


def fit_composite_single(
    tables: list[np.ndarray],
    m: int,
    method: str = "ls_tetra_int",
    use_adaptive_grid: bool = False,
    grid_mode: str | None = None,
) -> tuple[list[io.SparseLut], dict]:
    """Equivalent 1-stage optimization: compose 4 LUTs into 1 exact 256^3 LUT, then
    sparsify into a single m^3 LUT."""
    t0 = time.perf_counter()
    comp = io.compose(tables)
    grid = _grid_for(comp, m, use_adaptive_grid, grid_mode)
    nodes, grid, info = fit_mod.fit(comp, m, method, grid=grid)
    return [io.SparseLut(grid, nodes)], {
        "fit_s": round(time.perf_counter() - t0, 3),
        "inner_fit_s": info["fit_s"],
    }


# ================================================================ 2. Classical & Matrix / Basis routes
def eval_polynomial(T: np.ndarray, deg: int = 4, stride: int = 4) -> tuple[np.ndarray, dict]:
    """Global 3D polynomial regression of degree `deg` (monomial basis up to i+j+k <= deg)."""
    t0 = time.perf_counter()
    v = np.arange(0, 256, stride, dtype=np.float32) / 255.0
    pts = np.stack(np.meshgrid(v, v, v, indexing="ij"), -1).reshape(-1, 3)
    Y = T[::stride, ::stride, ::stride].reshape(-1, 3).astype(np.float32)

    exps = [
        (i, j, k)
        for i in range(deg + 1)
        for j in range(deg + 1 - i)
        for k in range(deg + 1 - i - j)
    ]

    def design(P):
        cols = [
            (P[:, 0] ** i) * (P[:, 1] ** j) * (P[:, 2] ** k) for (i, j, k) in exps
        ]
        return np.stack(cols, axis=1)

    A = design(pts)
    coef, _, _, _ = np.linalg.lstsq(A, Y, rcond=None)
    fit_s = time.perf_counter() - t0
    return coef, {"deg": deg, "n_terms": len(exps), "exps": exps, "fit_s": round(fit_s, 3), "bytes": coef.nbytes}


def apply_polynomial(coef: np.ndarray, exps: list[tuple[int, int, int]], img: np.ndarray) -> np.ndarray:
    P = img.reshape(-1, 3).astype(np.float32) / 255.0
    out = np.zeros_like(P)
    for idx, (i, j, k) in enumerate(exps):
        term = (P[:, 0] ** i) * (P[:, 1] ** j) * (P[:, 2] ** k)
        out += term[:, None] * coef[idx : idx + 1, :]
    return np.clip(np.floor(out + 0.5), 0, 255).astype(np.uint8).reshape(img.shape)


def fit_tucker_lut(T: np.ndarray, m: int, rank: int = 8) -> tuple[io.SparseLut, dict]:
    """Low-rank Tucker HOSVD decomposition on the m^3 lattice (tests 'matrix low-rank decomposition').
    Returns a SparseLut whose nodes are reconstructed from the rank-(R,R,R) Tucker core + factors."""
    t0 = time.perf_counter()
    grid = io.uniform_grid(m)
    X_full, _, _ = fit_mod.fit_ls_tetra(T, grid, stride=2)  # (m, m, m, 3) float
    recon = np.empty_like(X_full)
    for c in range(3):
        M0 = X_full[..., c]
        U0, _, _ = np.linalg.svd(M0.reshape(m, -1), full_matrices=False)
        U1, _, _ = np.linalg.svd(np.moveaxis(M0, 1, 0).reshape(m, -1), full_matrices=False)
        U2, _, _ = np.linalg.svd(np.moveaxis(M0, 2, 0).reshape(m, -1), full_matrices=False)
        u0, u1, u2 = U0[:, :rank], U1[:, :rank], U2[:, :rank]
        core = np.einsum("ia,jb,kc,ijk->abc", u0, u1, u2, M0)
        recon[..., c] = np.einsum("ia,jb,kc,abc->ijk", u0, u1, u2, core)
    # Parameter count per channel: rank^3 + 3*m*rank floats (or int16)
    raw_params = 3 * (rank ** 3 + 3 * m * rank)
    return io.SparseLut(grid, fit_mod.quantize(recon)), {
        "fit_s": round(time.perf_counter() - t0, 3),
        "rank": rank,
        "tucker_params": raw_params,
        "tucker_bytes_fp16": raw_params * 2,
    }


def fit_rbf(T: np.ndarray, n_centers: int = 216, stride: int = 8) -> tuple[dict, dict]:
    """Radial Basis Function (Gaussian + linear tail) approximation in 3D RGB space."""
    t0 = time.perf_counter()
    k = max(2, round(n_centers ** (1 / 3)))
    g = np.linspace(0, 1, k, dtype=np.float32)
    centers = np.stack(np.meshgrid(g, g, g, indexing="ij"), -1).reshape(-1, 3)
    sigma = 1.0 / (k - 1)
    c_norm2 = np.sum(centers * centers, axis=1, keepdims=True).T  # (1, K)

    v = np.round(np.linspace(0, 255, 256 // stride)).astype(np.intp)
    vf = v.astype(np.float32) / 255.0
    pts = np.stack(np.meshgrid(vf, vf, vf, indexing="ij"), -1).reshape(-1, 3)
    Y = T[np.ix_(v, v, v)].reshape(-1, 3).astype(np.float32)

    def feat(P):
        p_norm2 = np.sum(P * P, axis=1, keepdims=True)
        d2 = np.maximum(p_norm2 + c_norm2 - 2.0 * (P @ centers.T), 0.0)
        phi = np.exp(-0.5 * d2 / (sigma ** 2))
        return np.concatenate([phi, P, np.ones((len(P), 1), np.float32)], axis=1)

    A = feat(pts)
    ATA = A.T @ A + 1e-4 * np.eye(A.shape[1], dtype=np.float32)
    W = np.linalg.solve(ATA, A.T @ Y)
    fit_s = time.perf_counter() - t0
    model = {"centers": centers, "c_norm2": c_norm2, "sigma": float(sigma), "W": W}
    return model, {
        "n_centers": len(centers),
        "fit_s": round(fit_s, 3),
        "bytes": int(centers.nbytes + W.nbytes),
    }


def apply_rbf(model: dict, img: np.ndarray) -> np.ndarray:
    P = img.reshape(-1, 3).astype(np.float32) / 255.0
    centers, c_norm2, sigma, W = model["centers"], model["c_norm2"], model["sigma"], model["W"]
    out = np.empty_like(P, dtype=np.uint8)
    chunk = 131072
    for s in range(0, len(P), chunk):
        Pc = P[s : s + chunk]
        p_norm2 = np.sum(Pc * Pc, axis=1, keepdims=True)
        d2 = np.maximum(p_norm2 + c_norm2 - 2.0 * (Pc @ centers.T), 0.0)
        phi = np.exp(-0.5 * d2 / (sigma ** 2))
        F = np.concatenate([phi, Pc, np.ones((len(Pc), 1), np.float32)], axis=1)
        y = F @ W
        out[s : s + chunk] = np.clip(np.floor(y + 0.5), 0, 255).astype(np.uint8)
    return out.reshape(img.shape)


# ================================================================ 3. ML / DL routes (PyTorch)
def fit_mlp_lut(
    T: np.ndarray,
    hidden: int = 32,
    layers: int = 3,
    steps: int = 300,
    batch_size: int = 8192,
    siren: bool = False,
    seed: int = 0,
) -> tuple[dict, dict]:
    """Train an ultra-lightweight MLP / SIREN to approximate a 3D LUT (3 -> hidden -> ... -> 3)
    with residual identity connection y = clip(x + net(x)).
    Exports numpy weights so inference can run both in PyTorch and in vectorised NumPy/BLAS."""
    import torch
    import torch.nn as nn

    torch.set_num_threads(4)
    torch.manual_seed(seed)
    t0 = time.perf_counter()

    class Net(nn.Module):
        def __init__(self):
            super().__init__()
            mods = []
            d_in = 3
            for l in range(layers - 1):
                lin = nn.Linear(d_in, hidden)
                if siren:
                    w0 = 30.0 if l == 0 else 1.0
                    with torch.no_grad():
                        bound = (1.0 / d_in) if l == 0 else (np.sqrt(6.0 / d_in) / w0)
                        lin.weight.uniform_(-bound, bound)
                mods.append(lin)
                d_in = hidden
            self.hidden = nn.ModuleList(mods)
            self.out = nn.Linear(hidden, 3)
            self.siren = siren

        def forward(self, x):
            h = x
            for idx, lin in enumerate(self.hidden):
                z = lin(h)
                if self.siren:
                    w0 = 30.0 if idx == 0 else 1.0
                    h = torch.sin(w0 * z)
                else:
                    h = torch.nn.functional.gelu(z)
            return x * 255.0 + self.out(h)

    v = np.round(np.linspace(0, 255, 32)).astype(np.intp)
    vf = v.astype(np.float32) / 255.0
    pts = np.stack(np.meshgrid(vf, vf, vf, indexing="ij"), -1).reshape(-1, 3)
    Y = T[np.ix_(v, v, v)].reshape(-1, 3).astype(np.float32)

    X_t = torch.from_numpy(pts)
    Y_t = torch.from_numpy(Y)
    net = Net()
    opt = torch.optim.Adam(net.parameters(), lr=3e-3)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=steps, eta_min=1e-4)
    N = len(X_t)
    for _ in range(steps):
        idx = torch.randint(0, N, (batch_size,))
        pred = net(X_t[idx])
        loss = torch.mean((pred - Y_t[idx]) ** 2)
        opt.zero_grad()
        loss.backward()
        opt.step()
        sched.step()

    weights = []
    n_params = 0
    for lin in list(net.hidden) + [net.out]:
        W = lin.weight.detach().numpy().T.copy()
        b = lin.bias.detach().numpy().copy()
        weights.append((W, b))
        n_params += W.size + b.size

    fit_s = time.perf_counter() - t0
    return {"weights": weights, "siren": siren}, {
        "hidden": hidden,
        "layers": layers,
        "siren": siren,
        "params": n_params,
        "bytes_fp32": n_params * 4,
        "fit_s": round(fit_s, 3),
    }


def apply_mlp_lut(model: dict, img: np.ndarray) -> np.ndarray:
    """Evaluate trained MLP/SIREN directly on image pixels."""
    P = img.reshape(-1, 3).astype(np.float32) / 255.0
    weights = model["weights"]
    siren = model["siren"]
    h = P
    for idx, (W, b) in enumerate(weights[:-1]):
        z = h @ W + b
        if siren:
            w0 = 30.0 if idx == 0 else 1.0
            h = np.sin(w0 * z)
        else:
            # fast tanh gelu approx
            h = 0.5 * z * (1.0 + np.tanh(0.79788456 * (z + 0.044715 * z * z * z)))
    W_out, b_out = weights[-1]
    y = P * 255.0 + (h @ W_out + b_out)
    return np.clip(np.floor(y + 0.5), 0, 255).astype(np.uint8).reshape(img.shape)
