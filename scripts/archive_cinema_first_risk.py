"""归档全正支撑鲁棒危险筛查与安全CSR；不求解CP，不复制大后缀。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path): return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖完整危险筛查归档')
    study = ROOT/'artifacts/cinema-first-risk-v1'; run = read(study/'run.json'); summary = read(study/'summary.json')
    audit_path = ROOT/'artifacts/cinema-first-risk-independent-v1.json'; audit = read(audit_path)
    if not audit['pass'] or audit['summary_sha256'] != sha(study/'summary.json') or audit['screen_sha256'] != sha(study/'screen.npz'):
        raise ValueError('危险筛查审计不属于当前原件')
    if run['cp_solver_called'] or summary['cp_solver_called'] or audit['cp_solver_called']:
        raise ValueError('筛查阶段不应执行CP')
    for name, expected in run['source_sha256'].items():
        if sha(ROOT/name) != expected: raise ValueError('筛查实际源已变：'+name)
    args.output.mkdir(parents=True)
    copies = {'run.json': study/'run.json', 'summary.json': study/'summary.json', 'independent-audit.json': audit_path,
        'contract.json': ROOT/'artifacts/cinema-first-risk-contract-v1.json'}
    for name, path in copies.items(): shutil.copyfile(path, args.output/name)
    sources = set(run['source_sha256']) | {'scripts/audit_cinema_first_risk.py', 'scripts/archive_cinema_first_risk.py'}
    with zipfile.ZipFile(args.output/'source.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(sources): z.write(ROOT/name, name)
    evidence = {'screen.npz': study/'screen.npz', 'danger-allowed.npz': study/'danger-allowed.npz'}
    with zipfile.ZipFile(args.output/'support-evidence.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name, path in evidence.items(): z.write(path, name)
    reused = ROOT/'report/data/p16-cinema-first-hotspot-20261024/manifest.json'
    manifest = {'source_sha256': {name: sha(ROOT/name) for name in sorted(sources)},
        'support_member_sha256': {name: sha(path) for name, path in evidence.items()},
        'reused_full_support_manifest': {'path': reused.relative_to(ROOT).as_posix(), 'sha256': sha(reused)},
        'files': {path.name: sha(path) for path in args.output.iterdir()},
        'scope': '固定86节点±2下完整70571支撑鲁棒筛查：2224危险点、126765安全元组；不求解CP，不证明平均预算。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    for archive, field in (('source.zip', 'source_sha256'), ('support-evidence.zip', 'support_member_sha256')):
        with zipfile.ZipFile(args.output/archive) as z:
            for name, expected in manifest[field].items():
                if hashlib.sha256(z.read(name)).hexdigest() != expected: raise AssertionError('ZIP成员原字节不符')
    print({'raw_files': len(manifest['files']), 'source_members': len(sources), 'evidence_members': len(evidence)}, flush=True)


if __name__ == '__main__': main()
