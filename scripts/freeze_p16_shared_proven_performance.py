"""97正式单版冻结；沿已执行生产/质量原字节，两分母独立验收。"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def identity(path):
    return {'path': str(path.resolve()), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError('97正式单版不覆盖')
    base = ROOT / 'experiments/p16-palette-prepare-performance-v1.json'
    assert identity(base)['sha256'] == '2b802c6353ef0fc2a185ae435c1fc3786d38667308e2a0ca31a3df895efd1ed1'
    plan = json.loads(base.read_text(encoding='utf-8'))
    quality_path = ROOT / 'experiments/p16-shared-proven-quality-v2.json'
    assert identity(quality_path)['sha256'] == '0c3560daf4d2faf384e26393bc322a714ee34984beee11a70e0184847ca957a4'
    quality = json.loads(quality_path.read_text(encoding='utf-8'))
    proof = ROOT / 'artifacts/p16-shared-proven-quality-v2/correctness.json'
    assert identity(proof)['sha256'] == '8c77ccc886f32d623da5729573f0ca96f11b36a04a29d4065d9ca5f65c05b4a0'
    assert json.loads(proof.read_text(encoding='utf-8'))['passed']
    sources = {row['path']: row for row in quality['sources']}
    own = [Path(__file__), ROOT / 'scripts/bench_p16_shared_proven.py', ROOT / 'scripts/audit_p16_shared_proven.py',
        ROOT / 'experiments/p16-shared-proven-performance/预注册.md', quality_path,
        ROOT / 'artifacts/p16-shared-proven-quality-v2/independent-check.json']
    for path in own:
        row = identity(path);sources[row['path']] = row
    for row in sources.values():
        assert identity(Path(row['path'])) == row, row['path']
    plan.update({'purpose': '97旧15算术隔离改进，同场87/95/97两分母；默认/低hint/高hint分别验收',
        'sources': list(sources.values()), 'source_freeze': quality['source_freeze'],
        'repair_freeze': quality['repair_freeze'], 'libraries': quality['libraries'], 'quality_proof': identity(proof),
        'script_sha256': identity(ROOT / 'scripts/bench_p16_shared_proven.py')['sha256'],
        'audit_sha256': identity(ROOT / 'scripts/audit_p16_shared_proven.py')['sha256'],
        'images': [1, 10, 100], 'hot_images': [1, 10, 100], 'default_images': [1],
        'image_orders': [[1, 10, 100], [100, 10, 1], [1, 10, 100], [100, 10, 1]],
        'repeats': {'1': 63, '10': 16, '100': 9},
        'photo_expected': [r for r in plan['photo_expected'] if r['images'] in (1, 10, 100)],
        'cold_scope': '每模型/N三角色5正式+5AA按迭代交错新句柄；完整nativecreate及连续create→首Out4墙钟分列，包含全部文件读/解析/校验/prepare；不称磁盘/进程冷启动。',
        'hot_scope': 'N1默认、N10低hint、N100高hint均in/out1/4，warm2+正式/AA63/16/9；同源/工作地址，未测N86不授档。旧apply_to fallback保留copy+apply，纯apply前memcpy在外且total数组保留。',
        'sample_unit': '4worker：288热记录×3末组SHA=864，72冷记录×10句柄=720，共1584；两分母48热+36冷metric，全AA及最劣100..50保留。',
        'rss_scope': '12独立新进程=两模型×三库×N1/100，无照片；native容量与RSS/peak_wset分别披露，不将构造描述秒数作为配对样本。',
        'interpretation': '不以95慢分母救87底线，不将源未改或更少指令当实测收益；原15负证据/v1测试target失败保留。没有96 helper，不恢复旧资格；不扫阈值/重采。'})
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(identity(a.output), ensure_ascii=False))


if __name__ == '__main__':
    main()
