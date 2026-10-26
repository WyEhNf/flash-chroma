"""只数既有安全关系及补集的完整原point成本；不查询后缀、不构造CP。"""
from __future__ import annotations
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import psutil

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/cinema-cap40-complement-census-v1'
PLAN=ROOT/'experiments/p16-cinema-cap40-complement-census-v1.md'
INPUTS={
 'geometry_frozen':('artifacts/cinema-current-box-group-geometry-v1/frozen.json','6753527ad70f63659cd93ac29517e68525a39b2375170c4e7ebce3cb1fea8c8a'),
 'geometry_groups':('artifacts/cinema-current-box-group-geometry-v1/groups.npz','e0d2ad708d65adac99c7c571b8889c74b85382d4bae3fc410b21745fc4e2bf70'),
 'geometry_summary':('artifacts/cinema-current-box-group-geometry-v1/summary.json','76b48dbfd6e6a081148c1048986ffcd0156b033603342a9720d05b7b404c7ec0'),
 'geometry_audit':('artifacts/cinema-current-box-group-geometry-v1/independent.json','f3b0dbf4e30fa7dc45baa8b97ed89f435c6faf3576c763d8607b5331c2ccb141'),
 'screen_frozen':('artifacts/cinema-current-box-group-screen-v1/frozen.json','d1103997455ee40d99381840b00291e102cd9721c1600420af79d71a638bd9fb'),
 'screen_summary':('artifacts/cinema-current-box-group-screen-v1/summary.json','faceafb72f5c4d7e2253d1da8840a55a8686fc15a54663f35ef2bcc226794aee'),
 'screen_audit':('artifacts/cinema-current-box-group-screen-v1/independent.json','8bd29e5315224c0b658233ae83da2559e3979215386f20eb30dce03ab98b790b'),
 'group_stats':('artifacts/cinema-current-box-group-screen-v1/group-screen.npz','464b0349c80ef5ee23d992519d43c7359c213868d6a2c1d021e6c11cfae5ffc5'),
 'point_stats':('artifacts/cinema-current-box-group-screen-v1/point-screen.npz','37b00e42e30a5a1a56a8706efde5770b404e00b38855ca1154b59487c3f7e6ec')}


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path,value):
    if path.exists():
        raise FileExistsError('不覆盖补集普查原件：'+str(path))
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def freeze():
    if OUT.exists():
        raise FileExistsError('不覆盖补集阶段')
    sources={}
    for name in ('AGENTS.md',PLAN.relative_to(ROOT).as_posix(),
                 'scripts/census_cinema_cap40_complements.py','scripts/audit_cinema_cap40_complements.py'):
        path=ROOT/name
        if name.endswith('.py'):
            ast.parse(path.read_text(encoding='utf-8-sig'),filename=name)
        sources[name]=sha(path)
    inputs={}
    for name,(relative,expected) in INPUTS.items():
        path=ROOT/relative
        assert sha(path)==expected,name
        inputs[name]=dict(path=str(path),sha256=expected,bytes=path.stat().st_size)
    prior=read(inputs['screen_summary']['path']);audit=read(inputs['screen_audit']['path'])
    assert not prior['within_gate'] and audit['pass']
    assert audit['summary_sha256']==inputs['screen_summary']['sha256']
    assert prior['dangerous_original_points']==17620 and prior['safe_original_table_rows']==1525836
    save(OUT/'frozen.json',dict(sources_sha256=sources,inputs=inputs,proposal=PLAN.read_text(encoding='utf-8'),
        python=sys.version,numpy=np.__version__,psutil=psutil.__version__,byteorder=sys.byteorder,
        actual_suffix_queries=0,solver_calls=0,native_calls=0,performance_samples=0))
    print(dict(frozen_sha256=sha(OUT/'frozen.json'),sources=len(sources),inputs=len(inputs)),flush=True)


def checked():
    frozen=read(OUT/'frozen.json')
    for name,expected in frozen['sources_sha256'].items():
        assert sha(ROOT/name)==expected,name
    for name,spec in frozen['inputs'].items():
        assert sha(spec['path'])==spec['sha256'] and Path(spec['path']).stat().st_size==spec['bytes'],name
    return frozen


def summarize(q,s):
    q,s=np.asarray(q),np.asarray(s)
    if q.ndim!=1 or q.shape!=s.shape or q.dtype.kind not in 'iu' or s.dtype.kind not in 'iu':
        raise ValueError('需要同长一维整数计数')
    q,s=q.astype(np.int64),s.astype(np.int64)
    if np.any((q<1)|(q>125)|(s<0)|(s>q)):
        raise ValueError('计数须满足1<=q<=125及0<=s<=q')
    f=q-s;danger=f>0
    orientation=np.where(~danger,0,np.where(f<=s,2,1)).astype(np.uint8)
    rows=dict(points=len(q),dangerous_points=int(np.count_nonzero(danger)),empty_safe_points=int(np.count_nonzero(s==0)),
        all_positive_rows=int(s[danger].sum()),all_negative_rows=int(f[danger].sum()),
        mixed_rows=int(np.minimum(s[danger],f[danger]).sum()),
        mixed_positive_points=int(np.count_nonzero(orientation==1)),mixed_negative_points=int(np.count_nonzero(orientation==2)))
    return rows,orientation


