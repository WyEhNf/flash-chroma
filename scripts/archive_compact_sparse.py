"""发布冻结稀疏句柄的原始合同、四进程性能、RSS和可重放源，不重跑测量。"""
import argparse
from pathlib import Path
import zipfile
from study_memory_rom import ROOT,read,save,sha

def package(path,files):
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        for name,source in sorted(files.items()):z.write(source,name)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('build','finite','full','three','perf','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args()
    for key in vars(a):setattr(a,key,getattr(a,key).resolve())
    a.output.mkdir(parents=True,exist_ok=False)
    inputs={'build.json':a.build/'build.json','finite.json':a.finite/'finite.json','full.json':a.full/'full.json','three-stage.json':a.three/'results.json','performance.json':a.perf/'summary.json'}
    for name,source in inputs.items():(a.output/name).write_bytes(source.read_bytes())
    plan=ROOT/'experiments/compact-sparse-v1.json'
    sources={n:ROOT/n for n in read(plan)['source_sha256']}
    for n in ('experiments/compact-sparse-v1.json','scripts/check_compact_three_stage.py','scripts/archive_compact_sparse.py','scripts/study_memory_rom.py','scripts/bench_memory_rom.py'):
        sources[n]=ROOT/n
    for source in a.build.glob('*.su'):sources['stack-usage/'+source.name]=source
    package(a.output/'measured-source.zip',sources)
    libraries={'jshc_compact_sparse.dll':a.build/'jshc_compact_sparse.dll','specialized-avx2.o':Path(read(plan)['inputs']['avx2_object']['path'])}
    package(a.output/'new-library.zip',libraries)
    package(a.output/'general-fixtures.zip',{x.name:x for x in a.finite.iterdir() if x.suffix in ('.slut','.bin')})
    package(a.output/'performance-raw.zip',{x.relative_to(a.perf).as_posix():x for x in a.perf.rglob('*.json') if x.name not in ('summary.json','partial.json')})
    for label,directory in (('finite',a.finite),('full',a.full)):
        driver=directory/'driver.json'
        if driver.is_file():(a.output/(label+'-driver.json')).write_bytes(driver.read_bytes())
    summary=read(inputs['performance.json'])
    save(a.output/'acceptance.json',dict(results=[{k:r[k] for k in ('case','threads','worst_retention','median_retention','control_pass','tiers')} for r in summary['results']],precision='a399单级/四级与一般四级完整域逐字节相等；保留率100%是相对既有模型，没有相对原滤镜零误差声明。',scope='一般模型仅实测first_extended4；a399与同场最快78/80比后拒绝，不能改用specialized慢分母升级。'))
    save(a.output/'manifest.json',dict(purpose=__doc__,files={x.name:dict(bytes=x.stat().st_size,sha256=sha(x)) for x in a.output.iterdir() if x.is_file()},references='78/80/specialized与四MinGW依赖按build/performance原件SHA复用首阶段已发布库；不上传大照片/完整RGB域。'))
    with zipfile.ZipFile(a.output/'performance-raw.zip') as z:
        if z.testzip():raise AssertionError('性能压缩包CRC错误')
    print(a.output)
if __name__=='__main__':main()
