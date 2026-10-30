"""封存唯一RGB32块格式、原始质量及全部五角色性能，不重跑测量。"""
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
    a.output.mkdir(parents=True,exist_ok=False);planpath=ROOT/'experiments/color-dictionary-v1.json';plan=read(planpath)
    for name,source in {'build.json':a.build/'build.json','export.json':a.roms/'export.json','quality.json':a.verify/'results.json','performance.json':a.perf/'summary.json','benchmark-driver.json':a.perf/'driver.json'}.items():(a.output/name).write_bytes(source.read_bytes())
    sources={name:ROOT/name for name in plan['source_sha256']}
    for source in (planpath,ROOT/'scripts/archive_color_dictionary.py',ROOT/'scripts/audit_color_dictionary.py',ROOT/'scripts/archive_compact_sparse.py',ROOT/'experiments/color-dictionary-design-v1.md',ROOT/'experiments/compact-dictionary-runtime/channel_avx2_24.cpp',ROOT/'experiments/compact-dictionary-runtime/memory_parallel.cpp'):sources[source.relative_to(ROOT).as_posix()]=source
    for source in a.build.glob('*.su'):sources['stack-usage/'+source.name]=source
    package(a.output/'measured-source.zip',sources)
    package(a.output/'new-libraries.zip',{name:a.build/name for name in ('jshc_memory_color_dict.dll','jshc_color_dict_c99.dll','channel_avx2_color.o','memory_c.o','memory_parallel.o')})
    package(a.output/'exact-rom.zip',{'rom-24.bin':a.roms/'rom-24.bin','source-M16D.bin':Path(plan['input_rom_path'])})
    package(a.output/'performance-raw.zip',{source.relative_to(a.perf).as_posix():source for source in a.perf.rglob('*.json') if source.name not in ('summary.json','partial.json','driver.json')})
    workers=[read(a.perf/f'worker-{i}/results.json') for i in range(4)];pairs=[]
    for mode in ('inplace','outplace'):
        for threads in (1,4):
            values=[]
            for worker in workers:
                times={r['label']:r['median_seconds'] for r in worker['rows'] if r['mode']==mode and r['threads']==threads};values.append(times['avx2_24']/times['avx2_color'])
            pairs.append(dict(mode=mode,threads=threads,per_worker=values,median=statistics.median(values),worst=min(values)))
    save(a.output/'layout-pairs.json',dict(purpose='同场原3B耗时/新RGB32耗时；>1表示新块格式更快。',pairs=pairs,scope='旧3B有效低速反例不撤销，本场配对不能恢复稳健全情形资格。全部序列和最劣worker保留。'))
    save(a.output/'environment-note.json',dict(purpose='区分质量与正式计时环境及容量统计范围。',quality='root明确授权与tail16bit质量并行，均不计速度；导出独立进程峰值不冒充整机峰值。',performance='root另行授权的正式排他窗口，四新worker按冻结协议顺序运行；未锁频、未绑核、未控制温度。',console='原始execution.stdout保留底层bench.main过滤A/A前的打印；正式performance.json由冻结外层驱动按controls清空失效档位，审计逐项重算，不把旧stdout升级为资格。',capacity='只计实际ROM+32B借用对象。C99无堆是核心契约；Python、loader、OMP、桌面适配器和运行库的分配另列RSS。',portability='只实际执行Windows AMD64/GCC15.2 C99及桌面AVX2；未把C99语言合规写成WASM/ARM实板运行。'))
    save(a.output/'manifest.json',dict(purpose=__doc__,files={source.name:dict(bytes=source.stat().st_size,sha256=sha(source)) for source in a.output.iterdir() if source.is_file()},references='78/80与四MinGW依赖复用report/data/p16-memory-rom-v1/measured-libraries.zip；旧3B原DLL见report/data/p16-compact-dictionary-v1/new-libraries.zip。实际容量按解压ROM+32B，不以ZIP大小代替RAM。'))
    print(a.output)
if __name__=='__main__':main()
