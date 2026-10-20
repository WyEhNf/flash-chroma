"""标准库独立复算修订22的唯一性能记录；不载入动态库，不重新计时。"""
import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--performance', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), '审计结果不得覆盖')
    run = read(args.performance/'run.json')
    result = read(args.performance/'results.json')
    policy = run['policy']
    for key in ('plan', 'build', 'full_acceptance', 'topology', 'domain_contract',
                'packed_contract', 'signed_contract', 'validation'):
        spec = policy[key]
        require(sha(ROOT/spec['path']) == spec['sha256'], '策略输入身份不同：'+key)
    for path, digest in run['source_sha256'].items():
        require(sha(ROOT/path) == digest, '计时脚本身份不同：'+path)
    plan = read(ROOT/policy['plan']['path'])
    build = read(ROOT/policy['build']['path'])
    full = read(ROOT/policy['full_acceptance']['path'])
    require(build['revisions'] == {'reference': 16, 'candidate': 22}, '比较修订不同')
    require(full['pass'] and not full['cube']['byte_mismatches']
            and not full['photos']['byte_mismatches'], '完整正确性未通过')
    for path, digest in plan['source_sha256'].items():
        require(sha(ROOT/path) == digest, '运行时源码身份不同：'+path)
    expected_output = full['photos']['output_sha256']['reference']
    require(expected_output == full['photos']['output_sha256']['candidate'], '两库照片SHA不同')
    require(policy['repeats'] == 5 and policy['verify_each_measured_round'], '逐轮核验协议不同')
    workers = []
    for index in range(4):
        path = args.performance/f'worker{index}.json'
        require(sha(path) == result['worker_sha256'][index], '原始进程记录身份不同')
        worker = read(path)
        require(worker['worker_index'] == index and worker['order'] == policy['orders'][index]
                and worker['thread_order'] == policy['thread_orders'][index], '执行顺序不同')
        require(worker['actual_affinity'] == policy['affinity_cpus'], '亲和性不同')
        require(worker['build_sha256'] == policy['build']['sha256']
                and worker['libraries'] == build['libraries']
                and worker['full_acceptance_sha256'] == policy['full_acceptance']['sha256'], '库或验收身份不同')
        require(worker['source_bytes'] == 235929600 and len(worker['records']) == 4, '图组或配置数不同')
        require([(r['requested_threads'], r['variant']) for r in worker['records']]
                == [(t, role) for t in worker['thread_order'] for role in worker['order']], '原始配置顺序不同')
        for record in worker['records']:
            role = record['variant']
            require(record['library_revision'] == build['revisions'][role]
                    and record['library_sha256'] == build['libraries'][role]['sha256'], '实际库不同')
            require(record['warmup_output_sha256'] == expected_output
                    and record['per_round_output_sha256'] == [expected_output]*5, '逐轮输出不同')
            require(record['start_state']['affinity'] == record['end_affinity']
                    == policy['affinity_cpus'], '计时前后亲和性不同')
            a, c = record['apply_seconds'], record['copy_apply_seconds']
            require(len(a) == len(c) == 5 and all(math.isfinite(x) and 0 < x <= y
                    and math.isfinite(y) for x, y in zip(a, c)), '原始计时非法')
            require(math.isclose(record['prepare_plus_first_100_copy_apply_seconds'],
                    record['prepare_wall_seconds']+c[0], abs_tol=1e-12), '准备总计不同')
            require(record['cache_domain_certificate']['fast_path_enabled'] == 1, '域快路径未启用')
            require(record['model_accounting_bytes'] == (1800836 if role == 'reference' else 10190548), '容量不同')
            if role == 'candidate':
                p = record['compiled_palette']
                require(p['enabled'] == 1 and p['palette_size'] == 230
                        and p['fast_blocks'] == 1962299 and p['blocks'] == 2097152
                        and p['table_capacity_bytes'] == 8388608, '实际编码参数不同')
        workers.append(worker)
    require(len({w['pid'] for w in workers}) == 4
            and len({w['source_sha256'] for w in workers}) == 1, '进程隔离或输入不一致')
    paired = []
    for threads in (1, 4):
        pairs = [{r['variant']: r for r in w['records'] if r['requested_threads'] == threads} for w in workers]
        values = {}
        for label, field in (('apply', 'apply_seconds'), ('copy_apply', 'copy_apply_seconds')):
            values[label] = [median(p['candidate'][field])/median(p['reference'][field]) for p in pairs]
        prepared = [p['candidate']['prepare_plus_first_100_copy_apply_seconds']/
                    p['reference']['prepare_plus_first_100_copy_apply_seconds'] for p in pairs]
        official = next(p for p in result['paired'] if p['requested_threads'] == threads)
        for label, ratios in values.items():
            require(ratios == official['process_'+label+'_ratios']
                    and median(ratios) == official['median_'+label+'_ratio'], '配对结果复算不同')
        require(prepared == official['process_prepare_plus_100_copy_apply_ratios'], '准备比值复算不同')
        g = policy['adoption_gate']
        require(median(values['apply']) <= g['median_apply_ratio_max']
                and max(values['apply']) <= g['any_process_apply_ratio_max']
                and median(values['copy_apply']) <= g['median_copy_apply_ratio_max']
                and median(prepared) <= g['median_prepare_plus_100_ratio_max'], '冻结门槛未通过')
        paired.append({'threads': threads, 'apply_time_ratio': median(values['apply']),
            'apply_throughput_gain_percent': (1/median(values['apply'])-1)*100,
            'apply_time_reduction_percent': (1-median(values['apply']))*100,
            'copy_apply_time_ratio': median(values['copy_apply']),
            'copy_apply_throughput_gain_percent': (1/median(values['copy_apply'])-1)*100,
            'prepare_plus_first_warmed_100_copy_apply_ratio': median(prepared),
            'prepared_processes_slower_than_reference': sum(r > 1 for r in prepared)})
    require(result['accepted_on_this_host'] and not result['failed_gates'], '原始结果门槛不同')
    audit = {'pass': True, 'purpose': __doc__, 'performance_result_sha256': sha(args.performance/'results.json'),
        'auditor_sha256': sha(__file__), 'fresh_processes': 4, 'configurations': 16,
        'verified_rounds': 80, 'images_per_round': 100, 'paired': paired,
        'source_photo_sha256': workers[0]['source_sha256'], 'new_performance_calls': 0,
        'scope': '本机固定模型和协议的描述统计；温度频率未控制；非Skylake实测或任意LUT保证'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
