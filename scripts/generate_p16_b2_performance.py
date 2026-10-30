"""99机械沿用97计时边界/统计，新增97机制分母和第四角色，生成后须冻结。"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
target=ROOT/'scripts/bench_p16_b2_packed.py';audit=ROOT/'scripts/audit_p16_b2_packed.py'
if target.exists() or audit.exists():raise FileExistsError('99唯一正式源不覆盖')
prior=json.loads((ROOT/'experiments/p16-shared-proven-performance-v1.json').read_text(encoding='utf-8'))
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
for path in (ROOT/'scripts/bench_p16_shared_proven.py',ROOT/'scripts/audit_p16_shared_proven.py'):
    expected=next(row['sha256'] for row in prior['sources'] if Path(row['path'])==path)
    assert sha(path)==expected
text=(ROOT/'scripts/bench_p16_shared_proven.py').read_text(encoding='utf-8')
text=text.replace("{'reference': 87, 'previous': 95, 'candidate': 97}","{'reference': 87, 'previous': 95, 'isolated': 97, 'candidate': 99}")
text=text.replace("('reference', 'previous', 'candidate')","('reference', 'previous', 'isolated', 'candidate')")
text=text.replace('97首次正式','99首次正式').replace('97三角色配对进程完成','99四角色配对进程完成')
text=text.replace('同场97/87与97/95独立冷热资格，不以95分母救87的50；全部1584实际末组SHA/AA/12RSS保留。',
    '同场99/87、99/95与99/97独立冷热资格；不以97慢分母救87/95硬线，全部2112实际末组SHA/AA/16RSS保留。')
text=text.replace('97同场87/95/97；两个分母','99同场87/95/97/99；三个分母')
target.write_text(text,encoding='utf-8')
old=(ROOT/'scripts/audit_p16_shared_proven.py').read_text(encoding='utf-8')
header=old[:old.index("    assert plan['threshold_pixels']")]
header=header.replace('独立复算97同场87/95两分母、全部AA/1584实际SHA和12RSS','独立复算99三分母、全部AA/2112实际SHA和16RSS')
header+='''    assert plan['threshold_pixels']==1<<26 and plan['images']==plan['hot_images']==[1,10,100]
    assert plan['default_images']==[1] and plan['denominators']==['reference','previous','isolated']
    assert quality['passed'] and len(quality['photos'])+len(quality['boundary_photos'])==40
    assert len(quality['contracts'])==2 and sum(len(v) for v in quality['contracts'].values())==16
    assert quality['private_kernel_contract']['passed'] and quality['private_kernel_contract']['first_stage_u64_pixels']==33554432
    assert len(quality['table_cases'])+len(quality['contract_tables'])==34
    for row in quality['table_cases']+quality['contract_tables']:
        assert row['table_mismatches']==0 and row['measured_empty_owner_handle_difference']==8
        assert row['measured_model_bytes_delta']==8+(160320 if row['expected_b2_private_qualification'] else 0)
'''
tail=old[old.index("    expected = {(r['role'], r['images'])"):]
tail=tail.replace("('reference', 'previous', 'candidate')","('reference', 'previous', 'isolated', 'candidate')")
tail=tail.replace("len(w['records']) == 72 and len(w['cold_records']) == 18","len(w['records']) == 96 and len(w['cold_records']) == 24")
tail=tail.replace("len(result['hot']) == 48 and len(result['cold']) == 12","len(result['hot']) == 72 and len(result['cold']) == 18")
tail=tail.replace('assert checks == 1584','assert checks == 2112')
tail=tail.replace("'hot_records': 288, 'cold_records': 72","'hot_records': 384, 'cold_records': 96")
tail=tail.replace("'hot_comparisons': 48, 'cold_metric_comparisons': 36","'hot_comparisons': 72, 'cold_metric_comparisons': 54")
tail=tail.replace("'independent_rss_processes': 12","'independent_rss_processes': 16")
lines=[]
for line in tail.splitlines():
    lines.append(line)
    if 'expected_capacity =' in line:
        indentation=line[:len(line)-len(line.lstrip())]
        if "r['model']" in line:
            lines.append(indentation+"if r['role']=='candidate':expected_capacity+=8+(160320 if r['model']=='ordinary' and not expected_direct else 0)")
        else:
            assert 'model ==' in line
            lines.append(indentation+"if role=='candidate':expected_capacity+=8+(160320 if model=='ordinary' and not expected_direct else 0)")
audit.write_text(header+'\n'.join(lines)+'\n',encoding='utf-8')
print('99正式driver/audit静态生成完成；未执行预检或计时。')
