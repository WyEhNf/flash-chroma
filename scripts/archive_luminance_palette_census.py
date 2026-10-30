"""只封存唯一亮度bank失败普查原件；不重读完整ROM或执行普查。"""
import argparse
from pathlib import Path
import shutil
from study_memory_rom import ROOT,read,save,sha

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);planpath=ROOT/'experiments/luminance-palette-census-v1.json';plan=read(planpath);source=ROOT/plan['output_path']
    for name in ('run.json','results.json','frequency-support.json','rgb-stream-check.json'):shutil.copyfile(source/name,a.output/name)
    paths=[ROOT/name for name in plan['source_sha256']]+[planpath,ROOT/'scripts/archive_luminance_palette_census.py',ROOT/'scripts/audit_luminance_palette_census.py',ROOT/'scripts/verify_luminance_palette_rgb_support.py']
    for path in paths:
        target=a.output/'sources'/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
    save(a.output/'manifest.json',dict(purpose=__doc__,files={path.relative_to(a.output).as_posix():dict(bytes=path.stat().st_size,sha256=sha(path)) for path in a.output.rglob('*') if path.is_file()},scope='无ROM/decoder/性能。核心设计/脚本在普查前冻结；发布器和离线审计随后编写，未改变冻结源。原M16D源ROM已在tag阶段exact-rom.zip归档。'))
    print(a.output)
if __name__=='__main__':main()
