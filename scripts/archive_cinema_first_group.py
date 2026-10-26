"""归档52项整组探针全部严格49失败及所有完整直方图、拒绝理由。"""
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
    if args.output.exists(): raise ValueError('不覆盖整组探针原件')
    study = ROOT/'artifacts/cinema-first-group-v1'
    run = json.loads((study/'run.json').read_text(encoding='utf-8'))
    summary = json.loads((study/'summary.json').read_text(encoding='utf-8'))
    check_path = ROOT/'artifacts/cinema-first-group-independent-v1.json'
    check = json.loads(check_path.read_text(encoding='utf-8'))
    assert check['pass'] and check['checked_proposals'] == 52 and summary['winner'] is None
    assert check['independent_eight_corner_u64_total_rows'] == 3669692 and not summary['eligible_for_independent_final_checks']
    for name, sha in run['source_sha256'].items():
        if digest(ROOT/name) != sha: raise ValueError('执行源已变：'+name)
    assert check['source_sha256'] == digest(ROOT/'scripts/audit_cinema_first_group.py')
    args.output.mkdir(parents=True)
    for name, source in (('run.json', study/'run.json'), ('summary.json', study/'summary.json'),
        ('contract.json', ROOT/'artifacts/cinema-first-group-contract-v1.json'), ('independent-check.json', check_path)):
        shutil.copyfile(source, args.output/name)
    sources = set(run['source_sha256']) | {'scripts/archive_cinema_first_group.py'}
    with zipfile.ZipFile(args.output/'source.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(sources): z.write(ROOT/name, name)
    with zipfile.ZipFile(args.output/'support-evidence.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(study/'directions.json', 'directions.json')
    reused = ROOT/'report/data/p16-cinema-first-hotspot-20261024/manifest.json'
    manifest = {'source_sha256': {name: digest(ROOT/name) for name in sorted(sources)},
                'support_member_sha256': {'directions.json': digest(study/'directions.json')},
                'reused_full_support_manifest': {'path': reused.relative_to(ROOT).as_posix(), 'sha256': digest(reused)},
                'files': {p.name: digest(p) for p in args.output.iterdir()},
                'scope': '52项整组共同移动全部无strict max49，全部fresh及独立八角u64验证；保留截断、cap/八预算/完整直方图代价；不追加轮、不升级。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    for archive, field in (('source.zip', 'source_sha256'), ('support-evidence.zip', 'support_member_sha256')):
        with zipfile.ZipFile(args.output/archive) as z:
            for name, sha in manifest[field].items():
                if hashlib.sha256(z.read(name)).hexdigest() != sha: raise AssertionError('ZIP原件字节不同')
    print(json.dumps({'files': len(manifest['files']), 'sources': len(sources), 'raw_proposals': 52}, ensure_ascii=False), flush=True)


if __name__ == '__main__': main()
