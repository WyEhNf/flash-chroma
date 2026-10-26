"""归档完整成本规模超门负例及精确根差证明合同，不包含CP或候选。"""
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
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖完整成本规模归档')
    stage = ROOT/'artifacts/cinema-first-error-cost-census-v1'; run = read(stage/'run.json')
    audit_path = ROOT/'artifacts/cinema-first-error-cost-census-audit-v1.json'; audit = read(audit_path)
    if not audit['pass'] or audit['resource_gate_pass'] or audit['summary_sha256'] != sha(stage/'summary.json') or audit['census_sha256'] != sha(stage/'census.npz'):
        raise ValueError('不是已审计的资源超门阶段')
    for name, expected in run['source_sha256'].items():
        if sha(ROOT/name) != expected: raise ValueError('实际普查源已变：'+name)
    args.output.mkdir(parents=True)
    copies = {'frozen.json': ROOT/'artifacts/cinema-first-cost-census-frozen-v1.json',
        'contract.json': ROOT/'artifacts/cinema-first-error-cost-contract-v1.json', 'run.json': stage/'run.json',
        'summary.json': stage/'summary.json', 'independent-audit.json': audit_path}
    for name, path in copies.items(): shutil.copyfile(path, args.output/name)
    sources = set(run['source_sha256']) | {'scripts/audit_cinema_first_error_cost_census.py',
        'scripts/archive_cinema_first_error_cost_census.py', 'experiments/p16-cinema-first-budget-cpsat-proposal-v1.md'}
    with zipfile.ZipFile(args.output/'source.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(sources): z.write(ROOT/name, name)
    with zipfile.ZipFile(args.output/'support-evidence.zip', 'w', zipfile.ZIP_DEFLATED) as z: z.write(stage/'census.npz', 'census.npz')
    full = ROOT/'report/data/p16-cinema-first-hotspot-20261024/manifest.json'; risk = ROOT/'report/data/p16-cinema-first-risk-20261024/manifest.json'
    manifest = {'source_sha256': {name: sha(ROOT/name) for name in sorted(sources)}, 'support_member_sha256': {'census.npz': sha(stage/'census.npz')},
        'reused_full_support_manifest': {'path': full.relative_to(ROOT).as_posix(), 'sha256': sha(full)},
        'reused_risk_manifest': {'path': risk.relative_to(ROOT).as_posix(), 'sha256': sha(risk)},
        'files': {path.name: sha(path) for path in args.output.iterdir()},
        'scope': '完整成本普查32842点/975852表行超过固定两资源门，selector93564门内；合同全过但按约STOP，没有CP、候选或不可行证明。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    for archive, field in (('source.zip', 'source_sha256'), ('support-evidence.zip', 'support_member_sha256')):
        with zipfile.ZipFile(args.output/archive) as z:
            for name, expected in manifest[field].items():
                if hashlib.sha256(z.read(name)).hexdigest() != expected: raise AssertionError('ZIP成员SHA不一致')
    print({'files': len(manifest['files']), 'sources': len(sources), 'evidence_members': 1}, flush=True)


if __name__ == '__main__': main()
