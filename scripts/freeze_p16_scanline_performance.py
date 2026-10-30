"""100四角色正式单版预冻结；不预检、不加载库或计时。"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def identity(path):return {'path':str(path.resolve()),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    if args.output.exists():raise FileExistsError('100正式冻结不覆盖')
    base=ROOT/'experiments/p16-b2-packed-performance-v1.json'
    assert identity(base)['sha256']=='1d99b7f1b5ddde6f667c70dd2e11e6d35eff9a478e033765e2b7f8f8e386e518'
    plan=json.loads(base.read_text(encoding='utf-8'))
    quality_path=ROOT/'experiments/p16-scanline-prepare-quality-v1.json'
    assert identity(quality_path)['sha256']=='a098d3bdff6587491c083bc2595cf53d3e47003b4c769951cfb2a5c25e98873a'
    quality=json.loads(quality_path.read_text(encoding='utf-8'))
    proof=ROOT/'artifacts/p16-scanline-prepare-quality-v1/correctness.json'
    assert identity(proof)['sha256']=='7c5ac4e334951f80e68e2cf055bebcd6f8e204219883867efa31081b17c66d0e'
    assert json.loads(proof.read_text(encoding='utf-8'))['passed']
    independent=ROOT/'artifacts/p16-scanline-prepare-quality-v1/offline-audit.json'
    assert json.loads(independent.read_text(encoding='utf-8'))['passed']
    sources={r['path']:r for r in quality['sources']}
    for path in (Path(__file__),ROOT/'scripts/bench_p16_scanline_prepare.py',ROOT/'scripts/audit_p16_scanline_prepare.py',
            ROOT/'scripts/audit_p16_scanline_decimal.py',ROOT/'scripts/generate_p16_scanline_performance.py',
            ROOT/'scripts/preflight_p16_scanline_prepare.py',ROOT/'experiments/p16-scanline-prepare-正式预注册.md',
            quality_path,independent,base):
        entry=identity(path);sources[entry['path']]=entry
    for entry in sources.values():assert identity(Path(entry['path']))==entry,entry['path']
    libraries={'reference':plan['libraries']['reference'],'previous':plan['libraries']['previous'],
        'isolated':quality['libraries']['previous'],'candidate':quality['libraries']['candidate']}
    plan.update({'purpose':'100固定枚举scanline准备器同场87/95/97/100三分母冷热验收','candidate_revision':100,
        'sources':list(sources.values()),'source_freeze':quality['source_freeze'],'libraries':libraries,
        'quality_proof':identity(proof),'quality_plan':identity(quality_path),'quality_independent_proof':identity(independent),
        'expected_quality_counters':quality['expected_counters'],'script_sha256':identity(ROOT/'scripts/bench_p16_scanline_prepare.py')['sha256'],
        'audit_sha256':identity(ROOT/'scripts/audit_p16_scanline_prepare.py')['sha256'],
        'cold_scope':'各N/角色5正式+5AA交错；nativecreate读取/解析/校验/缓存/direct全计，prepare/首Out4/连续wall分别列。不称进程/磁盘冷。',
        'rss_scope':'16独立新进程，100无新owner/持久表，对97账单应同；RSS/peak_wset/描述构造秒分别保留，不推断CRT保留。',
        'interpretation':'同场100/87、100/95、100/97分别完整报告；AA/全部轮与100..50门不变，N86未测性能不授档；不能用prepare改善冒称热像素提速。',
        'execution_requires_root_exclusive_grant':True})
    args.output.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'plan':identity(args.output),'sources':len(sources),'script_sha256':plan['script_sha256'],
        'audit_sha256':plan['audit_sha256'],'performance_calls':0},ensure_ascii=False))


if __name__=='__main__':main()
