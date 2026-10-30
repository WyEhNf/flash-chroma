"""只核查归档成员、代码语法和指标覆盖，不运行数值实验。"""
import ast,hashlib,json,zipfile
from pathlib import Path
P=Path(__file__).resolve().parents[1]
m=json.loads((P/'manifest.json').read_text(encoding='utf8'))
for path,h in m['published_files'].items():
    assert hashlib.sha256((P/path).read_bytes()).hexdigest()==h,path
with zipfile.ZipFile(P/'evidence.zip') as z:
    assert set(z.namelist())==set(m['members'])
    for name,r in m['members'].items():
        b=z.read(name);assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'],name
    def read(name):return json.loads(z.read('data/'+name))
    if m['stage']=='A':
        s=read('survey.json');v=read('validation.json')
        assert len(s)==136 and len(v)==26 and sum(x['cube_mismatch']==0 for x in v)==19
        assert len({(x['id'],x['m']) for x in s})==136
    else:
        c=read('chains.json');assert len(c)==6
        for x in c:
            for r in x['modes'].values():assert len(r['per_image'])==100 and len(r['batch_ms'])==5
            if x['matched_kinds']==[0,0,0,0]:assert x['modes']['matched']['output_sha256']==x['modes']['uniform_tetra']['output_sha256']
    orig=ast.parse(z.read('provenance/original-experiment.py').decode('utf8'))
    split=ast.parse((P/'code'/m['runner']).read_text(encoding='utf8'))
    for name in m['unchanged_functions']:
        a=next(n for n in orig.body if isinstance(n,ast.FunctionDef) and n.name==name)
        b=next(n for n in split.body if isinstance(n,ast.FunctionDef) and n.name==name)
        assert ast.dump(a)==ast.dump(b),name
for name in m['unchanged_top_level_loops']:
        a=next(n for n in orig.body if isinstance(n,ast.For) and isinstance(n.iter,ast.Name) and n.iter.id==name)
        b=next(n for n in split.body if isinstance(n,ast.For) and isinstance(n.iter,ast.Name) and n.iter.id==name)
        assert ast.dump(a)==ast.dump(b),name
for p in (P/'code').glob('*.py'):ast.parse(p.read_text(encoding='utf8'))
print('通过：归档成员及公开文件SHA、数值函数AST、代码语法和结果覆盖核查；未重跑精度/性能。')
