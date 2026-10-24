"""复用八组完整投影证据，独立检查无目标首解参数与有限整数成员。"""
from __future__ import annotations
import argparse
import copy
import itertools
import json
from pathlib import Path
from ortools.sat.python import cp_model
from prepare_cinema_first_cpsat import add_point,contract_cases
from cinema_first_cpsat_model import build_model
from cinema_current_feasible_identity import SOLVE,sha
ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--frozen',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖首解有限合同')
    freeze=json.loads(args.frozen.read_text(encoding='utf-8'))
    for name,expected in freeze['source_sha256'].items():
        if sha(ROOT/name)!=expected:raise ValueError('首解合同源已变：'+name)
    prior_path=Path(freeze['inputs']['prior_contract']['path']);prior=json.loads(prior_path.read_text(encoding='utf-8'))
    if sha(prior_path)!=freeze['inputs']['prior_contract']['sha256'] or not prior['pass'] or len(prior['cases'])!=8:raise ValueError('原完整投影合同不符')
    for name,expected in prior['source_sha256'].items():
        if sha(ROOT/name)!=expected:raise ValueError('原完整投影执行源已变：'+name)
    cases=contract_cases();half=copy.deepcopy(cases[0]);half['name']='forced_negative_l1_1';half['problem']['points'][0]['allowed_deltas']=[[-1,0,0]]
    shared=copy.deepcopy(cases[3]);shared['name']='forced_shared_l1_2';shared['problem']['points'][0]['allowed_deltas']=[[-1,0,0]]
    mixed={'variables':[{'name':'red_zero','lower':0,'upper':2},{'name':'green_white','lower':-2,'upper':0},{'name':'blue','lower':-1,'upper':1}],
        'n_node_variables':3,'rows':[],'points':[]}
    add_point(mixed,[7*32768,455*32768,36*32768],[[[0,32768]],[[1,32768]],[[2,32768]]],[[5,227,19]])
    cases.extend((half,shared,{'name':'three_channel_allowed_l1_4','problem':mixed}));records=[]
    for case,prior_case in zip(cases,prior['cases']):
        problem=case['problem'];n=problem['n_node_variables'];expected=set()
        for assignment in itertools.product(*[range(v['lower'],v['upper']+1) for v in problem['variables'][:n]]):
            values=list(assignment)+[0]*(len(problem['variables'])-n);good=True
            for point in problem['points']:
                output=[]
                for c in range(3):
                    acc=point['original_acc'][c]+sum(w*assignment[i] for i,w in point['node_terms'][c]);z=(acc+32768)//65536-point['original_rgb'][c]
                    values[point['z_indices'][c]]=z;output.append(z)
                if output not in point['allowed_deltas']:good=False;break
            if good:expected.add(tuple(values))
        if case['name']!=prior_case['name'] or len(expected)!=prior_case['feasible_assignments']:raise AssertionError('原有限完整集合身份不同')
        model,variables=build_model(problem)
        if model.has_objective():raise AssertionError('有限首解模型含目标')
        path=args.output.with_name(args.output.stem+'-'+case['name']+'.pb')
        if path.exists() or not model.export_to_file(str(path)):raise ValueError('有限首解PB已存在或导出失败')
        solver=cp_model.CpSolver()
        for name,value in SOLVE.items():setattr(solver.parameters,name,value)
        solver.parameters.max_time_in_seconds=10.;status=solver.solve(model)
        if expected:
            if status not in (cp_model.FEASIBLE,cp_model.OPTIMAL):raise AssertionError('有限首解未返回可行成员')
            actual=tuple(int(solver.value(v)) for v in variables)
            if actual not in expected:raise AssertionError('首解不属于独立真实整数集合')
            observed=sum(abs(v) for v in actual[:n])
        else:
            if status!=cp_model.INFEASIBLE:raise AssertionError('有限空域没有拒绝')
            observed=None
        records.append({'name':case['name'],'independent_feasible_assignments':len(expected),'status':solver.status_name(status),
            'first_solution_member_verified':bool(expected),'objective_encoded':model.has_objective(),'observed_node_l1':observed,
            'model_proto_sha256':sha(path),'parameters':str(solver.parameters)})
    result={'pass':True,'source_sha256':freeze['source_sha256'],'prior_complete_projection_contract_sha256':sha(prior_path),
        'cases':records,'scope':'原8组完整投影证据不重写；新无目标/首解参数有限成员检查，L1只观察，未构造或求解15321变量真实问题。'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'pass':True,'first_solution_cases':len(records),'objective_encoded':False},flush=True)


if __name__=='__main__':main()
