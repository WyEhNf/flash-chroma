"""准备82胶水及静态门槛；不编译、加载或执行原生。"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def rename(text):
    return text.replace('input256','input256_deferred').replace('skylake-input256_deferred','skylake-input256-deferred')
for name in ('verify_skylake_input256_linux.py','bench_skylake_input256_long_linux.py'):
    text=rename((ROOT/'scripts'/name).read_text(encoding='utf-8'))
    text=text.replace('81按有效workers选择单YMM输入','82分阶段写入的单YMM输入').replace('冻结81对23','冻结82对23')
    text=text.replace("'candidate': 81","'candidate': 82").replace('新候选81','新候选82')
    with (ROOT/'scripts'/rename(name)).open('x',encoding='utf-8') as stream:stream.write(text)
target=ROOT/'artifacts/skylake-input256-deferred-static-v1';target.mkdir(exist_ok=False)
for name in ('single_support.py','pair_support.py'):
    (target/name).write_bytes((ROOT/'artifacts/skylake-input256-static-v1'/name).read_bytes())
print('82胶水已准备，未执行原生。')
