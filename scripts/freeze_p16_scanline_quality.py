"""100新增质量闭包：绑定旧已认证真值，不重复旧native质量。"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'experiments/p16-scanline-prepare-quality-v1.json'
if TARGET.exists():raise FileExistsError('100新增质量冻结不覆盖')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
row=lambda p:{'path':str(p),'sha256':sha(p)}
prior=ROOT/'experiments/p16-b2-packed-quality-v2.json'
old=json.loads(prior.read_text(encoding='utf-8'))
static=ROOT/'experiments/p16-scanline-prepare-static-v1.json'
assert sha(static)=='e7c2366010e1b9876f1a386c8405568eea853f81bbdcbb7d7d54fb574439793f'
sources=json.loads(static.read_text(encoding='utf-8'))['sources']
for r in sources:assert sha(Path(r['path']))==r['sha256']
build=ROOT/'artifacts/p16-scanline-prepare-build-v1';receipt=build/'build-receipt.json'
br=json.loads(receipt.read_text(encoding='utf-8'));assert br['return_code']==0 and br['all_eight_old_objects_byte_identical']
finite=ROOT/'artifacts/p16-scanline-prepare-finite-v1/results.json';assert json.loads(finite.read_text(encoding='utf-8'))['passed']
old_correctness=ROOT/'artifacts/p16-b2-packed-quality-v2/correctness.json'
certified=json.loads(old_correctness.read_text(encoding='utf-8'));assert certified['passed']
prefixes={}
for record in certified['photos']:
    key=(record['model'],record['images']);value=record['actual_output_sha256']
    assert key not in prefixes or prefixes[key]==value;prefixes[key]=value
for record in certified['boundary_photos']:
    key=(record['model'],record['images']);value=record['actual_output_sha256']
    assert value==record['scalar87_reference_sha256']
    assert key not in prefixes or prefixes[key]==value;prefixes[key]=value
assert len(prefixes)==10
original=Path('F:/Hackathon/projects/16-lut-color')
oracles={'ordinary':row(original/'artifacts/cinema-axis-calibration-v1/stage1_sweep012/cube.rgb'),
    'anchor':row(original/'artifacts/cinema-current-anchor-accept-v1/cube.rgb')}
for name,r in oracles.items():assert r['sha256']==old['expected_full_sha256'][name]
for path in (static,prior,old_correctness,receipt,finite,ROOT/'artifacts/p16-scanline-prepare-finite-v1/executed-plan.json',
        ROOT/'artifacts/p16-scanline-prepare-assembly-audit-v1.json',ROOT/'scripts/verify_p16_scanline_prepare.py',
        ROOT/'scripts/audit_p16_scanline_quality.py',Path(__file__)):
    sources.append(row(path))
sources={r['path']:r for r in sources}
libraries={'reference':old['libraries']['reference'],'previous':old['libraries']['isolated'],
    'candidate':row(build/'libjshc_scanline_prepare.dll')}
assert libraries['candidate']['sha256']==br['library_sha256']
plan={'purpose':'100新增完整质量，不重跑旧不可变native全域/99合同','script_sha256':sha(ROOT/'scripts/verify_p16_scanline_prepare.py'),
    'sources':list(sources.values()),'source_freeze':row(static),'libraries':libraries,'models':old['models'],
    'oracles':oracles,'expected_full_sha256':old['expected_full_sha256'],'private_native_receipt':row(finite),
    'photo_model_plan':old['photo_model_plan'],'photo_source_sha256':old['photo_source_sha256'],
    'photo_expected_prefixes':[{'model':m,'images':n,'sha256':v} for (m,n),v in sorted(prefixes.items())],
    'lengths':old['lengths'],'cpus':[0,2,4,6],
    'expected_counters':{'full_streams':16,'full_candidate_backend_calls':1024,'table_pairs':14,'finite_comparisons':10080,
        'finite_rejects':110,'u64_contracts':8,'u64_candidate_backend_calls':64,'photo_sha_checks':40,'typed_rejects':10,'native_create_rejects':10},
    'pre_registered_calls':{'candidate_successful_create':32,'previous97_successful_create':14,'reference87_successful_create':10,
        'candidate_valid_backend_invocations':11208,'reference87_finite_scalar_invocations':210,
        'candidate_invalid_apply_to_invocations':110,'candidate_null_empty_apply_to_invocations':10,'candidate_invalid_create_invocations':10,
        'scope':'上述是显式create/像素入口计数；不将诊断copy/capability查询或OpenMP内部调用混成全C ABI计数。'},
    'full_chain_calls_before_this_execution':0,'native_private_reruns':0,'performance_calls':0,
    'resources':{'native_threads_max':4,'estimated_peak_less_than_bytes':1073741824,'measured_rss':False},
    'scope':'finite三B批仅有限证据，只有本次16新流覆盖完整输入域；首错STOP原件保留，不覆盖修改后重采。'}
TARGET.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'plan_sha256':sha(TARGET),'sources':len(sources),'libraries':libraries,'expected_counters':plan['expected_counters']},ensure_ascii=False))
