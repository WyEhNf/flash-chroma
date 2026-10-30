"""封存24种均匀轴bank完整拒绝证据；不重跑普查、native或性能。"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'artifacts/p16-direct-axis-banks-v1'
OUT=ROOT/'report/data/p16-direct-axis-banks-20261024'
DOC='docs/stages/2026-10-24-p16-direct-axis-banks.md'
PUBLISHED=('experiments/p16-direct-axis-banks-proposal-v1.md',
    'scripts/census_direct_axis_banks.py','scripts/audit_direct_axis_banks.py',
    'scripts/archive_direct_axis_banks.py','scripts/audit_direct_axis_banks_git.py',DOC)
EXPECTED={
    'frozen.json':'081efe0a94ed789dc970b2804e1015f4f1a74178676b60532548c4467875194d',
    'contract.json':'fdac4ec9d65792026cd4da734de863d7e0b9ecc3db193b304527cb868fb9f7cf',
    'first-input-u32.bin':'a8fa7d0bfb1cbbb1b8efeba6bde77a7edf00d6befb82ed642e422fbf0dbfd33e',
    'active-colors-u32.bin':'e3a91175bf850756330c4a9d221dddb2ea05d315e50a61f1d323981360e0a224',
    'results.json':'61fde9e61595260cc5b5c954ff32a0d1313193b5603240cbb8243aca4155601b',
    'independent.json':'7eff395b9159dee0be981ed67140dfd718b2a62e2e64a613db59337c49561078'}
RAW_NAMES=set(EXPECTED)|{'start.json'}
MAXIMA={'R':[311,309,303,294,294,294,294,292],
    'G':[334,331,320,310,304,297,297,296],'B':[333,326,312,303,298,295,289,287]}
BANKS=[2,4,8,16,32,64,128,256]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path,value):
    if path.exists():
        raise FileExistsError('不覆盖轴bank交付原件：'+str(path))
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def package(filename,paths):
    members={}
    with zipfile.ZipFile(OUT/filename,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for path in sorted(paths):
            assert not path.is_symlink()
            name=path.relative_to(ROOT).as_posix();raw=path.read_bytes()
            assert name not in members
            archive.writestr(name,raw)
            members[name]={'bytes':len(raw),'sha256':sha(raw)}
    with zipfile.ZipFile(OUT/filename) as archive:
        names=archive.namelist()
        assert len(names)==len(set(names)) and set(names)==set(members)
        assert archive.testzip() is None
        for name,spec in members.items():
            raw=archive.read(name)
            assert len(raw)==spec['bytes'] and sha(raw)==spec['sha256']
            spec['crc32']=archive.getinfo(name).CRC
    return {'sha256':sha((OUT/filename).read_bytes()),'members':members}


def main():
    if OUT.exists():
        raise FileExistsError('不覆盖轴bank交付目录')
    assert {p.name for p in RAW.iterdir() if p.is_file()}==RAW_NAMES
    for name,expected in EXPECTED.items():
        assert sha((RAW/name).read_bytes())==expected,name
    frozen,result,independent,contract=[read(RAW/name) for name in
        ('frozen.json','results.json','independent.json','contract.json')]
    assert result['passed'] and independent['passed'] and contract['pass']
    assert result['frozen_sha256']==independent['frozen_sha256']==contract['frozen_sha256']==EXPECTED['frozen.json']
    assert result['contract_sha256']==EXPECTED['contract.json'] and independent['results_sha256']==EXPECTED['results.json']
    assert len(frozen['source_sha256'])==3 and len(frozen['inputs'])==7
    assert frozen['upstream_lineage_sources']==223 and frozen['upstream_lineage_inputs']==13
    for name,expected in frozen['source_sha256'].items():
        assert sha((ROOT/name).read_bytes())==expected,name
    assert independent['script_sha256']==frozen['source_sha256']['scripts/audit_direct_axis_banks.py']
    for name,spec in result['artifacts'].items():
        assert name in RAW_NAMES
        raw=(RAW/name).read_bytes()
        assert len(raw)==spec['bytes'] and sha(raw)==spec['sha256'],name
    actual_inputs=[]
    for name,spec in frozen['inputs'].items():
        path=Path(spec['path']).resolve()
        assert path.is_relative_to(ROOT.resolve()) and not path.is_symlink()
        raw=path.read_bytes()
        assert len(raw)==spec['bytes'] and sha(raw)==spec['sha256'],name
        actual_inputs.append(path)
    prior=read(Path(frozen['inputs']['frozen.json']['path']))
    prior_result=read(Path(frozen['inputs']['results.json']['path']))
    prior_audit=read(Path(frozen['inputs']['independent.json']['path']))
    assert len(prior['source_sha256'])==223 and len(prior['inputs_sha256'])==13
    assert prior_result['passed'] and prior_audit['passed']
    assert prior_audit['frozen_sha256']==frozen['inputs']['frozen.json']['sha256']
    assert prior_audit['results_sha256']==frozen['inputs']['results.json']['sha256']
    for name in ('physical-ids-u16-with-guard.bin','whole-palette-u32.bin',
                 'packed-ids-with-guard.bin','active-palette-u32.bin'):
        assert prior_result['artifacts'][name]=={k:frozen['inputs'][name][k] for k in ('bytes','sha256')}
    assert result['selected_configuration'] is independent['selected'] is None
    assert result['stop']=='no_representable_configuration' and result['selected_table_and_palette_bytes'] is None
    assert result['selected_full_rgb_decode_entries']==independent['independently_decoded_selected_entries']==0
    assert result['main_total_original_table_entries']==independent['independently_scanned_original_entries']==16777216
    assert independent['aggregate_total_original_table_entries']==33554432
    assert independent['full_first_matrix_rows']==264192 and result['first_matrix_payload_bytes']==1056768
    assert len(result['configurations'])==independent['configurations']==24
    for axis,maxima in MAXIMA.items():
        rows=[r for r in result['configurations'] if r['axis']==axis]
        assert [r['bank_count'] for r in rows]==BANKS
        assert [r['maximum_bank_colors'] for r in rows]==maxima
        assert all(not r['representable'] and len(r['overflow_257_colors'])==257 for r in rows)
    assert len(contract['cases'])==4 and len(contract['guard_lengths'])==8
    assert contract['all_24_rejected_configuration_fixture'] and contract['pure_function_rejects_without_output_files']==3
    assert result['native_prepare_calls']==result['native_apply_calls']==result['performance_samples']==0
    assert independent['native_prepare_calls']==independent['native_apply_calls']==independent['performance_samples']==0
    parent=subprocess.check_output(['git','-c','gc.auto=0','-c','maintenance.auto=false','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    OUT.mkdir(parents=True)
    archives={'source.zip':package('source.zip',[ROOT/name for name in PUBLISHED]),
        'raw.zip':package('raw.zip',[RAW/name for name in sorted(RAW_NAMES)]+actual_inputs)}
    for name in ('frozen.json','contract.json','results.json','independent.json'):
        shutil.copyfile(RAW/name,OUT/name)
        assert (OUT/name).read_bytes()==(RAW/name).read_bytes()
    save(OUT/'manifest.json',dict(parent_commit=parent,expected_executed_sha256=EXPECTED,zip_files=archives,
        executed_sources=3,actual_upstream_inputs=7,lineage_only_sources=223,lineage_only_inputs=13,
        mathematical_outcome='全部24均匀单轴bank不可表示；无候选、无容量、无native和速度资格',
        scanned_original_entries_per_path=16777216,aggregate_logical_entries=33554432,
        scope='只核已有原件/输入与封存字节；不重跑完整扫描、不加载历史native或谱系223源'))
    paths=[ROOT/name for name in PUBLISHED]+sorted(OUT.iterdir())
    files={p.relative_to(ROOT).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in paths}
    save(OUT/'git-whitelist.json',dict(files=files,parent_commit=parent,metadata_additional_path='.gitattributes',
        scope='白名单自身和attrs另显式stage；不含293/294、旧AGENTS或其它方案'))
    print(json.dumps(dict(passed=True,files_excluding_whitelist_attrs=len(files),
        source_members=6,raw_members=14,parent_commit=parent,native_calls=0,performance_samples=0),ensure_ascii=False))


if __name__=='__main__':
    main()
