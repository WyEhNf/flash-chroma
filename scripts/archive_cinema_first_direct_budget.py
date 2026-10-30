"""封存直接预算CP的V1路径失败、V2无解状态与独立编码审计。"""
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
    if args.output.exists(): raise ValueError('不覆盖直接预算CP阶段归档')
    base = ROOT/'artifacts'; audit_path = base/'cinema-first-direct-budget-independent-v2.json'; audit = read(audit_path)
    problem_path = base/'cinema-first-direct-budget-problem-v2.json'; problem = read(problem_path)
    solution_path = base/'cinema-first-direct-budget-solution-v2.json'; solution = read(solution_path)
    if not audit['pass'] or audit['problem_sha256'] != sha(problem_path) or audit['solution_sha256'] != sha(solution_path):
        raise ValueError('不是已独立审计的直接预算原件')
    if solution['status'] != 'INFEASIBLE' or solution['feasible']: raise ValueError('本归档必须保留实际无incumbent状态')
    for name, expected in problem['source_sha256'].items():
        if sha(ROOT/name) != expected: raise ValueError('真实直接预算源已变：'+name)
    for revision in (1, 2):
        frozen = read(base/('cinema-first-direct-budget-frozen-v'+str(revision)+'.json'))
        for name, expected in frozen['source_sha256'].items():
            if sha(ROOT/name) != expected: raise ValueError('V1/V2源没有保留原字节：'+name)
    args.output.mkdir(parents=True)
    copies = {name: base/('cinema-first-direct-budget-'+name) for name in
        ('frozen-v1.json', 'frozen-v2.json', 'contract-v1.json', 'contract-v2.json', 'preflight-v2.json', 'solution-v2.json')}
    copies['independent-audit-v2.json'] = audit_path
    for name, path in copies.items(): shutil.copyfile(path, args.output/name)
    sources = set(problem['source_sha256']) | {'scripts/audit_cinema_first_direct_budget.py', 'scripts/archive_cinema_first_direct_budget.py'}
    with zipfile.ZipFile(args.output/'source.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(sources): z.write(ROOT/name, name)
    evidence = {name: base/('cinema-first-direct-budget-'+name) for name in
        ('contract-input-v1.json', 'contract-input-v2.json', 'problem-v2.json', 'preflight-v2.pb',
         'preflight-execution-v1.log', 'preflight-execution-v2.log', 'solve-execution-v2.log')}
    evidence['environment-lock.json'] = base/'cinema-first-cpsat-environment-v1.json'
    with zipfile.ZipFile(args.output/'support-evidence.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name, path in sorted(evidence.items()): z.write(path, name)
    reused = {}
    for field, folder in (('reused_narrow_census_manifest', 'p16-cinema-first-narrow-cost-census-20261024'),
                          ('reused_environment_manifest', 'p16-cinema-first-cpsat-20261024'),
                          ('reused_witness_manifest', 'p16-cinema-first-safe-cpsat-20261024')):
        path = ROOT/'report/data'/folder/'manifest.json'; reused[field] = {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)}
    manifest = {'source_sha256': {name: sha(ROOT/name) for name in sorted(sources)},
        'support_member_sha256': {name: sha(path) for name, path in sorted(evidence.items())}, **reused,
        'files': {path.name: sha(path) for path in args.output.iterdir()},
        'solver_model_pb_sha256': solution['model_proto_sha256'], 'solver_model_equal_preflight_pb': True,
        'scope': '仅此逐分量窄域+原max_first八预算保守ceil编码的单次solver报告INFEASIBLE；无独立形式不可行证明，宽域与其他模型未排除。V1路径失败保留，V2不改数学。独立固定外域证实该95分量子空间max²下界48、p99下界3/sqrt12，无新候选。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    for archive, field in (('source.zip', 'source_sha256'), ('support-evidence.zip', 'support_member_sha256')):
        with zipfile.ZipFile(args.output/archive) as z:
            for name, expected in manifest[field].items():
                if hashlib.sha256(z.read(name)).hexdigest() != expected: raise AssertionError('ZIP原件SHA不符')
    print({'files': len(manifest['files']), 'sources': len(sources), 'evidence_members': len(evidence)}, flush=True)


if __name__ == '__main__': main()
