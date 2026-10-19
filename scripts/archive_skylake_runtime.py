"""只归档既有Skylake研究回执并复算性能门槛，不重新调用像素核或性能基准。"""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import statistics
import zipfile
from skylake_support import ROOT, digest, read, save


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--contract', type=Path, required=True)
    parser.add_argument('--cache-contract', type=Path)
    parser.add_argument('--full', type=Path, required=True)
    parser.add_argument('--performance', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); out = args.output.resolve()
    if out.exists():
        raise ValueError('不覆盖归档')
    build = read(args.build/'build.json'); full = read(args.full/'results.json')
    contract = read(args.contract/'results.json'); perf = read(args.performance/'results.json')
    policy = read(args.performance/'run.json')['policy']
    if not contract['pass'] or not full['pass'] or full['build_sha256'] != digest(args.build/'build.json'):
        raise ValueError('原正确性验收身份不同')
    workers = [read(args.performance/f'worker{i}.json') for i in range(4)]
    failures = []; recomputed = []
    for threads in (1, 4):
        matched = [{r['variant']: r for r in w['records'] if r['requested_threads'] == threads} for w in workers]
        ratios = [statistics.median(w['candidate']['apply_seconds'])/statistics.median(w['reference']['apply_seconds']) for w in matched]
        total = [statistics.median(w['candidate']['copy_apply_seconds'])/statistics.median(w['reference']['copy_apply_seconds']) for w in matched]
        old = next(p for p in perf['paired'] if p['requested_threads'] == threads)
        if ratios != old['process_apply_ratios'] or total != old['process_copy_apply_ratios']:
            raise ValueError('原始轮次不能精确复现配对统计')
        gates = policy['adoption_gate']
        if statistics.median(ratios) > gates['median_apply_ratio_max']: failures.append(f'{threads}线程apply中位比未达门槛')
        if max(ratios) > gates['any_process_apply_ratio_max']: failures.append(f'{threads}线程至少一个进程退化超限')
        if statistics.median(total) > gates['median_copy_apply_ratio_max']: failures.append(f'{threads}线程copy+apply退化')
        if 'median_prepare_plus_100_ratio_max' in gates:
            prepared = [w['candidate']['prepare_plus_first_100_copy_apply_seconds']/w['reference']['prepare_plus_first_100_copy_apply_seconds'] for w in matched]
            if prepared != old['process_prepare_plus_100_copy_apply_ratios']:
                raise ValueError('准备+100图配对统计不能复算')
            if statistics.median(prepared) > gates['median_prepare_plus_100_ratio_max']: failures.append(f'{threads}线程准备+100图退化')
        recomputed.append({'requested_threads': threads, 'median_apply_ratio': statistics.median(ratios),
            'max_process_apply_ratio': max(ratios), 'median_copy_apply_ratio': statistics.median(total)})
    if failures != perf['failed_gates'] or (not failures) != perf['accepted_on_this_host']:
        raise ValueError('性能门槛结论复算不同')
    out.mkdir(parents=True)
    mappings = [(args.plan, 'plan.json')]
    folders = [(args.build, 'build'), (args.contract, 'contract'), (args.full, 'full'), (args.performance, 'performance')]
    if args.cache_contract:
        folders.append((args.cache_contract, 'cache-contract'))
    for folder, prefix in folders:
        for p in folder.iterdir():
            if p.is_file() and p.suffix in ('.json', '.log', '.zip'):
                mappings.append((p, prefix+'-'+p.name))
    for source, name in mappings:
        shutil.copyfile(source, out/name)
    with zipfile.ZipFile(out/'assembly.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for p in sorted(args.build.glob('*.asm')):
            archive.write(p, p.name)
    binaries = {Path(v['path']).resolve() for v in build['libraries'].values()}
    binaries |= {(args.build/name).resolve() for name in build['dependencies']}
    binaries |= {p.resolve() for p in args.build.glob('core/*jshc_core.a')}
    with zipfile.ZipFile(out/'binaries-and-core.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for p in sorted(binaries): archive.write(p, p.name)
    save(out/'gate-recalculation.json', {'purpose': __doc__, 'pass': True, 'paired': recomputed,
        'accepted_on_this_host': not failures, 'failed_gates': failures, 'new_fits': 0, 'new_native_calls': 0,
        'new_performance_calls': 0, 'script_sha256': digest(Path(__file__)), 'source_results_sha256': digest(args.performance/'results.json')})
    save(out/'manifest.json', {'purpose': __doc__, 'files': {p.name: {'sha256': digest(p), 'bytes': p.stat().st_size}
        for p in sorted(out.iterdir()) if p.is_file()}, 'models': '复用PR42的report/data/cinema-current-anchor-accept-v1/models.zip，输入身份见plan/full结果',
        'scope': '归档及统计复算；原始测试范围以contract/full/performance回执为准，未运行新实验。'})
    print('归档完成；本机采用：', not failures, '文件数：', len(list(out.iterdir())), flush=True)


if __name__ == '__main__':
    main()
