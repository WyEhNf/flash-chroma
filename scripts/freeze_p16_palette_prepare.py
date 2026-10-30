"""冻结95固定字典单版来源/质量身份；不构建或运行模型。"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def identity(path):
    path = path.resolve()
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('phase', choices=('source', 'quality'))
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError('95冻结单版不覆盖')
    own = [*list((ROOT / 'experiments/p16-palette-prepare-runtime').glob('*')),
        ROOT / 'scripts/verify_p16_palette_prepare.py', ROOT / 'scripts/freeze_p16_palette_prepare.py']
    rows = [identity(f) for f in own]
    if a.phase == 'source':
        plan = {'purpose': '95固定512槽RGB24精确去重/升序ID，原94共享编译与阈值不动',
            'parent_head': '0d2fa16328441c5ba966c7f2062224b3d6f54025', 'sources': rows,
            'fixed_array_bytes': 3580, 'stack_scope': '计数/对齐及编译器总帧另以sizeof/.su披露，不能称无内存成本。'}
    else:
        old = ROOT / 'experiments/p16-shared-prepare-performance-v1.json'
        assert identity(old)['sha256'] == '9bfaaba25a2c51ed9a4943d96cadb860cf33bcf8acd2ec161f1793c16ac63852'
        baseline = json.loads(old.read_text(encoding='utf-8'))
        freeze = ROOT / 'experiments/p16-palette-prepare-static-v1.json'
        frozen = json.loads(freeze.read_text(encoding='utf-8'))
        assert frozen['sources'] == rows
        sources = {v['path']: v for v in baseline['sources']}
        for row in rows:
            sources[row['path']] = row
        for row in sources.values():
            assert identity(Path(row['path'])) == row
        plan = json.loads((ROOT / 'experiments/p16-shared-prepare-quality-v1.json').read_text(encoding='utf-8'))
        plan.update({'purpose': '95固定512槽字典；56全域流/20安全字节快照/13最坏冲突有限合同',
            'sources': list(sources.values()), 'source_freeze': identity(freeze),
            'libraries': {'reference': baseline['libraries']['reference'], 'previous': baseline['libraries']['candidate'],
                'candidate': identity(ROOT / 'artifacts/p16-palette-prepare-build-v1/libjshc_palette_prepare.dll')},
            'dictionary_contract_executable': identity(ROOT / 'artifacts/p16-palette-prepare-build-v1/p16_palette_contract.exe'),
            'script_sha256': identity(ROOT / 'scripts/verify_p16_palette_prepare.py')['sha256'],
            'boundary': '2模型default/high，87scalar对94/95各7后端完整域56流；原ABI安全copy逐字节；五hint有限/u64及N1真默认照片；固定13项字典最坏碰撞边界。'})
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(identity(a.output), ensure_ascii=False))


if __name__ == '__main__':
    main()
