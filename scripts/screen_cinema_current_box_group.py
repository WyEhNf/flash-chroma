"""独立入口：同盒cap40一次查询/完整原point散回；不构造CP或候选。"""
from __future__ import annotations
import argparse
import ast
import itertools
import json
from pathlib import Path
import sys
import numpy as np
import psutil
from count_cinema_current_box_group import OUT as GEOMETRY, load_frozen as geometry_frozen, read, sha

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'artifacts/cinema-current-box-group-screen-v1'
PLAN = ROOT/'experiments/p16-cinema-current-box-group-screen-v1.json'


def save(path, value):
    if path.exists():
        raise FileExistsError('不覆盖同盒cap40筛查原件：'+str(path))
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def freeze():
    if OUT.exists():
        raise FileExistsError('不覆盖同盒cap40阶段')
    geometry = geometry_frozen()
    assert sha(GEOMETRY/'frozen.json') == '6753527ad70f63659cd93ac29517e68525a39b2375170c4e7ebce3cb1fea8c8a'
    expected = {'groups.npz':'e0d2ad708d65adac99c7c571b8889c74b85382d4bae3fc410b21745fc4e2bf70',
        'summary.json':'76b48dbfd6e6a081148c1048986ffcd0156b033603342a9720d05b7b404c7ec0',
        'independent.json':'f3b0dbf4e30fa7dc45baa8b97ed89f435c6faf3576c763d8607b5331c2ccb141'}
    for name,digest in expected.items():
        assert sha(GEOMETRY/name)==digest,name
    summary,independent=read(GEOMETRY/'summary.json'),read(GEOMETRY/'independent.json')
    assert independent['pass'] and independent['summary_sha256']==sha(GEOMETRY/'summary.json')
    assert summary['within_gate'] and summary['grouped_query_states']==independent['grouped_query_states']==1267197
    assert summary['logical_point_states']==5284765 and summary['true_suffix_state_queries']==0
    sources=dict(geometry['source_sha256'])
    for name in ('scripts/screen_cinema_current_box_group.py','scripts/audit_cinema_current_box_group_screen.py',
                 'experiments/p16-cinema-current-box-group-screen-v1.json'):
        sources[name]=sha(ROOT/name)
    for name,digest in sources.items():
        assert sha(ROOT/name)==digest,name
        if name.endswith('.py'):
            ast.parse((ROOT/name).read_text(encoding='utf-8-sig'))
    inputs=dict(geometry['inputs'])
    for name in ('frozen.json','contract.json','groups.npz','summary.json','independent.json'):
        path=GEOMETRY/name
        inputs['geometry_'+name]={'path':str(path),'sha256':sha(path)}
    assert inputs['suffix']['sha256']=='0ced3cb5f1acad4ff15d392dfc52bf44af8e99807afc9b62ee7cb5625392a3d1'
    for name,spec in inputs.items():
        assert sha(spec['path'])==spec['sha256'],name
    save(OUT/'frozen.json',dict(ast_pass=True,source_sha256=sources,inputs=inputs,plan=read(PLAN),
        python=sys.version,numpy=np.__version__,psutil=psutil.__version__,byteorder=sys.byteorder,
        grouped_query_states_per_complete_path=1267197,old_logical_states=5284765,
        old_state_gate_preserved=True,solver_calls=0,performance_samples=0))
    print({'screen_frozen_sha256':sha(OUT/'frozen.json'),'sources':len(sources),'inputs':len(inputs)},flush=True)


def load_frozen():
    frozen=read(OUT/'frozen.json')
    for name,digest in frozen['source_sha256'].items():
        assert sha(ROOT/name)==digest,name
    for name,spec in frozen['inputs'].items():
        assert sha(spec['path'])==spec['sha256'],name
    return frozen


