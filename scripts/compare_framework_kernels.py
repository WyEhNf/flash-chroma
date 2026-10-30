"""在原框架计时区间中交错比较两份同模型程序，保留每次输出及来源。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import random
import statistics

import check_framework_delivery as check


def run(args):
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    logs = output/'runs'; logs.mkdir()
    executables = {'before': args.before.resolve(), 'after': args.after.resolve()}
    data = args.data.resolve()
    sources = [Path(__file__).resolve(), Path(check.__file__).resolve(), *executables.values()]
    for folder in sorted({p.parent for p in executables.values()}):
        sources += [folder/'main.cpp', folder/'flash_chroma_framework.hpp', folder/'run.ps1']
    sources += [data/'LUT'/f'Test{i}.3DL' for i in range(1, 5)]
    sources += [data/'image'/f'{i}.bin' for i in range(1, args.count+1)]
    before = check.file_identities(sources)
    config = dict(id='same-model', m=33, mode='direct_rgb24', backend='avx2', grid='framework', fit='chain_ls')
    rng = random.Random(20261030)
    orders = []
    for _ in range(args.reps):
        order = ['before', 'after']; rng.shuffle(order); orders.append(order)
    check.write_new(output/'execution.json', dict(sources_before=before, config=config, orders=orders,
                    reps=args.reps, affinity=args.affinity, count=args.count,
                    scope='每次独立进程，原main图间参考及含输出申请的TimeCost；本比较不授予独立A/A资格。'))
    runs = []
    failure = None
    try:
        for round_index, order in enumerate(orders, 1):
            for ordinal, name in enumerate(order, 1):
                actual = dict(config, id=name)
                record = check.launch(executables[name], data, actual, args.count, args.affinity, logs,
                                      f'r{round_index:02d}-{ordinal:02d}-{name}')
                record['round'] = round_index; runs.append(record)
                if not record['passed']: raise RuntimeError(record.get('error', '运行失败'))
        first = runs[0]['images']
        for record in runs:
            if [(r['candidate_delta'], r['reference_delta']) for r in record['images']] != [
                    (r['candidate_delta'], r['reference_delta']) for r in first]:
                raise RuntimeError('不同程序/重复的原框架逐图误差不一致')
    except Exception as error:
        failure = str(error)
    after = check.file_identities(sources)
    summaries = {name: check.summarize_config(dict(config, id=name), runs, args.reps, args.count)
                 for name in executables}
    ratios = []
    for i in range(1, args.reps+1):
        pair = {r['config']: r['batch_ms'] for r in runs if r['round'] == i and r['passed']}
        if len(pair) == 2: ratios.append(pair['after']/pair['before'])
    passed = not failure and before == after and all(r['complete'] and r['delta_consistent'] for r in summaries.values())
    summary = dict(passed=passed, error=failure, sources_unchanged=before == after, sources_after=after,
                   configurations=summaries, runs=runs, paired_after_before_ratios=ratios,
                   median_paired_ratio=statistics.median(ratios) if ratios else None,
                   aa_stability_evaluated=False,
                   scope='原框架固定四图、m33/framework/chain_ls/AVX2单线程；精度相同，原样保留所有重复。')
    check.write_new(output/'summary.json', summary)
    return dict(passed=passed, output=str(output), error=failure,
                median_paired_ratio=summary['median_paired_ratio'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', type=Path, required=True)
    parser.add_argument('--after', type=Path, required=True)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reps', type=int, default=5)
    parser.add_argument('--count', type=int, default=4)
    parser.add_argument('--affinity', type=int, default=16)
    args = parser.parse_args()
    if not 3 <= args.reps <= 10 or not 1 <= args.count <= 100:
        parser.error('重复数必须为3..10，图片数必须为1..100')
    result = run(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
