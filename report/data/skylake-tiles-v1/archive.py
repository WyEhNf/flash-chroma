"""归档47/49分块研究和48未执行草案，保留静态误报与全部计数证据；不执行新计时。"""
from pathlib import Path
import hashlib,json,shutil,zipfile
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'report/data/skylake-tiles-v1';OUT.mkdir(exist_ok=False)
NAMES=['tilebmi2','tilevector','tilemadd']
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for directory in sorted((ROOT/'artifacts').iterdir()):
    if not directory.is_dir() or not any(directory.name.startswith('skylake-'+name+'-') for name in NAMES):continue
    target=OUT/directory.name;target.mkdir()
    for p in directory.iterdir():
        if p.is_file() and p.suffix in ('.json','.zip','.log','.asm','.txt'):
            if p.stat().st_size>10*2**20:raise ValueError('意外大成员：'+str(p))
            shutil.copyfile(p,target/p.name)
    if (directory/'build.json').exists():
        build=read(directory/'build.json');index={}
        with zipfile.ZipFile(target/'binaries-and-objects.zip','w',zipfile.ZIP_DEFLATED) as z:
            paths=[p for p in directory.rglob('*') if p.is_file() and p.suffix in ('.o','.obj')]
            paths.extend(directory/Path(s['path'].replace('\\','/')).name for s in build['libraries'].values())
            for p in sorted(set(paths)):
                key=p.relative_to(directory).as_posix();z.write(p,key);index[key]={'bytes':p.stat().st_size,'sha256':sha(p)}
        save(target/'binary-index.json',index)
shutil.copyfile(Path(__file__).parent/'research-audit.json',OUT/'research-audit.json')
shutil.copyfile(Path(__file__).parent/'audit-before/check.json',OUT/'remote-check.json')
with zipfile.ZipFile(OUT/'remote-snapshot.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted((Path(__file__).parent/'audit-before').glob('*.json')):z.write(p,p.name)
with zipfile.ZipFile(OUT/'construction-and-validation-generators.zip','w',zipfile.ZIP_DEFLATED) as z:
    paths=[p for p in (ROOT/'artifacts').glob('*.py') if any(n in p.name for n in NAMES) ]
    paths.extend([Path(__file__).parent/'check_remote.py',Path(__file__).parent/'compare_refresh.py'])
    for p in sorted(set(paths)):z.write(p,p.relative_to(ROOT).as_posix())
shutil.copyfile(__file__,OUT/'archive.py')
save(OUT/'input-reuse.json',{'model_bundle':'report/data/skylake-palette-v1/fixed-models.zip','large_streams':'按冻结计划同SHA恢复235MB照片、两个50MB完整域；不重复打包大输入','threefold_goal_completed':False,'skylake_measured':False,'baseline_revision':23,'base_commit':'07c6e16e2adbd10c02172898c0ab7fce99b92ad9','reference40_archive':'report/data/skylake-inplace-path-v1/skylake-batchspan-linux-build-v1','unexecuted_revision':48,'full_wallclock_performance_calls':0})
save(OUT/'primary-sources.json',{'purpose':'一手来源支持可选BMI2和运行时分派；不把厂商说明当作性能证据','sources':[{'url':u} for u in ['https://www.intel.com/content/www/us/en/support/articles/000102715/processors/intel-xeon-processors.html','https://gcc.gnu.org/onlinedocs/gcc-11.2.0/gcc/x86-Built-in-Functions.html','https://cdrdv2-public.intel.com/814198/248966-Optimization-Reference-Manual-V1-049.pdf']]})
files={p.relative_to(OUT).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(OUT.rglob('*')) if p.is_file()}
save(OUT/'manifest.json',{'purpose':__doc__,'files':files,'self_included':False,'later_documents_included':False})
print('归档',len(files),'文件',sum(x['bytes'] for x in files.values()),'字节')
