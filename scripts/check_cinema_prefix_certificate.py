"""不调用球交实现，以Python整数循环复核真实证书每个RGB8候选。"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'python'))
import numpy as np
from lutlab import io,channel_coordinates as cc
from run_channel_tail_nodes import load_model


def python_pixel(model,point):
    # 独立Python任意精度整数，按坐标排序定义重建四面体，不调用Numba或uint64 oracle。
    m=model.m;nodes=model.nodes.reshape(-1,3);strides=[m*m,m,1]
    base=sum(int(model.idx[a,point[a]])*strides[a] for a in range(3));result=[]
    for channel in range(3):
        frac=[int(model.channel_frac[channel,a,point[a]]) for a in range(3)]
        order=sorted(range(3),key=lambda a:(-frac[a],a));x,y,z=[frac[a] for a in order]
        vertex=[base,base+strides[order[0]],base+strides[order[0]]+strides[order[1]],base+sum(strides)]
        weights=[65536-x,x-y,y-z,z]
        result.append((sum(w*int(nodes[v,channel]) for w,v in zip(weights,vertex))+32768)//65536)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('folder',type=Path)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖独立复核记录')
    identity=json.loads((args.folder/'run.json').read_text(encoding='utf-8'));inputs=identity['inputs']
    for name in ('first','stage2','reference'):
        with Path(inputs[name]['path']).open('rb') as stream:
            assert hashlib.file_digest(stream,'sha256').hexdigest()==inputs[name]['sha256']
    first=load_model(Path(inputs['first']['path']))
    second=cc.from_sparse(io.load_sparse(Path(inputs['stage2']['path']),competition=True))
    reference=np.load(inputs['reference']['path'],mmap_mode='r')
    assert reference.dtype==np.uint8 and reference.shape==(256**3,3)
    checked=[];membership=0
    for prefix in (1,2):
        path=args.folder/f'prefix-{prefix}.json'
        report=json.loads(path.read_text(encoding='utf-8'));infeasible=0;tested=0;simple_pairs=[]
        assert report['prefix_stages']==prefix
        for group in report['groups']:
            points=group['reference_rgb'];target=58;radius=math.isqrt(target)
            assert len(points)==len(group['source_rgb_codes'])==len(group['uniform_frequency'])
            for point,source,frequency in zip(points,group['source_rgb_codes'],group['uniform_frequency']):
                assert 0<=source<256**3 and frequency>0
                assert point==reference[source].tolist()
                value=python_pixel(first,[source>>16,(source>>8)&255,source&255])
                if prefix==2:value=python_pixel(second,value)
                assert value==group['arrived_rgb'];membership+=1
            lo=[max(0,max(p[c] for p in points)-radius) for c in range(3)]
            hi=[min(255,min(p[c] for p in points)+radius) for c in range(3)]
            result=group['intersection_at_58']
            assert lo==result['lo'] and hi==result['hi']
            feasible=False;visited=0;witness=None
            for colour in itertools.product(*(range(lo[c],hi[c]+1) for c in range(3))):
                visited+=1
                if all(sum((colour[c]-p[c])**2 for c in range(3))<=target for p in points):
                    feasible=True;witness=list(colour);break
            assert feasible==result['feasible'] and visited==result['tested'] and witness==result['witness']
            tested+=visited;infeasible+=int(not feasible)
            current=group['current_output']
            assert max(sum((current[c]-p[c])**2 for c in range(3)) for p in points)==59
            # 任意两参考点距离大于2sqrt(58)时，连续球已无交，可给更短的附加证据。
            found=None
            for i,a in enumerate(points):
                for j,b in enumerate(points[:i]):
                    d2=sum((a[c]-b[c])**2 for c in range(3))
                    if d2>4*target:found={'reference_indices':[j,i],'pair_distance_squared':d2};break
                if found:break
            if found:simple_pairs.append({'arrived_rgb':group['arrived_rgb'],**found})
        assert infeasible==report['infeasible_groups']
        assert report['fixed_prefix_max_squared_lower_bound']==(59 if infeasible else None)
        checked.append({'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'groups':len(report['groups']),'infeasible_groups':infeasible,'tested_integer_rgb_candidates':tested,
            'additional_pair_certificates':simple_pairs})
    if len(checked)!=2:raise AssertionError('缺少两个冻结前缀')
    args.output.write_text(json.dumps({'independent_python_integer_checks':checked,'independent_source_memberships':membership,'mismatches':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(checked,ensure_ascii=False))


if __name__=='__main__':main()
