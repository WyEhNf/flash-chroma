"""封存相同C99 store的Clang/GCC同场性能、机器码与真实复用对象证据。"""
import argparse
from pathlib import Path
import statistics
from archive_compact_sparse import package
from study_memory_rom import ROOT,read,save,sha

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('build','verify','perf','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args()
    for key in vars(a):setattr(a,key,getattr(a,key).resolve())
    a.output.mkdir(parents=True,exist_ok=False);plan=ROOT/'experiments/memory-rom-clang-store-v1.json';frozen=read(plan);old=Path(frozen['old_build'])
    files={'build.json':a.build/'build.json','full.json':a.verify/'full/results.json','contract.json':a.verify/'contract/results.json','verification-driver.json':a.verify/'driver.json','performance.json':a.perf/'summary.json','benchmark-driver.json':a.perf/'driver.json','clang-store-assembly.txt':a.build/'clang-store-assembly.txt'}
    for name,path in files.items():(a.output/name).write_bytes(path.read_bytes())
    sources={n:ROOT/n for n in frozen['source_sha256']}
    for path in (plan,ROOT/'experiments/memory-rom-store-v1.json',ROOT/'scripts/archive_memory_rom_clang_store.py',ROOT/'scripts/archive_compact_sparse.py'):sources[path.relative_to(ROOT).as_posix()]=path
    for path in a.build.glob('*.su'):sources['stack-usage/clang-'+path.name]=path
    if (old/'memory_store.su').is_file():sources['stack-usage/gcc-memory_store.su']=old/'memory_store.su'
    package(a.output/'measured-source.zip',sources)
    libraries={n:a.build/n for n in ('jshc_memory_clang_store.dll','jshc_memory_c99.dll','memory_store_clang.o')};libraries['gcc-memory_store.o']=old/'memory_store.o'
    package(a.output/'new-libraries.zip',libraries)
    package(a.output/'performance-raw.zip',{x.relative_to(a.perf).as_posix():x for x in a.perf.rglob('*.json') if x.name not in ('summary.json','partial.json','driver.json')})
    workers=[read(a.perf/f'worker-{i}/results.json') for i in range(4)];pairs=[]
    for mode in ('inplace','outplace'):
        for threads in (1,4):
            ratios=[]
            for w in workers:
                times={r['label']:r['median_seconds'] for r in w['rows'] if r['mode']==mode and r['threads']==threads};ratios.append(times['gcc_store']/times['clang_store'])
            pairs.append(dict(mode=mode,threads=threads,per_worker_gcc_over_clang=ratios,median=statistics.median(ratios),worst=min(ratios)))
    save(a.output/'compiler-pairs.json',dict(purpose='相同C99源/ROM、复用其余对象的同场配对吞吐比GCC耗时/Clang耗时，>1表示Clang较快。',pairs=pairs,scope='不把跨场绝对耗时或旧51.23%乘进本轮结论；编译器改变也可能改变函数布局/调度，不只归因静态栈尺寸。'))
    save(a.output/'manifest.json',dict(purpose=__doc__,files={x.name:dict(bytes=x.stat().st_size,sha256=sha(x)) for x in a.output.iterdir() if x.is_file()},references='固定78/80与四MinGW依赖在report/data/p16-memory-rom-v1/measured-libraries.zip；GCC store旧DLL在report/data/p16-memory-store-v1/new-libraries.zip。原SHA按plan/build/performance绑定。ROM仍首阶段rom-0.bin；不重复上传16MiB载荷。'))
    print(pairs)
if __name__=='__main__':main()
