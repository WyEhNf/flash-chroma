"""研究插值：原共享cell内按外部方向选择四面体；不属于现有SLUT/ChannelLut ABI。"""
from __future__ import annotations
import numpy as np
from numba import njit, prange
from . import channel_coordinates as cc, io


def validate(model, choices):
    cc.validate(model)
    if choices.shape != ((model.m-1)**3,) or choices.dtype != np.uint8 or not np.all(np.isin(choices, [0, 1, 2, 4])):
        raise ValueError('研究方向场必须为每shared-idx cell一个0/1/2/4 byte；相容性需另验')


@njit(cache=True, parallel=True)
def _design(points, idx, frac, m, choices):
    # 本研究m<=33，物理节点号最多35936；仅离线索引用uint16节约暂态。
    indices = np.empty((3, len(points), 4), np.uint16)
    weights = np.empty((3, len(points), 4), np.int32)
    for p in prange(len(points)):
        r, g, b = int(points[p, 0]), int(points[p, 1]), int(points[p, 2])
        ir, ig, ib = np.int64(idx[0, r]), np.int64(idx[1, g]), np.int64(idx[2, b])
        mask = choices[(ir*(m-1)+ig)*(m-1)+ib]
        base = (ir*m+ig)*m+ib
        sr, sg, sb = np.int64(m*m), np.int64(m), np.int64(1)
        if mask & 1: base += sr; sr = -sr
        if mask & 2: base += sg; sg = -sg
        if mask & 4: base += sb; sb = -sb
        for c in range(3):
            x, y, z = np.int64(frac[c, 0, r]), np.int64(frac[c, 1, g]), np.int64(frac[c, 2, b])
            if mask & 1: x = io.ONE-x
            if mask & 2: y = io.ONE-y
            if mask & 4: z = io.ONE-z
            a, d, e = sr, sg, sb
            if x < y: x, y, a, d = y, x, d, a
            if y < z: y, z, d, e = z, y, e, d
            if x < y: x, y, a, d = y, x, d, a
            indices[c, p, 0], indices[c, p, 1] = base, base+a
            indices[c, p, 2], indices[c, p, 3] = base+a+d, base+sr+sg+sb
            weights[c, p, 0], weights[c, p, 1] = io.ONE-x, x-y
            weights[c, p, 2], weights[c, p, 3] = y-z, z
    return indices, weights


def design(model, points, choices):
    validate(model, choices)
    return _design(points, model.idx, model.channel_frac, model.m, choices)


@njit(cache=True, parallel=True)
def _predict(points, nodes, idx, frac, m, choices):
    output = np.empty((len(points), 3), np.uint8)
    for p in prange(len(points)):
        r, g, b = int(points[p, 0]), int(points[p, 1]), int(points[p, 2])
        ir, ig, ib = np.int64(idx[0, r]), np.int64(idx[1, g]), np.int64(idx[2, b])
        mask = choices[(ir*(m-1)+ig)*(m-1)+ib]
        base = (ir*m+ig)*m+ib
        sr, sg, sb = np.int64(m*m), np.int64(m), np.int64(1)
        if mask & 1: base += sr; sr = -sr
        if mask & 2: base += sg; sg = -sg
        if mask & 4: base += sb; sb = -sb
        for c in range(3):
            x, y, z = np.int64(frac[c, 0, r]), np.int64(frac[c, 1, g]), np.int64(frac[c, 2, b])
            if mask & 1: x = io.ONE-x
            if mask & 2: y = io.ONE-y
            if mask & 4: z = io.ONE-z
            # 六区域分支与设计核的比较器网络分别实现排序。
            if x >= y:
                if y >= z: h, t, l, u, v = x, y, z, sr, sg
                elif x >= z: h, t, l, u, v = x, z, y, sr, sb
                else: h, t, l, u, v = z, x, y, sb, sr
            else:
                if x >= z: h, t, l, u, v = y, x, z, sg, sr
                elif y >= z: h, t, l, u, v = y, z, x, sg, sb
                else: h, t, l, u, v = z, y, x, sb, sg
            value = ((io.ONE-h)*np.int64(nodes[base, c])
                +(h-t)*np.int64(nodes[base+u, c])
                +(t-l)*np.int64(nodes[base+u+v, c])
                +l*np.int64(nodes[base+sr+sg+sb, c]))
            output[p, c] = (value+io.ONE//2) >> io.Q
    return output


def predict(model, points, choices):
    validate(model, choices)
    return _predict(points, model.nodes.reshape(-1, 3), model.idx, model.channel_frac, model.m, choices)
