"""仅冻结93原因辨别身份；不import实验模块、不加载DLL或运行图像。"""
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
    p.add_argument('phase', choices=('quality', 'performance'))
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError('93预注册不覆盖')
    old = ROOT / 'experiments/p16-workload-performance-v1.json'
    assert identity(old)['sha256'] == 'ad777e52927e309d942d579db4de5ba36213c1e8c0db9512746ca7a976e956a8'
    prior = json.loads(old.read_text(encoding='utf-8'))
    mp = json.loads(Path(prior['photo_model_plan']['path']).read_text(encoding='utf-8'))
    manifest = json.loads(Path(mp['manifest']['path']).read_text(encoding='utf-8'))
    first = manifest['images'][0]['evaluation']
    expected = next(v['output_sha256'] for v in prior['photo_expected'] if v['role'] == 'ordinary' and v['images'] == 1)
    own = [ROOT / 'scripts' / n for n in ('study_p16_default_layout.py',
        'freeze_p16_default_layout.py', 'audit_p16_default_layout.py')]
    own.append(ROOT / 'experiments/p16-default-layout/预注册.md')
    # 相同的实际原生库复用92执行依赖；本阶段只新增Python调度，没有新原生代码。
    sources = [row for row in prior['sources'] if Path(row['path']).name in (
        'bench_p16_model_pair.py', 'study_p16_direct_compile.py', 'channel_native.py',
        'suffix_cache_support.py', 'direct16_support.py', 'domain_cache_support.py',
        'palette_support.py', 'outplace_support.py', 'exception_support.py')]
    for row in sources:
        assert identity(Path(row['path'])) == row
    plan = {'purpose': '93仅ordinary N1/T1/inplace默认create的caller布局/角色分块交互诊断，不恢复92资格',
        'script_sha256': identity(own[0])['sha256'], 'sources': [*sources, *[identity(v) for v in own]],
        'libraries': prior['libraries'], 'model': prior['models']['ordinary'],
        'image': {'path': str(Path(mp['data_root']) / first['path']), 'sha256': first['sha256']},
        'source_sha256': first['pixel_sha256'], 'expected_output_sha256': expected,
        'manifest': mp['manifest'], 'prior92': identity(old), 'cpus': [0, 2, 4, 6],
        'work_offsets': [0, 64], 'construction_orders': [['ABBA', 'BAAB'], ['BAAB', 'ABBA'],
            ['BAAB', 'ABBA'], ['ABBA', 'BAAB']],
        'pair_orders': [[0, 1], [1, 0], [1, 0], [0, 1]],
        'offset_orders': [[0, 64], [64, 0], [64, 0], [0, 64]],
        'schedule_orders': [['blocked', 'interleaved'], ['interleaved', 'blocked'],
            ['blocked', 'interleaved'], ['interleaved', 'blocked']],
        'control_min': .85, 'control_max': 1.15, 'grades': [100, 90, 80, 70, 60, 50],
        'rounds_per_role_per_phase': 63, 'chunks_per_role_per_phase': 9, 'chunk_repeats': 7,
        'warmup_per_role_per_cell': 2, 'interest_interaction_min': .10, 'interest_workers': 3,
        'sample_unit': '4worker各2构造序×2对句柄×2work偏移×2调度=64cell；每cell两role各warm2、正式63、AA63，两调度均18个7轮CABI块；2432实际块末SHA，16128正式/AA+256warm=16384整图内轮。',
        'address_scope': '同source/backing，两个重叠work仅串行；各role同一work指针。记录module/function/handle/work地址和CPU端点；公共ABI没有cache指针，table_mod64=None，不冒称heap/实际TID/频率已控。',
        'interpretation': '比较各cell候选/基线比的因素两水平之商；两cell严格AA有效，至少3/4同向超过±10%且中位越同线才记录交互，否则未解。布局只到caller偏移，调度只到角色分块状态含cache共存；非统计显著性/频率因果，不追授92失效或改阈值。'}
    if a.phase == 'performance':
        proof = ROOT / 'artifacts/p16-default-layout-quality-v1/quality.json'
        assert json.loads(proof.read_text(encoding='utf-8'))['passed']
        plan['quality_proof'] = identity(proof)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(identity(a.output), ensure_ascii=False))


if __name__ == '__main__':
    main()
