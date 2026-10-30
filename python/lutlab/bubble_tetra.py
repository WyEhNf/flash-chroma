"""边界消失的两cell插值研究；不是现有SLUT或ChannelLut原生ABI。"""
from __future__ import annotations
import numpy as np
from numba import njit, prange
from . import channel_coordinates as cc, io

CELLS = (31725, 31726)
KAPPA = 3


@njit(cache=True)
def _acc(nodes, m, ir, ig, ib, x, y, z, c, mask):
    base = (ir*m+ig)*m+ib
    sr, sg, sb = np.int64(m*m), np.int64(m), np.int64(1)
    if mask & 1: base += sr; sr = -sr; x = io.ONE-x
    if mask & 2: base += sg; sg = -sg; y = io.ONE-y
    if mask & 4: base += sb; sb = -sb; z = io.ONE-z
    # 六区域分支与离线oracle的argsort独立实现。
    if x >= y:
        if y >= z: h, t, l, u, v = x, y, z, sr, sg
        elif x >= z: h, t, l, u, v = x, z, y, sr, sb
        else: h, t, l, u, v = z, x, y, sb, sr
    else:
        if x >= z: h, t, l, u, v = y, x, z, sg, sr
        elif y >= z: h, t, l, u, v = y, z, x, sg, sb
        else: h, t, l, u, v = z, y, x, sb, sg
    return ((io.ONE-h)*np.int64(nodes[base, c])+(h-t)*np.int64(nodes[base+u, c])
        +(t-l)*np.int64(nodes[base+u+v, c])+l*np.int64(nodes[base+sr+sg+sb, c]))


@njit(cache=True)
def _value(nodes, m, ir, ig, ib, x, y, z, c):
    acc = _acc(nodes, m, ir, ig, ib, x, y, z, c, 0)
    cell = (ir*(m-1)+ig)*(m-1)+ib
    if cell == CELLS[0] or cell == CELLS[1]:
        t = min(x, y, z, io.ONE-x, io.ONE-y, io.ONE-z)
        w = min(io.ONE, KAPPA*t)
        alt = _acc(nodes, m, ir, ig, ib, x, y, z, c, 1)
        return ((io.ONE-w)*acc+w*alt+(1 << 31)) >> 32
    return (acc+io.ONE//2) >> io.Q


@njit(cache=True, parallel=True)
def _predict(points, nodes, idx, frac, m):
    output = np.empty((len(points), 3), np.uint8)
    for p in prange(len(points)):
        r, g, b = int(points[p, 0]), int(points[p, 1]), int(points[p, 2])
        ir, ig, ib = np.int64(idx[0, r]), np.int64(idx[1, g]), np.int64(idx[2, b])
        for c in range(3):
            output[p, c] = _value(nodes, m, ir, ig, ib,
                np.int64(frac[c, 0, r]), np.int64(frac[c, 1, g]), np.int64(frac[c, 2, b]), c)
    return output


@njit(cache=True, parallel=True)
def explicit_faces(cells, frac, nodes, m):
    """显式cell及每输出独立三轴Q16，用于虚拟共享面的真实坐标截面。"""
    output = np.empty((len(cells), 3), np.uint8)
    for p in prange(len(cells)):
        ir, ig, ib = np.int64(cells[p, 0]), np.int64(cells[p, 1]), np.int64(cells[p, 2])
        for c in range(3):
            output[p, c] = _value(nodes, m, ir, ig, ib,
                np.int64(frac[p, c, 0]), np.int64(frac[p, c, 1]), np.int64(frac[p, c, 2]), c)
    return output


def predict(model, points):
    cc.validate(model)
    if model.m != 33:
        raise ValueError('冻结两cell研究仅接受33节点模型')
    return _predict(points, model.nodes.reshape(-1, 3), model.idx, model.channel_frac, model.m)
