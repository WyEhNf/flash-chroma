"""96独立默认N1 U/P诊断草稿；未经复核/冻结不得执行。"""
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
from PIL import Image
from bench_p16_model_pair import checked
from bench_p16_palette_prepare import setup
from bench_p16_workload import ratio_row
from study_p16_direct_compile import save, digest, env
from verify_p16_workload import state
from outplace_support import bind_to
from p16_omp_policy_support import Control


def sha(array):
    return hashlib.sha256(memoryview(array).cast('B')).hexdigest()


def first_source(plan):
    photograph = json.loads(checked(plan['photo_model_plan']).read_text(encoding='utf-8'))
    manifest = json.loads(checked(photograph['manifest']).read_text(encoding='utf-8'))
    first = manifest['images'][0]['evaluation']
    path = Path(photograph['data_root']) / first['path']
    assert digest(path) == first['sha256']
    with Image.open(path) as image:
        value = np.asarray(image).copy()
    assert value.shape == (768, 1024, 3) and value.dtype == np.uint8 and value.flags.c_contiguous
    assert sha(value) == first['pixel_sha256'] == plan['first_source_sha256']
    return value


def worker(args, plan):
    libraries, directory = setup(plan, ('reference', 'previous', 'candidate'))
    for library in libraries.values():
        bind_to(library.dll)
    inputs = first_source(plan)
    work = np.empty_like(inputs)
    u8, doubles = ct.POINTER(ct.c_uint8), ct.POINTER(ct.c_double)
    src, dst = inputs.ctypes.data_as(u8), work.ctypes.data_as(u8)
    error = ct.create_string_buffer(1024)
    expected = {v['role']: v['output_sha256'] for v in plan['photo_expected'] if v['images'] == 1}
    records, prewarm, handles = [], [], {}
    control = None
    modules_before, modules_after = [], []
    pending = None
    result_path = args.output / f'worker{args.worker}-t{args.threads}.json'
    mode = plan['mode']
    setup_start = time.perf_counter_ns() if mode == 'performance' else None

    def snapshot():
        return {'worker': args.worker, 'threads': args.threads, 'mode': mode,
            'records': records, 'prewarm': prewarm, 'pending_case': pending, 'control': control.export() if control else None,
            'source_sha256': sha(inputs), 'source_address': int(inputs.ctypes.data), 'work_address': int(work.ctypes.data),
            'actual_libgomp_paths_before': modules_before, 'actual_libgomp_paths_after': modules_after}

    try:
        control = Control(plan, args.threads)
        modules_before = control.modules()
        for model in plan['model_orders'][args.worker]:
            rows = plan['models'][model]
            paths = [checked(v) for v in rows['models']]
            sides = [checked(v) if v else None for v in rows['sidecars']]
            for role in plan['orders'][args.worker]:
                chain = libraries[role].chain(paths, sides)  # 真默认create，全部policy前一次构造。
                handles[model, role] = chain
                work.fill(173)
                rc = chain.library.dll.jshc_cc_apply_to(chain.handle, src, dst, inputs.nbytes, 1, args.threads, error, len(error))
                assert rc == 0, error.value
                actual = sha(work)
                assert actual == expected[model]
                prewarm.append({'model': model, 'role': role, 'actual_output_sha256': actual,
                    'handle_address': int(chain.handle.value), 'state': state(chain)})
        control.initialize_pool()
        setup_wall = (time.perf_counter_ns() - setup_start) * 1e-9 if setup_start is not None else None
        for block, policy in enumerate(plan['policy_orders'][args.worker]):
            control.apply_policy(policy, f'block{block}_{policy}')
            for model in plan['model_orders'][args.worker]:
                for role in plan['orders'][args.worker]:
                    chain = handles[model, role]
                    for boundary in plan['boundary_orders'][args.worker]:
                        row = {'block': block, 'policy': policy, 'model': model, 'role': role,
                            'boundary': boundary, 'threads': args.threads, 'handle_address': int(chain.handle.value),
                            'source_address': int(inputs.ctypes.data), 'work_address': int(work.ctypes.data)}
                        pending = row
                        for phase in ('warmup', 'measured', 'control'):
                            row['active_phase'] = phase
                            repeats = plan['warmup'] if phase == 'warmup' else plan['repeats']
                            before = control.endpoint(f'b{block}_{model}_{role}_{boundary}_{phase}_before')
                            work.fill(173)
                            if mode == 'quality':
                                for _ in range(repeats):
                                    if boundary == 'apply':
                                        work[:] = inputs
                                        chain.apply(work, kernel='avx2', threads=args.threads)
                                    else:
                                        rc = chain.library.dll.jshc_cc_apply_to(chain.handle, src, dst,
                                            inputs.nbytes, 1, args.threads, error, len(error))
                                        assert rc == 0, error.value
                                group = {'seconds': [], 'quality_apply_calls': repeats}
                            else:
                                values, total = np.empty(repeats, np.float64), np.empty(repeats, np.float64)
                                fields = [chain.handle, src, dst, inputs.nbytes, 1, args.threads, repeats,
                                    values.ctypes.data_as(doubles)]
                                if boundary == 'apply':
                                    rc = chain.library.dll.jshc_cc_bench(*fields, total.ctypes.data_as(doubles), error, len(error))
                                else:
                                    rc = chain.library.dll.jshc_cc_bench_to(*fields, error, len(error))
                                assert rc == 0, error.value
                                group = {'seconds': values.tolist()}
                                if boundary == 'apply':
                                    group['copy_apply_seconds'] = total.tolist()
                            after = control.endpoint(f'b{block}_{model}_{role}_{boundary}_{phase}_after')
                            actual = sha(work)
                            group.update({'actual_output_sha256': actual, 'before_control_index': before, 'after_control_index': after})
                            row[phase] = group
                            assert actual == expected[model]
                        row.pop('active_phase')
                        records.append(row)
                        pending = None
                        save(args.output / f'worker{args.worker}-t{args.threads}-partial.json', snapshot())
        control.apply_policy('U', 'final_restore55')
        modules_after = control.modules()
        assert modules_before == modules_after and sha(inputs) == plan['first_source_sha256']
        result = snapshot()
        result.update({'setup_wall_seconds_descriptive': setup_wall, 'environment': env(),
            'function_addresses': {r: {name: int(ct.cast(getattr(l.dll, name), ct.c_void_p).value)
                for name in ('jshc_cc_bench', 'jshc_cc_bench_to')} for r, l in libraries.items()},
            'table_addresses': None, 'table_address_scope': '既有公共ABI不暴露内部cache/direct地址，不声称heap已控。'})
        save(result_path, result)
    except BaseException as failure:
        failed = snapshot()
        failed['failure'] = repr(failure)
        save(args.output / f'worker{args.worker}-t{args.threads}-failure.json', failed)
        # 任何helper非零/身份失败不再调用控制函数，直接结束本子进程。
        raise
    finally:
        for chain in handles.values():
            chain.close()


