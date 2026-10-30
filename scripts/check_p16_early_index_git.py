"""101有限阶段增量Git blob/ZIP核对，非全历史或native重验。"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--ref',choices=('index','HEAD'),required=True);parser.add_argument('--receipt',type=Path,required=True);args=parser.parse_args()
    if args.receipt.exists():raise FileExistsError('101增量Git回执不覆盖')
    sha=lambda raw:hashlib.sha256(raw).hexdigest()
    folder=ROOT/'report/data/p16-early-index-finite-v1';identity=json.loads((folder/'identity.json').read_text(encoding='utf-8'))
    own=['.gitattributes','docs/stages/2026-10-24-p16-early-index-finite.md']
    for path in sorted((ROOT/'experiments').glob('p16-early-index*')):
        own+=[path.relative_to(ROOT).as_posix()] if path.is_file() else [p.relative_to(ROOT).as_posix() for p in sorted(path.rglob('*')) if p.is_file()]
    own+=[p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'scripts').glob('*p16_early_index*.py'))]
    own+=[p.relative_to(ROOT).as_posix() for p in sorted(folder.rglob('*')) if p.is_file()]
    assert len(own)==len(set(own));text_paths=set(own[:2]);expected={}
    for path in own:
        raw=(ROOT/path).read_bytes();expected[path]=sha(raw.replace(b'\r\n',b'\n') if path in text_paths else raw)
    for row in identity['execution_dependencies']:
        value=row['execution_sha256'] if row['path'] in own else row['parent_git_blob_sha256'];assert value is not None
        assert row['path'] not in expected or expected[row['path']]==value,row['path'];expected[row['path']]=value
    count=0
    for manifest,archive in (('raw-members.json','raw-evidence.zip'),('source-members.json','execution-and-post-sources.zip'),
            ('build-members.json','build-metadata.zip'),('product-members.json','own-build-products.zip')):
        rows=json.loads((folder/manifest).read_text(encoding='utf-8'))
        with zipfile.ZipFile(folder/archive) as zipped:
            assert zipped.testzip() is None and len(rows)==len(zipped.namelist())
            for row in rows:assert sha(zipped.read(row['member']))==row['sha256'];count+=1
    prefix=':' if args.ref=='index' else 'HEAD:'
    blobs=subprocess.run(['git','cat-file','--batch'],cwd=ROOT,input=''.join(prefix+p+'\n' for p in expected).encode(),capture_output=True,check=True).stdout
    position=0
    for path,value in expected.items():
        end=blobs.index(b'\n',position);header=blobs[position:end].split();assert len(header)==3 and header[1]==b'blob',path
        size=int(header[2]);assert sha(blobs[end+1:end+1+size])==value,path;position=end+size+2
    assert position==len(blobs)
    if args.ref=='index':
        staged=subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ROOT).decode().split('\0');assert set(staged)-{''}<=set(own),staged
    result={'ref':args.ref,'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'all_sha256_passed':True,
        'explicit_stage_whitelist_paths':len(own),'source_and_evidence_blobs':len(expected),'zip_members_verified':count,
        'text_normalization_only':sorted(text_paths),'checker_sha256':sha(Path(__file__).read_bytes()),'expected':expected}
    args.receipt.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='expected'},ensure_ascii=False))


if __name__=='__main__':main()
