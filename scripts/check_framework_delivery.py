"""串行复核交付程序的原框架计时；不替换原参考、计时或色差函数。"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import statistics
import subprocess
import time

try:
    import psutil
except ImportError:
    psutil = None


ROW = re.compile(r'^\s*Img:\s*(.*?)\s+TimeCost:\s*(\S+),\s*Delta:\s*(\S+)\s+(\S+)\s*$')


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write_new(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def parse_config(value):
    parts = value.split(',')
    if len(parts) != 6:
        raise ValueError('config格式必须是id,m,mode,backend,grid,fit')
    name, size, mode, backend, grid, fit = parts
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', name):
        raise ValueError('配置id只允许ASCII字母、数字、横线和下划线')
    if not re.fullmatch(r'[0-9]+', size) or not 17 <= int(size) <= 33:
        raise ValueError('每个配置的统一m必须在17..33内')
    if mode not in ('auto', 'sparse', 'direct_u8', 'direct_u16', 'direct_rgb24'):
        raise ValueError('未知表示模式')
    if backend not in ('auto', 'scalar', 'avx2') or grid not in ('uniform', 'framework'):
        raise ValueError('未知后端或网格')
    if fit not in ('sample', 'independent_ls', 'chain_ls', 'history'):
        raise ValueError('fit必须是sample、independent_ls、chain_ls或history')
    return dict(id=name, m=int(size), mode=mode, backend=backend, grid=grid, fit=fit)


def parse_output(text, count):
    """原程序只打印六位小数；这里保留其精度，不臆造更精细的数值。"""
    rows = []
    for line in text.splitlines():
        if not line.lstrip().startswith('Img:'):
            continue
        match = ROW.fullmatch(line)
        if not match:
            raise ValueError('无法解析原框架Img行：' + line)
        path, elapsed, original_delta, candidate_delta = match.groups()
        values = [float(elapsed), float(original_delta), float(candidate_delta)]
        if not all(math.isfinite(value) and value >= 0 for value in values):
            raise ValueError('计时和色差必须为有限非负数')
        basename = path.replace('\\', '/').rsplit('/', 1)[-1]
        expected = f'{len(rows) + 1}.bin'
        if basename != expected:
            raise ValueError('图片身份或顺序不符：' + basename + '，预期' + expected)
        rows.append({'image': len(rows) + 1, 'path': path, 'time_ms': values[0] * 1000,
                     'reference_delta': values[1], 'candidate_delta': values[2]})
    if len(rows) != count:
        raise ValueError(f'原框架成功图片数{len(rows)}，要求{count}')
    return rows


def file_identities(paths):
    return [{'path': str(path), 'bytes': path.stat().st_size, 'sha256': digest(path)} for path in paths]


def summarize_threads(history):
    entries = sorted(history.values(), key=lambda row: (-row['max_total_cpu_seconds'], row['id']))
    dominant = entries[0]['id'] if entries else None
    others = [row for row in entries if row['id'] != dominant]
    return {'threads': entries, 'observed_distinct_thread_count': len(entries),
            'threads_with_observed_cpu': sum(row['max_total_cpu_seconds'] > 0 for row in entries),
            'dominant_cpu_thread_id': dominant,
            'additional_threads_with_observed_cpu': sum(row['max_total_cpu_seconds'] > 0 for row in others),
            'additional_threads_observed_cpu_seconds': sum(row['max_total_cpu_seconds'] for row in others),
            'scope': 'CPU为每TID观测到的累计最大值；dominant只指观测CPU最多线程，不将其余线程擅自归因为系统线程。0.1秒采样可漏过短命线程及最后一次采样后的CPU；非算法并行的单独证明。'}


def launch(executable, data, config, count, affinity, log_dir, prefix):
    # 相邻的data用相对路径，避免MinGW窄字符argv中的中文绝对路径问题。
    data_arg = os.path.relpath(data, executable.parent)
    command = [str(executable), data_arg, str(config['m']), config['mode'], config['backend'],
               config['grid'], str(count), config['fit']]
    stdout_path, stderr_path = log_dir / f'{prefix}.stdout.log', log_dir / f'{prefix}.stderr.log'
    history, samples, peak_rss, max_threads = {}, 0, 0, 0
    observed_affinity, monitoring_error, code = None, None, None
    started_utc = datetime.now(timezone.utc).isoformat()
    started = time.perf_counter()
    with stdout_path.open('xb') as stdout, stderr_path.open('xb') as stderr:
        process = subprocess.Popen(command, cwd=executable.parent, stdout=stdout, stderr=stderr)
        observer = psutil.Process(process.pid)
        try:
            # 启动后立即绑核；原框架LUT读取/预处理在正式计时之前。
            observer.cpu_affinity([affinity])
            observed_affinity = observer.cpu_affinity()
            if observed_affinity != [affinity]:
                raise RuntimeError('显式绑核未生效')
            while process.poll() is None:
                try:
                    if observer.cpu_affinity() != [affinity]:
                        raise RuntimeError('进程绑核在运行期间改变')
                    peak_rss = max(peak_rss, observer.memory_info().rss)
                    max_threads = max(max_threads, observer.num_threads())
                    for thread in observer.threads():
                        row = history.setdefault(thread.id, {'id': thread.id, 'max_user_seconds': 0.0,
                                                            'max_system_seconds': 0.0, 'max_total_cpu_seconds': 0.0})
                        row['max_user_seconds'] = max(row['max_user_seconds'], thread.user_time)
                        row['max_system_seconds'] = max(row['max_system_seconds'], thread.system_time)
                        row['max_total_cpu_seconds'] = max(row['max_total_cpu_seconds'], thread.user_time + thread.system_time)
                    samples += 1
                except psutil.NoSuchProcess:
                    if process.poll() is None:
                        raise
                    break
                time.sleep(0.1)
            code = process.wait()
        except Exception as error:
            monitoring_error = str(error)
            if process.poll() is None:
                process.terminate()
            code = process.wait()
        child_wall_ms = (time.perf_counter() - started) * 1000
    record = {'config': config['id'], 'command': command, 'cwd': str(executable.parent),
              'pid': process.pid, 'started_utc': started_utc, 'returncode': code,
              'child_wall_ms': child_wall_ms, 'stdout': stdout_path.name, 'stderr': stderr_path.name,
              'stdout_sha256': digest(stdout_path), 'stderr_sha256': digest(stderr_path),
              'affinity': observed_affinity, 'peak_rss_observed_bytes': peak_rss,
              'max_threads_observed': max_threads, 'observation_samples': samples,
              'thread_observation': summarize_threads(history), 'passed': False}
    if monitoring_error:
        record['error'] = '进程观测失败：' + monitoring_error
    elif code != 0:
        record['error'] = f'原框架非零退出：{code}'
    else:
        try:
            record['images'] = parse_output(stdout_path.read_text(encoding='utf-8', errors='replace'), count)
            record['batch_ms'] = sum(row['time_ms'] for row in record['images'])
            record['passed'] = True
        except (ValueError, OverflowError) as error:
            record['error'] = str(error)
    write_new(log_dir / f'{prefix}.json', record)
    return record


def summarize_config(config, runs, repetitions, count):
    selected = [run for run in runs if run['config'] == config['id'] and run['passed']]
    complete = len(selected) == repetitions
    rows = []
    for index in range(count):
        values = [run['images'][index] for run in selected]
        times = [row['time_ms'] for row in values]
        deltas = [row['candidate_delta'] for row in values]
        references = [row['reference_delta'] for row in values]
        rows.append({'image': index + 1, 'time_samples_ms': times,
                     'time_median_ms': statistics.median(times) if times else None,
                     'candidate_delta_samples': deltas, 'reference_delta_samples': references,
                     'delta_consistent': bool(values) and len(set(deltas)) == len(set(references)) == 1})
    batches = [run['batch_ms'] for run in selected]
    return {'config': config, 'complete': complete, 'delta_consistent': all(row['delta_consistent'] for row in rows),
            'batch_samples_ms': batches, 'batch_median_ms': statistics.median(batches) if batches else None,
            'batch_min_ms': min(batches) if batches else None, 'batch_max_ms': max(batches) if batches else None,
            'images': rows}


def run(args):
    if psutil is None:
        raise RuntimeError('运行进程观测需要psutil；仅解析结果和单元测试不需要此可选依赖')
    executable, data, output = args.exe.resolve(), args.data.resolve(), args.output.resolve()
    if output.exists():
        raise FileExistsError('输出已存在，拒绝覆盖')
    if not 1 <= args.count <= 100 or args.reps < 1 or args.affinity < 0:
        raise ValueError('count必须为1..100，reps必须为正数，affinity必须非负')
    if args.affinity not in psutil.Process().cpu_affinity():
        raise ValueError('要求的CPU不在当前可用亲和性列表内')
    configs = [parse_config(value) for value in args.config]
    if len({row['id'] for row in configs}) != len(configs):
        raise ValueError('配置id重复')
    paths = [executable, executable.parent / 'main.cpp', executable.parent / 'flash_chroma_framework.hpp',
             executable.parent / 'run.ps1', Path(__file__).resolve()]
    paths += [data / 'LUT' / f'Test{i}.3DL' for i in range(1, 5)]
    paths += [data / 'image' / f'{i}.bin' for i in range(1, args.count + 1)]
    if not all(path.is_file() for path in paths):
        raise FileNotFoundError('必须提供完整exe/main/hpp/run.ps1及LUT/image数据')
    for path in paths[-args.count:]:
        if path.stat().st_size != 1024 * 768 * 3:
            raise ValueError('输入图片必须为1024x768 RGB8 raw：' + str(path))
    output.mkdir(parents=True)
    log_dir = output / 'runs'
    log_dir.mkdir()
    before = file_identities(paths)
    orders, rng = [], random.Random(args.seed)
    for _ in range(args.reps):
        order = [config['id'] for config in configs]
        rng.shuffle(order)
        orders.append(order)
    execution = {'schema': 'framework_delivery_check_v1', 'sources_before': before,
                 'configs': configs, 'count': args.count, 'repetitions': args.reps, 'seed': args.seed,
                 'affinity': args.affinity, 'randomized_orders': orders, 'psutil_version': psutil.__version__,
                 'timing_scope': '原main的TimeCost，包含输出申请；每配置每重复独立进程，参考/色差保留在原图间调用位置。无额外warmup，不是A/A稳定性结论。',
                 'fit_uses_images': False, 'official_score_available': False}
    write_new(output / 'execution.json', execution)
    runs, failure = [], None
    by_id = {config['id']: config for config in configs}
    try:
        for round_index, order in enumerate(orders, 1):
            for ordinal, name in enumerate(order, 1):
                record = launch(executable, data, by_id[name], args.count, args.affinity,
                                log_dir, f'r{round_index:02d}-{ordinal:02d}-{name}')
                record['round'] = round_index
                runs.append(record)
                if not record['passed']:
                    raise RuntimeError(record['error'])
    except Exception as error:
        failure = str(error)
    try:
        after = file_identities(paths)
        unchanged = before == after
    except Exception as error:
        after, unchanged = [], False
        failure = failure or '结束来源复核失败：' + str(error)
    summaries = [summarize_config(config, runs, args.reps, args.count) for config in configs]
    passed = not failure and unchanged and all(row['complete'] and row['delta_consistent'] for row in summaries)
    result = {'schema': 'framework_delivery_check_v1', 'passed': passed, 'error': failure,
              'sources_unchanged': unchanged, 'sources_after': after, 'configurations': summaries,
              'runs': runs, 'aa_stability_evaluated': False, 'official_score_available': False,
              'scope': '当前机器与所选图片上的原框架确认；辅助线程CPU是进程观测，算法单线程还须结合禁OpenMP构建和源码。统计范围不含离线LUT准备；child_wall_ms仅进程总墙钟，不作性能排名。'}
    write_new(output / 'summary.json', result)
    return {'passed': passed, 'summary': str(output / 'summary.json'), 'runs': len(runs),
            'sources_unchanged': unchanged, 'error': failure}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', type=Path, required=True)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--count', type=int, default=4)
    parser.add_argument('--reps', type=int, default=5)
    parser.add_argument('--affinity', type=int, default=16)
    parser.add_argument('--seed', type=int, default=20261029)
    parser.add_argument('--config', action='append', required=True)
    try:
        result = run(parser.parse_args(argv))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['passed'] else 1
    except Exception as error:
        print(json.dumps({'passed': False, 'error': str(error)}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
