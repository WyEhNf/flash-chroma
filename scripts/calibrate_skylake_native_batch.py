"""同一65句柄的固定长批次A/A校准；原生逐轮计时，不产生优化成绩。"""
import argparse
import ctypes as ct
import hashlib
import math
import os
from pathlib import Path
import statistics
import zipfile
from skylake_server_support import ROOT, read, save, digest, checked, topology, environment, driver_bind, loaded
from verify_skylake_linux_stdlib import bind, create
from pinned_openmp_support import places, probe, state
from paged_table_support import direct_info, paged_info


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--policy', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不得覆盖或自动重试')
    p = read(args.policy)
    cpus = p['cpus']
    os.sched_setaffinity(0, cpus)
    os.environ.update(OMP_NUM_THREADS='1', OMP_DYNAMIC='FALSE', OMP_PROC_BIND='TRUE', OMP_PLACES=places(cpus))
    os.environ.pop('GOMP_CPU_AFFINITY', None)
    checked(p['script'])
    plan, build, full = (read(checked(p[k])) for k in ('plan', 'build', 'full'))
    assert full['pass'] and full['build_sha256'] == p['build']['sha256'] and build['plan_sha256'] == p['plan']['sha256']
    assert full['libraries']['candidate'] == p['library']
    assert p['pairs_per_thread'] == 4 and p['inner_repeats'] == {'1': 16, '4': 64}
    assert p['orders'] == [['A', 'B'], ['B', 'A'], ['B', 'A'], ['A', 'B']]
    sources = {n: digest(ROOT/n) for n in p['python_sources']}
    for name, sha in plan['source_sha256'].items():
        assert digest(ROOT/name) == sha, name
        sources[name] = sha
    sources[args.policy.resolve().relative_to(ROOT).as_posix()] = digest(args.policy)
    args.output.mkdir(parents=True)
    save(args.output/'run.json', {'purpose': __doc__, 'policy': p, 'source_sha256': sources,
        'environment': environment(cpus), 'topology_before_openmp': topology(cpus),
        'scope': '固定A/A校准；内层每轮memcpy后独立计时apply，均值包含实际映射中断，复制单列；仅每原生批次末尾独立SHA。'})
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(sources):
            z.write(ROOT/name, name)
    raw = checked(p['photos']).read_bytes()
    assert len(raw) == 235929600
    source = (ct.c_uint8*len(raw)).from_buffer_copy(raw)
    del raw
    n = len(source)
    guard = ct.create_string_buffer(n+32)
    ct.memset(guard, 0xa7, len(guard))
    work = ct.cast(ct.addressof(guard)+16, ct.POINTER(ct.c_uint8))
    src = ct.cast(source, ct.POINTER(ct.c_uint8))
    def check_output():
        assert bytes(guard[:16]) == bytes([0xa7])*16 and bytes(guard[n+16:n+32]) == bytes([0xa7])*16
        assert hashlib.sha256(memoryview(guard).cast('B')[16:n+16]).hexdigest() == p['expected_output_sha256']
    d = bind(checked(p['library']))
    assert d.jshc_cc_revision() == 65 and d.jshc_cc_capabilities() == 7
    f = d.jshc_cc_bench
    f.argtypes = [ct.c_void_p, ct.POINTER(ct.c_uint8), ct.POINTER(ct.c_uint8), ct.c_size_t, ct.c_int, ct.c_int,
        ct.c_size_t, ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_char), ct.c_size_t]
    f.restype = ct.c_int
    driver = driver_bind(checked(p['driver']))
    probe(driver, 4, cpus)
    models = [checked(plan['fixed_inputs']['base']), *[checked(x) for x in plan['suffix_models']]]
    h = create(d, models, [checked(plan['fixed_inputs']['sidecar']), None, None, None])
    error = ct.create_string_buffer(1024)
    records = []
    try:
        before = {'paged_info': paged_info(d, h), 'direct_info': direct_info(d, h)}
        save(args.output/'handle-state-before.json', before)
        assert before['direct_info']['enabled'] == 1 and before['direct_info']['format'] == 9
        assert before['paged_info']['fully_huge'] and before['paged_info']['bytes'] == 2**24
        for pair, order in enumerate(p['orders']):
            for threads in p['thread_orders'][pair]:
                team = probe(driver, threads, cpus)
                repeats = p['inner_repeats'][str(threads)]
                for label in order:
                    ct.memmove(work, src, n)
                    if d.jshc_cc_apply(h, work, n, 1, threads, error, len(error)):
                        raise RuntimeError(error.value.decode())
                    check_output()
                    a, c = (ct.c_double*repeats)(), (ct.c_double*repeats)()
                    if f(h, src, work, n, 1, threads, repeats, a, c, error, len(error)):
                        raise RuntimeError(error.value.decode())
                    check_output()
                    assert all(math.isfinite(x) and 0 < x <= y for x, y in zip(a, c))
                    r = {'pair': pair, 'label': label, 'threads': threads, 'actual_team': team,
                        'inner_repeats': repeats, 'apply_seconds': list(a), 'copy_apply_seconds': list(c),
                        'mean_apply_seconds': statistics.mean(a), 'median_apply_seconds': statistics.median(a),
                        'mean_copy_apply_seconds': statistics.mean(c), 'tasks_after': state(cpus),
                        'batch_final_output_sha256': p['expected_output_sha256']}
                    records.append(r)
                    save(args.output/f'sample-{threads}-{pair}-{label}.json', r)
            print('完成原生长批次负对照配对', pair, flush=True)
        after = {'paged_info': paged_info(d, h), 'direct_info': direct_info(d, h)}
        save(args.output/'handle-state-after.json', after)
        assert after['paged_info']['fully_huge'] and after['paged_info']['bytes'] == 2**24
    finally:
        d.jshc_cc_destroy(h)
    summary = []
    for threads in (1, 4):
        values = []
        for pair in range(4):
            by = {r['label']: r for r in records if r['pair'] == pair and r['threads'] == threads}
            values.append(by['B']['mean_apply_seconds']/by['A']['mean_apply_seconds'])
        summary.append({'threads': threads, 'paired_mean_apply_ratios_B_over_A': values,
            'median_ratio': statistics.median(values), 'geometric_mean_ratio': math.exp(statistics.mean(math.log(x) for x in values)),
            'minimum': min(values), 'maximum': max(values), 'outside_three_percent_pairs': sum(x < 1/1.03 or x > 1.03 for x in values)})
    assert len(records) == 16 and hashlib.sha256(source).hexdigest() == p['photos']['sha256']
    for name, sha in sources.items():
        assert digest(ROOT/name) == sha, name
    save(args.output/'results.json', {'calibration_completed': True, 'same_library_and_handle': True,
        'summary': summary, 'native_batch_calls': 16, 'inner_apply_rounds': 640, 'warmup_calls': 16,
        'batch_final_sha_checks': 16, 'per_inner_round_independent_sha': False,
        'loaded_libraries': loaded([p['library'], p['driver']]),
        'limitation': '同进程固定次数描述性A/A，非独立宿主试验，无锁频/控温，不作为对23优化成绩或重评旧候选。'})
    print('原生长批次校准完成', summary, flush=True)


if __name__ == '__main__':
    main()
