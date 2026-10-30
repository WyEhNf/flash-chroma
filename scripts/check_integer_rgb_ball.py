"""独立Python整数穷举检查小球交及边界，数值合同不代替真实完整域证书。"""
from pathlib import Path
import itertools
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'python'))
import numpy as np
from lutlab.integer_rgb_ball import intersection


def independent(points, target):
    # 测试点限制在0..8或247..255；完整小立方包含其球交最优点。
    start, stop=(0,16) if int(points.max()) < 128 else (239,256)
    for colour in itertools.product(range(start,stop),repeat=3):
        if all(sum((int(colour[c])-int(p[c]))**2 for c in range(3))<=target for p in points):
            return True
    return False


def main():
    rng=np.random.default_rng(20261024)
    cases=0
    for offset in (0,247):
        for target in (0,1,2,5,58):
            for n in (1,2,4,8):
                for repeat in range(3):
                    points=(rng.integers(0,9,size=(n,3),dtype=np.uint8)+offset).astype(np.uint8)
                    value=intersection(points,target)
                    assert value['feasible']==independent(points,target)
                    assert value['tested']<=value['box_size']
                    if value['feasible']:
                        assert all(sum((int(value['witness'][c])-int(p[c]))**2 for c in range(3))<=target for p in points)
                    else: assert value['tested']==value['box_size']
                    cases+=1
    print(json.dumps({'cases':cases,'independent_python_integer_mismatches':0}))


if __name__=='__main__':main()
