"""静态核对暂存Git字节、冻结源、中文报告链接；不调用像素或性能入口。"""
from pathlib import Path
import ast,hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[2]
def git(*a,**kw):return subprocess.run(['git',*a],cwd=ROOT,check=True,capture_output=True,**kw).stdout
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
names=git('diff','--cached','6753b12','--name-only','--diff-filter=A').decode().splitlines();checked=[n for n in names if n.startswith(('experiments/','scripts/','report/data/'))]
raw=git('cat-file','--batch',input=''.join(':'+n+'\n' for n in checked).encode());cursor=0
for name in checked:
    end=raw.index(b'\n',cursor);header=raw[cursor:end].split();assert header[1]==b'blob';size=int(header[2]);start=end+1
    assert hashlib.sha256(raw[start:start+size]).hexdigest()==sha(ROOT/name),name;cursor=start+size+1
assert cursor==len(raw);syntax=0;sources=set();links=0
for name in names:
    if name.endswith('.py'):ast.parse((ROOT/name).read_text(encoding='utf-8-sig'),name);syntax+=1
for name in ('sparsehint','qwordpack','splitpack'):
    p=json.loads((ROOT/f'experiments/skylake-{name}-v{2 if name=="sparsehint" else 1}.json').read_text(encoding='utf-8'))
    for n,digest in p['source_sha256'].items():assert sha(ROOT/n)==digest,n;sources.add(n)
for name in ('docs/stages/2026-10-21-skylake-output-path.md','report/data/skylake-output-path-v1/README.md'):
    path=ROOT/name
    for target in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
        if '://' not in target:assert (path.parent/target.split('#')[0]).exists(),target;links+=1
for relative,script in [(f'skylake-{n}-linux-static-v1',f'inspect_skylake_{n}{"_v2" if n=="qwordpack" else ""}.py') for n in ('sparsehint','qwordpack','splitpack')]:
    assert json.loads((ROOT/'artifacts'/relative/'results.json').read_text(encoding='utf-8'))['script_sha256']==sha(ROOT/'scripts'/script)
assert not git('diff','HEAD','--','AGENTS.md','experiments/skylake-exception-runtime')
subprocess.run(['git','diff','--cached','--check'],cwd=ROOT,check=True)
result={'pass':True,'purpose':__doc__,'new_python_ast':syntax,'index_byte_matches':len(checked),'frozen_runtime_sources':len(sources),'local_document_links':links,'scope':'相对6753b12的全部阶段新增Git blob；冻结源保持测量字节','new_native_calls':0,'new_performance_calls':0}
import sys
output=ROOT/sys.argv[1]
assert not output.exists()
output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(result)
