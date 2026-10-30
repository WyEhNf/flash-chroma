"""封存逐分量窄域的完整支撑与成本规模普查，不包含CP模型或求解。"""
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
    if args.output.exists(): raise ValueError('不覆盖窄域成本普查归档')
    stage = ROOT/'artifacts/cinema-first-narrow-cost-census-v1'; run = read(stage/'run.json')
    audit_path = ROOT/'artifacts/cinema-first-narrow-cost-independent-v1.json'; audit = read(audit_path)
    frozen_path = ROOT/'artifacts/cinema-first-narrow-cost-frozen-v1.json'; frozen = read(frozen_path)
    if not audit['pass'] or audit['summary_sha256'] != sha(stage/'summary.json') or audit['census_sha256'] != sha(stage/'census.npz'):
        raise ValueError('不是已独立审计的窄域普查')
    if run['cp_model_built'] or run['cp_solver_called']: raise ValueError('本阶段不应构造或执行CP')
    for sources in (run['source_sha256'], frozen['source_sha256']):
        for name, expected in sources.items():
            if sha(ROOT/name) != expected: raise ValueError('窄域实际执行或冻结源已变：'+name)
    args.output.mkdir(parents=True)
    copies = {'frozen.json': frozen_path, 'contract.json': ROOT/'artifacts/cinema-first-narrow-cost-contract-v1.json',
        'run.json': stage/'run.json', 'summary.json': stage/'summary.json', 'independent-audit.json': audit_path}
    for name, path in copies.items(): shutil.copyfile(path, args.output/name)
    sources = set(frozen['source_sha256']) | set(run['source_sha256']) | {'scripts/archive_cinema_first_narrow_cost.py'}
    with zipfile.ZipFile(args.output/'source.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(sources): z.write(ROOT/name, name)
    with zipfile.ZipFile(args.output/'support-evidence.zip', 'w', zipfile.ZIP_DEFLATED) as z: z.write(stage/'census.npz', 'census.npz')
    reused = {}
    for field, folder in (('reused_full_support_manifest', 'p16-cinema-first-hotspot-20261024'),
                          ('reused_witness_manifest', 'p16-cinema-first-safe-cpsat-20261024'),
                          ('reused_error_cost_manifest', 'p16-cinema-first-error-cost-census-20261024')):
        path = ROOT/'report/data'/folder/'manifest.json'
        reused[field] = {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)}
    manifest = {'source_sha256': {name: sha(ROOT/name) for name in sorted(sources)},
        'support_member_sha256': {'census.npz': sha(stage/'census.npz')}, **reused,
        'files': {path.name: sha(path) for path in args.output.iterdir()},
        'scope': '逐分量窄域完整47013正支撑/117010状态，10335保留点/51926安全行/21825选择器通过原三资源门；尚未构造CP或求解，不表示原八预算与cap存在联合可行节点。旧宽域超门和L1六预算失败保持。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    for archive, field in (('source.zip', 'source_sha256'), ('support-evidence.zip', 'support_member_sha256')):
        with zipfile.ZipFile(args.output/archive) as z:
            for name, expected in manifest[field].items():
                if hashlib.sha256(z.read(name)).hexdigest() != expected: raise AssertionError('ZIP成员SHA不符')
    print({'files': len(manifest['files']), 'sources': len(sources), 'evidence_members': 1}, flush=True)


if __name__ == '__main__': main()
