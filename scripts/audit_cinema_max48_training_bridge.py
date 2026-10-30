"""独立逐点分类与binary整数根重放两预算桥普查，不生成CP。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def root_floor(value):
    lo,hi=0,1
    while hi*hi<=value:hi*=2
    while lo+1<hi:
        mid=(lo+hi)//2
        if mid*mid<=value:lo=mid
        else:hi=mid
    return lo


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖两预算桥独立重放')
    run=read(args.stage/'run.json');summary=read(args.stage/'summary.json');scale=1<<20
    with np.load(run['inputs']['screen']['path']) as data:
        keys=data['keys'];mn=data['minimum_squared'];mx=data['safe_maximum_squared'];max_all=data['maximum_squared'];weights=data['training_counts'];rows=data['safe_count']
        outside=data['outside_training_hist'];baseline=data['baseline_best_training'];fixed=outside.copy()
        union=[];danger=[];cost=[];flag=[];vmin=vmax=0;above=int(sum(outside[13:]));zero=0
        for i in range(len(keys)):
            a,b,w=int(mn[i]),int(mx[i]),int(weights[i]);d=int(max_all[i])>47;c=w>0 and a!=b;f=w>0 and a<=12<b
            if d:danger.append(i);zero+=int(w==0)
            if d or c:union.append(i)
            if c:
                cost.append(i)
                for q,name in ((a,'min'),(b,'max')):
                    value=q*scale*scale;floor=root_floor(value);ceil=floor+int(floor*floor<value)
                    if name=='min':vmin+=w*ceil
                    else:vmax+=w*ceil
            else:fixed[a]+=w
            if f:flag.append(i)
            elif a>12:above+=w
        def bounds(hist):
            lo=hi=0
            for q,w in enumerate(hist):
                if not w:continue
                value=q*scale*scale;v=root_floor(value);lo+=int(w)*v;hi+=int(w)*(v+int(v*v<value))
            return lo,hi
        blo,bhi=bounds(baseline);flo,fhi=bounds(fixed)
        with np.load(args.stage/'classification.npz') as saved:
            for field,expected in [('keys',keys),('union_rows',union),('danger_rows',danger),('cost_rows',cost),('flag_rows',flag),('fixed_training_hist',fixed)]:
                np.testing.assert_array_equal(saved[field],expected)
        expected={'union_points':len(union),'danger_points':len(danger),'danger_zero_training_points':zero,'cost_points':len(cost),
            'flag_points':len(flag),'safe_rows_in_union':sum(int(rows[i]) for i in union),'extra_cost_flag_variables':len(cost)+len(flag),
            'baseline_best_root_floor':blo,'baseline_best_root_ceil':bhi,'fixed_root_floor':flo,'fixed_root_ceil':fhi,
            'variable_root_minimum':vmin,'variable_root_maximum':vmax,'variable_mean_rhs':blo-fhi,'fixed_above12_mass':above,
            'variable_flag_mass_maximum':sum(int(weights[i]) for i in flag),'variable_flag_rhs':471859-above,
            'support_training_pixels':sum(int(w) for w in weights),'full_training_pixels':sum(int(w) for w in weights)+sum(int(w) for w in outside),
            'explicit_node_output_cost_flag_variables':366+3*len(union)+len(cost)+len(flag),
            'explicit_table_cells':3*sum(int(rows[i]) for i in union)+sum(int(rows[i]) for i in cost)+sum(int(rows[i]) for i in flag)}
    for key,value in expected.items():assert summary[key]==value,(key,summary[key],value)
    gates=summary['fixed_resource_gates'];gate=len(union)<=gates['union_points_max'] and expected['safe_rows_in_union']<=gates['safe_rows_max'] and len(cost)+len(flag)<=gates['extra_cost_flag_vars_max']
    assert gate==summary['within_resource_gates'] and not summary['cp_model_built'] and not summary['cp_solver_called'] and summary['new_rgb_queries']==0
    result={'pass':True,'checked_support_points':len(keys),'checked_integer_fields':len(expected),'summary_sha256':sha(args.stage/'summary.json'),
        'classification_sha256':sha(args.stage/'classification.npz'),'scope':'独立逐点集合/固定项与binary整数根复核；未建CP或RGB查询。'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'pass':True,'points':len(keys),'integer_fields':len(expected)},flush=True)


if __name__=='__main__':main()
