"""封存存储核可移植性的新执行与失败夹具证据，不重跑数值。"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    output = ROOT / 'report/data/p16-memory-store-portability-v1'
    output.mkdir(parents=True, exist_ok=True)
    if (output / 'evidence.zip').exists() or (output / 'manifest.json').exists():
        raise FileExistsError('证据归档已存在，拒绝覆盖')
    raw = []
    for name in ['p16-memory-store-portability-v1', 'p16-memory-store-portability-v2']:
        for path in sorted((ROOT / 'artifacts' / name).rglob('*')):
            if path.is_file():
                raw.append((path, 'artifacts/' + name + '/' + str(path.relative_to(ROOT / 'artifacts' / name)).replace('\\', '/')))
    run = json.loads((ROOT / 'artifacts/p16-memory-store-portability-v2/run.json').read_text(encoding='utf-8'))
    for name, expected in run['source_sha256'].items():
        path = ROOT / name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
        raw.append((path, 'source/' + name.replace('\\', '/')))
    raw.append((Path(__file__), 'source/' + str(Path(__file__).relative_to(ROOT)).replace('\\', '/')))
    manifest = []
    archive = output / 'evidence.zip'
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as packed:
        for path, name in raw:
            data = path.read_bytes()
            packed.writestr(name, data)
            manifest.append(dict(name=name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
    with zipfile.ZipFile(archive) as packed:
        assert packed.testzip() is None
        for item in manifest:
            data = packed.read(item['name'])
            assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']
    (output / 'manifest.json').write_text(json.dumps(dict(archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
        members=manifest), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{len(manifest)}份原始证据SHA与ZIP CRC通过')


if __name__ == '__main__':
    main()
