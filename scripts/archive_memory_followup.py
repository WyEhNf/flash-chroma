"""归档ROM后续阶段的实际源、库、全域合同与性能原件，不重跑测量。"""
import argparse
from pathlib import Path
import zipfile
from study_memory_rom import ROOT,sha,read,save

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('build','full','contract','perf','plan','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    for name in ('build','full','contract','perf','plan','output'):setattr(a,name,getattr(a,name).resolve())
    out=a.output;out.mkdir(parents=True,exist_ok=False)
    specs={'build.json':a.build/'build.json','full.json':a.full/'results.json','contract.json':a.contract/'results.json','performance.json':a.perf/'summary.json'}
    for name,path in specs.items():(out/name).write_bytes(path.read_bytes())
    driver=a.full.parent/'driver.json'
    if driver.is_file():(out/'verification-driver.json').write_bytes(driver.read_bytes())
    sources={Path(n).resolve() for n in read(specs['build.json'])['sources']}
    sources.update(ROOT/n for n in read(a.plan)['source_sha256']);sources.add(a.plan.resolve())
    sources.update(ROOT/'scripts'/n for n in ('study_memory_rom.py','verify_memory_rom_contract.py','archive_memory_followup.py'))
    with zipfile.ZipFile(out/'measured-source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for path in sorted(sources):z.write(path,path.relative_to(ROOT).as_posix())
        for path in a.build.glob('*.su'):z.write(path,path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(out/'new-libraries.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in ('jshc_memory_rom.dll','jshc_memory_c99.dll'):z.write(a.build/name,name)
    with zipfile.ZipFile(out/'performance-raw.zip','w',zipfile.ZIP_DEFLATED) as z:
        for path in sorted(a.perf.rglob('*.json')):
            if path.name not in ('partial.json','summary.json'):z.write(path,path.relative_to(a.perf).as_posix())
    save(out/'acceptance.json',dict(control=read(specs['performance.json'])['controls'],scope='A/A未通过的运行情形只能保留原始观察，禁止用其档位更新正式优选。'))
    save(out/'manifest.json',dict(purpose=__doc__,files={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in out.iterdir() if p.is_file()},scope='后补README及阶段说明不纳入原始清单；参考78/80及依赖沿用首阶段已测库；大ROM/照片不上传。'))
    print(out)
if __name__=='__main__':main()
