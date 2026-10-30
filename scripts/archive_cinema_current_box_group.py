"""封存同盒geometry过门/原point安全表超门原件，不执行数学/模型/性能。"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]
GEOMETRY=ROOT/'artifacts/cinema-current-box-group-geometry-v1'
SCREEN=ROOT/'artifacts/cinema-current-box-group-screen-v1'
OUT=ROOT/'report/data/p16-cinema-current-box-group-20261024'
PUBLISHED=[
    'experiments/p16-cinema-current-box-group-proposal-v1.md',
    'experiments/p16-cinema-current-box-group-v1.json',
    'experiments/p16-cinema-current-box-group-screen-v1.json',
    'scripts/cinema_box_group.py','scripts/count_cinema_current_box_group.py',
    'scripts/audit_cinema_current_box_group.py','scripts/screen_cinema_current_box_group.py',
    'scripts/audit_cinema_current_box_group_screen.py','scripts/archive_cinema_current_box_group.py',
    'scripts/audit_cinema_current_box_group_git.py','docs/stages/2026-10-24-p16-cinema-current-box-group.md']
EXPECTED={
    'geometry/frozen.json':'6753527ad70f63659cd93ac29517e68525a39b2375170c4e7ebce3cb1fea8c8a',
    'geometry/contract.json':'63cb7e96b44eaf4b312c4938c84665631fd4cdc21cc2a1ef404758ac5024f6b0',
    'geometry/groups.npz':'e0d2ad708d65adac99c7c571b8889c74b85382d4bae3fc410b21745fc4e2bf70',
    'geometry/summary.json':'76b48dbfd6e6a081148c1048986ffcd0156b033603342a9720d05b7b404c7ec0',
    'geometry/independent.json':'f3b0dbf4e30fa7dc45baa8b97ed89f435c6faf3576c763d8607b5331c2ccb141',
    'screen/frozen.json':'d1103997455ee40d99381840b00291e102cd9721c1600420af79d71a638bd9fb',
    'screen/contract.json':'71e3fd8c7de270a7a1f6d8c1c05b42da6db6c0fee217e74c43c69587e1cb9727',
    'screen/group-screen.npz':'464b0349c80ef5ee23d992519d43c7359c213868d6a2c1d021e6c11cfae5ffc5',
    'screen/point-screen.npz':'37b00e42e30a5a1a56a8706efde5770b404e00b38855ca1154b59487c3f7e6ec',
    'screen/summary.json':'faceafb72f5c4d7e2253d1da8840a55a8686fc15a54663f35ef2bcc226794aee',
    'screen/independent.json':'8bd29e5315224c0b658233ae83da2559e3979215386f20eb30dce03ab98b790b'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path,value):
    if path.exists():
        raise FileExistsError('不覆盖同盒归档：'+str(path))
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def package(filename,paths):
    members={}
    with zipfile.ZipFile(OUT/filename,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for path in sorted(set(paths)):
            name=path.relative_to(ROOT).as_posix();raw=path.read_bytes()
            assert name not in members
            archive.writestr(name,raw)
            members[name]={'bytes':len(raw),'sha256':sha(raw)}
    with zipfile.ZipFile(OUT/filename) as archive:
        names=archive.namelist();assert len(names)==len(set(names)) and set(names)==set(members)
        assert archive.testzip() is None
        for name,spec in members.items():
            raw=archive.read(name);assert len(raw)==spec['bytes'] and sha(raw)==spec['sha256']
            spec['crc32']=archive.getinfo(name).CRC
    return {'sha256':sha((OUT/filename).read_bytes()),'members':members}


def main():
    if OUT.exists():
        raise FileExistsError('不覆盖同盒归档目录')
    for name,digest in EXPECTED.items():
        stage,relative=name.split('/',1);path=(GEOMETRY if stage=='geometry' else SCREEN)/relative
        assert sha(path.read_bytes())==digest,name
    geometry,screen=read(GEOMETRY/'summary.json'),read(SCREEN/'summary.json')
    gi,si=read(GEOMETRY/'independent.json'),read(SCREEN/'independent.json')
    assert geometry['within_gate'] and gi['pass'] and si['pass']
    assert geometry['logical_point_states']==screen['logical_point_states']==5284765
    assert geometry['groups']==screen['groups']==27817
    assert geometry['grouped_query_states']==screen['main_true_suffix_state_queries']==1267197
    assert not screen['within_gate'] and screen['stop']=='empty_or_original_point_resource_gate'
    assert screen['dangerous_original_points']==17620 and screen['safe_original_table_rows']==1525836
    assert screen['zero_safe_original_points']==0 and si['aggregate_true_suffix_state_queries']==2534394
    assert not (SCREEN/'danger-allowed.npz').exists()
    frozen=read(SCREEN/'frozen.json')
    for name,digest in frozen['source_sha256'].items():
        assert sha((ROOT/name).read_bytes())==digest,name
    for name,spec in frozen['inputs'].items():
        assert sha(Path(spec['path']).read_bytes())==spec['sha256'],name
    old_aabb=Path(frozen['inputs']['old_aabb']['path'])
    old_summary=Path(frozen['inputs']['old_summary']['path'])
    old_independent=Path(frozen['inputs']['old_independent']['path'])
    old_frozen=Path(frozen['inputs']['old_freeze']['path'])
    old=read(old_summary);assert old['stop']=='state_count_gate' and old['state_queries']==0
    receipts=[ROOT/'artifacts/cinema-current-cap40-gac-head-incremental-v1.json',
              ROOT/'artifacts/p16-direct-active-packed-head-audit-v1.json']
    for path in receipts:
        value=read(path);assert value.get('pass',value.get('passed')) is True,path
    source_names=sorted(set(frozen['source_sha256'])|set(PUBLISHED))
    raws=sorted(p for folder in (GEOMETRY,SCREEN) for p in folder.iterdir() if p.is_file())
    raws.extend([old_aabb,old_summary,old_independent,old_frozen,*receipts])
    parent=subprocess.check_output(['git','-c','gc.auto=0','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    OUT.mkdir(parents=True)
    archives={'source.zip':package('source.zip',[ROOT/n for n in source_names]),'raw.zip':package('raw.zip',raws)}
    summary={
        'scope':'完全相同九字节盒共享查询；geometry过门，原point安全表两门失败，0CP/候选/native/性能',
        'original_points':171271,'selected_physical_nodes':273,'groups':27817,
        'logical_point_states':5284765,'old_logical_state_stop_preserved':True,
        'grouped_query_states_per_complete_path':1267197,'aggregate_true_suffix_state_queries':2534394,
        'dangerous_original_points':17620,'dangerous_point_gate':8192,
        'safe_original_table_rows':1525836,'safe_row_gate':500000,'zero_safe_original_points':0,
        'stop':'empty_or_original_point_resource_gate','shared_assignment_proved':False,'candidate_created':False,
        'geometry_independent_pass':True,'screen_independent_pass':True,'solver_calls':0,'performance_samples':0}
    save(OUT/'summary.json',summary)
    save(OUT/'manifest.json',dict(parent_commit=parent,expected_executed_raw_sha256=EXPECTED,zip_files=archives,
        frozen_mathematical_sources=len(frozen['source_sha256']),archived_source_members=len(source_names),
        archive_extra_only=[n for n in source_names if n not in frozen['source_sha256']],
        consumed_parent_receipts=[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())} for p in receipts],
        scope='消费父不可变收据与本阶段完整原件；不重跑历史数值，不改旧STOP，不将组数替换原point资源'))
    paths=[ROOT/name for name in PUBLISHED]+sorted(OUT.iterdir())
    files={p.relative_to(ROOT).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in paths}
    save(OUT/'git-whitelist.json',dict(files=files,parent_commit=parent,
        metadata_additional_path='.gitattributes',scope='白名单自身及attrs另显式stage；排除axis未执行源和root正式性能源'))
    print({'passed':True,'files_excluding_whitelist_attrs':len(files),'source_members':len(source_names),
        'raw_members':len(archives['raw.zip']['members']),'parent_commit':parent},flush=True)


if __name__=='__main__':
    main()
