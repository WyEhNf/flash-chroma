"""独立全可行投影及最小L1有限合同，不执行当前真实模型。"""
from __future__ import annotations
import argparse
import copy
import itertools
import json
from pathlib import Path
from ortools.sat.python import cp_model
from prepare_cinema_first_cpsat import add_point,contract_cases
from cinema_first_cpsat_model import build_model,reduce_row,SAFE
from cinema_first_safe_cpsat_model import build_safe_model
from cinema_current_safe_identity import sha
ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--frozen',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖当前安全minL1有限合同')
    freeze=json.loads(args.frozen.read_text(encoding='utf-8'))
    for name,expected in freeze['source_sha256'].items():
        if sha(ROOT/name)!=expected:raise ValueError('有限合同源已变：'+name)
    cases=contract_cases();half=copy.deepcopy(cases[0]);half['name']='forced_negative_l1_1';half['problem']['points'][0]['allowed_deltas']=[[-1,0,0]]
    shared=copy.deepcopy(cases[3]);shared['name']='forced_shared_l1_2';shared['problem']['points'][0]['allowed_deltas']=[[-1,0,0]]
    mixed={'variables':[{'name':'red_zero','lower':0,'upper':2},{'name':'green_white','lower':-2,'upper':0},{'name':'blue','lower':-1,'upper':1}],
        'n_node_variables':3,'rows':[],'points':[]}
    add_point(mixed,[7*32768,455*32768,36*32768],[[[0,32768]],[[1,32768]],[[2,32768]]],[[5,227,19]])
    cases.extend((half,shared,{'name':'three_channel_allowed_l1_4','problem':mixed}));records=[]
    for case in cases:
        problem=case['problem'];n=problem['n_node_variables'];problem.update(schema='cinema_first_safe_cpsat_problem_v1',
            objective={'kind':'minimize_node_delta_l1','node_variables':n},objective_absolute_upper_bound=sum(max(abs(v['lower']),abs(v['upper'])) for v in problem['variables'][:n]))
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
        model,variables=build_model(problem)
        class Capture(cp_model.CpSolverSolutionCallback):
            def __init__(self):super().__init__();self.rows=set()
            def on_solution_callback(self):self.rows.add(tuple(int(self.value(v)) for v in variables))
        callback=Capture();solver=cp_model.CpSolver();solver.parameters.num_search_workers=1;solver.parameters.enumerate_all_solutions=True;solver.parameters.max_time_in_seconds=10.
        projection_status=solver.solve(model,callback)
        if callback.rows!=expected or projection_status not in (cp_model.OPTIMAL,cp_model.INFEASIBLE):raise AssertionError('完整整数节点投影不同于独立穷举')
        optimal,values,absolutes=build_safe_model(problem);path=args.output.with_name(args.output.stem+'-'+case['name']+'.pb')
        if path.exists() or not optimal.export_to_file(str(path)):raise ValueError('有限PB已存在或导出失败')
        worker=cp_model.CpSolver();worker.parameters.num_search_workers=1;worker.parameters.max_time_in_seconds=10.;status=worker.solve(optimal)
        if expected:
            minimum=min(sum(abs(v) for v in row[:n]) for row in expected);actual=tuple(int(worker.value(v)) for v in values)
            actual_abs=[int(worker.value(v)) for v in absolutes]
            if status!=cp_model.OPTIMAL or actual not in expected or actual_abs!=[abs(v) for v in actual[:n]] or sum(actual_abs)!=minimum:raise AssertionError('最小L1或abs不等于独立穷举')
        else:
            if status!=cp_model.INFEASIBLE:raise AssertionError('有限无解域未拒绝')
            minimum=None
        records.append({'name':case['name'],'complete_projection_equal':True,'feasible_assignments':len(expected),'minimum_l1':minimum,'status':worker.status_name(status),'model_proto_sha256':sha(path)})
    if [r['minimum_l1'] for r in records[-3:]]!=[1,2,4]:raise AssertionError('正L1边界未被真实覆盖')
    rejected=0
    for terms,domains in (([[0,SAFE]],[{'lower':-2,'upper':2}]),([[0,SAFE+1]],[{'lower':0,'upper':1}])):
        try:reduce_row(terms,-1,1,domains)
        except OverflowError:rejected+=1
        else:raise AssertionError('溢出行未拒绝')
    result={'pass':True,'frozen_sha256':sha(args.frozen),'source_sha256':freeze['source_sha256'],'cases':records,'overflow_rows_rejected':rejected,
        'scope':'8组有限全节点域CP投影/独立整数集合和最小L1合同，未构造或求解4985危险点真实模型。'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'pass':True,'cases':len(records),'overflow_rejected':rejected},flush=True)


if __name__=='__main__':main()