def contract():
    checked()
    q=np.array([1,2,8,125,125,3],np.uint8);s=np.array([1,0,4,124,1,2],np.uint8)
    rows,orientation=summarize(q,s)
    assert rows==dict(points=6,dangerous_points=5,empty_safe_points=1,all_positive_rows=131,
                     all_negative_rows=132,mixed_rows=7,mixed_positive_points=2,mixed_negative_points=3)
    assert orientation.tolist()==[0,1,2,2,1,2]
    assert summarize(np.array([],np.int64),np.array([],np.int64))[0]['points']==0
    rejects=0
    for a,b in (([0],[0]),([126],[1]),([2],[-1]),([2],[3]),([2.0],[1.0])):
        try:
            summarize(a,b)
        except ValueError:
            rejects+=1
    assert rejects==5
    inverse=np.array([0,1,0,2,1,2,2],np.uint32)
    group_q=np.array([2,8,3],np.uint8);group_s=np.array([1,7,0],np.uint8)
    point_rows,_=summarize(group_q[inverse],group_s[inverse])
    assert point_rows['all_negative_rows']==2*1+2*1+3*3
    assert point_rows['all_positive_rows']==2*1+2*7+3*0
    save(OUT/'contract.json',dict(passed=True,frozen_sha256=sha(OUT/'frozen.json'),
        scalar_boundary_points=6,empty_input_cases=1,invalid_cases=rejects,repeated_group_points=7,
        actual_suffix_queries=0,solver_calls=0))
    print(dict(contract_passed=True,invalid_cases=rejects),flush=True)


def run():
    frozen=checked();finite=read(OUT/'contract.json')
    assert finite['passed'] and finite['frozen_sha256']==sha(OUT/'frozen.json')
    save(OUT/'start.json',dict(frozen_sha256=sha(OUT/'frozen.json'),contract_sha256=sha(OUT/'contract.json')))
    def arrays(name):
        with np.load(frozen['inputs'][name]['path']) as data:
            return {k:data[k] for k in data.files}
    groups,group,point=arrays('geometry_groups'),arrays('group_stats'),arrays('point_stats')
    inverse=groups['inverse'];assert len(inverse)==171271 and len(groups['multiplicity'])==27817
    np.testing.assert_array_equal(groups['source_keys'],point['source_keys'])
    for name in ('query_count','safe_count','maximum_squared'):
        np.testing.assert_array_equal(group[name][inverse],point[name])
    np.testing.assert_array_equal(np.bincount(inverse,minlength=27817),groups['multiplicity'])
    np.testing.assert_array_equal(np.diff(group['offsets']),group['safe_count'])
    rows,orientation=summarize(point['query_count'],point['safe_count'])
    np.testing.assert_array_equal(orientation!=0,point['maximum_squared']>40)
    assert rows['dangerous_points']==17620 and rows['all_positive_rows']==1525836 and rows['empty_safe_points']==0
    group_rows,_=summarize(group['query_count'],group['safe_count'])
    assert group_rows['all_negative_rows']==1267197-1214245
    orientation.tofile(OUT/'orientation-per-point.u8')
    result=dict(passed=True,frozen_sha256=sha(OUT/'frozen.json'),contract_sha256=sha(OUT/'contract.json'),
        point_counts=rows,group_counts=group_rows,
        projected_node_variables=819,projected_output_variables=3*rows['dangerous_points'],
        projected_total_integer_variables=819+3*rows['dangerous_points'],projected_rounding_rows=3*rows['dangerous_points'],
        original_gates=dict(danger_limit=8192,safe_row_limit=500000,danger_pass=False,positive_rows_pass=False),
        row_only_observations=dict(negative_rows_under500000=rows['all_negative_rows']<=500000,mixed_rows_under500000=rows['mixed_rows']<=500000),
        no_new_resource_qualification=True,new_candidate=False,actual_suffix_queries=0,solver_calls=0,native_calls=0,performance_samples=0,
        orientation=dict(bytes=orientation.nbytes,sha256=sha(OUT/'orientation-per-point.u8')),
        process_memory=psutil.Process().memory_info()._asdict(),
        scope='全部原point关系行数，非新CP可行性/部署或速度；旧两门STOP不变。')
    checked();save(OUT/'results.json',result)
    print(dict(point_counts=rows,group_counts=group_rows,no_solver=True),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('freeze','contract','run'))
    args=parser.parse_args();{'freeze':freeze,'contract':contract,'run':run}[args.mode]()
