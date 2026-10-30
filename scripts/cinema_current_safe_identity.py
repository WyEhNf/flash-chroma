"""当前122节点安全CP的纯整数身份与环境核验，不导入NumPy/Numba。"""
from __future__ import annotations
import hashlib
import importlib.metadata
import json
from pathlib import Path
from cinema_first_safe_cpsat_model import validate_safe_problem
ROOT=Path(__file__).resolve().parents[1]
SOLVE={'num_search_workers':1,'random_seed':20261024,'max_time_in_seconds':20.0}
GATE={'denominator':'best373a','uniform_mean_nonincrease':True,'uniform_p99_nonincrease':True,
      'training_mean_nonincrease':True,'training_p99_nonincrease':True,'global_max_squared_upper':43}


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def validate_current(problem):
    validate_safe_problem(problem)
    if problem['experiment']!='cinema_current741_safe_cap47_minl1_v1' or problem['initial_gate']!=GATE or problem['solve']!=SOLVE:
        raise ValueError('不是当前完整安全表冻结协议')
    if problem['n_node_variables']!=366 or len(problem['points'])!=4985 or len(problem['rows'])!=14955:
        raise ValueError('当前节点或危险表尺寸不符')
    if sum(len(p['allowed_deltas']) for p in problem['points'])!=386612:raise ValueError('未保留完整安全元组')
    for value in problem['variables'][:366]:
        old=value['original_value']
        if value['lower']!=max(-2,-old) or value['upper']!=min(2,255-old):raise ValueError('实际节点裁剪域不符')


def verify_frozen(problem):
    validate_current(problem)
    for name,expected in {**problem['source_sha256'],**problem['frozen_risk_sha256']}.items():
        if sha(ROOT/name)!=expected:raise ValueError('执行源或风险原件已变：'+name)
    for spec in problem['inputs'].values():
        if sha(spec['path'])!=spec['sha256']:raise ValueError('固定模型或数据已变')


def verify_lock(problem,path):
    if sha(path)!=problem['environment_lock_sha256']:raise ValueError('隔离环境锁已变')
    lock=json.loads(Path(path).read_text(encoding='utf-8'))
    for name,version in lock['packages'].items():
        if importlib.metadata.version(name)!=version:raise ValueError('依赖版本已变：'+name)
    if importlib.metadata.version('ortools')!='9.15.6755':raise ValueError('不是冻结ORTools版本')
    for name,expected in lock['installed_record_sha256'].items():
        dist=importlib.metadata.distribution(name);records=[v for v in dist.files or [] if str(v).endswith('.dist-info/RECORD')]
        if len(records)!=1 or sha(dist.locate_file(records[0]))!=expected:raise ValueError('依赖RECORD已变：'+name)


def process_peaks():
    import ctypes
    from ctypes import wintypes
    class Counters(ctypes.Structure):
        _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD),
            *[(name,ctypes.c_size_t) for name in ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage',
            'QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage')]]
    value=Counters();value.cb=ctypes.sizeof(value)
    kernel=ctypes.WinDLL('kernel32',use_last_error=True);kernel.GetCurrentProcess.restype=wintypes.HANDLE
    psapi=ctypes.WinDLL('psapi',use_last_error=True);psapi.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
    if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(),ctypes.byref(value),value.cb):raise ctypes.WinError(ctypes.get_last_error())
    return {'peak_working_set_bytes':int(value.PeakWorkingSetSize),'peak_pagefile_bytes':int(value.PeakPagefileUsage),
        'scope':'当前进程整个生存期Windows峰值，不是模型部署RAM。'}
