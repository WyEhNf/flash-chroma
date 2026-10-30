"""98 index/HEAD原字节核对；只按既有text规则归一属性和阶段正文。"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OWN = ['.gitattributes', 'docs/stages/2026-10-24-p16-first-structure.md',
    'experiments/p16-first-structure-v1.json', 'experiments/p16-node-tiling-census-v1.json',
    'scripts/census_p16_first_structure.py', 'scripts/census_p16_node_tiling.py',
    'scripts/audit_p16_structure_census.py', 'scripts/archive_p16_structure_census.py',
    'scripts/check_p16_structure_census_git.py']
TEXT = set(OWN[:2])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ref', choices=('HEAD', 'index'), required=True)
    p.add_argument('--receipt', required=True, type=Path)
    a = p.parse_args()
    if a.receipt.exists():
        raise FileExistsError('98 Git审计回执不覆盖')
    sha = lambda raw: hashlib.sha256(raw).hexdigest()
    data = ROOT/'report/data/p16-first-structure-v1'
    identity = json.loads((data/'identity.json').read_text(encoding='utf-8'))
    own = OWN + [f.relative_to(ROOT).as_posix() for f in sorted(data.rglob('*')) if f.is_file()]
    assert len(own) == len(set(own))
    expected = {}
    for path in own:
        raw = (ROOT/path).read_bytes()
        expected[path] = sha(raw.replace(b'\r\n', b'\n') if path in TEXT else raw)
    for row in identity['plain_files']:
        assert sha((data/row['member']).read_bytes()) == row['sha256']
    for row in identity['execution_dependencies']:
        value = row['execution_sha256'] if row['path'] in own else row['parent_git_blob_sha256']
        assert value is not None
        assert row['path'] not in expected or expected[row['path']] == value
        expected[row['path']] = value
    prefix = ':' if a.ref == 'index' else 'HEAD:'
    out = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT,
        input=''.join(prefix+path+'\n' for path in expected).encode(), capture_output=True, check=True).stdout
    pos = 0
    for path, wanted in expected.items():
        end = out.index(b'\n', pos); fields = out[pos:end].split()
        assert len(fields) == 3 and fields[1] == b'blob', path
        size = int(fields[2]);assert sha(out[end+1:end+1+size]) == wanted, path
        pos = end+size+2
    assert pos == len(out)
    if a.ref == 'index':
        staged = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '-z'], cwd=ROOT).decode().split('\0')
        assert set(staged)-{''} <= set(own), staged
    receipt = {'ref': a.ref, 'all_sha256_passed': True, 'explicit_stage_whitelist_paths': len(own),
        'source_and_evidence_blobs': len(expected), 'plain_exact_files': len(identity['plain_files']),
        'text_normalization_only': sorted(TEXT), 'checker_sha256': sha(Path(__file__).read_bytes()),
        'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'expected': expected}
    a.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k != 'expected'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
