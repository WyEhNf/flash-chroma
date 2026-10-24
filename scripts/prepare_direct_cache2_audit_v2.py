"""只修正离线审计的历史分离路径标签to12→to；保留原失败审计，绝不重跑native。"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/p16-direct-cache2-quality-audit-v2'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    target = ROOT / 'scripts/audit_direct_cache2_quality_v2.py'
    old = ROOT / 'scripts/audit_direct_cache2_quality.py'
    if OUT.exists() or target.exists():
        raise FileExistsError('不覆盖审计机械v2')
    text = old.read_text(encoding='utf-8')
    before = "key = (row['image'], row['path'])"
    assert text.count(before) == 2
    text = text.replace(before, "key = (row['image'], 'to' if row['path'] == 'to12' else row['path'])", 1)
    text = text.replace("OUT / 'independent-check.json'", "OUT / 'independent-check-v2.json'", 1)
    target.write_text(text, encoding='utf-8', newline='\n')
    OUT.mkdir(parents=True)
    sources = [Path(__file__), old, target, ROOT / 'scripts/qualify_cinema_current_full.py']
    result = {'purpose': __doc__, 'sources_sha256': {str(p.relative_to(ROOT)): sha(p) for p in sources},
        'primary_results_sha256': sha(ROOT / 'artifacts/p16-direct-cache2-quality-v1/results.json'),
        'legacy_current_results_sha256': sha(ROOT / 'artifacts/cinema-current-full-quality-v2/results.json'),
        'legacy_best_results_sha256': sha(ROOT / 'artifacts/p16-direct-rgb24-quality-v1/results.json'),
        'failed_audit': {'exit_code': 1, 'exception': "KeyError: ('kodak-kodim03', 'to')",
                         'evidence_origin': '本会话exec工具输出转录；原失败未写本地stdout，不伪称原始日志'},
        'mechanical_change': '仅历史to12分离路径标准化与新输出文件名；全部数学/原生/实际SHA原件不改',
        'native_calls': 0, 'performance_calls': 0}
    (OUT / 'protocol.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'prepared': True, 'native_calls': 0, 'new_audit_sha256': sha(target)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
