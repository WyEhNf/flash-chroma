"""消费已验完整直方图，独立核固定外域的乐观p99秩下界；不映射RGB。"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'python'))
OUT=ROOT/'artifacts/cinema-current-outside-rank-v1'
SCALE=1<<32


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def save(path,value):
    if path.exists():raise FileExistsError('不覆盖已执行外域秩证据')
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def ranks(hist):
    n=sum(hist);lo,rem=divmod(99*(n-1),100);hi=lo+int(bool(rem))
    def kth(rank):
        seen=0
        for q,count in enumerate(hist):
            seen+=count
            if seen>rank:return q
        raise AssertionError('整数秩超直方图')
    a,b=kth(lo),kth(hi)
    return {'lower_rank_zero_based':lo,'upper_rank_zero_based':hi,'lower_squared':a,'upper_squared':b,'remainder_percent':rem,
            'value':math.sqrt(a)+rem/100*(math.sqrt(b)-math.sqrt(a))}


def integer_interval(terms):
    lo=hi=0
    for q,n in terms.items():
        value=q*SCALE*SCALE;floor=math.isqrt(value)
        lo+=n*floor;hi+=n*(floor+int(floor*floor!=value))
    return lo,hi


def signature(terms):
    result={}
    for q,n in terms.items():
        if not q or not n:continue
        f=next(v for v in range(math.isqrt(q),0,-1) if q%(v*v)==0)
        result[q//(f*f)]=result.get(q//(f*f),0)+f*n
    return result


def compare_target(row,target):
    terms={}
    for q,n in ((row['lower_squared'],100-row['remainder_percent']),(row['upper_squared'],row['remainder_percent'])):
        terms[q]=terms.get(q,0)+n
    a,b=integer_interval(terms);c,d=integer_interval({target:100})
    equal=signature(terms)==signature({target:100})
    status='equal' if equal else 'blocked' if a>d else 'not_blocked_by_this_bound' if b<c else 'integer_interval_unresolved'
    return {'target_squared':target,'strict_status':status,'optimistic_p99_numerator_lower':a,'optimistic_p99_numerator_upper':b,
            'target_numerator_lower':c,'target_numerator_upper':d,'scale':SCALE,'exact_radical_equality':equal,
            'interpretation':'blocked仅指固定122节点子空间的目标被外域阻断；其余状态不是共享可行性证明'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--freeze',action='store_true');args=p.parse_args()
    sources=[Path(__file__),ROOT/'experiments/p16-cinema-current-outside-rank-v1.json',ROOT/'experiments/p16-cinema-current-hint-proposal-v1.md',
             ROOT/'python/lutlab/channel_hotspot_support.py']
    folder=ROOT/'artifacts/cinema-current-full-quality-v2';accepted=ROOT/'artifacts/cinema-current-feasible-cpsat-accept-v1'
    inputs=[folder/'histograms.npz',folder/'results.json',accepted/'replay.npz',accepted/'summary.json',
            ROOT/'artifacts/cinema-max48-risk-upper-v1/screen.npz',ROOT/'artifacts/cinema-current-full-quality-independent-v2.json']
    frozen=OUT/'frozen.json'
    if args.freeze:
        if OUT.exists():raise FileExistsError('不覆盖外域秩阶段')
        for path in sources:
            if path.suffix=='.py':ast.parse(path.read_text(encoding='utf-8-sig'))
        save(frozen,{'ast_pass':True,'sources_sha256':{str(v):sha(v) for v in sources},'inputs_sha256':{str(v):sha(v) for v in inputs},
                     'schema':'cinema_current_outside_rank_v1','rgb_queries':0,'solver_calls':0,'performance_calls':0})
        print({'freeze_sha256':sha(frozen),'sources':len(sources),'inputs':len(inputs)},flush=True);return
    proof=json.loads(frozen.read_text(encoding='utf-8'))
    for name,expected in {**proof['sources_sha256'],**proof['inputs_sha256']}.items():assert sha(name)==expected,name
    import numpy as np
    from lutlab import channel_hotspot_support as hs
    finite=0
    for n in (1,2,3,99,100,101):
        for zero in range(n+1):
            for q in (1,2,9,12):
                hist=[0]*(q+1);hist[0]=zero;hist[q]=n-zero
                observed=ranks(hist);assert abs(observed['value']-hs.metrics(hist)['p99'])<=1e-12
                expanded=np.array([0.]*zero+[math.sqrt(q)]*(n-zero))
                assert abs(observed['value']-float(np.percentile(expanded,99)))<=1e-12
                finite+=1
    prior=json.loads((ROOT/'artifacts/cinema-current-full-quality-independent-v2.json').read_text(encoding='utf-8'))
    assert prior['pass'] and prior['histograms_sha256']==sha(folder/'histograms.npz')
    current=json.loads((folder/'results.json').read_text(encoding='utf-8'))
    assert current['mismatches']==0 and current['candidate_oracle_sha256']=='728666cbc05f0cd2d9da112ce41a26117d67baee1511760d83df8f8cefe8ed98'
    with np.load(accepted/'replay.npz') as data:
        keys=data['keys'].copy();square=data['squared'].copy();weights=data['training_counts'].copy()
        replay={'cube':data['after_hist'].copy(),'training60':data['after_training_hist'].copy()}
    with np.load(ROOT/'artifacts/cinema-max48-risk-upper-v1/screen.npz') as data:
        np.testing.assert_array_equal(keys,data['keys']);np.testing.assert_array_equal(weights,data['training_counts'])
        selected=data['selected_nodes'].copy();saved={'cube':data['outside_hist'].copy(),'training60':data['outside_training_hist'].copy()}
    assert len(keys)==80751 and len(selected)==122 and int(weights.sum())==901853
    assert keys.dtype.kind=='u' and weights.dtype.kind in 'iu' and np.all(weights>=0) and np.all(square>=0)
    groups={}
    with np.load(folder/'histograms.npz') as data:
        for name,target,n,mass,count in [('cube',8,16777216,80751,None),('training60',11,47185920,901853,weights)]:
            full=[int(v) for v in data[name+'_candidate']];total_size=max(len(full),len(saved[name]),len(replay[name]))
            full+= [0]*(total_size-len(full));baseline=[int(v) for v in replay[name]]+[0]*(total_size-len(replay[name]))
            assert full==baseline and sum(full)==n
            support=[0]*total_size
            for i,q in enumerate(square):support[int(q)]+=1 if count is None else int(count[i])
            assert sum(support)==mass
            outside=[a-b for a,b in zip(full,support)];expected=[int(v) for v in saved[name]]+[0]*(total_size-len(saved[name]))
            assert outside==expected and min(outside)>=0 and sum(outside)==n-mass
            assert max(q for q,v in enumerate(outside) if v)==41
            optimistic=outside.copy();optimistic[0]+=mass
            row=ranks(optimistic);assert abs(row['value']-hs.metrics(optimistic)['p99'])<=1e-12
            groups[name]={'n':n,'support_mass':mass,'outside_mass':sum(outside),'outside_hist':outside,'support_hist':support,
                          'optimistic_hist':optimistic,'current_p99':ranks(full),'optimistic_p99_lower_bound':row,'comparison':compare_target(row,target),
                          'outside_max_squared':41,'outside_count_above_target':sum(outside[target+1:]),'outside_count_q41':outside[41]}
    for name,expected in {**proof['sources_sha256'],**proof['inputs_sha256']}.items():assert sha(name)==expected,name
    result={'pass':True,'frozen_sha256':sha(frozen),'finite_rank_cases':finite,'groups':groups,'rgb_queries':0,'solver_calls':0,'performance_calls':0,
            'scope':'完整hist减已验正支撑hist，原整数训练权重守恒；支撑理想归零给固定外域条件乐观秩下界，不构造共享解或晋级模型。'}
    save(OUT/'results.json',result)
    print({'pass':True,'finite_cases':finite,'groups':{k:{'p99_lower':v['optimistic_p99_lower_bound'],'target':v['comparison'],
            'outside_count_above_target':v['outside_count_above_target'],'outside_q41':v['outside_count_q41']} for k,v in groups.items()}},flush=True)


if __name__=='__main__':main()
