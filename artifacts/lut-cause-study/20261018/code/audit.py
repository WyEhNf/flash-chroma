"""独立检查结果范围、来源哈希、逐图聚合和关键诊断结论，不重跑拟合。"""
import csv
import hashlib
import json
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1]
ROOT = OUT.parents[2]
DATA = OUT/'data'
def read(name):
    return list(csv.DictReader((DATA/name).open(encoding='utf-8-sig')))
run=json.loads((DATA/'run.json').read_text(encoding='utf-8'))
for path, expected in run['inputs_and_code_sha256'].items():
    with (ROOT/path).open('rb') as f:
        assert hashlib.file_digest(f,'sha256').hexdigest()==expected,path
metrics=read('metrics.csv'); images=read('per-image.csv')
assert len(metrics)==20 and len(images)==2000
index={(r['case'],r['variant']):r for r in metrics}
assert len(index)==20
for key,r in index.items():
    part=[p for p in images if (p['case'],p['variant'])==key]
    assert len(part)==100 and len({p['image'] for p in part})==100
    expected={'photo_mean':sum(float(p['mean']) for p in part)/100,
        'photo_rms':math.sqrt(sum(float(p['rms'])**2 for p in part)/100),
        'photo_worst_p99':max(float(p['p99']) for p in part),'photo_max':max(float(p['max']) for p in part)}
    for k,v in expected.items(): assert abs(float(r[k])-v)<1e-10,(key,k)
for m in [17,33]:
    assert float(index['filmic06',f'raw_exact_positions_exact_weights_m{m}']['cube_max'])==0
    for field in ['cube_mean','cube_rms','cube_max','photo_mean','photo_worst_p99']:
        assert index['filmic06',f'byte_nodes_exact_weights_m{m}'][field]==index['filmic06',f'byte_nodes_q16_weights_m{m}'][field]
checks=json.loads((DATA/'checks.json').read_text(encoding='utf-8'))
assert sum(x['check']=='全色域整数参考逐字节一致' for x in checks)==10
assert sum(x['check']=='历史百图四项误差一致' for x in checks)==10
summary=dict(status='通过',sha256_files=len(run['inputs_and_code_sha256']),variants=20,per_image_rows=2000,
    frozen_cube_oracle_checks=10,new_cube_oracle_checks=2,historical_full_quality_checks=10,
    scope='来源字节、唯一配对、100图聚合、诊断零误差/Q16不变结论；不替代性能或实板测试')
(DATA/'audit.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
