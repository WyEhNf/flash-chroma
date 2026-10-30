"""冻结94质量/正式身份；参数沿单版预注册，不执行模型或图像。"""
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
        raise FileExistsError('94冻结不覆盖')
    old = ROOT / 'experiments/p16-workload-performance-v1.json'
    assert identity(old)['sha256'] == 'ad777e52927e309d942d579db4de5ba36213c1e8c0db9512746ca7a976e956a8'
    baseline = json.loads(old.read_text(encoding='utf-8'))
    oldq = json.loads((ROOT / 'experiments/p16-workload-quality-v1.json').read_text(encoding='utf-8'))
    own = [*list((ROOT / 'experiments/p16-shared-prepare-runtime').glob('*')),
        ROOT / 'scripts/verify_p16_shared_prepare.py', ROOT / 'scripts/freeze_p16_shared_prepare.py']
    if a.phase == 'performance':
        own += [ROOT / 'scripts/bench_p16_shared_prepare.py', ROOT / 'scripts/audit_p16_shared_prepare.py']
    sources = {v['path']: v for v in baseline['sources']}
    for f in own:
        row = identity(f)
        sources[row['path']] = row
    for row in sources.values():
        assert identity(Path(row['path'])) == row
    libraries = {'reference': baseline['libraries']['reference'], 'previous': baseline['libraries']['candidate'],
        'candidate': identity(ROOT / 'artifacts/p16-shared-prepare-build-v1/libjshc_shared_prepare.dll')}
    plan = dict(oldq)
    plan.update({'purpose': '94共享prepare现有true分派，2^26/ABI/ID/热像素不变，同场87/92/94',
        'sources': list(sources.values()), 'source_freeze': identity(ROOT / 'experiments/p16-shared-prepare-static-v1.json'),
        'libraries': libraries, 'models': baseline['models'], 'images': [1, 10, 86, 100],
        'photo_expected': [v for v in baseline['photo_expected'] if v['images'] in (1, 10, 86, 100)],
        'script_sha256': identity(ROOT / 'scripts/verify_p16_shared_prepare.py')['sha256'],
        'boundary': '2模型default/high，87scalar对92/94各7后端完整域56流；安全copy导出直接ID/palette逐字节对旧92；五hint有限/u64合同及N1真默认照片。'})
    if a.phase == 'performance':
        proof = ROOT / 'artifacts/p16-shared-prepare-quality-v1/correctness.json'
        assert json.loads(proof.read_text(encoding='utf-8'))['passed']
        plan = dict(baseline)
        plan.update({'purpose': '94共享prepare单版，同场87/92/94；两分母独立冷/热/50底线',
            'sources': [*sources.values(), identity(ROOT / 'experiments/p16-shared-prepare-quality-v1.json')],
            'source_freeze': identity(ROOT / 'experiments/p16-shared-prepare-static-v1.json'),
            'libraries': libraries, 'quality_proof': identity(proof),
            'script_sha256': identity(ROOT / 'scripts/bench_p16_shared_prepare.py')['sha256'],
            'images': [1, 10, 86, 100], 'default_images': [1],
            'photo_expected': [v for v in baseline['photo_expected'] if v['images'] in (1, 10, 86, 100)],
            'orders': [['reference', 'previous', 'candidate'], ['candidate', 'previous', 'reference'],
                ['previous', 'reference', 'candidate'], ['candidate', 'reference', 'previous']],
            'image_orders': [[1, 10, 86, 100], [100, 86, 10, 1], [1, 10, 86, 100], [100, 86, 10, 1]],
            'repeats': {'1': 64, '10': 16, '86': 9, '100': 9},
            'denominators': ['reference', 'previous'],
            'cold_scope': '每模型/N三角色按迭代交错5正式+5AA新句柄；第N1三库真默认create，N10/86/100的92/94用N×786432原hint。每次完整nativecreate到首组Out4连续wall计含文件读取/解析/校验/全部prepare；copy/hash/分配在外，文件缓存/OMP池可热。最后各角色句柄用于对应热场。',
            'hot_scope': '各N同source/work地址，三角色热in/out1/4，warm2和正式/AA64/16/9/9。两分母不拼接，不能只赢较慢92救87的50。',
            'sample_unit': '4worker、384热记录×3组=1152实际末SHA；96冷记录×10句柄=960实际首SHA，合2112；两分母各32热+24冷metric独立AA/最劣100..50。',
            'rss_scope': '12新进程=2模型×3角色×N1/100，无照片；nativecapacity和真实RSS/peak_wset分列，非正式配对计时样本。',
            'interpretation': '94/92 nativeprepare为替换编译机制的整体作用，palette.prepare仍包括sort/ids/compile，不当纯compile微计时。87/94首次整作业和热吞吐独立验50；保留默认小N及非共享a399控制。'})
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(identity(a.output), ensure_ascii=False))


if __name__ == '__main__':
    main()
