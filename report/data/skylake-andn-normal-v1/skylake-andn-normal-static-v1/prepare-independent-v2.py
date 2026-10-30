"""保留独立初件，将静态调度断言范围限定于实际两个apply函数；不改候选和门槛。"""
from pathlib import Path

here=Path(__file__).resolve().parent
source=(here/'independent_audit.py').read_text(encoding='utf-8')
old="'static_contiguous':runtime.count('schedule(static)')==2 and 'schedule(static,1)' not in runtime,"
new="'static_contiguous':runtime[runtime.index('void apply('):runtime.index('void apply_to(')].count('schedule(static)')==1 and runtime[runtime.index('void apply_to('):runtime.index('void prepare_palette(')].count('schedule(static)')==1 and 'schedule(static,1)' not in runtime,"
assert source.count(old)==1
# apply_to之后是prepare_palette，不应把后续构造并行循环算成像素分派。
source=source.replace(old,new).replace("'independent-audit.json'","'independent-audit-v2.json'")
marker="'candidate_library_loads':0,'pixel_calls':0,'performance_calls':0,'compiler_calls':0}"
replacement="'initial_audit_sha256':sha(HERE/'independent-audit.json'),'initial_script_sha256':sha(HERE/'independent_audit.py'),\n        'checker_correction':'初件完整保留；原断言误把3处既有构造/诊断schedule(static)计入两个像素函数，现分别核对apply和apply_to，门槛仍要求各一次连续static且无static,1。候选源/对象/正式root静态结果不变。',\n        "+marker
assert source.count(marker)==1
source=source.replace(marker,replacement)
with (here/'independent_audit_v2.py').open('x',encoding='utf-8') as stream:
    stream.write(source)
print('独立审计v2已生成；尚未执行')
