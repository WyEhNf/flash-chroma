"""封存固定1024B块LE16及0x55受控同场原始测量，不重跑测试。"""
import argparse
from collections import Counter
from pathlib import Path
import statistics
from archive_compact_sparse import package
from study_memory_rom import ROOT,read,save,sha

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('build','roms','verify','perf','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    for key in vars(a):setattr(a,key,getattr(a,key).resolve())
    a.output.mkdir(parents=True,exist_ok=False);planpath=ROOT/'experiments/le16-block1024-v1.json';plan=read(planpath)
    for name,source in {'build.json':a.build/'build.json','export.json':a.roms/'export.json','quality.json':a.verify/'results.json','performance.json':a.perf/'summary.json','benchmark-driver.json':a.perf/'driver.json'}.items():(a.output/name).write_bytes(source.read_bytes())
    sources={name:ROOT/name for name in plan['source_sha256']}
    for source in (planpath,ROOT/'scripts/archive_le16_block1024.py',ROOT/'scripts/audit_le16_block1024.py',ROOT/'scripts/archive_compact_sparse.py',ROOT/'experiments/le16-block1024-design-v1.md'):sources[source.relative_to(ROOT).as_posix()]=source
    sources['old-control/memory_avx2_10.cpp']=Path(plan['old_avx2_source_path']);sources['old-control/build.json']=ROOT/'artifacts/p16-memory-build-v2/build.json'
    for source in a.build.glob('*.su'):sources['stack-usage/'+source.name]=source
    package(a.output/'measured-source.zip',sources)
    package(a.output/'new-libraries.zip',{name:a.build/name for name in ('jshc_memory_le16_1024.dll','jshc_le16_1024_c99.dll','channel_avx2_le16.o','memory_c.o','memory_parallel.o')})
    package(a.output/'exact-rom.zip',{'new-LE16.bin':a.roms/'rom-10.bin','source-M16D-1024.bin':Path(plan['input_rom_path'])})
    package(a.output/'performance-raw.zip',{source.relative_to(a.perf).as_posix():source for source in a.perf.rglob('*.json') if source.name not in ('summary.json','partial.json','driver.json')})
    workers=[read(a.perf/f'worker-{i}/results.json') for i in range(4)];pairs=[]
    for mode in ('inplace','outplace'):
        for threads in (1,4):
            values=[]
            for worker in workers:
                times={r['label']:r['median_seconds'] for r in worker['rows'] if r['mode']==mode and r['threads']==threads};values.append(times['old1024']/times['avx2_le16'])
            pairs.append(dict(mode=mode,threads=threads,per_worker=values,median=statistics.median(values),worst=min(values)))
    save(a.output/'layout-pairs.json',dict(purpose='同场原1024B块耗时/新LE16耗时；大于1为新格式较快，资格仍以fast78/80作分母。',pairs=pairs,scope='两控制环境分开，禁止与旧unbound绝对秒数归因；有效旧1024反例须保留降级。'))
    calls=[call for worker in workers for row in worker['rows']+worker['controls'] for call in row['cpu_calls']]
    save(a.output/'cpu-records-summary.json',dict(total=len(calls),phases=dict(Counter(c['phase'] for c in calls)),cpu_before=dict(Counter(c['cpu_before'] for c in calls)),cpu_after=dict(Counter(c['cpu_after'] for c in calls)),endpoint_changes=sum(c['cpu_before']!=c['cpu_after'] for c in calls),allowed_cpus=[0,2,4,6],scope='记录caller端点，非OMP线程轨迹；只描述本轮受控环境，不与旧187/512作迁移因果比较。'))
    save(a.output/'environment-note.json',dict(purpose='新受控环境与旧未绑定证据分开。',quality='与tail288质量并行，无速度结论；质量峰值含67MiB正向65535夹具，导出进程峰值另列。',performance='全部自有测量/RSS进程process mask0x55=0/2/4/6；native wall外记录caller端点CPU。root明确授权的独占窗口，无逐OMP线程绑定/锁频/温控。',frozen_wording='原计划scope仍含旧措辞无affinity，未同步更新；同一冻结计划process_control与执行源已在冻结前加入0x55。原文字节均保留，实际有process affinity控制，没有执行另立的漂移因果干预，不得称本场unbound。',causality='新控制不是旧跨场变动的归因实验，不恢复3B，也不将旧1024好场覆盖新有效失败。',console='底层bench.main.stdout可能打印A/A过滤前档位；正式performance.json由冻结驱动清空无效场并复算。',rss='相同import群的新进程，照片分配前；含Python/NumPy/库及流式SHA，不当纯核心RAM。'))
    save(a.output/'manifest.json',dict(purpose=__doc__,files={source.name:dict(bytes=source.stat().st_size,sha256=sha(source)) for source in a.output.iterdir() if source.is_file()},references='78/80、原1024块DLL和四MinGW依赖见report/data/p16-memory-rom-v1/measured-libraries.zip。真实容量为解压新ROM+1056B，不以ZIP替代RAM。'))
    print(a.output)
if __name__=='__main__':main()
