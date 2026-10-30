"""独立核同盒阶段Git对象、ZIP CRC/SHA、旧STOP与完整查询身份；不重做数学。"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]
BASE='report/data/p16-cinema-current-box-group-20261024/'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git(*args):
    return subprocess.check_output(['git','-c','gc.auto=0','-c','maintenance.auto=false',*args],cwd=ROOT)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--git-ref',choices=(':','HEAD'),required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():
        raise FileExistsError('不覆盖同盒Git字节审计')
    prefix=':' if args.git_ref==':' else 'HEAD:'
    def blob(name):
        return git('show',prefix+name)
    whitelist=json.loads(blob(BASE+'git-whitelist.json'));checks=1
    for name,spec in whitelist['files'].items():
        raw=blob(name);assert len(raw)==spec['bytes'] and sha(raw)==spec['sha256'],name
        checks+=1
    manifest=json.loads(blob(BASE+'manifest.json'));assert manifest['parent_commit']==whitelist['parent_commit']
    parent=manifest['parent_commit'];permitted=set(whitelist['files'])|{BASE+'git-whitelist.json','.gitattributes'}
    if args.git_ref==':':
        assert git('rev-parse','HEAD').decode().strip()==parent
        changed=set(git('diff','--cached','--name-only').decode().splitlines())
    else:
        subprocess.check_call(['git','-c','gc.auto=0','merge-base','--is-ancestor',parent,'HEAD'],cwd=ROOT)
        changed=set(git('diff','--name-only',parent,'HEAD').decode().splitlines())
    assert changed==permitted,{'extra':sorted(changed-permitted),'missing':sorted(permitted-changed)}
    members={}
    for filename,spec in manifest['zip_files'].items():
        raw=blob(BASE+filename);assert sha(raw)==spec['sha256']
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            names=archive.namelist();assert len(names)==len(set(names)) and set(names)==set(spec['members'])
            assert archive.testzip() is None
            for name,expected in spec['members'].items():
                data=archive.read(name)
                assert len(data)==expected['bytes'] and sha(data)==expected['sha256'] and archive.getinfo(name).CRC==expected['crc32'],name
                if name in members:
                    assert members[name]==data
                members[name]=data;checks+=1
    roots={'geometry':'artifacts/cinema-current-box-group-geometry-v1/','screen':'artifacts/cinema-current-box-group-screen-v1/'}
    for name,expected in manifest['expected_executed_raw_sha256'].items():
        stage,relative=name.split('/',1);assert sha(members[roots[stage]+relative])==expected
    frozen=json.loads(members[roots['screen']+'frozen.json'])
    for name,expected in frozen['source_sha256'].items():
        assert sha(members[name])==expected,name
    geometry=json.loads(members[roots['geometry']+'summary.json'])
    screen=json.loads(members[roots['screen']+'summary.json']);independent=json.loads(members[roots['screen']+'independent.json'])
    assert geometry['within_gate'] and not screen['within_gate']
    assert geometry['logical_point_states']==5284765 and screen['main_true_suffix_state_queries']==1267197
    assert screen['dangerous_original_points']==17620 and screen['safe_original_table_rows']==1525836
    assert independent['pass'] and independent['summary_sha256']==sha(members[roots['screen']+'summary.json'])
    assert independent['aggregate_true_suffix_state_queries']==2534394
    for spec in manifest['consumed_parent_receipts']:
        raw=members[spec['path']];assert sha(raw)==spec['sha256']
        value=json.loads(raw);assert value.get('pass',value.get('passed')) is True
    value={'pass':True,'git_ref':args.git_ref,'parent_commit':parent,'new_checks':checks,
        'whitelist_objects':len(whitelist['files'])+1,'changed_paths_including_attrs':len(changed),
        'zip_members':sum(len(v['members']) for v in manifest['zip_files'].values()),
        'frozen_mathematical_sources':len(frozen['source_sha256']),'all_crc_sha_pass':True,
        'scope':'增量Git/ZIP原字节与不可变父收据；不重新执行历史数值或作新精度资格'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(value,flush=True)


if __name__=='__main__':
    main()
