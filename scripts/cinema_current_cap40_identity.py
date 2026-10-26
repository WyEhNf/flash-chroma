"""273节点±1 cap40首解的纯整数身份，隔离环境不导入NumPy。"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from cinema_first_cpsat_model import validate_problem
from cinema_current_safe_identity import sha,verify_lock,process_peaks
ROOT=Path(__file__).resolve().parents[1]
SOLVE={'num_search_workers':1,'random_seed':20261024,'max_time_in_seconds':60.0,'stop_after_first_solution':True}
GATE={'denominator':'best373a','uniform_mean_nonincrease':True,'uniform_p99_nonincrease':True,
      'training_mean_nonincrease':True,'training_p99_nonincrease':True,'global_max_squared_upper':40}


def signature(problem):
    keys=('variables','n_node_variables','rows','points','initial_gate')
    return hashlib.sha256(json.dumps({k:problem[k] for k in keys},ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()


def validate(problem):
    validate_problem(problem)
    if problem['schema']!='cinema_current_cap40_feasible_v1' or problem['solve']!=SOLVE or problem['initial_gate']!=GATE:raise ValueError('不是固定cap40首解协议')
    if any(k in problem for k in ('objective','objective_absolute_upper_bound','hint')):raise ValueError('禁止目标/abs/hint')
    if (problem['n_node_variables'],len(problem['variables']),len(problem['points']),len(problem['rows']))!=(819,12993,4058,12174):raise ValueError('完整整数问题尺寸不符')
    if sum(len(p['allowed_deltas']) for p in problem['points'])!=74081:raise ValueError('完整安全表不符')
    for i,v in enumerate(problem['variables'][:819]):
        if v['lower']!=max(-1,-v['original_value']) or v['upper']!=min(1,255-v['original_value']) or v['channel']!=i%3:raise ValueError('真实节点±1/clip域不符')
    for i,point in enumerate(problem['points']):
        if point['z_indices']!=list(range(819+3*i,822+3*i)):raise ValueError('稳定输入/输出映射不同')
    if signature(problem)!=problem['constraint_sha256']:raise ValueError('数学签名已变')


def verify(problem):
    validate(problem)
    for name,expected in problem['source_sha256'].items():
        if sha(ROOT/name)!=expected:raise ValueError('冻结源已变：'+name)
    for name,expected in problem['inputs_sha256'].items():
        if sha(name)!=expected:raise ValueError('冻结输入已变：'+name)
