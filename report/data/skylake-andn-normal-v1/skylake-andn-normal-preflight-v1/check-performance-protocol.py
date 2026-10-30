"""80验收前核对原协议及胶水差异；只允许新身份和额外正确性夹具，不执行原生。"""
import copy
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent


def read(p):
    return json.loads((ROOT/p).read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()


old_path='experiments/skylake-pair48-long-perf-v1.json'
new_path='experiments/skylake-andn-normal-long-perf-v1.json'
old,new=read(old_path),read(new_path)
left,right=copy.deepcopy(old),copy.deepcopy(new)
for key in ('purpose','plan','build','full_acceptance','validation','benchmark_script','limits'):
    left.pop(key)
    right.pop(key)
left['confirmation'].pop('output')
right['confirmation'].pop('output')
assert left==right
bench=(ROOT/'scripts/bench_skylake_pair48_long_linux.py').read_text(encoding='utf-8')
assert bench.replace('79','80').replace('pair48','andn_normal')==(ROOT/'scripts/bench_skylake_andn_normal_long_linux.py').read_text(encoding='utf-8')
expected=(ROOT/'scripts/verify_skylake_pair48_linux.py').read_text(encoding='utf-8').replace('79双像素ANDN输入','80按有效workers选择普通写').replace('pair48','andn_normal')
actual=(ROOT/'scripts/verify_skylake_andn_normal_linux.py').read_text(encoding='utf-8')
start=actual.index('def apply_known_alignment(')
end=actual.index('def main():',start)
reduced=actual[:start]+actual[end:]
start=reduced.index('            # 新普通写只有有效workers>1')
end=reduced.index('            # 262144像素',start)
reduced=reduced[:start]+reduced[end:]
start=reduced.index("        'normal_inplace_alignment_comparisons'")
end=reduced.index("        'scope':",start)
reduced=reduced[:start]+reduced[end:]
assert reduced==expected
full=read('artifacts/skylake-andn-normal-linux-full-v1/results.json')
assert full['normal_inplace_alignment_comparisons']==64
assert full['normal_inplace_actual_offsets']==list(range(64))
value={'pass':True,'purpose':__doc__,'old_policy_sha256':sha(old_path),'new_policy_sha256':sha(new_path),
       'benchmark_only_identity_changed':True,'correctness_change':'保留79全部矩阵，仅增加双块64实际偏移夹具、哨兵和结果字段',
       'gate_control_order_repeats_quiet_pinning_thp_confirmation_unchanged':True,'native_calls':0}
with (HERE/'performance-protocol-audit.json').open('x',encoding='utf-8') as stream:
    json.dump(value,stream,ensure_ascii=False,indent=2)
    stream.write('\n')
print(json.dumps(value,ensure_ascii=False))
