"""本地研究用LLVM CPU内核；计时不与既有C++/CUDA记录混排。"""
import numpy as np
from numba import njit, prange


@njit(cache=True, inline="always")
def pixel(nodes, idx, frac, m, r, g, b, kind):
    base = (idx[0, r] * m + idx[1, g]) * m + idx[2, b]
    x, y, z = frac[0, r], frac[1, g], frac[2, b]
    a, b_out, c_out = 0., 0., 0.
    if kind == 2 or kind == 3:
        offset = 0
        if kind == 2:
            offset = (int(x >= .5) * m + int(y >= .5)) * m + int(z >= .5)
        else:
            offset = (int(x >= 1.) * m + int(y >= 1.)) * m + int(z >= 1.)
        return float(nodes[base + offset, 0]), float(nodes[base + offset, 1]), float(nodes[base + offset, 2])
    elif kind == 0:
        s1, s2, s3 = m * m, m, 1
        if x < y:
            x, y, s1, s2 = y, x, s2, s1
        if y < z:
            y, z, s2, s3 = z, y, s3, s2
        if x < y:
            x, y, s1, s2 = y, x, s2, s1
        w0, w1, w2, w3 = 1-x, x-y, y-z, z
        i0, i1, i2, i3 = base, base+s1, base+s1+s2, base+m*m+m+1
        return (w0*nodes[i0,0]+w1*nodes[i1,0]+w2*nodes[i2,0]+w3*nodes[i3,0],
                w0*nodes[i0,1]+w1*nodes[i1,1]+w2*nodes[i2,1]+w3*nodes[i3,1],
                w0*nodes[i0,2]+w1*nodes[i1,2]+w2*nodes[i2,2]+w3*nodes[i3,2])
    elif kind == 4:
        # 固定B方向挤出的三角棱柱，六节点，区别于四面体四节点。
        side = m * m if x >= y else m
        high, low = max(x, y), min(x, y)
        for db in range(2):
            weight = z if db else 1 - z
            i0, i1, i2 = base+db, base+side+db, base+m*m+m+db
            a += weight*((1-high)*nodes[i0,0]+(high-low)*nodes[i1,0]+low*nodes[i2,0])
            b_out += weight*((1-high)*nodes[i0,1]+(high-low)*nodes[i1,1]+low*nodes[i2,1])
            c_out += weight*((1-high)*nodes[i0,2]+(high-low)*nodes[i1,2]+low*nodes[i2,2])
    else:
        for dr in range(2):
            for dg in range(2):
                for db in range(2):
                    weight = (x if dr else 1 - x) * (y if dg else 1 - y) * (z if db else 1 - z)
                    node = base + (dr * m + dg) * m + db
                    a += weight*nodes[node,0]
                    b_out += weight*nodes[node,1]
                    c_out += weight*nodes[node,2]
    return a, b_out, c_out


@njit(cache=True, parallel=True)
def map_pixels(rgb, nodes, idx, frac, m, kind):
    output = np.empty(rgb.shape, np.uint8)
    for i in prange(len(rgb)):
        value = pixel(nodes, idx, frac, m, int(rgb[i, 0]), int(rgb[i, 1]), int(rgb[i, 2]), kind)
        for c in range(3):
            output[i, c] = min(255, max(0, int(np.floor(value[c] + .5))))
    return output


@njit(cache=True, parallel=True)
def expand_cube(nodes, idx, frac, m, kind):
    output = np.empty((256 ** 3, 3), np.uint8)
    for i in prange(256 ** 3):
        value = pixel(nodes, idx, frac, m, i >> 16, (i >> 8) & 255, i & 255, kind)
        for c in range(3):
            output[i, c] = min(255, max(0, int(np.floor(value[c] + .5))))
    return output


@njit(cache=True, parallel=True)
def image_metrics(images, truth, nodes, idx, frac, m, kind):
    # 每张图片单独累加平方色差直方图，返回精确的逐图分位数。
    summary = np.empty((len(images), 8), np.float64)
    for j in prange(len(images)):
        hist = np.zeros(3 * 255 * 255 + 1, np.int64)
        for i in range(images.shape[1]):
            r, g, b = int(images[j, i, 0]), int(images[j, i, 1]), int(images[j, i, 2])
            value = pixel(nodes, idx, frac, m, r, g, b, kind)
            d2 = 0
            for c in range(3):
                q = min(255, max(0, int(np.floor(value[c] + .5))))
                difference = q - int(truth[(r * 256 + g) * 256 + b, c])
                d2 += difference * difference
            hist[d2] += 1
        n = images.shape[1]
        rank = .99 * (n - 1)
        lo, hi = int(np.floor(rank)), int(np.ceil(rank))
        total, squares, cumulative, p_lo, p_hi, maximum = 0., 0., 0, 0., 0., 0.
        exceed = np.zeros(4, np.int64)
        for d2 in range(len(hist)):
            count = hist[d2]
            if count == 0:
                continue
            distance = np.sqrt(d2)
            total += count * distance
            squares += count * d2
            if cumulative <= lo < cumulative + count:
                p_lo = distance
            if cumulative <= hi < cumulative + count:
                p_hi = distance
            cumulative += count
            maximum = distance
            for k in range(4):
                if distance >= (1., 2., 3., 5.)[k]:
                    exceed[k] += count
        summary[j, 0] = total / n
        summary[j, 1] = np.sqrt(squares / n)
        summary[j, 2] = p_lo + (rank - lo) * (p_hi - p_lo)
        summary[j, 3] = maximum
        for k in range(4):
            summary[j, 4 + k] = exceed[k] / n
    return summary
