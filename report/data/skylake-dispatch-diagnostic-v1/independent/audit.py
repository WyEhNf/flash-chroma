"""独立离线复算78发射诊断；不导入原诊断模块、不加载动态库、不执行像素或计数。"""
import ast
import hashlib
import json
import math
from pathlib import Path
import platform
import struct
import sys
import zipfile


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'artifacts/skylake-dispatch-diagnostic-v1'
POLICY = ROOT / 'experiments/skylake-dispatch-diagnostic-v2.json'
OUTPUT = Path(__file__).with_name('results.json')
POLICY_SHA = '7549c82eae9dc5821352dd9043977c6b886931c57538789072da0b034c842865'
# 独立写入官方编码，不复用被审计脚本的raw函数或EVENT_GROUPS。
EVENTS = {
    'dispatch': [('cycles', 0x76), ('instructions', 0xc0),
                 ('frontend_unused_slots', 0x1000001a0), ('backend_unused_slots', 0x100001ea0),
                 ('load_queue_stall_cycles', 0x2ae), ('store_queue_stall_cycles', 0x4ae)],
    'resources': [('cycles', 0x76), ('integer_prf_stall_cycles', 0x1ae),
                  ('integer_scheduler_any_stall_cycles', 0x01000faf), ('retire_token_stall_cycles', 0x20af),
                  ('oldest_not_complete', 0x2d6), ('oldest_load_not_complete', 0xa2d6)]
}
CASES = [('photo_inplace', 1, 'dispatch'), ('photo_inplace', 1, 'resources'),
         ('photo_inplace', 4, 'resources'), ('photo_inplace', 4, 'dispatch'),
         ('uniform_inplace', 4, 'resources'), ('uniform_inplace', 4, 'dispatch'),
         ('uniform_inplace', 1, 'dispatch'), ('uniform_inplace', 1, 'resources')]
INPUTS = {}


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def register(path):
    path = Path(path)
    INPUTS[path.relative_to(ROOT).as_posix()] = {'sha256': sha(path), 'bytes': path.stat().st_size}
    return path


def read(path):
    return json.loads(register(path).read_text(encoding='utf-8'))


def check(ok, message):
    if not ok:
        raise AssertionError(message)


def checked(spec):
    path = ROOT / spec['path']
    check(sha(path) == spec['sha256'], '身份SHA不同：' + spec['path'])
    if 'bytes' in spec:
        check(path.stat().st_size == spec['bytes'], '身份长度不同：' + spec['path'])
    return register(path)


def same(actual, expected, label):
    if isinstance(expected, dict):
        for key, value in expected.items():
            check(key in actual, label + '缺少字段：' + key)
            same(actual[key], value, label + '/' + key)
    elif isinstance(expected, float):
        check(isinstance(actual, (int, float)) and math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-15), label)
    else:
        check(actual == expected, label)


def derived(counts, pixels):
    cycles = counts['cycles']
    out = {'per_nominal_pixel': {k: v / pixels for k, v in counts.items()} if pixels else None}
    if 'instructions' in counts:
        out['instructions_per_cycle'] = counts['instructions'] / cycles if cycles else None
    for key, value in counts.items():
        if key.endswith('_unused_slots'):
            check(0 <= value <= 6 * cycles, '槽位范围：' + key)
            out[key + '_fraction'] = value / (6 * cycles) if cycles else None
        elif key.endswith('_stall_cycles') or key in ('oldest_not_complete', 'oldest_load_not_complete'):
            check(0 <= value <= cycles, '周期范围：' + key)
            out[key + '_fraction'] = value / cycles if cycles else None
    if 'oldest_load_not_complete' in counts:
        check(counts['oldest_load_not_complete'] <= counts['oldest_not_complete'], 'load等待包含关系')
    return out


