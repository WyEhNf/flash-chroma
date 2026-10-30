"""封存290故障、291精确质量与一次正式性能；只校验和归档，不重跑像素或计时。"""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'report/data/p16-direct-sentinel-20261024'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def pack(target, members):
    hashes = {name: sha(path) for name, path in members.items()}
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, path in sorted(members.items()):
            archive.write(path, name)
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(hashes) and set(archive.namelist()) == set(hashes)
        for name, expected in hashes.items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == expected
    return hashes


def main():
    if OUT.exists():
        raise FileExistsError('不覆盖290/291归档')
    artifacts = ROOT / 'artifacts'
    quality_path = artifacts / 'p16-direct-sentinel-v2-quality-v1/results.json'
    quality = read(quality_path)
    finite = read(artifacts / 'p16-direct-sentinel-v2-contracts-v1/results.json')
    mt = read(artifacts / 'p16-direct-sentinel-v2-full-mt-v2/results.json')
    align = read(artifacts / 'p16-direct-sentinel-v2-alignment-diagnose-v2/results.json')
    plan_path = artifacts / 'p16-direct-sentinel-perf-frozen-v1/plan.json'
    plan = read(plan_path)
    perf = read(artifacts / 'p16-direct-sentinel-perf-v1/independent-check.json')
    assert quality['passed'] and quality['performance_calls'] == 0
    assert len(quality['full_matrix']) == 30 and len(quality['photo_matrix']) == 800
    assert quality['contract']['short_pattern_backend_cases'] == 972
    assert all(row['mismatches'] == 0 for row in quality['full_matrix'] + quality['photo_matrix'])
    assert all(value == 11 for value in quality['outplace_rejections'].values())
    assert finite['passed'] and finite['contract']['guarded_cases'] == 1520
    assert finite['contract']['selection_cases'] == 9 and finite['contract']['compile_id_cases'] == 3
    assert finite['contract']['scalar_cases'] == 80
    assert align['completed'] and len(align['rows']) == 128
    assert mt['passed'] and len(mt['outputs']) == 10 and len(mt['read_only_team_snapshots']) == 20
    assert all(row['mismatches'] == 0 and row['blocks'] == 256 for row in mt['outputs'])
    assert all(row['return_code'] == 0 and len(row['members']) == 4 for row in mt['read_only_team_snapshots'])
    assert perf['passed'] and perf['plan_sha256'] == sha(plan_path)
    assert perf['actual_native_output_sha_checks'] == 1284 and perf['pair_source_sha_checks'] == 208
    assert len(perf['AA']) == len(perf['comparisons']) == 624
    assert sum(row['pass'] for row in perf['AA']) == 569
    assert all(row['rejected_by_any_valid_required_below50'] and not any(row['tiers'].values())
               for row in perf['candidate_gates'].values())
    sources = {}
    for name, expected in plan['sources_sha256'].items():
        assert sha(ROOT / name) == expected, name
        sources[name] = ROOT / name
    for variant in ('p16-direct-sentinel-build-frozen-v1', 'p16-direct-sentinel-v2-build-frozen-v1'):
        frozen = read(artifacts / variant / 'frozen.json')
        for name, row in frozen['sources'].items():
            assert sha(ROOT / name) == row['sha256'] == sha(artifacts / variant / 'sources' / name), name
            sources[name] = ROOT / name
    for name in sentinel_paths():
        sources[name] = ROOT / name
    for name, path in sources.items():
        if path.suffix == '.py':
            ast.parse(path.read_bytes().decode('utf-8-sig'), filename=name)
    for row in plan['libraries'].values():
        assert sha(row['path']) == row['sha256']
    model_members = {}
    for role, spec in plan['models'].items():
        for index, path in enumerate(spec['models']):
            assert sha(path) == spec['input_sha256'][path]
            model_members[f'{role}/stage{index+1}.slut'] = Path(path)
        for index, path in enumerate(spec['sidecars']):
            if path:
                assert sha(path) == spec['input_sha256'][path]
                model_members[f'{role}/stage{index+1}-sidecar.bin'] = Path(path)
    raw = {}
    directories = [p for p in artifacts.glob('p16-direct-sentinel*') if p.is_dir()]
    directories += [artifacts / 'p16-exception-probe-build-v1']
    for directory in directories:
        for path in directory.rglob('*'):
            if path.is_file():
                raw[directory.name + '/' + path.relative_to(directory).as_posix()] = path
    for path in artifacts.glob('p16-direct-sentinel*.json'):
        raw[path.name] = path
    fault = artifacts / 'p16-direct-sentinel-session-failures-v1.json'
    assert fault.exists()
    raw[fault.name] = fault
    disassembly = artifacts / 'p16-direct-sentinel-v1-fault-disassembly.txt'
    assert disassembly.exists() and b'vmovdqa' in disassembly.read_bytes()
    raw[disassembly.name] = disassembly
    OUT.mkdir(parents=True)
    for name, path in [('quality.json', quality_path), ('finite.json', artifacts / 'p16-direct-sentinel-v2-contracts-v1/results.json'),
                       ('full-mt.json', artifacts / 'p16-direct-sentinel-v2-full-mt-v2/results.json'),
                       ('perf-independent-check.json', artifacts / 'p16-direct-sentinel-perf-v1/independent-check.json'),
                       ('perf-plan.json', plan_path), ('session-failures.json', fault)]:
        shutil.copyfile(path, OUT / name)
    hashes = {name: pack(OUT / name, members) for name, members in
              [('source.zip', sources), ('raw.zip', raw), ('models.zip', model_members)]}
    result = {'passed': True, 'purpose': '原字节和既有质量/计时汇总归档校验，不是新增数值实验',
              'source_members': len(sources), 'raw_members': len(raw), 'model_members': len(model_members),
              'full_quality_configs': 30, 'photo_quality_configs': 800, 'whole_mt_configs': 10,
              'guard_cases': 1520, 'alignment_cases': 128, 'short_cases': 972,
              'formal_output_sha_checks': 1284, 'formal_AA_passed': 569, 'formal_AA_total': 624,
              'candidate_gates': perf['candidate_gates'], 'zip_members_sha256': hashes,
              'source_sha256': {name: sha(path) for name, path in sources.items()},
              'performance_reruns': 0, 'discarded_workers': 0,
              'known_gaps': ['290初始父工具stderr没有本地原文件，只有明确标为后补的会话错误记录',
                             '291初次whole-MT观察前置失败未保存原returncode，不补造值',
                             '没有分配失败或无AVX2注入；冷首无AA；不证明任意输入最差速度']}
    write(OUT / 'independent-check.json', result)
    write(OUT / 'manifest.json', {'files': {path.name: sha(path) for path in OUT.iterdir()},
                                 'source_sha256': result['source_sha256'],
                                 'scope': '290故障不覆盖；291精确输出通过而三个宽palette模型有效速度均跌破50%，停止采用。'})
    print(json.dumps({key: result[key] for key in ['passed', 'source_members', 'raw_members', 'model_members', 'formal_AA_passed', 'formal_AA_total']}, ensure_ascii=False))


