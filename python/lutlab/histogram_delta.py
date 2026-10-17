"""先抵消相同频数，再用有符号Q24整数界证明RGB距离和非增。"""
import math


def mean_difference(reference,candidate):
    def checked(pairs):
        if (not pairs or any(type(d) is not int or type(n) is not int or not 0 <= d <= 3*255**2 or n <= 0 for d,n in pairs)
                or [d for d,n in pairs] != sorted(set(d for d,n in pairs))):
            raise ValueError("差值证书要求有序、唯一的RGB平方误差频数")
        n = sum(count for d,count in pairs)
        if not 0 < n <= 1 << 30:raise ValueError("距离差值像素数超出冻结频数范围")
        return n,dict(pairs)
    n,old = checked(reference)
    count,new = checked(candidate)
    if count != n:raise ValueError("不同像素数的距离和不能作为mean差值比较")
    lower,upper,changes = 0,0,[]
    for d in sorted(old.keys() | new.keys()):
        delta = new.get(d,0)-old.get(d,0)
        if not delta:continue
        lo = math.isqrt(d << 48)
        hi = lo+int(lo*lo != d << 48)
        lower += delta*(lo if delta > 0 else hi)
        upper += delta*(hi if delta > 0 else lo)
        changes.append([d,delta])
    return {"n":n,"precision_bits":24,"delta_lower_q24":str(lower),"delta_upper_q24":str(upper),
        "changed_counts":changes,"accepted":upper <= 0,"scope":"固定同像素数距离和差值的充分非增证书；未变项精确抵消，剩余有符号根号界仍可能保守；未改变mean门槛"}
