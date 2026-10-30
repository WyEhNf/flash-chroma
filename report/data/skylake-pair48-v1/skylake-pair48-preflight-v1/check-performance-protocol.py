"""只读比较79与78的验收协议，允许新身份和说明；不执行原生。"""
import copy
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def read(p):
    return json.loads((ROOT/p).read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()


old_path = 'experiments/skylake-andn-split-long-perf-v1.json'
new_path = 'experiments/skylake-pair48-long-perf-v1.json'
old, new = read(old_path), read(new_path)
allowed = ('purpose', 'plan', 'build', 'full_acceptance', 'validation', 'benchmark_script', 'limits')
left, right = copy.deepcopy(old), copy.deepcopy(new)
for key in allowed:
    left.pop(key)
    right.pop(key)
left['confirmation'].pop('output')
right['confirmation'].pop('output')
assert left == right
source = (ROOT/'scripts/bench_skylake_andn_split_long_linux.py').read_text(encoding='utf-8')
expected = source.replace('78','79').replace('andn_split','pair48').replace('andn-split','pair48')
assert expected == (ROOT/'scripts/bench_skylake_pair48_long_linux.py').read_text(encoding='utf-8')
vsource = (ROOT/'scripts/verify_skylake_andn_split_linux.py').read_text(encoding='utf-8')
assert vsource.replace('78ANDN分入口','79双像素ANDN输入').replace('andn_split','pair48') == (ROOT/'scripts/verify_skylake_pair48_linux.py').read_text(encoding='utf-8')
result = {'pass': True, 'purpose': __doc__, 'old_policy_sha256': sha(old_path),
          'new_policy_sha256': sha(new_path), 'allowed_new_identity_fields': allowed,
          'unchanged': ['三倍/单进程/准备门槛','A/A控制','ABBA和线程顺序','16/64内轮','源和输出SHA检查','团队绑定与THP','空闲协议','唯一条件确认'],
          'benchmark_glue_only_identity_changed': True, 'correctness_glue_only_identity_changed': True,
          'candidate_calls': 0}
with (HERE/'performance-protocol-audit.json').open('x', encoding='utf-8') as stream:
    json.dump(result, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps(result, ensure_ascii=False))
