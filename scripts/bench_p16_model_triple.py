"""同87库固定三模型配对；原生计时和调用者持有的实际末轮输出逐组留证。"""
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
import numpy as np
import psutil
from bench_p16_model_pair import checked, source, native_create
from study_p16_direct_compile import Library, save, digest, env
from palette_support import info as palette_info
from suffix_cache_support import cache_info
from direct16_support import info as direct_info
from domain_cache_support import info as domain_info


def array_sha(a):
    return hashlib.sha256(memoryview(a).cast('B')).hexdigest()


def preflight(args, plan):
    if args.output.exists():
        raise FileExistsError('保留已有目录')
    args.output.mkdir(parents=True)
    frames, manifest = source(plan)
    expected = {}
    for name, role in plan['roles'].items():
        for row in role['models'] + [v for v in role['sidecars'] if v]:
            checked(row)
        cube = np.memmap(checked(role['oracle']), dtype=np.uint8, mode='r', shape=(1 << 24, 3))
        whole = hashlib.sha256()
        per_image = []
        for frame in frames:
            a = frame.astype(np.uint32)
            code = (a[:, :, 0] << 16) | (a[:, :, 1] << 8) | a[:, :, 2]
            prediction = cube[code]
            whole.update(memoryview(prediction).cast('B'))
            per_image.append(array_sha(prediction))
        expected[name] = {'whole_sha256': whole.hexdigest(), 'per_image_sha256': per_image}
        if role.get('acceptance'):
            acceptance = json.loads(checked(role['acceptance']).read_text(encoding='utf-8'))
            result = acceptance['variants']['candidate']
            assert acceptance['library_sha256'] == plan['library']['sha256']
            assert result['full_native_byte_mismatches'] == result['photo_native_byte_mismatches'] == 0
            assert result['sha256']['oracle'] == role['oracle']['sha256']
            assert per_image == [row['prediction_sha256'] for row in result['photos']['per_image']]
        del cube
    save(args.output / 'preflight.json', {
        'oracle_photo_outputs': expected, 'source_sha256': array_sha(frames),
        'scope': '固定全域独立oracle按100张源图索引；既有完整87验收以文件与DLL身份绑定，未重复全域质量拟合。'})
    save(args.output / 'executed-plan.json', plan)
    print('三模型oracle、百图预期及既有87验收身份通过', flush=True)


def worker(args, plan):
    psutil.Process().cpu_affinity(plan['cpus'])
    dll_directory = os.add_dll_directory('E:/mingw64/bin') if os.name == 'nt' else None
    library = Library(checked(plan['library']), plan['library']['sha256'])
    assert library.revision == 87
    pre = json.loads((args.output / 'preflight.json').read_text(encoding='utf-8'))
    frames, _ = source(plan)
    source_sha = array_sha(frames)
    assert source_sha == pre['source_sha256']
    work = np.empty_like(frames)
    work.fill(0)
    u8 = ct.POINTER(ct.c_uint8)
    doubles = ct.POINTER(ct.c_double)
    common = [ct.c_void_p, u8, u8, ct.c_size_t, ct.c_int, ct.c_int, ct.c_size_t]
    inplace = library.dll.jshc_cc_bench
    inplace.argtypes = common + [doubles, doubles, ct.POINTER(ct.c_char), ct.c_size_t]
    inplace.restype = ct.c_int
    separate = library.dll.jshc_cc_bench_to
    separate.argtypes = common + [doubles, ct.POINTER(ct.c_char), ct.c_size_t]
    separate.restype = ct.c_int
    error = ct.create_string_buffer(1024)
    records = []
    constructions = []
    for name in plan['orders'][args.worker]:
        chain, prepared = native_create(library, plan['roles'][name])
        expected = pre['oracle_photo_outputs'][name]['whole_sha256']
        with chain:
            direct = direct_info(chain)
            assert direct['enabled'] and direct['format'] == 9
            state = {'cache': cache_info(chain), 'domain': domain_info(chain),
                     'palette': palette_info(chain), 'direct': direct, 'model_bytes': chain.model_bytes}

            def run(boundary, repeats, threads):
                # 先毒化而后让原生写入；SHA和工作区分配不计入映射，末轮work始终属于本调用者。
                work.fill(173)
                seconds = np.empty(repeats, np.float64)
                total = np.empty(repeats, np.float64)
                fields = [chain.handle, frames.ctypes.data_as(u8), work.ctypes.data_as(u8),
                          frames.nbytes, 1, threads, repeats, seconds.ctypes.data_as(doubles)]
                if boundary == 'apply':
                    rc = inplace(*fields, total.ctypes.data_as(doubles), error, len(error))
                else:
                    rc = separate(*fields, error, len(error))
                if rc:
                    raise RuntimeError(error.value.decode('utf-8', 'replace'))
                actual_sha = array_sha(work)
                assert actual_sha == expected, (name, boundary, threads, actual_sha)
                result = {'seconds': seconds.tolist(), 'actual_output_sha256': actual_sha}
                if boundary == 'apply':
                    result['copy_apply_seconds'] = total.tolist()
                return result

            first = run('outplace', 1, 4)
            constructions.append({'role': name, 'prepare_seconds': prepared,
                'first_outplace4': first, 'prepare_plus_first100_seconds': prepared + first['seconds'][0],
                'state': state})
            for threads in plan['thread_orders'][args.worker]:
                for boundary in plan['boundary_orders'][args.worker]:
                    warm = run(boundary, plan['warmup'], threads)
                    measured = run(boundary, plan['repeats'], threads)
                    control = run(boundary, plan['repeats'], threads)
                    records.append({'role': name, 'threads': threads, 'boundary': boundary,
                        'warmup': warm, 'measured': measured, 'control': control})
                    save(args.output / f'worker{args.worker}-partial.json', {
                        'records': records, 'constructions': constructions, 'source_sha256': source_sha})
    assert array_sha(frames) == source_sha
    save(args.output / f'worker{args.worker}.json', {'records': records, 'constructions': constructions,
        'source_sha256': source_sha, 'environment': env(),
        'scope': '末轮实际caller-owned work逐组SHA；纯apply不含前置memcpy，copy_apply含；真分离直接读source写work。'})


