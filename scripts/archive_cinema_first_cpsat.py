"""归档唯一CP热点可行、完整支撑失败；只存wheel锁/官方下载链接，不存venv。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True); args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖CP首轮证据')
    problem = read(ROOT/'artifacts/cinema-first-cpsat-problem-v1.json')
    audit_path = ROOT/'artifacts/cinema-first-cpsat-audit-v1.json'; audit = read(audit_path)
    assert audit['pass'] and not audit['full_support_accepted']
    for name, expected in problem['source_sha256'].items():
        if sha(ROOT/name) != expected: raise ValueError('冻结实际源已变：'+name)
    args.output.mkdir(parents=True)
    copies = {'environment-lock.json': ROOT/'artifacts/cinema-first-cpsat-environment-v1.json',
              'official-wheels.json': ROOT/'artifacts/cinema-first-cpsat-wheels-public-v1.json',
              'contract-input.json': ROOT/'artifacts/cinema-first-cpsat-contract-input-v2.json',
              'contract.json': ROOT/'artifacts/cinema-first-cpsat-contract-v2.json',
              'preflight.json': ROOT/'artifacts/cinema-first-cpsat-preflight-v1.json',
              'solution.json': ROOT/'artifacts/cinema-first-cpsat-solution-v1.json',
              'accept-summary.json': ROOT/'artifacts/cinema-first-cpsat-accept-v1/summary.json', 'independent-audit.json': audit_path}
    for name, source in copies.items(): shutil.copyfile(source, args.output/name)
    sources = set(problem['source_sha256']) | {'scripts/lock_cinema_cpsat_environment.py', 'scripts/cite_cinema_cpsat_wheels.py',
               'scripts/preflight_cinema_first_cpsat.py', 'scripts/audit_cinema_first_cpsat.py', 'scripts/archive_cinema_first_cpsat.py'}
    with zipfile.ZipFile(args.output/'source.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(sources): z.write(ROOT/name, name)
    evidence = {'problem.json': ROOT/'artifacts/cinema-first-cpsat-problem-v1.json',
                'actual-model.pb': ROOT/'artifacts/cinema-first-cpsat-solution-v1-model.pb',
                'preflight-model.pb': ROOT/'artifacts/cinema-first-cpsat-preflight-v1.pb'}
    evidence.update({p.name: p for p in (ROOT/'artifacts').glob('cinema-first-cpsat-contract-v2-*.pb')})
    with zipfile.ZipFile(args.output/'support-evidence.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name, source in evidence.items(): z.write(source, name)
    candidate = ROOT/'artifacts/cinema-first-cpsat-accept-v1/candidate'; models = {p.name: sha(p) for p in candidate.iterdir()}
    with zipfile.ZipFile(args.output/'models.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name in models: z.write(candidate/name, name)
    reused = ROOT/'report/data/p16-cinema-first-hotspot-20261024/manifest.json'
    manifest = {'source_sha256': {name: sha(ROOT/name) for name in sorted(sources)},
                'frozen_solve_source_sha256': problem['source_sha256'],
                'support_member_sha256': {name: sha(path) for name, path in evidence.items()}, 'model_member_sha256': models,
                'reused_full_support_manifest': {'path': reused.relative_to(ROOT).as_posix(), 'sha256': sha(reused)},
                'files': {p.name: sha(p) for p in args.output.iterdir()},
                'scope': '唯一CP无目标可行性0.613秒；116原热点max34，完整支撑max108、285点越cap及七项平均/尾部退化，严格拒绝；venv/wheels不入Git。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    for archive, field in (('source.zip', 'source_sha256'), ('support-evidence.zip', 'support_member_sha256'), ('models.zip', 'model_member_sha256')):
        with zipfile.ZipFile(args.output/archive) as z:
            for name, expected in manifest[field].items():
                if hashlib.sha256(z.read(name)).hexdigest() != expected: raise AssertionError('ZIP成员原字节不一致')
    print(json.dumps({'files': len(manifest['files']), 'sources': len(sources), 'evidence_members': len(evidence), 'models': len(models)}, ensure_ascii=False), flush=True)


if __name__ == '__main__': main()
