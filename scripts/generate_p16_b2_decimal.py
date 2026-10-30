"""99独立50位复算沿97算式，仅固定三分母计数126/1764，不执行数据复算。"""
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
target=ROOT/'scripts/audit_p16_b2_packed_decimal.py'
if target.exists():raise FileExistsError('99十进制审计源不覆盖')
old=ROOT/'scripts/audit_p16_shared_proven_decimal.py'
text=old.read_text(encoding='utf-8')
assert text.count('assert sets == 84 and len(differences) == 1176')==1
text=text.replace('assert sets == 84 and len(differences) == 1176','assert sets == 126 and len(differences) == 1764')
text=text.replace('97事后50位十进制独立复算84','99事后50位十进制独立复算126').replace('97十进制原始回执','99十进制原始回执')
target.write_text(text,encoding='utf-8')
print('99仅静态生成十进制审计源，母本SHA256='+hashlib.sha256(old.read_bytes()).hexdigest())
