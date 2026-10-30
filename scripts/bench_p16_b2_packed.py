"""99同场87/95/97/99；三个分母、完整准备/首组wall与冷热边界分别验收。"""
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
from bench_p16_model_pair import checked, source
from bench_p16_workload import ratio_row
from study_p16_direct_compile import Library, save, digest, env
from channel_native import Chain
from p16_workload_support import bind_workload, workload_chain, THRESHOLD
from verify_p16_workload import state
from direct16_support import info as direct_info


def sha(array):
    return hashlib.sha256(memoryview(array).cast('B')).hexdigest()


def setup(plan, roles):
    psutil.Process().cpu_affinity(plan['cpus'])
    directory = os.add_dll_directory('E:/mingw64/bin') if os.name == 'nt' else None
    libraries = {r: Library(checked(plan['libraries'][r]), plan['libraries'][r]['sha256']) for r in roles}
    for role, library in libraries.items():
        assert library.revision == {'reference': 87, 'previous': 95, 'isolated': 97, 'candidate': 99}[role]
        if role != 'reference':
            bind_workload(library)
        u8, d = ct.POINTER(ct.c_uint8), ct.POINTER(ct.c_double)
        common = [ct.c_void_p, u8, u8, ct.c_size_t, ct.c_int, ct.c_int, ct.c_size_t]
        library.dll.jshc_cc_bench.argtypes = common + [d, d, ct.POINTER(ct.c_char), ct.c_size_t]
        library.dll.jshc_cc_bench_to.argtypes = common + [d, ct.POINTER(ct.c_char), ct.c_size_t]
        library.dll.jshc_cc_bench_to.restype = ct.c_int
    return libraries, directory


def arrays(model):
    paths = [checked(v) for v in model['models']]
    sides = [checked(v) if v else None for v in model['sidecars']]
    a = (ct.c_char_p * 4)(*(str(v).encode('utf-8') for v in paths))
    b = (ct.c_char_p * 4)(*(str(v).encode('utf-8') if v else None for v in sides))
    return paths, sides, a, b


def expected_direct(model, role, images):
    return model == 'anchor' or (role != 'reference' and images * 786432 >= THRESHOLD)


def rss_worker(args, plan):
    libraries, directory = setup(plan, [args.rss_role])
    paths, sides, _, _ = arrays(plan['models'][args.rss_model])
    library = libraries[args.rss_role]
    default = args.rss_role == 'reference' or args.rss_images == 1
    before = psutil.Process().memory_info()
    started = time.perf_counter_ns()
    chain = library.chain(paths, sides) if default else workload_chain(library, paths, sides,
        expected_pixels=args.rss_images * 786432)
    elapsed = (time.perf_counter_ns() - started) * 1e-9
    with chain:
        after = psutil.Process().memory_info()
        assert bool(direct_info(chain)['enabled']) == expected_direct(args.rss_model, args.rss_role, args.rss_images)
        save(args.output / f'rss-{args.rss_model}-{args.rss_role}-{args.rss_images}.json', {
            'model': args.rss_model, 'role': args.rss_role, 'images': args.rss_images, 'used_default_create': default,
            'before': before._asdict(), 'after': after._asdict(), 'rss_delta_bytes': after.rss - before.rss,
            'state': state(chain), 'prepare_seconds_descriptive_with_wrapper': elapsed, 'environment': env(),
            'scope': '独立新进程无照片；描述包装/构造后实际RSS和peak_wset，不作配对计时样本。'})


