"""99构建前生产/私有质量/协议闭包；只冻结，不构建或执行native质量。"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'experiments/p16-b2-packed-static-v1.json'
if TARGET.exists():raise FileExistsError('99静态冻结不覆盖')
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
contract=ROOT/'experiments/p16-b2-packed-axis-contract-v1.json'
result=ROOT/'artifacts/p16-b2-packed-axis-contract-v1/results.json'
assert sha(contract)=='7b86f2de92a67119ef4121c779792557da9ecdbcd8a5d141a2193c0fb467e801'
assert sha(result)=='bad35f0a0c4a4996d6a438d41b81a46bd929d88db964cf52b278f2a00c6c467e'
assert json.loads(result.read_text(encoding='utf-8'))['passed']
sources=[p for p in sorted((ROOT/'experiments/p16-b2-packed-runtime').rglob('*')) if p.is_file()]
sources+=[Path(__file__),ROOT/'scripts/build_p16_b2_packed.py',ROOT/'scripts/generate_p16_b2_packed_runtime.py',contract,result]
sources+=[ROOT/'scripts/contract_p16_b2_packed_axis.py',ROOT/'scripts/freeze_p16_b2_packed_axis.py',ROOT/'experiments/p16-b2-packed-axis-预注册.md']
# 旧来源的完整执行依赖沿97原冻结闭包绑定，不重新生成旧源。
prior=ROOT/'experiments/p16-shared-proven-static-v1.json'
old=json.loads(prior.read_text(encoding='utf-8'))
for row in old['sources']:
    path=Path(row['path']);assert sha(path)==row['sha256'];sources.append(path)
unique={str(path):path for path in sources}
plan={'purpose':'99唯一packed-axis B2隔离runtime构建前冻结','parent_revision':97,'candidate_revision':99,
    'contract_plan_sha256':sha(contract),'contract_result_sha256':sha(result),
    'sources':[{'path':str(path),'sha256':sha(path)} for path in sorted(unique.values())],
    'old_static_freeze_sha256':sha(prior),'aligned_allocation_bytes':160320,
    'owner_expected_pointer_count':1,'abi_changes':0,'native_quality_calls':0,'performance_calls':0,
    'scope':'本闭包含生产/私有C++质量与完整质量协议；实际DLL产生后完整Python质量plan另绑定实库SHA，不可在本阶段冒称已跑。'}
TARGET.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'plan_sha256':sha(TARGET),'sources':len(plan['sources']),'native_quality_calls':0,'performance_calls':0},ensure_ascii=False))
