"""准备83静态/像素/性能胶水；不构建或执行原生。"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def rename(s):return s.replace('input256_deferred','input256_ordered').replace('input256-deferred','input256-ordered')
def put(path,text):
    with (ROOT/path).open('x',encoding='utf-8',newline='') as stream:stream.write(text)
verify=rename((ROOT/'scripts/verify_skylake_input256_deferred_linux.py').read_text(encoding='utf-8'))
verify=verify.replace('82分阶段写入的单YMM输入','83固定读写顺序的单YMM输入')
put('scripts/verify_skylake_input256_ordered_linux.py',verify)
bench=(ROOT/'scripts/bench_skylake_andn_normal_long_linux.py').read_text(encoding='utf-8')
bench=bench.replace('冻结80对23','冻结83对23').replace("'candidate': 80","'candidate': 83").replace('新候选80','新候选83').replace('仅新80对23','仅新83对23')
bench=bench.replace('andn_normal','input256_ordered').replace('andn-normal','input256-ordered')
assert "'comparison_inner_rounds': 1280" in bench
put('scripts/bench_skylake_input256_ordered_long_linux.py',bench)
base=ROOT/'artifacts/skylake-input256-ordered-static-v1';base.mkdir(exist_ok=False)
for name in ('single_support.py','pair_support.py'):(base/name).write_bytes((ROOT/'artifacts/skylake-input256-deferred-static-v1'/name).read_bytes())
check=rename((ROOT/'artifacts/skylake-input256-deferred-static-v1/check.py').read_text(encoding='utf-8'))
check=check.replace('82静态筛查','83静态筛查').replace('deferred_inplace/channel_avx2.cpp.o','ordered_inplace/channel_avx2.cpp.o')
check=check.replace('store_offsets[:2]==[0,32]','sorted(store_offsets[:2])==[0,32]')
check=check.replace('store_offsets[2:]==[64,96,128,160]','sorted(store_offsets[2:])==[64,96,128,160]')
check=check.replace('last_four_nt_order','last_four_nt_coverage')
put('artifacts/skylake-input256-ordered-static-v1/check.py',check)
perf=rename((ROOT/'artifacts/prepare_input256_deferred_perf.py').read_text(encoding='utf-8'))
perf=perf.replace('82静态','83静态').replace('82分阶段','83固定顺序').replace('82单YMM','83单YMM').replace('仅新82','仅新83')
perf=perf.replace('冻结82对23','冻结83对23').replace("'candidate': 82","'candidate': 83").replace('新候选82','新候选83')
put('artifacts/prepare_input256_ordered_perf.py',perf)
print('83胶水已准备，未执行候选。')
