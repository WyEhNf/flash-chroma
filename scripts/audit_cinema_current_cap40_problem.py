"""原环境独立八角帽权/clip/gcd核全部真实cap40整数行及安全CSR。"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'python'),str(ROOT/'scripts')]
import numpy as np
from lutlab import channel_hotspot_support as hs
from run_channel_tail_nodes import load_model
from cinema_current_cap40_identity import sha,verify
OUT=ROOT/'artifacts/cinema-current-cap40-cpsat-v1';SAFE=(1<<62)-1


def main():
    p=argparse.ArgumentParser(description=__doc__);p.parse_args()
    if (OUT/'problem-independent.json').exists():raise FileExistsError('不覆盖cap40真实整数独立审计')
    path=OUT/'problem.json';problem=json.loads(path.read_text(encoding='utf-8'));verify(problem)
    with np.load(problem['unit_screen']) as data:
        selected=data['selected_nodes'].copy();danger=data['dangerous_rows'].copy();keys=data['keys'][danger].copy();lower=data['lower_rgb'][danger].copy();upper=data['upper_rgb'][danger].copy();original=data['original_first'][danger].copy()
    with np.load(problem['unit_allowed']) as data:csr_keys,offsets,allowed=data['source_keys'],data['offsets'],data['allowed_rgb']
    np.testing.assert_array_equal(keys,csr_keys);np.testing.assert_array_equal(keys,[p['source_key'] for p in problem['points']])
    model=load_model(problem['original_inputs']['first']['path']);nodes=model.nodes.reshape(-1,3).astype(np.int64);indices,weights=hs.corners(model,hs.rgb(keys))
    acc=np.sum(weights.astype(np.int64)*nodes[indices],axis=1,dtype=np.int64);np.testing.assert_array_equal((acc+32768)//65536,original)
    mapping={int(node):i for i,node in enumerate(selected)};max_bound=0
    for i,node in enumerate(selected):
        for c in range(3):
            v=problem['variables'][3*i+c];old=int(nodes[node,c]);assert (v['physical_node'],v['channel'],v['original_value'],v['lower'],v['upper'])==(int(node),c,old,max(-1,-old),min(1,255-old))
    for i,point in enumerate(problem['points']):
        np.testing.assert_array_equal(point['original_acc'],acc[i]);np.testing.assert_array_equal(point['original_rgb'],original[i])
        expected=allowed[int(offsets[i]):int(offsets[i+1])].astype(np.int64)-original[i];np.testing.assert_array_equal(point['allowed_deltas'],expected)
        for c in range(3):
            terms={}
            for corner in range(8):
                node=int(indices[i,corner]);w=int(weights[i,corner,c])
                if node in mapping and w:terms[3*mapping[node]+c]=terms.get(3*mapping[node]+c,0)+w
            assert sorted(point['node_terms'][c])==sorted([[j,w] for j,w in terms.items()])
            z=point['z_indices'][c];domain=problem['variables'][z]
            assert (domain['lower'],domain['upper'])==(int(lower[i,c])-int(original[i,c]),int(upper[i,c])-int(original[i,c]))
            terms[z]=-65536;raw=sorted([[j,w] for j,w in terms.items()]);row=problem['rows'][3*i+c]
            lo=int(original[i,c])*65536-32768-int(acc[i,c]);hi=lo+65535
            assert (row['raw_terms'],row['raw_lower'],row['raw_upper'])==(raw,lo,hi)
            gcd=math.gcd(*(abs(w) for _,w in raw));assert row['gcd']==gcd and row['terms']==[[j,w//gcd] for j,w in raw]
            assert (row['lower'],row['upper'])==(-((-lo)//gcd),hi//gcd)
            bound=sum(abs(w)*max(abs(problem['variables'][j]['lower']),abs(problem['variables'][j]['upper'])) for j,w in raw)
            assert bound<=SAFE and row['int64_audit']['raw_absolute_sum_bound']==bound;max_bound=max(max_bound,bound)
    inputs=problem['original_inputs'];suffix=np.load(inputs['suffix']['path'],mmap_mode='r');gold=np.load(inputs['gold']['path'],mmap_mode='r');repeated=np.repeat(keys,np.diff(offsets))
    error=suffix[hs.key(allowed)].astype(np.int32)-gold[repeated].astype(np.int32);q=np.sum(error*error,axis=1,dtype=np.int32)
    assert len(q)==74081 and np.all(q<=40)
    result={'pass':True,'problem_sha256':sha(path),'checked_points':4058,'checked_q16_rows':12174,'checked_allowed_rgb':74081,
        'maximum_raw_absolute_bound':max_bound,'scope':'独立八角/fullacc/clip/gcd.int64/全部安全CSR，未建模或搜索。'}
    (OUT/'problem-independent.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(result,flush=True)


if __name__=='__main__':main()
