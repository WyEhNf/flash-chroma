"""封存四档bank容量剖析、唯一4bank实现及七角色完整原始轮次。"""
import argparse
from pathlib import Path
import statistics
from archive_compact_sparse import package
from study_memory_rom import ROOT,read,save,sha

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('build','roms','verify','perf','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    for key in vars(a):setattr(a,key,getattr(a,key).resolve())
    a.output.mkdir(parents=True,exist_ok=False);planpath=ROOT/'experiments/banked-dictionary-native-v1.json';plan=read(planpath)
    for name,source in {'profile.json':Path(plan['profile_result_path']),'build.json':a.build/'build.json','export.json':a.roms/'export.json','quality.json':a.verify/'results.json','performance.json':a.perf/'summary.json','benchmark-driver.json':a.perf/'driver.json'}.items():(a.output/name).write_bytes(source.read_bytes())
    sources={name:ROOT/name for name in plan['source_sha256']}
    for source in (planpath,ROOT/'scripts/archive_banked_dictionary.py',ROOT/'scripts/archive_compact_sparse.py',ROOT/'experiments/compact-dictionary-v1.json'):sources[source.relative_to(ROOT).as_posix()]=source
    for source in a.build.glob('*.su'):sources['stack-usage/'+source.name]=source
    package(a.output/'measured-source.zip',sources)
    package(a.output/'new-libraries.zip',{name:a.build/name for name in ('jshc_memory_bank.dll','jshc_bank_c99.dll','channel_avx2_bank.o','memory_c.o','memory_parallel.o')})
    package(a.output/'exact-rom.zip',{'rom-4.bin':a.roms/'rom-4.bin'})
    package(a.output/'performance-raw.zip',{source.relative_to(a.perf).as_posix():source for source in a.perf.rglob('*.json') if source.name not in ('summary.json','partial.json','driver.json')})
    workers=[read(a.perf/f'worker-{i}/results.json') for i in range(4)];pairs=[]
    for mode in ('inplace','outplace'):
        for threads in (1,4):
            for old in ('dict32','avx2_24','avx2_17'):
                values=[]
                for worker in workers:
                    times={r['label']:r['median_seconds'] for r in worker['rows'] if r['mode']==mode and r['threads']==threads};values.append(times[old]/times['avx2_bank'])
                pairs.append(dict(mode=mode,threads=threads,old=old,per_worker=values,median=statistics.median(values),worst=min(values)))
    save(a.output/'layout-pairs.json',dict(purpose='同场旧字典耗时/新4bank耗时，>1表示4bank较快；原二进制直接载入。',pairs=pairs,scope='只比较冻结唯一4bank，2/8/16没有native实现。旧跨场变化保持未知，不拼接历史最好值。'))
    save(a.output/'manifest.json',dict(purpose=__doc__,files={source.name:dict(bytes=source.stat().st_size,sha256=sha(source)) for source in a.output.iterdir() if source.is_file()},references='78/80、原32bit及四MinGW依赖见report/data/p16-memory-rom-v1/measured-libraries.zip；旧3B/17bit见report/data/p16-compact-dictionary-v1/new-libraries.zip及exact-roms.zip。实际容量按解压ROM+1072B新ABI，不以ZIP替代RAM。'))
    print(a.output)
if __name__=='__main__':main()
