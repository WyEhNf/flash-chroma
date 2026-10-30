"""80完整域与静态通过后才冻结首次受控长批次；本文件不执行原生。"""
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]


def read(p):
    return json.loads((ROOT/p).read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()


def spec(p):
    return {'path': p, 'sha256': sha(p)}


def write(p, value):
    with (ROOT/p).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


plan = 'experiments/skylake-andn-normal-v1.json'
build = 'artifacts/skylake-andn-normal-linux-build-v1/build.json'
full = 'artifacts/skylake-andn-normal-linux-full-v1/results.json'
static = 'artifacts/skylake-andn-normal-static-v1/results-v2.json'
r, st = read(full), read(static)
assert r['pass'] and r['andn_normal_enabled'] == {'single': 0, 'chain': 1}
assert r['model_accounting_bytes']['candidate']['chain'] == 28046644
assert r['normal_inplace_alignment_comparisons']==64 and r['normal_inplace_actual_offsets']==list(range(64))
assert r['normal_inplace_alignment_pixels']==65793
assert st['accepted'] and st['plan_sha256'] == sha(plan) and st['build_sha256'] == sha(build)
validation = 'experiments/skylake-andn-normal-validation-v1.json'
write(validation, {'purpose': '80实际有效workers分派ANDN及完整RGB8/边界验证身份，不计性能',
    'plan_sha256': sha(plan), 'source_sha256': {p: sha(p) for p in (
        'scripts/verify_skylake_andn_normal_linux.py', 'scripts/paged_table_support.py',
        'scripts/outplace_support.py', 'scripts/guarded_buffer_support.py')},
    'full_result': spec(full), 'static_result': spec(static)})
p = read('experiments/skylake-andn-split-long-perf-v1.json')
p['purpose'] = '80多线程原地ANDN32/T0普通写及其余79保留路径直接对23受控长批次；原三倍/A/A/唯一条件确认不变'
for key, path in {'plan': plan, 'build': build, 'full_acceptance': full, 'validation': validation,
                  'benchmark_script': 'scripts/bench_skylake_andn_normal_long_linux.py'}.items():
    p[key] = spec(path)
p['limits'] = ['仅新80，不重评79/78或旧失败，不跨场拼接',
    '唯一16MiB线性表，实际ANDN能力与源分派及前后精确VMA/全THP核对',
    '多线程原地切到mem32及T0普通写，源/预排冻结；不能把旧诊断方向乘成预期吞吐',
    '原16/64内轮、ABBA、批内均值及四配对中位，批末SHA不是每内轮SHA',
    '原三倍门槛与同库控制不变；首次全部通过才有唯一确认，失败不重试择优',
    'CPU不支持BMI1时精确回退；未执行真实缺BMI1硬件，不外推Skylake']
p['confirmation']['output'] = 'artifacts/skylake-andn-normal-long-confirm-v1'
write('experiments/skylake-andn-normal-long-perf-v1.json', p)
print(json.dumps({'validation_sha256': sha(validation),
                  'policy_sha256': sha('experiments/skylake-andn-normal-long-perf-v1.json')}, ensure_ascii=False))
