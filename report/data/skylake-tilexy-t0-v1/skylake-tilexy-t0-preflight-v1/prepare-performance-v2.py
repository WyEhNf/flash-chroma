"""仅在73完整域通过后冻结原三倍门槛和长批次身份；不运行像素。"""
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def read(p): return json.loads((ROOT/p).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def spec(p): return {'path':p,'sha256':sha(p)}
def write(p,v):
    with (ROOT/p).open('x',encoding='utf-8') as f: json.dump(v,f,ensure_ascii=False,indent=2); f.write('\n')
plan='experiments/skylake-tilexy-t0-v1.json'
full='artifacts/skylake-tilexy-t0-linux-full-v1/results.json'
verify=read(full)
assert verify['pass'] and verify['byte_mismatches']==0 and verify['tilexy_validation']['byte_mismatches_vs_linear']==0
assert verify['model_accounting_bytes']['candidate']['chain']==44823884
validation_path='experiments/skylake-tilexy-t0-validation-v1.json'
validation={'purpose':'73双表独立逆置换及完整RGB8/边界验证身份，不计性能','plan_sha256':sha(plan),'source_sha256':{p:sha(p) for p in ('scripts/verify_skylake_tilexy_t0_linux.py','scripts/paged_table_support.py','scripts/outplace_support.py','scripts/guarded_buffer_support.py')},'full_result':spec(full)}
assert read(validation_path)==validation
p=read('experiments/skylake-adaptive-dictionary-long-perf-v1.json')
p['purpose']='73多线程原地组合二维分块/四ID/T0普通写，直接对23受控长批次；原三倍门槛和唯一条件确认保持'
for key,path in {'plan':plan,'build':'artifacts/skylake-tilexy-t0-linux-build-v1/build.json','full_acceptance':full,'validation':validation_path,'benchmark_script':'scripts/bench_skylake_tilexy_t0_long_linux.py'}.items(): p[key]=spec(path)
p['limits']=['仅新73组合，不重评旧54、65、68或71的失败判定','单线程及分离输出用16MiB线性，多线程原地用16MiB二维表；两表分别核对前后精确VMA/全THP','16/64原生内轮，先批内均值再四worker配对中位；每批末SHA，非每内轮SHA','主门槛及A/A控制、唯一条件确认与71/72协议相同，不放宽','仅AMD/WSL2本机实测，通用AVX2，不外推Skylake或改系统权限/频率/缓解']
p['confirmation']['output']='artifacts/skylake-tilexy-t0-long-confirm-v1'
write('experiments/skylake-tilexy-t0-long-perf-v1.json',p)
print(json.dumps({'validation':sha(validation_path),'policy':sha('experiments/skylake-tilexy-t0-long-perf-v1.json')},ensure_ascii=False))