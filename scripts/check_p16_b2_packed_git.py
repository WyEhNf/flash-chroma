"""99 index/HEAD逐blob SHA，属性/阶段正文按text归一LF，其余原字节。"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ref',choices=('index','HEAD'),required=True)
    p.add_argument('--receipt',required=True,type=Path);a=p.parse_args()
    if a.receipt.exists():raise FileExistsError('99 Git原字节审计不覆盖')
    sha=lambda raw:hashlib.sha256(raw).hexdigest()
    folder=ROOT/'report/data/p16-b2-packed-v1';identity=json.loads((folder/'identity.json').read_text(encoding='utf-8'))
    own=['.gitattributes','docs/stages/2026-10-24-p16-b2-packed-axis.md']
    for path in sorted((ROOT/'experiments').glob('p16-b2*')):
        own += [path.relative_to(ROOT).as_posix()] if path.is_file() else [p.relative_to(ROOT).as_posix() for p in sorted(path.rglob('*')) if p.is_file()]
    own += [p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'scripts').glob('*p16_b2*.py'))]
    own += [p.relative_to(ROOT).as_posix() for p in sorted(folder.rglob('*')) if p.is_file()]
    assert len(own)==len(set(own))
    text_paths=set(own[:2]);expected={}
    for path in own:
        raw=(ROOT/path).read_bytes();expected[path]=sha(raw.replace(b'\r\n',b'\n') if path in text_paths else raw)
    for row in identity['execution_dependencies']:
        value=row['execution_sha256'] if row['path'] in own else row['parent_git_blob_sha256']
        assert value is not None
        assert row['path'] not in expected or expected[row['path']]==value,row['path'];expected[row['path']]=value
    members=0
    for manifest,archive in (('raw-members.json','raw-evidence.zip'),('source-members.json','execution-and-post-sources.zip'),
            ('build-members.json','build-metadata.zip'),('product-members.json','own-build-products.zip'),('model-members.json','fixed-model-inputs.zip')):
        rows=json.loads((folder/manifest).read_text(encoding='utf-8'))
        with zipfile.ZipFile(folder/archive) as z:
            assert z.testzip() is None and len(z.namelist())==len(rows)
            for row in rows:assert sha(z.read(row['member']))==row['sha256'];members+=1
    prefix=':' if a.ref=='index' else 'HEAD:'
    out=subprocess.run(['git','cat-file','--batch'],cwd=ROOT,input=''.join(prefix+p+'\n' for p in expected).encode(),capture_output=True,check=True).stdout
    pos=0
    for path,value in expected.items():
        end=out.index(b'\n',pos);header=out[pos:end].split();assert len(header)==3 and header[1]==b'blob',path
        n=int(header[2]);assert sha(out[end+1:end+1+n])==value,path;pos=end+n+2
    assert pos==len(out)
    if a.ref=='index':
        staged=subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ROOT).decode().split('\0')
        assert set(staged)-{''}<=set(own),staged
    receipt={'ref':a.ref,'all_sha256_passed':True,'explicit_stage_whitelist_paths':len(own),
        'source_and_evidence_blobs':len(expected),'zip_members_verified':members,'text_normalization_only':sorted(text_paths),
        'checker_sha256':sha(Path(__file__).read_bytes()),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'expected':expected}
    a.receipt.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k!='expected'},ensure_ascii=False))


if __name__=='__main__':main()
