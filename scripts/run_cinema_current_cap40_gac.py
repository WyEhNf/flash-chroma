"""冻结/有限合同/唯一真实GAC及独立重放；纯整数，不导入NumPy/ORTools。"""
from __future__ import annotations
import argparse
import ast
import copy
import itertools
import json
from pathlib import Path
from cinema_cap40_gac_core import propagate,compile_points,supported_masks
from cinema_cap40_gac_checker import independent_support,verify_certificate
from cinema_current_cap40_identity import sha,verify
from prepare_cinema_first_cpsat import add_point,contract_cases
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/cinema-current-cap40-gac-v1'
SOURCE=ROOT/'artifacts/cinema-current-cap40-cpsat-v1'


def save(path,value):
    if path.exists():raise FileExistsError('不覆盖GAC独立证据')
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def freeze():
    if OUT.exists():raise FileExistsError('不覆盖GAC阶段')
    problem_path=SOURCE/'problem.json';assert sha(problem_path)=='f492e49bc17dd98efbf743629180a8ed656729d859c1953bbe83f3c29ddfe41c'
    problem=json.loads(problem_path.read_text(encoding='utf-8'));verify(problem)
    prior_independent_path=SOURCE/'problem-independent.json';prior_independent=json.loads(prior_independent_path.read_text(encoding='utf-8'))
    assert prior_independent['pass'] and prior_independent['problem_sha256']==sha(problem_path)
    sources=dict(problem['source_sha256'])
    for name in ['experiments/p16-cinema-current-cap40-gac-v1.json','experiments/p16-cinema-current-cap40-gac-proposal-v1.md',
        'scripts/cinema_cap40_gac_core.py','scripts/cinema_cap40_gac_checker.py','scripts/run_cinema_current_cap40_gac.py']:sources[name]=sha(ROOT/name)
    for name,expected in sources.items():
        assert sha(ROOT/name)==expected,name
        if name.endswith('.py'):ast.parse((ROOT/name).read_text(encoding='utf-8-sig'))
    plan=json.loads((ROOT/'experiments/p16-cinema-current-cap40-gac-v1.json').read_text(encoding='utf-8'))
    save(OUT/'frozen.json',{'ast_pass':True,'source_sha256':sources,'problem_path':str(problem_path),'problem_sha256':sha(problem_path),
        'prior_independent_sha256':sha(prior_independent_path),'plan':plan,'search_calls':0})
    print({'frozen_sha256':sha(OUT/'frozen.json'),'sources':len(sources),'search_calls':0},flush=True)


def load_frozen():
    frozen=json.loads((OUT/'frozen.json').read_text(encoding='utf-8'))
    for name,expected in frozen['source_sha256'].items():assert sha(ROOT/name)==expected,name
    assert sha(frozen['problem_path'])==frozen['problem_sha256'];return frozen


