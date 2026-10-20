"""同模型、同机、固定CPU集合的四进程平衡性能比较；AMD与最终服务器结果分别保存。"""
from __future__ import annotations
import argparse
import hashlib
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
import numpy as np
from PIL import Image
import psutil
from skylake_support import ROOT, build_libraries, checked, claim, digest, environment, read, save, unchanged
from suffix_cache_support import cache_info
from delta16_support import layouts
from axis_preweight_support import formats as axis_formats
from restrict_support import info as domain_info
from cache_encoding_support import info as encoding_info


def worker(args, policy):
    # 在载入OpenMP库和创建工作线程前约束进程，不修改机器的全局亲和性。
    requested = policy['affinity_cpus']; process = psutil.Process()
    allowed = process.cpu_affinity()
    if not set(requested) <= set(allowed):
        raise ValueError('冻结CPU集合超出当前进程允许范围')
    process.cpu_affinity(requested)
    if sorted(process.cpu_affinity()) != sorted(requested):
        raise ValueError('设置后实际CPU亲和性不符')
    plan, build, libraries, loaded = build_libraries(checked(policy['plan']), Path(policy['build_path']))
    if checked(policy['build']).resolve() != (Path(policy['build_path'])/'build.json').resolve():
        raise ValueError('策略中构建身份与目录不一致')
    checked(policy['topology'])
    full_path = checked(policy['full_acceptance']); full = read(full_path)
    if (not full['pass'] or full['libraries'] != build['libraries']
            or full['build_sha256'] != digest(Path(policy['build_path'])/'build.json')
            or full['cube']['byte_mismatches'] or full['photos']['byte_mismatches']):
        raise ValueError('同模型完整整数等价尚未通过')
    rows = read(checked(plan['fixed_inputs']['manifest']))['images']
    if len(rows) != 100:
        raise ValueError('需要冻结100图')
    images = []
    for row in rows:
        with Image.open(checked(row['evaluation'])) as image:
            if image.mode != 'RGB' or image.size != (1024, 768):
                raise ValueError('图片输入契约不符')
            images.append(np.asarray(image).reshape(-1, 3).copy())
    source = np.concatenate(images); del images
    if source.nbytes != 235929600:
        raise ValueError('100图源字节数不同')
    source_sha = hashlib.sha256(source.tobytes()).hexdigest()
    models = [checked(plan['fixed_inputs']['base']), *[checked(p) for p in plan['suffix_models']]]
    sides = [checked(plan['fixed_inputs']['sidecar']), None, None, None]
    order = policy['orders'][args.worker_index]; thread_order = policy['thread_orders'][args.worker_index]
    records = []
    for threads in thread_order:
        for name in order:
            lib = libraries[name]
            started = time.perf_counter(); chain = lib.chain(models, sides)
            prepare_seconds = time.perf_counter()-started
            with chain:
                info = cache_info(chain)
                coordinate_layouts = layouts(chain)
                shared_axis_formats = axis_formats(chain)
                read_domains = domain_info(chain)
                cache_encoding = encoding_info(chain)
                if name=='candidate' and 'compact_cache_policy' in plan and (cache_encoding is None or cache_encoding['format']!=1):
                    raise ValueError('实际计时模型未使用冻结的可逆半字编码')
                if name == 'candidate' and 'restrict_policy' in plan and read_domains is None:
                    raise ValueError('计时模型缺少读取域保护诊断')
                if name == 'candidate' and 'axis_preweight_policy' in plan and shared_axis_formats != plan['axis_preweight_policy']['actual_chain_formats']:
                    raise ValueError('计时模型未使用冻结的共享轴预计算格式')
                if name == 'candidate' and 'delta16_policy' in plan and coordinate_layouts != plan['delta16_policy']['actual_chain_layouts']:
                    raise ValueError('计时模型未使用冻结的坐标差布局')
                if name == 'candidate' and 'cache_policy' in plan and (not info or not info['enabled']):
                    raise ValueError('实际计时未启用冻结缓存候选')
                actual = chain.apply(source.copy(), kernel='avx2', threads=threads)
                actual_sha = hashlib.sha256(actual.tobytes()).hexdigest(); del actual
                if actual_sha != full['photos']['output_sha256'][name]:
                    raise AssertionError('计时前完整100图输出不同')
                freq = psutil.cpu_freq()
                start = {'affinity': process.cpu_affinity(), 'frequency_reported_mhz': None if freq is None else freq.current}
                measured = chain.bench(source, kernel='avx2', threads=threads, repeats=policy['repeats'])
                if any(a <= 0 or b < a for a, b in zip(measured['apply_seconds'], measured['copy_apply_seconds'])):
                    raise ValueError('原生回执计时非法')
                records.append({'variant': name, 'requested_threads': threads, 'kernel': 'avx2', 'stages': 4,
                    'images': 100, 'library_sha256': lib.sha256, 'library_revision': lib.revision,
                    'warmup_output_sha256': actual_sha, 'model_accounting_bytes': chain.model_bytes,
                    'prepare_wall_seconds': prepare_seconds, 'suffix_cache_info': info,
                    'coordinate_layouts': coordinate_layouts,
                    'shared_axis_formats': shared_axis_formats,
                    'model_read_domains': read_domains,
                    'cache_encoding': cache_encoding,
                    'prepare_plus_first_100_apply_seconds': prepare_seconds+measured['apply_seconds'][0],
                    'prepare_plus_first_100_copy_apply_seconds': prepare_seconds+measured['copy_apply_seconds'][0],
                    'serialized_input_bytes': sum(p.stat().st_size for p in models)+sum(p.stat().st_size for p in sides if p),
                    'start_state': start, 'end_affinity': process.cpu_affinity(), **measured})
    if hashlib.sha256(source.tobytes()).hexdigest() != source_sha:
        raise AssertionError('只读源图片被基准修改')
    return {'worker_index': args.worker_index, 'pid': os.getpid(), 'order': order, 'thread_order': thread_order,
        'environment': environment(), 'initial_allowed_cpus': allowed, 'actual_affinity': process.cpu_affinity(),
        'source_sha256': source_sha, 'source_bytes': source.nbytes, 'loaded_libraries': loaded,
        'libraries': build['libraries'], 'build_sha256': digest(Path(policy['build_path'])/'build.json'),
        'full_acceptance_sha256': digest(full_path), 'records': records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--policy', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--worker-index', type=int)
    args = parser.parse_args(); policy = read(args.policy)
    if args.worker_index is not None:
        result = worker(args, policy); save(args.output, result)
        print('完成性能进程：', args.worker_index, flush=True)
        return
    if (policy['repeats'] != 5 or len(policy['orders']) != 4 or len(policy['thread_orders']) != 4
            or policy['orders'] != [['reference', 'candidate'], ['candidate', 'reference'],
                                    ['candidate', 'reference'], ['reference', 'candidate']]):
        raise ValueError('必须使用预冻结四进程平衡顺序与5轮')
    plan_path = checked(policy['plan'])
    # 主进程不加载原生库，使计时子进程有独立的动态库和OpenMP生命周期。
    out, identity = claim(args.output, plan_path,
        ['scripts/bench_skylake_runtime.py', 'experiments/channel-runtime/channel_native.py',
         'scripts/suffix_cache_support.py',
         'scripts/delta16_support.py',
         'scripts/axis_preweight_support.py',
         'scripts/restrict_support.py',
         'scripts/cache_encoding_support.py',
         args.policy.resolve().relative_to(ROOT).as_posix()],
        {'purpose': __doc__, 'policy': policy,
         'scope': '一次100图完整组，稳态毫秒每图不含准备/IO/解码；另外列准备墙钟与准备+首轮100图，后者仍已预热'})
    workers = []
    env = os.environ.copy()
    for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
        env[key] = '1'
    env['OMP_DYNAMIC'] = 'FALSE'; env['OMP_PROC_BIND'] = 'FALSE'; env['PYTHONIOENCODING'] = 'utf-8'
    for index in range(4):
        destination = out/f'worker{index}.json'
        proc = subprocess.run([sys.executable, '-X', 'utf8', str(Path(__file__).resolve()),
            '--policy', str(args.policy.resolve()), '--output', str(destination), '--worker-index', str(index)],
            capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
        (out/f'worker{index}.stdout.log').write_text(proc.stdout, encoding='utf-8')
        (out/f'worker{index}.stderr.log').write_text(proc.stderr, encoding='utf-8')
        if proc.returncode:
            raise RuntimeError(f'性能进程{index}失败：'+proc.stderr)
        workers.append(read(destination)); print('完成串行性能进程', index, flush=True)
    if len({w['source_sha256'] for w in workers}) != 1:
        raise ValueError('各进程源图组不同')
    if any(w['actual_affinity'] != policy['affinity_cpus'] for w in workers):
        raise ValueError('实际亲和性不是冻结集合')
    summaries = []; paired = []; failures = []
    for threads in (1, 4):
        matched = [{r['variant']: r for r in w['records'] if r['requested_threads'] == threads} for w in workers]
        for name in ('reference', 'candidate'):
            values = [statistics.median(w[name]['apply_seconds'])*10 for w in matched]
            total = [statistics.median(w[name]['copy_apply_seconds'])*10 for w in matched]
            summaries.append({'variant': name, 'requested_threads': threads,
                'median_apply_ms_per_image': statistics.median(values), 'process_medians_ms_per_image': values,
                'median_copy_apply_ms_per_image': statistics.median(total),
                'prepare_wall_seconds': [w[name]['prepare_wall_seconds'] for w in matched],
                'median_prepare_plus_first_100_apply_seconds': statistics.median(
                    w[name]['prepare_plus_first_100_apply_seconds'] for w in matched),
                'median_prepare_plus_first_100_copy_apply_seconds': statistics.median(
                    w[name]['prepare_plus_first_100_copy_apply_seconds'] for w in matched),
                'model_accounting_bytes': matched[0][name]['model_accounting_bytes']})
        ratios = [statistics.median(w['candidate']['apply_seconds'])/statistics.median(w['reference']['apply_seconds']) for w in matched]
        totals = [statistics.median(w['candidate']['copy_apply_seconds'])/statistics.median(w['reference']['copy_apply_seconds']) for w in matched]
        prepared = [w['candidate']['prepare_plus_first_100_copy_apply_seconds']/w['reference']['prepare_plus_first_100_copy_apply_seconds'] for w in matched]
        gates = policy['adoption_gate']
        if statistics.median(ratios) > gates['median_apply_ratio_max']:
            failures.append(f'{threads}线程apply中位比未达门槛')
        if max(ratios) > gates['any_process_apply_ratio_max']:
            failures.append(f'{threads}线程至少一个进程退化超限')
        if statistics.median(totals) > gates['median_copy_apply_ratio_max']:
            failures.append(f'{threads}线程copy+apply退化')
        if 'median_prepare_plus_100_ratio_max' in gates and statistics.median(prepared) > gates['median_prepare_plus_100_ratio_max']:
            failures.append(f'{threads}线程准备+100图退化')
        paired.append({'requested_threads': threads, 'process_apply_ratios': ratios,
            'median_apply_ratio': statistics.median(ratios), 'process_copy_apply_ratios': totals,
            'median_copy_apply_ratio': statistics.median(totals),
            'process_prepare_plus_100_copy_apply_ratios': prepared,
            'median_prepare_plus_100_copy_apply_ratio': statistics.median(prepared)})
    unchanged(identity)
    result = {'measurement_completed': True, 'accepted_on_this_host': not failures, 'failed_gates': failures,
        'summary': summaries, 'paired': paired, 'worker_sha256': [digest(out/f'worker{i}.json') for i in range(4)],
        'actual_affinity': policy['affinity_cpus'], 'frequency_and_temperature_controlled': False,
        'sample_unit': '每进程/每配置一次100图完整组，5轮中位；同进程比值后取四进程比值中位',
        'scope': '本机当前编译、模型与核集合的描述；不作为Skylake服务器实测，不因本机采用而替换公共默认。'}
    save(out/'results.json', result)
    print('性能比较完成：', result['accepted_on_this_host'], result['paired'], flush=True)


if __name__ == '__main__':
    main()
