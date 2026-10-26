"""保留116点±2节点盒必要下界未发现障碍的完整原件和冻结源。"""
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
    if args.output.exists(): raise ValueError('不覆盖节点盒证据')
    certificate = ROOT/'artifacts/cinema-first-box-v1.json'
    value = json.loads(certificate.read_text(encoding='utf-8'))
    check_path = ROOT/'artifacts/cinema-first-box-independent-v1.json'
    check = json.loads(check_path.read_text(encoding='utf-8'))
    assert check['pass'] and check['certificate_sha256'] == digest(certificate)
    assert value['blocked_hotspots'] == 0 and value['total_suffix_queries'] == 8993
    assert all(r['relaxed_minimum_squared'] == 22 and r['gold_rgb'] == [0, 0, 0] for r in value['records'])
    for name, sha in value['source_sha256'].items():
        if digest(ROOT/name) != sha: raise ValueError('实际证书源已变：'+name)
    assert check['source_sha256'] == digest(ROOT/'scripts/audit_cinema_first_box.py')
    args.output.mkdir(parents=True)
    for name, source in (('frozen.json', ROOT/'artifacts/cinema-first-box-v1-frozen.json'),
                         ('contract.json', ROOT/'artifacts/cinema-first-box-contract-v1.json'), ('independent-check.json', check_path)):
        shutil.copyfile(source, args.output/name)
    sources = set(value['source_sha256']) | {'scripts/archive_cinema_first_box.py'}
    with zipfile.ZipFile(args.output/'source.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(sources): z.write(ROOT/name, name)
    with zipfile.ZipFile(args.output/'support-evidence.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(certificate, 'certificate.json')
    reused = ROOT/'report/data/p16-cinema-first-hotspot-20261024/manifest.json'
    manifest = {'source_sha256': {name: digest(ROOT/name) for name in sorted(sources)},
                'support_member_sha256': {'certificate.json': digest(certificate)},
                'reused_full_support_manifest': {'path': reused.relative_to(ROOT).as_posix(), 'sha256': digest(reused)},
                'files': {p.name: digest(p) for p in args.output.iterdir()},
                'scope': '116热点/86节点分量±2盒，8993后缀查询，放松下界全部22；没有不可行证书，也不代表整数及共享节点联合可行。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    for archive, field in (('source.zip', 'source_sha256'), ('support-evidence.zip', 'support_member_sha256')):
        with zipfile.ZipFile(args.output/archive) as z:
            for name, sha in manifest[field].items():
                if hashlib.sha256(z.read(name)).hexdigest() != sha: raise AssertionError('ZIP成员原件不一致')
    print(json.dumps({'files': len(manifest['files']), 'sources': len(sources), 'certificate_members': 1}, ensure_ascii=False), flush=True)


if __name__ == '__main__': main()
