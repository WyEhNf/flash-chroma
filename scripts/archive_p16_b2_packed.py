"""99归档固定单版/全部失败和原始数据；不加载DLL或重测。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def sha(raw):return hashlib.sha256(raw).hexdigest()


def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def pack(target,members):
    rows=[]
    with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_STORED) as z:
        for name,path in sorted(members.items()):
            raw=path.read_bytes();z.writestr(name,raw)
            rows.append({'member':name,'bytes':len(raw),'sha256':sha(raw)})
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        for row in rows:assert sha(z.read(row['member']))==row['sha256']
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError('99归档不覆盖')
    a.output.mkdir(parents=True)
    perf=ROOT/'artifacts/p16-b2-packed-performance-v1';quality=ROOT/'artifacts/p16-b2-packed-quality-v2'
    build=ROOT/'artifacts/p16-b2-packed-build-v1'
    plan=json.loads((perf/'executed-plan.json').read_text(encoding='utf-8'))
    assert sha((perf/'executed-plan.json').read_bytes())=='1d99b7f1b5ddde6f667c70dd2e11e6d35eff9a478e033765e2b7f8f8e386e518'
    for folder,source,dest in ((perf,'executed-plan.json','executed-plan.json'),(perf,'results.json','results.json'),
            (perf,'decimal-audit.json','decimal-audit.json'),(perf,'threshold-summary.json','threshold-summary.json'),
            (quality,'correctness.json','quality-results.json'),(quality,'independent-check-v2.json','quality-independent-check-v2.json')):
        shutil.copyfile(folder/source,a.output/dest)
    audit=json.loads((perf/'offline-audit-v2.log').read_text(encoding='utf-8'))
    assert audit['actual_group_output_sha256_checks']==2112
    save(a.output/'offline-audit-v2.json',audit)
    raw={}
    for name,folder in (('performance',perf),('quality-v2',quality),
            ('finite-v1',ROOT/'artifacts/p16-b2-packed-finite-v1'),('symbolic-contract-v1',ROOT/'artifacts/p16-b2-packed-axis-contract-v1')):
        raw.update({name+'/'+path.relative_to(folder).as_posix():path for path in folder.rglob('*') if path.is_file()})
    for path in sorted((ROOT/'artifacts').glob('p16-b2-packed*')):
        if path.is_file():raw['boundary-and-static/'+path.name]=path
    save(a.output/'raw-members.json',pack(a.output/'raw-evidence.zip',raw))
    sources,dependencies={},{}
    for row in plan['sources']:
        path=Path(row['path']);data=path.read_bytes();assert sha(data)==row['sha256'],str(path)
        if path.is_relative_to(ROOT) and not path.is_relative_to(ROOT/'artifacts') and path.suffix.lower() not in ('.dll','.exe','.png','.slut','.bin'):
            relative=path.relative_to(ROOT).as_posix();sources[relative]=path;dependencies[relative]=path
    for path in sorted((ROOT/'scripts').glob('*p16_b2*.py')):
        sources[path.relative_to(ROOT).as_posix()]=path;dependencies[path.relative_to(ROOT).as_posix()]=path
    for path in sorted((ROOT/'experiments').glob('p16-b2*')):
        files=[path] if path.is_file() else [f for f in path.rglob('*') if f.is_file()]
        for source in files:
            relative=source.relative_to(ROOT).as_posix();sources[relative]=source;dependencies[relative]=source
    save(a.output/'source-members.json',pack(a.output/'execution-and-post-sources.zip',sources))
    metadata,products={},{}
    for path in build.rglob('*'):
        if not path.is_file():continue
        name=path.relative_to(build).as_posix()
        if path.name in ('build.log','build-receipt.json','CMakeCache.txt','flags.make','link.txt','linkLibs.rsp','objects1.rsp','includes_CXX.rsp','libraries-Release.json') or path.name.endswith(('.obj.d','.su')):
            metadata[name]=path
        if path.name.endswith(('.obj','.dll','.exe')) or path.name=='libjshc_core.a':products[name]=path
    save(a.output/'build-members.json',pack(a.output/'build-metadata.zip',metadata))
    save(a.output/'product-members.json',pack(a.output/'own-build-products.zip',products))
    models={}
    for role,model in plan['models'].items():
        for row in model['models']+[r for r in model['sidecars'] if r]:
            path=Path(row['path']);assert sha(path.read_bytes())==row['sha256']
            models[row['sha256']+path.suffix]=path
    pure=json.loads((ROOT/'experiments/p16-b2-packed-axis-contract-v1.json').read_text(encoding='utf-8'))
    for row in pure['models'].values():
        path=Path(row['path']);assert sha(path.read_bytes())==row['sha256'];models[row['sha256']+path.suffix]=path
    save(a.output/'model-members.json',pack(a.output/'fixed-model-inputs.zip',models))
    query=''.join('HEAD:'+relative+'\n' for relative in dependencies).encode()
    output=subprocess.run(['git','cat-file','--batch'],cwd=ROOT,input=query,capture_output=True,check=True).stdout
    offset=0;dep=[]
    for relative,path in dependencies.items():
        end=output.index(b'\n',offset);header=output[offset:end].split()
        if header[-1]==b'missing':prior=None;offset=end+1
        else:
            assert header[1]==b'blob';size=int(header[2]);prior=sha(output[end+1:end+1+size]);offset=end+size+2
        dep.append({'path':relative,'execution_sha256':sha(path.read_bytes()),'parent_git_blob_sha256':prior})
    assert offset==len(output)
    identity={'parent_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'execution_dependencies':dep,'executed_plan_sha256':sha((perf/'executed-plan.json').read_bytes()),
        'library_sha256':plan['libraries']['candidate']['sha256'],'archive_script_sha256':sha(Path(__file__).read_bytes()),
        'all_raw_source_product_model_members_sha256_passed':True,
        'member_counts':{'raw':len(raw),'source':len(sources),'build_metadata':len(metadata),'own_products':len(products),'models':len(models)},
        'scope':'原native/正式仅一次，所有失效/负例和两类独立audit-v1失败保留；v1完整质量草稿/未执行freezer明确作为未执行来源保留。新源postprocessing按事后身份，不伪称正式前冻结。MinGW外部依赖与100照片不复制，保留原计划身份/路径，需要原环境重现。'}
    save(a.output/'identity.json',identity)
    print(json.dumps({k:v for k,v in identity.items() if k!='execution_dependencies'},ensure_ascii=False))


if __name__=='__main__':main()
