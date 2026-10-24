"""100新增质量独立离线计数、身份及逐流SHA复核，不调用native。"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--plan',type=Path,required=True);parser.add_argument('--results',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError('100离线质量审计不覆盖')
    plan=json.loads(args.plan.read_text(encoding='utf-8'));result=json.loads(args.results.read_text(encoding='utf-8'))
    for entry in plan['sources']:assert sha(Path(entry['path']))==entry['sha256']
    assert result['passed'] and result['counters']==plan['expected_counters']
    streams=0
    for model,modes in result['full'].items():
        for name,entry in modes.items():
            assert entry['colors']==1<<24 and entry['byte_mismatches']==0
            assert set(entry['streams'])=={'avx1','avx4','out1','out4'}
            assert set(entry['streams'].values())=={plan['expected_full_sha256'][model]};streams+=len(entry['streams'])
    assert streams==16 and len(result['table_cases'])==14
    for entry in result['table_cases']:assert entry['byte_mismatches']==0 and entry['previous_sha256']==entry['candidate_sha256']
    expected={(r['model'],r['images']):r['sha256'] for r in plan['photo_expected_prefixes']}
    for entry in result['photos']:assert entry['actual_output_sha256']==entry['expected_prefix_sha256']==expected[entry['model'],entry['images']]
    assert len(result['photos'])==40 and len(result['contracts'])==8
    assert sum(entry['backend_comparisons'] for entry in result['contracts'])==64
    assert all(entry['byte_mismatches']==0 for entry in result['contracts'])
    for model,hints in result['finite_cases'].items():
        assert len(hints)==5 and all(v['comparisons']==1008 and v['rejects']==11 for v in hints.values())
    receipt={'passed':True,'plan_sha256':sha(args.plan),'results_sha256':sha(args.results),'source_rows_checked':len(plan['sources']),
        'full_streams':streams,'table_pairs':14,'photo_sha_checks':40,'finite_comparisons':10080,'finite_rejects':110,
        'u64_contracts':8,'u64_backend_comparisons':64,'native_calls':0,'performance_calls':0,
        'scope':'只复核原已执行新100质量结果与身份，不重新运行旧/新native或计时。'}
    args.output.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt,ensure_ascii=False))


if __name__=='__main__':main()
