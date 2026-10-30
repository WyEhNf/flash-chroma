"""99事后独立audit-v2仅补两个紧凑角色集合，保留冻结v1和失败log。"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
old=ROOT/'scripts/audit_p16_b2_packed.py';new=ROOT/'scripts/audit_p16_b2_packed_v2.py'
folder=ROOT/'artifacts/p16-b2-packed-performance-v1'
failure=folder/'offline-audit-v1-failure.json'
if new.exists() or failure.exists():raise FileExistsError('99正式审计修复不覆盖')
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(old)=='325b931fde2b52e96104da526bbee78ec72ad60564aceb858175178b500b3021'
text=old.read_text(encoding='utf-8');before="('reference','previous','candidate')"
assert text.count(before)==2
new.write_text(text.replace(before,"('reference','previous','isolated','candidate')"),encoding='utf-8')
failure.write_text(json.dumps({'passed':False,'old_source_sha256':sha(old),
    'raw_failed_log_path':str(folder/'offline-audit.log'),'raw_failed_log_sha256':sha(folder/'offline-audit.log'),
    'failure':'AssertionError：原角色集合生成器只替换带空格tuple，两个无空格集合仍三个角色。',
    'scope':'只改事后集合枚举；不改raw/driver/统计/阈值/质量，也不重复测量。',
    'new_source_sha256':sha(new)},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('99冻结计数audit-v1/失败log保留，独立v2只补两处紧凑角色集合。')
