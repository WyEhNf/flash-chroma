"""只准备80静态/完整验证框架，不编译或执行原生。"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'artifacts/skylake-andn-normal-static-v1'
HERE.mkdir(exist_ok=False)
single=(ROOT/'artifacts/skylake-andn-split-static-v1/inspect-v2.py').read_text(encoding='utf-8')
single=single.replace("all(o['offset']==last_use and o['mnemonic']=='andn' for o in writes)","all(o['offset']>=last_use for o in writes)")
(HERE/'single_support.py').write_text(single,encoding='utf-8')
(HERE/'pair_support.py').write_bytes((ROOT/'artifacts/skylake-pair48-static-v1/inspect-v2.py').read_bytes())
verify=(ROOT/'scripts/verify_skylake_pair48_linux.py').read_text(encoding='utf-8')
verify=verify.replace('79双像素ANDN输入','80按有效workers选择普通写').replace('pair48','andn_normal')
(ROOT/'scripts/verify_skylake_andn_normal_linux.py').write_text(verify,encoding='utf-8')
bench=(ROOT/'scripts/bench_skylake_pair48_long_linux.py').read_text(encoding='utf-8')
bench=bench.replace('79','80').replace('pair48','andn_normal').replace('andn-normal','andn-normal')
(ROOT/'scripts/bench_skylake_andn_normal_long_linux.py').write_text(bench,encoding='utf-8')
