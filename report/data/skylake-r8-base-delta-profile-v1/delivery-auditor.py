"""核对已暂存冻结副本、语法及两份归档清单；不运行原分析。"""
from pathlib import Path
import ast
import json
import hashlib
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
paths=subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ROOT).decode().split('\0')
paths=[p for p in paths if p.startswith('report/data/skylake-r8-base-delta-profile-v1/') or p.startswith('report/data/skylake-xor-chroma-profile-v1/')]
assert paths
process=subprocess.run(['git','cat-file','--batch'],cwd=ROOT,input=b''.join((':'+p+'\n').encode() for p in paths),stdout=subprocess.PIPE,check=True)
data=process.stdout;offset=0;hashes={}
for p in paths:
    end=data.index(b'\n',offset)
    header=data[offset:end].split();size=int(header[2]);offset=end+1
    blob=data[offset:offset+size];offset+=size+1
    assert blob==(ROOT/p).read_bytes(),p
    hashes[p]=hashlib.sha256(blob).hexdigest()
    if p.endswith('.py'):ast.parse(blob)
    if p.endswith('.json'):json.loads(blob)
assert offset==len(data)
for directory in ['skylake-r8-base-delta-profile-v1','skylake-xor-chroma-profile-v1']:
    base=ROOT/'report/data'/directory
    manifest=json.loads((base/'manifest.json').read_text(encoding='utf-8'))
    for item in manifest['files']:
        archive=base/item['archive'];original=ROOT/item['source']
        assert archive.read_bytes()==original.read_bytes()
        assert hashlib.sha256(archive.read_bytes()).hexdigest()==item['sha256']
        assert archive.stat().st_size==item['bytes']
out=ROOT/'artifacts/skylake-screen-delivery-20261023.json'
with out.open('x',encoding='utf-8') as f:
    json.dump({'purpose':__doc__,'pass':True,'files':len(paths),'python':sys.version,'frozen_blob_sha256':hashes,'limits':'阶段文档/.gitattributes采用Git常规文本规范；不计入冻结字节。该交付结果位于artifacts，不自引用，也不是新精度或性能测试。'},f,ensure_ascii=False,indent=2)
    f.write('\n')
print(json.dumps({'frozen_blobs':len(paths),'pass':True},ensure_ascii=False))
