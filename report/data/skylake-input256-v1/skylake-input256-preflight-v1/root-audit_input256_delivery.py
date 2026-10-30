"""只读核对81冻结源、档案原件和暂存Git blob，不执行原生。"""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
ARCH=ROOT/'report/data/skylake-input256-v1'
def sha(data):return hashlib.sha256(data).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))

def main():
    manifest=read(ARCH/'manifest.json')
    for name,spec in manifest['files'].items():
        data=(ARCH/name).read_bytes();assert len(data)==spec['bytes'] and sha(data)==spec['sha256'],name
    plan=read(ROOT/'experiments/skylake-input256-v1.json')
    for name,value in plan['source_sha256'].items():assert sha((ROOT/name).read_bytes())==value,name
    names=subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ROOT).decode('utf-8').split('\0')[:-1]
    frozen=[n for n in names if n.startswith(('experiments/skylake-input256','scripts/verify_skylake_input256','scripts/bench_skylake_input256','report/data/skylake-input256-v1/')) and not n.endswith('/delivery-audit.json')]
    assert frozen
    proc=subprocess.run(['git','cat-file','--batch'],input=''.join(':'+n+'\n' for n in frozen).encode(),stdout=subprocess.PIPE,check=True,cwd=ROOT)
    data=proc.stdout;cursor=0
    for name in frozen:
        end=data.index(b'\n',cursor);header=data[cursor:end].split();assert header[1]==b'blob',name
        size=int(header[2]);begin=end+1;blob=data[begin:begin+size];cursor=begin+size+1
        assert blob==(ROOT/name).read_bytes(),name
    assert cursor==len(data)
    syntax=[]
    for name in frozen:
        if name.endswith('.py'):
            ast.parse((ROOT/name).read_text(encoding='utf-8'));syntax.append(name)
    result={'purpose':__doc__,'pass_check':True,'manifest_files':len(manifest['files']),'source_entries':len(plan['source_sha256']),
        'frozen_blob_files':len(frozen),'syntax_files':syntax,'candidate_library_loads':0,'pixel_calls':0,'performance_calls':0,
        'scope':'delivery-audit.json本结果自身不参与自引用，其他本阶段暂存冻结文件逐字节等工作区；文档及属性由git diff --cached --check另验。'}
    with (ARCH/'delivery-audit.json').open('w',encoding='utf-8') as stream:json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
