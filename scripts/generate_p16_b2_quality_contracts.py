"""99机械复制旧u64夹具，仅替换旧零容量差断言，不执行fixture或原生质量。"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
target=ROOT/'scripts/p16_b2_quality_contracts.py'
if target.exists():raise FileExistsError('99独立u64合同胶水不覆盖')
source=ROOT/'scripts/verify_p16_workload.py'
plan=json.loads((ROOT/'experiments/p16-shared-proven-quality-v2.json').read_text(encoding='utf-8'))
prior=next(row for row in plan['sources'] if Path(row['path'])==source)
assert hashlib.sha256(source.read_bytes()).hexdigest()==prior['sha256']
text=source.read_text(encoding='utf-8')
body=text[text.index('def contracts('):text.index('\ndef photos(')]
old='assert a.model_bytes == b.model_bytes'
assert body.count(old)==1
body=body.replace(old,'assert b.model_bytes-a.model_bytes in (8,160328)  # 另由99 proxy逐模型精确核。')
header='"""99既有u64输入合同，保留旧fixture seed/公式，仅容量断言适配明确新增owner。"""\nfrom verify_p16_workload import np, io, cc, checked, state, cache_table, cache_info, integer_oracle, apply_to\n\n\n'
target.write_text(header+body+'\n',encoding='utf-8')
print('99仅静态复制u64合同输入；无fixture生成/原生调用/计时。')
