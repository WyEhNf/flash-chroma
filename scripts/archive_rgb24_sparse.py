"""发布RGB24无损稀疏句柄的真实源、库、保护页/全域/性能原件。"""
import argparse
from pathlib import Path
import subprocess
from archive_compact_sparse import package
from study_memory_rom import ROOT,read,save,sha

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('build','finite','full','three','probe','perf','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args()
    for key in vars(a):setattr(a,key,getattr(a,key).resolve())
    a.output.mkdir(parents=True,exist_ok=False)
    inputs={'build.json':a.build/'build.json','finite.json':a.finite/'finite.json','full.json':a.full/'full.json','three-stage.json':a.three/'results.json','node-guard-probe.json':a.probe/'results.json','performance.json':a.perf/'summary.json'}
    for name,source in inputs.items():(a.output/name).write_bytes(source.read_bytes())
    plan=ROOT/'experiments/rgb24-sparse-v1.json';sources={n:ROOT/n for n in read(plan)['source_sha256']}
    for n in ('experiments/rgb24-sparse-v1.json','scripts/archive_rgb24_sparse.py','scripts/archive_compact_sparse.py','scripts/study_memory_rom.py','scripts/bench_memory_rom.py'):sources[n]=ROOT/n
    for source in a.build.glob('*.su'):sources['stack-usage/'+source.name]=source
    package(a.output/'measured-source.zip',sources)
    package(a.output/'new-library.zip',{n:a.build/n for n in ('jshc_compact_sparse.dll','rgb24_probe.dll','runtime.o','avx2.o')})
    package(a.output/'general-fixtures.zip',{x.name:x for x in a.finite.iterdir() if x.suffix in ('.slut','.bin')})
    package(a.output/'performance-raw.zip',{x.relative_to(a.perf).as_posix():x for x in a.perf.rglob('*.json') if x.name not in ('summary.json','partial.json')})
    for label,directory in (('finite',a.finite),('full',a.full)):
        driver=directory/'driver.json'
        if driver.is_file():(a.output/(label+'-driver.json')).write_bytes(driver.read_bytes())
    assembly=subprocess.check_output(['E:/mingw64/bin/objdump.exe','-d','-Mintel',str(a.build/'avx2.o')]);(a.output/'avx2-assembly.txt').write_bytes(assembly)
    save(a.output/'manifest.json',dict(purpose=__doc__,files={x.name:dict(bytes=x.stat().st_size,sha256=sha(x)) for x in a.output.iterdir() if x.is_file()},references='78/80/MinGW依赖在report/data/p16-memory-rom-v1/measured-libraries.zip；specialized在report/data/channel-runtime-specialized-v1/binaries-and-core.zip。原件SHA在build/performance中绑定；大照片/完整RGB域不上传。'))
    print(a.output)
if __name__=='__main__':main()
