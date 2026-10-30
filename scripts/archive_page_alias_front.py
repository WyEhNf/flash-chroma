"""封存页别名前置三fresh及三次STOP证据，不重执行。"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile
ROOT=Path(__file__).resolve().parents[1]
def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def package(path,items):
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as archive:
        for name,source in sorted(items.items()):archive.write(source,name)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--front',type=Path);p.add_argument('--handles',type=Path);p.add_argument('--metadata',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--check-index',action='store_true');a=p.parse_args();plans=[ROOT/'experiments'/name for name in ('page-alias-runtime-v1.json','page-alias-handle-observer-v1.json','page-alias-metadata-observer-v1.json')]
    if a.check_index:
        manifest=read(a.output/'manifest.json');paths=[a.output/name for name in manifest['files']]+[a.output/'manifest.json'];payload='\n'.join(':'+path.resolve().relative_to(ROOT).as_posix() for path in paths)+'\n';stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],input=payload.encode(),cwd=ROOT));members=0
        for path in paths:
            header=stream.readline().split()
            if len(header)!=3:raise AssertionError('发布件未暂存')
            raw=stream.read(int(header[2]));assert stream.read(1)==b'\n';info=manifest['files'].get(path.name)
            if raw!=path.read_bytes() or info and (len(raw)!=info['bytes'] or hashlib.sha256(raw).hexdigest()!=info['sha256']):raise AssertionError('暂存原字节不同')
            if path.suffix=='.zip':
                with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                    if archive.testzip():raise AssertionError('ZIP CRC错误')
                    members+=len(archive.infolist())
        with zipfile.ZipFile(a.output/'frozen-source.zip') as archive:
            for plan in plans:
                if archive.read(plan.relative_to(ROOT).as_posix())!=plan.read_bytes():raise AssertionError('冻结计划不同')
                for name,value in read(plan)['source_sha256'].items():
                    if hashlib.sha256(archive.read(name)).hexdigest()!=value or sha(ROOT/name)!=value:raise AssertionError('冻结执行源不同')
        with zipfile.ZipFile(a.output/'front-raw.zip') as archive:
            if archive.read('front/run.json')!=(a.output/'front-run.json').read_bytes() or archive.read('front/contracts/failure.json')!=(a.output/'front-failure.json').read_bytes() or archive.read('handles/results.json')!=(a.output/'handles-result.json').read_bytes() or archive.read('metadata/results.json')!=(a.output/'metadata-result.json').read_bytes():raise AssertionError('发布原件副本不同')
        save(a.output/'git-byte-audit.json',dict(audit_passed=True,front_gate_passed=False,files=len(paths),zip_members=members,scope='暂存字节/CRC及冻结计划一致；原实验保持STOP，没有新运行。'));print(dict(audit_passed=True,files=len(paths),zip_members=members));return
    if not all((a.front,a.handles,a.metadata)):raise ValueError('需要全部原始目录')
    a.output.mkdir(parents=True,exist_ok=False);items={}
    for name,directory in (('front',a.front),('handles',a.handles),('metadata',a.metadata)):
        for path in directory.rglob('*'):
            if path.is_file() and path.name!='offline-audit.json':items[name+'/'+path.relative_to(directory).as_posix()]=path
    package(a.output/'front-raw.zip',items);sources={}
    for path in plans:
        sources[path.relative_to(ROOT).as_posix()]=path
        for name in read(path)['source_sha256']:sources[name]=ROOT/name
    for path in (ROOT/'scripts/audit_page_alias_front.py',Path(__file__).resolve()):sources[path.relative_to(ROOT).as_posix()]=path
    package(a.output/'frozen-source.zip',sources)
    for source,name in ((a.front/'run.json','front-run.json'),(a.front/'contracts/failure.json','front-failure.json'),(a.handles/'results.json','handles-result.json'),(a.metadata/'results.json','metadata-result.json'),(a.front/'offline-audit.json','offline-audit.json')):(a.output/name).write_bytes(source.read_bytes())
    save(a.output/'manifest.json',dict(purpose=__doc__,files={path.name:dict(bytes=path.stat().st_size,sha256=sha(path)) for path in a.output.iterdir()},references='原DLL/模型不改；两个实际backing容器随rawZIP保留；没有照片/gold/完整像素域或性能。三个STOP与所有source/CSV/binary/closed-reader原件并列，不恢复资格。'))
    print(dict(output=str(a.output),files=len(list(a.output.iterdir())),bytes=sum(path.stat().st_size for path in a.output.iterdir())))
if __name__=='__main__':main()
