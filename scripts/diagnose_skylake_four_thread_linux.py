"""65的单/四线程六事件诊断：照片原地、固定灰色原地及照片分离输出；不作吞吐验收。"""
import argparse
import ctypes as ct
import fcntl
import hashlib
import os
from pathlib import Path
import platform
import struct
import zipfile

from skylake_server_support import ROOT, read, save, digest, checked, topology, environment, driver_bind, loaded
from verify_skylake_linux_stdlib import bind, create
from outplace_support import bind_to
from pinned_openmp_support import places, probe, state
from paged_table_support import direct_info, paged_info
from quiet_host_support import require_quiet
from lookup_pmu_support import EVENTS
from probe_skylake_pmu import Attr


CASES = [('photo_inplace', 1), ('photo_inplace', 4), ('uniform_inplace', 4),
         ('uniform_inplace', 1), ('photo_outplace', 1), ('photo_outplace', 4)]
NAMES = [name for name, _ in EVENTS]


class ThreadGroup:
    """沿用既有六事件及pinned/exclude标志，唯一变化是显式绑定目标TID。"""
    def __init__(self, tid):
        self.tid, self.fds = tid, []
        libc = ct.CDLL(None, use_errno=True)
        call = libc.syscall
        call.restype = ct.c_long
        call.argtypes = [ct.c_long, ct.c_void_p, ct.c_int, ct.c_int, ct.c_int, ct.c_ulong]
        try:
            for name, config in EVENTS:
                attr = Attr()
                attr.type, attr.size, attr.config, attr.read_format = 4, ct.sizeof(attr), config, 11
                attr.flags = 32 | 64 | (5 if not self.fds else 0)
                fd = call(298, ct.byref(attr), tid, -1, self.fds[0] if self.fds else -1, 8)
                if fd < 0:
                    raise OSError(ct.get_errno(), f'TID {tid}六事件组不可用：{name}')
                self.fds.append(fd)
        except BaseException:
            self.close()
            raise

    def enable(self):
        fcntl.ioctl(self.fds[0], 0x2403, 1)
        fcntl.ioctl(self.fds[0], 0x2400, 1)

    def disable(self):
        fcntl.ioctl(self.fds[0], 0x2401, 1)

    def read(self):
        raw = os.read(self.fds[0], 4096)
        result = {'tid': self.tid, 'raw_group_read_hex': raw.hex()}
        if len(raw) != 9*8:
            result['decode_error'] = '六事件组读取长度不符'
            return result
        values = struct.unpack('<9Q', raw)
        if values[0] != 6:
            result['decode_error'] = '六事件组事件数不符'
            return result
        result.update(time_enabled_ns=values[1], time_running_ns=values[2],
            counts=dict(zip(NAMES, values[3:])),
            running_fraction=values[2]/values[1] if values[1] else None)
        return result

    def close(self):
        for fd in self.fds:
            os.close(fd)
        self.fds = []


