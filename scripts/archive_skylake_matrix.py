"""只读归档四后端矩阵并独立复算门槛；不加载原生库、不重跑像素或计时。"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import shutil
import statistics
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ROLES = ('original', 'delta', 'cache', 'combo')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def identity(path):
    return {'sha256': digest(path), 'bytes': Path(path).stat().st_size}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('bundle', 'run', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    bundle_root = args.bundle.resolve(); run = args.run.resolve(); out = args.output.resolve()
    if out.exists():
        raise ValueError('不覆盖矩阵档案')
    bundle = read(bundle_root/'bundle-manifest.json'); final = read(run/'results.json')
    correct = read(run/'correctness.json'); policy = read(run/'performance-policy.json')
    perf = read(run/'performance.json'); workers = [read(run/f'worker{i}.json') for i in range(4)]
    for name, spec in bundle['files'].items():
        if identity(bundle_root/name) != {k: spec[k] for k in ('sha256', 'bytes')}:
            raise ValueError('输入包字节不同：'+name)
    if (not final['pass'] or not final['correctness_passed'] or not final['performance_measured']
        or not correct['pass'] or correct['finite_backend_offset_comparisons'] != 4224
        or correct['diagnostic_negative_checks'] != 64 or correct['byte_mismatches'] or correct['sentinel_mismatches']
        or not correct['driver_callback_failure_aborted'] or len(correct['driver_negative_contract']) != 14
        or any(row['returncode'] != 1 for row in correct['driver_negative_contract'])):
        raise ValueError('集中正确性未完成')
    if (final['correctness_sha256'] != digest(run/'correctness.json')
        or final['policy_sha256'] != digest(run/'policy.json')
        or perf['policy_sha256'] != digest(run/'performance-policy.json')
        or final['bundle_sha256'] != digest(bundle_root/'bundle-manifest.json')
        or policy['correctness']['sha256'] != final['correctness_sha256']
        or correct['policy_sha256'] != digest(run/'policy.json')
        or policy['validation_policy_sha256'] != correct['policy_sha256']):
        raise ValueError('门槛、库、正确性与包身份不相连')
    plan = read(bundle_root/bundle['plans']['uncached'])
    for key, sha in correct['full_output_sha256'].items():
        expected = (bundle['files'][bundle['single_oracle_stream']]['sha256'] if '_single_' in key
                    else plan['fixed_inputs']['cube']['sha256'])
        if sha != expected or correct['full_domain_pixels_per_configuration'][key] != 256**3:
            raise ValueError('完整色域预期不同：'+key)
    if len(correct['full_output_sha256']) != 24 or len(correct['photos']) != 16:
        raise ValueError('完整配置数量不同')
    if any(row['output_sha256'] != bundle['photo_output_sha256'] for row in correct['photos']):
        raise ValueError('逐图调度金标准不同')
    groups = 0
    for index, worker in enumerate(workers):
        if (worker['worker_index'] != index or worker['policy_sha256'] != perf['policy_sha256']
            or worker['libraries'] != correct['libraries'] or len(worker['records']) != 16
            or worker['photo_source_sha256'] != correct['photo_source_sha256']):
            raise ValueError('进程身份不同')
        for row in worker['records']:
            segments = 100 if row['mode'] else 1
            if (row['repeats'] != 5 or row['images'] != 100 or row['output_sha256'] != bundle['photo_output_sha256']
                or row['library'] != worker['libraries'][row['role']]):
                raise ValueError('原始轮次配置不同')
            for kind in ('apply', 'copy_apply'):
                raw = row['segment_'+kind+'_seconds']; rounds = row['round_'+kind+'_seconds']
                if len(raw) != 5*segments or any(not math.isfinite(x) or x <= 0 for x in raw):
                    raise ValueError('原始分段计时无效')
                if [sum(raw[i*segments:(i+1)*segments]) for i in range(5)] != rounds:
                    raise ValueError('分段不能复算整轮')
            if (len(row['round_wall_seconds']) != 5
                or any(not 0 < a <= c <= w for a, c, w in zip(row['round_apply_seconds'], row['round_copy_apply_seconds'], row['round_wall_seconds']))):
                raise ValueError('计时范围关系不符')
            groups += 5
    if groups != 320:
        raise ValueError('并非唯一320轮矩阵')
    gates = policy['protocol']['gates']; comparisons = []
    for old in perf['comparisons']:
        a, b = old['reference'], old['candidate']; rows = []
        for worker in workers:
            selected = {r['role']: r for r in worker['records'] if (r['threads'], r['mode']) == (old['threads'], old['mode'])}
            if set(selected) != set(ROLES):
                raise ValueError('角色不完整')
            rows.append(selected)
        ratios = {name: [statistics.median(r[b][key])/statistics.median(r[a][key]) for r in rows]
                  for name, key in (('apply', 'round_apply_seconds'), ('copy_apply', 'round_copy_apply_seconds'), ('wall', 'round_wall_seconds'))}
        ratios['prepared'] = [r[b]['prepare_plus_first_100_copy_apply_seconds']/r[a]['prepare_plus_first_100_copy_apply_seconds'] for r in rows]
        medians = {k: statistics.median(v) for k, v in ratios.items()}
        checks = [medians['apply'] <= gates['median_apply_ratio_max'], max(ratios['apply']) <= gates['any_process_apply_ratio_max'],
                  medians['copy_apply'] <= gates['median_copy_apply_ratio_max'], medians['prepared'] <= gates['median_prepare_plus_100_ratio_max']]
        if ratios != old['process_ratios'] or medians != old['median_ratios'] or all(checks) != old['passed_host_gates']:
            raise ValueError('独立门槛复算不同')
        comparisons.append({'reference': a, 'candidate': b, 'threads': old['threads'], 'mode': old['mode'],
                            'median_ratios': medians, 'max_process_apply_ratio': max(ratios['apply']), 'gate_checks': checks,
                            'passed_host_gates': all(checks), 'failed_gates': old['failed_gates']})
    adoption = {a+'->'+b: all(r['passed_host_gates'] for r in comparisons if (r['reference'], r['candidate']) == (a, b))
                for a, b in policy['protocol']['pairs']}
    if len(comparisons) != 16 or adoption != perf['adoption_by_comparison'] or adoption != final['adoption_by_comparison']:
        raise ValueError('采用结论与完整矩阵不一致')
    out.mkdir(parents=True)
    for p in sorted(run.glob('*.json')):
        shutil.copyfile(p, out/p.name)
    for key in ('uncached', 'cached'):
        folder = run/('backend-'+key)
        for p in sorted(folder.glob('*.json')):
            shutil.copyfile(p, out/(key+'-'+p.name))
        shutil.copyfile(folder/'measured-source.zip', out/(key+'-measured-source.zip'))
    shutil.copyfile(bundle_root/'bundle-manifest.json', out/'bundle-manifest.json')
    for key, name in bundle['plans'].items():
        shutil.copyfile(bundle_root/name, out/(key+'-plan.json'))
    shutil.copyfile(run/'driver/compile_commands.json', out/'driver-compile_commands.json')
    shutil.copyfile(bundle_root/bundle['cache_gold_generation'], out/'cache-gold-generation.json')
    # Linux绝对路径在Windows归档时由构建目录定位；SHA必须仍与实际加载回执一致。
    binaries = []
    with zipfile.ZipFile(out/'binaries.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for role, spec in correct['libraries'].items():
            pair = bundle['roles'][role]['pair']; p = run/('backend-'+pair)/Path(spec['path']).name
            if digest(p) != spec['sha256']:
                raise ValueError('实际库不同：'+role)
            name = role+'/'+p.name; archive.write(p, name); binaries.append({'role': role, 'archive_path': name, **identity(p)})
        p = run/'driver'/Path(policy['driver']['path']).name
        if digest(p) != policy['driver']['sha256']:
            raise ValueError('原生驱动不同')
        archive.write(p, 'driver/'+p.name); binaries.append({'role': 'driver', 'archive_path': 'driver/'+p.name, **identity(p)})
    excluded = {bundle['photo_pixels'], bundle['single_oracle_stream'], plan['fixed_inputs']['cube']['path']}
    with zipfile.ZipFile(out/'frozen-small-packet.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(set(bundle['files'])-excluded):
            archive.write(bundle_root/name, name)
        archive.write(bundle_root/'bundle-manifest.json', 'bundle-manifest.json')
    save(out/'recalculation.json', {'purpose': __doc__, 'pass': True, 'environment': {'python': sys.version, 'platform': platform.platform()},
        'script_sha256': digest(Path(__file__)), 'source_results_sha256': digest(run/'results.json'), 'hundred_image_groups': groups,
        'comparisons': comparisons, 'adoption_by_comparison': adoption, 'binaries': binaries,
        'new_fits': 0, 'native_calls': 0, 'performance_calls': 0,
        'scope': '静态复核现有回执及门槛；不删样本、不重测、不改变候选采用结论'})
    save(out/'packet-identity.json', {'bundle_manifest': identity(bundle_root/'bundle-manifest.json'),
        'local_transfer_zip': identity(Path(str(bundle_root)+'.zip')), 'excluded_large_streams': {n: bundle['files'][n] for n in sorted(excluded)},
        'scope': '三个大流保留在本地固定传输ZIP；其余固定源码与小输入保存于frozen-small-packet.zip，系统动态库只记录实际路径和SHA'})
    save(out/'manifest.json', {'purpose': __doc__, 'files': {p.name: identity(p) for p in sorted(out.iterdir()) if p.is_file()},
        'scope': '实际WSL/Linux AMD四库正确性及320轮比较；不是Skylake或官方验收；性能失败项原样保留'})
    print(json.dumps({'archive_completed': True, 'hundred_image_groups': groups, 'adoption_by_comparison': adoption}, ensure_ascii=False))


if __name__ == '__main__':
    main()
