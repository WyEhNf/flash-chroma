"""只读已认证screen与完整训练频数，统计公共mean/p99桥规模和整数预算。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'python'))
from lutlab import training_budget_bridge as bridge
N=47185920


def digest(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def save(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--frozen',type=Path,required=True);p.add_argument('--contract',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖唯一两预算桥规模普查')
    freeze=read(args.frozen);contract=read(args.contract)
    if not freeze['ast_pass'] or not contract['pass']:raise ValueError('先冻结并通过独立有限合同')
    for sources in (freeze['source_sha256'],contract['source_sha256']):
        for name,expected in sources.items():
            if digest(ROOT/name)!=expected:raise ValueError('冻结源已变：'+name)
    for value in freeze['inputs'].values():
        if digest(value['path'])!=value['sha256']:raise ValueError('冻结输入已变')
    inputs=freeze['inputs'];summary=read(inputs['risk_summary']['path']);audit=read(inputs['risk_audit']['path'])
    if not audit['pass'] or audit['screen_sha256']!=inputs['screen']['sha256'] or audit['summary_sha256']!=inputs['risk_summary']['sha256']:
        raise ValueError('不是已认证screen')
    if not summary['within_frozen_resource_gate'] or summary['zero_safe_rows']:raise ValueError('原风险门或非空安全表未过')
    for metric in ('mean','p99','max'):
        if not summary['comparisons']['best']['uniform']['certificates'][metric]['automatically_protected']:raise ValueError('公共全域充分上界不成立')
    with np.load(inputs['screen']['path']) as data:
        keys=data['keys'].copy();selected=data['selected_nodes'].copy();minimum=data['minimum_squared'].astype(np.int64)
        maximum=data['maximum_squared'].astype(np.int64);safe_max=data['safe_maximum_squared'].astype(np.int64)
        weights=data['training_counts'].astype(np.int64);safe_count=data['safe_count'].astype(np.int64)
        outside=data['outside_training_hist'].copy();best=data['baseline_best_training'].copy()
    if len(keys)!=80751 or len(selected)!=122 or np.any(keys[1:]<=keys[:-1]) or np.any(weights<0) or np.any(minimum<0) or np.any(minimum>safe_max) or np.any(safe_max>47):
        raise AssertionError('已验完整支撑或安全误差域不符')
    if int(weights.sum())!=901853 or int(outside.sum())+int(weights.sum())!=N or int(best.sum())!=N:raise AssertionError('完整原60图固定质量不符')
    freq=np.load(inputs['mass']['path'],mmap_mode='r');total=float(freq.sum(dtype=np.float64));reconstructed=affected=0;max_residual=0.0
    if freq.shape!=(1<<24,) or not total>0:raise AssertionError('不是完整逐RGB训练频数')
    for start in range(0,1<<24,262144):
        end=min(start+262144,1<<24);values=freq[start:end].astype(np.float64)*(N/total);counts=np.rint(values).astype(np.int64)
        max_residual=max(max_residual,float(np.max(np.abs(values-counts),initial=0)))
        if max_residual>1e-6 or np.any(counts<0):raise AssertionError('完整原60图整数频数恢复失败')
        reconstructed+=int(counts.sum());a,b=np.searchsorted(keys,[start,end]);observed=counts[keys[a:b].astype(np.int64)-start]
        np.testing.assert_array_equal(observed,weights[a:b]);affected+=int(observed.sum())
    if reconstructed!=N or affected!=901853:raise AssertionError('完整/受影响训练质量重建不符')
    danger=maximum>47;cost=(weights>0)&(minimum<safe_max);flag=(weights>0)&(minimum<=12)&(safe_max>12);union=danger|cost
    if np.any(flag&~cost) or int(danger.sum())!=4985 or int(safe_count[danger].sum())!=386612:raise AssertionError('分类或原安全表数不符')
    constant_cost=(weights>0)&~cost;fixed_hist=outside.copy()
    for q,w in zip(minimum[constant_cost],weights[constant_cost]):fixed_hist[int(q)]+=int(w)
    baseline_floor,baseline_ceil=bridge.root_sum(best);fixed_floor,fixed_ceil=bridge.root_sum(fixed_hist)
    min_variable=sum(int(w)*bridge.root_bounds(int(q))[1] for q,w in zip(minimum[cost],weights[cost]))
    max_variable=sum(int(w)*bridge.root_bounds(int(q))[1] for q,w in zip(safe_max[cost],weights[cost]))
    fixed_above=int(outside[13:].sum())+int(weights[(~flag)&(minimum>12)].sum());variable_above_max=int(weights[flag].sum())
    count_limit=bridge.above_limit(N);mean_rhs=baseline_floor-fixed_ceil;flag_rhs=count_limit-fixed_above
    for value in (baseline_floor,baseline_ceil,fixed_floor,fixed_ceil,min_variable,max_variable,fixed_above,variable_above_max):
        if not 0<=value<=bridge.SAFE:raise OverflowError('逐项整数总界超保守int64')
    limits=freeze['plan']['固定资源门'];rows=int(safe_count[union].sum());extras=int(cost.sum()+flag.sum())
    gate=len(keys[union])<=limits['union_points_max'] and rows<=limits['safe_rows_max'] and extras<=limits['extra_cost_flag_vars_max']
    args.output.mkdir(parents=True)
    np.savez_compressed(args.output/'classification.npz',keys=keys,union_rows=np.flatnonzero(union).astype(np.uint32),
        danger_rows=np.flatnonzero(danger).astype(np.uint32),cost_rows=np.flatnonzero(cost).astype(np.uint32),
        flag_rows=np.flatnonzero(flag).astype(np.uint32),fixed_training_hist=fixed_hist)
    record={'complete_support_rows':len(keys),'selected_physical_nodes':len(selected),'active_node_components':3*len(selected),
        'danger_points':int(danger.sum()),'danger_zero_training_points':int(np.count_nonzero(danger&(weights==0))),
        'cost_points':int(cost.sum()),'flag_points':int(flag.sum()),'union_points':int(union.sum()),'safe_rows_in_union':rows,
        'extra_cost_flag_variables':extras,'explicit_node_output_cost_flag_variables':3*len(selected)+3*int(union.sum())+extras,
        'explicit_table_cells':3*rows+int(safe_count[cost].sum())+int(safe_count[flag].sum()),
        'fixed_resource_gates':limits,'within_resource_gates':bool(gate),'gate_failure_action':'STOP，不删点/变门/建CP',
        'full_training_pixels':reconstructed,'support_training_pixels':affected,'maximum_frequency_reconstruction_residual':max_residual,
        'root_scale':bridge.SCALE,'baseline_best_root_floor':baseline_floor,'baseline_best_root_ceil':baseline_ceil,
        'fixed_root_floor':fixed_floor,'fixed_root_ceil':fixed_ceil,'variable_root_minimum':min_variable,'variable_root_maximum':max_variable,
        'variable_mean_rhs':mean_rhs,'relaxed_variable_mean_interval_intersects_budget':min_variable<=mean_rhs,
        'p99_threshold_squared':12,'above12_full_mass_limit':count_limit,'fixed_above12_mass':fixed_above,
        'variable_flag_mass_maximum':variable_above_max,'variable_flag_rhs':flag_rhs,'relaxed_flag_interval_intersects_budget':flag_rhs>=0,
        'conditional_full_domain_cap_squared_upper':43,'cp_model_built':False,'cp_solver_called':False,'new_rgb_queries':0,
        'scope':'仅完整两训练预算表列/整数固定项/资源普查；有界区间相交不保证共享可行，未产生候选或100图/性能结论。'}
    save(args.output/'summary.json',record)
    save(args.output/'run.json',{'inputs':inputs,'source_sha256':freeze['source_sha256'],'plan':freeze['plan'],'frozen_sha256':digest(args.frozen),
        'contract_sha256':digest(args.contract),'environment':{'python':sys.version,'platform':platform.platform(),'machine':platform.machine(),'numpy':np.__version__,
        'quality_shared_host':True},'cp_model_built':False,'cp_solver_called':False})
    print({k:record[k] for k in ('union_points','safe_rows_in_union','extra_cost_flag_variables','within_resource_gates')},flush=True)


if __name__=='__main__':main()
