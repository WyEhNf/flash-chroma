"""只核对已保存字节和4×5计时回执并归档；不调用模型、原生库、像素或性能。"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import shutil
import statistics
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def read(path): return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8', newline='\n')


def equal(a, b):
    if abs(a-b) > 1e-12: raise ValueError(f'冻结统计复算不同：{a} / {b}')


def check_spec(spec):
    path = ROOT/spec['path']
    if digest(path) != spec['sha256']: raise ValueError('原始字节SHA不同：'+spec['path'])
    return path


def source_receipt(folder, record):
    with zipfile.ZipFile(folder/'measured-source.zip') as archive:
        for name, sha in record['source_sha256'].items():
            if digest(ROOT/name) != sha or hashlib.sha256(archive.read(name)).hexdigest() != sha:
                raise ValueError('源码当前字节/实测ZIP不同：'+name)


def csv_file(path, fields, rows):
    with Path(path).open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fields); writer.writeheader(); writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'report/data/channel-runtime-specialized-v1')
    args = parser.parse_args(); out = args.output.resolve()
    if out.exists(): raise ValueError('不覆盖本阶段档案')
    policy_path = ROOT/'experiments/channel-runtime-specialized-v1.json'
    native_plan_path = ROOT/'experiments/cinema-specialized-native-v1.json'
    runtime_plan_path = ROOT/'experiments/cinema-specialized-runtime-v1.json'
    policy, native_plan, plan = map(read, (policy_path, native_plan_path, runtime_plan_path))
    build_dir = ROOT/'artifacts/channel-native-specialized-v1'
    contract_dir = ROOT/'artifacts/channel-native-specialized-contract-v1'
    native_dir = ROOT/'artifacts/cinema-specialized-native-v1'
    runtime_dir = ROOT/'artifacts/cinema-specialized-runtime-v1'
    build, contract, native, native_run, result, runtime_run = map(read, (
        build_dir/'build.json', contract_dir/'results.json', native_dir/'results.json', native_dir/'run.json',
        runtime_dir/'results.json', runtime_dir/'run.json'))
    gates = policy['future_performance_gates']
    if (plan != runtime_run['plan'] or native_plan != native_run['plan']
            or plan['orders'] != gates['balanced_orders'] or plan['thread_orders'] != gates['thread_orders']
            or plan['repeats'] != gates['repeats_per_process_configuration'] or len(plan['orders']) != gates['processes']):
        raise ValueError('实际计划/顺序/预算不同')
    for record in (plan, native_plan):
        for spec in record['inputs'].values(): check_spec(spec)
        for spec in record.get('suffix_models', record.get('controls', [])): check_spec(spec)
    for spec in policy['build_inputs'].values(): check_spec(spec)
    primary_sha = plan['inputs']['library']['sha256']; old_sha = plan['inputs']['baseline_library']['sha256']
    prior = read(check_spec(native_plan['inputs']['prior_full']))
    prior_run = read(check_spec(native_plan['inputs']['prior_run']))
    if (not contract['pass'] or not native['pass'] or not result['pass'] or not prior['acceptance']['accepted']
            or contract['library_sha256'] != primary_sha or native['library_sha256'] != primary_sha
            or native['prior_full_results_sha256'] != digest(check_spec(native_plan['inputs']['prior_full']))
            or native['representation_sha256'] != native_plan['inputs']['model']['sha256']
            or build['files']['jshc_channel_specialized.dll'] != primary_sha
            or native['cube']['byte_mismatches'] or native['photos']['byte_mismatches']):
        raise ValueError('构建、合同或完整native身份/状态不同')
    if (plan['inputs']['baseline_model'] != plan['inputs']['candidate_base']
            or plan['inputs']['baseline_sidecar'] != plan['inputs']['candidate_sidecar']
            or plan['inputs']['baseline_cube'] != plan['inputs']['candidate_cube']
            or plan['controls'] != native_plan['suffix_models']
            or native_plan['inputs']['base'] != plan['inputs']['candidate_base']
            or native_plan['inputs']['sidecar'] != plan['inputs']['candidate_sidecar']
            or native_plan['inputs']['cube'] != plan['inputs']['candidate_cube']
            or native_plan['suffix_models'] != prior_run['plan']['suffix_models']):
        raise ValueError('不是同一a399四级模型/输入的两库比较')
    sidecar = check_spec(plan['inputs']['candidate_sidecar']).read_bytes()
    if len(sidecar) != 9216 or (sidecar[:3072] == sidecar[3072:6144] == sidecar[6144:]):
        raise ValueError('本实际模型首级没有独立通道几何')
    identity = dict(native_run); recorded = identity.pop('identity_sha256')
    if (hashlib.sha256(json.dumps(identity, sort_keys=True, allow_nan=False).encode()).hexdigest() != recorded
            or native['run_identity'] != recorded): raise ValueError('完整native运行身份不能复算')
    for folder, record in ((build_dir, build), (contract_dir, contract), (native_dir, native_run), (runtime_dir, runtime_run)):
        source_receipt(folder, record)
    if (build['plan_sha256'] != digest(policy_path) or contract['plan_sha256'] != digest(policy_path)
            or contract['build_sha256'] != digest(build_dir/'build.json') or len(contract['cases']) != 44):
        raise ValueError('唯一计划、构建或44组合同不同')
    for case in contract['cases']:
        if case['integer_oracle_mismatches'] or case['sentinel_mismatches']: raise ValueError('有限合同非零差异')
    for name, sha in native['cube']['sha256'].items():
        expected = prior['native']['cube_sha256']['single_oracle'] if name.startswith('single') else prior['cube']['prediction_sha256']
        if sha != expected: raise ValueError('完整单级/四级流身份不同')
    if (native['photos']['output_sha256'] != prior['photos']['output_sha256'] or native['photos']['count'] != 100
            or any(a['image'] != b['image'] or a['prediction_sha256'] != b['prediction_sha256'] or a['byte_mismatches']
                for a, b in zip(native['photos']['per_image'], prior['photos']['per_image']))):
        raise ValueError('完整百图输出身份不同')
    workers = []; raw_rows = []; process_rows = []
    if len(result['worker_sha256']) != 4: raise ValueError('不是四份原worker回执')
    for index, expected_sha in enumerate(result['worker_sha256']):
        path = runtime_dir/f'worker{index}.json'
        if digest(path) != expected_sha: raise ValueError('worker原字节SHA不同')
        worker = read(path)
        if (worker['worker_index'] != index or worker['order'] != plan['orders'][index]
                or worker['thread_order'] != plan['thread_orders'][index] or len(worker['records']) != 4
                or worker['source_bytes'] != 235929600 or worker['capabilities'] != 7
                or worker['libraries']['baseline']['sha256'] != old_sha
                or worker['libraries']['candidate']['sha256'] != primary_sha): raise ValueError('worker输入、库或顺序不同')
        for dependency in worker['loaded_dependency_sources']:
            name = dependency['name']; expected = build['files'][name]
            if (dependency['sha256'] != expected or digest(Path(dependency['adjacent_path'])) != expected
                    or digest(Path(dependency['loaded_module_path'])) != expected): raise ValueError('实际已载DLL字节不同')
        if len(worker['loaded_dependency_sources']) != 5: raise ValueError('实际已载五DLL记录不全')
        for record in worker['records']:
            variant = record['variant']; threads = record['requested_threads']
            if (variant not in ('baseline', 'candidate') or threads not in (1, 4) or record['images'] != 100
                    or record['stages'] != 4 or record['kernel'] != 'avx2' or record['library_revision'] != 2
                    or record['library_sha256'] != (old_sha if variant == 'baseline' else primary_sha)
                    or record['native_preflight_sha256'] != native['photos']['output_sha256']
                    or record['model_accounting_bytes'] != native['model_accounting_bytes']['actual_four']
                    or record['serialized_input_bytes'] != prior['serialized_four_input_bytes']
                    or len(record['apply_seconds']) != 5 or len(record['copy_apply_seconds']) != 5):
                raise ValueError('计时原轮次/模型/后端/输出身份不同')
            for repeat, (apply, total) in enumerate(zip(record['apply_seconds'], record['copy_apply_seconds'])):
                if not math.isfinite(apply) or not math.isfinite(total) or apply <= 0 or total < apply:
                    raise ValueError('计时值非正/非有限或总耗时小于apply')
                raw_rows.append({'worker': index, 'variant': variant, 'requested_threads': threads, 'repeat': repeat,
                    'images': 100, 'stages': 4, 'apply_seconds': apply, 'copy_apply_seconds': total})
        workers.append(worker)
    if len({w['source_sha256'] for w in workers}) != 1 or len({w['pid'] for w in workers}) != 4:
        raise ValueError('原图组不相同或不是四独立进程')
    failures = []; summaries = []; paired = []
    for threads in gates['threads']:
        per = [{r['variant']: r for r in w['records'] if r['requested_threads'] == threads} for w in workers]
        if any(set(r) != {'baseline', 'candidate'} for r in per): raise ValueError('线程/配置记录不全')
        apply_ratio = []; total_ratio = []
        for index, record in enumerate(per):
            med_apply = {v: statistics.median(record[v]['apply_seconds']) for v in ('baseline', 'candidate')}
            med_total = {v: statistics.median(record[v]['copy_apply_seconds']) for v in ('baseline', 'candidate')}
            a = med_apply['candidate']/med_apply['baseline']; t = med_total['candidate']/med_total['baseline']
            apply_ratio.append(a); total_ratio.append(t)
            process_rows.append({'worker': index, 'requested_threads': threads,
                'baseline_apply_ms_per_image': 10*med_apply['baseline'], 'candidate_apply_ms_per_image': 10*med_apply['candidate'],
                'baseline_copy_apply_ms_per_image': 10*med_total['baseline'], 'candidate_copy_apply_ms_per_image': 10*med_total['candidate'],
                'apply_ratio': a, 'copy_apply_ratio': t})
        saved = next(r for r in result['paired'] if r['requested_threads'] == threads)
        for a, b in zip(apply_ratio, saved['process_ratios']): equal(a, b)
        equal(statistics.median(apply_ratio), saved['median_ratio'])
        if statistics.median(apply_ratio) > gates['apply_ratio_max_by_thread']: failures.append(f'threads{threads}.apply_median')
        if max(apply_ratio) > gates['apply_ratio_max_in_any_process']: failures.append(f'threads{threads}.apply_any_process')
        if statistics.median(total_ratio) > gates['copy_apply_median_ratio_max_by_thread']: failures.append(f'threads{threads}.copy_apply_median')
        paired.append({'requested_threads': threads, 'process_apply_ratios': apply_ratio,
            'median_apply_ratio': statistics.median(apply_ratio), 'apply_reduction_percent': 100*(1-statistics.median(apply_ratio)),
            'worst_process_apply_ratio': max(apply_ratio), 'process_copy_apply_ratios': total_ratio,
            'median_copy_apply_ratio': statistics.median(total_ratio), 'copy_apply_reduction_percent': 100*(1-statistics.median(total_ratio))})
        for variant in ('baseline', 'candidate'):
            a = [statistics.median(r[variant]['apply_seconds'])*10 for r in per]
            t = [statistics.median(r[variant]['copy_apply_seconds'])*10 for r in per]
            saved = next(r for r in result['summary'] if r['requested_threads'] == threads and r['variant'] == variant)
            for left, right in zip(a, saved['process_medians_apply_ms_per_image']): equal(left, right)
            equal(statistics.median(a), saved['median_apply_ms_per_image']); equal(statistics.median(t), saved['median_copy_apply_ms_per_image'])
            equal(min(a), saved['process_median_range_ms_per_image'][0]); equal(max(a), saved['process_median_range_ms_per_image'][1])
            summaries.append({'variant': variant, 'requested_threads': threads,
                'median_apply_ms_per_image': statistics.median(a), 'apply_process_min_ms_per_image': min(a), 'apply_process_max_ms_per_image': max(a),
                'median_copy_apply_ms_per_image': statistics.median(t), 'model_accounting_bytes': saved['model_accounting_bytes'],
                'serialized_input_bytes': saved['serialized_input_bytes']})
    inherited_models = ROOT/'report/data/cinema-current-anchor-accept-v1/models.zip'
    inherited_manifest = read(inherited_models.parent/'manifest.json')
    if digest(inherited_models) != inherited_manifest['files']['models.zip']['sha256']: raise ValueError('复用模型包SHA不同')
    with zipfile.ZipFile(inherited_models) as archive:
        member_hashes = {name: hashlib.sha256(archive.read(name)).hexdigest() for name in archive.namelist()}
    for spec in [native_plan['inputs']['model'], native_plan['inputs']['base'], native_plan['inputs']['sidecar'], *native_plan['suffix_models']]:
        if spec['sha256'] not in member_hashes.values(): raise ValueError('复用包缺少冻结模型：'+spec['path'])
    core = ROOT/'build-channel-research/libjshc_core.a'
    if digest(core) != build['static_core_sha256']: raise ValueError('静态核心与实际构建不同')
    out.mkdir(parents=True)
    audit = {'purpose': __doc__, 'performance_accepted': not failures, 'failures': failures,
        'frozen_gates': gates, 'paired_recomputed': paired, 'raw_rounds': len(raw_rows), 'independent_processes': 4,
        'copy_apply_formula': 'median_i(median_5(candidate_copy_apply_i)/median_5(v3_copy_apply_i))；不是两端四进程中位数之比',
        'source_and_snapshot_sha_verified': True, 'native_identity_recomputed': True, 'same_a399_model_and_suffixes': True,
        'same_preloaded_source_sha256': workers[0]['source_sha256'], 'hot_path_layout_proven_from_sidecar_bytes': True,
        'candidate_library_sha256': primary_sha, 'baseline_library_sha256': old_sha,
        'native_results_sha256': digest(native_dir/'results.json'), 'runtime_results_sha256': digest(runtime_dir/'results.json'),
        'build_sha256': digest(build_dir/'build.json'), 'contract_sha256': digest(contract_dir/'results.json'),
        'prior_accuracy_results_sha256': digest(check_spec(native_plan['inputs']['prior_full'])),
        'reused_model_bundle': {'path': inherited_models.relative_to(ROOT).as_posix(), 'sha256': digest(inherited_models)},
        'additional_native_or_pixel_or_performance_or_fit_calls': 0,
        'loaded_module_scope': '新主DLL及四个共用GCC依赖均记录实际已载路径/字节SHA；v3主库由冻结完整路径ct.CDLL加载及worker SHA绑定，未另记录GetModuleFileNameW枚举旧主库。',
        'limits': '只对原回执做统计/来源审查，不重跑数值；本机未控频温/绑核，不给统计显著性或跨机器保证，不跨阶段与af974绝对耗时拼接。'}
    save(out/'gate-audit.json', audit)
    csv_file(out/'performance.csv', list(summaries[0]), summaries)
    csv_file(out/'process-pairs.csv', list(process_rows[0]), process_rows)
    csv_file(out/'raw-rounds.csv', list(raw_rows[0]), raw_rows)
    for folder, name in [(build_dir, 'build.json'), (contract_dir, 'contract-results.json'),
            (native_dir, 'native-results.json'), (runtime_dir, 'runtime-results.json')]:
        source = folder/('build.json' if folder == build_dir else 'results.json'); shutil.copyfile(source, out/name)
    source_paths = [Path(__file__), policy_path, native_plan_path, runtime_plan_path,
        ROOT/'docs/stages/2026-10-19-channel-runtime-specialized.md']
    with zipfile.ZipFile(out/'evidence.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for folder in (build_dir, contract_dir, native_dir, runtime_dir):
            for path in sorted(folder.iterdir()):
                if path.is_file() and path.suffix in ('.json', '.zip', '.log', '.slut', '.bin'):
                    archive.write(path, path.relative_to(ROOT).as_posix())
        for path in source_paths: archive.write(path, path.relative_to(ROOT).as_posix())
    dll = check_spec(plan['inputs']['library']); old = check_spec(plan['inputs']['baseline_library'])
    with zipfile.ZipFile(out/'binaries-and-core.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in [dll, old, core, *[dll.parent/name for name in build['files'] if name != dll.name]]:
            expected = build['static_core_sha256'] if path == core else old_sha if path == old else build['files'][path.name]
            if digest(path) != expected: raise ValueError('二进制/依赖SHA不同')
            archive.write(path, path.relative_to(ROOT).as_posix())
    table = '\n'.join(f"| {r['requested_threads']} | {r['apply_reduction_percent']:.6f}% | {r['median_apply_ratio']:.12f} | {r['copy_apply_reduction_percent']:.6f}% | {r['median_copy_apply_ratio']:.12f} |" for r in paired)
    (out/'README.md').write_text(f'''# 固定四级AVX2专门化：同一a399模型的后端验收

Agent：Codex；Operator：WyEhNf；状态：唯一候选构建、44组集中合同、完整native等价和固定性能门禁均通过；仅本地归档，未PR/push，默认不变。

本阶段只改变内核的编译期共享分派和四级循环展开。对照与候选均为a399首级+933a/95cb/932f后三模型、同一sidecar和原100张1024×768 RGB8；对照库7ceb30d…，候选库507b51a…。原v3、CMake、标量壳和核心未修改。没有新拟合、数据、权重或参数扫描，没有使用已失败reuse源码。

完整256³单级及实际四级的标量1/AVX2请求4与已验独立整数oracle流零差，100图输出SHA逐图一致。本阶段不重新选择精度，复用先前已完整验收的同一模型；精度证据见[原报告](../cinema-current-anchor-accept-v1/README.md)。模型只引用[原models.zip](../cinema-current-anchor-accept-v1/models.zip)，SHA `{digest(inherited_models)}`，本包不重复。

4个新进程串行AB/BA/BA/AB，线程顺序[1,4]/[4,1]/[1,4]/[4,1]，每配置5次完整100图，预加载235929600字节并逐配置预热/核SHA。apply与copy+apply分列，排除模型加载、文件IO、图像解码/编码和hash。两种比值都先算每进程5轮中位数之比，再取四进程比值中位数；不能用两端汇总中位数相除。

| 请求线程 | apply时间下降 | apply配对比 | copy+apply时间下降 | copy+apply配对比 |
|---|---:|---:|---:|---:|
{table}

原门槛为1/4线程apply配对比均≤0.97、任何进程≤1.02、copy+apply配对比≤1，全部通过，见`gate-audit.json`。`performance.csv`列绝对摊销统计和进程范围，`process-pairs.csv`列各进程配对中位数，`raw-rounds.csv`保留80个原轮次；全部原worker JSON/日志另在`evidence.zip`。这里时间下降率不是吞吐提升率。

环境：Windows11 26200 x64、Ryzen9 8945HX 16c32t/32GB，MinGW GCC15.2.0 Release -O3 -DNDEBUG、C++17/OpenMP；仅AVX2 TU带-mavx2，dispatcher保持baseline ISA；Python3.12.14/NumPy1.26.4/Pillow10.4。OMP_DYNAMIC=FALSE，BLAS/MKL/OMP环境1，原生显式请求1或4线程。新主DLL及共用4依赖的实际已载路径/SHA保存于run/worker；旧主DLL按冻结完整路径加载和SHA绑定，未额外枚举旧主模块路径。

`evidence.zip`收录构建、44合同、完整native及性能的全部run/results/worker轮次/日志和源码ZIP、冻结计划、合成合同输入；`binaries-and-core.zip`收录两主DLL、4依赖及实际链接静态核心，各有原始SHA。独立builder及其源码ZIP可复现本候选，不依赖修改公共CMake。`manifest.json`校验本包原字节，`commands.txt`区分历史测量命令与本次只读归档命令。归档脚本只重算旧回执，没有新native、像素、性能或拟合调用。

未锁频/控温/绑核，四进程范围不是置信区间；100图摊销ms/图不是单图延迟或尾延迟。上一阶段v3新表示相对af974约慢46%的结论仍只属于那组不同模型配对；本轮不能跨阶段用绝对耗时或乘比值推算相对af974的最终速度。没有后续硬件变体，未推广公共CLI/GUI/C99或默认，实验sidecar不是官方已认可格式。四张创意LUT只作数值串联，色彩域匹配未证明，无官方数据/Threshold或官方分数。
''', encoding='utf-8', newline='\n')
    commands = '''以下为已经执行的历史命令，归档时不再次运行：
artifacts/error-study-py312/Scripts/python.exe scripts/build_channel_specialized.py --plan experiments/channel-runtime-specialized-v1.json --output artifacts/channel-native-specialized-v1
artifacts/error-study-py312/Scripts/python.exe scripts/verify_channel_specialized.py --plan experiments/channel-runtime-specialized-v1.json --library artifacts/channel-native-specialized-v1/jshc_channel_specialized.dll --output artifacts/channel-native-specialized-contract-v1
artifacts/error-study-py312/Scripts/python.exe scripts/accept_cinema_specialized_native.py --plan experiments/cinema-specialized-native-v1.json --output artifacts/cinema-specialized-native-v1
artifacts/error-study-py312/Scripts/python.exe scripts/bench_cinema_specialized.py --plan experiments/cinema-specialized-runtime-v1.json --output artifacts/cinema-specialized-runtime-v1

实际构建参数/环境见build.json和各run/worker；关键环境OMP_NUM_THREADS=1、OMP_DYNAMIC=FALSE、OPENBLAS_NUM_THREADS=1、MKL_NUM_THREADS=1。

本次仅从既有文件复算/归档，没有调用以上测量命令：
artifacts/error-study-py312/Scripts/python.exe scripts/archive_channel_specialized.py --output report/data/channel-runtime-specialized-v1
'''
    (out/'commands.txt').write_text(commands, encoding='utf-8', newline='\n')
    save(out/'manifest.json', {'purpose': '唯一固定四级候选完整后端证据；原字节SHA清单，manifest本身不自包含',
        'source_archive_script_sha256': digest(Path(__file__)),
        'reused_model_bundle': audit['reused_model_bundle'],
        'files': {p.name: {'sha256': digest(p), 'bytes': p.stat().st_size} for p in sorted(out.iterdir()) if p.is_file()}})
    print(json.dumps({'performance_accepted': not failures, 'failures': failures, 'paired': paired,
        'archive_bytes': sum(p.stat().st_size for p in out.iterdir()), 'manifest_sha256': digest(out/'manifest.json')}, ensure_ascii=False))


if __name__ == '__main__': main()
