"""封存max48三分母独立质量资格、真实四模型和旧局部失败边界。"""
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
    if args.output.exists(): raise ValueError('不覆盖三分母资格归档')
    stage = ROOT/'artifacts/cinema-max48-pareto-quality-v1'; identity = read(stage/'identity.json')
    audit_path = ROOT/'artifacts/cinema-max48-pareto-quality-audit-v1.json'; audit = read(audit_path)
    if not audit['pass'] or audit['results_sha256'] != sha(stage/'results.json'): raise ValueError('不是已审计的独立质量原件')
    for name, expected in identity['source_sha256'].items():
        if sha(ROOT/name) != expected: raise ValueError('实际执行源字节已变：'+name)
    args.output.mkdir(parents=True)
    copies = {'frozen.json': ROOT/'artifacts/cinema-max48-pareto-quality-frozen-v1.json',
        'identity.json': stage/'identity.json', 'results.json': stage/'results.json', 'independent-audit.json': audit_path}
    for name, path in copies.items(): shutil.copyfile(path, args.output/name)
    sources = set(identity['source_sha256']) | {'scripts/audit_cinema_max48_quality.py', 'scripts/archive_cinema_max48_quality.py'}
    with zipfile.ZipFile(args.output/'source.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(sources): z.write(ROOT/name, name)
    models = {}
    for role, spec in identity['roles'].items():
        for i, path in enumerate(spec['models']): models[role+'/stage'+str(i+1)+'.slut'] = Path(path)
        for i, path in enumerate(spec['sidecars']):
            if path: models[role+'/stage'+str(i+1)+'-sidecar.bin'] = Path(path)
    models['candidate/model.npz'] = ROOT/'artifacts/cinema-first-safe-cpsat-accept-v2/candidate/model.npz'
    with zipfile.ZipFile(args.output/'models.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name, path in sorted(models.items()): z.write(path, name)
    with zipfile.ZipFile(args.output/'support-evidence.zip', 'w', zipfile.ZIP_DEFLATED) as z: z.write(stage/'histograms.npz', 'histograms.npz')
    witness = ROOT/'report/data/p16-cinema-first-safe-cpsat-20261024/manifest.json'
    manifest = {'source_sha256': {name: sha(ROOT/name) for name in sorted(sources)},
        'support_member_sha256': {'histograms.npz': sha(stage/'histograms.npz')},
        'model_member_sha256': {name: sha(path) for name, path in sorted(models.items())},
        'reused_witness_manifest': {'path': witness.relative_to(ROOT).as_posix(), 'sha256': sha(witness)},
        'full_candidate_stream_sha256': sha(stage/'candidate.rgb'), 'files': {path.name: sha(path) for path in args.output.iterdir()},
        'scope': '三分母完整域24配置/四模型400逐图通过，公共基线mean达标；旧六预算失败和首级独立忠实度代价保留。速度50%未证，不切默认；完整流留artifacts不放Git。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    for archive, field in (('source.zip', 'source_sha256'), ('support-evidence.zip', 'support_member_sha256'), ('models.zip', 'model_member_sha256')):
        with zipfile.ZipFile(args.output/archive) as z:
            for name, expected in manifest[field].items():
                if hashlib.sha256(z.read(name)).hexdigest() != expected: raise AssertionError('ZIP成员实际SHA不符')
    print({'raw_files': len(manifest['files']), 'source_members': len(sources), 'model_members': len(models), 'evidence_members': 1}, flush=True)


if __name__ == '__main__': main()
