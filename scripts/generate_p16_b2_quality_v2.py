"""99分阶段质量机械v2：消费唯一finite回执，保留未执行v1草稿原字节。"""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
verify=ROOT/'scripts/verify_p16_b2_packed_v2.py'
freeze=ROOT/'scripts/freeze_p16_b2_packed_quality_v2.py'
if verify.exists() or freeze.exists():raise FileExistsError('99 v2质量胶水不覆盖')
old=(ROOT/'scripts/verify_p16_b2_packed.py').read_text(encoding='utf-8')
begin=old.index('    private=json.loads(subprocess.check_output(')
end=old.index("    assert private['passed']",begin)
replacement="""    finite_path=q.checked(plan['private_kernel_contract_receipt'])
    finite=json.loads(finite_path.read_text(encoding='utf-8'))
    execution_path=q.checked(plan['private_native_execution_plan'])
    execution=json.loads(execution_path.read_text(encoding='utf-8'))
    assert finite['passed'] and finite['return_code']==0 and finite['native_contract_calls']==1
    assert finite['execution_plan_sha256']==q.digest(execution_path)
    assert finite['executable_sha256']==q.digest(executable)
    assert finite['library_sha256']==plan['libraries']['candidate']['sha256']
    for key in ('runner','source_freeze','build_receipt','executable','library','model','disassembly','symbols'):
        q.checked(execution[key])
    assert execution['model']['sha256']==plan['models']['ordinary']['models'][0]['sha256']
    private=finite['native_result']  # 唯一原始native执行结果；本入口不再次运行private exe。
"""
old=old[:begin]+replacement+old[end:]
verify.write_text(old,encoding='utf-8')
old=(ROOT/'scripts/freeze_p16_b2_packed_quality.py').read_text(encoding='utf-8')
old=old.replace('p16-b2-packed-quality-v1.json','p16-b2-packed-quality-v2.json')
old=old.replace("ROOT/'scripts/verify_p16_b2_packed.py'","ROOT/'scripts/verify_p16_b2_packed_v2.py'")
token="for path in (Path(__file__),"
assert old.count(token)==1
old=old.replace(token,"for path in (ROOT/'scripts/generate_p16_b2_quality_v2.py',ROOT/'scripts/run_p16_b2_finite.py',\n        ROOT/'artifacts/p16-b2-packed-finite-v1/results.json',ROOT/'artifacts/p16-b2-packed-finite-v1/executed-plan.json',\n        ROOT/'artifacts/p16-b2-packed-finite-v1/stdout.txt',ROOT/'artifacts/p16-b2-packed-finite-v1/stderr.txt',Path(__file__),")
token="'private_kernel_contract_executable':row(build/'p16_b2_packed_contract.exe'),"
assert old.count(token)==1
old=old.replace(token,token+"\n    'private_kernel_contract_receipt':row(ROOT/'artifacts/p16-b2-packed-finite-v1/results.json'),\n    'private_native_execution_plan':row(ROOT/'artifacts/p16-b2-packed-finite-v1/executed-plan.json'),")
freeze.write_text(old,encoding='utf-8')
print('99质量v2只机械消费已验finite原件；未运行native或完整质量。')
