"""消费已证273节点固定外域，独立记录新子空间的乐观p99下界。"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'python'),str(ROOT/'scripts')]
import numpy as np
from lutlab import channel_hotspot_support as hs
from check_cinema_current_outside_rank import ranks,compare_target
from run_channel_tail_nodes import digest
OUT=ROOT/'artifacts/cinema-current-expanded-outside-rank-v1'


def save(path,value):
    if path.exists():raise FileExistsError('不覆盖扩展外域秩证据')
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    if OUT.exists():raise FileExistsError('不覆盖扩展外域秩阶段')
    folder=ROOT/'artifacts/cinema-current-all-max-unit-v1'
    inputs=[folder/'aabb.npz',folder/'summary.json',ROOT/'artifacts/cinema-current-all-max-unit-independent-v1.json']
    sources=[Path(__file__),ROOT/'scripts/check_cinema_current_outside_rank.py',ROOT/'python/lutlab/channel_hotspot_support.py']
    save(OUT/'frozen.json',{'sources_sha256':{str(p):digest(p) for p in sources},'inputs_sha256':{str(p):digest(p) for p in inputs},
         'rgb_queries':0,'solver_calls':0,'scope':'只消费认证外域；可变171271及训练3541732理想归零，linear整数秩及根界沿旧已验实现。'})
    summary=json.loads((folder/'summary.json').read_text(encoding='utf-8'));audit=json.loads(inputs[-1].read_text(encoding='utf-8'))
    assert audit['pass'] and audit['summary_sha256']==digest(folder/'summary.json') and summary['complete_support_rows']==171271 and summary['affected_training_mass']==3541732
    groups={}
    with np.load(folder/'aabb.npz') as data:
        for name,key,n,mass,target in [('cube','outside_hist',16777216,171271,8),('training60','outside_training_hist',47185920,3541732,11)]:
            outside=data[key].copy();assert int(outside.sum())+mass==n and np.all(outside>=0) and int(np.flatnonzero(outside)[-1])==38
            optimistic=outside.copy();optimistic[0]+=mass;row=ranks([int(v) for v in optimistic]);assert abs(row['value']-hs.metrics(optimistic)['p99'])<=1e-12
            groups[name]={'n':n,'support_mass':mass,'outside_mass':int(outside.sum()),'outside_hist_sha256':hashlib.sha256(outside.tobytes()).hexdigest(),
                'outside_nonzero_bins':[[int(q),int(outside[q])] for q in np.flatnonzero(outside)],'outside_count_above_target':int(outside[target+1:].sum()),
                'optimistic_p99_lower_bound':row,'comparison':compare_target(row,target),'outside_max_squared':38}
    save(OUT/'results.json',{'pass':True,'frozen_sha256':digest(OUT/'frozen.json'),'groups':groups,'rgb_queries':0,'solver_calls':0,
         'scope':'固定273节点/固定轴后缀子空间的乐观下界；未阻断不证明共享可行，也不授mean或速度。'})
    print({'pass':True,'groups':{k:{'lower_bound':v['optimistic_p99_lower_bound'],'comparison':v['comparison'],'outside_above':v['outside_count_above_target']} for k,v in groups.items()}},flush=True)


if __name__=='__main__':main()
