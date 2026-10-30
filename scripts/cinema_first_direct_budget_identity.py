"""隔离CP进程只读核源、证据、版本身份并记录Windows峰工作集。"""
from __future__ import annotations
import ctypes
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path


def sha(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify_identity(problem, environment_lock):
    root = Path(__file__).resolve().parents[1]
    if problem['solve'] != {'num_search_workers': 1, 'random_seed': 20261024, 'max_time_in_seconds': 20.0}:
        raise ValueError('不是冻结的唯一单worker/seed/20秒参数')
    if problem['objective'] != 'none' or problem['hint'] != 'none': raise ValueError('本次仅可行性，无目标或hint')
    for name, expected in {**problem['source_sha256'], **problem['frozen_evidence_sha256']}.items():
        if sha(root/name) != expected: raise ValueError('实际源或成本证据已变：'+name)
    for spec in [*problem['inputs'].values(), problem['witness']]:
        if sha(spec['path']) != spec['sha256']: raise ValueError('固定原模型、数据或窄域见证已变')
    if sha(environment_lock) != problem['environment_lock_sha256']: raise ValueError('隔离环境锁已变')
    lock = json.loads(Path(environment_lock).read_text(encoding='utf-8'))
    if lock['packages']['ortools'] != '9.15.6755': raise ValueError('错误ORTools锁版本')
    for name, version in lock['packages'].items():
        if importlib.metadata.version(name) != version: raise ValueError('隔离依赖版本已变：'+name)
    for name, expected in lock['installed_record_sha256'].items():
        distribution = importlib.metadata.distribution(name)
        records = [v for v in distribution.files or [] if str(v).endswith('.dist-info/RECORD')]
        if len(records) != 1 or sha(distribution.locate_file(records[0])) != expected:
            raise ValueError('隔离依赖RECORD已变：'+name)


def process_memory():
    if os.name != 'nt': return {'supported': False, 'scope': '本阶段峰工作集读取只实现Windows'}
    size = ctypes.c_size_t
    class Counters(ctypes.Structure):
        _fields_ = [('cb', ctypes.c_ulong), ('PageFaultCount', ctypes.c_ulong),
            ('PeakWorkingSetSize', size), ('WorkingSetSize', size), ('QuotaPeakPagedPoolUsage', size),
            ('QuotaPagedPoolUsage', size), ('QuotaPeakNonPagedPoolUsage', size), ('QuotaNonPagedPoolUsage', size),
            ('PagefileUsage', size), ('PeakPagefileUsage', size)]
    kernel = ctypes.WinDLL('kernel32', use_last_error=True); psapi = ctypes.WinDLL('psapi', use_last_error=True)
    kernel.GetCurrentProcess.restype = ctypes.c_void_p
    psapi.GetProcessMemoryInfo.argtypes = (ctypes.c_void_p, ctypes.POINTER(Counters), ctypes.c_ulong)
    psapi.GetProcessMemoryInfo.restype = ctypes.c_int
    values = Counters(); values.cb = ctypes.sizeof(values)
    if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(values), values.cb):
        raise OSError(ctypes.get_last_error(), '读取CP进程工作集失败')
    return {'supported': True, 'peak_working_set_bytes': int(values.PeakWorkingSetSize),
        'working_set_bytes': int(values.WorkingSetSize), 'peak_pagefile_usage_bytes': int(values.PeakPagefileUsage),
        'scope': '当前CP Python进程自启动累计峰工作集，含JSON解析/模型/solver；不是部署LUT RAM或纯CP单项内存。'}
