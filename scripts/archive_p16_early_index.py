"""101有限阶段原件封存，不重复native或执行完整链/照片/性能。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from archive_p16_scanline_prepare import pack,save

ROOT=Path(__file__).resolve().parents[1]
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    if args.output.exists():raise FileExistsError('101有限归档不覆盖')
    frozen=ROOT/'experiments/p16-early-index-static-v1.json';assert sha(frozen)=='0803366eafad0bcfd00c69398572fcab518871ff57141fe2b50d6cf47b209e78'
    plan=json.loads(frozen.read_text(encoding='utf-8'))
    for row in plan['sources']:assert sha(Path(row['path']))==row['sha256']
    build=ROOT/'artifacts/p16-early-index-build-v1';finite=ROOT/'artifacts/p16-early-index-finite-v1';observation=ROOT/'artifacts/p16-early-index-finite-observation-v1'
    result=json.loads((finite/'results.json').read_text(encoding='utf-8'));assert result['passed'] and result['return_code']==0
    assert all(result['native_result'].get(k)==v for k,v in plan['finite_expected'].items())
    br=json.loads((build/'build-receipt.json').read_text(encoding='utf-8'));assert br['return_code']==0 and br['all_nine_old_objects_byte_identical']
    obs=json.loads((observation/'results.json').read_text(encoding='utf-8'))
    assert obs['passed'] and obs['native_result_sha256']==sha(finite/'results.json')
    assert obs['sample_count']==0 and obs['sampled_rss_max_bytes'] is None and obs['observed_os_peak_wset_max_bytes'] is None
    args.output.mkdir(parents=True)
    for source,name in ((frozen,'source-freeze.json'),(finite/'results.json','finite-results.json'),(finite/'executed-plan.json','finite-executed-plan.json'),
            (observation/'results.json','rss-observation.json'),(build/'build-receipt.json','build-receipt.json'),
            (ROOT/'artifacts/p16-early-index-assembly-audit-v1.json','assembly-audit.json')):shutil.copyfile(source,args.output/name)
    raw={}
    for name,folder in (('finite',finite),('observation',observation)):
        raw.update({name+'/'+path.relative_to(folder).as_posix():path for path in folder.rglob('*') if path.is_file()})
    for path in sorted((ROOT/'artifacts').glob('p16-early-index*')):
        if path.is_file():raw['static/'+path.name]=path
    save(args.output/'raw-members.json',pack(args.output/'raw-evidence.zip',raw))
    sources={}
    for row in plan['sources']:
        path=Path(row['path'])
        if path.is_relative_to(ROOT) and not path.is_relative_to(ROOT/'artifacts') and path.suffix.lower() not in ('.exe','.dll','.png','.slut','.bin'):
            sources[path.relative_to(ROOT).as_posix()]=path
    for path in sorted((ROOT/'scripts').glob('*p16_early_index*.py')):sources[path.relative_to(ROOT).as_posix()]=path
    helper=ROOT/'scripts/archive_p16_scanline_prepare.py';sources[helper.relative_to(ROOT).as_posix()]=helper
    for path in sorted((ROOT/'experiments').glob('p16-early-index*')):
        for source in ([path] if path.is_file() else [p for p in sorted(path.rglob('*')) if p.is_file()]):sources[source.relative_to(ROOT).as_posix()]=source
    save(args.output/'source-members.json',pack(args.output/'execution-and-post-sources.zip',sources))
    metadata,products={},{}
    for path in build.rglob('*'):
        if not path.is_file():continue
        name=path.relative_to(build).as_posix()
        if path.name in ('build.log','build-receipt.json','CMakeCache.txt','flags.make','link.txt','linkLibs.rsp','objects1.rsp','includes_CXX.rsp','libraries-Release.json') or path.name.endswith(('.obj.d','.su')):metadata[name]=path
        if path.name.endswith(('.obj','.dll','.exe')) or path.name=='libjshc_core.a':products[name]=path
    save(args.output/'build-members.json',pack(args.output/'build-metadata.zip',metadata))
    save(args.output/'product-members.json',pack(args.output/'own-build-products.zip',products))
    query=''.join('HEAD:'+relative+'\n' for relative in sources).encode()
    blobs=subprocess.run(['git','cat-file','--batch'],cwd=ROOT,input=query,capture_output=True,check=True).stdout
    position=0;dependencies=[]
    for relative,path in sources.items():
        end=blobs.index(b'\n',position);header=blobs[position:end].split()
        if header[-1]==b'missing':prior=None;position=end+1
        else:
            assert header[1]==b'blob';size=int(header[2]);prior=hashlib.sha256(blobs[end+1:end+1+size]).hexdigest();position=end+size+2
        dependencies.append({'path':relative,'execution_sha256':sha(path),'parent_git_blob_sha256':prior})
    assert position==len(blobs)
    identity={'parent_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'execution_dependencies':dependencies,'source_freeze_sha256':sha(frozen),'finite_results_sha256':sha(finite/'results.json'),
        'rss_observation_sha256':sha(observation/'results.json'),'library_sha256':br['library_sha256'],'executable_sha256':br['executable_sha256'],
        'archive_script_sha256':sha(Path(__file__)),'all_member_sha256_passed':True,
        'member_counts':{'raw':len(raw),'source':len(sources),'build_metadata':len(metadata),'own_products':len(products)},
        'scope':'只101构建/机器码/唯一有限及RSS未采到原件；不重复旧native或新增整链/照片/性能。768B不是速度证据；16MiB不是RSS。synthetic输入由已冻结C++确定，无外部模型；外部MinGW依赖保留原路径/身份而不复制。'}
    save(args.output/'identity.json',identity);print(json.dumps({k:v for k,v in identity.items() if k!='execution_dependencies'},ensure_ascii=False))


if __name__=='__main__':main()
