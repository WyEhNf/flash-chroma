"""独立Decimal核六角色近邻配对、240自身AA和6主metric-cell；仅静态待测。"""
import argparse
from collections import Counter
from decimal import Decimal, localcontext
from pathlib import Path
from study_memory_rom import ROOT, read, save, sha

PLAN = ROOT / 'experiments/page-id16-native-pages-performance-v1.json'


def median(values):
    ordered = sorted(values)
    if len(ordered) != 5:
        raise AssertionError('每计时组必须恰好5次')
    return Decimal(ordered[2])


def tier(value):
    return next((limit for limit in (100, 90, 80, 70, 60, 50)
                 if value >= Decimal(limit) / 100), None)


def audit_modules(observations, plan):
    if len(observations) != 3:
        raise AssertionError('实际模块必须三时点')
    known = {str(Path(path)).casefold(): value for path, value in plan['input_sha256'].items()}
    for observation in observations[1:]:
        for name, rows in observation['dependencies'].items():
            if len(rows) != 1 or known.get(str(Path(rows[0]['path'])).casefold()) != rows[0]['sha256']:
                raise AssertionError('实际依赖身份/数量不同：' + name)


def audit_runtime(value, plan):
    actual = value['runtime_contract']
    if actual['python'] != plan['expected_versions']['python'] or actual['numpy'] != plan['expected_versions']['numpy']:
        raise AssertionError('worker/RSS实际Python/NumPy版本不同')
    if actual['environment_before_numpy'] != plan['required_environment'] or actual['environment_after_numpy'] != plan['required_environment'] or actual['environment_end'] != plan['required_environment']:
        raise AssertionError('worker/RSS冻结环境实录不同')
    if actual['allowed_before_numpy'] != 85 or actual['allowed_cpus'] != plan['allowed_cpus'] or Path(actual['plan_path']) != PLAN.resolve():
        raise AssertionError('worker/RSS在NumPy/native导入前允许集/协议实录不同')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('正式审计结果不能覆盖')
    plan = read(PLAN)
    driver = read(args.input / 'driver.json')
    if not driver['passed'] or driver['plan_sha256'] != sha(PLAN) or len(driver['jobs']) != 10 or any(job['returncode'] for job in driver['jobs']):
        raise AssertionError('四worker六RSS未完整一次完成')
    pairs, controls, exceptions = [], [], []
    rows_total = hashes = timed = input_checks = 0
    with localcontext() as context:
        context.prec = 60
        for worker in range(4):
            result = read(args.input / ('worker' + str(worker)) / 'results.json')
            if not result['passed'] or result['plan_sha256'] != sha(PLAN) or len(result['rows']) != 480 or result['affinity']['allowed'] != 85:
                raise AssertionError('worker身份/调用/允许集不同')
            audit_modules(result['module_observations'], plan)
            audit_runtime(result, plan)
            if set(result['identities']) != set(plan['roles']):
                raise AssertionError('六角色热驻留身份不完整')
            library_keys = dict(ref78='ref78', ref80='ref80', linear_c99='linear',
                                copy4_c99='copy4', p4_avx='p4', pages_c99='pages')
            for role, identity in result['identities'].items():
                path = plan['libraries'][library_keys[role]]
                if identity['capacity'] != plan['capacities'][role] or identity['library'] != path or identity['library_sha256'] != plan['input_sha256'][path]:
                    raise AssertionError('六角色实际库/容量与冻结不同')
            rows = result['rows']
            jsonl = [__import__('json').loads(line) for line in (args.input / ('worker' + str(worker)) / 'calls.jsonl').read_text(encoding='utf-8').splitlines()]
            if Counter(row['event'] for row in jsonl) != {'call_attempt': 480, 'call': 480, 'input_identity': 22}:
                raise AssertionError('逐调用尝试/返回及输入身份JSONL不完整')
            if [{key: value for key, value in row.items() if key != 'event'} for row in jsonl if row['event'] == 'call'] != rows:
                raise AssertionError('JSONL和worker原rows不同')
            attempts = [row for row in jsonl if row['event'] == 'call_attempt']
            for attempt, row in zip(attempts, rows):
                if any(attempt[key] != row[key] for key in ('sequence', 'pair', 'role', 'threads', 'mode', 'kind', 'group', 'round')) or attempt['pixels'] != 78643200 or attempt['hash_expected'] != row['hash_checked']:
                    raise AssertionError('调用前尝试与实际返回行不配对')
            if [row['sequence'] for row in rows] != list(range(480)):
                raise AssertionError('调用序号缺失或重复')
            rows_total += len(rows)
            for row in rows:
                if row['returncode'] or any(row[key] not in (0, 2, 4, 6) for key in
                    ('cpu_copy_before', 'cpu_native_before', 'cpu_native_after')):
                    raise AssertionError('native/CPU允许集失败')
                if row['target_address'] != result['target_address'] or row['source_address'] != (result['target_address'] if row['mode'] == 'in' else result['source_address']):
                    raise AssertionError('跨角色输入/输出地址不同')
                if row['apply_ns'] <= 0:
                    raise AssertionError('非法apply时间')
                if row['mode'] == 'out':
                    if any(row[key] is not None for key in ('copy_ns', 'gap_ns', 'copy_apply_ns')):
                        raise AssertionError('分离模式不应产生copy metric')
                elif row['copy_ns'] <= 0 or row['gap_ns'] < 0 or row['copy_apply_ns'] != row['copy_ns'] + row['gap_ns'] + row['apply_ns']:
                    raise AssertionError('原地copy/apply/gap账本不同')
                if row['hash_checked']:
                    hashes += 1
                    if row['sha256'] != plan['expected_output_sha256']:
                        raise AssertionError('组末全百图SHA不同')
                elif row['sha256'] is not None:
                    raise AssertionError('不应隐藏额外输出hash')
                timed += row['kind'] == 'timed'
            identities = result['input_identities']
            if [{key: value for key, value in row.items() if key != 'event'} for row in jsonl if row['event'] == 'input_identity'] != identities:
                raise AssertionError('输入SHA JSONL与身份记录不一致')
            if len(identities) != 22 or identities[0]['label'] != 'worker-start' or identities[-1]['label'] != 'worker-end':
                raise AssertionError('master起止/20cell末身份次数不同')
            expected_labels = {'worker-start', 'worker-end'} | {
                f'cell-end/{threads}/{mode}/{peer}' for threads in (1, 4) for mode in ('in', 'out') for peer in plan['pair_controls']}
            if {row['label'] for row in identities} != expected_labels:
                raise AssertionError('master cell末标签不同')
            for observation in identities:
                protection = observation['protection']
                if observation['sha256'] != plan['expected_input_sha256'] or protection['address'] != result['source_address'] or protection['bytes'] != 235929600 or protection['numpy_writeable']:
                    raise AssertionError('master原输入身份不同')
                cursor, end = protection['address'], protection['address'] + protection['bytes']
                for region in protection['regions']:
                    if region['Protect'] != 2 or region['State'] != 0x1000 or not region['BaseAddress'] <= cursor < region['BaseAddress'] + region['RegionSize']:
                        raise AssertionError('master全区间只读证据不完整')
                    cursor = min(end, region['BaseAddress'] + region['RegionSize'])
                if cursor != end:
                    raise AssertionError('master只读区间缺尾部')
            input_checks += len(identities)
            expected_controls = list(plan['pair_controls'])
            shift = worker % len(expected_controls)
            expected_controls = expected_controls[shift:] + expected_controls[:shift]
            if worker % 2:
                expected_controls.reverse()
            expected_threads = [1, 4] if worker % 2 == 0 else [4, 1]
            expected_modes = ['in', 'out'] if worker % 2 == 0 else ['out', 'in']
            if result['pair_controls'] != expected_controls or result['thread_order'] != expected_threads or result['mode_order'] != expected_modes:
                raise AssertionError('四worker的整体镜像次序不同')
            expected_cell_order = [(threads, mode, 'pages_c99/' + peer) for threads in expected_threads for mode in expected_modes for peer in expected_controls]
            if [(row['threads'], row['mode'], row['pair']) for row in rows[::24]] != expected_cell_order:
                raise AssertionError('实际24调用cell整体次序不同')
            for threads in (1, 4):
                for mode in ('in', 'out'):
                    for peer in plan['pair_controls']:
                        pair_name = 'pages_c99/' + peer
                        selected = [row for row in rows if row['threads'] == threads and row['mode'] == mode and row['pair'] == pair_name]
                        if len(selected) != 24:
                            raise AssertionError('pair-cell必须24调用')
                        mirrored = (worker + int(threads == 4) + int(mode == 'out')) % 2
                        a, b = 'pages_c99', peer
                        warm_order = [b, a, b, a] if mirrored else [a, b, a, b]
                        group_order = [b, a, a, b] if mirrored else [a, b, b, a]
                        warm = [row for row in selected if row['kind'] == 'warm']
                        if [row['role'] for row in warm] != warm_order or [row['hash_checked'] for row in warm] != [False, False, True, True]:
                            raise AssertionError('warm镜像/各角色两次/末SHA不同')
                        groups = {}
                        for group, role in enumerate(group_order):
                            values = [row for row in selected if row['kind'] == 'timed' and row['group'] == group]
                            if len(values) != 5 or [row['round'] for row in values] != list(range(5)) or any(row['role'] != role for row in values) or [row['hash_checked'] for row in values] != [False, False, False, False, True]:
                                raise AssertionError('ABBA/BAAB组/5round/末SHA不同')
                            groups[group] = values
                        for metric in (('apply_ns', 'copy_apply_ns') if mode == 'in' else ('apply_ns',)):
                            own = {}
                            valid = True
                            for role in (a, b):
                                group_ids = [group for group, name in enumerate(group_order) if name == role]
                                samples = [median([row[metric] for row in groups[group]]) for group in group_ids]
                                aa = samples[1] / samples[0]
                                accepted = Decimal('.85') <= aa <= Decimal('1.15')
                                controls.append(dict(worker=worker, threads=threads, mode=mode, peer=peer,
                                    metric=metric, role=role, first_ns=str(samples[0]), second_ns=str(samples[1]),
                                    aa=str(aa), valid=accepted))
                                own[role] = samples
                                valid = valid and accepted
                            ratios = [own[b][index] / own[a][index] for index in (0, 1)]
                            row = dict(worker=worker, threads=threads, mode=mode, peer=peer, metric=metric,
                                valid=valid, ratios=[str(value) for value in ratios], worst_raw=str(min(ratios)))
                            pairs.append(row)
                            if peer in ('ref78', 'ref80') and valid and min(ratios) < Decimal('.5'):
                                exceptions.append(row)
        if (rows_total, timed, hashes, input_checks, len(controls), len(pairs)) != (1920, 1600, 480, 88, 240, 120):
            raise AssertionError('独立调用/AA/输出或输入SHA总数不同')
        cases, auxiliary = [], []
        for threads in (1, 4):
            for mode in ('in', 'out'):
                for metric in (('apply_ns', 'copy_apply_ns') if mode == 'in' else ('apply_ns',)):
                    main = [row for row in pairs if row['threads'] == threads and row['mode'] == mode and row['metric'] == metric and row['peer'] in ('ref78', 'ref80')]
                    if len(main) != 8:
                        raise AssertionError('主双基线四worker pair证据不完整')
                    worst = min(Decimal(row['worst_raw']) for row in main)
                    valid = all(row['valid'] for row in main)
                    cases.append(dict(threads=threads, mode=mode, metric=metric, all_main_pairs_valid=valid,
                                      worst_raw_retention=str(worst), tier=tier(worst) if valid else None))
                    for peer in ('linear_c99', 'copy4_c99', 'p4_avx'):
                        selected = [row for row in pairs if row['threads'] == threads and row['mode'] == mode and row['metric'] == metric and row['peer'] == peer]
                        worst_aux = min(Decimal(row['worst_raw']) for row in selected)
                        auxiliary.append(dict(threads=threads, mode=mode, metric=metric, peer=peer,
                            all_pairs_valid=all(row['valid'] for row in selected), worst_raw_retention=str(worst_aux), scope='仅辅助，不给主档或恢复旧资格。'))
        global_valid = all(row['all_main_pairs_valid'] for row in cases)
        global_worst = min(Decimal(row['worst_raw_retention']) for row in cases)
        global_tier = tier(global_worst) if global_valid else None
        matrix = {str(precision): {str(speed): 12665940 if global_valid and global_worst >= Decimal(speed) / 100 else None
            for speed in (100, 90, 80, 70, 60, 50)} for precision in (100, 90, 80, 70, 60, 50)}
        rss = []
        for role in plan['roles']:
            value = read(args.input / ('rss-' + role) / 'rss.json')
            path = plan['libraries'][library_keys[role]]
            if value['plan_sha256'] != sha(PLAN) or value['role'] != role or value['identity']['capacity'] != plan['capacities'][role] or value['affinity']['allowed'] != 85 or value['identity']['library'] != path or value['identity']['library_sha256'] != plan['input_sha256'][path]:
                raise AssertionError('六fresh RSS身份/容量不同')
            audit_modules(value['module_observations'], plan)
            audit_runtime(value, plan)
            rss.append(value)
        save(args.output, dict(audit_passed=True, purpose=__doc__, plan_sha256=sha(PLAN), calls=rows_total,
            timed=timed, output_sha_checks=hashes, input_sha_checks=input_checks, controls=controls, pair_metrics=pairs,
            cases=cases, auxiliary=auxiliary, valid_low50_main_examples=exceptions, rss=rss,
            global_all_main_controls_valid=global_valid, global_worst_raw_retention=str(global_worst), global_tier=global_tier,
            actual_capacity=12665940, precision_retained_percent=100, candidate_tier_matrix=matrix,
            scope='Decimal60位精确整数ns中位数/比值；各主pair独立自身AA，原地apply与copy_apply共同过线，分离仅apply。无效不授档、有效<50保留，不补跑、不把辅助分母救全局。'))
    print(dict(audit_passed=True, calls=rows_total, controls=len(controls), hashes=hashes,
               global_tier=global_tier, valid_low50=len(exceptions)), flush=True)


if __name__ == '__main__':
    main()
