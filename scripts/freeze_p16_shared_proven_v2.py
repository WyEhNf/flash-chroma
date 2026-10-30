"""97机械合同修复单独冻结；沿原生产/质量源原字节，不覆盖首构建失败。"""
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
        raise FileExistsError('97修复冻结不覆盖')
    original = ROOT / 'experiments/p16-shared-proven-static-v1.json'
    assert identity(original)['sha256'] == '1cd5415d99c169f56cd25f3fbb928cb734d26618d91a0216513140e14a95d10f'
    sources = {row['path']: row for row in json.loads(original.read_text(encoding='utf-8'))['sources']}
    production = ROOT / 'artifacts/p16-shared-proven-build-v1/libjshc_shared_proven.dll'
    assert identity(production)['sha256'] == '11e9029117c94fc439d5c261265a38625ba8bfb29e5bdef3c3404b7a0cfa1433'
    objects = ROOT / 'artifacts/p16-shared-proven-object-audit-v1.json'
    proof = json.loads(objects.read_text(encoding='utf-8'))
    assert proof['object_count'] == 7 and proof['all_byte_identical']
    extra = [original, production, objects, ROOT / 'experiments/p16-shared-proven-contract-v2/CMakeLists.txt',
        ROOT / 'scripts/build_p16_shared_proven_contract_v2.py', ROOT / 'scripts/freeze_p16_shared_proven_v2.py',
        ROOT / 'artifacts/p16-shared-proven-build-v1/build-receipt.json',
        ROOT / 'artifacts/p16-shared-proven-build-v1/build.log']
    for path in extra:
        row = identity(path);sources[row['path']] = row
    for row in sources.values():
        assert identity(Path(row['path'])) == row, row['path']
    if a.phase == 'source':
        plan = {'purpose': '97测试target机械补头路径；冻结v1生产DLL与七旧对象证据，不重建生产库',
            'sources': list(sources.values()), 'production_library': identity(production),
            'original_freeze': identity(original), 'original_build_return_code': 2,
            'quality_source_unchanged': identity(ROOT / 'scripts/verify_p16_shared_proven.py')}
    else:
        repair_path = ROOT / 'experiments/p16-shared-proven-repair-v2.json'
        repaired = json.loads(repair_path.read_text(encoding='utf-8'))
        assert repaired['sources'] == list(sources.values())
        old = ROOT / 'experiments/p16-palette-prepare-quality-v1.json'
        assert identity(old)['sha256'] == '98aca4c52054d412962b7fbf40773b67d3b085d414dc5c6dcd6abdb3e55772b1'
        plan = json.loads(old.read_text(encoding='utf-8'))
        build = ROOT / 'artifacts/p16-shared-proven-contract-build-v2'
        receipt_path = build / 'build-receipt.json'
        receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
        assert receipt['return_code'] == 0 and receipt['sources_unchanged'] and not receipt['production_dll_rebuilt']
        plan.update({'purpose': '97同87/95/97质量，机械合同修复后唯一执行；v1编译失败保留',
            'sources': [*sources.values(), identity(repair_path), identity(receipt_path)], 'source_freeze': identity(original),
            'repair_freeze': identity(repair_path), 'libraries': {'reference': plan['libraries']['reference'],
                'previous': identity(ROOT / 'artifacts/p16-palette-prepare-build-v1/libjshc_palette_prepare.dll'),
                'candidate': identity(production)}, 'dictionary_contract_executable': identity(build / 'p16_palette_contract.exe'),
            'private_kernel_contract_executable': identity(build / 'p16_shared_proven_contract.exe'),
            'script_sha256': identity(ROOT / 'scripts/verify_p16_shared_proven.py')['sha256'],
            'build_receipt': identity(receipt_path), 'old_object_proof': identity(objects),
            'boundary': '56完整流/20cache-ID-palette快照/10080有限+110拒绝/16u64/32照片；私有核150显式合同。生产源/质量wrapper沿v1原字节，不添加新C ABI。'})
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(identity(a.output), ensure_ascii=False))


if __name__ == '__main__':
    main()
