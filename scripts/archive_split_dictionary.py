"""封存M16S分平面精确布局、七角色原始轮次与同容量配对证据。"""
import argparse
from pathlib import Path
import statistics
from archive_compact_sparse import package
from study_memory_rom import ROOT,sha,read,save

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('build','roms','verify','perf','rss','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args()
    for key in vars(a):setattr(a,key,getattr(a,key).resolve())
    a.output.mkdir(parents=True,exist_ok=False);path=ROOT/'experiments/split-dictionary-v1.json';plan=read(path)
    for name,source in {'build.json':a.build/'build.json','export.json':a.roms/'export.json','quality.json':a.verify/'results.json','performance.json':a.perf/'summary.json','benchmark-driver.json':a.perf/'driver.json','stream-rss.json':a.rss/'summary.json'}.items():(a.output/name).write_bytes(source.read_bytes())
    sources={n:ROOT/n for n in plan['source_sha256']}
    for item in (path,ROOT/'scripts/archive_split_dictionary.py',ROOT/'scripts/archive_compact_sparse.py',ROOT/'scripts/rss_split_dictionary.py',ROOT/'experiments/split-dictionary-rss-v1.json',ROOT/'experiments/compact-dictionary-v1.json'):sources[item.relative_to(ROOT).as_posix()]=item
    for item in a.build.glob('*.su'):sources['stack-usage/'+item.name]=item
    package(a.output/'measured-source.zip',sources)
    package(a.output/'new-libraries.zip',{n:a.build/n for n in ('jshc_memory_split.dll','jshc_split_c99.dll','channel_avx2_split.o','memory_c.o','memory_parallel.o')})
    package(a.output/'exact-rom.zip',{'rom-17.bin':a.roms/'rom-17.bin'})
    package(a.output/'performance-raw.zip',{item.relative_to(a.perf).as_posix():item for item in a.perf.rglob('*.json') if item.name not in ('summary.json','partial.json','driver.json')})
    package(a.output/'stream-rss-raw.zip',{item.relative_to(a.rss).as_posix():item for item in a.rss.rglob('*.json') if item.name!='summary.json'})
    workers=[read(a.perf/f'worker-{i}/results.json') for i in range(4)];pairs=[]
    for mode in ('inplace','outplace'):
        for threads in (1,4):
            for old in ('avx2_17','avx2_24','dict32'):
                values=[]
                for worker in workers:
                    times={r['label']:r['median_seconds'] for r in worker['rows'] if r['mode']==mode and r['threads']==threads};values.append(times[old]/times['avx2_split'])
                pairs.append(dict(mode=mode,threads=threads,old=old,per_worker=values,median=statistics.median(values),worst=min(values)))
    save(a.output/'layout-pairs.json',dict(purpose='同场旧字典耗时/新分平面耗时；>1表示新分平面较快，旧17bit与新分平面容量相同。',pairs=pairs,scope='旧32/24/17均原DLL原字节，不把历史跨场漂移解释为本轮布局收益；保留所有worker。'))
    save(a.output/'manifest.json',dict(purpose=__doc__,files={item.name:dict(bytes=item.stat().st_size,sha256=sha(item)) for item in a.output.iterdir() if item.is_file()},references='78/80、原32bit字典及四MinGW依赖在report/data/p16-memory-rom-v1/measured-libraries.zip；旧17/24字典DLL及ROM在report/data/p16-compact-dictionary-v1/new-libraries.zip和exact-roms.zip。SHA按冻结plan、build和worker身份记录核对；此包仅新增分平面，不重复旧二进制。解压ROM+真实model字节决定容量，不用ZIP大小代替RAM。'))
    print(a.output)
if __name__=='__main__':main()