def worker(args, plan):
    libraries, directory = setup(plan, ('reference', 'previous', 'isolated', 'candidate'))
    frames, manifest = source(json.loads(checked(plan['photo_model_plan']).read_text(encoding='utf-8')))
    assert sha(frames) == plan['source_sha256']
    whole_work = np.empty_like(frames)
    expected = {(v['role'], v['images']): v['output_sha256'] for v in plan['photo_expected']}
    u8, doubles = ct.POINTER(ct.c_uint8), ct.POINTER(ct.c_double)
    records, cold_records = [], []
    for model in plan['model_orders'][args.worker]:
        paths, sides, path_array, side_array = arrays(plan['models'][model])
        for images in plan['image_orders'][args.worker]:
            inputs, work = frames[:images], whole_work[:images]
            src, dst = inputs.ctypes.data_as(u8), work.ctypes.data_as(u8)
            error = ct.create_string_buffer(1024)
            samples = {role: [] for role in libraries}
            keepers = {}
            try:
                for iteration in range(plan['cold_repeats'] * 2):
                    for role in plan['orders'][args.worker]:
                        library = libraries[role]
                        default = role == 'reference' or images in plan['default_images']
                        hint = None if default else images * 786432
                        work.fill(173)
                        handle, first = ct.c_void_p(), np.empty(1, np.float64)
                        first_pointer = first.ctypes.data_as(doubles)
                        out_handle = ct.byref(handle)
                        started = time.perf_counter_ns()
                        if default:
                            rc = library.dll.jshc_cc_create(path_array, side_array, 4, out_handle, error, len(error))
                        else:
                            rc = library.dll.jshc_cc_create_for_workload(path_array, side_array, 4, hint,
                                out_handle, error, len(error))
                        created = time.perf_counter_ns()
                        if rc:
                            raise RuntimeError(error.value.decode('utf-8', 'replace'))
                        rc = library.dll.jshc_cc_bench_to(handle, src, dst, inputs.nbytes, 1, 4, 1,
                            first_pointer, error, len(error))
                        ended = time.perf_counter_ns()
                        if rc:
                            library.dll.jshc_cc_destroy(handle)
                            raise RuntimeError(error.value.decode('utf-8', 'replace'))
                        actual = sha(work)
                        assert actual == expected[model, images]
                        samples[role].append({'prepare_seconds': (created - started) * 1e-9,
                            'first_outplace4_seconds': float(first[0]), 'create_to_first_wall_seconds': (ended - started) * 1e-9,
                            'actual_output_sha256': actual, 'used_default_create': default, 'expected_pixels': hint})
                        if iteration + 1 == plan['cold_repeats'] * 2:
                            chain = Chain.__new__(Chain)
                            chain.library, chain.handle = library, handle
                            keepers[role] = chain
                        else:
                            library.dll.jshc_cc_destroy(handle)
                for role in plan['orders'][args.worker]:
                    chain = keepers[role]
                    snapshot = state(chain)
                    assert bool(snapshot['direct']['enabled']) == expected_direct(model, role, images)
                    cold_records.append({'model': model, 'images': images, 'role': role,
                        'samples': samples[role][:plan['cold_repeats']], 'control': samples[role][plan['cold_repeats']:],
                        'state': snapshot, 'source_address': int(inputs.ctypes.data), 'work_address': int(work.ctypes.data)})

                    if images not in plan['hot_images']:
                        continue

                    def group(boundary, threads, repeats):
                        work.fill(173)
                        times, total = np.empty(repeats, np.float64), np.empty(repeats, np.float64)
                        fields = [chain.handle, src, dst, inputs.nbytes, 1, threads, repeats, times.ctypes.data_as(doubles)]
                        if boundary == 'apply':
                            rc = chain.library.dll.jshc_cc_bench(*fields, total.ctypes.data_as(doubles), error, len(error))
                        else:
                            rc = chain.library.dll.jshc_cc_bench_to(*fields, error, len(error))
                        assert rc == 0, error.value
                        actual = sha(work)
                        assert actual == expected[model, images]
                        row = {'seconds': times.tolist(), 'actual_output_sha256': actual}
                        if boundary == 'apply':
                            row['copy_apply_seconds'] = total.tolist()
                        return row

                    for threads in plan['thread_orders'][args.worker]:
                        for boundary in plan['boundary_orders'][args.worker]:
                            warm = group(boundary, threads, plan['warmup'])
                            measured = group(boundary, threads, plan['repeats'][str(images)])
                            control = group(boundary, threads, plan['repeats'][str(images)])
                            records.append({'model': model, 'images': images, 'role': role, 'threads': threads,
                                'boundary': boundary, 'source_address': int(inputs.ctypes.data),
                                'work_address': int(work.ctypes.data), 'warmup': warm, 'measured': measured, 'control': control})
                            save(args.output / f'worker{args.worker}-partial.json', {'records': records, 'cold_records': cold_records})
            finally:
                for chain in keepers.values():
                    chain.close()
    assert sha(frames) == plan['source_sha256']
    save(args.output / f'worker{args.worker}.json', {'records': records, 'cold_records': cold_records,
        'source_sha256': plan['source_sha256'], 'environment': env()})


