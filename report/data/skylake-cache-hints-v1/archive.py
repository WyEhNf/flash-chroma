"""归档38—42的全部原始回执、失败验证、配对计数及二进制；不执行新计时。"""
from pathlib import Path
import hashlib,json,shutil,zipfile
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'report/data/skylake-cache-hints-v1';OUT.mkdir(exist_ok=False)
NAMES=['sourcehint','tablehint','batchspan','skew','wordload']
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
for source,name in [('skylake-pinned-openmp-v1','pinned-openmp'),('skylake-pmu-probe-v1','pmu-probe'),('skylake-host-space-v1','host-space'),('skylake-pmu-mapping-v1','pmu-mapping')]:shutil.copytree(ROOT/'artifacts'/source,OUT/name)
shutil.copyfile(Path(__file__).parent/'performance-audit.json',OUT/'performance-audit.json')
shutil.copyfile(Path(__file__).parent/'audit-before/check.json',OUT/'remote-check.json')
with zipfile.ZipFile(OUT/'remote-snapshot.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted((Path(__file__).parent/'audit-before').glob('*.json')):z.write(p,p.name)
with zipfile.ZipFile(OUT/'construction-and-validation-generators.zip','w',zipfile.ZIP_DEFLATED) as z:
    paths=[p for p in (ROOT/'artifacts').glob('*.py') if any(n in p.name for n in NAMES) or p.name=='prepare_cache_hints_delivery.py']
    paths.extend([Path(__file__).parent/'check_remote.py',Path(__file__).parent/'compare_refresh.py'])
    for p in sorted(set(paths)):z.write(p,p.relative_to(ROOT).as_posix())
shutil.copyfile(__file__,OUT/'archive.py')
save(OUT/'input-reuse.json',{'model_bundle':'report/data/skylake-palette-v1/fixed-models.zip','large_streams':'按冻结计划同SHA恢复235MB照片、两个50MB完整域；不重复打包大输入','threefold_goal_completed':False,'skylake_measured':False,'baseline_revision':23,'base_commit':'acaf2b2fea95151a7b35e2d5158b6e236d2d47fd'})
save(OUT/'primary-sources.json',{'purpose':'所读一手技术来源和适用边界，启发假设，不把厂商示例当作本机或服务器成绩','sources':[{'url':'https://cdrdv2-public.intel.com/814198/248966-Optimization-Reference-Manual-V1-049.pdf','section':'15.16.4与图15-12','finding':'Skylake的硬件和软件gather取舍随局部性变化，不能从AMD本机结果推定普遍优胜；本轮保留原23作同场参考'},{'url':'https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/technical-documentation/gather-data-sampling.html','finding':'受影响平台的gather缓解会增加结果可消费延迟；本任务没有修改任何缓解或系统安全设置'},{'url':'https://man7.org/linux/man-pages/man2/perf_event_open.2.html','finding':'cache泛化事件的具体含义依CPU而异；本轮只报告原始generic事件和组运行比例，不标作L3实测'},{'url':'https://raw.githubusercontent.com/torvalds/linux/v6.18/arch/x86/events/amd/core.c','finding':'Zen4的generic cache编码与本机sysfs观察一致；未把虚拟机计数当作Skylake证据'},{'url':'https://www.kernel.org/doc/html/latest/admin-guide/mm/transhuge.html','finding':'只对本对象内存调用MADV_HUGEPAGE；从smaps核验实际大页覆盖，没有系统级配置变更'}]})
files={p.relative_to(OUT).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(OUT.rglob('*')) if p.is_file()}
save(OUT/'manifest.json',{'purpose':__doc__,'files':files,'self_included':False,'later_documents_included':False})
print('归档',len(files),'文件',sum(x['bytes'] for x in files.values()),'字节')
