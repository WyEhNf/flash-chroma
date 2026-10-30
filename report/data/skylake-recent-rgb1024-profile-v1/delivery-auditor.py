"""验证已暂存档案原字节和ZIP成员身份；不运行命中分析或性能。"""
from pathlib import Path
import ast
import hashlib
import json
import subprocess
import zipfile
ROOT=Path(__file__).resolve().parents[1]
prefix='report/data/skylake-recent-rgb1024-profile-v1/'
paths=[x for x in subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ROOT).decode().split('\0') if x.startswith(prefix)]
assert paths
data=subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=b''.join((':'+x+'\n').encode() for x in paths))
offset=0; hashes={}
for path in paths:
    end=data.index(b'\n',offset);size=int(data[offset:end].split()[2]);offset=end+1
    raw=data[offset:offset+size];offset+=size+1
    assert raw==(ROOT/path).read_bytes(),path
    hashes[path]=hashlib.sha256(raw).hexdigest()
    if path.endswith('.py'):ast.parse(raw)
    if path.endswith('.json'):json.loads(raw)
assert offset==len(data)
base=ROOT/prefix
manifest=json.loads((base/'manifest.json').read_text(encoding='utf-8'))
assert hashlib.sha256((base/'evidence.zip').read_bytes()).hexdigest()==manifest['archive_sha256']
with zipfile.ZipFile(base/'evidence.zip') as archive:
    assert archive.testzip() is None
out=ROOT/'artifacts/skylake-recent1024-delivery-v1.json'
with out.open('x',encoding='utf-8') as f:
    json.dump({'purpose':__doc__,'passed':True,'frozen_blobs':len(paths),'sha256':hashes,'scope':'后补交付脚本/回执排除自引用；文档/属性按Git常规文本处理。ZIP内容统计另见已执行标准库audit.json。'},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'frozen_blobs':len(paths),'passed':True}))
