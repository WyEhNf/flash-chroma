"""封存照片工作台/赛前集成的原始回执，或只读核对归档；不重跑性能实验。"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'report/data/p16-studio-event-20261029'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def verify():
    manifest = read(DEST / 'manifest.json')
    archive = DEST / manifest['archive']
    assert sha(archive.read_bytes()) == manifest['archive_sha256'], '归档ZIP摘要不符'
    with zipfile.ZipFile(archive) as zipped:
        assert set(zipped.namelist()) == set(manifest['members']), '归档成员集合不符'
        assert len(zipped.namelist()) == len(manifest['members']), '归档成员重复'
        for name, value in manifest['members'].items():
            payload = zipped.read(name)
            assert len(payload) == value['bytes'] and sha(payload) == value['sha256'], name
    for name, value in manifest['receipts'].items():
        payload = (DEST / name).read_bytes()
        assert len(payload) == value['bytes'] and sha(payload) == value['sha256'], name
    return {'passed': True, 'members': len(manifest['members']),
            'archive_sha256': manifest['archive_sha256'],
            'scope': '逐字节核对归档与顶层回执；不重跑图像、拟合或性能，不提升原证据资格。'}


def collect(package_receipt):
    if DEST.exists():
        raise FileExistsError('证据目录已存在，拒绝覆盖；使用--verify核对')
    package_receipt = Path(package_receipt).resolve()
    packet = read(package_receipt)
    assert packet['passed'] and Path(packet['archive']).is_file()
    assert sha(Path(packet['archive']).read_bytes()) == packet['archive_sha256']
    sources = [ROOT / name for name in (
        'gui/server.py', 'gui/studio.py', 'gui/studio_catalog.json', 'gui/studio_smoke_test.py',
        'gui/static/studio.html', 'gui/static/studio.css', 'gui/static/studio.js',
        'start-gui.ps1', 'start-event.ps1', 'scripts/p16_event.py',
        'scripts/package_p16_event.py', 'scripts/prepare_studio_catalog.py',
        'scripts/archive_studio_event.py', 'single_header/event_run.cpp', 'single_header/CMakeLists.txt',
        'tests/test_studio.py', 'tests/test_p16_event.py', 'tests/test_p16_event_package.py',
        'docs/event-quickstart.md', 'gui/README.md', 'include/flash_chroma.hpp', 'include/flash_chroma_c.h')]
    evidence = [ROOT / 'artifacts' / name for name in (
        'studio-http-smoke-20261029.json', 'studio-backend-real-presets.json',
        'studio-backend-tests.log', 'studio-backend-tests-final.log', 'studio-event-final-tests.log',
        'studio-launcher-verification-20261029.json', 'studio-catalog-final-check.log',
        'studio-frontend-final-check.json', 'event-cli-tests.log', 'event-cli-count-tests.log',
        'event-package-tests-20261029.log',
        'event-package-verification-20261029.json', 'event-package-launcher-20261029.json',
        'event-package-launcher-20261029-v2.json', 'studio_frontend_check.cjs',
        'event_cpp_smoke.py', 'event-cpp-build/build.log', 'event-cpp-build/compile_commands.json',
        'single-header-perf-build/libflash_chroma_bridge.dll.build.json')]
    for directory in ('event-cli-20261029', 'event-cpp-smoke-20261029', 'event-wrapper-smoke-20261029'):
        evidence.extend(p for p in (ROOT / 'artifacts' / directory).rglob('*')
                        if p.is_file() and p.suffix in ('.json', '.jsonl', '.log'))
    packet_root = Path(packet['directory'])
    evidence.extend(packet_root / name for name in ('MANIFEST.json', 'DEPENDENCIES.json', 'LOCAL-RUNTIME.json',
                                                   'README-LOCAL.md', 'start-local.ps1'))
    evidence.extend(p for p in (packet_root / 'SELF-CHECK').rglob('*')
                    if p.is_file() and p.suffix in ('.json', '.jsonl', '.log'))
    for path in sources + evidence:
        if not path.is_file():
            raise FileNotFoundError(path)
    DEST.mkdir(parents=True)
    receipts = {}
    for name, source in (
        ('package-receipt.json', package_receipt),
        ('http-verification.json', ROOT / 'artifacts/studio-http-smoke-20261029.json'),
        ('event-verification.json', ROOT / 'artifacts/event-cli-20261029/verification.json'),
        ('cpp-verification.json', ROOT / 'artifacts/event-cpp-smoke-20261029/results.json'),
        ('package-self-check.json', Path(packet['directory']) / 'SELF-CHECK/verification.json'),
        ('frontend-verification.json', ROOT / 'artifacts/studio-frontend-final-check.json')):
        payload = source.read_bytes()
        (DEST / name).write_bytes(payload)
        receipts[name] = {'bytes': len(payload), 'sha256': sha(payload)}
    members = {}
    archive = DEST / 'raw-evidence-and-source.zip'
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as zipped:
        for prefix, paths in (('source', sources), ('raw', evidence)):
            for path in sorted(set(paths)):
                payload = path.read_bytes()
                name = prefix + '/' + path.relative_to(ROOT).as_posix()
                zipped.writestr(name, payload)
                members[name] = {'bytes': len(payload), 'sha256': sha(payload)}
    manifest = {'schema': 'studio_event_evidence_v1', 'base_commit': 'fb7e195215f14df9f635394d75cde0e0e69c82c9',
                'archive': archive.name, 'archive_sha256': sha(archive.read_bytes()),
                'members': members, 'receipts': receipts,
                'scope': '原始文件字节与最终源码快照；早期回执保留其原源码身份，最终计数门禁另由55项契约测试覆盖。'
                         '未纳入大照片/模型包或把本机功能计时升级为受控性能证据。'}
    (DEST / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    return verify()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--package-receipt', type=Path)
    args = parser.parse_args()
    if not args.verify and not args.package_receipt:
        parser.error('首次归档必须指定--package-receipt')
    print(json.dumps(verify() if args.verify else collect(args.package_receipt), ensure_ascii=False, indent=2))
