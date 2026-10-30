"""91同模型87配对：准备到首次映射连续墙钟、N1/10/100热路径、独立RSS。"""
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
import psutil
from bench_p16_model_pair import checked, source, native_create
from study_p16_direct_compile import Library, save, digest, env
from channel_native import Chain
from suffix_cache_support import cache_info
from domain_cache_support import info as domain_info
from palette_support import info as palette_info
from direct16_support import info as direct_info


def sha(a):
    return hashlib.sha256(memoryview(a).cast('B')).hexdigest()


def state(c):
    return {'cache': cache_info(c), 'domain': domain_info(c), 'palette': palette_info(c),
            'direct': direct_info(c), 'model_bytes': c.model_bytes}


def setup(plan, roles):
    psutil.Process().cpu_affinity(plan['cpus'])
    directory = os.add_dll_directory('E:/mingw64/bin') if os.name == 'nt' else None
    libs = {r: Library(checked(plan['libraries'][r]), plan['libraries'][r]['sha256']) for r in roles}
    u8, doubles = ct.POINTER(ct.c_uint8), ct.POINTER(ct.c_double)
    common = [ct.c_void_p, u8, u8, ct.c_size_t, ct.c_int, ct.c_int, ct.c_size_t]
    for role, lib in libs.items():
        assert lib.revision == (87 if role == 'reference' else 91)
        lib.dll.jshc_cc_bench.argtypes = common + [doubles, doubles, ct.POINTER(ct.c_char), ct.c_size_t]
        lib.dll.jshc_cc_bench_to.argtypes = common + [doubles, ct.POINTER(ct.c_char), ct.c_size_t]
        lib.dll.jshc_cc_bench_to.restype = ct.c_int
    return libs, directory


def rss_worker(args, plan):
    libs, directory = setup(plan, [args.rss_role])
    m = plan['models'][args.rss_model]
    before = psutil.Process().memory_info()
    chain, elapsed = native_create(libs[args.rss_role], m)
    with chain:
        after = psutil.Process().memory_info()
        save(args.output / f'rss-{args.rss_model}-{args.rss_role}.json', {
            'model': args.rss_model, 'role': args.rss_role, 'before': before._asdict(), 'after': after._asdict(),
            'rss_delta_bytes': after.rss - before.rss, 'prepare_seconds_descriptive': elapsed,
            'state': state(chain), 'environment': env(),
            'scope': '每模型/角色独立新进程，不加载照片；实际RSS/Windows peak_wset非容器容量，描述构造内存，不作配对计时样本。'})


