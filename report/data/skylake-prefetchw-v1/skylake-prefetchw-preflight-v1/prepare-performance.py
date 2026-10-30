"""74完整域后首次冻结受控长批次；不执行像素。"""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def spec(p):return {'path':p,'sha256':sha(p)}
def write(p,v):
    with (ROOT/p).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
plan='experiments/skylake-prefetchw-v1.json';full='artifacts/skylake-prefetchw-linux-full-v1/results.json'
r=read(full);assert r['pass'] and r['prefetchw_enabled']=={'single':0,'chain':1} and r['model_accounting_bytes']['candidate']['chain']==28046644
validation_path='experiments/skylake-prefetchw-validation-v1.json'
v={'purpose':'74实际写预取分派及完整RGB8/边界验证身份，不计性能','plan_sha256':sha(plan),'source_sha256':{p:sha(p) for p in ('scripts/verify_skylake_prefetchw_linux.py','scripts/paged_table_support.py','scripts/outplace_support.py','scripts/guarded_buffer_support.py')},'full_result':spec(full)}
write(validation_path,v)
p=read('experiments/skylake-tilexy-t0-long-perf-v1.json')
p['purpose']='74支持prfchw时多线程原地改用写预取，直接对23受控长批次；原三倍/A/A/唯一条件确认不变'
for key,path in {'plan':plan,'build':'artifacts/skylake-prefetchw-linux-build-v1/build.json','full_acceptance':full,'validation':validation_path,'benchmark_script':'scripts/bench_skylake_prefetchw_long_linux.py'}.items():p[key]=spec(path)
p['limits']=['仅新74写预取，不重评旧候选判定','16MiB线性表；单线程及分离输出保留原NTA/NT，多线程原地实际W/普通写；前后真实W启用及精确VMA/全THP验证','原16/64内轮、ABBA、批内均值及四配对中位；每批末SHA非每内轮SHA','原三倍门槛和同库控制不放宽；首次通过后才有唯一确认','CPU不支持prfchw时精确回退T0；本机未执行真实缺特征硬件；不外推Skylake性能']
p['confirmation']['output']='artifacts/skylake-prefetchw-long-confirm-v1'
write('experiments/skylake-prefetchw-long-perf-v1.json',p)
print(json.dumps({'validation_sha256':sha(validation_path),'policy_sha256':sha('experiments/skylake-prefetchw-long-perf-v1.json')},ensure_ascii=False))