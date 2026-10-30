"""固定default/max_first百图ABBA及A/A对照；同时测热映射与新句柄完整作业。"""
import argparse
import json
import os
from pathlib import Path
import statistics
import time

import numpy as np

import p16_unified_support as s


def summary(cycles):
    ratios = []
    for cycle in cycles:
        a = [v['seconds'] for v in cycle['trials'] if v['role'] == 'A']
        b = [v['seconds'] for v in cycle['trials'] if v['role'] == 'B']
        ratios.append(statistics.mean(b) / statistics.mean(a))
    return {'time_ratios_b_over_a_raw': ratios, 'median': statistics.median(ratios),
        'min': min(ratios), 'max': max(ratios)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library', type=Path, required=True)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--correctness', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('配对结果目录已存在')
    args.output.mkdir(parents=True)
    s.setup(cpus='0,2,4,6')
    plan, library = s.load_plan(args.plan), s.Library(args.library)
    q = json.loads(args.correctness.read_text(encoding='utf-8'))
    assert q['passed'] and q['library']['sha256'] == library.sha256
    assert q['input_plan']['sha256'] == plan['input_plan']['sha256']
    gold = {v['model']: v['expected_photos']['batch_sha256'] for v in q['models']}
    frames, _ = s.photos(plan)
    target = np.empty_like(frames)
    target.fill(173)
    environment = s.environment()
    environment['thread_environment'] = {k: os.environ.get(k) for k in
        ('OMP_NUM_THREADS', 'OMP_WAIT_POLICY', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS')}
    frozen = {'library': library.record(), 'plan': plan['input_plan'], 'rounds': 8,
        'threads': 4, 'orders': ['ABBA', 'BAAB'], 'a_model': 'default', 'b_models': ['default', 'max_first'],
        'modes': ['hot_apply', 'create_to_first_batch'], 'aa_time_ratio_bounds': [.90, 1.10],
        'environment': environment, 'source_sha256': s.sha(frames),
        'scripts': s.script_records(__file__, Path(s.__file__))}
    s.save(args.output / 'plan.json', frozen)
    records = []
    for mode in frozen['modes']:
        for candidate in frozen['b_models']:
            models = {'A': 'default', 'B': candidate}
            handles = {}
            if mode == 'hot_apply':
                for role, name in models.items():
                    handles[role] = library.create(plan['models'][name])
                    handles[role].apply(frames, target, 'avx2', 4)
                    assert s.sha(target) == gold[name]
            cycles = []
            try:
                for index in range(8):
                    trials = []
                    order = 'ABBA' if index % 2 == 0 else 'BAAB'
                    for role in order:
                        name = models[role]
                        if mode == 'hot_apply':
                            elapsed, _ = handles[role].apply(frames, target, 'avx2', 4)
                        else:
                            start = time.perf_counter_ns()
                            chain = library.create(plan['models'][name])
                            try:
                                _, stop = chain.apply(frames, target, 'avx2', 4)
                                elapsed = (stop - start) * 1e-9
                            finally:
                                chain.close()
                        actual = s.sha(target)
                        assert actual == gold[name]
                        trials.append({'role': role, 'model': name, 'seconds': elapsed, 'sha256': actual})
                    cycles.append({'index': index, 'order': order, 'trials': trials})
                records.append({'mode': mode, 'a_model': 'default', 'b_model': candidate,
                    'cycles': cycles, 'summary': summary(cycles)})
                s.save(args.output / 'partial.json', {'records': records})
                print('配对完成：', mode, candidate, flush=True)
            finally:
                for handle in handles.values():
                    handle.close()
    assert s.sha(frames) == frozen['source_sha256']
    for row in records:
        control = next(v for v in records if v['mode'] == row['mode'] and v['b_model'] == 'default')
        row['aa_stable'] = control['summary']['min'] >= .90 and control['summary']['max'] <= 1.10
    s.save(args.output / 'results.json', {'completed': True, 'plan': frozen, 'records': records,
        'timed_batches': 128, 'scope': '八固定配对周期，A/A按全部周期范围判定；没有置信区间或跨机结论。新句柄含SLUT加载与精确缓存准备，不含原始LUT拟合、图片解码或输出哈希。'})


if __name__ == '__main__':
    main()
