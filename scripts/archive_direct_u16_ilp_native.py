"""归档288完整质量、同287的表字节恒等及六个独立进程RSS观察。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
ROOT=Path(__file__).resolve().parents[1]


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖288质量归档')
    measured=ROOT/'artifacts/p16-direct-u16-ilp-quality-v1';build=ROOT/'artifacts/p16-direct-u16-ilp-build-v1'
    frozen_path=ROOT/'artifacts/p16-direct-u16-ilp-frozen-v1/frozen.json';frozen=read(frozen_path);result=read(measured/'results.json')
    assert result['passed'] and result['performance_calls']==0
    expected={(n,k,t,p) for n in ('max_first','p99_first','old_best','87_old_best') for k,t in [('scalar',1),('avx2',1),('avx2',4)] for p in ('inplace','to')}
    seen=set()
    for row in result['full_matrix']:
        key=(row['model'],row['kernel'],row['threads'],row['path']);assert key not in seen;seen.add(key)
        spec=frozen['models']['old_best' if row['model']=='87_old_best' else row['model']]
        assert row['mismatches']==0 and row['sha256']==spec['oracle_sha256']
    assert seen==expected and result['guard_contract']['guarded_cases']==88 and result['guard_contract']['bmi_supported']
    photos={(r['image'],r['model'],r['path']):r for r in result['photo_matrix']}
    assert len(photos)==len(result['photo_matrix'])==600 and len({k[0] for k in photos})==100
    for (image,model,path),row in photos.items():assert row['mismatches']==0 and row['sha256']==photos[image,model,'inplace']['sha256']==photos[image,model,'to']['sha256']
    assert len(result['287_table_identity'])==2
    for row in result['287_table_identity']:assert row['table_bytes_equal'] and row['palette_equal'] and row['capacity_equal']
    assert result['contract']['short_pattern_backend_cases']==729 and result['contract']['diagnostic_rejections']==8 and all(v==11 for v in result['outplace_rejections'].values())
    assert [r['wide']['reason'] for r in result['synthetic']]==[1,0,3,2]
    prior=ROOT/'report/data/p16-direct-u16-native-20261024-v2';assert read(prior/'frozen-v2.json')['models']==frozen['models']
    for spec in frozen['models'].values():
        for path,sha in spec['input_sha256'].items():assert digest(Path(path))==sha
    args.output.mkdir(parents=True)
    for target,source in [('results.json',measured/'results.json'),('frozen.json',frozen_path),('plan.md',ROOT/'experiments/p16-direct-u16-ilp-plan-v1.md'),
        ('prior-287-manifest.json',prior/'manifest.json'),('models.zip',prior/'models.zip')]:shutil.copyfile(source,args.output/target)
    sources={name:digest(ROOT/name) for name in frozen['sources_sha256']}
    assert sources==frozen['sources_sha256'];sources['scripts/archive_direct_u16_ilp_native.py']=digest(Path(__file__))
    # 逐编译器依赖核对本次已前置冻结的基础C、头文件及全部kernel。
    dependencies=set()
    for dep in build.rglob('*.obj.d'):
        for line in dep.read_text(encoding='utf-8').splitlines():
            token=line.strip().rstrip('\\').strip().replace('\\','/')
            if token.lower().startswith(ROOT.as_posix().lower()+'/'):
                name=Path(token).resolve().relative_to(ROOT).as_posix();assert name in sources,name;dependencies.add(name)
    with zipfile.ZipFile(args.output/'source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in sorted(sources):z.write(ROOT/name,name)
    with zipfile.ZipFile(args.output/'build-evidence.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in ('build.log','compile_commands.json','CMakeCache.txt'):z.write(build/name,name)
        z.write(frozen_path.with_name('configure.log'),'configure.log')
        for path in sorted(build.rglob('*')):
            if path.suffix=='.su' or path.name.endswith('.obj.d'):z.write(path,path.relative_to(build).as_posix())
        for name in ('contracts-stdout.txt','contracts-stderr.txt'):z.write(measured/name,name)
    rss=[]
    with zipfile.ZipFile(args.output/'rss-raw.zip','w',zipfile.ZIP_DEFLATED) as z:
        for revision in (287,288):
            for model in ('max_first','p99_first','old_best'):
                path=ROOT/f'artifacts/p16-direct-u16-ilp-rss-{revision}-v1/{model}.json';row=read(path)
                assert row['model']==model and row['revision']==revision and row['apply_calls']==row['performance_calls']==0
                assert row['frozen_sha256']==digest(frozen_path) and row['library_sha256']==(frozen['frozen_287_sha256'] if revision==287 else result['library_sha256'])
                z.write(path,f'{revision}/{model}.json');rss.append(row)
    check={'pass':True,'full_configs':24,'photos':600,'guard_cases':88,'table_identity':result['287_table_identity'],'RSS_processes':len(rss),
        'compiler_dependency_count':len(dependencies),'all_compiler_dependencies_prefrozen':True,'performance_calls':0,
        'scope':'独立核JSON矩阵、源/依赖SHA和模型冻结，以及真实RSS原件身份；不重跑像素/计时。RSS为绝对进程/增量，非净table或全系统RAM。'}
    (args.output/'independent-check.json').write_text(json.dumps(check,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    manifest={'source_sha256':sources,'files':{p.name:digest(p) for p in args.output.iterdir()},'scope':'288完整质量+287表/容量恒等+六进程实际RSS；无性能、无默认升级。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'pass':True,'files':len(manifest['files']),'source_members':len(sources),'dependencies':len(dependencies),'RSS_processes':len(rss)}),flush=True)


if __name__=='__main__':main()
