"""99四角色正式单版预冻结；只查身份，不执行预检、像素或计时。"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def identity(path):
    return {'path':str(path.resolve()),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError('99正式冻结不覆盖')
    base=ROOT/'experiments/p16-shared-proven-performance-v1.json'
    assert identity(base)['sha256']=='2534782322401fac5abd33c6c6cacb3062a9bb1aa5d1ca846b3caee52bc5ee77'
    plan=json.loads(base.read_text(encoding='utf-8'))
    quality_path=ROOT/'experiments/p16-b2-packed-quality-v2.json'
    assert identity(quality_path)['sha256']=='148aaf7e67c1fd7cc95a952efee1ccf01fcefb3a1d7cde595db24b7990557a26'
    quality=json.loads(quality_path.read_text(encoding='utf-8'))
    proof=ROOT/'artifacts/p16-b2-packed-quality-v2/correctness.json'
    assert identity(proof)['sha256']=='f0225fcb3ad659bc22b1a75cc41b6141c6db8c066a9437f5986f4d6dfaf03fe2'
    assert json.loads(proof.read_text(encoding='utf-8'))['passed']
    independent=ROOT/'artifacts/p16-b2-packed-quality-v2/independent-check-v2.json'
    assert json.loads(independent.read_text(encoding='utf-8'))['passed']
    sources={row['path']:row for row in quality['sources']}
    own=[Path(__file__),ROOT/'scripts/bench_p16_b2_packed.py',ROOT/'scripts/audit_p16_b2_packed.py',
        ROOT/'scripts/generate_p16_b2_performance.py',ROOT/'scripts/generate_p16_b2_decimal.py',
        ROOT/'scripts/audit_p16_b2_packed_decimal.py',ROOT/'scripts/audit_p16_b2_packed_quality.py',
        ROOT/'scripts/audit_p16_b2_packed_quality_v2.py',ROOT/'scripts/repair_p16_b2_quality_audit_v2.py',
        ROOT/'experiments/p16-b2-packed-正式预注册.md',quality_path,independent,
        ROOT/'artifacts/p16-b2-packed-quality-v2/independent-check-v1-failure.json',
        ROOT/'artifacts/p16-b2-packed-quality-v2/independent-check-v2.log']
    for path in own:
        row=identity(path);sources[row['path']]=row
    for row in sources.values():assert identity(Path(row['path']))==row,row['path']
    plan.update({'purpose':'99唯一packed-axis B2，与87/95/97三个分母独立冷热验收',
        'sources':list(sources.values()),'source_freeze':quality['source_freeze'],
        'libraries':quality['libraries'],'quality_proof':identity(proof),'quality_plan':identity(quality_path),
        'quality_independent_proof':identity(independent),'denominators':['reference','previous','isolated'],
        'script_sha256':identity(ROOT/'scripts/bench_p16_b2_packed.py')['sha256'],
        'audit_sha256':identity(ROOT/'scripts/audit_p16_b2_packed.py')['sha256'],
        'orders':[['reference','previous','isolated','candidate'],['candidate','isolated','previous','reference'],
            ['previous','reference','candidate','isolated'],['isolated','candidate','reference','previous']],
        'images':[1,10,100],'hot_images':[1,10,100],'default_images':[1],
        'image_orders':[[1,10,100],[100,10,1],[1,10,100],[100,10,1]],'repeats':{'1':63,'10':16,'100':9},
        'sample_unit':'4worker：384热记录×3末SHA=1152；96冷记录×10新句柄=960；共2112实际SHA。3分母总72热/54冷metric。',
        'cold_scope':'各N/角色5正式+5AA迭代交错；完整nativecreate读/解析/校验/缓存/direct/B2申请填充分列prepare、首Out4及连续wall，不称进程/磁盘冷。',
        'hot_scope':'N1真默认/N10低hint/N100高hint；in/out1/4，warm2+63/16/9正式及同长AA。纯apply拷贝在外且total保留；不引入96 pin。',
        'rss_scope':'16独立新进程=2模型×4角色×N1/100；申请160320+Handle实差8、RSS/peak_wset和包装描述秒分别报告，不推断CRT真实保留。',
        'interpretation':'保持.85..1.15与全部最劣100..50；失效不授档；87/95/97三个分母分别完整报告，不能用97救线。N86未测性能，未重复/择样/调阈值或布局。',
        'execution_requires_root_exclusive_grant':True})
    a.output.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'plan':identity(a.output),'sources':len(sources),'script_sha256':plan['script_sha256'],
        'audit_sha256':plan['audit_sha256'],'performance_calls':0},ensure_ascii=False))


if __name__=='__main__':main()