def summarize(plan, workers):
    hot, cold = [], []
    for denominator in plan['denominators']:
        roles = (denominator, 'candidate')
        for model in plan['models']:
            for images in plan['images']:
                matched = [{r['role']: r for r in w['cold_records'] if
                    (r['model'], r['images']) == (model, images)} for w in workers]
                metrics = {}
                for key in ('prepare_seconds', 'first_outplace4_seconds', 'create_to_first_wall_seconds'):
                    values = {role: [st.median(v[key] for v in m[role]['samples']) for m in matched] for role in roles}
                    controls = [st.median(v[key] for v in m[role]['control']) / st.median(v[key] for v in m[role]['samples'])
                        for m in matched for role in roles]
                    metrics[key] = ratio_row(plan, values['candidate'], values[denominator], controls)
                    metrics[key]['milliseconds'] = {r: [v * 1000 for v in a] for r, a in values.items()}
                cold.append({'denominator': denominator, 'model': model, 'images': images, 'metrics': metrics})
                if images not in plan['hot_images']:
                    continue
                for threads in (1, 4):
                    for boundary in ('apply', 'outplace'):
                        matched = [{r['role']: r for r in w['records'] if
                            (r['model'], r['images'], r['threads'], r['boundary']) == (model, images, threads, boundary)} for w in workers]
                        values = {role: [st.median(m[role]['measured']['seconds']) for m in matched] for role in roles}
                        controls = [st.median(m[role]['control']['seconds']) / st.median(m[role]['measured']['seconds'])
                            for m in matched for role in roles]
                        row = ratio_row(plan, values['candidate'], values[denominator], controls)
                        row.update({'denominator': denominator, 'model': model, 'images': images, 'threads': threads,
                            'boundary': boundary, 'ms_per_image': {r: [v * 1000 / images for v in a] for r, a in values.items()}})
                        hot.append(row)
    return {'hot': hot, 'cold': cold}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--worker', type=int)
    p.add_argument('--rss-role', choices=('reference', 'previous', 'isolated', 'candidate'))
    p.add_argument('--rss-model', choices=('ordinary', 'anchor'))
    p.add_argument('--rss-images', type=int, choices=(1, 100))
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
        raise FileExistsError('99首次正式不覆盖或重选')
    a.output.mkdir(parents=True)
    save(a.output / 'executed-plan.json', plan)
    workers = []
    for i in range(4):
        subprocess.run([sys.executable, '-X', 'utf8', __file__, '--plan', str(a.plan), '--output', str(a.output), '--worker', str(i)], check=True)
        workers.append(json.loads((a.output / f'worker{i}.json').read_text(encoding='utf-8')))
        print('99四角色配对进程完成', i, flush=True)
    for model in plan['models']:
        for role in plan['libraries']:
            for images in (1, 100):
                subprocess.run([sys.executable, '-X', 'utf8', __file__, '--plan', str(a.plan), '--output', str(a.output),
                    '--rss-model', model, '--rss-role', role, '--rss-images', str(images)], check=True)
    result = summarize(plan, workers)
    result.update({'worker_sha256': [digest(a.output / f'worker{i}.json') for i in range(4)],
        'scope': '同场99/87、99/95与99/97独立冷热资格；不以97慢分母救87/95硬线，全部2112实际末组SHA/AA/16RSS保留。N1/10/100冷热均测，未重测86不授档。'})
    save(a.output / 'results.json', result)


if __name__ == '__main__':
    main()
