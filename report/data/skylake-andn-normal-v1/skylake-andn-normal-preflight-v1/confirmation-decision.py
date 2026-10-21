"""按80首次结果决定是否允许确认；本阶段失败则不新增原生调用。"""
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
path = ROOT/'artifacts/skylake-andn-normal-long-perf-v1/results.json'
policy = ROOT/'experiments/skylake-andn-normal-long-perf-v1.json'
result = json.loads(path.read_text(encoding='utf-8'))
assert not result['accepted_on_this_host']
decision = {'purpose': '80首次受控长批次未过四线程纯apply门槛，按冻结规则跳过唯一确认',
    'first_result': {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()},
    'policy_sha256': hashlib.sha256(policy.read_bytes()).hexdigest(),
    'measurement_control_valid': result['measurement_control_valid'],
    'accepted_on_this_host': result['accepted_on_this_host'], 'failed_gates': result['failed_gates'],
    'confirmation_executed': False, 'additional_series': 0, 'additional_native_calls': 0,
    'no_retry_or_sample_selection': True}
with (ROOT/'artifacts/skylake-andn-normal-confirmation-decision-v1.json').open('x',encoding='utf-8') as stream:
    json.dump(decision,stream,ensure_ascii=False,indent=2)
    stream.write('\n')
print(json.dumps(decision,ensure_ascii=False))
print([(row['requested_threads'],1/row['median_apply_ratio'],1/row['median_outplace_ratio'],1/row['median_legacy_copy_apply_ratio']) for row in result['paired']])
