"""独立Python真整数逐组穷举全部后缀状态，核散回与原point门。"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
from screen_cinema_current_box_group import OUT,load_frozen,read,save,sha


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():
        raise FileExistsError('不覆盖同盒完整screen独立审计')
    frozen=load_frozen();summary=read(OUT/'summary.json')
    assert summary['frozen_sha256']==sha(OUT/'frozen.json')
    for name,spec in summary['outputs'].items():
        assert sha(OUT/name)==spec['sha256'],name
    with np.load(frozen['inputs']['geometry_groups.npz']['path']) as data:
        groups={n:data[n] for n in data.files}
    with np.load(frozen['inputs']['old_aabb']['path']) as data:
        original={n:data[n] for n in data.files}
    with np.load(OUT/'group-screen.npz') as data:
        screen={n:data[n] for n in data.files}
    with np.load(OUT/'point-screen.npz') as data:
        point={n:data[n] for n in data.files}
    suffix=np.load(frozen['inputs']['suffix']['path'],mmap_mode='r');queries=0
    names=('minimum_squared','maximum_squared','query_count','safe_count','safe_maximum_squared')
    for group,key in enumerate(groups['group_keys']):
        values=[int(v) for v in key];lo,hi,gold=values[:3],values[3:6],values[6:]
        qvalues=[];safe=[]
        for r in range(lo[0],hi[0]+1):
            for g in range(lo[1],hi[1]+1):
                for b in range(lo[2],hi[2]+1):
                    output=suffix[(r*256+g)*256+b]
                    q=sum((int(v)-t)**2 for v,t in zip(output,gold));qvalues.append(q);queries+=1
                    if q<=40:
                        safe.append([r,g,b])
        expected=[min(qvalues),max(qvalues),len(qvalues),len(safe),max((q for q in qvalues if q<=40),default=-1)]
        assert expected==[int(screen[name][group]) for name in names]
        assert safe==screen['allowed_rgb'][screen['offsets'][group]:screen['offsets'][group+1]].tolist()
        assert int(screen['offsets'][group+1])-int(screen['offsets'][group])==len(safe)
    assert queries==summary['main_true_suffix_state_queries']==1267197
    assert queries<=frozen['plan']['资源门']['maximum_group_query_states_per_complete_path']
    dangerous=[];rows=empty=0
    for i in range(len(original['keys'])):
        group=int(groups['inverse'][i]);key=groups['group_keys'][group]
        assert key.tolist()==[*original['lower_rgb'][i].tolist(),*original['upper_rgb'][i].tolist(),*original['gold'][i].tolist()]
        for name in names:
            assert int(point[name][i])==int(screen[name][group])
        assert int(point['query_count'][i])==int(original['state_count'][i])
        if int(point['safe_count'][i])==0:
            empty+=1
        if int(point['maximum_squared'][i])>40:
            dangerous.append(i);rows+=int(point['safe_count'][i])
    np.testing.assert_array_equal(original['keys'],point['source_keys']);assert dangerous==point['dangerous_rows'].tolist()
    assert len(dangerous)==summary['dangerous_original_points'] and rows==summary['safe_original_table_rows'] and empty==summary['zero_safe_original_points']
    gate=empty==0 and len(dangerous)<=8192 and rows<=500000
    assert gate==summary['within_gate']
    if gate:
        with np.load(OUT/'danger-allowed.npz') as data:
            expanded={n:data[n] for n in data.files}
        assert len(expanded['allowed_rgb'])==rows and len(expanded['offsets'])==len(dangerous)+1
        assert expanded['source_keys'].tolist()==original['keys'][dangerous].tolist()
        for j,row in enumerate(dangerous):
            group=int(groups['inverse'][row]);a,b=[int(v) for v in expanded['offsets'][j:j+2]]
            assert b-a==int(point['safe_count'][row])
            np.testing.assert_array_equal(expanded['allowed_rgb'][a:b],screen['allowed_rgb'][screen['offsets'][group]:screen['offsets'][group+1]])
    else:
        assert not (OUT/'danger-allowed.npz').exists()
    load_frozen();save(args.output,dict(**{'pass':True},frozen_sha256=sha(OUT/'frozen.json'),summary_sha256=sha(OUT/'summary.json'),
        groups=len(groups['group_keys']),original_points=len(original['keys']),independent_true_suffix_state_queries=queries,
        main_true_suffix_state_queries=summary['main_true_suffix_state_queries'],aggregate_true_suffix_state_queries=2*queries,
        dangerous_original_points=len(dangerous),safe_original_table_rows=rows,zero_safe_original_points=empty,
        within_gate=gate,all_group_stats_and_csr_equal=True,all_original_point_scatter_equal=True,
        solver_calls=0,performance_samples=0))
    print({'screen_independent_pass':True,'queries':queries,'aggregate_queries':2*queries,'within_gate':gate},flush=True)


if __name__=='__main__':
    main()
