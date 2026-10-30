"""从已审计288的独立Decimal复算器另建289版，不改旧文件。"""
from pathlib import Path
import hashlib
import json
ROOT = Path(__file__).resolve().parents[1]


def main():
    old = ROOT / 'scripts/check_direct_u16_ilp_perf.py'
    new = ROOT / 'scripts/check_direct_u10_perf.py'
    if new.exists():
        raise ValueError('不覆盖289独立复算源')
    text = old.read_text(encoding='utf-8')
    replacements = {'len(comparisons)==528': 'len(comparisons)==624',
                    "for role in ('288max','288p99')": "for role in ('289max','289p99')"}
    for a, b in replacements.items():
        if text.count(a) != 1:
            raise ValueError('独立复算器标记失配：' + a)
        text = text.replace(a, b)
    text = text.replace('八角色全部raw计时独立Decimal复核', '289八角色全部raw计时独立Decimal复核')
    new.write_text(text, encoding='utf-8', newline='\n')
    receipt = {'source_sha256': hashlib.sha256(old.read_bytes()).hexdigest(),
               'builder_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'generated_sha256': hashlib.sha256(new.read_bytes()).hexdigest(),
               'scope': '只改独立复算器的13比较数量与候选名称，未调用原汇总器或性能。'}
    (ROOT / 'artifacts/p16-direct-u10-perf-audit-generated-v1.json').write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(receipt)


if __name__ == '__main__':
    main()
