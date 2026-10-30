"""归档精确ROM内存阶段的小型证据；不重复执行数值或性能，不上传照片或大ROM。"""
from pathlib import Path
import argparse
import json
import zipfile
from study_memory_rom import ROOT,sha,read,save

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--ref80',type=Path,required=True);a=p.parse_args();out=a.output;out.mkdir(parents=True,exist_ok=False)
    base=ROOT/'artifacts';specs={'build':base/'p16-memory-build-v2/build.json','export':base/'p16-memory-rom-v2/export.json','full':base/'p16-memory-verify-v2/results.json','contract':base/'p16-memory-contract-v1/results.json','performance':base/'p16-memory-perf-v1/summary.json'}
    files=[]
    for label,path in specs.items():
        target=out/(label+'.json');target.write_bytes(path.read_bytes());files.append(target)
    for path in sorted((base/'p16-memory-perf-v1').rglob('*.json')):
        target=out/'performance-raw'/path.relative_to(base/'p16-memory-perf-v1');target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes());files.append(target)
    build=read(specs['build']);sources={Path(x) for x in build['sources']}
    for directory in ('experiments/memory-rom','experiments/skylake-andn-split-runtime','experiments/channel-runtime'):
        sources.update(x for x in (ROOT/directory).rglob('*') if x.is_file())
    sources.update(ROOT/'scripts'/name for name in ('build_memory_rom.py','study_memory_rom.py','verify_memory_rom_contract.py','bench_memory_rom.py','archive_memory_rom.py'))
    # 依赖与实际生成源码同包，原静态核心由既有归档与SHA绑定。
    sourcezip=out/'measured-source.zip'
    with zipfile.ZipFile(sourcezip,'w',zipfile.ZIP_DEFLATED) as z:
        for path in sorted(sources):z.write(path,path.relative_to(ROOT).as_posix())
        for path in (base/'p16-memory-build-v2').glob('*.su'):z.write(path,path.relative_to(ROOT).as_posix())
    files.append(sourcezip)
    libraries=list((base/'p16-memory-build-v2').glob('*.dll'))+[a.ref80]
    with zipfile.ZipFile(out/'measured-libraries.zip','w',zipfile.ZIP_DEFLATED) as z:
        for path in libraries:z.write(path,path.name)
    files.append(out/'measured-libraries.zip')
    save(out/'manifest.json',dict(purpose=__doc__,files={p.relative_to(out).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in files},libraries={str(p):sha(p) for p in libraries},large_inputs='模型身份在export/build和固定既有计划；ROM可由a399四级重建，文件大小/SHA在export.json，照片不上传。'))
    print(json.dumps({'files':len(files),'bytes':sum(p.stat().st_size for p in files)},ensure_ascii=False))
if __name__=='__main__':main()
