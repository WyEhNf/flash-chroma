"""发布唯一4KiB普查原件并核暂存字节/CRC；不重普查、不部署。"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def package(path,items):
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as archive:
        for name,source in sorted(items.items()):archive.write(source,name)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--check-index',action='store_true');a=p.parse_args();plan_path=ROOT/'experiments/page-alias-census-v1.json';plan=read(plan_path)
    if a.check_index:
        manifest=read(a.output/'manifest.json');paths=[a.output/name for name in manifest['files']]+[a.output/'manifest.json'];names=[path.relative_to(ROOT).as_posix() for path in (p.resolve() for p in paths)];stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(':'+name for name in names)+'\n').encode(),cwd=ROOT));members=0
        for name,path in zip(names,paths,strict=True):
            header=stream.readline().split()
            if len(header)!=3:raise AssertionError('发布件未暂存')
            raw=stream.read(int(header[2]));assert stream.read(1)==b'\n';info=manifest['files'].get(path.name)
            if raw!=path.read_bytes() or (info and (len(raw)!=info['bytes'] or sha(path)!=info['sha256'])):raise AssertionError('发布字节不同')
            if path.suffix=='.zip':
                with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                    if archive.testzip():raise AssertionError('ZIP CRC不同')
                    members+=len(archive.infolist())
        with zipfile.ZipFile(a.output/'frozen-source.zip') as archive:
            for name,value in plan['source_sha256'].items():
                if hashlib.sha256(archive.read(name)).hexdigest()!=value or sha(ROOT/name)!=value:raise AssertionError('冻结源不同')
            if archive.read('experiments/page-alias-census-v1.json')!=plan_path.read_bytes():raise AssertionError('冻结计划不同')
        with zipfile.ZipFile(a.output/'census-raw.zip') as archive:
            if archive.read('results.json')!=(a.output/'census-summary.json').read_bytes() or archive.read('offline-audit.json')!=(a.output/'offline-audit.json').read_bytes():raise AssertionError('封存原件不同')
            result=json.loads(archive.read('results.json'));support=json.loads(archive.read('support.json'))
            if hashlib.sha256(archive.read('support.json')).hexdigest()!=result['support_sha256'] or result['plan_sha256']!=sha(plan_path):raise AssertionError('原始身份不同')
            counts=[0]*result['unique_pages']
            for identifier in support['page_ids']:counts[identifier]+=1
            if counts!=support['unique_page_references'] or sum(counts)!=4096 or result['projected_total_bytes']!=4096+16384+4096*len(counts)+48+1056 or result['net_backing_saving_bytes']!=16779328-result['projected_total_bytes'] or result['gate_pass']!=(result['net_backing_saving_bytes']>=1048576):raise AssertionError('静态重算容量/频数不同')
        save(a.output/'git-byte-audit.json',dict(passed=True,purpose=__doc__,files=len(paths),zip_members=members,plan_sha256=sha(plan_path),scope='已完成独立原byte重放另见offline-audit；这里不新开部署/普查/计时。'))
        print(dict(passed=True,files=len(paths),zip_members=members));return
    if not a.input:raise ValueError('需要原件目录')
    a.output.mkdir(parents=True,exist_ok=False)
    package(a.output/'census-raw.zip',{name:a.input/name for name in ('results.json','support.json','offline-audit.json')})
    sources={name:ROOT/name for name in plan['source_sha256']}
    for path in (plan_path,ROOT/'scripts/audit_page_alias_census.py',Path(__file__).resolve()):sources[path.relative_to(ROOT).as_posix()]=path
    package(a.output/'frozen-source.zip',sources)
    for source,target in (('results.json','census-summary.json'),('offline-audit.json','offline-audit.json')):(a.output/target).write_bytes((a.input/source).read_bytes())
    save(a.output/'manifest.json',dict(purpose=__doc__,files={path.name:dict(bytes=path.stat().st_size,sha256=sha(path)) for path in a.output.iterdir()},references='原linear M16D按146a5f28…复用首阶段ROM，不生成新backing/loader或上传照片；原字节重放已完成，unique backing投影不等实际物理RAM。'))
    print(a.output)
if __name__=='__main__':main()
