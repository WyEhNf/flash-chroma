"""公共训练mean/p99桥的保守整数根预算，不含RGB查询或求解器。"""
from __future__ import annotations
import math
SCALE = 1 << 20
SAFE = (1 << 62)-1


def root_bounds(q):
    if type(q) is not int or q < 0: raise ValueError('误差平方须为非负整数')
    value = q*SCALE*SCALE; floor = math.isqrt(value)
    return floor, floor+int(floor*floor != value)


def root_sum(hist):
    lo = hi = 0
    for q, count in enumerate(hist):
        count = int(count)
        if count < 0: raise ValueError('完整直方图不得有负质量')
        if count:
            a,b = root_bounds(q); lo += count*a; hi += count*b
    if not 0 <= lo <= hi <= SAFE: raise OverflowError('根和超保守int64界')
    return lo,hi


def above_limit(n):
    if type(n) is not int or n <= 0: raise ValueError('像素数须为正整数')
    upper_rank = (99*(n-1)+99)//100
    return n-upper_rank-1


def classify(minimum, safe_maximum, training_count, dangerous):
    if not 0 <= minimum <= safe_maximum <= 47 or training_count < 0: raise ValueError('安全误差或质量域非法')
    cost = training_count > 0 and minimum < safe_maximum
    flag = training_count > 0 and minimum <= 12 < safe_maximum
    return bool(dangerous or cost), bool(cost), bool(flag)
