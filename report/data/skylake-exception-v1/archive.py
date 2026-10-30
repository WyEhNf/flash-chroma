"""只读保存23对22的单次研究证据；不重跑任何数值或性能。"""
from pathlib import Path
import json,hashlib,shutil,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'report/data/skylake-exception-v1'
OUT.mkdir(exist_ok=False)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def group(source,target,patterns=('*.json','*.zip','*.log','*.slut','*.bin')):
    dest=OUT/target;dest.mkdir()
    for p in (ROOT/'artifacts'/source).iterdir():
        if p.is_file() and any(p.match(x) for x in patterns):shutil.copyfile(p,dest/p.name)
for source,target in [
    ('base-contract-v1','base-contract'),('cache-contract-v1','cache-contract'),
    ('domain-contract-v1','domain-contract'),('packed-contract-v1','failed-packed-contract-v1'),
    ('packed-contract-v2','packed-contract'),('signed-contract-v1','signed-contract'),
    ('fallback-contract-v1','fallback-contract'),('full-v1','full'),('linux-full-v1','linux-full'),
    ('perf-v1','performance'),('audit-v1','audit')]:group('skylake-exception-'+source,target)
for suffix,label in [('build-v1','windows-build'),('linux-build-v1','linux-build')]:
    folder=ROOT/'artifacts'/('skylake-exception-'+suffix)
    group(folder.name,label,('build*.json','compile_commands.json','measured-source.zip','libraries-*.json'))
    with zipfile.ZipFile(OUT/label/'binaries-and-objects.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(folder.rglob('*')):
            if p.is_file() and p.suffix in ('.dll','.so','.o','.obj'):z.write(p,p.relative_to(folder).as_posix())
group('skylake-exception-static-v1','static',('*.json','*.asm'))
shutil.copyfile(ROOT/'artifacts/skylake-exception-reference22-object-proof.json',OUT/'reference22-object-proof.json')
shutil.copyfile(__file__,OUT/'archive.py')
with zipfile.ZipFile(OUT/'construction-and-validation-generators.zip','w',zipfile.ZIP_DEFLATED) as z:
    for name in ('setup_exception_runtime.py','setup_exception_validation.py','prepare_exception_measurement.py','setup_exception_audit.py'):
        z.write(ROOT/'artifacts'/name,name)
save(OUT/'failed-packed-contract-v1/failure.json',{'status':'failed','exception':'UnboundLocalError: cannot access local variable storage where it is not associated with a value',
    'cause':'验证器的局部哨兵数组storage遮蔽导入的容量函数；尚未开始独立解码比较',
    'repair':'仅将函数导入改名compiled_storage；C++、构建、模型不变；validation-v2固定新身份，完整packed-v2通过后才计时'})
folder=ROOT/'artifacts/skylake-exception-linux-build-v1';proof={}
for name in ('skylake-domain-isolated-runtime','skylake-suffix-cache-runtime'):
    paths=[p for p in folder.rglob('channel_avx2.cpp.o') if name in p.parts]
    assert len(paths)==2 and sha(paths[0])==sha(paths[1])
    proof[name]={'sha256':sha(paths[0]),'paths':[p.relative_to(folder).as_posix() for p in paths]}
save(OUT/'linux-fallback-object-proof.json',{'pass':True,'objects':proof,'scope':'各自同一新构建的旧回退对象完全相同；不替代新构造器资源与性能核验'})
remote=ROOT/'artifacts/skylake-exception-delivery-v1';previous=ROOT/'artifacts/skylake-palette-delivery-v1/pre-create'
changed=[]
for p in remote.glob('*.json'):
    if p.name not in ('repo.json','prs.json','issues.json','summary.json','graphql.json') and (previous/p.name).exists():
        if read(p)!=read(previous/p.name):changed.append(p.name)
assert not changed
a=read(remote/'graphql.json')['data']['repository'];b=read(previous/'graphql.json')['data']['repository']
assert all(a[k]==v for k,v in b.items())
assert not a['p45']['reviewThreads']['nodes']
ancestry={c:subprocess.run(['git','merge-base','--is-ancestor',c,'HEAD'],cwd=ROOT).returncode==0 for c in ('b19c5a0','337a3dd','876e15b8','397cc367','59586f7','860d6bf','e3975ea','b3d7f4c')}
assert all(ancestry.values())
prior_check=read(ROOT/'report/data/skylake-palette-v1/remote-check.json')
save(OUT/'remote-check.json',{'scope':'创建Draft前全量REST/GraphQL，相关正文、全部评论/review/行内与Discussion及修复祖先检查',
    'summary':read(remote/'summary.json'),'existing_opinion_changes':changed,'existing_graphql_changes':[],
    'new_pr45':{'head':'b3d7f4c70aed2a4e4b17a5ffd6ea7375f088dd53','state':'open','draft':True,'comments':0,'reviews':0,'review_threads':0},
    'included_commits':ancestry,'related':prior_check['related'],
    'unresolved':prior_check['unresolved'],'decision':'保持Draft、不合并；固定22为参考，不乘算旧16收益；没有新增未披露的相关阻塞意见',
    'redaction':'递归剔除API临时克隆元数据字段；正文、评论和数值保持'})
with zipfile.ZipFile(OUT/'remote-snapshot.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(remote.glob('*.json')):z.write(p,p.name)
    z.write(remote/'fetch_remote.py','fetch_remote.py')
save(OUT/'input-reuse.json',{'fixed_model_archive':'report/data/skylake-palette-v1/fixed-models.zip',
    'large_input_identity':'report/data/skylake-palette-v1/large-input-identities.json',
    'scope':'与22相同四模型、照片及独立完整oracle；未复制大流或改变来源'})
save(OUT/'manifest.json',{'purpose':__doc__,'files':{p.relative_to(OUT).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(OUT.rglob('*')) if p.is_file()}})
print('归档',len(read(OUT/'manifest.json')['files']),'文件；字节',sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file()))
