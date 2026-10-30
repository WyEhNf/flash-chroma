"""封存既有离线344色/9位证据，不生成模型、不执行native或性能。"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'artifacts/p16-direct-active-packed-v2'
OUT = ROOT / 'report/data/p16-direct-active-packed-20261024'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    frozen = read(RAW / 'frozen.json')
    result = read(RAW / 'results.json')
    independent = read(RAW / 'independent.json')
    assert sha((RAW / 'frozen.json').read_bytes()) == 'ba77cb94813346b1906f696c30637933be7b62d738221331d725af34142268d4'
    assert sha((RAW / 'results.json').read_bytes()) == '728165235480fb336ef39ec4ce6ffb801c33d59a3c19676c62aa063ba249dc7e'
    assert result['passed'] and independent['passed']
    assert result['native_prepare_calls'] == 1 and result['native_apply_calls'] == result['performance_samples'] == 0
    assert result['logical_entries'] == independent['independently_decoded_entries'] == 16777216
    assert result['whole_cache_colors'] == 613 and result['active_colors'] == independent['active_colors'] == 344
    assert result['packed_bits'] == independent['bits'] == 9 and independent['packed_and_palette_bytes'] == 18875748
    assert independent['frozen_sha256'] == sha((RAW / 'frozen.json').read_bytes())
    assert independent['results_sha256'] == sha((RAW / 'results.json').read_bytes())
    assert independent['script_sha256'] == sha((ROOT / 'scripts/audit_direct_active_packed.py').read_bytes())
    for name, expected in result['artifacts'].items():
        raw = (RAW / name).read_bytes()
        assert len(raw) == expected['bytes'] and sha(raw) == expected['sha256'], name
    source_map = frozen['sources_sha256'] if 'sources_sha256' in frozen else frozen['source_sha256']
    for name, expected in source_map.items():
        assert sha((ROOT / name).read_bytes()) == expected, name
    extra = [
        'experiments/p16-direct-active-packed-plan-v1.md',
        'experiments/p16-direct-active-packed-mechanical-v2.md',
        'scripts/census_direct_active_packed.py',
        'scripts/census_direct_active_packed_v2.py',
        'scripts/prepare_direct_active_packed_v2.py',
        'scripts/audit_direct_active_packed.py',
        'scripts/archive_p16_direct_active_packed.py',
        'scripts/audit_p16_direct_active_packed_git.py',
        'docs/stages/2026-10-24-p16-direct-active-packed.md',
    ]
    sources = sorted(set(source_map) | set(extra))
    raw_paths = sorted(p for p in RAW.rglob('*') if p.is_file())
    raw_paths.append(ROOT / 'artifacts/p16-direct-active-packed-v1-freeze-stop.json')
    OUT.mkdir(parents=True, exist_ok=False)
    archives = {}
    for filename, paths in [('sources.zip', [ROOT / name for name in sources]), ('raw.zip', raw_paths)]:
        index = {}
        with zipfile.ZipFile(OUT / filename, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for path in paths:
                name = path.relative_to(ROOT).as_posix()
                assert name not in index
                raw = path.read_bytes()
                archive.writestr(name, raw)
                index[name] = dict(bytes=len(raw), sha256=sha(raw))
        with zipfile.ZipFile(OUT / filename) as archive:
            assert archive.testzip() is None and set(archive.namelist()) == set(index)
            assert len(archive.namelist()) == len(index)
            for name, expected in index.items():
                raw = archive.read(name)
                assert len(raw) == expected['bytes'] and sha(raw) == expected['sha256']
        archives[filename] = dict(sha256=sha((OUT / filename).read_bytes()), members=index)
    for name in ('frozen.json', 'results.json', 'independent.json'):
        shutil.copyfile(RAW / name, OUT / name)
    save(OUT / 'manifest.json', dict(purpose=__doc__, zip_files=archives,
        frozen_sources=len(source_map), archived_sources=len(sources), raw_files=len(raw_paths),
        native_apply_calls=0, native_prepare_calls_in_original_census=1, performance_samples=0,
        scope='344色/9位仅离线可表示性；旧10位有效低50拒绝保持；没有新native收益。'))
    publish_sources = [ROOT / name for name in extra]
    files = publish_sources + sorted(OUT.iterdir())
    whitelist = {p.relative_to(ROOT).as_posix(): dict(bytes=p.stat().st_size, sha256=sha(p.read_bytes())) for p in files}
    save(OUT / 'git-whitelist.json', dict(files=whitelist,
        scope='白名单自身另行stage；旧源仅留于ZIP，无AGENTS/其它方案/正式perf稿。'))
    print(json.dumps(dict(files_excluding_whitelist=len(whitelist),
        source_members=len(sources), raw_members=len(raw_paths), passed=True), ensure_ascii=False))


if __name__ == '__main__':
    main()