def page(snapshot):
    direct, pages = snapshot['direct_info'], snapshot['paged_info']
    same(direct, {'enabled': 1, 'format': 9, 'entries': 2**22, 'table_capacity_bytes': 2**24}, '直接表')
    same(snapshot, {'model_accounting_bytes': 28046644, 'andn_split_enabled': 1}, '句柄')
    same(pages, {'bytes': 2**24, 'anon_huge_bytes': 2**24, 'fully_huge': True, 'aligned_2m': True}, '大页')
    check(pages['base'] % 2**21 == 0, '表基址2MiB对齐')
    mapping = pages['smaps']
    start, end = (int(x, 16) for x in mapping['header'].split()[0].split('-'))
    check(start == pages['base'] and end - start == mapping['mapping_bytes'] == 2**24, '精确对象VMA')
    for key in ('Size', 'AnonHugePages'):
        number, unit = mapping['properties'][key].split()
        check(unit == 'kB' and int(number) * 1024 == 2**24, 'smaps原始大小：' + key)
    return pages['base']


def quiet(path, policy):
    q = read(path)
    check(q['pass'] and q['policy'] == policy and q['new_native_calls'] == q['new_performance_calls'] == 0, '空闲回执')
    check(len(q['samples']) == len(q['intervals']) + 1, '空闲采样数量')
    for previous, current, interval in zip(q['samples'], q['samples'][1:], q['intervals']):
        busy = {}
        for key, row in current['cpu_ticks'].items():
            old = previous['cpu_ticks'][key]
            check(row['total'] == sum(row['raw_ticks'][:8]) and row['idle'] == row['raw_ticks'][3], 'CPU原始tick')
            total, idle = row['total'] - old['total'], row['idle'] - old['idle']
            check(total > 0 and 0 <= idle <= total, 'CPU增量范围')
            busy[key] = 100 * (total - idle) / total
        same(interval['busy_percent'], busy, '独立空闲比例')
        settled = interval['elapsed_seconds'] >= q['actual_settle_min_seconds'] and current['pid1_age_seconds'] >= policy['minimum_pid1_age_seconds']
        check(interval['settled'] == settled, '空闲稳定期')
        check(interval['pass'] == (settled and all(v <= policy['busy_percent_max'] for v in busy.values())), '空闲判定')
    check(all(x['pass'] for x in q['intervals'][-policy['consecutive_good_intervals']:]), '连续空闲间隔')


