"""100沿99已修复四角色协议生成独立driver/audit，不执行计时。"""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
target=ROOT/'scripts/bench_p16_scanline_prepare.py';audit=ROOT/'scripts/audit_p16_scanline_prepare.py';decimal=ROOT/'scripts/audit_p16_scanline_decimal.py'
if any(p.exists() for p in (target,audit,decimal)):raise FileExistsError('100正式三源不覆盖')
text=(ROOT/'scripts/bench_p16_b2_packed.py').read_text(encoding='utf-8')
assert text.count("'candidate': 99")==1
text=text.replace("'candidate': 99","'candidate': 100").replace('99','100')
target.write_text(text,encoding='utf-8',newline='\n')
text=(ROOT/'scripts/audit_p16_b2_packed_v2.py').read_text(encoding='utf-8')
begin=text.index("    assert quality['passed']")
end=text.index("    expected = {(r['role'], r['images'])")
text=text[:begin]+'''    assert quality['passed'] and quality['counters']==plan['expected_quality_counters']
    assert len(quality['photos'])==40 and len(quality['contracts'])==8 and len(quality['table_cases'])==14
    for row in quality['table_cases']:
        assert row['byte_mismatches']==0 and row['previous_sha256']==row['candidate_sha256']
'''+text[end:]
lines=[line for line in text.splitlines() if 'expected_capacity+=' not in line]
audit.write_text('\n'.join(lines).replace('99','100')+'\n',encoding='utf-8',newline='\n')
text=(ROOT/'scripts/audit_p16_b2_packed_decimal.py').read_text(encoding='utf-8')
decimal.write_text(text.replace('99','100'),encoding='utf-8',newline='\n')
print('100正式三源静态生成；尚未预检或计时。')
