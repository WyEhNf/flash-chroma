"""核对两格式归档暂存字节、语法、ZIP整体身份与CRC；不执行profile。"""
from pathlib import Path
import ast, hashlib, json, subprocess, zipfile
ROOT=Path(__file__).resolve().parents[1]
prefixes=['report/data/skylake-brick2-rgb-base-profile-v1/','report/data/skylake-brick2-header15-profile-v1/']
paths=[x for x in subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ROOT).decode().split('\0') if any(x.startswith(p) for p in prefixes)]
assert paths
data=subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=b''.join((':'+x+'\n').encode() for x in paths))
offset=0;hashes={}
for path in paths:
    end=data.index(b'\n',offset);size=int(data[offset:end].split()[2]);offset=end+1
    raw=data[offset:offset+size];offset+=size+1
    assert raw==(ROOT/path).read_bytes(),path
    hashes[path]=hashlib.sha256(raw).hexdigest()
    if path.endswith('.py'):ast.parse(raw)
    if path.endswith('.json'):json.loads(raw)
assert offset==len(data)
for p in prefixes:
    base=ROOT/p;m=json.loads((base/'manifest.json').read_text(encoding='utf-8'))
    assert hashlib.sha256((base/'evidence.zip').read_bytes()).hexdigest()==m['archive_sha256']
    for z in base.glob('*.zip'):
        with zipfile.ZipFile(z) as archive:assert archive.testzip() is None
out=ROOT/'artifacts/skylake-brickrgb-delivery-v1.json'
with out.open('x',encoding='utf-8') as f:
    json.dump({'purpose':__doc__,'passed':True,'frozen_blobs':len(paths),'sha256':hashes,'scope':'独立统计审计已另执行；后补交付回执/协作终刷排除自引用，stage/属性沿Git文本规则。不是精度或性能测试。'},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'passed':True,'frozen_blobs':len(paths)}))
