"""289八角色同场正式性能；只在质量通过及明确排他窗口后执行。"""
from __future__ import annotations
import argparse
import ctypes as ct
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
from contextlib import ExitStack
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'python'), str(ROOT / 'experiments/channel-runtime')]
import numpy as np
import psutil
from channel_native import Library
from run_channel_tail_nodes import digest, save
from run_velvia_bubble_perf import bench, array_sha
from run_direct_u16_ilp_perf import definitions as old_definitions, dataset
from check_direct_u16_ilp_native import info as info288
from check_direct_u10_native import info as info289
from direct16_support import info as direct_info
from lutlab import study_provenance
PLAN = ROOT / 'experiments/p16-direct-u10-perf-v1.json'


def definitions(cache, frozen):
    previous = old_definitions(cache, frozen)
    specs = frozen['models']
    return {'87a399': previous['87a399'], '87old': previous['87old'], '288old': previous['288old'],
        '289old': (289, specs['old_best']), '288max': previous['288max'], '288p99': previous['288p99'],
        '289max': (289, specs['max_first']), '289p99': (289, specs['p99_first'])}


def identities(plan):
    for path, expected in plan['source_sha256'].items():
        if digest(ROOT / path) != expected:
            raise ValueError('正式冻结源码改变：' + path)
    frozen = json.loads((ROOT / plan['quality_frozen']).read_text(encoding='utf-8'))
    if digest(ROOT / plan['quality_frozen']) != plan['quality_frozen_sha256']:
        raise ValueError('质量冻结清单改变')
    quality = json.loads((ROOT / plan['quality_result']).read_text(encoding='utf-8'))
    if digest(ROOT / plan['quality_result']) != plan['quality_result_sha256'] or not quality['passed']:
        raise ValueError('必须保持全部质量通过')
    for path, expected in frozen['files_sha256'].items():
        if digest(path) != expected:
            raise ValueError('已有质量来源改变：' + path)
    return frozen


def worker(args, plan):
    frozen = identities(plan)
    psutil.Process().cpu_affinity(plan['allowed_logical_cpus'])
    if sorted(psutil.Process().cpu_affinity()) != plan['allowed_logical_cpus']:
        raise ValueError('进程允许CPU集合不同')
    folder = args.output / ('worker' + str(args.worker))
    folder.mkdir()
    models = definitions(args.cache_root, frozen)
    source, expected = dataset(args.cache_root, models, frozen)
    source_sha = array_sha(source)
    dirs = [os.add_dll_directory('E:/mingw64/bin'),
            os.add_dll_directory(str(Path(frozen['library']).parent)),
            os.add_dll_directory(str(Path(frozen['frozen_288_library']).parent))]
    libraries = {87: Library(frozen['frozen_87_library'], frozen['frozen_87_sha256']),
        288: Library(frozen['frozen_288_library'], frozen['frozen_288_sha256']),
        289: Library(frozen['library'], frozen['library_sha256'])}
    cpu = ct.WinDLL('kernel32', use_last_error=True).GetCurrentProcessorNumber
    cpu.argtypes = []
    cpu.restype = ct.c_uint32
    record = {'worker': args.worker, 'environment': study_provenance.environment_fingerprint(),
        'allowed_logical_cpus': psutil.Process().cpu_affinity(), 'thread_pinning': False,
        'expected_output_sha256': expected, 'source_sha256': source_sha, 'groups': [], 'prepare': [],
        'models': models, 'plan_sha256': digest(PLAN), 'driver_sha256': digest(Path(__file__))}
    with ExitStack() as stack:
        work = np.empty_like(source)
        chains = {}
        for role in plan['roles']:
            revision, spec = models[role]
            for name, sha in spec['input_sha256'].items():
                if digest(name) != sha:
                    raise ValueError('模型改变')
            start = time.perf_counter()
            chain = stack.enter_context(libraries[revision].chain(spec['models'], spec['sidecars']))
            create = time.perf_counter() - start
            chains[role] = chain
            first = bench(chain, source, work, 'inplace', 4, 1)
            if array_sha(work) != expected[role] or array_sha(source) != source_sha:
                raise AssertionError('首次百图输出或源SHA错误')
            diagnostic = info289(chain) if revision == 289 else info288(chain) if revision == 288 else None
            record['prepare'].append({'role': role, 'construction_seconds': create,
                'cold_first_seconds': first,
                'construction_plus_first_copy_apply_seconds': create + first['copy_apply_seconds'][0],
                'output_sha256': array_sha(work), 'model_bytes': chain.model_bytes,
                'direct': direct_info(chain), 'wide': diagnostic})
            save(folder / 'results.json', record)
        scenes = [(path, threads) for path in plan['paths'] for threads in plan['threads']]
        if args.worker % 2:
            scenes.reverse()
        for path, threads in scenes:
            for label in plan['group_order']:
                role, phase = label[:-1], label[-1]
                chain = chains[role]
                bench(chain, source, work, path, threads, plan['warmup_per_group'])
                cpu_before = int(cpu())
                values = bench(chain, source, work, path, threads, plan['repeats_per_group'])
                cpu_after = int(cpu())
                output_sha = array_sha(work)
                if output_sha != expected[role] or array_sha(source) != source_sha:
                    raise AssertionError('组末输出或源SHA错误')
                record['groups'].append({'role': role, 'phase': phase, 'path': path, 'threads': threads,
                    'seconds': values, 'medians': {name: statistics.median(v) for name, v in values.items()},
                    'output_sha256': output_sha, 'source_readonly': True,
                    'main_cpu_before': cpu_before, 'main_cpu_after': cpu_after})
                save(folder / 'results.json', record)
    identities(plan)
    print(json.dumps({'worker': args.worker, 'groups': len(record['groups']), 'all_sha_passed': True}), flush=True)


