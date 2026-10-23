"""93只辨别默认小N的共同work布局/角色分块交互，不恢复92资格。"""
from __future__ import annotations
import argparse
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import statistics as st
import subprocess
import sys
import time
import numpy as np
from PIL import Image
import psutil
from bench_p16_model_pair import checked
from study_p16_direct_compile import Library, digest, env, save
from suffix_cache_support import cache_info
from direct16_support import info as direct_info


def sha(array):
    return hashlib.sha256(memoryview(array).cast('B')).hexdigest()


def setup(plan):
    psutil.Process().cpu_affinity(plan['cpus'])
    directory = os.add_dll_directory('E:/mingw64/bin') if os.name == 'nt' else None
    libraries = {r: Library(checked(row), row['sha256']) for r, row in plan['libraries'].items()}
    assert libraries['reference'].revision == 87 and libraries['candidate'].revision == 92
    for lib in libraries.values():
        assert lib.capabilities & 2
    image = checked(plan['image'])
    with Image.open(image) as picture:
        source = np.array(picture, dtype=np.uint8)
    assert source.shape == (768, 1024, 3) and sha(source) == plan['source_sha256']
    backing = np.empty(source.nbytes + 128, np.uint8)
    aligned = (-backing.ctypes.data) & 63
    works = {offset: backing[aligned + offset:aligned + offset + source.nbytes].reshape(source.shape)
             for offset in plan['work_offsets']}
    assert works[0].ctypes.data % 64 == works[64].ctypes.data % 64 == 0
    assert works[64].ctypes.data - works[0].ctypes.data == 64
    # 两个work视图重叠，但只串行使用；每次源与目标独立且无重叠。
    assert not np.shares_memory(source, backing)
    kernel = ct.WinDLL('kernel32', use_last_error=True)
    cpu = kernel.GetCurrentProcessorNumber
    cpu.argtypes, cpu.restype = [], ct.c_uint32
    return libraries, source, works, backing, cpu, directory


def code_addresses(libraries):
    return {role: {'module_base': int(lib.dll._handle),
        'apply_function': int(ct.cast(lib.dll.jshc_cc_apply, ct.c_void_p).value),
        'apply_function_mod64': int(ct.cast(lib.dll.jshc_cc_apply, ct.c_void_p).value) % 64}
        for role, lib in libraries.items()}


def create_set(libraries, plan, order):
    models = [checked(row) for row in plan['model']['models']]
    sides = [checked(row) if row else None for row in plan['model']['sidecars']]
    handles, counts, snapshots = {}, {'reference': 0, 'candidate': 0}, []
    try:
        for letter in order:
            role = 'reference' if letter == 'A' else 'candidate'
            pair = counts[role]
            counts[role] += 1
            chain = libraries[role].chain(models, sides)  # 两库均调用默认create，绝不传hint。
            handles[role, pair] = chain
            cache, direct = cache_info(chain), direct_info(chain)
            assert chain.model_bytes == 1852824 and cache['enabled'] and not direct['enabled']
            snapshots.append({'role': role, 'pair': pair, 'handle': int(chain.handle.value),
                'handle_mod64': int(chain.handle.value) % 64, 'model_bytes': chain.model_bytes,
                'cache': cache, 'direct': direct, 'cache_pointer_available_by_public_ABI': False,
                'cache_table_mod64': None})
    except BaseException:
        for chain in handles.values():
            chain.close()
        raise
    assert set(handles) == {(r, i) for r in libraries for i in (0, 1)}
    return handles, snapshots


def chunk(chain, source, work, repeats, cpu, expected):
    apply_seconds = np.empty(repeats, np.float64)
    copy_seconds = np.empty(repeats, np.float64)
    error = ct.create_string_buffer(1024)
    u8 = ct.POINTER(ct.c_uint8)
    source_pointer, work_pointer = source.ctypes.data_as(u8), work.ctypes.data_as(u8)
    a, b = apply_seconds.ctypes.data_as(ct.POINTER(ct.c_double)), copy_seconds.ctypes.data_as(ct.POINTER(ct.c_double))
    work.fill(173)
    cpu_begin = int(cpu())
    started = time.perf_counter_ns()
    rc = chain.library.dll.jshc_cc_bench(chain.handle, source_pointer, work_pointer, source.nbytes,
        1, 1, repeats, a, b, error, len(error))
    ended = time.perf_counter_ns()
    cpu_end = int(cpu())
    assert rc == 0, error.value
    actual = sha(work)
    assert actual == expected
    return {'repeats': repeats, 'apply_seconds': apply_seconds.tolist(),
        'copy_apply_seconds': copy_seconds.tolist(), 'wall_begin_ns': started, 'wall_end_ns': ended,
        'wall_seconds': (ended - started) * 1e-9, 'caller_cpu_begin': cpu_begin,
        'caller_cpu_end': cpu_end, 'actual_output_sha256': actual}


