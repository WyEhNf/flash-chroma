"""保留初件，仅把栈spill与图像写入分开统计；不改候选、对象或无栈门槛。"""
import hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
source=(HERE/'check.py').read_text(encoding='utf-8')
old="stores=[o for o in body if o['mnemonic'].startswith('vmov') and '(' in h.operands(o['operands'])[-1]]"
new="stores=[o for o in body if o['mnemonic'].startswith('vmov') and '(' in h.operands(o['operands'])[-1] and '%rsp' not in o['operands'] and not(frame and '%rbp' in o['operands'])]"
assert source.count(old)==1
source=source.replace(old,new).replace("HERE/'results.json'","HERE/'results-v2.json'")
source=source.replace("with asm.open('x',encoding='utf-8') as stream:stream.write(text)","assert asm.read_text(encoding='utf-8')==text, '原反汇编不得改变'")
source=source.replace("scope='本筛查通过仍须", "initial_checker_sha256=sha(HERE/'check.py'),initial_result_sha256=sha(HERE/'results.json'),classifier_correction='初版把栈spill存储计为图像写入，连带输出门槛误报；v2仅分类非栈输出，无栈门槛仍失败，不改源/对象或执行原生。',scope='本筛查通过仍须")
with (HERE/'check-v2.py').open('x',encoding='utf-8') as stream:stream.write(source)
print(hashlib.sha256((HERE/'check-v2.py').read_bytes()).hexdigest())