def summarize(plan, workers):
    pairs = [('anchor', 'incumbent'), ('anchor', 'candidate'), ('incumbent', 'candidate')]
    gates = plan['gates']
    summaries = []
    for before, after in pairs:
        rows = []
        retained = []
        controls = []
        for threads in (1, 4):
            for boundary in ('apply', 'outplace'):
                matched = [{r['role']: r for r in w['records']
                    if r['threads'] == threads and r['boundary'] == boundary} for w in workers]
                ratios = [st.median(m[after]['measured']['seconds']) /
                          st.median(m[before]['measured']['seconds']) for m in matched]
                aa = {n: [st.median(m[n]['control']['seconds']) /
                          st.median(m[n]['measured']['seconds']) for m in matched] for n in (before, after)}
                controls.extend(v for values in aa.values() for v in values)
                retained.extend(1 / v for v in ratios)
                rows.append({'threads': threads, 'boundary': boundary, 'time_ratios': ratios,
                    'median_time_ratio': st.median(ratios), 'worst_throughput_retained': 1 / max(ratios),
                    'controls': aa, 'ms_per_image': {n: [st.median(m[n]['measured']['seconds']) * 10
                        for m in matched] for n in (before, after)}})
        valid = all(gates['control_any_min'] <= v <= gates['control_any_max'] for v in controls)
        constructions = [{r['role']: r for r in w['constructions']} for w in workers]
        cold = {k: [m[after][k] / m[before][k] for m in constructions]
                for k in ('prepare_seconds', 'prepare_plus_first100_seconds')}
        summaries.append({'before': before, 'after': after, 'control_valid': valid,
            'summary': rows, 'construction_time_ratios': cold,
            'worst_throughput_retained': min(retained),
            'grades': {str(g): valid and min(retained) >= g / 100 for g in plan['grades']},
            'no_obvious_slowdown': valid and all(r['median_time_ratio'] <= gates['no_obvious_median_time_ratio_max']
                and max(r['time_ratios']) <= gates['no_obvious_any_time_ratio_max'] for r in rows)})
    return summaries


def measure(args, plan):
    if any(args.output.glob('worker*.json')):
        raise FileExistsError('已有性能证据，不覆盖或重选')
    workers = []
    for i in range(4):
        subprocess.run([sys.executable, '-X', 'utf8', __file__, '--plan', str(args.plan), '--output',
            str(args.output), '--mode', 'measure', '--worker', str(i)], check=True)
        workers.append(json.loads((args.output / f'worker{i}.json').read_text(encoding='utf-8')))
        print('完成三模型配对进程', i, flush=True)
    result = {'comparisons': summarize(plan, workers),
        'worker_sha256': [digest(args.output / f'worker{i}.json') for i in range(4)],
        'scope': '三固定模型同87/同场；初次prepare含底层文件读取与原生校验，源图预载预触及hash在外；首次百图与稳态分别报告。'}
    save(args.output / 'results.json', result)
    for row in result['comparisons']:
        print(row['before'], '→', row['after'], '控制', row['control_valid'], '最劣吞吐保留',
            row['worst_throughput_retained'], '无明显退化', row['no_obvious_slowdown'], flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--mode', choices=('preflight', 'measure'), required=True)
    p.add_argument('--worker', type=int)
    args = p.parse_args()
    plan = json.loads(args.plan.read_text(encoding='utf-8'))
    assert digest(Path(__file__)) == plan['script_sha256']
    for row in plan['execution_dependencies']:
        checked(row)
    if args.worker is not None:
        return worker(args, plan)
    return (preflight if args.mode == 'preflight' else measure)(args, plan)


if __name__ == '__main__':
    main()
