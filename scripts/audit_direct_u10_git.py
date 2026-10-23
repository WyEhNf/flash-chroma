"""按289白名单核暂存/HEAD原始字节；只允许文档与attrs的既有LF规范化。"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ref', choices=['index', 'HEAD'], required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        raise ValueError('不覆盖Git字节审计')
    names = ['.gitattributes', 'docs/stages/2026-10-24-p16-direct-u10.md',
        'experiments/p16-direct-u10-plan-v1.md', 'experiments/p16-direct-u10-quality-plan-v1.md',
        'experiments/p16-direct-u10-perf-v1.json', 'scripts/prepare_direct_u10.py',
        'scripts/audit_direct_u10_dependencies.py', 'scripts/check_direct_u10_native.py',
        'scripts/inspect_direct_u10_rss.py', 'scripts/run_direct_u10_perf.py', 'scripts/freeze_direct_u10_perf.py',
        'scripts/prepare_direct_u10_perf_audit.py', 'scripts/check_direct_u10_perf.py',
        'scripts/archive_direct_u10.py', 'scripts/audit_direct_u10_git.py']
    for directory in ('experiments/p16-direct-u10-runtime', 'report/data/p16-direct-u10-20261024'):
        names += [p.relative_to(ROOT).as_posix() for p in (ROOT / directory).iterdir() if p.is_file()]
    names = sorted(names)
    assert len(names) == len(set(names))
    if args.ref == 'index':
        actual = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '-z'], cwd=ROOT).decode('utf-8').split('\0')
        assert set(filter(None, actual)) == set(names), '暂存范围必须恰等白名单'
    rows = []
    for name in names:
        spec = ':' + name if args.ref == 'index' else 'HEAD:' + name
        blob = subprocess.check_output(['git', 'show', '--no-textconv', spec], cwd=ROOT)
        work = (ROOT / name).read_bytes()
        normalized = name in ('.gitattributes', 'docs/stages/2026-10-24-p16-direct-u10.md')
        expected = work.replace(b'\r\n', b'\n') if normalized else work
        assert blob == expected, name
        rows.append({'path': name, 'sha256': hashlib.sha256(blob).hexdigest(),
                     'bytes': len(blob), 'text_lf_normalization_allowed': normalized})
    result = {'pass': True, 'ref': args.ref, 'paths': rows, 'raw_exact': sum(not r['text_lf_normalization_allowed'] for r in rows),
              'text_checked': sum(r['text_lf_normalization_allowed'] for r in rows),
              'scope': '仅289白名单，不包含并行tail组探针或旧未跟踪目录；不修改索引或源码。'}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'pass': True, 'ref': args.ref, 'paths': len(rows), 'raw_exact': result['raw_exact'], 'text_checked': result['text_checked']}))


if __name__ == '__main__':
    main()
