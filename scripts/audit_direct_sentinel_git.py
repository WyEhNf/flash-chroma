"""独立检查290/291暂存或HEAD的白名单与原始字节；不编辑索引。"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from archive_direct_sentinel import sentinel_paths

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ref', choices=['index', 'HEAD'], required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('不覆盖Git原字节审计')
    names = sentinel_paths() + ['.gitattributes', 'docs/stages/2026-10-24-p16-direct-sentinel.md']
    names += [path.relative_to(ROOT).as_posix() for path in (ROOT / 'report/data/p16-direct-sentinel-20261024').iterdir() if path.is_file()]
    assert len(names) == len(set(names))
    if args.ref == 'index':
        staged = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '-z'], cwd=ROOT).decode('utf-8')
        assert set(filter(None, staged.split('\0'))) == set(names), '暂存必须恰等本阶段白名单'
    rows = []
    for name in sorted(names):
        spec = ':' + name if args.ref == 'index' else 'HEAD:' + name
        blob = subprocess.check_output(['git', 'show', '--no-textconv', spec], cwd=ROOT)
        work = (ROOT / name).read_bytes()
        normalize = name in ['.gitattributes', 'docs/stages/2026-10-24-p16-direct-sentinel.md']
        assert blob == (work.replace(b'\r\n', b'\n') if normalize else work), name
        rows.append({'path': name, 'bytes': len(blob), 'sha256': hashlib.sha256(blob).hexdigest(), 'LF_normalization_allowed': normalize})
    result = {'passed': True, 'ref': args.ref, 'paths': rows, 'raw_exact': sum(not row['LF_normalization_allowed'] for row in rows),
              'scope': '仅本阶段白名单；旧失败源和执行冻结源均保持原字节，不含并行精度阶段。'}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': True, 'ref': args.ref, 'paths': len(rows), 'raw_exact': result['raw_exact']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