def summarize(records, plan):
    aa, ratios = [], []
    lo, hi = plan['AA_time_ratio_bounds']
    for record in records:
        for path, threads in [(p, t) for p in plan['paths'] for t in plan['threads']]:
            rows = {(r['role'], r['phase']): r for r in record['groups'] if (r['path'], r['threads']) == (path, threads)}
            valid = {}
            for role in plan['roles']:
                valid[role] = True
                for metric in rows[role, 'A']['medians']:
                    ratio = rows[role, 'B']['medians'][metric] / rows[role, 'A']['medians'][metric]
                    passed = lo <= ratio <= hi
                    valid[role] &= passed
                    aa.append({'worker': record['worker'], 'path': path, 'threads': threads, 'role': role,
                        'metric': metric, 'B_over_A': ratio, 'pass': passed})
            for left, right in plan['comparisons']:
                for phase in ('A', 'B'):
                    for metric in rows[left, phase]['medians']:
                        ratio = rows[right, phase]['medians'][metric] / rows[left, phase]['medians'][metric]
                        ratios.append({'worker': record['worker'], 'path': path, 'threads': threads,
                            'phase': phase, 'comparison': right + '/' + left, 'metric': metric,
                            'time_ratio': ratio, 'throughput_retention': 1 / ratio,
                            'AA_valid': bool(valid[left] and valid[right])})
    result = {'AA': aa, 'comparisons': ratios, 'AA_all_passed': all(r['pass'] for r in aa), 'pairs': {}}
    for left, right in plan['comparisons']:
        name = right + '/' + left
        all_rows = [r for r in ratios if r['comparison'] == name]
        rows = [r for r in all_rows if r['AA_valid']]
        worst = min((r['throughput_retention'] for r in rows), default=None)
        result['pairs'][name] = {'valid_rows': len(rows),
            'worst': min(rows, key=lambda r: r['throughput_retention']) if rows else None,
            'minimum_valid_throughput_retention': worst,
            'tiers': {str(t): worst is not None and worst >= t / 100 for t in (100, 90, 80, 70, 60, 50)},
            'no_obvious_degradation': bool(worst is not None and worst >= 1 / plan['no_obvious_time_ratio_cap']),
            'rejected_by_valid_below_50': bool(worst is not None and worst < .5),
            'all_AA_passed_for_pair': all(r['AA_valid'] for r in all_rows)}
    result['candidate_gates'] = {}
    for role in ('289max', '289p99'):
        names = [role + '/' + base for base in ('87a399', '87old', '288old')]
        result['candidate_gates'][role] = {
            'hard50': all(result['pairs'][n]['tiers']['50'] and result['pairs'][n]['all_AA_passed_for_pair'] for n in names),
            'rejected_by_valid_below_50': any(result['pairs'][n]['rejected_by_valid_below_50'] for n in names)}
    result['scope'] = '四worker全部相位与AA保留；进程允许0/2/4/6不是每OMP TID绑定；首批无AA仅描述，不重跑择样、不升级默认。'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--worker', type=int)
    args = parser.parse_args()
    plan = json.loads(PLAN.read_text(encoding='utf-8'))
    if args.worker is not None:
        return worker(args, plan)
    identities(plan)
    if args.output.exists():
        raise ValueError('不覆盖正式性能')
    args.output.mkdir(parents=True)
    save(args.output / 'identity.json', {'plan': plan, 'plan_sha256': digest(PLAN),
        'driver_sha256': digest(Path(__file__)), 'environment': study_provenance.environment_fingerprint()})
    for index in range(plan['workers']):
        subprocess.run([sys.executable, str(Path(__file__)), '--cache-root', str(args.cache_root),
                        '--output', str(args.output), '--worker', str(index)], check=True, cwd=ROOT)
    records = [json.loads((args.output / ('worker' + str(n)) / 'results.json').read_text(encoding='utf-8'))
               for n in range(plan['workers'])]
    result = summarize(records, plan)
    save(args.output / 'results.json', result)
    print(json.dumps({'AA_all_passed': result['AA_all_passed'], 'candidate_gates': result['candidate_gates'],
        'pairs': result['pairs']}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