def worker(args, plan):
    libs, directory = setup(plan, ('reference', 'candidate'))
    mp = json.loads(checked(plan['photo_model_plan']).read_text(encoding='utf-8'))
    frames, manifest = source(mp)
    assert sha(frames) == plan['source_sha256']
    expected = {(r['role'], r['images']): r['output_sha256'] for r in plan['photo_expected']}
    u8, doubles = ct.POINTER(ct.c_uint8), ct.POINTER(ct.c_double)
    records, cold_records = [], []
    for model in plan['model_orders'][args.worker]:
        m = plan['models'][model]
        paths = [checked(row) for row in m['models']]
        sides = [checked(row) if row else None for row in m['sidecars']]
        path_array = (ct.c_char_p * 4)(*(str(v).encode('utf-8') for v in paths))
        side_array = (ct.c_char_p * 4)(*(str(v).encode('utf-8') if v else None for v in sides))
        for role in plan['orders'][args.worker]:
            lib = libs[role]
            for images in plan['image_orders'][args.worker]:
                inputs = frames[:images]
                work = np.empty_like(inputs)
                work.fill(0)
                actual_expected = expected[model, images]
                error = ct.create_string_buffer(1024)
                first_time = np.empty(1, np.float64)
                source_pointer, work_pointer = inputs.ctypes.data_as(u8), work.ctypes.data_as(u8)
                cold = []
                handle = ct.c_void_p()
                for iteration in range(plan['cold_repeats'] * 2):
                    work.fill(173)
                    handle = ct.c_void_p()
                    handle_pointer = ct.byref(handle)
                    begin = time.perf_counter_ns()
                    rc = lib.dll.jshc_cc_create(path_array, side_array, 4, handle_pointer, error, len(error))
                    created = time.perf_counter_ns()
                    if rc:
                        raise RuntimeError(error.value.decode('utf-8', 'replace'))
                    rc = lib.dll.jshc_cc_bench_to(handle, source_pointer, work_pointer, inputs.nbytes,
                        1, 4, 1, first_time.ctypes.data_as(doubles), error, len(error))
                    ended = time.perf_counter_ns()
                    if rc:
                        lib.dll.jshc_cc_destroy(handle)
                        raise RuntimeError(error.value.decode('utf-8', 'replace'))
                    actual = sha(work)
                    assert actual == actual_expected
                    cold.append({'prepare_seconds': (created - begin) * 1e-9,
                        'first_outplace4_seconds': float(first_time[0]),
                        'create_to_first_wall_seconds': (ended - begin) * 1e-9,
                        'actual_output_sha256': actual})
                    if iteration + 1 < plan['cold_repeats'] * 2:
                        lib.dll.jshc_cc_destroy(handle)
                chain = Chain.__new__(Chain)
                chain.library, chain.handle = lib, handle
                with chain:
                    snapshot = state(chain)
                    cold_records.append({'model': model, 'role': role, 'images': images,
                        'samples': cold[:plan['cold_repeats']], 'control': cold[plan['cold_repeats']:], 'state': snapshot})

                    def group(boundary, threads, repeats):
                        work.fill(173)
                        seconds, total = np.empty(repeats, np.float64), np.empty(repeats, np.float64)
                        fields = [chain.handle, source_pointer, work_pointer, inputs.nbytes, 1, threads,
                                  repeats, seconds.ctypes.data_as(doubles)]
                        if boundary == 'apply':
                            rc = lib.dll.jshc_cc_bench(*fields, total.ctypes.data_as(doubles), error, len(error))
                        else:
                            rc = lib.dll.jshc_cc_bench_to(*fields, error, len(error))
                        assert rc == 0, error.value
                        actual = sha(work)
                        assert actual == actual_expected
                        result = {'seconds': seconds.tolist(), 'actual_output_sha256': actual}
                        if boundary == 'apply':
                            result['copy_apply_seconds'] = total.tolist()
                        return result

                    for threads in plan['thread_orders'][args.worker]:
                        for boundary in plan['boundary_orders'][args.worker]:
                            warm = group(boundary, threads, plan['warmup'])
                            measured = group(boundary, threads, plan['repeats'][str(images)])
                            control = group(boundary, threads, plan['repeats'][str(images)])
                            records.append({'model': model, 'role': role, 'images': images, 'threads': threads,
                                'boundary': boundary, 'warmup': warm, 'measured': measured, 'control': control})
                            save(args.output / f'worker{args.worker}-partial.json', {'records': records, 'cold_records': cold_records})
    assert sha(frames) == plan['source_sha256']
    save(args.output / f'worker{args.worker}.json', {'records': records, 'cold_records': cold_records,
        'source_sha256': plan['source_sha256'], 'environment': env()})


def ratio_row(plan, numerator, denominator, controls):
    ratios = [a / b for a, b in zip(numerator, denominator)]
    valid = all(plan['control_min'] <= v <= plan['control_max'] for v in controls)
    retained = 1 / max(ratios)
    return {'time_ratios': ratios, 'median_time_ratio': st.median(ratios), 'worst_throughput_retained': retained,
        'controls': controls, 'control_valid': valid, 'grades': {str(g): valid and retained >= g / 100 for g in plan['grades']},
        'no_obvious_slowdown': valid and st.median(ratios) <= plan['no_obvious_median_max']
            and max(ratios) <= plan['no_obvious_any_max']}


