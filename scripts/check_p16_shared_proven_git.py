"""97 Git index/HEAD独立原字节核对；只有属性和阶段正文按原text规则归一LF。"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ref', choices=('HEAD', 'index'), required=True)
    p.add_argument('--receipt', type=Path, required=True)
    a = p.parse_args()
    if a.receipt.exists():
        raise FileExistsError('97 Git审计回执不覆盖')
    digest = lambda raw: hashlib.sha256(raw).hexdigest()
    data = ROOT / 'report/data/p16-shared-proven-v1'
    identity = json.loads((data / 'identity.json').read_text(encoding='utf-8'))
    own = ['.gitattributes', 'docs/stages/2026-10-24-p16-shared-proven.md']
    for path in sorted((ROOT / 'experiments').glob('p16-shared-proven*')):
        own += [f.relative_to(ROOT).as_posix() for f in sorted(path.rglob('*')) if f.is_file()] if path.is_dir() else [path.relative_to(ROOT).as_posix()]
    own += [f.relative_to(ROOT).as_posix() for f in sorted((ROOT / 'scripts').glob('*p16_shared_proven*.py'))]
    own += [f.relative_to(ROOT).as_posix() for f in sorted(data.iterdir()) if f.is_file()]
    assert len(own) == len(set(own))
    text_paths = {'.gitattributes', 'docs/stages/2026-10-24-p16-shared-proven.md'}
    expected = {}
    for path in own:
        raw = (ROOT / path).read_bytes()
        expected[path] = digest(raw.replace(b'\r\n', b'\n') if path in text_paths else raw)
    for row in identity['execution_dependencies']:
        value = row['execution_sha256'] if row['path'] in own else row['parent_git_blob_sha256']
        if value is not None:
            assert row['path'] not in expected or expected[row['path']] == value, row['path']
            expected[row['path']] = value
    prefix = ':' if a.ref == 'index' else 'HEAD:'
    output = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT,
        input=''.join(prefix + path + '\n' for path in expected).encode('utf-8'), capture_output=True, check=True).stdout
    position = 0
    for path, wanted in expected.items():
        end = output.index(b'\n', position);fields = output[position:end].split()
        assert len(fields) == 3 and fields[1] == b'blob', path
        size = int(fields[2]);assert digest(output[end + 1:end + 1 + size]) == wanted, path
        position = end + size + 2
    assert position == len(output)
    if a.ref == 'index':
        staged = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '-z'], cwd=ROOT).decode('utf-8').split('\0')
        assert set(staged) - {''} <= set(own), staged
    receipt = {'ref': a.ref, 'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'all_sha256_passed': True, 'explicit_stage_whitelist_paths': len(own), 'source_and_evidence_blobs': len(expected),
        'text_normalization_only': sorted(text_paths), 'all_execution_sources_raw_zips_are_exact_bytes': True,
        'checker_sha256': digest(Path(__file__).read_bytes()), 'expected': expected}
    a.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in receipt.items() if key != 'expected'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
