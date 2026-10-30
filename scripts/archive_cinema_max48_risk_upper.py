"""封存当前122节点完整风险普查及条件误差上界，保留无CP状态。"""
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
    if args.output.exists(): raise ValueError('不覆盖完整风险与条件上界归档')
    stage = ROOT/'artifacts/cinema-max48-risk-upper-v1'; run = read(stage/'run.json'); summary = read(stage/'summary.json')
    audit_path = ROOT/'artifacts/cinema-max48-risk-upper-independent-v1.json'; audit = read(audit_path)
    if not audit['pass'] or audit['summary_sha256'] != sha(stage/'summary.json') or audit['screen_sha256'] != sha(stage/'screen.npz'):
        raise ValueError('不是已认证当前122节点完整筛查')
    if run['cp_solver_called'] or summary['cp_solver_called'] or not summary['within_frozen_resource_gate']:
        raise ValueError('阶段边界或固定资源门不符')
    for name, expected in run['source_sha256'].items():
        if sha(ROOT/name) != expected: raise ValueError('执行源已变：'+name)
    args.output.mkdir(parents=True)
    raw = {'frozen.json': ROOT/'artifacts/cinema-max48-risk-upper-frozen-v1.json',
           'contract.json': ROOT/'artifacts/cinema-max48-risk-upper-contract-v1.json',
           'run.json': stage/'run.json', 'summary.json': stage/'summary.json', 'independent-audit.json': audit_path}
    if sha(raw['frozen.json']) != run['frozen_sha256'] or sha(raw['contract.json']) != run['contract_sha256']:
        raise ValueError('冻结或有限合同身份已变')
    for name, path in raw.items(): shutil.copyfile(path, args.output/name)
    sources = set(run['source_sha256']) | {'scripts/archive_cinema_max48_risk_upper.py'}
    with zipfile.ZipFile(args.output/'source.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(sources): z.write(ROOT/name, name)
    evidence = {'screen.npz': stage/'screen.npz', 'danger-allowed.npz': stage/'danger-allowed.npz',
                'execution.log': ROOT/'artifacts/cinema-max48-risk-upper-execution-v1.log'}
    with zipfile.ZipFile(args.output/'support-evidence.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name, path in evidence.items(): z.write(path, name)
    reused = {}
    for field, folder in (('reused_max48_box_manifest', 'p16-cinema-max48-first-box-20261024'),
                          ('reused_quality_manifest', 'p16-cinema-max48-pareto-quality-20261024')):
        path = ROOT/'report/data'/folder/'manifest.json'; reused[field] = {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)}
    manifest = {'source_sha256': {name: sha(ROOT/name) for name in sorted(sources)},
        'support_member_sha256': {name: sha(path) for name, path in evidence.items()}, **reused,
        'files': {path.name: sha(path) for path in args.output.iterdir()},
        'scope': '固定741e55f的122首级节点±2完整80751正支撑、2102192个AABB状态；4985危险点/386612安全元组。若共享赋值满足cap47，则公共误差直方图被安全q上界43支配；未证明共享解存在，无CP/拟合/新模型/性能。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    for archive, field in (('source.zip', 'source_sha256'), ('support-evidence.zip', 'support_member_sha256')):
        with zipfile.ZipFile(args.output/archive) as z:
            for name, expected in manifest[field].items():
                if hashlib.sha256(z.read(name)).hexdigest() != expected: raise AssertionError('ZIP原字节SHA不符')
    print({'files': len(manifest['files']), 'sources': len(sources), 'evidence_members': len(evidence)}, flush=True)


if __name__ == '__main__': main()
