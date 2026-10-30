"""冻结95正式三角色协议；已执行的来源/质量冻结器保持原字节。"""
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
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError('95正式协议不覆盖')
    previous = ROOT / 'experiments/p16-shared-prepare-performance-v1.json'
    assert identity(previous)['sha256'] == '9bfaaba25a2c51ed9a4943d96cadb860cf33bcf8acd2ec161f1793c16ac63852'
    plan = json.loads(previous.read_text(encoding='utf-8'))
    quality_path = ROOT / 'experiments/p16-palette-prepare-quality-v1.json'
    assert identity(quality_path)['sha256'] == '98aca4c52054d412962b7fbf40773b67d3b085d414dc5c6dcd6abdb3e55772b1'
    quality = json.loads(quality_path.read_text(encoding='utf-8'))
    proof = ROOT / 'artifacts/p16-palette-prepare-quality-v1/correctness.json'
    assert identity(proof)['sha256'] == 'e39164a0f2c4eaa0028166e063c15e5e0dacf0d2b0506e5aa19397a90d1a808f'
    assert json.loads(proof.read_text(encoding='utf-8'))['passed']
    sources = {v['path']: v for v in quality['sources']}
    own = [ROOT / 'scripts/bench_p16_palette_prepare.py', ROOT / 'scripts/audit_p16_palette_prepare.py',
        Path(__file__), quality_path, ROOT / 'experiments/p16-palette-prepare-static-v1.json']
    for path in own:
        row = identity(path)
        sources[row['path']] = row
    for row in sources.values():
        assert identity(Path(row['path'])) == row
    plan.update({'purpose': '95固定512槽字典准备，同场87/94/95；两分母冷/热底线分列',
        'sources': list(sources.values()), 'source_freeze': quality['source_freeze'],
        'libraries': quality['libraries'], 'quality_proof': identity(proof),
        'script_sha256': identity(ROOT / 'scripts/bench_p16_palette_prepare.py')['sha256'],
        'images': [1, 10, 86, 100], 'hot_images': [1, 100], 'repeats': {'1': 64, '100': 9},
        'cold_scope': '每模型/N三角色按迭代交错5正式+5AA完整新句柄；N1三库真默认，N10/86/100的94/95传原hint。nativecreate含文件读取/解析/校验及全部prepare；连续create→首Out4完整wall另测，不将内部时钟相加；hash/分配在外，文件缓存/OMP池可热。',
        'hot_scope': '热只N1/100同source/work地址，三角色in/out1/4，warm2和正式/AA64/9。N10/86热未重测不授档、不插值。各分母独立，94慢分母不可救87底线。',
        'sample_unit': '4worker：192热记录×3组=576实际末SHA；96冷记录×10句柄=960实际首SHA，合1536；每分母16热+24冷metric独立AA/最劣100..50。',
        'rss_scope': '12新进程=2模型×3角色×N1/100，无照片；持久capacity/逻辑temporary（含3584B对象栈）/RSS及peak_wset分列，不将.su总静态帧7568B伪称仅3580B。',
        'interpretation': '95/94 nativeprepare辨别固定字典整体机制，95/87完整作业独立验底线。临时heap降低与新增3580B固定数组、对象3584B及实际create总帧7568B分别披露。未加逐TID绑定，不恢复94/92旧失效，固定hash/阈值不扫描或补测。'})
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(identity(a.output), ensure_ascii=False))


if __name__ == '__main__':
    main()
