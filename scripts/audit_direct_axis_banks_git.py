"""独立核轴bank拒绝阶段的Git原字节、ZIP CRC/SHA与冻结引用；不重算数值。"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]
BASE='report/data/p16-direct-axis-banks-20261024/'
RAW='artifacts/p16-direct-axis-banks-v1/'
EXPECTED={
    'frozen.json':'081efe0a94ed789dc970b2804e1015f4f1a74178676b60532548c4467875194d',
    'contract.json':'fdac4ec9d65792026cd4da734de863d7e0b9ecc3db193b304527cb868fb9f7cf',
    'first-input-u32.bin':'a8fa7d0bfb1cbbb1b8efeba6bde77a7edf00d6befb82ed642e422fbf0dbfd33e',
    'active-colors-u32.bin':'e3a91175bf850756330c4a9d221dddb2ea05d315e50a61f1d323981360e0a224',
    'results.json':'61fde9e61595260cc5b5c954ff32a0d1313193b5603240cbb8243aca4155601b',
    'independent.json':'7eff395b9159dee0be981ed67140dfd718b2a62e2e64a613db59337c49561078'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git(*args):
    return subprocess.check_output(['git','-c','gc.auto=0','-c','maintenance.auto=false',*args],cwd=ROOT)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--git-ref',choices=(':','HEAD'),required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():
        raise FileExistsError('不覆盖轴bank Git审计原件')
    prefix=':' if args.git_ref==':' else 'HEAD:'
    def blob(name):
        return git('show',prefix+name)
    whitelist=json.loads(blob(BASE+'git-whitelist.json'));checks=1
    for name,spec in whitelist['files'].items():
        raw=blob(name)
        assert len(raw)==spec['bytes'] and sha(raw)==spec['sha256'],name
        checks+=1
    manifest=json.loads(blob(BASE+'manifest.json'))
    assert manifest['parent_commit']==whitelist['parent_commit']
    permitted=set(whitelist['files'])|{BASE+'git-whitelist.json','.gitattributes'}
    parent=manifest['parent_commit']
    if args.git_ref==':':
        assert git('rev-parse','HEAD').decode().strip()==parent
        changed=set(git('diff','--cached','--name-only').decode().splitlines())
    else:
        subprocess.check_call(['git','-c','gc.auto=0','-c','maintenance.auto=false','merge-base','--is-ancestor',parent,'HEAD'],cwd=ROOT)
        changed=set(git('diff','--name-only',parent,'HEAD').decode().splitlines())
    assert changed==permitted,{'extra':sorted(changed-permitted),'missing':sorted(permitted-changed)}
    members={};member_count=0
    assert set(manifest['zip_files'])=={'source.zip','raw.zip'}
    for filename,spec in manifest['zip_files'].items():
        raw=blob(BASE+filename)
        assert sha(raw)==spec['sha256']
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            names=archive.namelist()
            assert len(names)==len(set(names)) and set(names)==set(spec['members'])
            assert archive.testzip() is None
            for name,expected in spec['members'].items():
                value=archive.read(name)
                assert len(value)==expected['bytes'] and sha(value)==expected['sha256']
                assert archive.getinfo(name).CRC==expected['crc32']
                if name in members:
                    assert members[name]==value
                members[name]=value;checks+=1;member_count+=1
    assert len(manifest['zip_files']['source.zip']['members'])==6
    assert len(manifest['zip_files']['raw.zip']['members'])==14
    assert manifest['expected_executed_sha256']==EXPECTED
    for name,expected in EXPECTED.items():
        assert sha(members[RAW+name])==expected,name
    for name in ('frozen.json','contract.json','results.json','independent.json'):
        assert blob(BASE+name)==members[RAW+name],name
    frozen,result,independent,contract=[json.loads(members[RAW+name]) for name in
        ('frozen.json','results.json','independent.json','contract.json')]
    assert len(frozen['source_sha256'])==3 and len(frozen['inputs'])==7
    for name,expected in frozen['source_sha256'].items():
        assert sha(members[name])==expected,name
    for name,spec in frozen['inputs'].items():
        member=Path(spec['path']).relative_to(ROOT).as_posix()
        raw=members[member]
        assert len(raw)==spec['bytes'] and sha(raw)==spec['sha256'],name
    for name,spec in result['artifacts'].items():
        raw=members[RAW+name]
        assert len(raw)==spec['bytes'] and sha(raw)==spec['sha256'],name
    assert result['passed'] and independent['passed'] and contract['pass']
    assert result['frozen_sha256']==independent['frozen_sha256']==contract['frozen_sha256']==EXPECTED['frozen.json']
    assert result['contract_sha256']==EXPECTED['contract.json'] and independent['results_sha256']==EXPECTED['results.json']
    assert independent['script_sha256']==frozen['source_sha256']['scripts/audit_direct_axis_banks.py']
    assert result['selected_configuration'] is independent['selected'] is None
    assert result['stop']=='no_representable_configuration' and result['selected_table_and_palette_bytes'] is None
    assert len(result['configurations'])==24 and all(not row['representable'] for row in result['configurations'])
    assert result['selected_full_rgb_decode_entries']==independent['independently_decoded_selected_entries']==0
    assert independent['aggregate_total_original_table_entries']==33554432
    assert manifest['lineage_only_sources']==223 and manifest['lineage_only_inputs']==13
    upstream_prefix=Path(frozen['inputs']['frozen.json']['path']).relative_to(ROOT).as_posix().rsplit('/',1)[0]+'/'
    upstream_frozen=json.loads(members[upstream_prefix+'frozen.json'])
    upstream_result=json.loads(members[upstream_prefix+'results.json'])
    upstream_audit=json.loads(members[upstream_prefix+'independent.json'])
    assert len(upstream_frozen['source_sha256'])==223 and len(upstream_frozen['inputs_sha256'])==13
    assert upstream_result['passed'] and upstream_audit['passed']
    assert upstream_audit['frozen_sha256']==sha(members[upstream_prefix+'frozen.json'])
    assert upstream_audit['results_sha256']==sha(members[upstream_prefix+'results.json'])
    for name in ('physical-ids-u16-with-guard.bin','whole-palette-u32.bin',
                 'packed-ids-with-guard.bin','active-palette-u32.bin'):
        raw=members[upstream_prefix+name];expected=upstream_result['artifacts'][name]
        assert len(raw)==expected['bytes'] and sha(raw)==expected['sha256']
    value=dict(passed=True,git_ref=args.git_ref,parent_commit=parent,new_checks=checks,
        whitelist_objects=len(whitelist['files'])+1,changed_paths_including_attrs=len(changed),
        zip_members=member_count,executed_sources=3,actual_upstream_inputs=7,lineage_only_sources=223,
        all_crc_sha_passed=True,native_calls=0,performance_samples=0,
        scope='Git/ZIP原字节与已完成独立审计绑定；不重新扫描16M或授新精度/速度资格')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(value,ensure_ascii=False))


if __name__=='__main__':
    main()
