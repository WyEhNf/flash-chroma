"""归档完整正支撑、4472项单节点负例与逐节点覆盖证书，保留冻结源和模型字节。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists(): raise ValueError('不覆盖首级单节点证据')
    study = ROOT/'artifacts/cinema-first-hotspot-v1'
    run = json.loads((study/'run.json').read_text(encoding='utf-8'))
    check_path = ROOT/'artifacts/cinema-first-hotspot-independent-v1.json'
    check = json.loads(check_path.read_text(encoding='utf-8'))
    assert check['pass'] and check['checked_directions'] == 4472
    assert check['minimum_hotspots_necessarily_unaffected_by_any_single_node'] == 84
    for name, sha in run['sources_sha256'].items():
        if digest(ROOT/name) != sha: raise ValueError('完整证书执行源已变：'+name)
    if check['source_sha256'] != digest(ROOT/'scripts/audit_cinema_first_hotspot.py'):
        raise ValueError('独立复核执行源已变')
    args.output.mkdir(parents=True)
    copies = {name: study/name for name in ('run.json', 'summary.json', 'profile-initial.json')}
    copies['contract.json'] = Path(run['contract']['path']); copies['independent-check.json'] = check_path
    for name, source in copies.items(): shutil.copyfile(source, args.output/name)
    evidence = {name: study/name for name in ('suffix.npy', 'support-index.npz', 'directions.json')}
    with zipfile.ZipFile(args.output/'support-evidence.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name, source in evidence.items(): z.write(source, name)
    source_names = set(run['sources_sha256']) | {'scripts/audit_cinema_first_hotspot.py', 'scripts/archive_cinema_first_hotspot.py'}
    with zipfile.ZipFile(args.output/'source.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(source_names): z.write(ROOT/name, name)
    model_names = ('first', 'first_slut', 'sidecar', 'stage2', 'stage3', 'stage4')
    models = {}
    with zipfile.ZipFile(args.output/'models.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name in model_names:
            spec = run['inputs'][name]; source = Path(spec['path']); member = name+'/'+source.name
            if digest(source) != spec['sha256']: raise ValueError('冻结模型字节已变')
            z.write(source, member); models[member] = spec['sha256']
    manifest = {'source_sha256': {name: digest(ROOT/name) for name in sorted(source_names)},
                'support_member_sha256': {name: digest(source) for name, source in evidence.items()},
                'model_member_sha256': models, 'files': {p.name: digest(p) for p in args.output.iterdir()},
                'scope': '完整新后缀/正支撑全部复核；52方向×86节点无max49候选；84个必然未触及热点是单节点几何边界，非多节点不可行证明。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    for archive, field in (('source.zip', 'source_sha256'), ('support-evidence.zip', 'support_member_sha256'), ('models.zip', 'model_member_sha256')):
        with zipfile.ZipFile(args.output/archive) as z:
            for name, sha in manifest[field].items():
                if hashlib.sha256(z.read(name)).hexdigest() != sha: raise AssertionError('ZIP成员原字节不一致')
    print(json.dumps({'files': len(manifest['files']), 'sources': len(source_names), 'models': len(models), 'support_members': len(evidence)}, ensure_ascii=False), flush=True)


if __name__ == '__main__': main()
