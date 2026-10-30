"""96质量/正式独立冻结；复用已验helper并核实际依赖源，不构建。"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAIL = Path('F:/Hackathon/worktrees/p16-tail-20261023')


def identity(path):
    path = path.resolve()
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('phase', choices=('quality', 'performance'))
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError('96单版冻结不覆盖')
    baseline = ROOT / 'experiments/p16-palette-prepare-performance-v1.json'
    assert identity(baseline)['sha256'] == '2b802c6353ef0fc2a185ae435c1fc3786d38667308e2a0ca31a3df895efd1ed1'
    plan = json.loads(baseline.read_text(encoding='utf-8'))
    sources = {}
    closed = json.loads((ROOT / 'report/data/p16-palette-prepare-v1/identity.json').read_text(encoding='utf-8'))
    for row in closed['execution_dependencies']:
        path = ROOT / row['path']
        assert identity(path)['sha256'] == row['execution_sha256']
        sources[str(path.resolve())] = identity(path)
    build = TAIL / 'artifacts/p16-omp-affinity-control-build-v2'
    quality = TAIL / 'artifacts/p16-omp-affinity-control-quality-v2'
    helper = build / 'libp16_omp_affinity.dll'
    assert identity(helper)['sha256'] == 'fbf717dd92e0f38e93394c88255ca9a36f9fab48ef30878b0200f9f4c4a0901f'
    receipt = json.loads((build / 'build-receipt.json').read_text(encoding='utf-8'))
    assert receipt['return_code'] == 0 and receipt['sources_unchanged'] and receipt['library_sha256'] == identity(helper)['sha256']
    root_proof = json.loads((quality / 'results.json').read_text(encoding='utf-8'))
    assert root_proof['passed'] and root_proof['rejections'] == 6 and root_proof['performance_calls'] == 0
    assert root_proof['frozen_sha256'] == identity(quality / 'frozen.json')['sha256']
    for filename, key in ((build / 'frozen.json', 'sources_sha256'), (quality / 'frozen.json', 'source_sha256')):
        for path, expected in json.loads(filename.read_text(encoding='utf-8'))[key].items():
            row = identity(Path(path));assert row['sha256'] == expected
            sources[row['path']] = row
    own = [*list((ROOT / 'experiments/p16-omp-policy-v1').glob('*')),
        *[ROOT / 'scripts' / name for name in ('p16_omp_policy_support.py', 'bench_p16_omp_policy.py',
            'audit_p16_omp_policy.py', 'freeze_p16_omp_policy.py')],
        *[p for p in build.iterdir() if p.is_file()], quality / 'frozen.json', quality / 'results.json',
        TAIL / 'experiments/p16-omp-affinity-control-v1/control.cpp',
        TAIL / 'experiments/p16-omp-affinity-control-v1/plan-v2.md',
        TAIL / 'report/data/p16-omp-affinity-control-v1/manifest.json',
        TAIL / 'report/data/p16-omp-affinity-control-v1/independent-check.json',
        ROOT / 'report/data/p16-palette-prepare-v1/identity.json', baseline,
        Path(plan['quality_proof']['path']),
        *[Path('E:/mingw64/bin') / name for name in ('libgomp-1.dll', 'libstdc++-6.dll', 'libgcc_s_seh-1.dll', 'libwinpthread-1.dll')],
        Path(receipt['command'][0])]
    for path in own:
        row = identity(path);sources[row['path']] = row
    photograph = json.loads(Path(plan['photo_model_plan']['path']).read_text(encoding='utf-8'))
    assert identity(Path(plan['photo_model_plan']['path']))['sha256'] == plan['photo_model_plan']['sha256']
    manifest = json.loads(Path(photograph['manifest']['path']).read_text(encoding='utf-8'))
    assert identity(Path(photograph['manifest']['path']))['sha256'] == photograph['manifest']['sha256']
    first = manifest['images'][0]['evaluation']
    first_path = Path(photograph['data_root']) / first['path']
    assert identity(first_path)['sha256'] == first['sha256']
    for path in (Path(plan['photo_model_plan']['path']), Path(photograph['manifest']['path']), first_path):
        row = identity(path);sources[row['path']] = row
    for row in sources.values():
        assert identity(Path(row['path'])) == row
    plan['runtime_quality_proof'] = plan.pop('quality_proof')
    for key in ('source_freeze', 'images', 'hot_images', 'default_images', 'cold_scope', 'hot_scope',
                'sample_unit', 'rss_scope', 'interpretation', 'image_orders', 'thread_orders', 'source_sha256'):
        plan.pop(key, None)
    plan['photo_expected'] = [row for row in plan['photo_expected'] if row['images'] == 1]
    plan.update({'purpose': '96独立默认N1 U/P原因诊断，不恢复旧资格', 'mode': a.phase,
        'sources': list(sources.values()), 'root_helper_source_commit': '77cdbfc',
        'affinity_helper': identity(helper), 'helper_quality_proof': identity(quality / 'results.json'),
        'helper_build_receipt': identity(build / 'build-receipt.json'),
        'helper_quality_frozen': identity(quality / 'frozen.json'),
        'libgomp': identity(Path('E:/mingw64/bin/libgomp-1.dll')),
        'helper_rejections': {'count': 6, 'scope': '复用root质量v2原件，不称96新重复拒绝'},
        'script_sha256': identity(ROOT / 'scripts/bench_p16_omp_policy.py')['sha256'],
        'audit_sha256': identity(ROOT / 'scripts/audit_p16_omp_policy.py')['sha256'],
        'first_source_sha256': first['pixel_sha256'], 'first_source_file': identity(first_path),
        'repeats': 1 if a.phase == 'quality' else 63, 'warmup': 2,
        'policy_orders': [['U', 'P', 'P', 'U'], ['P', 'U', 'U', 'P'], ['U', 'P', 'P', 'U'], ['P', 'U', 'U', 'P']],
        'process_order': [{'worker': i, 'threads': t} for i in range(4) for t in ((1, 4) if i % 2 == 0 else (4, 1))],
        'scope': '8fresh进程，T1/T4分开；6句柄/地址不变；48prewarm+1152warm/formal/AA=1200实际SHA。helper任何非零停止不修复。setup只描述无cold，统计保留32角色比/24P-U/16交互及全部AA。'})
    if a.phase == 'performance':
        quality_plan = ROOT / 'experiments/p16-omp-policy-quality-v1.json'
        proof = ROOT / 'artifacts/p16-omp-policy-quality-v1/results.json'
        q = json.loads(proof.read_text(encoding='utf-8'))
        assert q['quality_only'] and q['performance_calls'] == 0 and q['actual_output_sha_checks'] == 1200
        plan['independent_quality_proof'] = identity(proof)
        plan['independent_quality_plan'] = identity(quality_plan)
        plan['sources'] += [identity(quality_plan)]
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(identity(a.output), ensure_ascii=False))


if __name__ == '__main__':
    main()
