"""封存copy4唯一质量/正式及单独synthetic预检，保留有效低50和自身AA失败。"""
import argparse
import hashlib
import io
from pathlib import Path
import subprocess
import zipfile
from study_memory_rom import ROOT,read,save,sha
PLAN_NAMES=('page-id16-copy4-runtime-v1.json','page-id16-copy4-performance-v1.json')

def package(path,items):
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as archive:
        for name,source in sorted(items.items()):archive.write(source,name)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quality',type=Path)
    parser.add_argument('--performance',type=Path)
    parser.add_argument('--synthetic',type=Path)
    parser.add_argument('--process-preflight',type=Path)
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
            if stream.read(1)!=b'\n':raise AssertionError('Git batch边界不同')
            info=manifest['files'].get(path.name)
            if raw!=path.read_bytes() or info and (len(raw)!=info['bytes'] or hashlib.sha256(raw).hexdigest()!=info['sha256']):raise AssertionError('发布暂存字节不同')
            if path.suffix=='.zip':
                with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                    if archive.testzip():raise AssertionError('ZIP CRC错误')
                    members+=len(archive.infolist())
        with zipfile.ZipFile(args.output/'frozen-source.zip') as archive:
            for plan in plans:
                if archive.read(plan.relative_to(ROOT).as_posix())!=plan.read_bytes():raise AssertionError('冻结计划ZIP不同')
                for name,value in read(plan)['source_sha256'].items():
                    if hashlib.sha256(archive.read(name)).hexdigest()!=value or sha(ROOT/name)!=value:raise AssertionError('冻结执行源ZIP不同')
            if hashlib.sha256(archive.read('scripts/preflight_page_id16_copy4_performance.py')).hexdigest()!=read(args.output/'synthetic-preflight.json')['source_sha256']:raise AssertionError('synthetic预检源码身份不同')
        with zipfile.ZipFile(args.output/'experiment-raw.zip') as archive:
            copies={'quality-audit.json':'quality/quality-audit.json','performance-summary.json':'performance/summary.json','publication-audit.json':'performance/publication-audit.json','synthetic-preflight.json':'preflight-synthetic/preflight.json','process-preflight.json':'process-preflight.json'}
            for published,member in copies.items():
                if archive.read(member)!=(args.output/published).read_bytes():raise AssertionError('原始副本不同')
        save(args.output/'git-byte-audit.json',dict(audit_passed=True,files=len(paths),zip_members=members,scope='暂存字节/CRC/冻结源与真实及synthetic分区原件核对；不重新运行native或补测。'))
        print(dict(audit_passed=True,files=len(paths),zip_members=members),flush=True)
        return
    if not all((args.quality,args.performance,args.synthetic,args.process_preflight)):raise ValueError('需要四份原件')
    args.output.mkdir(parents=True,exist_ok=False)
    items={}
    for prefix,directory in (('quality',args.quality),('performance',args.performance),('preflight-synthetic',args.synthetic)):
        for path in directory.rglob('*'):
            if path.is_file():items[prefix+'/'+path.relative_to(directory).as_posix()]=path
    items['process-preflight.json']=args.process_preflight
    package(args.output/'experiment-raw.zip',items)
    sources={}
    for plan in plans:
        sources[plan.relative_to(ROOT).as_posix()]=plan
        for name in read(plan)['source_sha256']:sources[name]=ROOT/name
    for name in ('scripts/preflight_page_id16_copy4_performance.py','scripts/audit_page_id16_copy4_publication.py','scripts/archive_page_id16_copy4.py','experiments/page-id16-copy4-portability-design-v1.md'):sources[name]=ROOT/name
    package(args.output/'frozen-source.zip',sources)
    for path,name in ((args.quality/'quality-audit.json','quality-audit.json'),(args.performance/'summary.json','performance-summary.json'),(args.performance/'publication-audit.json','publication-audit.json'),(args.synthetic/'preflight.json','synthetic-preflight.json'),(args.process_preflight,'process-preflight.json')):(args.output/name).write_bytes(path.read_bytes())
    save(args.output/'manifest.json',dict(purpose=__doc__,files={path.name:dict(bytes=path.stat().st_size,sha256=sha(path)) for path in args.output.iterdir()},references='原P4 ROM沿report/data/p16-page-id16-v1/experiment-raw.zip内quality/rom/page-id16.bin，SHA a953eef0…，不重复导出或复制。当前ZIP含新DLL/对象/依赖/实际机器码及全部真实1040调用/5RSS；preflight-synthetic明确是模拟整数，不是测量。移植方案仅静态，不含WASM运行证据。'))
    print(dict(output=str(args.output),files=len(list(args.output.iterdir())),bytes=sum(path.stat().st_size for path in args.output.iterdir())),flush=True)

if __name__=='__main__':main()
