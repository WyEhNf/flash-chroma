"""核对本阶段暂存blob原字节、JSON/AST和新增文档本地链接，不执行候选。"""
from pathlib import Path
import ast
import hashlib
import json
import platform
import re
import subprocess
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def git(args,**kw):return subprocess.check_output(['git',*args],cwd=ROOT,**kw)
names=git(['diff','--cached','--name-only','-z']).decode('utf-8').split('\0')
names=[n for n in names if n and not n.endswith('/delivery-check.json')]
assert names and all('brick2' in n or n=='.gitattributes' for n in names)
frozen=[n for n in names if n!='.gitattributes' and not n.startswith('docs/')]
out=git(['cat-file','--batch'],input=''.join(':'+n+'\n' for n in frozen).encode('utf-8'))
offset=0;blobs=[]
for n in frozen:
    end=out.index(b'\n',offset);header=out[offset:end].decode('ascii').split();size=int(header[-1])
    blob=out[end+1:end+1+size];offset=end+size+2
    assert blob==(ROOT/n).read_bytes(),n
    blobs.append(dict(path=n,bytes=size,sha256=hashlib.sha256(blob).hexdigest()))
assert offset==len(out)
jsons=asts=links=0
for n in names:
    p=ROOT/n
    if p.suffix=='.json':json.loads(p.read_text(encoding='utf-8'));jsons+=1
    if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8'));asts+=1
    if p.suffix=='.md':
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            if target.startswith(('https:','http:','#')):continue
            assert (p.parent/target.split('#')[0]).exists(),(n,target)
            links+=1
git(['diff','--cached','--check'])
result=dict(passed=True,purpose=__doc__,environment=dict(platform=platform.platform(),python=sys.version),
    staged_files=len(names),frozen_blobs=blobs,json_files=jsons,ast_files=asts,local_links=links,
    exclusion='attrs和阶段文档按常规文本处理；delivery-check.json排除自引用，其余暂存原字节逐项一致',
    native_calls=0,performance_calls=0)
with (HERE/'delivery-check.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(dict(passed=True,staged_files=len(names),frozen_blobs=len(blobs),json_files=jsons,ast_files=asts,local_links=links),ensure_ascii=False))
