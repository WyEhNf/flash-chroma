"""标准库核验直接表、二维分块、编译器档案及三组单次计数；不执行原生映射或计时。"""
import argparse,hashlib,json,zipfile
from pathlib import Path,PurePosixPath
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--archive',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('不得覆盖旧审计')
    manifest=read(a.archive/'manifest.json');snapshots=0;members=0;binary_members=0
    for name,spec in manifest['files'].items():
        f=a.archive/name;assert f.stat().st_size==spec['bytes'] and sha(f)==spec['sha256'],name
    for path in sorted(a.archive.rglob('measured-source.zip')):
        receipt=read(path.parent/('build.json' if (path.parent/'build.json').exists() else 'run.json'))
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None
            for name,digest in receipt['source_sha256'].items():
                logical=name.replace('\\','/');options=[n for n in z.namelist() if n==logical]
                if not options and '/16-lut-color/' in logical:
                    suffix=logical.split('/16-lut-color/',1)[-1];options=[n for n in z.namelist() if n.endswith('/'+suffix) or n==suffix]
                assert len(options)==1 and hashlib.sha256(z.read(options[0])).hexdigest()==digest,(str(path),name);members+=1
        snapshots+=1
    for path in sorted(a.archive.rglob('binaries-and-objects.zip')):
        index=read(path.parent/'binary-index.json');build=read(path.parent/'build.json')
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None and set(z.namelist())==set(index)
            for name,spec in index.items():
                data=z.read(name);assert len(data)==spec['bytes'] and hashlib.sha256(data).hexdigest()==spec['sha256'];binary_members+=1
        for spec in build['libraries'].values():assert index[PurePosixPath(spec['path'].replace('\\','/')).name]['sha256']==spec['sha256']
    full=[p for p in a.archive.glob('*-full-v*/results.json')];assert len(full)==3 and all(read(p)['pass'] for p in full)
    audit=read(a.archive/'research-audit.json');assert audit['pass'] and audit['new_full_domain_api_configurations']==72
    assert audit['full_wallclock_performance_calls']==0
    assert not audit['threefold_goal_completed']
    pmus=[read(p) for p in a.archive.glob('*-pmu-v1/results.json')];assert len(pmus)==3
    assert all(x['profile_completed'] and len(x['records'])==4 and x['candidate_wallclock_timing_calls']==0 for x in pmus)
    assert all(not read(p)['pass'] and not read(p)['goal_achieved'] for p in a.archive.glob('*-pmu-v1/screen-decision.json'))
    result={'pass':True,'purpose':__doc__,'manifest_files':len(manifest['files']),'source_snapshots':snapshots,'source_members':members,'binary_members':binary_members,'full_domain_acceptances':len(full),'performance_comparisons':0,'pmu_profiles':12,'threefold_goal_completed':False,'new_native_calls':0,'new_performance_calls':0,'script_sha256':sha(__file__)}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
