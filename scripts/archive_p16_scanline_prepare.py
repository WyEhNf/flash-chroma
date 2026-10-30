"""100归档唯一执行/全部AA失效及来源；不加载native或重测。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def pack(target,members):
    rows=[]
    with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_STORED) as archive:
        for name,path in sorted(members.items()):
            raw=path.read_bytes();archive.writestr(name,raw);rows.append({'member':name,'bytes':len(raw),'sha256':sha(raw)})
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        for row in rows:assert sha(archive.read(row['member']))==row['sha256']
    return rows


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    if args.output.exists():raise FileExistsError('100归档不覆盖')
    args.output.mkdir(parents=True)
    performance=ROOT/'artifacts/p16-scanline-prepare-performance-v1';quality=ROOT/'artifacts/p16-scanline-prepare-quality-v1'
    build=ROOT/'artifacts/p16-scanline-prepare-build-v1';plan=json.loads((performance/'executed-plan.json').read_text(encoding='utf-8'))
    assert sha((performance/'executed-plan.json').read_bytes())=='bd51bee8e992d46e26fb6b2678d44f5b24c81255643b85d52b8eab4c189b5936'
    for folder,source,destination in ((performance,'executed-plan.json','executed-plan.json'),(performance,'results.json','results.json'),
            (performance,'summary.json','summary.json'),(performance,'all-grades.csv','all-grades.csv'),
            (performance,'decimal-audit.json','decimal-audit.json'),(quality,'correctness.json','quality-results.json'),
            (quality,'offline-audit.json','quality-offline-audit.json')):
        shutil.copyfile(folder/source,args.output/destination)
    audit=json.loads((performance/'offline-audit.log').read_text(encoding='utf-8'))
    assert audit['actual_group_output_sha256_checks']==2112;save(args.output/'offline-audit.json',audit)
    raw={}
    for name,folder in (('performance',performance),('quality',quality),('finite',ROOT/'artifacts/p16-scanline-prepare-finite-v1')):
        raw.update({name+'/'+path.relative_to(folder).as_posix():path for path in folder.rglob('*') if path.is_file()})
    for path in sorted((ROOT/'artifacts').glob('p16-scanline*')):
        if path.is_file():raw['preflight-and-assembly/'+path.name]=path
    save(args.output/'raw-members.json',pack(args.output/'raw-evidence.zip',raw))
    sources,dependencies={},{}
    for entry in plan['sources']:
        path=Path(entry['path']);assert sha(path.read_bytes())==entry['sha256'],str(path)
        if path.is_relative_to(ROOT) and not path.is_relative_to(ROOT/'artifacts') and path.suffix.lower() not in ('.dll','.exe','.png','.slut','.bin'):
            relative=path.relative_to(ROOT).as_posix();sources[relative]=path;dependencies[relative]=path
    for path in sorted((ROOT/'scripts').glob('*p16_scanline*.py')):
        sources[path.relative_to(ROOT).as_posix()]=path;dependencies[path.relative_to(ROOT).as_posix()]=path
    for path in sorted((ROOT/'experiments').glob('p16-scanline*')):
        files=[path] if path.is_file() else [p for p in sorted(path.rglob('*')) if p.is_file()]
        for source in files:
            relative=source.relative_to(ROOT).as_posix();sources[relative]=source;dependencies[relative]=source
    save(args.output/'source-members.json',pack(args.output/'execution-and-post-sources.zip',sources))
    metadata,products={},{}
    for path in build.rglob('*'):
        if not path.is_file():continue
        name=path.relative_to(build).as_posix()
        if path.name in ('build.log','build-receipt.json','CMakeCache.txt','flags.make','link.txt','linkLibs.rsp','objects1.rsp','includes_CXX.rsp','libraries-Release.json') or path.name.endswith(('.obj.d','.su')):metadata[name]=path
        if path.name.endswith(('.obj','.dll','.exe')) or path.name=='libjshc_core.a':products[name]=path
    save(args.output/'build-members.json',pack(args.output/'build-metadata.zip',metadata))
    save(args.output/'product-members.json',pack(args.output/'own-build-products.zip',products))
    models={}
    for model in plan['models'].values():
        for entry in model['models']+[r for r in model['sidecars'] if r]:
            path=Path(entry['path']);assert sha(path.read_bytes())==entry['sha256'];models[entry['sha256']+path.suffix]=path
    save(args.output/'model-members.json',pack(args.output/'fixed-model-inputs.zip',models))
    query=''.join('HEAD:'+relative+'\n' for relative in dependencies).encode()
    output=subprocess.run(['git','cat-file','--batch'],cwd=ROOT,input=query,capture_output=True,check=True).stdout
    offset=0;records=[]
    for relative,path in dependencies.items():
        end=output.index(b'\n',offset);header=output[offset:end].split()
        if header[-1]==b'missing':parent=None;offset=end+1
        else:
            assert header[1]==b'blob';size=int(header[2]);parent=sha(output[end+1:end+1+size]);offset=end+size+2
        records.append({'path':relative,'execution_sha256':sha(path.read_bytes()),'parent_git_blob_sha256':parent})
    assert offset==len(output)
    identity={'parent_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'execution_dependencies':records,'executed_plan_sha256':sha((performance/'executed-plan.json').read_bytes()),
        'library_sha256':plan['libraries']['candidate']['sha256'],'archive_script_sha256':sha(Path(__file__).read_bytes()),
        'all_raw_source_product_model_members_sha256_passed':True,
        'member_counts':{'raw':len(raw),'source':len(sources),'build_metadata':len(metadata),'own_products':len(products),'models':len(models)},
        'scope':'100唯一构建/私有合同/新增整链/正式原件全部保留，AA49/126与所有失效不筛选。101静态草稿不在本归档或提交。事后汇总/封存源按事后身份，不伪称正式前冻结。旧已认证cube/照片前缀及MinGW外部依赖/100照片不复制，保留原计划路径和SHA；需要相应原件重现。'}
    save(args.output/'identity.json',identity)
    print(json.dumps({k:v for k,v in identity.items() if k!='execution_dependencies'},ensure_ascii=False))


if __name__=='__main__':main()
