"""归档24—30完整原始回执及二进制/源快照；不包含大输入流，不执行新计时。"""
from pathlib import Path
import hashlib,json,shutil,zipfile
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'report/data/skylake-threefold-v1';OUT.mkdir(exist_ok=False)
names=['direct16','byteindex','paged32','pageindex','fused16','load16','tileindex']
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for directory in sorted((ROOT/'artifacts').iterdir()):
    if not directory.is_dir() or not any(directory.name.startswith('skylake-'+name+'-') for name in names):continue
    target=OUT/directory.name;target.mkdir()
    for p in directory.iterdir():
        if p.is_file() and p.suffix in ('.json','.zip','.log','.asm','.txt'):
            if p.stat().st_size>10*2**20:raise ValueError('意外大成员：'+str(p))
            shutil.copyfile(p,target/p.name)
    if (directory/'build.json').exists():
        build=read(directory/'build.json');binary_index={}
        with zipfile.ZipFile(target/'binaries-and-objects.zip','w',zipfile.ZIP_DEFLATED) as z:
            paths=[p for p in directory.rglob('*') if p.is_file() and p.suffix in ('.o','.obj')]
            for role,spec in build['libraries'].items():paths.append(directory/Path(spec['path'].replace('\\','/')).name)
            for p in sorted(set(paths)):
                key=p.relative_to(directory).as_posix();z.write(p,key);binary_index[key]={'bytes':p.stat().st_size,'sha256':sha(p)}
        save(target/'binary-index.json',binary_index)
for src,dirname in [('skylake-tile-locality-v1','tile-locality'),('skylake-threefold-profile-v1','structure-profile')]:
    shutil.copytree(ROOT/'artifacts'/src,OUT/dirname)
shutil.copyfile(ROOT/'artifacts/skylake-large-pages-readonly-v1.json',OUT/'windows-large-pages-readonly.json')
shutil.copyfile(Path(__file__).parent/'performance-audit-final.json',OUT/'performance-audit.json')
shutil.copyfile(Path(__file__).parent/'audit-before/check.json',OUT/'remote-check.json')
with zipfile.ZipFile(OUT/'remote-snapshot.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted((Path(__file__).parent/'audit-before').glob('*.json')):z.write(p,p.name)
with zipfile.ZipFile(OUT/'construction-and-validation-generators.zip','w',zipfile.ZIP_DEFLATED) as z:
    paths=[p for p in (ROOT/'artifacts').glob('*.py') if any(n in p.name for n in names) or p.name in ('profile_threefold_structure.py','profile_tile_locality.py','probe_large_pages_readonly.py')]
    paths += [Path(__file__).parent/'check_remote.py']
    for p in sorted(paths):z.write(p,p.relative_to(ROOT).as_posix())
shutil.copyfile(__file__,OUT/'archive.py')
save(OUT/'input-reuse.json',{'model_bundle':'report/data/skylake-palette-v1/fixed-models.zip','large_streams':'按实验计划同SHA恢复235MB照片流、两个50MB完整域流；本目录未打包大流','threefold_goal_completed':False,'skylake_measured':False,'baseline_revision':23,'base_commit':'83554020bee6b3313292d40d41d8f3a29b8b87de'})
files={p.relative_to(OUT).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(OUT.rglob('*')) if p.is_file()}
save(OUT/'manifest.json',{'purpose':__doc__,'files':files,'self_included':False,'later_documents_included':False})
print('归档',len(files),'文件',sum(s['bytes'] for s in files.values()),'字节')
