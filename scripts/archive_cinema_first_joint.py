"""归档首级一次八色扫描的完整负例、逐节点拒绝原因与独立重放。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with Path(path).open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖单次八色证据')
    study = ROOT/'artifacts/cinema-first-joint-v1'
    run = json.loads((study/'run.json').read_text(encoding='utf-8'))
    check_path = ROOT/'artifacts/cinema-first-joint-independent-v1.json'
    check = json.loads(check_path.read_text(encoding='utf-8'))
    assert check['pass'] and check['checked_nodes'] == 86 and check['checked_proposals'] == 4472
    for name, sha in run['sources_sha256'].items():
        if digest(ROOT/name) != sha: raise ValueError('执行源已变化：'+name)
    assert check['source_sha256'] == digest(ROOT/'scripts/audit_cinema_first_joint.py')
    args.output.mkdir(parents=True)
    copies = {name: study/name for name in ('run.json', 'summary.json', 'profile.json', 'colours.json', 'nodes.json')}
    copies.update({'contract.json': Path(run['contract']['path']), 'independent-check.json': check_path})
    for name, source in copies.items(): shutil.copyfile(source, args.output/name)
    evidence = {name: study/name for name in ('directions.json', 'final-state.npz')}
    with zipfile.ZipFile(args.output/'support-evidence.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name, source in evidence.items(): z.write(source, name)
    sources = set(run['sources_sha256']) | {'scripts/audit_cinema_first_joint.py', 'scripts/archive_cinema_first_joint.py'}
    with zipfile.ZipFile(args.output/'source.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(sources): z.write(ROOT/name, name)
    models = {p.name: digest(p) for p in (study/'candidate').iterdir()}
    with zipfile.ZipFile(args.output/'models.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(models): z.write(study/'candidate'/name, name)
    reused = ROOT/'report/data/p16-cinema-first-hotspot-20261024/manifest.json'
    manifest = {'source_sha256': {name: digest(ROOT/name) for name in sorted(sources)},
                'support_member_sha256': {name: digest(path) for name, path in evidence.items()},
                'model_member_sha256': models, 'reused_full_support_manifest': {'path': reused.relative_to(ROOT).as_posix(), 'sha256': digest(reused)},
                'files': {p.name: digest(p) for p in args.output.iterdir()},
                'scope': '一次8色4472提案，58节点修改、max50计数116到91、八预算通过；max仍50故不晋级，不加轮，无新native/百图/性能。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    for archive, field in (('source.zip', 'source_sha256'), ('support-evidence.zip', 'support_member_sha256'), ('models.zip', 'model_member_sha256')):
        with zipfile.ZipFile(args.output/archive) as z:
            for name, sha in manifest[field].items():
                if hashlib.sha256(z.read(name)).hexdigest() != sha: raise AssertionError('ZIP成员字节不一致')
    print(json.dumps({'files': len(manifest['files']), 'sources': len(sources), 'models': len(models), 'evidence_members': len(evidence)}, ensure_ascii=False), flush=True)


if __name__ == '__main__': main()
