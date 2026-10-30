"""准备80全域后的协议生成器；本入口本身不生成性能策略或执行原生。"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'artifacts/skylake-pair48-preflight-v1/prepare-performance.py'
text=source.read_text(encoding='utf-8').replace('skylake-pair48','skylake-andn-normal').replace('skylake_pair48','skylake_andn_normal').replace('pair48_enabled','andn_normal_enabled')
text=text.replace('79完整域','80完整域').replace('79实际双像素ANDN','80实际有效workers分派ANDN').replace('79双像素mem64输入ANDN直接对23受控长批次','80多线程原地ANDN32/T0普通写及其余79保留路径直接对23受控长批次').replace('仅新79，不重评78或旧失败，不跨场拼接','仅新80，不重评79/78或旧失败，不跨场拼接').replace('实际pair48分派','实际ANDN能力与源分派').replace('输入加载指令减少不等于输入字节或DRAM流量减半，不把诊断当吞吐验收','多线程原地切到mem32及T0普通写，源/预排冻结；不能把旧诊断方向乘成预期吞吐')
needle="assert r['model_accounting_bytes']['candidate']['chain'] == 28046644"
assert text.count(needle)==1
text=text.replace(needle,needle+"\nassert r['normal_inplace_alignment_comparisons']==64 and r['normal_inplace_actual_offsets']==list(range(64))\nassert r['normal_inplace_alignment_pixels']==65793")
with (Path(__file__).with_name('prepare-performance.py')).open('x',encoding='utf-8') as stream:
    stream.write(text)
