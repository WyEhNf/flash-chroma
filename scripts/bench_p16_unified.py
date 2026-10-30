"""102固定四级模型、真实100图CPU批次总时间；保留所有七轮原始值。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import time
import traceback

import numpy as np

import p16_unified_support as s


def run(args, output):
    s.setup(args.dll_directory, args.cpus)
    plan = s.load_plan(args.plan)
    library = s.Library(args.library)
    assert library.revision == 102
    quality_path = args.correctness.resolve()
    quality = json.loads(quality_path.read_text(encoding='utf-8'))
    assert quality['passed'] and quality['library']['sha256'] == library.sha256
    assert quality['input_plan']['sha256'] == plan['input_plan']['sha256']
    environment = s.environment(args.build_receipt)
    environment['script_sha256'].update(s.script_records(__file__))
    executed = {'plan': plan, 'library': library.record(), 'backends': args.backends, 'threads': args.threads,
        'warmup_batches': 1, 'measured_batches': 7, 'images_per_batch': 100, 'expected_pixels_hint': s.PIXELS,
        'mode': 'caller-owned分离输出，输入解码/哈希/分配/预触页在计时外',
        'quality': {'path': str(quality_path), 'sha256': s.digest(quality_path)}, 'environment': environment,
        'scope': '单进程单场CPU描述性测量，无跨机器加速外推；创建与首批连续wall另报，不计图像解码。'}
    s.save(output / 'executed-plan.json', executed)
    frames, photo_inputs = s.photos(plan)
    source_sha = s.sha(frames)
    target = np.empty_like(frames)
    target.fill(173)
    records = []
    verified = {row['model']: row for row in quality['models']}
    for name, row in plan['models'].items():
        expected = verified[name]['expected_photos']['batch_sha256']
        verified_backend = {v['backend']: v for v in verified[name]['backends']}
        for backend in args.backends:
            if not library.supported(backend):
                records.append({'model': name, 'backend': backend, 'executed': False,
                    'reason': 'CPU/OS未开放此后端；质量阶段已核明确拒绝，不冒充AVX512计时。'})
                continue
            if backend not in verified_backend or not verified_backend[backend]['executed']:
                raise ValueError('所选后端未通过绑定的质量回执')
            for threads in args.threads:
                if not any(v['threads'] == threads for v in verified_backend[backend]['photos']):
                    raise ValueError('所选线程数未通过绑定的质量回执')
                target.fill(173)
                before = s.rss()
                # paths/sidecar数组和错误缓冲位于create内部，属于本轮创建wall。
                started = time.perf_counter_ns()
                chain = library.create(row)
                try:
                    first_apply, stopped = chain.apply(frames, target, backend, threads)
                    continuous = (stopped - started) * 1e-9
                    assert s.sha(target) == expected
                    after = s.rss()
                    state = s.diagnostics(chain)
                    warmup, _ = chain.apply(frames, target, backend, threads)
                    assert s.sha(target) == expected
                    rounds, hashes = [], []
                    for index in range(7):
                        elapsed, _ = chain.apply(frames, target, backend, threads)
                        actual = s.sha(target)
                        assert actual == expected, (name, backend, threads, index)
                        rounds.append(elapsed)
                        hashes.append(actual)
                    record = {'model': name, 'backend': backend, 'threads': threads, 'executed': True,
                        'prepare_native_seconds': chain.prepare_seconds, 'first_batch_apply_seconds': first_apply,
                        'create_to_first_batch_wall_seconds': continuous, 'warmup_batch_seconds': warmup,
                        'batch_total_seconds_raw': rounds, 'batch_total_seconds_median': statistics.median(rounds),
                        'batch_total_seconds_min': min(rounds), 'batch_total_seconds_max': max(rounds),
                        'per_round_output_sha256': hashes, 'state': state,
                        'memory': {'process_before_create': before, 'process_after_first_batch': after,
                            'model_capacity_bytes': state['model_capacity_bytes'], 'source_image_bytes': frames.nbytes,
                            'output_image_bytes': target.nbytes, 'explicit_image_buffers_bytes': frames.nbytes + target.nbytes,
                            'scope': 'capacity为模型账单；RSS/Private含Python和依赖，进程峰值不是算法专属峰值。'}}
                finally:
                    chain.close()
                record['memory']['process_after_destroy'] = s.rss()
                records.append(record)
                s.save(output / 'partial.json', {'records': records, 'source_sha256': source_sha})
                print('百图批次七轮完成：', name, backend, threads, flush=True)
    assert s.sha(frames) == source_sha
    s.save(output / 'results.json', {'completed': True, 'library': library.record(), 'records': records,
        'environment': environment, 'source_sha256': source_sha, 'photo_inputs': photo_inputs,
        'measurement': {'images_per_batch': 100, 'warmup_batches': 1, 'measured_batches': 7,
            'batch_timer': 'Python perf_counter_ns包围单次native C ABI apply_to；含线程调度与FFI',
            'cold_scope': '新模型句柄；输入与输出已驻内存；不是冷磁盘或新进程',
            'excluded': '图像解码、文件校验、输出哈希、图像分配、预触页',
            'scope': '描述性单场总时间；无A/A稳定性或配对基线资格，不据此独立宣称普遍加速。'}})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library', type=Path, required=True)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--correctness', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--build-receipt', type=Path)
    parser.add_argument('--dll-directory')
    parser.add_argument('--cpus', default='0,2,4,6')
    parser.add_argument('--backends', nargs='+', choices=tuple(s.BACKENDS), default=['avx2', 'avx512'])
    parser.add_argument('--threads', nargs='+', type=int, default=[1, 4])
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('基准输出目录已存在，保留原始测量')
    args.output.mkdir(parents=True)
    try:
        run(args, args.output)
    except BaseException:
        s.save(args.output / 'failure.json', {'completed': False, 'traceback': traceback.format_exc()})
        raise


if __name__ == '__main__':
    main()