def enumerate_groups(group_keys,lookup,cap):
    if group_keys.dtype!=np.uint8 or group_keys.ndim!=2 or group_keys.shape[1]!=9 or type(cap) is not int:
        raise ValueError('需要精确uint8九字节组键与整数cap')
    lower,upper,gold=group_keys[:,:3],group_keys[:,3:6],group_keys[:,6:]
    span=upper.astype(np.int16)-lower.astype(np.int16)
    if np.any(span<0) or np.any(span>4):
        raise ValueError('非法每轴1..5值闭盒')
    n=len(lower)
    minimum=np.full(n,195076,np.int32);maximum=np.full(n,-1,np.int32)
    count=np.zeros(n,np.uint8);safe_count=np.zeros(n,np.uint8);safe_max=np.full(n,-1,np.int32)
    good_rows=[];good_rgb=[];queries=0
    for offset in itertools.product(range(5),repeat=3):
        rows=np.flatnonzero(np.all(span>=offset,axis=1))
        if not len(rows):
            continue
        rgb=(lower[rows].astype(np.int16)+offset).astype(np.uint8)
        observed=lookup(rgb)
        assert observed.shape==rgb.shape and observed.dtype==np.uint8
        delta=observed.astype(np.int32)-gold[rows].astype(np.int32)
        q=np.sum(delta*delta,axis=1,dtype=np.int32)
        assert np.all((q>=0)&(q<=195075))
        minimum[rows]=np.minimum(minimum[rows],q);maximum[rows]=np.maximum(maximum[rows],q);count[rows]+=1
        good=q<=cap;safe_count[rows]+=good.astype(np.uint8)
        safe_max[rows[good]]=np.maximum(safe_max[rows[good]],q[good])
        good_rows.append(rows[good].astype(np.uint32));good_rgb.append(rgb[good]);queries+=len(rows)
    np.testing.assert_array_equal(count.astype(np.int64),np.prod(span+1,axis=1,dtype=np.int64))
    rows=np.concatenate(good_rows) if good_rows else np.empty(0,np.uint32)
    rgb=np.concatenate(good_rgb) if good_rgb else np.empty((0,3),np.uint8)
    code=(rgb[:,0].astype(np.uint32)<<16)|(rgb[:,1].astype(np.uint32)<<8)|rgb[:,2].astype(np.uint32)
    order=np.lexsort((code,rows));rows,rgb=rows[order],rgb[order]
    offsets=np.r_[0,np.cumsum(np.bincount(rows,minlength=n),dtype=np.int64)]
    np.testing.assert_array_equal(np.diff(offsets),safe_count)
    return dict(minimum_squared=minimum,maximum_squared=maximum,query_count=count,
        safe_count=safe_count,safe_maximum_squared=safe_max,offsets=offsets,allowed_rgb=rgb),queries


def contract():
    frozen=load_frozen()
    if (OUT/'contract.json').exists():
        raise FileExistsError('不覆盖独立screen有限合同')
    from cinema_box_group import group_boxes
    from count_cinema_current_box_group import simple_stats
    cases=[('duplicate',[[0,0,0],[0,0,0]],[[4,4,4]]*2,[[1,1,1]]*2),
        ('different_gold',[[0,0,0]]*2,[[4,4,4]]*2,[[0,0,0],[255,255,255]]),
        ('boundary_and_empty',[[251,251,251],[255,255,255],[0,0,0]],[[255,255,255],[255,255,255],[0,0,0]],
             [[255,255,255],[0,0,0],[0,0,0]]),
        ('mixed',[[3,4,5],[0,0,0],[3,4,5]],[[7,8,9],[4,4,4],[7,8,9]],[[5,5,5],[0,0,0],[5,5,5]])]
    records=[]
    for name,lo,hi,gold in cases:
        lower,upper,target=[np.asarray(v,np.uint8) for v in (lo,hi,gold)]
        groups=group_boxes(lower,upper,target)
        observed,queries=enumerate_groups(groups['group_keys'],lambda rgb:rgb.copy(),40)
        direct=simple_stats(lower,upper,target)
        assert queries==sum(int(v) for v in groups['group_state_count'])
        for i,(stats,safe) in enumerate(direct):
            g=int(groups['inverse'][i]);actual=[int(observed[k][g]) for k in
                ('minimum_squared','maximum_squared','query_count','safe_count','safe_maximum_squared')]
            assert actual==stats
            assert observed['allowed_rgb'][observed['offsets'][g]:observed['offsets'][g+1]].tolist()==safe
        records.append(dict(name=name,original_points=len(lo),groups=len(groups['group_keys']),
            identity_lookup_queries=queries,complete_scatter_and_csr_equal=True))
    save(OUT/'contract.json',{'pass':True,'frozen_sha256':sha(OUT/'frozen.json'),'cases':records,
        'real_suffix_state_queries':0,'identity_lookup_only':True,'solver_calls':0})
    print({'screen_contract_pass':True,'cases':len(records),'real_suffix_state_queries':0},flush=True)


