"""仅标准库：独立聚合Emerald既有记录与逐轴曲线，不新增模型或全域前向。"""
from __future__ import annotations
import argparse
import ast
from collections import Counter
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import platform
import struct


def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def npy_rgb8(path):
    data=path.read_bytes()
    assert data[:6]==b'\x93NUMPY'
    major=data[6]
    n=struct.unpack_from('<H' if major==1 else '<I',data,8)[0]
    offset=10 if major==1 else 12
    header=ast.literal_eval(data[offset:offset+n].decode('latin1'))
    assert header['descr']=='|u1' and header['shape']==(256,256,256,3) and not header['fortran_order']
    payload=data[offset+n:]
    assert len(payload)==256**3*3
    return payload


def curve_histogram(model,reference):
    data=model.read_bytes();assert data[:4]==b'SLUT'
    version,m,reserved=struct.unpack_from('<III',data,4)
    assert version==1 and reserved==0
    s=16+12*m
    idx=data[s:s+768];frac=struct.unpack_from('<768I',data,s+768)
    nodes=data[s+3840:];assert len(nodes)==m**3*3
    histogram=Counter({0:1})
    for channel,stride in enumerate((m*m,m,1)):
        channel_hist=Counter()
        for code in range(256):
            cell=idx[channel*256+code];f=frac[channel*256+code]
            prediction=(nodes[cell*stride*3+channel]*(65536-f)+nodes[(cell+1)*stride*3+channel]*f+32768)//65536
            target=reference[code*(65536,256,1)[channel]*3+channel]
            channel_hist[(prediction-target)**2]+=1
        result=Counter()
        for a,x in histogram.items():
            for b,y in channel_hist.items():result[a+b]+=x*y
        histogram=result
    assert sum(histogram.values())==256**3
    return histogram


def histogram_metrics(hist):
    n=sum(hist.values());ordered=sorted(hist.items())
    def quantile_rank(rank):
        total=0
        for squared,count in ordered:
            total+=count
            if total>rank:return math.sqrt(squared)
        raise AssertionError('直方图分位秩越界')
    rank=Fraction(99,100)*(n-1);lo=rank.numerator//rank.denominator
    p99=quantile_rank(lo)+float(rank-lo)*(quantile_rank(lo+1)-quantile_rank(lo))
    # 沿用项目既定口径：取ceil(N*1%)个最坏像素，而非分数尾质量。
    tail_count=max(1,(n+99)//100)
    left=tail_count;tail_sum=0.
    for squared,count in reversed(ordered):
        take=min(left,count);tail_sum+=take*math.sqrt(squared);left-=take
        if not left:break
    return {'n':n,'mean':sum(math.sqrt(v)*c for v,c in ordered)/n,
        'rms':math.sqrt(sum(v*c for v,c in ordered)/n),'p99':p99,'max':math.sqrt(ordered[-1][0]),
        'cvar_1pct':tail_sum/tail_count}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('不覆盖已有分析')
    r=json.loads((args.run/'full-results.json').read_text(encoding='utf-8'))
    prep=json.loads((args.run/'preparation.json').read_text(encoding='utf-8'))
    run=json.loads((args.run/'run.json').read_text(encoding='utf-8'))
    root=Path(__file__).resolve().parents[1]
    reference_path=root/run['identity']['plan']['inputs']['reference']['path']
    assert sha(reference_path)==run['identity']['plan']['inputs']['reference']['sha256']
    reference=npy_rgb8(reference_path)
    metrics={}
    for name in ['baseline17','baseline33','calibrated17']:
        metrics[name]=histogram_metrics(curve_histogram(args.run/(name+'.slut'),reference))
        for key in ['mean','rms','p99','max']:
            assert abs(metrics[name][key]-prep['analytic_cube'][name][key])<1e-12
        rows=r['photos'][name]['per_image']
        assert len(rows)==100 and len({x['image'] for x in rows})==100
        for key,value in [('mean',sum(x['mean'] for x in rows)/100),('rms',math.sqrt(sum(x['rms']**2 for x in rows)/100)),
            ('worst_image_p99',max(x['p99'] for x in rows)),('max',max(x['max'] for x in rows)),
            ('mean_image_cvar_1pct',sum(x['cvar_1pct'] for x in rows)/100)]:
            assert abs(r['photos'][name][key]-value)<1e-12
    assert all(metrics['calibrated17'][key]==0 for key in ['mean','rms','p99','max','cvar_1pct'])
    assert len(r['native_cube'])==5 and len({x['kernel'] for x in r['native_cube']})==5
    assert all(x['sha256']==r['cube']['prediction_sha256'] and x['byte_mismatches']==0 for x in r['native_cube'])
    assert sha(args.run/'calibrated17.slut')==r['candidate_sha256']==prep['candidate_sha256']
    old=(args.run/'baseline17.slut').read_bytes();new=(args.run/'calibrated17.slut').read_bytes()
    m=struct.unpack_from('<I',old,8)[0];s=16+12*m+768;e=s+3072
    assert old[:s]==new[:s] and old[e:]==new[e:]
    a=struct.unpack_from('<768I',old,s);b=struct.unpack_from('<768I',new,s)
    changed=[i for i in range(768) if a[i]!=b[i]]
    assert len(changed)==7 and max(abs(a[i]-b[i]) for i in changed)==547
    result={'pass':True,'purpose':'标准库独立聚合已有300逐图与256码值曲线，新增解析CVaR；不新增全域/照片前向或性能测试',
        'environment':{'python':platform.python_version(),'platform':platform.platform(),'numeric_backend':None},
        'cube_analytic_independent':metrics,'fraction_entries_changed':changed,'maximum_fraction_shift':547,
        'full_results_sha256':sha(args.run/'full-results.json'),'script_sha256':sha(Path(__file__)),
        'models_sha256':{n:sha(args.run/(n+'.slut')) for n in metrics},'photo_rows_checked':300,
        'limits':'曲线卷积依赖前阶段全部原表已证明同轴可分离；不是对任意非可分离输入的检验'}
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
