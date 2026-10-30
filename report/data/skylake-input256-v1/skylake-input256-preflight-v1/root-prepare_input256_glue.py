"""准备81验证胶水；只做文件派生，不编译、加载或执行原生代码。"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def put(path,text):
    with (ROOT/path).open('x',encoding='utf-8',newline='') as stream:
        stream.write(text)

verify=(ROOT/'scripts/verify_skylake_andn_normal_linux.py').read_text(encoding='utf-8')
verify=verify.replace('80按有效workers选择普通写','81按有效workers选择单YMM输入')
verify=verify.replace('andn_normal','input256').replace('normal_inplace','input256_inplace')
verify=verify.replace('新普通写只有有效workers>1','新单YMM输入只有有效workers>1')
verify=verify.replace('新普通写两块','新单YMM输入两块').replace('进入普通写','进入单YMM输入路径')
verify=verify.replace('return 80','return 81').replace("'candidate':80","'candidate':81")
put('scripts/verify_skylake_input256_linux.py',verify)
bench=(ROOT/'scripts/bench_skylake_andn_normal_long_linux.py').read_text(encoding='utf-8')
bench=bench.replace('80','81').replace('andn_normal','input256').replace('andn-normal','input256')
put('scripts/bench_skylake_input256_long_linux.py',bench)
base=ROOT/'artifacts/skylake-input256-static-v1'
base.mkdir(exist_ok=False)
for name in ('single_support.py','pair_support.py'):
    (base/name).write_bytes((ROOT/'artifacts/skylake-andn-normal-static-v1'/name).read_bytes())
print('81验证胶水与保留对象静态支持已准备；无原生调用。')
