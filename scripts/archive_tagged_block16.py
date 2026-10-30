"""封存一次M16T普查、单版质量与六角色受控同场，不重跑测量。"""
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
    a.output.mkdir(parents=True,exist_ok=False);planpath=ROOT/'experiments/tagged-block16-native-v1.json';plan=read(planpath)
    originals={'build.json':a.build/'build.json','export.json':a.roms/'export.json','quality.json':a.verify/'results.json','performance.json':a.perf/'summary.json','benchmark-driver.json':a.perf/'driver.json','census.json':Path(plan['census_path'])}
    for name,source in originals.items():(a.output/name).write_bytes(source.read_bytes())
    sources={name:ROOT/name for name in plan['source_sha256']}
    for name in ('experiments/tagged-block16-native-v1.json','experiments/tagged-block16-census-v1.json','experiments/tagged-block16-design-v1.md','scripts/archive_tagged_block16.py','scripts/audit_tagged_block16.py','scripts/archive_compact_sparse.py'):
        sources[name]=ROOT/name
    for source in a.build.glob('*.su'):sources['stack-usage/'+source.name]=source
    package(a.output/'measured-source.zip',sources)
    package(a.output/'new-libraries.zip',{name:a.build/name for name in ('jshc_memory_tag16.dll','jshc_tag16_c99.dll','channel_avx2_tag.o','memory_c.o','memory_parallel.o')})
    package(a.output/'exact-rom.zip',{'new-M16T.bin':a.roms/'rom-4.bin','source-M16D-16.bin':Path(plan['input_rom_path'])})
    package(a.output/'performance-raw.zip',{source.relative_to(a.perf).as_posix():source for source in a.perf.rglob('*.json') if source.name not in ('summary.json','partial.json','driver.json')})
    workers=[read(a.perf/f'worker-{i}/results.json') for i in range(4)];pairs=[]
    for mode in ('inplace','outplace'):
        for threads in (1,4):
            for control in ('old32','old3B'):
                values=[]
                for worker in workers:
                    times={r['label']:r['median_seconds'] for r in worker['rows'] if r['mode']==mode and r['threads']==threads};values.append(times[control]/times['tag_avx'])
                pairs.append(dict(control=control,mode=mode,threads=threads,per_worker=values,median=statistics.median(values),worst=min(values)))
    save(a.output/'layout-pairs.json',dict(purpose='旧32/3B耗时除以新tag耗时；大于1为tag较快。资格仍只用每worker较快78/80。',pairs=pairs,scope='新增0x55受控同场，旧3B历史有效反例及失效场均不被好场覆盖。'))
    calls=[call for worker in workers for row in worker['rows']+worker['controls'] for call in row['cpu_calls']]
    save(a.output/'cpu-records-summary.json',dict(total=len(calls),phases=dict(Counter(c['phase'] for c in calls)),cpu_before=dict(Counter(c['cpu_before'] for c in calls)),cpu_after=dict(Counter(c['cpu_after'] for c in calls)),endpoint_changes=sum(c['cpu_before']!=c['cpu_after'] for c in calls),allowed_cpus=[0,2,4,6],scope='caller端点，不是OMP轨迹或旧unbound迁移因果证据。'))
    save(a.output/'environment-note.json',dict(purpose='一次普查、质量与性能的环境及容量分开。',quality='Windows x64/GCC15.2；root授权与tail质量可并行，无速度结论。原ROM与合成ROM紧贴只读/NOACCESS边界。',performance='六角色/四worker统一process mask0x55，native wall外CPU端点；root授权独占窗口，无逐OMP线程绑定或锁频。',memory='实际ROM5915136+Model1056=5916192B；C99无堆且prepare栈1152/apply64，AVX入口栈208。导出和质量峰值含Python/库/数组，RSS在照片分配前相同import群的新进程测得，均不冒充核心RAM。',census='只读原ROM唯一普查；37.41198%为均匀域引用，不是照片tag率/分支命中。',console='底层stdout可能含A/A过滤前档位，正式performance.json已由冻结驱动清空失效场。',references='固定a399与原78/80，独立speed85/87容量和当前其它精度模型不作为本场分母。'))
    save(a.output/'manifest.json',dict(purpose=__doc__,files={source.name:dict(bytes=source.stat().st_size,sha256=sha(source)) for source in a.output.iterdir() if source.is_file()},references='旧32/78/80/四MinGW依赖见原ROM阶段库；旧3B见compact-dictionary阶段。新ROM按解压实际容量计，不以ZIP计RAM；不上传照片。'))
    print(a.output)
if __name__=='__main__':main()
