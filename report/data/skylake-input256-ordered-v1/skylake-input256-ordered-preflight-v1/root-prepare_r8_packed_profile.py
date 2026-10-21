"""冻结唯一R连续8色/3bit只读筛查；不启动候选原生或性能。"""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/skylake-r8-packed-profile-v1';OUT.mkdir(exist_ok=False)
text=(ROOT/'artifacts/skylake-brick2-packed-profile-v1/analyze.py').read_text(encoding='utf-8')
text=text.replace('固定2×2×2砖块','固定R连续8色块')
text=text.replace('def coarse(c):return ((c>>1)&0x7f)|((c>>2)&0x3f80)|((c>>3)&0x1fc000)','def coarse(c):return c>>3')
text=text.replace('def fine(c):return (c&1)|((c>>7)&2)|((c>>14)&4)','def fine(c):return c&7')
text=text.replace('def inverse(q,k):return ((q&0x7f)<<1)|((q&0x3f80)<<2)|((q&0x1fc000)<<3)|(k&1)|((k&2)<<7)|((k&4)<<14)','def inverse(q,k):return (q<<3)|k')
old=" bricks=np.empty((128,128,128,8),dtype=np.uint8)\n for k in range(8):bricks[:,:,:,k]=direct[(k>>2)&1::2,(k>>1)&1::2,k&1::2]\n members=bricks.reshape(-1,8)"
assert text.count(old)==1
text=text.replace(old,' members=linear.reshape(-1,8)')
text=text.replace("r'0xfefefe|0x010101|2×2×2|2x2x2|2³|\\bbrick'","r'R连续.*3bit|3bit.*R连续|R低.*3bit|3bit.*R低|r8.*pack|code.*>>3'")
text=text.replace('未发现已实现相同2立方体/3bit差值GPR查表。42为原23按RGB字典序的B连续8色主词；47为4立方体未压缩u8表；62为R连续8色5bit差值；70为64B去重字典，均与本统计不同。',
 '本轮只统计固定R连续8色/3bit表示，不据关键词搜索断言完整组合从未实现。23/42为B连续8色3bit，62为R连续8色5bit；实现前仍须主流程完整历史核对。')
text=text.replace("coarse='PEXT(c,0xfefefe) = (R>>1) | ((G>>1)<<7) | ((B>>1)<<14)',fine='PEXT(c,0x010101) = (R&1) | ((G&1)<<1) | ((B&1)<<2)'", "coarse='c>>3，固定G/B的连续8个R',fine='c&7'")
text=text.replace('空间覆盖32×2×2个RGB8颜色','空间覆盖128×1×1个RGB8颜色')
text=text.replace('未计PEXT/位移/调色板依赖成本','未计标量位移、异常分支与调色板依赖成本')
with (OUT/'analyze.py').open('x',encoding='utf-8',newline='') as f:f.write(text)
protocol={'purpose':__doc__,'script_sha256':hashlib.sha256((OUT/'analyze.py').read_bytes()).hexdigest(),
    'mapping':'R | G<<8 | B<<16；coarse=c>>3、fine=c&7，固定8色/3bit，不扫描轴/尺寸/参数',
    'gate':{'exception_packet8_fraction_max':0.05,'mean_word_lines_per64_ratio_max':0.80},
    'decision':'只有两个固定只读门槛均过才考虑实现；失败停止；行集合不是硬件miss或吞吐证据。',
    'native_calls':0,'performance_calls':0}
with (OUT/'protocol.json').open('x',encoding='utf-8') as f:json.dump(protocol,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(protocol,ensure_ascii=False))
