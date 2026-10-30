"""90独立确认：三项既定N100/T4失效场景，31完整轮及镜像角色时序。"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import statistics as st
import subprocess
import sys
import numpy as np
from p16_segment_support import checked, setup, run_driver, output_hash, close, save, digest, env


def summarize(plan, workers):
    rows = []
    for scene in plan['scenes']:
        matched = [{r['variant']: r for r in w['records'] if r['scene'] == scene['id']} for w in workers]
        controls = {str(v): [st.median(m[v]['occurrences'][1]['seconds']) /
            st.median(m[v]['occurrences'][0]['seconds']) for m in matched] for v in (0, 1, 2)}
        estimates = [{v: math.sqrt(st.median(m[v]['occurrences'][0]['seconds']) *
            st.median(m[v]['occurrences'][1]['seconds'])) for v in (0, 1, 2)} for m in matched]
        comparisons = {}
        for before, after in ((0, 2), (1, 2), (0, 1)):
            ratios = [e[after] / e[before] for e in estimates]
            aa = controls[str(before)] + controls[str(after)]
            valid = all(plan['control_min'] <= v <= plan['control_max'] for v in aa)
            worst = 1 / max(ratios)
            comparisons[f'{after}_over_{before}'] = {'time_ratios': ratios,
                'median_time_ratio': st.median(ratios), 'worst_throughput_retained': worst,
                'control_valid': valid, 'grades': {str(g): valid and worst >= g / 100 for g in plan['grades']}}
        rows.append({'scene': scene, 'controls': controls, 'comparisons': comparisons,
            'geomean_ms_per_image': {str(v): [e[v] * 10 for e in estimates] for v in (0, 1, 2)}})
    return rows


def worker(args, plan):
    quality = json.loads(checked(plan['quality_proof']).read_text(encoding='utf-8'))
    expected = {(r['scale'], r['images']): r['output_sha256'] for r in quality['photos'] if r['role'] == 'direct'}
    libs, chains, frames, function, model_plan, directory, driver = setup(plan)
    records = []
    source_full_sha = output_hash([frames])
    assert source_full_sha == plan['source_sha256']
    try:
        scene_order = plan['scene_orders'][args.worker]
        for index in scene_order:
            scene = plan['scenes'][index]
            scale, layout = scene['scale'], scene['layout']
            if layout == 0:
                packed_source = np.ascontiguousarray(frames[:, ::scale, ::scale])
                packed_destination = np.empty_like(packed_source)
                sources = [packed_source[i] for i in range(100)]
                destinations = [packed_destination[i] for i in range(100)]
            else:
                sources = [frames[i, ::scale, ::scale].copy() for i in range(100)]
                destinations = [np.empty_like(a) for a in sources]
                shape = (100, frames.shape[1] // scale, frames.shape[2] // scale, 3)
                packed_source, packed_destination = np.empty(shape, np.uint8), np.empty(shape, np.uint8)
            before = output_hash(sources)

            def group(variant, repeats):
                for target in destinations:
                    target.fill(173)
                if layout:
                    packed_source.fill(239)
                    packed_destination.fill(173)
                seconds = run_driver(function, chains['direct'], sources, destinations, packed_source,
                    packed_destination, layout, variant, 4, repeats)
                actual = output_hash(destinations)
                assert actual == expected[scale, 100]
                return {'seconds': seconds, 'actual_output_sha256': actual}

            warm = {str(v): group(v, plan['warm_repeats']) for v in plan['warm_orders'][args.worker]}
            current = {v: {'scene': scene['id'], 'variant': v, 'warmup': warm[str(v)],
                'occurrences': [], 'source_sha256': before} for v in (0, 1, 2)}
            for position, variant in enumerate(plan['sequences'][args.worker]):
                result = group(variant, plan['repeats'])
                result['sequence_position'] = position
                current[variant]['occurrences'].append(result)
                save(args.output / f'worker{args.worker}-partial.json', {
                    'records': records, 'current_scene': list(current.values())})
            assert output_hash(sources) == before
            records.extend(current.values())
            del sources, destinations, packed_source, packed_destination
        assert output_hash([frames]) == source_full_sha
        save(args.output / f'worker{args.worker}.json', {'records': records, 'environment': env(),
            'source_full_sha256': source_full_sha})
    finally:
        close(chains)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--worker', type=int)
    args = p.parse_args()
    plan = json.loads(args.plan.read_text(encoding='utf-8'))
    assert digest(Path(__file__)) == plan['script_sha256']
    for row in plan['execution_dependencies'] + plan['source_identities']:
        checked(row)
    checked(plan['quality_proof'])
    checked(plan['previous_results'])
    if args.worker is not None:
        return worker(args, plan)
    if args.output.exists():
        raise FileExistsError('保留首次确认，不重跑或覆盖')
    args.output.mkdir(parents=True)
    save(args.output / 'executed-plan.json', plan)
    workers = []
    for i in range(4):
        subprocess.run([sys.executable, '-X', 'utf8', __file__, '--plan', str(args.plan),
            '--output', str(args.output), '--worker', str(i)], check=True)
        workers.append(json.loads((args.output / f'worker{i}.json').read_text(encoding='utf-8')))
        print('完成90独立确认进程', i, flush=True)
    summary = summarize(plan, workers)
    save(args.output / 'results.json', {'summary': summary,
        'worker_sha256': [digest(args.output / f'worker{i}.json') for i in range(4)],
        'scope': '独立新31轮镜像协议，不覆盖v1；按冻结几何均值估计及A/A门，不与旧场绝对时间相除。'})
    for row in summary:
        print(row['scene']['id'], {k: (v['control_valid'], v['median_time_ratio'], v['worst_throughput_retained'])
            for k, v in row['comparisons'].items()}, flush=True)


if __name__ == '__main__':
    main()