def phase(plan, chains, pair, source, work, schedule, role_order, cpu):
    chunks = []
    # 两模式都18次C ABI调用，每role9块×7轮=63；只改变调用先后，不改变块边界。
    if schedule == 'blocked':
        calls = [(role, block) for role in role_order for block in range(9)]
    else:
        calls = [(role, block) for block in range(9)
                 for role in (role_order if block % 2 == 0 else list(reversed(role_order)))]
    for role, block in calls:
        result = chunk(chains[role, pair], source, work, 7, cpu, plan['expected_output_sha256'])
        result.update({'role': role, 'block': block})
        chunks.append(result)
    return chunks


def worker(args, plan):
    libraries, source, works, backing, cpu, directory = setup(plan)
    records, allocations = [], []
    for order in plan['construction_orders'][args.worker]:
        chains, snapshots = create_set(libraries, plan, order)
        allocations.append({'order': order, 'handles': snapshots})
        try:
            for pair in plan['pair_orders'][args.worker]:
                for offset in plan['offset_orders'][args.worker]:
                    work = works[offset]
                    for schedule in plan['schedule_orders'][args.worker]:
                        reverse = (args.worker + pair + offset // 64 + (order == 'BAAB') + (schedule == 'interleaved')) % 2
                        role_order = ['candidate', 'reference'] if reverse else ['reference', 'candidate']
                        warm = []
                        for role in role_order:
                            item = chunk(chains[role, pair], source, work, 2, cpu, plan['expected_output_sha256'])
                            item['role'] = role
                            warm.append(item)
                        measured = phase(plan, chains, pair, source, work, schedule, role_order, cpu)
                        control = phase(plan, chains, pair, source, work, schedule, role_order, cpu)
                        records.append({'construction': order, 'pair': pair, 'work_offset': offset,
                            'work_address': int(work.ctypes.data), 'work_mod64': int(work.ctypes.data) % 64,
                            'work_mod4096': int(work.ctypes.data) % 4096, 'schedule': schedule,
                            'role_order': role_order, 'warmup': warm, 'measured': measured, 'control': control})
                        save(args.output / f'worker{args.worker}-partial.json', {'records': records, 'allocations': allocations})
        finally:
            for chain in chains.values():
                chain.close()
    assert sha(source) == plan['source_sha256']
    save(args.output / f'worker{args.worker}.json', {'records': records, 'allocations': allocations,
        'source_address': int(source.ctypes.data), 'source_sha256': sha(source),
        'code_addresses': code_addresses(libraries), 'environment': env(),
        'scope': 'CPU仅记录每个C ABI块wall外端点；端点相同不证明内轮未迁移。公共ABI不公开cache指针，未控制或读取其地址。'})


def quality(args, plan):
    libraries, source, works, backing, cpu, directory = setup(plan)
    checks, allocations = [], []
    for order in ('ABBA', 'BAAB'):
        chains, snapshots = create_set(libraries, plan, order)
        allocations.append({'order': order, 'handles': snapshots})
        try:
            for pair in (0, 1):
                for offset, work in works.items():
                    for role in libraries:
                        result = chunk(chains[role, pair], source, work, 2, cpu, plan['expected_output_sha256'])
                        checks.append({'order': order, 'pair': pair, 'offset': offset, 'role': role,
                            'work_address': int(work.ctypes.data), 'work_mod64': int(work.ctypes.data) % 64,
                            'actual_output_sha256': result['actual_output_sha256']})
        finally:
            for chain in chains.values():
                chain.close()
    assert len(checks) == 16 and sha(source) == plan['source_sha256']
    save(args.output / 'quality.json', {'passed': True, 'actual_checks': checks, 'allocations': allocations,
        'code_addresses': code_addresses(libraries), 'source_sha256': sha(source),
        'environment': env(), 'scope': '仅短接口/同work指针/默认cached/完整首图输出资格；短内部计时不作速度结论。'})


def role_values(record, phase_name, role):
    values = [v for c in record[phase_name] if c['role'] == role for v in c['apply_seconds']]
    assert len(values) == 63
    return values


def summarize(plan, workers):
    cells = []
    for construction in ('ABBA', 'BAAB'):
        for pair in (0, 1):
            for offset in (0, 64):
                for schedule in ('blocked', 'interleaved'):
                    match = [next(r for r in w['records'] if (r['construction'], r['pair'], r['work_offset'], r['schedule'])
                        == (construction, pair, offset, schedule)) for w in workers]
                    values = {role: [st.median(role_values(r, 'measured', role)) for r in match] for role in ('reference', 'candidate')}
                    controls = [st.median(role_values(r, 'control', role)) / st.median(role_values(r, 'measured', role))
                        for r in match for role in ('reference', 'candidate')]
                    ratios = [a / b for a, b in zip(values['candidate'], values['reference'])]
                    valid = all(plan['control_min'] <= v <= plan['control_max'] for v in controls)
                    cells.append({'construction': construction, 'pair': pair, 'work_offset': offset, 'schedule': schedule,
                        'time_ratios': ratios, 'median_time_ratio': st.median(ratios), 'controls': controls,
                        'control_valid': valid, 'worst_throughput_retained': 1 / max(ratios),
                        'grades': {str(g): valid and 1 / max(ratios) >= g / 100 for g in plan['grades']},
                        'no_obvious_slowdown': valid and st.median(ratios) <= 1.05 and max(ratios) <= 1.10})
    interactions = []
    dimensions = {'schedule': ('blocked', 'interleaved'), 'work_offset': (0, 64), 'construction': ('ABBA', 'BAAB')}
    for dimension, levels in dimensions.items():
        for low in [c for c in cells if c[dimension] == levels[0]]:
            high = next(c for c in cells if c[dimension] == levels[1] and all(
                c[k] == low[k] for k in ('construction', 'pair', 'work_offset', 'schedule') if k != dimension))
            ratios = [a / b for a, b in zip(high['time_ratios'], low['time_ratios'])]
            valid = high['control_valid'] and low['control_valid']
            direction = ('increase' if st.median(ratios) >= 1.1 and sum(v >= 1.1 for v in ratios) >= 3
                else 'decrease' if st.median(ratios) <= .9 and sum(v <= .9 for v in ratios) >= 3 else 'unresolved')
            interactions.append({'dimension': dimension, 'fixed': {k: low[k] for k in
                ('construction', 'pair', 'work_offset', 'schedule') if k != dimension}, 'ratios': ratios,
                'median_ratio': st.median(ratios), 'control_valid': valid,
                'diagnostic_direction': direction if valid else 'invalid',
                'scope': '10%与3/4仅为原因辨别的预注册兴趣线，不是用户50底线，不声称频率/heap/ASLR因果。'})
    return {'cells': cells, 'interactions': interactions}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--worker', type=int)
    p.add_argument('--quality', action='store_true')
    a = p.parse_args()
    plan = json.loads(a.plan.read_text(encoding='utf-8'))
    assert digest(Path(__file__)) == plan['script_sha256']
    for row in plan['sources']:
        checked(row)
    if a.worker is not None:
        return worker(a, plan)
    if a.output.exists():
        raise FileExistsError('保留首次诊断，不覆盖或重选')
    a.output.mkdir(parents=True)
    save(a.output / 'executed-plan.json', plan)
    if a.quality:
        return quality(a, plan)
    checked(plan['quality_proof'])
    workers = []
    for i in range(4):
        subprocess.run([sys.executable, '-X', 'utf8', __file__, '--plan', str(a.plan),
            '--output', str(a.output), '--worker', str(i)], check=True)
        workers.append(json.loads((a.output / f'worker{i}.json').read_text(encoding='utf-8')))
        print('93原因辨别进程完成', i, flush=True)
    result = summarize(plan, workers)
    result.update({'worker_sha256': [digest(a.output / f'worker{i}.json') for i in range(4)],
        'scope': '独立N1默认路径原因辨别，保持92原有效80档/失效结果。无hint新阈值、无产品代码更改、无频率因果或92追授。'})
    save(a.output / 'results.json', result)


if __name__ == '__main__':
    main()
