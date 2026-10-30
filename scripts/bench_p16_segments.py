"""90显式分段接口三角色同场；连续及真正非连续布局分别完整计费。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import statistics as st
import subprocess
import sys
import numpy as np
import psutil
from p16_segment_support import checked, setup, run_driver, output_hash, close, save, digest, env


def worker(args, plan):
    proof = json.loads(checked(plan['quality_proof']).read_text(encoding='utf-8'))
    assert proof['passed']
    expected = {(r['role'], r['scale'], r['images']): r['output_sha256'] for r in proof['photos']}
    libs, chains, frames, function, model_plan, directory, driver = setup(plan)
    records = []
    source_full_sha = output_hash([frames])
    assert source_full_sha == plan['source_sha256']
    try:
        for model in plan['model_orders'][args.worker]:
            pair = chains[model]
            scales = list(plan['role_scales'][model])
            if args.worker % 2:
                scales.reverse()
            for scale in scales:
                for images in plan['image_orders'][args.worker]:
                    shape = (images, frames.shape[1] // scale, frames.shape[2] // scale, 3)
                    for layout in plan['layout_orders'][args.worker]:
                        if layout == 0:
                            packed_source = np.ascontiguousarray(frames[:images, ::scale, ::scale])
                            packed_destination = np.empty_like(packed_source)
                            sources = [packed_source[i] for i in range(images)]
                            destinations = [packed_destination[i] for i in range(images)]
                            fixture_bytes = packed_source.nbytes + packed_destination.nbytes
                        else:
                            sources = [frames[i, ::scale, ::scale].copy() for i in range(images)]
                            destinations = [np.empty_like(a) for a in sources]
                            packed_source = np.empty(shape, np.uint8)
                            packed_destination = np.empty(shape, np.uint8)
                            fixture_bytes = packed_source.nbytes + packed_destination.nbytes
                            fixture_bytes += sum(a.nbytes for a in sources + destinations)
                        before = output_hash(sources)
                        expected_sha = expected[model, scale, images]
                        # 填充在计时外；正式role1的pack/scatter仍在原生driver计时内。
                        def group(variant, threads, repeats):
                            for target in destinations:
                                target.fill(173)
                            if layout:
                                packed_source.fill(239)
                                packed_destination.fill(173)
                            seconds = run_driver(function, pair, sources, destinations, packed_source,
                                packed_destination, layout, variant, threads, repeats)
                            actual_sha = output_hash(destinations)
                            assert actual_sha == expected_sha, (model, scale, images, layout, variant, threads)
                            return {'seconds': seconds, 'actual_output_sha256': actual_sha}

                        rss_after_alloc = psutil.Process().memory_info().rss
                        for threads in plan['thread_orders'][args.worker]:
                            for variant in plan['orders'][args.worker]:
                                warm = group(variant, threads, plan['warm_repeats'])
                                measured = group(variant, threads, plan['repeats'][str(images)])
                                control = group(variant, threads, plan['repeats'][str(images)])
                                records.append({'model': model, 'scale': scale, 'images': images,
                                    'layout': layout, 'variant': variant, 'threads': threads,
                                    'warmup': warm, 'measured': measured, 'control': control,
                                    'source_sha256': before, 'fixture_bytes': fixture_bytes,
                                    'rss_after_alloc_snapshot_bytes': rss_after_alloc,
                                    'model_bytes': {n: c.model_bytes for n, c in pair.items()}})
                                save(args.output / f'worker{args.worker}-partial.json', {'records': records})
                        assert output_hash(sources) == before
                        del sources, destinations, packed_source, packed_destination
        assert output_hash([frames]) == source_full_sha
        save(args.output / f'worker{args.worker}.json', {'records': records, 'environment': env(),
            'source_full_sha256': source_full_sha,
            'scope': '每组实际caller-owned末轮SHA；非连续bulk含pack/scatter；分段验证/任务构造与分配/调度全在计时内。'})
    finally:
        close(chains)


def summarize(plan, workers):
    rows = []
    for model, scales in plan['role_scales'].items():
        for scale in scales:
            for images in (1, 10, 100):
                for layout in (0, 1):
                    for threads in (1, 4):
                        matched = [{r['variant']: r for r in w['records'] if
                            (r['model'], r['scale'], r['images'], r['layout'], r['threads']) ==
                            (model, scale, images, layout, threads)} for w in workers]
                        assert all(set(m) == {0, 1, 2} for m in matched)
                        comparisons = {}
                        controls = {str(v): [st.median(m[v]['control']['seconds']) /
                            st.median(m[v]['measured']['seconds']) for m in matched] for v in (0, 1, 2)}
                        for before, after in ((0, 2), (1, 2), (0, 1)):
                            ratios = [st.median(m[after]['measured']['seconds']) /
                                st.median(m[before]['measured']['seconds']) for m in matched]
                            aa = controls[str(before)] + controls[str(after)]
                            valid = all(plan['control_min'] <= v <= plan['control_max'] for v in aa)
                            retained = 1 / max(ratios)
                            comparisons[f'{after}_over_{before}'] = {'time_ratios': ratios,
                                'median_time_ratio': st.median(ratios), 'worst_throughput_retained': retained,
                                'control_valid': valid,
                                'grades': {str(g): valid and retained >= g / 100 for g in plan['grades']},
                                'no_obvious_slowdown': valid and st.median(ratios) <= plan['no_obvious_median_max']
                                    and max(ratios) <= plan['no_obvious_any_max']}
                        rows.append({'model': model, 'scale': scale, 'images': images, 'layout': layout,
                            'threads': threads, 'controls': controls, 'comparisons': comparisons,
                            'ms_per_image': {str(v): [st.median(m[v]['measured']['seconds']) * 1000 / images
                                for m in matched] for v in (0, 1, 2)}})
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--worker', type=int)
    args = p.parse_args()
    plan = json.loads(args.plan.read_text(encoding='utf-8'))
    assert digest(Path(__file__)) == plan['script_sha256']
    for row in plan['execution_dependencies']:
        checked(row)
    for row in plan['source_identities']:
        checked(row)
    if args.worker is not None:
        return worker(args, plan)
    if args.output.exists():
        raise FileExistsError('保留全部轮次，不覆盖重选')
    args.output.mkdir(parents=True)
    checked(plan['quality_proof'])
    checked(plan['quality_plan'])
    save(args.output / 'executed-plan.json', plan)
    workers = []
    for i in range(4):
        subprocess.run([sys.executable, '-X', 'utf8', __file__, '--plan', str(args.plan),
            '--output', str(args.output), '--worker', str(i)], check=True)
        workers.append(json.loads((args.output / f'worker{i}.json').read_text(encoding='utf-8')))
        print('完成90三角色进程', i, flush=True)
    summary = summarize(plan, workers)
    save(args.output / 'results.json', {'summary': summary,
        'worker_sha256': [digest(args.output / f'worker{i}.json') for i in range(4)],
        'scope': '36独立模型/布局/形状/线程场景；不跨布局相除，三角色同场。准备/文件hash/分配fixture在外；目标API自身全部验证、任务构造分配、调度及必要pack/scatter在内。'})
    for baseline in (0, 1):
        selected = [r['comparisons'][f'2_over_{baseline}'] for r in summary]
        print('新segments对照', baseline, '有效场景', sum(r['control_valid'] for r in selected),
            '50档场景', sum(r['grades']['50'] for r in selected), '共', len(selected), flush=True)


if __name__ == '__main__':
    main()
