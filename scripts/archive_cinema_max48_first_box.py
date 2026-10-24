"""封存当前145热点必要盒证书及完整查询，不含新模型或CP。"""
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
    if args.output.exists(): raise ValueError('不覆盖当前145必要盒证书归档')
    stage = ROOT/'artifacts/cinema-max48-first-box-v1'; run = read(stage/'results.json')
    audit_path = ROOT/'artifacts/cinema-max48-first-box-independent-v1.json'; audit = read(audit_path)
    if not audit['pass'] or audit['results_sha256'] != sha(stage/'results.json') or audit['replay_sha256'] != sha(stage/'replay.npz'):
        raise ValueError('不是已认证当前145必要证书')
    for name, expected in run['source_sha256'].items():
        if sha(ROOT/name) != expected: raise ValueError('当前热点源已变')
    args.output.mkdir(parents=True)
    for name, path in {'frozen.json': ROOT/'artifacts/cinema-max48-first-box-frozen-v1.json',
        'results.json': stage/'results.json', 'independent-audit.json': audit_path}.items(): shutil.copyfile(path, args.output/name)
    sources = set(run['source_sha256']) | {'scripts/archive_cinema_max48_first_box.py'}
    with zipfile.ZipFile(args.output/'source.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(sources): z.write(ROOT/name, name)
    evidence = {'replay.npz': stage/'replay.npz', 'execution.log': ROOT/'artifacts/cinema-max48-first-box-execution-v1.log'}
    with zipfile.ZipFile(args.output/'support-evidence.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name, path in evidence.items(): z.write(path, name)
    reused = {}
    for field, folder in (('reused_box_contract_manifest', 'p16-cinema-first-box-20261024'),
                          ('reused_quality_manifest', 'p16-cinema-max48-pareto-quality-20261024')):
        path = ROOT/'report/data'/folder/'manifest.json'; reused[field] = {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)}
    manifest = {'source_sha256': {name: sha(ROOT/name) for name in sorted(sources)},
        'support_member_sha256': {name: sha(path) for name, path in evidence.items()}, **reused,
        'files': {path.name: sha(path) for path in args.output.iterdir()},
        'scope': '145当前max48输入、122首级物理节点±2盒完整17565状态，全部单点未阻断目标≤47，未证明共享赋值存在。无新模型/CP/拟合/照片选择/性能，完整流和源SHA固定。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    for archive, field in (('source.zip', 'source_sha256'), ('support-evidence.zip', 'support_member_sha256')):
        with zipfile.ZipFile(args.output/archive) as z:
            for name, expected in manifest[field].items():
                if hashlib.sha256(z.read(name)).hexdigest() != expected: raise AssertionError('ZIP原字节SHA不符')
    print({'files': len(manifest['files']), 'sources': len(sources), 'evidence_members': len(evidence)}, flush=True)


if __name__ == '__main__': main()
