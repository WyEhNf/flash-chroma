"""Generate publication-ready plots and markdown tables from `experiments/route_sweep.json`."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
EXP_JSON = ROOT / "experiments" / "route_sweep.json"
PLOTS = ROOT / "docs" / "plots"


def main():
    PLOTS.mkdir(parents=True, exist_ok=True)
    d = json.loads(EXP_JSON.read_text())
    lat = d["lattice_routes"]
    nonlat = d["non_lattice_routes"]
    bench = d["cpp_benchmarks"]

    # 1. Accuracy vs Route bar chart on isp-0 (m=17 vs m=33)
    fig, ax = plt.subplots(figsize=(11, 5.2), dpi=160)
    routes_order = [
        "R1_naive_sample_tri",
        "R2_naive_sample_tetra",
        "R4_box_filter_tetra",
        "R5_ls_separable_tri",
        "R7_ls_tetra_exact",
        "R8_ls_tetra_int_refine",
        "R10_adaptive_grid_int",
        "R11_cascade_residual_4stage",
        "R12_cascade_residual_adaptive",
        "R13_composite_1stage_equiv",
        "R14_composite_1stage_adaptive",
    ]
    m17 = {r["route"]: r["mean_de"] for r in lat if r["scenario"] == "isp-0" and r["m"] == 17}
    m33 = {r["route"]: r["mean_de"] for r in lat if r["scenario"] == "isp-0" and r["m"] == 33}
    x = np.arange(len(routes_order))
    w = 0.38
    ax.bar(x - w / 2, [m17.get(k, 0) for k in routes_order], w, label="m = 17 (14.7 KB/LUT)", color="#3b82f6")
    ax.bar(x + w / 2, [m33.get(k, 0) for k in routes_order], w, label="m = 33 (107.8 KB/LUT)", color="#10b981")
    ax.set_xticks(x)
    ax.set_xticklabels([k.replace("_", "\n", 1) for k in routes_order], rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("Mean ΔE (RGB Euclidean Error, lower is better)")
    ax.set_title("ISP-0 4-Stage Pipeline: Mean ΔE Across Lattice Sparsification & Interpolation Routes")
    ax.grid(axis="y", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS / "accuracy_routes_isp0.png")
    plt.close(fig)

    # 2. C++ Throughput bar chart (ms per image vs 1500 ms target)
    fig, ax = plt.subplots(figsize=(9.5, 4.8), dpi=160)
    labels, vals = [], []
    for b in bench:
        if "with_png_io" in b["stage_mode"]:
            continue
        if b["m"] in (17, 33) and b["threads"] in (1, 20):
            labels.append(f"{b['stage_mode']}\nm={b['m']} {b['kernel']}\n{b['threads']}T")
            vals.append(b["apply_ms_mean"])
    y = np.arange(len(labels))
    ax.barh(y, vals, color="#6366f1")
    for idx, v in enumerate(vals):
        ax.text(v + max(vals) * 0.015, idx, f"{v:.3f} ms", va="center", fontsize=8)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("Mean Time per 1024×768 Image (ms) — Target Threshold < 1500 ms")
    ax.set_title("C++17 Execution Speed on 100× 1024×768 Images (4-Stage & 1-Stage Equivalent)")
    ax.set_xlim(0, max(vals) * 1.18)
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOTS / "cpp_throughput.png")
    plt.close(fig)
    print(f"[report] generated plots in {PLOTS}")


if __name__ == "__main__":
    main()