def run():
    frozen=load_frozen();finite=read(OUT/'contract.json')
    assert finite['pass'] and finite['frozen_sha256']==sha(OUT/'frozen.json')
    save(OUT/'start.json',dict(frozen_sha256=sha(OUT/'frozen.json'),contract_sha256=sha(OUT/'contract.json'),solver_calls=0))
    with np.load(frozen['inputs']['geometry_groups.npz']['path']) as data:
        groups={n:data[n] for n in data.files}
    with np.load(frozen['inputs']['old_aabb']['path']) as data:
        original={n:data[n] for n in data.files}
    np.testing.assert_array_equal(groups['source_keys'],original['keys'])
    keys=groups['group_keys'];inverse=groups['inverse'];gates=frozen['plan']['资源门']
    planned=sum(int(v) for v in groups['group_state_count'])
    assert planned==1267197 and planned<=gates['maximum_group_query_states_per_complete_path']
    suffix=np.load(frozen['inputs']['suffix']['path'],mmap_mode='r')
    assert suffix.shape==(1<<24,3) and suffix.dtype==np.uint8
    def lookup(rgb):
        code=(rgb[:,0].astype(np.uint32)<<16)|(rgb[:,1].astype(np.uint32)<<8)|rgb[:,2].astype(np.uint32)
        return suffix[code]
    screen,queries=enumerate_groups(keys,lookup,40)
    assert queries==planned
    np.testing.assert_array_equal(screen['query_count'],groups['group_state_count'])
    point={name:screen[name][inverse] for name in
        ('minimum_squared','maximum_squared','query_count','safe_count','safe_maximum_squared')}
    np.testing.assert_array_equal(point['query_count'].astype(np.int32),original['state_count'])
    dangerous=np.flatnonzero(point['maximum_squared']>40).astype(np.uint32)
    safe_rows=sum(int(v) for v in point['safe_count'][dangerous]);empty=int(np.count_nonzero(point['safe_count']==0))
    expanded_danger=sum(int(m) for m,q in zip(groups['multiplicity'],screen['maximum_squared']) if int(q)>40)
    expanded_rows=sum(int(m)*int(n) for m,q,n in zip(groups['multiplicity'],screen['maximum_squared'],screen['safe_count']) if int(q)>40)
    assert expanded_danger==len(dangerous) and expanded_rows==safe_rows
    gate=empty==0 and len(dangerous)<=gates['dangerous_original_points_max'] and safe_rows<=gates['safe_original_table_rows_max']
    np.savez_compressed(OUT/'group-screen.npz',**screen)
    np.savez_compressed(OUT/'point-screen.npz',source_keys=original['keys'],dangerous_rows=dangerous,**point)
    if gate:
        offsets=np.r_[0,np.cumsum(point['safe_count'][dangerous],dtype=np.int64)]
        allowed=np.empty((safe_rows,3),np.uint8)
        for j,row in enumerate(dangerous):
            group=int(inverse[row])
            allowed[offsets[j]:offsets[j+1]]=screen['allowed_rgb'][screen['offsets'][group]:screen['offsets'][group+1]]
        np.savez_compressed(OUT/'danger-allowed.npz',source_keys=original['keys'][dangerous],offsets=offsets,allowed_rgb=allowed)
    result=dict(within_gate=bool(gate),stop=None if gate else 'empty_or_original_point_resource_gate',
        frozen_sha256=sha(OUT/'frozen.json'),contract_sha256=sha(OUT/'contract.json'),groups=len(keys),original_points=len(inverse),
        logical_point_states=5284765,old_logical_state_stop_preserved=True,main_true_suffix_state_queries=queries,
        independent_queries_expected=queries,aggregate_queries_expected=2*queries,
        dangerous_original_points=len(dangerous),safe_original_table_rows=safe_rows,zero_safe_original_points=empty,
        zero_training_mass_dangerous_points=int(np.count_nonzero(original['training_counts'][dangerous]==0)),
        group_safe_csr_rows=len(screen['allowed_rgb']),group_array_payload_bytes=sum(v.nbytes for v in screen.values()),
        point_array_payload_bytes=sum(v.nbytes for v in point.values()),
        process_memory_observation=psutil.Process().memory_info()._asdict(),
        memory_scope='进程记录时刻/OS峰和数组有效载荷，不是部署RAM或精确全暂态和',
        solver_calls=0,performance_samples=0,
        outputs={p.name:{'sha256':sha(p),'bytes':p.stat().st_size} for p in OUT.glob('*.npz')},
        scope='完整组查询与原point展开安全表示；门内也不保证共享解/mean/p99/速度，不CP')
    load_frozen();save(OUT/'summary.json',result)
    print({k:result[k] for k in ('within_gate','groups','main_true_suffix_state_queries','dangerous_original_points','safe_original_table_rows','zero_safe_original_points')},flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('freeze','contract','run'))
    args=parser.parse_args();{'freeze':freeze,'contract':contract,'run':run}[args.mode]()
