"""封存C7BK实际ROM、质量和完整六角色同场，不重复像素测试。"""
import argparse
from collections import Counter
from pathlib import Path
import statistics
from archive_compact_sparse import package
from rgb3d7_support import ROOT,PLAN,read,save,sha
from recompute_rgb3d7_decimal import compute_raw
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('build','roms','quality','rss-pure','rss-desktop','perf','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    for name in vars(a):setattr(a,name,getattr(a,name).resolve())
    a.output.mkdir(parents=True,exist_ok=False);plan=read(PLAN)
    originals={'build.json':a.build/'build.json','export.json':a.roms/'export.json','quality.json':a.quality/'results.json','quality-rss-pure.json':a.rss_pure/'rss.json','quality-rss-desktop.json':a.rss_desktop/'rss.json','performance.json':a.perf/'summary.json','benchmark-driver.json':a.perf/'driver.json'}
    for name,source in originals.items():(a.output/name).write_bytes(source.read_bytes())
    sources={name:ROOT/name for name in plan['source_sha256']}
    for source in (PLAN,ROOT/'scripts/archive_rgb3d7.py',ROOT/'scripts/audit_rgb3d7.py',ROOT/'scripts/recompute_rgb3d7_decimal.py',ROOT/'scripts/archive_compact_sparse.py'):sources[source.relative_to(ROOT).as_posix()]=source
    sources['old-pixel/channel_avx2_tag.cpp']=ROOT/'experiments/tagged-block16-runtime/channel_avx2_tag.cpp';sources['object/c99-assembly.txt']=a.build/'c99-assembly.txt'
    for source in a.build.glob('*.su'):sources['stack-usage/'+source.name]=source
    package(a.output/'measured-source.zip',sources)
    package(a.output/'new-libraries.zip',{name:a.build/name for name in ('jshc_rgb3d7.dll','jshc_rgb3d7_c99.dll','memory_c.o','memory_parallel.o','channel_avx2_rgb3d7.o')})
    package(a.output/'exact-rom.zip',{'C7BK.bin':a.roms/'rgb3d7.bin'})
    package(a.output/'performance-raw.zip',{source.relative_to(a.perf).as_posix():source for source in a.perf.rglob('*.json') if source.name not in ('summary.json','partial.json','driver.json','independent-decimal-summary.json')})
    workers=[read(a.perf/f'worker-{i}/results.json') for i in range(4)];pairs=[]
    save(a.output/'decimal-summary.json',compute_raw([(a.perf/f'worker-{i}/results.json').read_bytes() for i in range(4)],(a.perf/'summary.json').read_bytes()))
    for mode in ('inplace','outplace'):
        for threads in (1,4):
            for control,candidate in (('linear8_avx','rgb3d7_avx'),('linear8_clang_c99','rgb3d7_c99')):
                values=[]
                for worker in workers:
                    times={r['label']:r['median_seconds'] for r in worker['rows'] if r['mode']==mode and r['threads']==threads};values.append(times[control]/times[candidate])
                pairs.append(dict(control=control,candidate=candidate,mode=mode,threads=threads,per_worker=values,median=statistics.median(values),worst=min(values)))
    save(a.output/'linear-pairs.json',dict(purpose='同场原线性8bit耗时/新本地7bit耗时，AVX/C99各自配对；资格仍仅fast78/80。',pairs=pairs,scope='大于1为新格式较快，AA有效性另看正式performance；不拼旧场绝对秒数。'))
    calls=[call for worker in workers for row in worker['rows']+worker['controls'] for call in row['cpu_calls']]
    save(a.output/'cpu-records-summary.json',dict(total=len(calls),phases=dict(Counter(c['phase'] for c in calls)),cpu_before=dict(Counter(c['cpu_before'] for c in calls)),cpu_after=dict(Counter(c['cpu_after'] for c in calls)),endpoint_changes=sum(c['cpu_before']!=c['cpu_after'] for c in calls),allowed_cpus=[0,2,4,6],scope='caller端点，不是OMP线程轨迹或迁移因果证明。'))
    save(a.output/'environment-note.json',dict(purpose='质量、容量、不同import群RSS及正式性能分开。',format='真实ROM14943268+实际model32=14943300B，无原global palette/热表副本；4B自有guard及全65536 palette槽均计入。',quality='Clang21严格C99 generic x64无AVX/BMI；GCC15.2 AVX2/OMP。root授权非性能窗，质量可与其它质量并行；8完整域/8百图/合同全过。',performance='六角色/四worker固定process mask0x55，native wall外端点；root另授独占，不逐OMP线程绑定/锁频，全部AA与最劣样本保留。',memory='离线/质量峰含Python/数组/夹具；早先quality RSS只有支持模块，正式六角色RSS另有bench/控制导入，不直接相减绝对峰。核心无堆，静态栈不是整个调用链/OMP总栈。',scope='旧6bit54失败不改，不重census、不用照片/gold选型；旧线性仅配对，主分母fast78/80仍28046644B；无WASM/实板或官方许可声明。',console='底层控制台可能打印AA过滤前档位；正式performance由冻结suffix清空无效场，不能读stdout授档。'))
    save(a.output/'manifest.json',dict(purpose=__doc__,files={path.name:dict(bytes=path.stat().st_size,sha256=sha(path)) for path in a.output.iterdir() if path.is_file()},references='原6bit完整联合频数复用p16-rgb3d-palette-census-v1/census-raw.zip；旧线性库复用Clang store阶段，fast78/80与依赖复用首ROM阶段。ZIP不作RAM，不上传照片。'))
    print(a.output)
if __name__=='__main__':main()
