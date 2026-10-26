"""核逐TID控制阶段的显式白名单与暂存/HEAD原字节，不写索引。"""
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
        raise ValueError('不覆盖线程控制Git字节核验')
    names = ['.gitattributes', 'docs/stages/2026-10-24-p16-omp-affinity-control.md',
             'experiments/p16-omp-affinity-control-v1/control.cpp',
             'experiments/p16-omp-affinity-control-v1/plan.md',
             'experiments/p16-omp-affinity-control-v1/plan-v2.md',
             'scripts/build_omp_affinity_control.py', 'scripts/build_omp_affinity_control_v2.py',
             'scripts/check_omp_affinity_control.py', 'scripts/check_omp_affinity_control_v2.py',
             'scripts/archive_omp_affinity_control.py', 'scripts/audit_omp_affinity_control_git.py']
    names += [p.relative_to(ROOT).as_posix() for p in (ROOT / 'report/data/p16-omp-affinity-control-v1').iterdir() if p.is_file()]
    assert len(names) == len(set(names))
    if args.ref == 'index':
        actual = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '-z'], cwd=ROOT).decode('utf-8').split('\0')
        assert set(filter(None, actual)) == set(names), '暂存集合必须恰等本阶段白名单'
    rows = []
    for name in sorted(names):
        blob = subprocess.check_output(['git', 'show', '--no-textconv', (':' if args.ref == 'index' else 'HEAD:') + name], cwd=ROOT)
        data = (ROOT / name).read_bytes()
        normalized = name in ('.gitattributes', 'docs/stages/2026-10-24-p16-omp-affinity-control.md')
        assert blob == (data.replace(b'\r\n', b'\n') if normalized else data), name
        rows.append({'path': name, 'sha256': hashlib.sha256(blob).hexdigest(), 'bytes': len(blob),
                     'text_lf_normalization_allowed': normalized})
    value = {'passed': True, 'ref': args.ref, 'paths': rows,
             'raw_exact': sum(not row['text_lf_normalization_allowed'] for row in rows),
             'scope': '只核本阶段白名单；仅attrs/阶段正文沿用LF，实际执行源与raw证据原字节一致。'}
    args.output.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': True, 'ref': args.ref, 'paths': len(rows), 'raw_exact': value['raw_exact']}))


if __name__ == '__main__':
    main()
