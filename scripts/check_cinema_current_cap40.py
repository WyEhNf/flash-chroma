"""隔离环境有限全可行投影及首解成员合同，不运行真实cap40问题。"""
from __future__ import annotations
import argparse
import copy
import itertools
import importlib.metadata
import json
from pathlib import Path
import platform
import sys
from ortools.sat.python import cp_model
from cinema_first_cpsat_model import build_model,reduce_row,SAFE
from prepare_cinema_first_cpsat import add_point,contract_cases
from cinema_current_cap40_identity import SOLVE,sha,verify_lock
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/cinema-current-cap40-cpsat-v1'


def main():
    p=argparse.ArgumentParser(description=__doc__);p.parse_args()
    if (OUT/'contract.json').exists():raise FileExistsError('不覆盖新cap40有限合同')
    frozen=json.loads((OUT/'frozen.json').read_text(encoding='utf-8'))
    for name,expected in frozen['source_sha256'].items():assert sha(ROOT/name)==expected,name
    for name,expected in frozen['inputs_sha256'].items():assert sha(name)==expected,name
    lock_path=Path(frozen['environment_lock']);lock=json.loads(lock_path.read_text(encoding='utf-8'))
    verify_lock({'environment_lock_sha256':sha(lock_path)},lock_path)
    environment={'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'environment_lock_sha256':sha(lock_path),
        'packages':{name:importlib.metadata.version(name) for name in lock['packages']},
        'verified_installed_record_sha256':lock['installed_record_sha256']}
    cases=contract_cases();forced=copy.deepcopy(cases[0]);forced['name']='forced_nonzero_negative';forced['problem']['points'][0]['allowed_deltas']=[[-1,0,0]];cases.append(forced)
    mixed={'variables':[{'name':'red','lower':-1,'upper':1},{'name':'green_white','lower':-1,'upper':0},{'name':'blue_zero','lower':0,'upper':1}],
        'n_node_variables':3,'rows':[],'points':[]}
    add_point(mixed,[3*65536,255*65536,0],[[[0,65536]],[[1,65536]],[[2,65536]]],[[4,254,1]])
    cases.append({'name':'three_outputs_forced_nonzero','problem':mixed});records=[]
    for case in cases:
        problem=case['problem'];n=problem['n_node_variables']
        for v in problem['variables'][:n]:v['lower']=max(v['lower'],-1);v['upper']=min(v['upper'],1)
        problem['rows']=[reduce_row(r['raw_terms'],r['raw_lower'],r['raw_upper'],problem['variables']) for r in problem['rows']]
        expected=set()
        for assignment in itertools.product(*[range(v['lower'],v['upper']+1) for v in problem['variables'][:n]]):
            values=list(assignment)+[0]*(len(problem['variables'])-n);good=True
            for point in problem['points']:
                output=[]
                for c in range(3):
                    acc=point['original_acc'][c]+sum(w*assignment[i] for i,w in point['node_terms'][c]);z=(acc+32768)//65536-point['original_rgb'][c]
                    values[point['z_indices'][c]]=z;output.append(z)
                if output not in point['allowed_deltas']:good=False;break
            if good:expected.add(tuple(values))
        model,variables=build_model(problem);assert not model.has_objective()
        class Capture(cp_model.CpSolverSolutionCallback):
            def __init__(self):super().__init__();self.members=set()
            def on_solution_callback(self):self.members.add(tuple(int(self.value(v)) for v in variables))
        callback=Capture();solver=cp_model.CpSolver();solver.parameters.num_search_workers=1;solver.parameters.enumerate_all_solutions=True;solver.parameters.max_time_in_seconds=10.
        status=solver.solve(model,callback);assert callback.members==expected and status in (cp_model.OPTIMAL,cp_model.INFEASIBLE)
        first=cp_model.CpSolver()
        for k,v in SOLVE.items():setattr(first.parameters,k,v)
        first.parameters.max_time_in_seconds=10.;first_status=first.solve(model)
        if expected:
            assert first_status in (cp_model.FEASIBLE,cp_model.OPTIMAL);actual=tuple(int(first.value(v)) for v in variables);assert actual in expected
            if case['name'] in ('forced_nonzero_negative','three_outputs_forced_nonzero'):assert any(actual[:n])
        else:assert first_status==cp_model.INFEASIBLE
        records.append({'name':case['name'],'complete_projection_equal':True,'feasible_assignments':len(expected),
            'first_solution_status':first.status_name(first_status),'forced_positive_perturbation':case['name'].startswith(('forced_','three_outputs')),
            'minimum_observed_l1_from_exhaustive':min((sum(abs(v) for v in row[:n]) for row in expected),default=None)})
    rejected=0
    for terms,domains in (([[0,SAFE]],[{'lower':-2,'upper':2}]),([[0,SAFE+1]],[{'lower':0,'upper':1}])):
        try:reduce_row(terms,-1,1,domains)
        except OverflowError:rejected+=1
        else:raise AssertionError('溢出行未拒绝')
    result={'pass':True,'frozen_sha256':sha(OUT/'frozen.json'),'cases':records,'overflow_rows_rejected':rejected,'environment':environment,
        'scope':'有限完整投影/首解成员/强制非零合同；没有构造或求解12993变量真实模型。'}
    (OUT/'contract.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print({'pass':True,'cases':len(records),'overflow_rejected':rejected},flush=True)


if __name__=='__main__':main()
