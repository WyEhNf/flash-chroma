"""97隔离shared无检查核来源/质量冻结；不构建或加载模型。"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def identity(path):
    return {'path': str(path.resolve()), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('phase', choices=('source', 'quality'))
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError('97单版冻结不覆盖')
    prior = json.loads((ROOT / 'report/data/p16-palette-prepare-v1/identity.json').read_text(encoding='utf-8'))
    sources = {}
    for row in prior['execution_dependencies']:
        path = ROOT / row['path']
        value = identity(path)
        assert value['sha256'] == row['execution_sha256']
        sources[value['path']] = value
    own = [*list((ROOT / 'experiments/p16-shared-proven-runtime').glob('*')),
        *[ROOT / 'scripts' / n for n in ('generate_p16_shared_proven.py', 'build_p16_shared_proven.py',
            'freeze_p16_shared_proven.py', 'verify_p16_shared_proven.py')],
        ROOT / 'report/data/skylake-domain-template-static-v1/analysis-results.json',
        ROOT / 'docs/stages/2026-10-20-skylake-domain-proof.md']
    for path in own:
        row = identity(path)
        sources[row['path']] = row
    if a.phase == 'source':
        plan = {'purpose': '97旧15省check算术的隔离结构改进；保留其shared静态负证据',
            'parent_head': '7cf7f371979078bcfda7e2958ec9cf31c92df465', 'sources': list(sources.values()),
            'pixel_predicate': 'domain_proven && first/suffix allshared && direct/compiled empty，私有批入口',
            'unchanged': ['原domain_fast_enabled', '2^26及默认prepare', '所有模型/轴/舍入',
                '旧checked fallback TU源', '非shared/direct路径', '生产C ABI/Handle字段'],
            'static_negative': '15 shared/shared proven MCA17935/14026=1.2786967，更差；不将更少指令视作收益。'}
    else:
        frozen_path = ROOT / 'experiments/p16-shared-proven-static-v1.json'
        frozen = json.loads(frozen_path.read_text(encoding='utf-8'))
        assert frozen['sources'] == list(sources.values())
        old = ROOT / 'experiments/p16-palette-prepare-quality-v1.json'
        assert identity(old)['sha256'] == '98aca4c52054d412962b7fbf40773b67d3b085d414dc5c6dcd6abdb3e55772b1'
        plan = json.loads(old.read_text(encoding='utf-8'))
        build = ROOT / 'artifacts/p16-shared-proven-build-v1'
        receipt = json.loads((build / 'build-receipt.json').read_text(encoding='utf-8'))
        assert receipt['return_code'] == 0 and receipt['all_old_pixel_objects_byte_identical']
        plan.update({'purpose': '97同87/95/97完整质量；显式新私有核+旧回退/默认/高hint',
            'source_freeze': identity(frozen_path), 'sources': list(sources.values()),
            'libraries': {'reference': plan['libraries']['reference'],
                'previous': identity(ROOT / 'artifacts/p16-palette-prepare-build-v1/libjshc_palette_prepare.dll'),
                'candidate': identity(build / 'libjshc_shared_proven.dll')},
            'dictionary_contract_executable': identity(build / 'p16_palette_contract.exe'),
            'private_kernel_contract_executable': identity(build / 'p16_shared_proven_contract.exe'),
            'script_sha256': identity(ROOT / 'scripts/verify_p16_shared_proven.py')['sha256'],
            'build_receipt': identity(build / 'build-receipt.json'),
            'boundary': '56完整流/20安全表快照/10080有限+110拒绝/16独立u64/32照片SHA；新私有核150显式合同。原domain_fast仍0，不新增生产C ABI诊断。'})
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(identity(a.output), ensure_ascii=False))


if __name__ == '__main__':
    main()