def median(row):
    return st.median(row['measured']['seconds'])


def aa(row):
    return st.median(row['control']['seconds']) / median(row)


def summarize(plan, workers):
    pairs, policies, interactions = [], [], []
    indexed = {(w['worker'], w['threads']): {(v['block'], v['model'], v['role'], v['boundary']): v
        for v in w['records']} for w in workers}
    for threads in (1, 4):
        for model in plan['models']:
            for boundary in ('apply', 'outplace'):
                for denominator in plan['denominators']:
                    for policy in ('U', 'P'):
                        numerator, divisor, controls = [], [], []
                        for worker in range(4):
                            for block, p in enumerate(plan['policy_orders'][worker]):
                                if p != policy:
                                    continue
                                rows = indexed[worker, threads]
                                a, b = rows[block, model, 'candidate', boundary], rows[block, model, denominator, boundary]
                                numerator.append(median(a));divisor.append(median(b));controls += [aa(a), aa(b)]
                        value = ratio_row(plan, numerator, divisor, controls)
                        value.update({'threads': threads, 'model': model, 'boundary': boundary,
                            'denominator': denominator, 'policy': policy, 'unit': 'worker0..3各两个同policy块，共8比，最劣不合并。'})
                        pairs.append(value)
                    ds, controls = [], []
                    for worker in range(4):
                        rows = indexed[worker, threads]
                        for blocks in ((0, 1), (2, 3)):
                            slots = {plan['policy_orders'][worker][b]: b for b in blocks}
                            c = {p: rows[slots[p], model, 'candidate', boundary] for p in ('U', 'P')}
                            d = {p: rows[slots[p], model, denominator, boundary] for p in ('U', 'P')}
                            ds.append((median(c['P']) / median(d['P'])) / (median(c['U']) / median(d['U'])))
                            controls += [aa(c['U']), aa(d['U']), aa(c['P']), aa(d['P'])]
                    valid = all(plan['control_min'] <= x <= plan['control_max'] for x in controls)
                    worker_values = [st.median(ds[2 * i:2 * i + 2]) for i in range(4)]
                    center = st.median(ds)
                    interactions.append({'threads': threads, 'model': model, 'boundary': boundary, 'denominator': denominator,
                        'ratios': ds, 'controls': controls, 'control_valid': valid, 'median_interaction': center,
                        'worker_medians': worker_values,
                        'supported_improvement': valid and center <= .90 and sum(x < 1 for x in worker_values) >= 3,
                        'supported_regression': valid and center >= 1.10 and sum(x > 1 for x in worker_values) >= 3})
                for role in ('reference', 'previous', 'candidate'):
                    numerator, divisor, controls = [], [], []
                    for worker in range(4):
                        rows = indexed[worker, threads]
                        for blocks in ((0, 1), (2, 3)):
                            slots = {plan['policy_orders'][worker][b]: b for b in blocks}
                            u, p = rows[slots['U'], model, role, boundary], rows[slots['P'], model, role, boundary]
                            numerator.append(median(p));divisor.append(median(u));controls += [aa(u), aa(p)]
                    value = ratio_row(plan, numerator, divisor, controls)
                    value.update({'threads': threads, 'model': model, 'boundary': boundary, 'role': role})
                    policies.append(value)
    aa_counts = {policy: {'passed': 0, 'total': 0} for policy in ('U', 'P')}
    for w in workers:
        for row in w['records']:
            q = aa_counts[row['policy']];q['total'] += 1
            q['passed'] += plan['control_min'] <= aa(row) <= plan['control_max']
    return {'role_pairs': pairs, 'policy_pairs': policies, 'interactions': interactions, 'aa_counts': aa_counts}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--worker', type=int)
    p.add_argument('--threads', type=int, choices=(1, 4))
    a = p.parse_args()
    plan = json.loads(a.plan.read_text(encoding='utf-8'))
    assert plan['mode'] in ('quality', 'performance') and digest(Path(__file__)) == plan['script_sha256']
    for v in plan['sources']:
        checked(v)
    checked(plan['helper_quality_proof'])
    if a.worker is not None:
        return worker(a, plan)
    if a.output.exists():
        raise FileExistsError('96独立单版不覆盖')
    a.output.mkdir(parents=True)
    save(a.output / 'executed-plan.json', plan)
    workers = []
    for item in plan['process_order']:
        i, t = item['worker'], item['threads']
        subprocess.run([sys.executable, '-X', 'utf8', __file__, '--plan', str(a.plan), '--output', str(a.output),
            '--worker', str(i), '--threads', str(t)], check=True)
        workers.append(json.loads((a.output / f'worker{i}-t{t}.json').read_text(encoding='utf-8')))
        print('96独立进程完整通过', i, t, flush=True)
    result = summarize(plan, workers) if plan['mode'] == 'performance' else {'quality_only': True, 'performance_calls': 0}
    result.update({'workers': plan['process_order'], 'raw_worker_sha256': [digest(a.output / f"worker{v['worker']}-t{v['threads']}.json")
        for v in plan['process_order']], 'actual_output_sha_checks': 1200,
        'scope': '独立默认N1热U/P控制诊断，setup描述性分列，无cold或旧资格恢复；全部失败保留。'})
    save(a.output / 'results.json', result)


if __name__ == '__main__':
    main()
