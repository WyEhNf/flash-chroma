"""有限笛卡尔穷举核cap47风险核和全部选择的直方图充分上界。"""
from __future__ import annotations
import argparse
import itertools
import json
import math
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/'python'))
import numpy as np
from lutlab import channel_capped_risk as risk, channel_hotspot_support as hs
from run_channel_tail_nodes import digest, save


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖cap47风险和公共上界有限合同')
    lower = np.array([[0,0,0], [3,3,3], [0,0,0], [255,255,255], [7,8,9]], np.uint8)
    upper = np.array([[4,4,4], [7,7,7], [4,4,4], [255,255,255], [7,8,9]], np.uint8)
    gold = np.array([[6,6,6], [5,5,5], [255,255,255], [255,255,255], [0,0,0]], np.uint8)
    observed = risk.enumerate_stats(lower, upper, gold, lambda rgb: rgb, 47)
    offsets, allowed = risk.collect_allowed(lower, upper, gold, lambda rgb: rgb, 47)
    for j, (lo, hi, target) in enumerate(zip(lower, upper, gold)):
        rgb = list(itertools.product(*[range(int(a), int(b)+1) for a,b in zip(lo,hi)]))
        q = [sum((v-int(t))**2 for v,t in zip(row,target)) for row in rgb]
        safe = [row for row,value in zip(rgb,q) if value<=47]
        expected = [min(q),max(q),len(q),len(safe),max([v for v in q if v<=47],default=-1)]
        assert [int(a[j]) for a in observed] == expected
        assert allowed[offsets[j]:offsets[j+1]].tolist() == [list(row) for row in safe]
    choices = ((0,1,4),(2,3),(0,6)); weights = (0,2,1); cases = 0
    for weighted in (False,True):
        worst = np.zeros(67,np.int64); worst[0]=2
        for values,mass in zip(choices,weights):worst[max(values)] += mass if weighted else 1
        for assignment in itertools.product(*choices):
            hist=np.zeros(67,np.int64);hist[0]=2
            for value,mass in zip(assignment,weights):hist[value] += mass if weighted else 1
            proof=risk.compare_histograms(hist,worst)
            assert proof['all_five_automatically_protected'];cases+=1
    for q in [*range(67),195075]:
        hist=np.zeros(q+1,np.int64);hist[q]=1;lo,hi=risk.root_interval(hist);value=q*risk.SCALE*risk.SCALE
        assert lo*lo<=value<=hi*hi and hi-lo<=1
    a=np.zeros(9,np.int64);b=a.copy();a[8]=1;a[0]=1;b[2]=2
    assert risk.root_comparison(a,b)['exact_equal_radical_sum']
    names=['python/lutlab/channel_capped_risk.py','scripts/check_cinema_max48_risk_upper.py',
        'scripts/screen_cinema_max48_risk_upper.py','scripts/audit_cinema_max48_risk_upper.py',
        'experiments/p16-cinema-max48-risk-upper-v1.json']
    save(args.output,{'pass':True,'risk_points':len(lower),'complete_bound_assignments':cases,'integer_root_cases':68,
        'source_sha256':{name:digest(ROOT/name) for name in names},'scope':'有限全状态/全部选择核对，不是完整当前模型可行性或性能。'})
    print({'pass':True,'risk_points':len(lower),'bound_assignments':cases},flush=True)


if __name__=='__main__':main()
