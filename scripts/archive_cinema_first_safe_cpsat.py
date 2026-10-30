"""封存完整危险表minL1单轮与六预算失败，保留两版预检的实际字节。"""
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
    if args.output.exists(): raise ValueError('不覆盖完整危险表minL1归档')
    artifacts = ROOT/'artifacts'; problem = read(artifacts/'cinema-first-safe-cpsat-problem-v2.json')
    first = read(artifacts/'cinema-first-safe-cpsat-problem-v1.json')
    audit_path = artifacts/'cinema-first-safe-cpsat-audit-v2.json'; audit = read(audit_path)
    if not audit['pass'] or audit['full_support_accepted']: raise ValueError('不是已审计的minL1失败阶段')
    for name, expected in {**first['source_sha256'], **problem['source_sha256']}.items():
        if sha(ROOT/name) != expected: raise ValueError('任一版实际源已变：'+name)
    args.output.mkdir(parents=True)
    copies = {'environment-lock.json': artifacts/'cinema-first-cpsat-environment-v1.json',
        'official-wheels.json': artifacts/'cinema-first-cpsat-wheels-public-v1.json',
        'contract-v1.json': artifacts/'cinema-first-safe-cpsat-contract-v1.json',
        'contract-v2.json': artifacts/'cinema-first-safe-cpsat-contract-v2.json',
        'preflight-v1.json': artifacts/'cinema-first-safe-cpsat-preflight-v1.json',
        'preflight-v2.json': artifacts/'cinema-first-safe-cpsat-preflight-v2.json',
        'solution-v2.json': artifacts/'cinema-first-safe-cpsat-solution-v2.json',
        'accept-summary.json': artifacts/'cinema-first-safe-cpsat-accept-v2/summary.json', 'independent-audit.json': audit_path}
    for name, path in copies.items(): shutil.copyfile(path, args.output/name)
    sources = set(first['source_sha256']) | set(problem['source_sha256']) | {
        'scripts/audit_cinema_first_safe_cpsat.py', 'scripts/archive_cinema_first_safe_cpsat.py'}
    with zipfile.ZipFile(args.output/'source.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(sources): z.write(ROOT/name, name)
    evidence = {'problem-v1.json': artifacts/'cinema-first-safe-cpsat-problem-v1.json',
        'problem-v2.json': artifacts/'cinema-first-safe-cpsat-problem-v2.json',
        'preflight-model-v1.pb': artifacts/'cinema-first-safe-cpsat-preflight-v1.pb',
        'preflight-model-v2.pb': artifacts/'cinema-first-safe-cpsat-preflight-v2.pb',
        'actual-model-v2.pb': artifacts/'cinema-first-safe-cpsat-solution-v2-model.pb',
        'replay.npz': artifacts/'cinema-first-safe-cpsat-accept-v2/replay.npz'}
    for version in (1, 2):
        evidence.update({path.name: path for path in artifacts.glob('cinema-first-safe-cpsat-contract-v'+str(version)+'-*.pb')})
    with zipfile.ZipFile(args.output/'support-evidence.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name, path in evidence.items(): z.write(path, name)
    candidate = artifacts/'cinema-first-safe-cpsat-accept-v2/candidate'; models = {path.name: sha(path) for path in candidate.iterdir()}
    with zipfile.ZipFile(args.output/'models.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(models): z.write(candidate/name, name)
    reused = ROOT/'report/data/p16-cinema-first-hotspot-20261024/manifest.json'
    risk = ROOT/'report/data/p16-cinema-first-risk-20261024/manifest.json'
    manifest = {'source_sha256': {name: sha(ROOT/name) for name in sorted(sources)},
        'frozen_solve_source_sha256': problem['source_sha256'], 'frozen_preflight_v1_source_sha256': first['source_sha256'],
        'support_member_sha256': {name: sha(path) for name, path in evidence.items()}, 'model_member_sha256': models,
        'reused_full_support_manifest': {'path': reused.relative_to(ROOT).as_posix(), 'sha256': sha(reused)},
        'reused_risk_manifest': {'path': risk.relative_to(ROOT).as_posix(), 'sha256': sha(risk)},
        'files': {path.name: sha(path) for path in args.output.iterdir()},
        'scope': '唯一20秒minL1得FEASIBLE，max²50→48且无cap违例；六项原平均/尾部预算上升严格拒绝，保留v1/v2源和预检，不补跑。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    for archive, field in (('source.zip', 'source_sha256'), ('support-evidence.zip', 'support_member_sha256'), ('models.zip', 'model_member_sha256')):
        with zipfile.ZipFile(args.output/archive) as z:
            for name, expected in manifest[field].items():
                if hashlib.sha256(z.read(name)).hexdigest() != expected: raise AssertionError('ZIP成员原字节不符')
    print({'raw_files': len(manifest['files']), 'source_members': len(sources), 'evidence_members': len(evidence), 'model_members': len(models)}, flush=True)


if __name__ == '__main__': main()