def audit():
    p, result, run = read(POLICY), read(DATA/'results.json'), read(DATA/'run.json')
    check(sha(POLICY) == POLICY_SHA == result['policy_sha256'], '冻结v2策略SHA')
    check(run['policy'] == p, 'run内嵌策略')
    check(p['events'] == {k: [list(x) for x in v] for k, v in EVENTS.items()}, '独立事件常量/顺序')
    check(p['cases'] == [{'case': a, 'threads': b, 'group': c} for a, b, c in CASES], 'AB/BA/BA/AB矩阵')
    same(result, {'pass': True, 'warmup_calls': 8, 'counted_calls': 8, 'wallclock_calls': 0,
                  'handle_creation_count': 1, 'threefold_goal_completed': False, 'automatic_retry': False}, '调用总数')
    check(p['candidate_apply_calls'] == p['warmup_calls'] + p['counted_calls'] == 16, '16次公开apply')
    check(run['candidate_wallclock_timing_calls'] == 0 and len(result['records']) == 8, '无墙钟调用')
    plan, build, full, validation = [read(checked(p[k])) for k in ('plan', 'build', 'full', 'validation')]
    check(build['revisions'] == {'reference': 23, 'candidate': 78}, '修订身份')
    check(full['pass'] and full['build_sha256'] == p['build']['sha256'], '全域身份')
    check(full['libraries'] == build['libraries'], '全域/构建库身份')
    candidate = build['libraries']['candidate']
    check(candidate['sha256'] == p['library']['sha256'] and
          candidate['path'] == '/mnt/f/Hackathon/projects/16-lut-color/' + p['library']['path'], '同库WSL绝对路径/仓库相对路径')
    check(build['plan_sha256'] == validation['plan_sha256'] == p['plan']['sha256'], '计划身份')
    check(build['source_sha256'] == plan['source_sha256'], '构建源身份')
    check(validation['full_result'] == p['full'], '验证单全域身份')
    static = read(checked(validation['static_result']))
    check(static['accepted'] and static['plan_sha256'] == p['plan']['sha256'] and static['build_sha256'] == p['build']['sha256'], '静态v2身份')
    for key in ('probe', 'pinning_probe', 'library', 'driver'):
        checked(p[key])
    check(read(ROOT/p['probe']['path'])['available'], '两组事件探测')
    sources = {**plan['source_sha256'], **validation['source_sha256'], **p['source_hashes']}
    for name, digest in sources.items():
        check(sha(ROOT/name) == digest, '当前源SHA：' + name)
    for name, digest in run['source_sha256'].items():
        check(sha(ROOT/name) == digest, '测量归档源SHA：' + name)
        register(ROOT/name)
    check(all(run['source_sha256'].get(n) == h for n, h in sources.items()), '归档源覆盖所有冻结源')
    with zipfile.ZipFile(register(DATA/'measured-source.zip')) as z:
        check(len(z.namelist()) == len(set(z.namelist())) and set(z.namelist()) == set(run['source_sha256']), 'ZIP源清单')
        for name, digest in run['source_sha256'].items():
            check(hashlib.sha256(z.read(name)).hexdigest() == digest, 'ZIP源字节：' + name)
    driver = ROOT/'scripts/diagnose_skylake_dispatch_linux.py'
    tree = ast.parse(driver.read_text(encoding='utf-8'))
    check(sum(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'call' for n in ast.walk(tree)) == 2, '每案例两处apply调用')
    check(not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in ('jshc_cc_bench', 'jshc_sb_run') for n in ast.walk(tree)), '无原生计时调用')
    check('attr.config' not in driver.read_text(encoding='utf-8'), '事件由已冻结支持模块提供')
    support = (ROOT/'scripts/zen4_dispatch_pmu_support.py').read_text(encoding='utf-8')
    check('attr.flags = 32 | 64 | (5 if not self.fds else 0)' in support and 'attr.read_format = 4, ct.sizeof(attr), config, 11' in support, 'pinned/user态/组格式')
    for name in ('probe_skylake_pmu.py', 'zen4_dispatch_pmu_support.py', 'probe_skylake_dispatch_pmu.py'):
        ast.parse((ROOT/'scripts'/name).read_text(encoding='utf-8'))
    check("('config','sample_period','sample_type','read_format','flags')" in (ROOT/'scripts/probe_skylake_pmu.py').read_text(encoding='utf-8'), 'Attr.config属于uint64字段组')
    for key in ('library', 'driver'):
        check(any(row['sha256'] == p[key]['sha256'] for row in result['loaded_libraries']), '实际映射库SHA：' + key)
    bases = {page(result['table_before']), page(result['table_after'])}
    check(read(DATA/'before-table.json') == result['table_before'] and read(DATA/'after-table.json') == result['table_after'], '整体页原件')
    quiet(DATA/'quiet-parent.json', p['quiet_protocol'])
    summaries, raw_rows, active_count, inactive_count = [], [], 0, 0
    for i, (label, threads, group_name) in enumerate(CASES):
        row = result['records'][i]
        key = f'case{i}-{label}-{threads}-{group_name}'
        check((row['case'], row['requested_threads'], row['group']) == (label, threads, group_name), '案例顺序')
        check(read(DATA/(key+'.json')) == row, '逐案例原件与总结果相同')
        check(row['pass'] and row['warmup_return_code'] == row['native_return_code'] == 0, '原生返回')
        check(row['source_unchanged'] and row['sentinels_unchanged'], '源及哨兵回执')
        expected = p['photo_output_sha256'] if label == 'photo_inplace' else p['uniform_output_sha256']
        check(row['output_sha256_expected'] == row['warmup_output_sha256'] == row['output_sha256'] == expected, '完整输出SHA回执')
        check(row['pixels'] == 78643200 and row['runtime_blocks'] == 1200 and row['runtime_block_pixels'] == 65536, '像素/块合同')
        before = row['tasks_before']
        check(before == row['tasks_after'] and len(before) == 4, 'TID/affinity前后')
        by_tid = {x['tid']: x['allowed_cpus'] for x in before}
        check(sorted(by_tid.values()) == [[0], [2], [4], [6]], '四个不同物理CPU绑定')
        for team in (row['actual_team'], row['actual_team_after']):
            check(team['actual'] == team['requested'] == threads and team['cpus'] == [0, 2, 4, 6][:threads], '实际团队')
            check(team['task_affinities'] == before and team['main_allowed_cpus_after_openmp'] == [0], '团队绑定')
        main = next(tid for tid, cpus in by_tid.items() if cpus == [0])
        order = sorted(by_tid, key=lambda tid: (tid == main, tid))
        check(row['counter_enable_tid_order'] == order and row['counter_disable_tid_order'] == order[::-1], '主TID最后开最先关')
        names = [n for n, _ in EVENTS[group_name]]
        check(len(row['thread_counters']) == 4 and {x['tid'] for x in row['thread_counters']} == set(by_tid), '四TID完整原件')
        active, all_counts = [], []
        for counter in row['thread_counters']:
            raw = bytes.fromhex(counter['raw_group_read_hex'])
            check(len(raw) == 72, '原始读取72字节')
            decoded = struct.unpack('<9Q', raw)
            check(decoded[0] == 6, '原始事件数')
            enabled, running = decoded[1:3]
            counts = dict(zip(names, decoded[3:]))
            check(counts == counter['counts'] and enabled == counter['time_enabled_ns'] and running == counter['time_running_ns'], '原始计数/时长解码')
            check(0 <= running <= enabled, '运行时长包含关系')
            tid, cpu = counter['tid'], by_tid[counter['tid']][0]
            participating = cpu in [0, 2, 4, 6][:threads]
            nominal = row['pixels']//threads if participating else 0
            inactive = not participating and enabled == 0 and running == 0 and not any(counts.values())
            fraction = running/enabled if enabled else None
            check(inactive or fraction is not None and .99 <= fraction <= 1, '无复用运行比例')
            check(not participating or counts['cycles'] > 0, '参与线程有效周期')
            same(counter, {'group': group_name, 'cpu': cpu, 'participates_in_requested_team': participating,
                           'nominal_assigned_pixels': nominal, 'is_calling_thread': tid == main,
                           'inactive_zero_window': inactive, 'running_fraction': fraction}, '线程诊断字段')
            values = derived(counts, nominal)
            same(counter, values, '独立线程单位/比例')
            raw_rows.append({'case_index': i, 'case': label, 'threads': threads, 'group': group_name,
                             'tid': tid, 'cpu': cpu, 'participating': participating, 'raw_hex': raw.hex(),
                             'enabled_ns': enabled, 'running_ns': running, 'counts': counts, **values})
            all_counts.append(counts)
            if participating:
                active.append(counts)
                active_count += 1
            else:
                inactive_count += 1
        check(len(active) == threads, '参与线程个数')
        sums = {n: sum(x[n] for x in active) for n in names}
        totals = {n: sum(x[n] for x in all_counts) for n in names}
        values = derived(sums, row['pixels'])
        same(row['participating_sum'], {'counts': sums, **values}, '参与线程独立聚合')
        check(row['all_observed_tid_sum_counts'] == totals, '全TID聚合')
        check(row['nonparticipating_sum_counts'] == {n: totals[n]-sums[n] for n in names}, '旁观TID聚合')
        same(row['individual_cycle_range'], {'min': min(x['cycles'] for x in active), 'max': max(x['cycles'] for x in active)}, '周期范围')
        for phase in ('before', 'after'):
            snap = row['table_'+phase]
            check(read(DATA/(key+'-'+phase+'-table.json')) == snap, '逐案例页原件')
            bases.add(page(snap))
        quiet(DATA/('quiet-'+key+'.json'), p['quiet_protocol'])
        summaries.append({'case': label, 'threads': threads, 'group': group_name, 'counts': sums, **values})
    check(len(raw_rows) == 32 and active_count == 20 and inactive_count == 12, '32份逐TID覆盖')
    check(len(bases) == 1, '一句柄同表基址')
    partial = read(DATA/'partial-results.json')
    check(partial['records'] == result['records'] and partial['warmup_calls'] == partial['counted_calls'] == 8, '增量结果一致')
    return {'pass': True, 'decoded_tid_records': 32, 'participating_tid_records': 20, 'nonparticipating_tid_records': 12,
            'source_zip_entries': len(run['source_sha256']), 'table_snapshots_checked': 18, 'quiet_receipts_checked': 9,
            'warmup_apply_calls': 8, 'counted_apply_calls': 8, 'candidate_wallclock_calls': 0,
            'summaries': summaries, 'independently_decoded_records': raw_rows,
            'interpretation': {
                'finding': '照片1/4线程LQ受阻约71.11%/72.94%，FE空槽约0.842%/2.425%；SQ与整数PRF/调度队列原因很低。支持以额外整数拆分减少输入加载个数的有限假设。',
                'proposal': '下一候选若另行授权：每两个RGB24一次mem64 ANDN，保留四ID屏障、两级查表及输出；总加载次数约3降至2.5每像素。',
                'static_cost': '每对ANDN64+MOV+AND24+SHR24替换两条ANDN32，约增加1条指令每像素；输入请求字节仍为4B每像素，ID/palette随机加载未减。',
                'risks': '输入通常命中L1，未证明其占据主要LQ时间；两索引增加拆分依赖、寄存器活跃区间及可能spill。照片低FE空槽不保证新增指令免费。',
                'gray_observation': '灰色4线程retire-token约38.06%，1线程约1.60%；不能由此直接认定store、barrier或其他单一根因。',
                'stop_scope': '本审计不实现候选、不执行原生或性能，不宣布达到三倍目标。'},
            'limitations': [
                '审计重算已保存raw与哈希回执，没有重新生成像素；输出一致性及源/哨兵仅核对原始诊断回执。',
                'time_enabled/time_running为计数窗口累积时长，没有绝对启停时间戳；启停顺序由冻结源及保存TID顺序交叉核对。',
                'A/B是独立原生调用；不相加原因，不跨组构建同时因果分解，不把灰色与照片相减当纯查表代价。',
                '每TID窗口包含OpenMP调度、barrier、收尾与启停边界；名义像素分配不是内核内部计数。',
                'WSL虚拟PMU可调度且范围自洽不代表宿主已校准全部语义；本机Zen4不代表Skylake实机。']}


def main():
    if OUTPUT.exists():
        raise FileExistsError('不覆盖独立审计结果：' + str(OUTPUT))
    register(Path(__file__))
    result = {'pass': False, 'purpose': __doc__, 'audit_environment': {'platform': platform.platform(), 'python': sys.version},
              'reproduction': 'python artifacts/skylake-dispatch-diagnostic-independent-v1/audit.py',
              'new_candidate_calls': 0, 'new_counter_calls': 0, 'new_builds': 0}
    try:
        result.update(audit())
    except BaseException as exc:
        result['failure'] = {'type': type(exc).__name__, 'message': str(exc)}
        raise
    finally:
        result['inputs'] = INPUTS
        OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
        print(json.dumps({'pass': result['pass'], 'decoded_tid_records': result.get('decoded_tid_records'),
                          'failure': result.get('failure')}, ensure_ascii=True))


if __name__ == '__main__':
    main()
