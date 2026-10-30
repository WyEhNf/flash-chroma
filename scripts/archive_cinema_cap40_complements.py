"""只封存已完成补集账单及原字节，不运行数值、CP或native。"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'artifacts/cinema-cap40-complement-census-v1'
DEST=ROOT/'report/data/p16-cinema-cap40-complements-20261024'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    if DEST.exists():
        raise FileExistsError('不覆盖补集原字节封存')
    frozen,result,audit=(read(BASE/name) for name in ('frozen.json','results.json','independent.json'))
    assert audit['passed'] and result['passed']
    assert audit['results_sha256']==sha(BASE/'results.json')
    assert audit['frozen_sha256']==result['frozen_sha256']==sha(BASE/'frozen.json')
    sources=dict(frozen['sources_sha256'])
    for name in ('scripts/archive_cinema_cap40_complements.py','scripts/audit_cinema_cap40_complements_git.py',
                 'docs/stages/2026-10-24-p16-cinema-cap40-complements.md'):
        sources[name]=sha(ROOT/name)
    for name,expected in sources.items():
        assert sha(ROOT/name)==expected,name
    for spec in frozen['inputs'].values():
        assert sha(spec['path'])==spec['sha256'] and Path(spec['path']).stat().st_size==spec['bytes']
    raw_names=('frozen.json','contract.json','start.json','results.json','independent.json','orientation-per-point.u8')
    raw={name:dict(sha256=sha(BASE/name),bytes=(BASE/name).stat().st_size) for name in raw_names}
    DEST.mkdir(parents=True)
    copied={}
    for name in ('frozen.json','contract.json','results.json','independent.json'):
        shutil.copyfile(BASE/name,DEST/name)
        assert sha(DEST/name)==raw[name]['sha256']
        copied[(DEST/name).relative_to(ROOT).as_posix()]=raw[name]['sha256']
    archive_path=DEST/'source-and-raw.zip'
    with zipfile.ZipFile(archive_path,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name in sources:
            archive.write(ROOT/name,'source/'+name)
        for name in raw:
            archive.write(BASE/name,'raw/'+name)
    with zipfile.ZipFile(archive_path) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist())==len(set(archive.namelist()))==len(sources)+len(raw)
        for name,expected in sources.items():
            assert hashlib.sha256(archive.read('source/'+name)).hexdigest()==expected
        for name,spec in raw.items():
            assert hashlib.sha256(archive.read('raw/'+name)).hexdigest()==spec['sha256']
    copied[archive_path.relative_to(ROOT).as_posix()]=sha(archive_path)
    tracked={name:value for name,value in sources.items() if name!='AGENTS.md'}
    tracked.update(copied)
    manifest=dict(schema='p16_cap40_complement_delivery_v1',passed=True,
        frozen_sha256=sha(BASE/'frozen.json'),results_sha256=sha(BASE/'results.json'),
        sources_sha256=sources,raw=raw,tracked_sha256=tracked,
        archive=dict(path=archive_path.relative_to(ROOT).as_posix(),sha256=sha(archive_path),
                     bytes=archive_path.stat().st_size,members=len(sources)+len(raw)),
        actual_suffix_queries=0,solver_calls=0,native_calls=0,performance_samples=0,
        scope='结果后处理封存；7源和6原件逐字节，不重新普查、不获得新模型资格。')
    path=DEST/'manifest.json'
    path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,manifest_sha256=sha(path),sources=len(sources),raw=len(raw),
                         zip_members=manifest['archive']['members']),ensure_ascii=False),flush=True)


if __name__=='__main__':
    main()
