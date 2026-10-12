"""Synthetic 256^3 integer LUT generators.

The official LUTs are unknown. We build 4-stage pipelines that mimic the kinds of colour
operations an ISP / camera app / in-car streaming stack applies (white balance + CCM, tone
curves, saturation/vibrance, local hue edits, film looks), plus deliberately hard cases
(hard clipping, posterisation) to measure where sparse lattices break down.
All ops take float arrays (..., 3) in [0, 1] and return the same shape.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

import numpy as np

# ---------------------------------------------------------------- helpers
_LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)


def s2l(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def l2s(x):
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def to_ycc(x):
    y = x @ _LUMA
    cb = (x[..., 2] - y) / 1.8556
    cr = (x[..., 0] - y) / 1.5748
    return y, cb, cr


def from_ycc(y, cb, cr):
    r = y + 1.5748 * cr
    b = y + 1.8556 * cb
    g = (y - _LUMA[0] * r - _LUMA[2] * b) / _LUMA[1]
    return np.stack([r, g, b], -1)


# ---------------------------------------------------------------- operations
def op_wb_ccm(x, gains, ccm):
    lin = s2l(x) * np.asarray(gains, np.float32)
    lin = lin @ np.asarray(ccm, np.float32).T
    return l2s(lin)


def op_tone(x, contrast=1.2, pivot=0.45, gamma=1.0, lift=0.0, gain=1.0):
    # normalised logistic S-curve per channel, then lift/gamma/gain
    def s(v):
        return 1 / (1 + np.exp(-contrast * 4 * (v - pivot)))
    lo, hi = s(0.0), s(1.0)
    y = (s(x) - lo) / (hi - lo)
    y = np.power(np.clip(y, 0, 1), gamma)
    return lift + (gain - lift) * y


def op_saturation(x, sat=1.2, vibrance=0.0):
    y = (x @ _LUMA)[..., None]
    c = x - y
    chroma = np.abs(c).max(-1, keepdims=True)
    k = sat * (1 + vibrance * (1 - smoothstep(0.0, 0.5, chroma)))
    return y + c * k


def op_hue_local(x, center_deg, width_deg, shift_deg, sat_gain=1.0, min_chroma=0.02):
    y, cb, cr = to_ycc(x)
    hue = np.degrees(np.arctan2(cr, cb))
    chroma = np.hypot(cb, cr)
    dh = (hue - center_deg + 180) % 360 - 180
    w = np.exp(-0.5 * (dh / width_deg) ** 2) * smoothstep(min_chroma, 3 * min_chroma, chroma)
    ang = np.radians(shift_deg) * w
    k = 1 + (sat_gain - 1) * w
    cb2 = (cb * np.cos(ang) - cr * np.sin(ang)) * k
    cr2 = (cb * np.sin(ang) + cr * np.cos(ang)) * k
    return from_ycc(y, cb2, cr2)


def op_filmic(x, exposure=1.0):
    v = s2l(x) * exposure
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14
    return l2s((v * (a * v + b)) / (v * (c * v + d) + e))


def op_split_tone(x, shadow=(0.0, 0.05, 0.12), highlight=(0.10, 0.05, -0.05), amount=1.0):
    y = (x @ _LUMA)[..., None]
    sh = np.asarray(shadow, np.float32) * (1 - y) ** 2
    hl = np.asarray(highlight, np.float32) * y ** 2
    return x + amount * (sh + hl)


def op_warp(x, amp, k_vecs, phases, dirs):
    out = x.copy()
    for k, p, d in zip(k_vecs, phases, dirs):
        out += amp * np.sin(2 * np.pi * (x @ np.asarray(k, np.float32)) + p)[..., None] * np.asarray(d, np.float32)
    return out


def op_posterize(x, levels=32):
    return np.round(x * (levels - 1)) / (levels - 1)


OPS = {
    "wb_ccm": op_wb_ccm, "tone": op_tone, "saturation": op_saturation, "hue_local": op_hue_local,
    "filmic": op_filmic, "split_tone": op_split_tone, "warp": op_warp, "posterize": op_posterize,
}


@dataclass
class Stage:
    ops: list[tuple[str, dict]] = field(default_factory=list)

    def __call__(self, x):
        for name, kw in self.ops:
            x = OPS[name](x, **kw)
        return np.clip(x, 0.0, 1.0)


def build_lut(stage: Stage) -> np.ndarray:
    """Evaluate a stage on every 8-bit colour and quantise to uint8."""
    v = np.arange(256, dtype=np.float32) / 255.0
    out = np.empty((256, 256, 256, 3), np.uint8)
    gg, bb = np.meshgrid(v, v, indexing="ij")
    for r in range(0, 256, 16):
        rr = v[r:r + 16][:, None, None]
        x = np.stack(np.broadcast_arrays(rr, gg[None], bb[None]), -1).astype(np.float32)
        y = stage(x)
        out[r:r + 16] = np.clip(np.floor(y * 255.0 + 0.5), 0, 255).astype(np.uint8)
    return out


# ---------------------------------------------------------------- scenarios
def _ccm(rng, strength):
    off = rng.uniform(-strength, strength, (3, 3))
    np.fill_diagonal(off, 0)
    M = np.eye(3) + off
    M -= np.diag(M.sum(1) - 1)  # rows sum to 1 -> preserves neutrals
    return M.tolist()


def scenario(name: str, seed: int) -> list[Stage]:
    rng = np.random.default_rng(seed)
    u = rng.uniform
    if name == "isp":
        return [
            Stage([("wb_ccm", dict(gains=[u(0.85, 1.25), 1.0, u(0.8, 1.3)], ccm=_ccm(rng, 0.25)))]),
            Stage([("tone", dict(contrast=u(1.0, 1.4), pivot=u(0.4, 0.5), gamma=u(0.9, 1.1)))]),
            Stage([("saturation", dict(sat=u(1.05, 1.3), vibrance=u(0.0, 0.3)))]),
            Stage([("hue_local", dict(center_deg=u(100, 140), width_deg=20, shift_deg=u(-8, 8), sat_gain=0.9)),
                   ("hue_local", dict(center_deg=u(-60, -30), width_deg=25, shift_deg=u(-10, 10), sat_gain=1.15))]),
        ]
    if name == "film":
        return [
            Stage([("filmic", dict(exposure=u(1.2, 1.8)))]),
            Stage([("split_tone", dict(amount=u(0.6, 1.2)))]),
            Stage([("hue_local", dict(center_deg=u(110, 130), width_deg=30, shift_deg=u(10, 20), sat_gain=1.2)),
                   ("hue_local", dict(center_deg=u(-70, -50), width_deg=30, shift_deg=u(-20, -10), sat_gain=1.3))]),
            Stage([("tone", dict(contrast=u(0.8, 1.1), lift=u(0.03, 0.08), gain=u(0.92, 0.98)))]),
        ]
    if name == "warp":
        def w():
            return ("warp", dict(amp=u(0.02, 0.05), k_vecs=rng.uniform(-1.5, 1.5, (3, 3)).tolist(),
                                 phases=rng.uniform(0, 6.28, 3).tolist(), dirs=rng.normal(size=(3, 3)).tolist()))
        return [Stage([w()]) for _ in range(4)]
    if name == "clip":
        return [
            Stage([("wb_ccm", dict(gains=[u(1.3, 1.6), 1.0, u(0.6, 0.8)], ccm=_ccm(rng, 0.5)))]),
            Stage([("tone", dict(contrast=u(1.8, 2.4), pivot=0.45))]),
            Stage([("saturation", dict(sat=u(1.5, 1.8), vibrance=0.3))]),
            Stage([("hue_local", dict(center_deg=0, width_deg=15, shift_deg=30, sat_gain=1.5))]),
        ]
    if name == "stress":
        return [
            Stage([("tone", dict(contrast=1.3))]),
            Stage([("posterize", dict(levels=24))]),
            Stage([("hue_local", dict(center_deg=120, width_deg=10, shift_deg=40, sat_gain=1.6))]),
            Stage([("saturation", dict(sat=1.4))]),
        ]
    raise KeyError(name)


DEFAULT_SCENARIOS = ["isp-0", "isp-1", "film-0", "warp-0", "clip-0", "stress-0"]


def parse_scenario(sid: str) -> tuple[str, int]:
    name, seed = sid.rsplit("-", 1)
    return name, int(seed)


def describe(stages: list[Stage]) -> str:
    return json.dumps([s.ops for s in stages], default=float)
