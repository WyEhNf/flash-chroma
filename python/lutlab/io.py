"""File formats shared with the C++ side (see cpp/include/jshc/lut.hpp)."""
from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

FULL_SHAPE = (256, 256, 256, 3)
Q = 16
ONE = 1 << Q


# ---------------------------------------------------------------- full LUTs
def save_full(path: str | Path, lut: np.ndarray) -> None:
    assert lut.shape == FULL_SHAPE and lut.dtype == np.uint8
    np.ascontiguousarray(lut).tofile(path)


def load_full(path: str | Path, mmap: bool = False) -> np.ndarray:
    if mmap:
        return np.memmap(path, dtype=np.uint8, mode="r", shape=FULL_SHAPE)
    return np.fromfile(path, dtype=np.uint8).reshape(FULL_SHAPE)


def compose(luts: list[np.ndarray]) -> np.ndarray:
    """Exact composition L_k(...L_2(L_1(x))) as a single 256^3 LUT."""
    out = luts[0].copy()
    for L in luts[1:]:
        for r0 in range(0, 256, 32):  # chunk to bound temporary memory
            blk = out[r0:r0 + 32]
            out[r0:r0 + 32] = L[blk[..., 0], blk[..., 1], blk[..., 2]]
    return out


def apply_full(lut: np.ndarray, img: np.ndarray) -> np.ndarray:
    return lut[img[..., 0], img[..., 1], img[..., 2]]


# ---------------------------------------------------------------- sparse LUTs
@dataclass
class SparseLut:
    grid: np.ndarray   # (3, m) float positions in input units [0, 255]
    nodes: np.ndarray  # (m, m, m, 3) uint8

    @property
    def m(self) -> int:
        return self.grid.shape[1]

    def tables(self) -> tuple[np.ndarray, np.ndarray]:
        return axis_tables(self.grid)


def uniform_grid(m: int) -> np.ndarray:
    g = np.linspace(0.0, 255.0, m)
    return np.stack([g, g, g])


def axis_tables(grid: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """idx (3,256) uint8 cell index, frac (3,256) uint32 Q16 position inside the cell.

    Grid positions must be strictly increasing with grid[0] <= 0 and grid[-1] >= 255.
    """
    m = grid.shape[1]
    x = np.arange(256, dtype=np.float64)
    idx = np.empty((3, 256), np.uint8)
    frac = np.empty((3, 256), np.uint32)
    for a in range(3):
        g = grid[a].astype(np.float64)
        assert np.all(np.diff(g) > 0), "grid must be strictly increasing"
        assert g[0] <= 0 and g[-1] >= 255, "grid must cover [0,255]"
        i = np.clip(np.searchsorted(g, x, side="right") - 1, 0, m - 2)
        f = (x - g[i]) / (g[i + 1] - g[i])
        idx[a] = i
        frac[a] = np.clip(np.floor(f * ONE + 0.5), 0, ONE).astype(np.uint32)
    return idx, frac


def save_sparse(path: str | Path, s: SparseLut) -> None:
    idx, frac = s.tables()
    m = s.m
    assert s.nodes.shape == (m, m, m, 3) and s.nodes.dtype == np.uint8
    with open(path, "wb") as f:
        f.write(b"SLUT")
        f.write(struct.pack("<III", 1, m, 0))
        f.write(s.grid.astype("<f4").tobytes())
        f.write(idx.tobytes())
        f.write(frac.astype("<u4").tobytes())
        f.write(np.ascontiguousarray(s.nodes).tobytes())


def load_sparse(path: str | Path) -> SparseLut:
    b = Path(path).read_bytes()
    assert b[:4] == b"SLUT"
    _, m, _ = struct.unpack("<III", b[4:16])
    o = 16
    grid = np.frombuffer(b, "<f4", 3 * m, o).reshape(3, m).astype(np.float64)
    o += 12 * m + 3 * 256 + 3 * 256 * 4
    nodes = np.frombuffer(b, np.uint8, m ** 3 * 3, o).reshape(m, m, m, 3).copy()
    return SparseLut(grid, nodes)


# ---------------------------------------------------------------- images
def load_image(path: str | Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB"))


def save_image(path: str | Path, img: np.ndarray) -> None:
    Image.fromarray(img).save(path, compress_level=1)
