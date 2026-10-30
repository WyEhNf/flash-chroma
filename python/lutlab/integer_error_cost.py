"""两个独立纯整数方法给平方根差精确ceil及CVaR正超额成本。"""
from __future__ import annotations
import math

SCALE = 1 << 20


def ceil_div(value, divisor):
    if divisor <= 0: raise ValueError('分母必须正')
    return -((-value)//divisor)


def check_inputs(a, b, scale):
    if type(a) is not int or type(b) is not int or type(scale) is not int or min(a, b) < 0 or scale <= 0:
        raise ValueError('需要非负整数被开方数和正整数尺度')


def sqrt_difference_interval(a, b, scale=SCALE):
    check_inputs(a, b, scale)
    if a == b: return 0
    ra, rb = math.isqrt(a), math.isqrt(b)
    if ra*ra == a and rb*rb == b: return scale*(ra-rb)
    for bits in (16, 32, 64, 128, 256, 512, 1024):
        denominator = 1 << bits
        aa, bb = a*denominator**2, b*denominator**2
        la, lb = math.isqrt(aa), math.isqrt(bb)
        ua, ub = la+int(la*la != aa), lb+int(lb*lb != bb)
        lower = ceil_div(scale*(la-ub), denominator); upper = ceil_div(scale*(ua-lb), denominator)
        if lower == upper: return lower
    raise ArithmeticError('区间尚未证明唯一ceil，禁止浮点猜测')


def compare_scaled_difference(a, b, integer, scale=SCALE):
    """返回scale*(sqrt(a)-sqrt(b))与integer比较的精确符号。"""
    check_inputs(a, b, scale)
    if type(integer) is not int: raise ValueError('比较值必须整数')
    if integer < 0: return -compare_scaled_difference(b, a, -integer, scale)
    if integer == 0: return (a > b)-(a < b)
    # 两边均非负时先移项，再只对已知非负量平方，避免引入伪根。
    left = scale*scale*(a-b)-integer*integer
    if left < 0: return -1
    right_squared = 4*integer*integer*scale*scale*b
    if left == 0: return 0 if right_squared == 0 else -1
    difference = left*left-right_squared
    return (difference > 0)-(difference < 0)


def sqrt_difference_squared(a, b, scale=SCALE):
    """独立符号平方判定器二分最小上界，不使用区间根。"""
    check_inputs(a, b, scale)
    bound = scale*(math.isqrt(max(a, b))+1)
    lower, upper = -bound-1, bound
    while lower+1 < upper:
        middle = (lower+upper)//2
        if compare_scaled_difference(a, b, middle, scale) <= 0: upper = middle
        else: lower = middle
    return upper


def excess_difference(a, b, threshold, scale=SCALE, method=sqrt_difference_interval):
    if type(threshold) is not int or threshold < 0: raise ValueError('阈值平方须非负整数')
    if a <= threshold and b <= threshold: return 0
    if a > threshold and b > threshold: return method(a, b, scale)
    if a > threshold: return method(a, threshold, scale)
    return method(threshold, b, scale)


def costs(a, b, uniform_threshold, training_threshold):
    return (sqrt_difference_interval(a, b), a-b,
        int(a > uniform_threshold)-int(b > uniform_threshold),
        int(a > training_threshold)-int(b > training_threshold),
        excess_difference(a, b, uniform_threshold), excess_difference(a, b, training_threshold))
