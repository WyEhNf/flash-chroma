"""封存P4唯一质量、双阶段正式计时及实际模块观察；不重新运行算法。"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile
ROOT=Path(__file__).resolve().parents[1]
PLAN_NAMES=('page-id16-runtime-v1.json','page-id16-performance-v2.json','page-id16-module-observer-v1.json')

def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def read(path):return json.loads(path.read_text(encoding='utf-8'))

def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def package(path,items):
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as archive:
        for name,source in sorted(items.items()):archive.write(source,name)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quality',type=Path)
    parser.add_argument('--performance',type=Path)
    parser.add_argument('--modules',type=Path)
    parser.add_argument('--preflight',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--check-index',action='store_true')
    args=parser.parse_args()
    plans=[ROOT/'experiments'/name for name in PLAN_NAMES]
    if args.check_index:
        manifest=read(args.output/'manifest.json')
        paths=[args.output/name for name in manifest['files']]+[args.output/'manifest.json']
        payload='\n'.join(':'+path.resolve().relative_to(ROOT).as_posix() for path in paths)+'\n'
        stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],input=payload.encode(),cwd=ROOT))
        members=0
        for path in paths:
            header=stream.readline().split()
            if len(header)!=3:raise AssertionError('发布件未暂存')
            raw=stream.read(int(header[2]))
            if stream.read(1)!=b'\n':raise AssertionError('git batch边界不同')
            info=manifest['files'].get(path.name)
            if raw!=path.read_bytes() or info and (len(raw)!=info['bytes'] or hashlib.sha256(raw).hexdigest()!=info['sha256']):raise AssertionError('暂存字节/SHA不同')
            if path.suffix=='.zip':
                with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                    if archive.testzip():raise AssertionError('ZIP CRC错误')
                    members+=len(archive.infolist())
        with zipfile.ZipFile(args.output/'frozen-source.zip') as archive:
            for plan in plans:
                if archive.read(plan.relative_to(ROOT).as_posix())!=plan.read_bytes():raise AssertionError('冻结计划ZIP字节不同')
                for name,value in read(plan)['source_sha256'].items():
                    if hashlib.sha256(archive.read(name)).hexdigest()!=value or sha(ROOT/name)!=value:raise AssertionError('执行源ZIP字节不同')
        with zipfile.ZipFile(args.output/'experiment-raw.zip') as archive:
            originals={'quality-audit.json':'quality/quality-audit.json','performance-summary.json':'performance/summary.json','publication-audit.json':'performance/publication-audit.json','module-observation.json':'modules/results.json','process-preflight.json':'preflight.json'}
            for published,member in originals.items():
                if archive.read(member)!=(args.output/published).read_bytes():raise AssertionError('发布副本与raw不同')
        save(args.output/'git-byte-audit.json',dict(audit_passed=True,files=len(paths),zip_members=members,scope='暂存字节/CRC与冻结源/计划/原始副本一致；不重执行质量/性能。'))
        print(dict(audit_passed=True,files=len(paths),zip_members=members))
        return
    if not all((args.quality,args.performance,args.modules,args.preflight)):raise ValueError('需要完整四份原始输入')
    args.output.mkdir(parents=True,exist_ok=False)
    items={}
    for prefix,directory in (('quality',args.quality),('performance',args.performance),('modules',args.modules)):
        for path in directory.rglob('*'):
            if path.is_file():items[prefix+'/'+path.relative_to(directory).as_posix()]=path
    items['preflight.json']=args.preflight
    package(args.output/'experiment-raw.zip',items)
    sources={}
    for plan in plans:
        sources[plan.relative_to(ROOT).as_posix()]=plan
        for name in read(plan)['source_sha256']:sources[name]=ROOT/name
    for path in (ROOT/'scripts/audit_page_id16_publication.py',Path(__file__).resolve()):sources[path.relative_to(ROOT).as_posix()]=path
    package(args.output/'frozen-source.zip',sources)
    for path,name in ((args.quality/'quality-audit.json','quality-audit.json'),(args.performance/'summary.json','performance-summary.json'),(args.performance/'publication-audit.json','publication-audit.json'),(args.modules/'results.json','module-observation.json'),(args.preflight,'process-preflight.json')):(args.output/name).write_bytes(path.read_bytes())
    save(args.output/'manifest.json',dict(purpose=__doc__,files={path.name:dict(bytes=path.stat().st_size,sha256=sha(path)) for path in args.output.iterdir()},references='三份冻结协议、v1未执行草稿、全部1232调用/960timed、6RSS、独立审计、P4实际ROM和主/独立C99 DLL及四依赖/对象/栈随ZIP保留。原78/80和linear DLL、五模型、照片只以冻结SHA引用，不复制235MB照片；单fresh模块观察不能冒称全部RSS实际加载同目录。'))
    print(dict(output=str(args.output),files=len(list(args.output.iterdir())),bytes=sum(path.stat().st_size for path in args.output.iterdir())))

if __name__=='__main__':main()