def summarize(plan, workers):
    hot, cold = [], []
    for model in plan['models']:
        for images in (1, 10, 100):
            matched_cold = [{r['role']: r for r in w['cold_records'] if
                (r['model'], r['images']) == (model, images)} for w in workers]
            metrics = {}
            for key in ('prepare_seconds', 'first_outplace4_seconds', 'create_to_first_wall_seconds'):
                values = {role: [st.median(x[key] for x in m[role]['samples']) for m in matched_cold]
                          for role in ('reference', 'candidate')}
                controls = [st.median(x[key] for x in m[role]['control']) / st.median(x[key] for x in m[role]['samples'])
                            for m in matched_cold for role in ('reference', 'candidate')]
                metrics[key] = ratio_row(plan, values['candidate'], values['reference'], controls)
                metrics[key]['milliseconds'] = {r: [v * 1000 for v in a] for r, a in values.items()}
            cold.append({'model': model, 'images': images, 'metrics': metrics})
            for threads in (1, 4):
                for boundary in ('apply', 'outplace'):
                    matched = [{r['role']: r for r in w['records'] if
                        (r['model'], r['images'], r['threads'], r['boundary']) == (model, images, threads, boundary)} for w in workers]
                    values = {role: [st.median(m[role]['measured']['seconds']) for m in matched]
                              for role in ('reference', 'candidate')}
                    controls = [st.median(m[role]['control']['seconds']) / st.median(m[role]['measured']['seconds'])
                                for m in matched for role in ('reference', 'candidate')]
                    row = ratio_row(plan, values['candidate'], values['reference'], controls)
                    row.update({'model': model, 'images': images, 'threads': threads, 'boundary': boundary,
                        'ms_per_image': {r: [v * 1000 / images for v in a] for r, a in values.items()}})
                    hot.append(row)
    return {'hot': hot, 'cold': cold}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--worker', type=int)
    p.add_argument('--rss-role', choices=('reference', 'candidate'))
    p.add_argument('--rss-model', choices=('ordinary', 'anchor'))
    a = p.parse_args()
    plan = json.loads(a.plan.read_text(encoding='utf-8'))
    assert digest(Path(__file__)) == plan['script_sha256']
    for row in plan['sources']:
        checked(row)
    checked(plan['quality_proof'])
    if a.rss_role:
        return rss_worker(a, plan)
    if a.worker is not None:
        return worker(a, plan)
    if a.output.exists():
        raise FileExistsError('保留首次正式性能，不覆盖重选')
    a.output.mkdir(parents=True)
    save(a.output / 'executed-plan.json', plan)
    workers = []
    for i in range(4):
        subprocess.run([sys.executable, '-X', 'utf8', __file__, '--plan', str(a.plan), '--output', str(a.output), '--worker', str(i)], check=True)
        workers.append(json.loads((a.output / f'worker{i}.json').read_text(encoding='utf-8')))
        print('完成91配对进程', i, flush=True)
    for model in ('ordinary', 'anchor'):
        for role in ('reference', 'candidate'):
            subprocess.run([sys.executable, '-X', 'utf8', __file__, '--plan', str(a.plan), '--output', str(a.output),
                '--rss-model', model, '--rss-role', role], check=True)
    results = summarize(plan, workers)
    results.update({'worker_sha256': [digest(a.output / f'worker{i}.json') for i in range(4)],
        'scope': '各N/模型/边界独立资格与100~50档；冷prepare/内部首次映射/连续create→首次墙钟分列；热吞吐不能豁免冷作业退化。'})
    save(a.output / 'results.json', results)
    for model in ('ordinary', 'anchor'):
        rows = [r for r in results['hot'] if r['model'] == model]
        print(model, '热控制有效', sum(r['control_valid'] for r in rows), '/', len(rows), flush=True)


if __name__ == '__main__':
    main()