def sentinel_paths():
    names = ['scripts/generate_direct_sentinel.py', 'scripts/prepare_direct_sentinel_sources.py',
             'scripts/fork_direct_sentinel_v2.py', 'scripts/build_direct_sentinel.py',
             'scripts/build_direct_sentinel_v2.py', 'scripts/check_direct_sentinel_contracts.py',
             'scripts/check_direct_sentinel_contracts_v2.py', 'scripts/check_direct_sentinel_native.py',
             'scripts/check_direct_sentinel_native_v2.py', 'scripts/diagnose_direct_sentinel_v1.py',
             'scripts/build_exception_probe.py', 'scripts/diagnose_direct_sentinel_alignment.py',
             'scripts/prepare_direct_sentinel_alignment_v2.py', 'scripts/diagnose_direct_sentinel_alignment_v2.py',
             'scripts/prepare_direct_sentinel_alignment_v3.py', 'scripts/diagnose_direct_sentinel_alignment_v3.py',
             'scripts/check_direct_sentinel_full_mt.py', 'scripts/check_direct_sentinel_full_mt_v2.py',
             'scripts/prepare_direct_sentinel_mt_v3.py', 'scripts/check_direct_sentinel_full_mt_v3.py',
             'scripts/run_direct_sentinel_perf.py', 'scripts/audit_direct_sentinel_perf.py',
             'scripts/archive_direct_sentinel.py', 'scripts/audit_direct_sentinel_git.py',
             'experiments/p16-direct-sentinel-plan-v1.md', 'experiments/p16-direct-sentinel-perf-plan-v1.md',
             'experiments/p16-exception-probe-v1/probe.cpp']
    for folder in ('experiments/p16-direct-sentinel-runtime', 'experiments/p16-direct-sentinel-runtime-v2'):
        names += [path.relative_to(ROOT).as_posix() for path in (ROOT / folder).iterdir() if path.is_file()]
    assert len(names) == len(set(names))
    return sorted(names)


if __name__ == '__main__':
    main()