def metrics(counts, pixels):
    cycles = counts['cycles']
    return {'per_nominal_pixel': {k: v/pixels for k, v in counts.items()} if pixels else None,
        'oldest_load_wait_cycle_fraction': counts['oldest_load_not_complete']/cycles if cycles else None,
        'oldest_pending_cycle_fraction': counts['oldest_not_complete']/cycles if cycles else None,
        'instructions_per_cycle': counts['instructions']/cycles if cycles else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--policy', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if platform.system() != 'Linux' or platform.machine().lower() not in ('x86_64', 'amd64'):
        raise ValueError('只允许实际Linux x86_64；原始事件不适用于Skylake')
    if args.output.exists():
        raise ValueError('不得覆盖诊断或自动重试旧结果')
    policy = read(args.policy)
    cpus = policy['affinity_cpus']
    if (cpus != [0, 2, 4, 6] or policy['events'] != [list(x) for x in EVENTS]
            or policy['cases'] != [{'case': name, 'threads': threads} for name, threads in CASES]
            or policy['revision'] != 65 or policy['warmup_per_case'] != 1
            or policy['count_per_case'] != 1 or policy['min_running_fraction'] != .99
            or policy['pin_all_six'] is not True or policy['exclude_kernel_hypervisor'] is not True
            or policy['wallclock_timing_calls'] != 0 or ct.sizeof(Attr) != 128):
        raise ValueError('诊断案例、事件或固定次数不同')
    if policy['source_hashes'].get(Path(__file__).resolve().relative_to(ROOT).as_posix()) != digest(__file__):
        raise ValueError('策略未绑定实际脚本')
    if not read(checked(policy['probe']))['available']:
        raise ValueError('既有六事件可用性探测未通过')
    if os.environ.get('JSHC_CHANNEL_FORCE_LINEAR_INDEX') is not None:
        raise ValueError('不接受外部强制布局设置')
    plan, build, full = [read(checked(policy[key])) for key in ('plan', 'build', 'full')]
    validation = read(checked(policy['validation']))
    if (not full['pass'] or full['build_sha256'] != policy['build']['sha256']
            or full['libraries'] != build['libraries'] or build['plan_sha256'] != policy['plan']['sha256']
            or build['source_sha256'] != plan['source_sha256']
            or build['revisions'] != {'reference': 23, 'candidate': 65}
            or build['libraries']['candidate']['sha256'] != policy['library']['sha256']
            or validation['plan_sha256'] != policy['plan']['sha256']
            or validation['full_result']['sha256'] != policy['full']['sha256']):
        raise ValueError('65构建、全域、验证单或计划身份不同')
    checked(validation['full_result'])
    checked(build['libraries']['candidate'])
    checked(policy['library'])
    checked(policy['pinning_probe'])
    sources = {**plan['source_sha256'], **validation['source_sha256'], **policy['source_hashes']}
    for key in ('plan', 'build', 'full', 'validation', 'probe', 'pinning_probe'):
        path = checked(policy[key]).resolve()
        sources[path.relative_to(ROOT).as_posix()] = digest(path)
    sources[args.policy.resolve().relative_to(ROOT).as_posix()] = digest(args.policy)
    for name, sha in sources.items():
        if digest(ROOT/name) != sha:
            raise ValueError('冻结源码或身份文件不同：'+name)
    os.sched_setaffinity(0, cpus)
    top = topology(cpus)
    os.environ.update(OMP_NUM_THREADS='1', OMP_DYNAMIC='FALSE', OMP_PROC_BIND='TRUE', OMP_PLACES=places(cpus))
    os.environ.pop('GOMP_CPU_AFFINITY', None)
    env = environment(cpus)
    for row in env['selected_cpu_details'].values():
        if int(row['cpu family']) != policy['cpu_family'] or int(row['model']) != policy['cpu_model']:
            raise ValueError('当前CPU不是冻结Zen4事件对应的family/model')
    args.output.mkdir(parents=True)
    result = {'pass': False, 'purpose': __doc__, 'records': [], 'warmup_calls': 0, 'counted_calls': 0,
        'wallclock_calls': 0, 'threefold_goal_completed': False, 'automatic_retry': False,
        'policy_sha256': digest(args.policy), 'limits': policy['limitations']}
    save(args.output/'run.json', {'purpose': __doc__, 'policy': policy, 'source_sha256': sources,
        'environment': env, 'topology_before_openmp': top, 'candidate_wallclock_timing_calls': 0})
    with zipfile.ZipFile(args.output/'measured-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(sources):
            archive.write(ROOT/name, name)
    handle, d = None, None
    try:
        quiet = policy['quiet_protocol']
        require_quiet(quiet, cpus, args.output, 'quiet-parent', quiet['minimum_parent_settle_seconds'])
        d = bind(checked(policy['library']))
        if d.jshc_cc_revision() != 65 or d.jshc_cc_abi_version() != 1 or d.jshc_cc_capabilities() != 7:
            raise ValueError('实际65库ABI、后端或修订不同')
        to = bind_to(d)
        driver = driver_bind(checked(policy['driver']))
        result['initial_team'] = probe(driver, 4, cpus)
        result['loaded_libraries'] = loaded([policy['library'], policy['driver']])
        raw = checked(policy['photos']).read_bytes()
        n, pixels = len(raw), len(raw)//3
        if n != 235929600 or pixels % (65536*4):
            raise ValueError('固定照片长度或四线程均分条件不同')
        photo = (ct.c_uint8*n).from_buffer_copy(raw)
        del raw
        uniform = (ct.c_uint8*n).from_buffer_copy(bytes(policy['uniform_rgb'])*pixels)
        if hashlib.sha256(uniform).hexdigest() != policy['uniform_source_sha256']:
            raise ValueError('固定灰色输入SHA不同')
        storage = ct.create_string_buffer(n+128)
        base = ct.addressof(storage)
        addr = (base+63)&~63
        if addr == base:
            addr += 64
        offset = addr-base
        if offset < 1 or addr+n >= base+len(storage):
            raise ValueError('对齐目标没有前后保护空间')
        target = ct.cast(addr, ct.POINTER(ct.c_uint8))
        error = ct.create_string_buffer(1024)
        models = [checked(plan['fixed_inputs']['base']), *[checked(x) for x in plan['suffix_models']]]
        sides = [checked(plan['fixed_inputs']['sidecar']), None, None, None]
        handle = create(d, models, sides)
        result['handle_creation_count'] = 1

        def pages_snapshot(label):
            snapshot = {'direct_info': direct_info(d, handle), 'paged_info': paged_info(d, handle),
                'model_accounting_bytes': d.jshc_cc_model_bytes(handle)}
            save(args.output/(label+'-table.json'), snapshot)
            ds, pg = snapshot['direct_info'], snapshot['paged_info']
            if (ds['enabled'] != 1 or ds['format'] != 9 or ds['entries'] != 2**22
                    or ds['table_capacity_bytes'] != 2**24 or pg['bytes'] != 2**24
                    or pg['smaps']['mapping_bytes'] != 2**24 or not pg['fully_huge'] or not pg['aligned_2m']):
                raise ValueError('65精确16MiB VMA及全THP条件失败；原诊断已保存')
            return snapshot

        result['table_before'] = pages_snapshot('before')
        for case_index, (label, threads) in enumerate(CASES):
            key = f'case{case_index}-{label}-{threads}'
            path = args.output/(key+'.json')
            require_quiet(quiet, cpus, args.output, 'quiet-'+key, 0)
            team = probe(driver, threads, cpus)
            src = uniform if label == 'uniform_inplace' else photo
            expected = policy['uniform_output_sha256'] if label == 'uniform_inplace' else policy['photo_output_sha256']
            record = {'case': label, 'requested_threads': threads, 'actual_team': team,
                'pixels': pixels, 'runtime_block_pixels': 65536, 'runtime_blocks': pixels//65536,
                'nominal_assignment_source': '冻结65的schedule(static)，1200块被1/4个参与线程整除；非线程内测量',
                'counter_window': '逐TID启用后的一次公开API调用；包括调度、barrier和收尾自旋，未拆出纯像素循环',
                'output_sha256_expected': expected, 'table_before': pages_snapshot(key+'-before')}
            save(path, record)

            def reset():
                ct.memset(storage, 0xa7, len(storage))
                ct.memmove(target, src, n)

            def call():
                if label == 'photo_outplace':
                    return to(handle, ct.cast(src, ct.POINTER(ct.c_uint8)), target, n, 1, threads, error, len(error))
                return d.jshc_cc_apply(handle, target, n, 1, threads, error, len(error))

            def check():
                view = memoryview(storage).cast('B')
                if bytes(view[:offset]) != b'\xa7'*offset or bytes(view[offset+n:]) != b'\xa7'*(len(storage)-offset-n):
                    raise AssertionError('输入输出保护区被改写')
                sha = hashlib.sha256(view[offset:offset+n]).hexdigest()
                if sha != expected:
                    raise AssertionError('完整100图或灰色输出SHA不同')
                if (hashlib.sha256(photo).hexdigest() != policy['photos']['sha256']
                        or hashlib.sha256(uniform).hexdigest() != policy['uniform_source_sha256']):
                    raise AssertionError('只读源被改写')
                return sha

            reset()
            status = call()
            result['warmup_calls'] += 1
            record['warmup_return_code'] = status
            save(path, record)
            if status:
                raise RuntimeError(error.value.decode('utf-8', errors='replace'))
            record['warmup_output_sha256'] = check()
            reset()
            before = state(cpus)
            if len(before) != 4 or len({x['allowed_cpus'][0] for x in before}) != 4:
                raise ValueError('实际TID与四个固定CPU不一一对应')
            record['tasks_before'] = before
            groups, enabled = [], []
            try:
                groups = []
                for task in before:
                    groups.append(ThreadGroup(task['tid']))
                # 主线程最后启用、最先关闭，减少其计入其他TID ioctl的额外工作。
                sequence = sorted(groups, key=lambda g: (g.tid == os.getpid(), g.tid))
                record['counter_enable_tid_order'] = [g.tid for g in sequence]
                record['counter_disable_tid_order'] = [g.tid for g in reversed(sequence)]
                save(path, record)
                for group in sequence:
                    group.enable()
                    enabled.append(group)
                status = call()
                for group in reversed(enabled):
                    group.disable()
                enabled.clear()
                result['counted_calls'] += 1
                record['native_return_code'] = status
                record['thread_counters'] = [group.read() for group in groups]
                # running比例、输出和各线程等式检查前保存全部原始六事件字节。
                save(path, record)
            finally:
                for group in reversed(enabled):
                    group.disable()
                for group in groups:
                    group.close()
            if status:
                raise RuntimeError(error.value.decode('utf-8', errors='replace'))
            record['output_sha256'] = check()
            after = state(cpus)
            record['tasks_after'] = after
            if before != after:
                raise ValueError('计数前后TID或绑定变化')
            record['actual_team_after'] = probe(driver, threads, cpus)
            tasks = {row['tid']: row for row in before}
            active = []
            for counter in record['thread_counters']:
                cpu = tasks[counter['tid']]['allowed_cpus'][0]
                participating = cpu in cpus[:threads]
                nominal_pixels = pixels//threads if participating else 0
                counter.update(cpu=cpu, participates_in_requested_team=participating,
                    nominal_assigned_pixels=nominal_pixels, is_calling_thread=counter['tid'] == os.getpid())
                if 'decode_error' in counter:
                    raise ValueError(counter['decode_error'])
                counts = counter['counts']
                fraction = counter['running_fraction']
                # 未参与且完全未被调度的旁观TID允许零enabled；仍原样保存其所有事件。
                inactive_zero = not participating and counter['time_enabled_ns'] == 0 and all(v == 0 for v in counts.values())
                counter['inactive_zero_window'] = inactive_zero
                if not inactive_zero and (fraction is None or fraction < policy['min_running_fraction'] or fraction > 1):
                    raise ValueError(f'TID {counter["tid"]}六事件运行比例不足或非法')
                if participating and counts['cycles'] <= 0:
                    raise ValueError('参与线程缺少有效周期')
                if not 0 <= counts['oldest_load_not_complete'] <= counts['oldest_not_complete'] <= counts['cycles']:
                    raise ValueError('逐TID最老指令/加载等待事件包含关系异常')
                counter.update(metrics(counts, nominal_pixels))
                if participating:
                    active.append(counter)
            if len(active) != threads:
                raise ValueError('参与计数的TID数量与实际团队不同')
            sums = {name: sum(row['counts'][name] for row in active) for name in NAMES}
            all_sums = {name: sum(row['counts'][name] for row in record['thread_counters']) for name in NAMES}
            record['participating_sum'] = {'counts': sums, **metrics(sums, pixels)}
            record['all_observed_tid_sum_counts'] = all_sums
            record['nonparticipating_sum_counts'] = {name: all_sums[name]-sums[name] for name in NAMES}
            record['individual_cycle_range'] = {'min': min(row['counts']['cycles'] for row in active),
                'max': max(row['counts']['cycles'] for row in active),
                'meaning': '含barrier/收尾/启停差异；不能单独解释为每线程像素工作量或自旋时间'}
            record['table_after'] = pages_snapshot(key+'-after')
            record['source_unchanged'] = True
            record['sentinels_unchanged'] = True
            record['pass'] = True
            save(path, record)
            result['records'].append(record)
            save(args.output/'partial-results.json', result)
            print('完成65六事件诊断', label, threads, flush=True)
        result['table_after'] = pages_snapshot('after')
        if len(result['records']) != 6 or result['warmup_calls'] != 6 or result['counted_calls'] != 6:
            raise AssertionError('固定六案例调用数不同')
        for name, sha in sources.items():
            if digest(ROOT/name) != sha:
                raise ValueError('诊断期间冻结源码或身份改变：'+name)
        result['pass'] = True
        save(args.output/'results.json', result)
    except BaseException as exc:
        result['failure'] = {'type': type(exc).__name__, 'message': str(exc)}
        save(args.output/'failure.json', result)
        raise
    finally:
        if handle is not None:
            d.jshc_cc_destroy(handle)


if __name__ == '__main__':
    main()
