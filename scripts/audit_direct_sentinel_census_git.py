"""核哨兵普查阶段显式白名单与Git原字节，不修改索引。"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ref', choices=['index', 'HEAD'], required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖哨兵普查Git审计')
    names = ['.gitattributes', 'docs/stages/2026-10-24-p16-sentinel-census.md',
             'experiments/p16-sentinel-census-plan-v1.json', 'scripts/census_direct_sentinel.py',
             'scripts/archive_direct_sentinel_census.py', 'scripts/audit_direct_sentinel_census_git.py']
    names += [path.relative_to(ROOT).as_posix() for path in (ROOT / 'report/data/p16-sentinel-census-v1').iterdir() if path.is_file()]
    assert len(names) == len(set(names))
    if args.ref == 'index':
        actual = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '-z'], cwd=ROOT).decode('utf-8').split('\0')
        assert set(filter(None, actual)) == set(names), '暂存集合必须恰等白名单'
    rows = []
    for name in sorted(names):
        blob = subprocess.check_output(['git', 'show', '--no-textconv', (':' if args.ref == 'index' else 'HEAD:') + name], cwd=ROOT)
        raw = (ROOT / name).read_bytes()
        normalized = name in ('.gitattributes', 'docs/stages/2026-10-24-p16-sentinel-census.md')
        assert blob == (raw.replace(b'\r\n', b'\n') if normalized else raw), name
        rows.append({'path': name, 'sha256': hashlib.sha256(blob).hexdigest(), 'bytes': len(blob),
                     'text_lf_normalization_allowed': normalized})
    value = {'passed': True, 'ref': args.ref, 'paths': rows,
             'raw_exact': sum(not row['text_lf_normalization_allowed'] for row in rows),
             'scope': '只核此普查；执行原源及证据原字节，attrs/阶段说明沿既有LF规范化。'}
    args.output.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': True, 'ref': args.ref, 'paths': len(rows), 'raw_exact': value['raw_exact']}))


if __name__ == '__main__':
    main()
