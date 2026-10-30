"""有限全集核对训练mean/p99桥的保守成本、上端秩和分类。"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'python'))
from lutlab import training_budget_bridge as bridge


def binary_root(value):
    lo,hi=0,1
    while hi*hi<=value:hi*=2
    while lo+1<hi:
        mid=(lo+hi)//2
        if mid*mid<=value:lo=mid
        else:hi=mid
    return lo


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖两训练预算桥有限合同')
    roots=0
    for q in [*range(67),195075]:
        lo,hi=bridge.root_bounds(q);value=q*bridge.SCALE**2;expected=binary_root(value)
        assert lo==expected and hi==expected+int(expected*expected!=value);roots+=1
    classes=[(0,0,0,True,(True,False,False)),(4,4,3,False,(False,False,False)),
        (2,9,2,False,(True,True,False)),(13,18,5,False,(True,True,False)),
        (9,17,4,False,(True,True,True)),(0,17,0,True,(True,False,False))]
    for a,b,w,d,expected in classes:assert bridge.classify(a,b,w,d)==expected
    # 真实根和的充分性用平方根区间完全独立核对，不以float判号。
    choices=((0,1,2),(9,12,13),(0,17));weights=(0,2,1);outside={4:100};n=sum(outside.values())+sum(weights)
    baseline={4:103};base_hist=[0]*18
    for q,w in baseline.items():base_hist[q]=w
    base_floor=bridge.root_sum(base_hist)[0];cases=accepted=0
    for values in itertools.product(*choices):
        hist=[0]*18
        for q,w in outside.items():hist[q]+=w
        for q,w in zip(values,weights):hist[q]+=w
        lhs=bridge.root_sum(hist)[1];above=sum(hist[13:]);passes=lhs<=base_floor and above<=bridge.above_limit(n)
        if passes:
            # 独立binary整数根给同样充分界，同时直接核p99上端秩。
            actual_hi=sum(w*(binary_root(q*bridge.SCALE**2)+int(binary_root(q*bridge.SCALE**2)**2!=q*bridge.SCALE**2)) for q,w in enumerate(hist))
            assert actual_hi<=base_floor
            ordered=sorted(q for q,w in enumerate(hist) for _ in range(w));rank=(99*(n-1)+99)//100
            assert ordered[rank]<=12;accepted+=1
        cases+=1
    assert cases==18 and accepted>0 and bridge.above_limit(47185920)==471859
    # 纯平方根等式以及单像素/小样本上端秩的边界不能被浮点近似放过。
    for n in range(1,202):
        limit=bridge.above_limit(n);upper=(99*(n-1)+99)//100
        for above in range(n+1):assert (above<=limit)==(n-above>upper)
    names=['python/lutlab/training_budget_bridge.py','scripts/check_cinema_max48_training_bridge.py',
        'scripts/census_cinema_max48_training_bridge.py','scripts/audit_cinema_max48_training_bridge.py',
        'experiments/p16-cinema-max48-training-bridge-census-v1.json','experiments/p16-cinema-max48-training-bridge-proposal-v1.md']
    record={'pass':True,'independent_root_cases':roots,'classification_cases':len(classes),'complete_q_assignments':cases,
        'accepted_assignments':accepted,'p99_sample_sizes':201,'source_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names},
        'scope':'只核两预算桥数学与有限分类，无真实CP/新RGB查询/拟合/性能。'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({k:record[k] for k in ('pass','complete_q_assignments','accepted_assignments')},flush=True)


if __name__=='__main__':main()
