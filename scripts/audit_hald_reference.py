"""独立Pillow解码及整数有理三线性，核有限热点支撑的原Hald参考。"""
import hashlib
import itertools
import json
from pathlib import Path
import sys
import PIL
from PIL import Image


def interpolate(image,n,rgb,*,witness=False):
    if len(rgb) != 3 or any(type(v) is not int or not 0 <= v <= 255 for v in rgb):raise ValueError("Hald探针必须为RGB8")
    base = [min(v*(n-1)//255,n-2) for v in rgb]
    remainder = [v*(n-1)-255*i for v,i in zip(rgb,base)]
    numerator,corners = [0,0,0],[]
    denominator = 255**3
    for bits in itertools.product((0,1),repeat=3):
        xyz = [a+b for a,b in zip(base,bits)]
        linear = xyz[0]+n*xyz[1]+n*n*xyz[2]
        pixel = [linear%image.width,linear//image.width]
        value = image.getpixel(tuple(pixel))
        weight = 1
        for bit,fraction in zip(bits,remainder):weight *= fraction if bit else 255-fraction
        for c in range(3):numerator[c] += weight*value[c]
        if witness:corners.append({"node_rgb_index":xyz,"pixel_xy":pixel,"rgb":list(value),"weight_numerator":weight})
    output = [max(0,min(255,(2*v+denominator)//(2*denominator))) for v in numerator]
    return {"rgb":rgb,"output":output,"numerator":numerator,"denominator":denominator,"corners":corners} if witness else output


def audit(source,table,n,points,probes):
    source,table = Path(source),Path(table)
    def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
    data = table.read_bytes()
    if len(data) != 3*256**3:raise ValueError("Hald参考表长度错误")
    frozen = sorted({tuple(map(int,p)) for p in points}|set(itertools.product((0,255),repeat=3))|
        {p for rgb in probes for p in itertools.product(*(range(max(0,v-1),min(256,v+2)) for v in rgb))})
    expected,actual,errors = bytearray(),bytearray(),[]
    with Image.open(source) as image:
        if image.mode != "RGB" or image.width != image.height or n**3 != image.width*image.height or image.tag_v2.get(274,1) != 1:
            raise ValueError("独立审计只接受未旋转RGB8方形Hald")
        image.load()
        metadata = {"mode":image.mode,"size":list(image.size),"orientation":image.tag_v2.get(274,1),"icc_applied":False}
        for p in frozen:
            predicted = interpolate(image,n,list(p))
            key = (p[0]*256+p[1])*256+p[2]
            target = list(data[3*key:3*key+3])
            expected.extend(predicted);actual.extend(target)
            if predicted != target and len(errors) < 10:errors.append({"rgb":list(p),"rational":predicted,"cached":target})
        witnesses = [interpolate(image,n,list(p),witness=True) for p in probes]
    mismatch = sum(a != b for a,b in zip(expected,actual))
    return {"verified":mismatch == 0,"source_sha256":digest(source),"table_sha256":digest(table),"grid_size":n,"image":metadata,
        "points":len(frozen),"points_sha256":hashlib.sha256(bytes(v for p in frozen for v in p)).hexdigest(),
        "rational_sha256":hashlib.sha256(expected).hexdigest(),"cached_sha256":hashlib.sha256(actual).hexdigest(),"byte_mismatches":mismatch,"examples":errors,
        "witnesses":witnesses,"python":sys.version,"pillow":PIL.__version__,"verifier_sha256":digest(Path(__file__)),
        "scope":"有限完整热点支撑加冻结探针±1及RGB角点；Pillow独立解码R-fast像素，不复用项目解析/插值/NumPy/Numba，不应用ICC；未审计全部256³或第三方色彩意图"}
