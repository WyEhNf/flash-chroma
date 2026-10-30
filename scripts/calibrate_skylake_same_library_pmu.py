"""固定同一65句柄的A/A负对照，量化本机筛查波动，不生成优化吞吐成绩。"""
import argparse
import ctypes as ct
import hashlib
import math
import os
from pathlib import Path
import statistics
import time
import zipfile
from skylake_server_support import ROOT, read, save, digest, checked, topology, environment
from skylake_server_support import driver_bind, loaded
from verify_skylake_linux_stdlib import bind, create
from pinned_openmp_support import places, probe, state
from paged_table_support import direct_info, paged_info
from profile_skylake_chroma_batch4_pmu import Group, NAMES


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--policy', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不得覆盖负对照结果或自动重试')
    policy = read(args.policy)
    cpus = policy['cpus']
    os.sched_setaffinity(0, cpus)
    os.environ.update(OMP_NUM_THREADS='1', OMP_DYNAMIC='FALSE', OMP_PROC_BIND='TRUE', OMP_PLACES=places(cpus))
    os.environ.pop('GOMP_CPU_AFFINITY', None)
    assert read(checked(policy['probe']))['available']
    checked(policy['script'])
    plan = read(checked(policy['plan']))
    full = read(checked(policy['full']))
    build = read(checked(policy['build']))
    assert full['pass'] and full['build_sha256'] == policy['build']['sha256']
    assert build['plan_sha256'] == policy['plan']['sha256']
    assert full['libraries']['candidate'] == policy['library']
    assert policy['pairs_per_thread'] == 16 and policy['orders'] == [['A', 'B'], ['B', 'A'], ['B', 'A'], ['A', 'B']]
    sources = {k: digest(ROOT/k) for k in policy['python_sources']}
    for name, sha in plan['source_sha256'].items():
        assert digest(ROOT/name) == sha, name
        sources[name] = sha
    sources[args.policy.resolve().relative_to(ROOT).as_posix()] = digest(args.policy)
    args.output.mkdir(parents=True)
    save(args.output/'run.json', {'purpose': __doc__, 'policy': policy, 'source_sha256': sources,
        'environment': environment(cpus), 'topology_before_openmp': topology(cpus),
        'scope': '同一已验65库和同一句柄；A/B仅标签，不是优化对照，不重评旧失败候选。'})
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(sources):
            z.write(ROOT/name, name)
    source_bytes = checked(policy['photos']).read_bytes()
    assert len(source_bytes) == 235929600
    source = (ct.c_uint8*len(source_bytes)).from_buffer_copy(source_bytes)
    del source_bytes
    n = len(source)
    pixels = n//3
    guard = ct.create_string_buffer(n+32)
    ct.memset(guard, 0xa7, len(guard))
    work = ct.cast(ct.addressof(guard)+16, ct.POINTER(ct.c_uint8))
    src = ct.cast(source, ct.POINTER(ct.c_uint8))
    def output_sha():
        assert bytes(guard[:16]) == bytes([0xa7])*16 and bytes(guard[n+16:n+32]) == bytes([0xa7])*16
        return hashlib.sha256(memoryview(guard).cast('B')[16:n+16]).hexdigest()
    d = bind(checked(policy['library']))
    assert d.jshc_cc_revision() == 65 and d.jshc_cc_capabilities() == 7
    driver = driver_bind(checked(policy['driver']))
    probe(driver, 4, cpus)
    models = [checked(plan['fixed_inputs']['base']), *[checked(x) for x in plan['suffix_models']]]
    sides = [checked(plan['fixed_inputs']['sidecar']), None, None, None]
    h = create(d, models, sides)
    error = ct.create_string_buffer(1024)
    records = []
    try:
        pages = paged_info(d, h)
        direct = direct_info(d, h)
        save(args.output/'handle-state-before.json', {'paged_info': pages, 'direct_info': direct})
        assert direct['format'] == 9 and direct['enabled'] == 1 and pages['bytes'] == 2**24 and pages['fully_huge']
        for block in range(4):
            for threads in policy['thread_orders'][block]:
                team = probe(driver, threads, cpus)
                for pair in range(4):
                    pair_id = block*4+pair
                    for label in policy['orders'][pair]:
                        ct.memmove(work, src, n)
                        if d.jshc_cc_apply(h, work, n, 1, threads, error, len(error)):
                            raise RuntimeError(error.value.decode())
                        assert output_sha() == policy['expected_output_sha256']
                        ct.memmove(work, src, n)
                        tasks = state(cpus)
                        chosen = [r for r in tasks if r['allowed_cpus'][0] in cpus[:threads]]
                        assert len(chosen) == threads
                        groups = []
                        try:
                            for task in chosen:
                                groups.append(Group(task['tid']))
                            for group in groups:
                                group.enable()
                            start = time.perf_counter_ns()
                            status = d.jshc_cc_apply(h, work, n, 1, threads, error, len(error))
                            elapsed = time.perf_counter_ns()-start
                            for group in groups:
                                group.disable()
                            counters = [group.read() for group in groups]
                        finally:
                            for group in groups:
                                group.close()
                        if status:
                            raise RuntimeError(error.value.decode())
                        assert output_sha() == policy['expected_output_sha256']
                        sums = {name: sum(r['counts'][name] for r in counters) for name in NAMES}
                        record = {'threads': threads, 'pair': pair_id, 'label': label, 'order': policy['orders'][pair],
                            'actual_team': team, 'thread_counters': counters, 'sum_counts': sums,
                            'cycles_per_pixel': sums['cycles']/pixels, 'instructions_per_pixel': sums['instructions']/pixels,
                            'apply_wall_seconds': elapsed/1e9, 'tasks_before': tasks, 'tasks_after': state(cpus),
                            'output_sha256': policy['expected_output_sha256'],
                            'multiplexing_acceptable': all(r['running_fraction'] is not None and r['running_fraction'] >= .99 for r in counters)}
                        records.append(record)
                        save(args.output/f'sample-{threads}-{pair_id:02d}-{label}.json', record)
                print('完成同库负对照块', block, threads, flush=True)
        assert len(records) == 64
        pages_after = paged_info(d, h)
        save(args.output/'handle-state-after.json', {'paged_info': pages_after, 'direct_info': direct_info(d, h)})
        assert pages_after['fully_huge'] and pages_after['bytes'] == 2**24
    finally:
        d.jshc_cc_destroy(h)
    summary = []
    for threads in (1, 4):
        ratios = {key: [] for key in ('cycles_per_pixel', 'apply_wall_seconds')}
        for pair in range(16):
            by = {r['label']: r for r in records if r['threads'] == threads and r['pair'] == pair}
            assert set(by) == {'A', 'B'}
            for key in ratios:
                ratios[key].append(by['B'][key]/by['A'][key])
        row = {'threads': threads}
        for key, values in ratios.items():
            row[key] = {'paired_ratios_B_over_A': values, 'median_ratio': statistics.median(values),
                'geometric_mean_ratio': math.exp(statistics.mean(math.log(x) for x in values)),
                'minimum': min(values), 'maximum': max(values),
                'outside_three_percent_pairs': sum(x < 1/1.03 or x > 1.03 for x in values)}
        summary.append(row)
    assert hashlib.sha256(source).hexdigest() == policy['photos']['sha256']
    for name, sha in sources.items():
        assert digest(ROOT/name) == sha, name
    save(args.output/'results.json', {'calibration_completed': True, 'same_library_and_handle': True,
        'summary': summary, 'counted_calls': 64, 'warmup_calls': 64,
        'all_multiplexing_acceptable': all(r['multiplexing_acceptable'] for r in records),
        'loaded_libraries': loaded([policy['library'], policy['driver']]),
        'limitation': '固定次数的同进程描述性负对照；非独立宿主试验，无锁频/控温；不能由A/A范围推导特定新候选收益或重写旧失败。'})
    print('同库负对照完成', summary, flush=True)


if __name__ == '__main__':
    main()