def all_assignments(problem):
    n=problem['n_node_variables'];good=[]
    for assignment in itertools.product(*[range(v['lower'],v['upper']+1) for v in problem['variables'][:n]]):
        valid=True
        for point in problem['points']:
            z=[]
            for c in range(3):
                acc=point['original_acc'][c]+sum(w*assignment[i] for i,w in point['node_terms'][c]);z.append((acc+32768)//65536-point['original_rgb'][c])
            if z not in point['allowed_deltas']:valid=False;break
        if valid:good.append(assignment)
    return good


def contract():
    frozen=load_frozen()
    if (OUT/'contract.json').exists():raise FileExistsError('不覆盖GAC有限合同')
    gates=frozen['plan']['资源门'];cases=contract_cases()
    for case in cases:
        for v in case['problem']['variables'][:case['problem']['n_node_variables']]:v['lower']=max(v['lower'],-1);v['upper']=min(v['upper'],1)
    forced=copy.deepcopy(cases[0]);forced['name']='forced_nonzero';forced['problem']['points'][0]['allowed_deltas']=[[-1,0,0]];cases.append(forced)
    cascade={'variables':[{'name':'x','lower':-1,'upper':1},{'name':'y','lower':-1,'upper':1}],'n_node_variables':2,'rows':[],'points':[]}
    add_point(cascade,[128*65536]*3,[[[0,65536]],[],[]],[[129,128,128]])
    add_point(cascade,[128*65536]*3,[[[0,32768],[1,32768]],[],[]],[[128,128,128]])
    add_point(cascade,[128*65536]*3,[[[1,65536]],[],[]],[[129,128,128]])
    cases.append({'name':'cross_point_cascade_empty','problem':cascade})
    odd={'variables':[{'name':n,'lower':0,'upper':1} for n in ('r','g','b')],'n_node_variables':3,'rows':[],'points':[]}
    add_point(odd,[128*65536]*3,[[[0,65536]],[[1,65536]],[]],[[128,129,128],[129,128,128]])
    add_point(odd,[128*65536]*3,[[],[[1,65536]],[[2,65536]]],[[128,128,129],[128,129,128]])
    add_point(odd,[128*65536]*3,[[[0,65536]],[],[[2,65536]]],[[128,128,129],[129,128,128]])
    cases.append({'name':'arc_consistent_odd_cycle_unsat','problem':odd})
    duplicate={'variables':[{'name':'x','lower':0,'upper':1}],'n_node_variables':1,'rows':[],'points':[]}
    add_point(duplicate,[0,128*65536,128*65536],[[[0,32768],[0,32768]],[],[]],[[1,128,128]])
    cases.append({'name':'duplicate_coefficients_clipped_zero','problem':duplicate})
    constant={'variables':[],'n_node_variables':0,'rows':[],'points':[]};add_point(constant,[128*65536]*3,[[],[],[]],[[129,128,128]])
    cases.append({'name':'constant_empty','problem':constant});records=[]
    for case in cases:
        problem=case['problem'];expected=all_assignments(problem);result=propagate(problem,gates);checked=verify_certificate(problem,result)
        domains,points,_=compile_points(problem)
        for point,raw in zip(points,problem['points']):
            fast,retained,_=supported_masks(point,domains);sets=[set(range(v['lower'],v['upper']+1)) for v in problem['variables'][:problem['n_node_variables']]]
            other,count,_=independent_support(raw,sets,len(sets));assert count==retained
            assert fast=={i:sum(1<<(v+1) for v in values) for i,values in other.items()}
            single={**problem,'points':[raw]};joint=all_assignments(single)
            exact={i:{assignment[i] for assignment in joint} for i in other}
            assert exact==other, '有限全局笛卡尔支持不同于通道因式分解'
        for assignment in expected:assert all(result['domain_masks'][i]&(1<<(v+1)) for i,v in enumerate(assignment))
        if result['status']=='GAC_CONTRADICTION':assert not expected
        if case['name']=='arc_consistent_odd_cycle_unsat':assert not expected and result['status']=='GAC_FIXPOINT_UNDECIDED'
        if case['name'] in ('cross_point_cascade_empty','constant_empty'):assert result['status']=='GAC_CONTRADICTION'
        records.append({'name':case['name'],'global_assignments':len(expected),'gac_status':result['status'],'deletions':result['deletions'],'checker_pass':checked['pass']})
    bad=copy.deepcopy(cases[0]['problem']);bad['points'][0]['node_terms'][1]=bad['points'][0]['node_terms'][0]
    try:compile_points(bad)
    except ValueError:overlap_rejected=True
    else:raise AssertionError('跨通道共享变量未拒绝')
    save(OUT/'contract.json',{'pass':True,'frozen_sha256':sha(OUT/'frozen.json'),'cases':records,'cross_channel_overlap_rejected':overlap_rejected,'search_calls':0})
    print({'pass':True,'cases':len(records),'search_calls':0},flush=True)


def run():
    frozen=load_frozen();contract=json.loads((OUT/'contract.json').read_text(encoding='utf-8'));assert contract['pass'] and contract['frozen_sha256']==sha(OUT/'frozen.json')
    if (OUT/'certificate.json').exists():raise FileExistsError('不覆盖唯一真实GAC')
    problem=json.loads(Path(frozen['problem_path']).read_text(encoding='utf-8'));verify(problem)
    result=propagate(problem,frozen['plan']['资源门']);result.update(problem_sha256=frozen['problem_sha256'],frozen_sha256=sha(OUT/'frozen.json'),contract_sha256=sha(OUT/'contract.json'))
    save(OUT/'certificate.json',result)
    print({k:result[k] for k in ('status','reason','point_revisions','local_assignments','deletions')},flush=True)


def audit():
    frozen=load_frozen();path=OUT/'certificate.json';result=json.loads(path.read_text(encoding='utf-8'))
    if (OUT/'independent.json').exists():raise FileExistsError('不覆盖唯一真实GAC独立重放')
    assert result['problem_sha256']==frozen['problem_sha256'] and result['frozen_sha256']==sha(OUT/'frozen.json')
    problem=json.loads(Path(frozen['problem_path']).read_text(encoding='utf-8'));verify(problem);checked=verify_certificate(problem,result)
    physical=sorted({problem['variables'][i]['physical_node'] for i in checked['reason_variable_indices']})
    checked.update(problem_sha256=frozen['problem_sha256'],certificate_sha256=sha(path),certificate_reason_physical_nodes=physical,
        physical_node_rule='所有删值原因point中node_terms涉及的原273变量物理节点，不仅删除变量；非混合半径执行授权。')
    save(OUT/'independent.json',checked)
    print({'pass':True,'status':checked['status'],'deletions':checked['independently_checked_deletions'],
        'contradiction_replayed':checked['contradiction_replayed'],'reason_physical_nodes':len(physical)},flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['freeze','contract','run','audit']);a=p.parse_args();{'freeze':freeze,'contract':contract,'run':run,'audit':audit}[a.mode]()
