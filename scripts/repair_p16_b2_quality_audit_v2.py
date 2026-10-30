"""99独立audit-v2只修正既有拒绝计数为int；保留v1失败边界。"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
old=ROOT/'scripts/audit_p16_b2_packed_quality.py'
new=ROOT/'scripts/audit_p16_b2_packed_quality_v2.py'
failure=ROOT/'artifacts/p16-b2-packed-quality-v2/independent-check-v1-failure.json'
if new.exists() or failure.exists():raise FileExistsError('99审计修复不覆盖')
raw=old.read_bytes();text=raw.decode('utf-8')
before="rejects+=len(entry['rejects'])";after="rejects+=entry['rejects']"
assert text.count(before)==1
new.write_text(text.replace(before,after),encoding='utf-8')
failure.write_text(json.dumps({'passed':False,'stage':'事后独立audit-v1，非native质量',
    'source_path':str(old),'source_sha256':hashlib.sha256(raw).hexdigest(),
    'command':'python -X utf8 scripts/audit_p16_b2_packed_quality.py --input artifacts/p16-b2-packed-quality-v2 --output artifacts/p16-b2-packed-quality-v2/independent-check.json',
    'exit_code':1,'error':"TypeError: object of type 'int' has no len()",
    'failing_expression':before,'scope':'会话工具已保存原trace；此回执事后记录边界，不伪称存在当时未保存的原始日志文件。原质量/原生未重测，仅新增v2整数计数适配。',
    'new_source_sha256':hashlib.sha256(new.read_bytes()).hexdigest()},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('99 audit-v1原字节保留，独立v2仅修拒绝计数类型。')
