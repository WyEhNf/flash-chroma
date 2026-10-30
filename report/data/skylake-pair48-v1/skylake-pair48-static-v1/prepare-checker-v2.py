"""保留79检查初件，仅修正死mask最后消费后的结果处理；不编译或执行原生。"""
from pathlib import Path
HERE = Path(__file__).resolve().parent
source = (HERE/'inspect.py').read_text(encoding='utf-8')
old = "all(o['offset']==last_use and o['mnemonic']=='andn' for o in writes)"
assert source.count(old) == 1
text = source.replace(old, "all(o['offset']>=last_use for o in writes)")
text = text.replace('# 回环要求掩码整个迭代不变；直线只允许最后一次ANDN同时把死掩码写成结果。',
                    '# 回环要求mask不变；直线最后消费后mask已死，后续结果拆位可复用寄存器。')
text = text.replace('results.json', 'results-v2.json')
marker = "    save_new(HERE/'results-v2.json',result)"
assert text.count(marker) == 1
text = text.replace(marker, "    result['initial_script_sha256']=sha(HERE/'inspect.py')\n"
                           "    result['initial_results_sha256']=sha(HERE/'results.json')\n"
                           "    result['checker_correction']='所有ANDN消费前mask正确；直线无后续ANDN且写入均在最后消费以后，可用于结果移位。源/对象/门槛未变，旧件保留。'\n"+marker)
with (HERE/'inspect-v2.py').open('x', encoding='utf-8') as stream:
    stream.write(text)
