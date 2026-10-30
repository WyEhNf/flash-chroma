"""99整链结果独立原件/流/账单复核；只读JSON和字节，不加载DLL或重复映射。"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError('99独立审计不覆盖')
    read=lambda path:json.loads(path.read_text(encoding='utf-8'))
    sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    plan=read(a.input/'executed-plan.json');data=read(a.input/'correctness.json')
    assert data['passed'] and sha(ROOT/'scripts/verify_p16_b2_packed_v2.py')==plan['script_sha256']
    checked=0
    for row in plan['sources']+list(plan['libraries'].values()):
        assert sha(Path(row['path']))==row['sha256'],row['path'];checked+=1
    full_streams=0
    for model in ('ordinary','anchor'):
        for mode in ('default','high'):
            for role in ('previous','isolated','candidate'):
                result=data['full'][model][mode][role]
                assert result['colors']==1<<24 and result['byte_mismatches']==0
                assert len(result['streams'])==7 and set(result['streams'].values())=={plan['expected_full_sha256'][model]}
                full_streams+=len(result['streams'])
            states=data['states'][model][mode]
            active=model=='ordinary' and mode=='default'
            assert states['previous']['model_bytes']==states['isolated']['model_bytes']
            assert states['candidate']['model_bytes']-states['isolated']['model_bytes']==8+(160320 if active else 0)
            assert bool(states['candidate']['direct']['enabled'])==(model=='anchor' or mode=='high')
    snapshots=data['table_cases']+data['contract_tables']
    for row in snapshots:
        assert row['table_mismatches']==0 and row['measured_empty_owner_handle_difference']==8
        assert row['measured_model_bytes_delta']==8+row['expected_new_aligned_request_bytes']
        assert row['expected_new_aligned_request_bytes']==(160320 if row['expected_b2_private_qualification'] else 0)
    comparisons=rejects=0
    for model in data['finite_cases'].values():
        assert len(model)==5
        for entry in model.values():
            comparisons+=entry['comparisons'];rejects+=len(entry['rejects'])
    contracts=[row for rows in data['contracts'].values() for row in rows]
    assert len(contracts)==16 and all(row['byte_mismatches']==0 for row in contracts)
    for row in contracts:
        assert row['backend_comparisons']==8 and row['oracle_pixels']==8200
    expected={(row['role'],row['images']):row['output_sha256'] for row in plan['photo_expected']}
    for row in data['photos']:
        assert row['actual_output_sha256']==expected[row['model'],row['images']]
    for row in data['boundary_photos']:
        assert row['actual_output_sha256']==row['scalar87_reference_sha256']
        if (row['model'],row['images']) in expected:
            assert row['actual_output_sha256']==expected[row['model'],row['images']]
    assert len(data['photos'])==24 and len(data['boundary_photos'])==16
    finite=read(Path(plan['private_kernel_contract_receipt']['path']))
    assert finite['passed'] and finite['native_contract_calls']==1 and finite['performance_calls']==0
    assert finite['native_result']==data['private_kernel_contract']
    assert finite['native_result']['first_stage_u64_pixels']==33554432
    result={'passed':True,'quality_plan_sha256':sha(a.input/'executed-plan.json'),
        'quality_results_sha256':sha(a.input/'correctness.json'),'source_and_library_identities':checked,
        'full_16m_rgb_streams':full_streams,'exact_cache_id_palette_domain_capacity_snapshots':len(snapshots),
        'active_b2_snapshots':sum(row['expected_b2_private_qualification'] for row in snapshots),
        'finite_backend_comparisons':comparisons,'finite_output_argument_rejects':rejects,
        'independent_u64_synthetic_cases':len(contracts),'u64_synthetic_backend_comparisons':sum(row['backend_comparisons'] for row in contracts),
        'actual_photo_groups':len(data['photos'])+len(data['boundary_photos']),
        'private_first_u64_pixels_consumed_without_rerun':finite['native_result']['first_stage_u64_pixels'],
        'default_ordinary_model_bytes':data['states']['ordinary']['default']['candidate']['model_bytes'],
        'default_anchor_model_bytes':data['states']['anchor']['default']['candidate']['model_bytes'],
        'measured_empty_owner_handle_difference':8,'new_aligned_request_bytes_on_qualified_path':160320,
        'scope':'独立离线复核身份/结果/原始计数，不重新执行native/完整域/照片。容量是账单与合法申请，未宣称CRT真实保留或RSS；OOM/noAVX2未注入。',
        'native_calls':0,'performance_calls':0,'audit_script_sha256':sha(Path(__file__))}
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
