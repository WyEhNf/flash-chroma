"""当前完整安全首解模型的独立身份，复用已冻结Q16行审计。"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from cinema_first_cpsat_model import validate_problem
from cinema_current_safe_identity import GATE,sha,verify_lock,process_peaks
ROOT=Path(__file__).resolve().parents[1]
SOLVE={'num_search_workers':1,'random_seed':20261024,'max_time_in_seconds':60.0,'stop_after_first_solution':True}
MATH_FIELDS=('variables','n_node_variables','rows','points','initial_gate')


def constraint_signature(problem):
    raw=json.dumps({name:problem[name] for name in MATH_FIELDS},ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def validate_feasible(problem):
    validate_problem(problem)
    if problem['schema']!='cinema_current_feasible_problem_v1' or problem['experiment']!='cinema_current741_cap47_feasible_v1':raise ValueError('不是当前安全首解问题')
    if problem['solve']!=SOLVE or problem['initial_gate']!=GATE or 'objective' in problem or 'objective_absolute_upper_bound' in problem:raise ValueError('目标/首解参数/公共初门已变')
    if problem['n_node_variables']!=366 or len(problem['variables'])!=15321 or len(problem['points'])!=4985 or len(problem['rows'])!=14955:raise ValueError('完整首解模型尺寸不符')
    if sum(len(p['allowed_deltas']) for p in problem['points'])!=386612:raise ValueError('安全表不完整')
    if constraint_signature(problem)!=problem['constraint_sha256']:raise ValueError('完整整数约束签名不同')


def verify_frozen(problem):
    validate_feasible(problem)
    for name,expected in {**problem['source_sha256'],**problem['frozen_risk_sha256']}.items():
        if sha(ROOT/name)!=expected:raise ValueError('首解冻结源/数据已变：'+name)
    for spec in problem['inputs'].values():
        if sha(spec['path'])!=spec['sha256']:raise ValueError('原模型或数据已变')
