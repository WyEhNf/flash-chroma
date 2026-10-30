"""独立八角帽权与完整CSR核当前真实整数问题，不构造CP或搜索。"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'python'))
from lutlab import channel_hotspot_support as hs
from run_channel_tail_nodes import load_model
from cinema_current_safe_identity import sha,verify_frozen
SAFE=(1<<62)-1


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--problem',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖当前真实问题独立审计')
    problem=json.loads(args.problem.read_text(encoding='utf-8'));verify_frozen(problem);inputs=problem['source_inputs'];model=load_model(problem['inputs']['first']['path'])
    with np.load(inputs['screen']['path']) as data:
        selected=data['selected_nodes'];danger=data['dangerous_rows'];keys=data['keys'][danger]
        low=data['lower_rgb'][danger];high=data['upper_rgb'][danger];old_first=data['original_first'][danger]
    with np.load(inputs['allowed']['path']) as data:csr_keys,offsets,allowed=data['source_keys'],data['offsets'],data['allowed_rgb']
    np.testing.assert_array_equal(keys,csr_keys);np.testing.assert_array_equal(keys,[p['source_key'] for p in problem['points']])
    flat=model.nodes.reshape(-1,3).astype(np.int64);indices,weights=hs.corners(model,hs.rgb(keys));acc=np.sum(weights.astype(np.int64)*flat[indices],axis=1,dtype=np.int64)
    np.testing.assert_array_equal((acc+32768)//65536,old_first)
    mapping={int(node):i for i,node in enumerate(selected)}
    for i,node in enumerate(selected):
        for c in range(3):
            domain=problem['variables'][3*i+c];old=int(flat[node,c])
            assert (domain['physical_node'],domain['channel'],domain['original_value'],domain['lower'],domain['upper'])==(int(node),c,old,max(-2,-old),min(2,255-old))
    maximum_raw=0
    for i,point in enumerate(problem['points']):
        np.testing.assert_array_equal(point['original_acc'],acc[i]);np.testing.assert_array_equal(point['original_rgb'],old_first[i])
        expected=allowed[int(offsets[i]):int(offsets[i+1])].astype(np.int64)-old_first[i]
        np.testing.assert_array_equal(point['allowed_deltas'],expected)
        for c in range(3):
            terms={}
            for corner in range(8):
                node=int(indices[i,corner]);w=int(weights[i,corner,c])
                if node in mapping and w:terms[3*mapping[node]+c]=terms.get(3*mapping[node]+c,0)+w
            assert sorted(point['node_terms'][c])==sorted([[j,w] for j,w in terms.items()])
            z=point['z_indices'][c];domain=problem['variables'][z]
            assert (domain['lower'],domain['upper'])==(int(low[i,c])-int(old_first[i,c]),int(high[i,c])-int(old_first[i,c]))
            terms[z]=-65536;raw=sorted([[j,w] for j,w in terms.items()]);row=problem['rows'][3*i+c]
            lower=int(old_first[i,c])*65536-32768-int(acc[i,c]);upper=lower+65535
            assert (row['raw_terms'],row['raw_lower'],row['raw_upper'])==(raw,lower,upper)
            divisor=math.gcd(*(abs(w) for _,w in raw));lo=-((-lower)//divisor);hi=upper//divisor
            assert row['gcd']==divisor and row['terms']==[[j,w//divisor] for j,w in raw] and (row['lower'],row['upper'])==(lo,hi)
            bound=sum(abs(w)*max(abs(problem['variables'][j]['lower']),abs(problem['variables'][j]['upper'])) for j,w in raw)
            assert bound<=SAFE and row['int64_audit']['raw_absolute_sum_bound']==bound;maximum_raw=max(maximum_raw,bound)
    suffix=np.load(problem['inputs']['suffix']['path'],mmap_mode='r');gold=np.load(problem['inputs']['gold']['path'],mmap_mode='r')
    repeated=np.repeat(keys,np.diff(offsets));error=suffix[hs.key(allowed)].astype(np.int32)-gold[repeated].astype(np.int32)
    square=np.sum(error*error,axis=1,dtype=np.int32)
    assert len(square)==386612 and np.all(square<=47)
    result={'pass':True,'problem_sha256':sha(args.problem),'checked_points':len(keys),'checked_q16_rows':len(problem['rows']),
        'checked_allowed_rgb':len(square),'maximum_raw_absolute_bound':maximum_raw,
        'scope':'独立八角帽权/fullacc/节点clip/完整CSR/原始与gcd舍入行以及全部安全输出误差；未建CP或搜索。'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({k:result[k] for k in ('pass','checked_points','checked_q16_rows','checked_allowed_rgb')},flush=True)


if __name__=='__main__':main()
