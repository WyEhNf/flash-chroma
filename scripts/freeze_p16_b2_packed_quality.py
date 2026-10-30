"""99实库产生后的独立质量冻结；不得在无构建grant时执行。"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'experiments/p16-b2-packed-quality-v1.json'
if TARGET.exists():raise FileExistsError('99质量冻结不覆盖')
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
row=lambda path:{'path':str(path),'sha256':sha(path)}
prior=ROOT/'experiments/p16-shared-proven-quality-v2.json'
old=json.loads(prior.read_text(encoding='utf-8'))
static=ROOT/'experiments/p16-b2-packed-static-v1.json'
assert sha(static)=='f51415ce4d8e705c8f9d6ff77e4a7b124a1f3543488c43e5798025c15c44a033'
frozen=json.loads(static.read_text(encoding='utf-8'))
build=ROOT/'artifacts/p16-b2-packed-build-v1'
receipt=json.loads((build/'build-receipt.json').read_text(encoding='utf-8'))
assert receipt['return_code']==0 and receipt['sources_unchanged'] and receipt['all_eight_old_objects_byte_identical']
plan={k:v for k,v in old.items() if k not in ('sources','libraries','script_sha256','source_freeze','private_kernel_contract_executable')}
sources={r['path']:r for r in old['sources']}
for r in frozen['sources']:
    assert sha(Path(r['path']))==r['sha256'];sources[r['path']]=r
for r in list(sources.values()):assert sha(Path(r['path']))==r['sha256']
for path in (Path(__file__),ROOT/'scripts/verify_p16_b2_packed.py',ROOT/'scripts/p16_b2_quality_contracts.py',
        ROOT/'scripts/generate_p16_b2_quality_contracts.py',static,prior,build/'build-receipt.json'):
    sources[str(path)]=row(path)
plan.update({'purpose':'99独立完整质量，87/95/97/99四库，全部prepare/私有申请账单另列',
    'script_sha256':sha(ROOT/'scripts/verify_p16_b2_packed.py'), 'sources':list(sources.values()),
    'libraries':{'reference':old['libraries']['reference'],'previous':old['libraries']['previous'],
        'isolated':old['libraries']['candidate'],'candidate':row(build/'libjshc_b2_packed.dll')},
    'private_kernel_contract_executable':row(build/'p16_b2_packed_contract.exe'),
    'source_freeze':row(static),'images':[1,10,100],'extra_boundary_images':[85,86],
    'cpus':[0,2,4,6],'native_performance_calls':0,
    'expected_private_owner_object_bytes':8,'expected_aligned_request_bytes':160320,
    'scope':'继承原97真实照片/模型/独立u64输入身份，不改变旧计划；新版DLL和quality源此刻单独冻结，尚未执行native质量。'})
TARGET.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'quality_plan_sha256':sha(TARGET),'sources':len(sources),'library_sha256':plan['libraries']['candidate']['sha256']},ensure_ascii=False))
