"""82静态及完整域通过后才冻结首次长批次；不执行原生。"""
import copy
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def spec(p):return {'path':p,'sha256':sha(p)}
def save(p,v):
    with (ROOT/p).open('x',encoding='utf-8') as stream:json.dump(v,stream,ensure_ascii=False,indent=2);stream.write('\n')
plan='experiments/skylake-input256-deferred-v1.json'
build='artifacts/skylake-input256-deferred-linux-build-v1/build.json'
static='artifacts/skylake-input256-deferred-static-v1/results.json'
independent='artifacts/skylake-input256-deferred-static-v1/independent_results.json'
full='artifacts/skylake-input256-deferred-linux-full-v1/results.json'
st,ind,r=read(static),read(independent),read(full)
assert st['accepted'] and ind['accepted'] and r['pass']
assert all(v['plan_sha256']==sha(plan) and v['build_sha256']==sha(build) for v in (st,ind,r))
assert r['input256_deferred_enabled']=={'single':0,'chain':1}
assert r['input256_deferred_inplace_alignment_comparisons']==64
assert r['input256_deferred_inplace_actual_offsets']==list(range(64))
assert r['input256_deferred_inplace_alignment_pixels']==65793
assert r['model_accounting_bytes']['candidate']['chain']==28046644
validation='experiments/skylake-input256-deferred-validation-v1.json'
save(validation,{'purpose':'82分阶段NT写入的独立静态与完整RGB8/边界身份，不计性能',
    'plan_sha256':sha(plan),'source_sha256':{p:sha(p) for p in ('scripts/verify_skylake_input256_deferred_linux.py',
        'scripts/paged_table_support.py','scripts/outplace_support.py','scripts/guarded_buffer_support.py')},
    'full_result':spec(full),'static_result':spec(static),'independent_static_result':spec(independent)})
old=read('experiments/skylake-andn-normal-long-perf-v1.json');policy=copy.deepcopy(old)
policy['purpose']='82单YMM输入及分阶段NT输出直接对23受控长批次；三倍/A/A/唯一条件确认规则不变'
for key,path in {'plan':plan,'build':build,'full_acceptance':full,'validation':validation,
    'benchmark_script':'scripts/bench_skylake_input256_deferred_long_linux.py'}.items():policy[key]=spec(path)
policy['limits']=['仅新82，不重评81或旧失败，不跨场拼接历史成绩',
    '唯一16MiB线性表，单线程/分离保留79 pair；新多线程只需AVX2，BMI可选回退不变',
    '首两NT只写首完整64B行，pending及后三NT在后组读完后写；静态和全域均通过才计时',
    '原16/64内轮、ABBA/A/A、批内均值及四配对中位；48批末SHA非每内轮SHA',
    '原三倍门槛不变；首次全部通过才有唯一确认，失败不重试择优',
    '本机WSL Zen4结果不外推真实Skylake，未运行缺BMI硬件']
policy['confirmation']['output']='artifacts/skylake-input256-deferred-long-confirm-v1'
left,right=copy.deepcopy(old),copy.deepcopy(policy)
for k in ('purpose','plan','build','full_acceptance','validation','benchmark_script','limits'):left.pop(k);right.pop(k)
left['confirmation'].pop('output');right['confirmation'].pop('output');assert left==right
previous=(ROOT/'scripts/bench_skylake_andn_normal_long_linux.py').read_text(encoding='utf-8')
expected=previous.replace('冻结80对23','冻结82对23').replace("'candidate': 80","'candidate': 82").replace('新候选80','新候选82').replace('仅新80对23','仅新82对23')
expected=expected.replace('andn_normal','input256_deferred').replace('andn-normal','input256-deferred')
assert expected==(ROOT/'scripts/bench_skylake_input256_deferred_long_linux.py').read_text(encoding='utf-8')
save('experiments/skylake-input256-deferred-long-perf-v1.json',policy)
save('artifacts/skylake-input256-deferred-preflight-v1/performance-protocol-audit.json',{
    'pass_check':True,'purpose':__doc__,'old_policy':spec('experiments/skylake-andn-normal-long-perf-v1.json'),
    'new_policy':spec('experiments/skylake-input256-deferred-long-perf-v1.json'),
    'benchmark_identity_only_change':True,'all_gates_controls_repeats_orders_quiet_affinity_thp_confirmation_unchanged':True,'native_calls':0})
print(json.dumps({'validation_sha256':sha(validation),'policy_sha256':sha('experiments/skylake-input256-deferred-long-perf-v1.json')},ensure_ascii=False))
