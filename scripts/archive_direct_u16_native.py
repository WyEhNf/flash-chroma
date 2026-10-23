"""归档287精确质量、失败构建和真实编译依赖；不重新运行映射或计时。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile
ROOT=Path(__file__).resolve().parents[1]


def sha(data):return hashlib.sha256(data).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖16bit质量归档')
    measured=ROOT/'artifacts/p16-direct-u16-quality-v1';build=ROOT/'artifacts/p16-direct-u16-build-v1'
    frozen=read(ROOT/'artifacts/p16-direct-u16-frozen-v2/frozen.json');result=read(measured/'results.json')
    if not result['passed'] or result['performance_calls']!=0:raise ValueError('必须保持质量/性能边界')
    # 独立核对完整矩阵、冻结流与逐图覆盖，完全不重用原脚本的循环或汇总函数。
    seen=set()
    for row in result['full_matrix']:
        spec=frozen['models']['old_best' if row['model']=='87_old_best' else row['model']]
        assert row['mismatches']==0 and row['sha256']==spec['oracle_sha256']
        key=(row['model'],row['kernel'],row['threads'],row['path']);assert key not in seen;seen.add(key)
    expected={(n,k,t,p) for n in ('max_first','p99_first','old_best','87_old_best') for k,t in [('scalar',1),('avx2',1),('avx2',4)] for p in ('inplace','to')}
    assert seen==expected
    photos={}
    for row in result['photo_matrix']:
        key=(row['image'],row['model'],row['path']);assert key not in photos and row['mismatches']==0;photos[key]=row['sha256']
    assert len(photos)==600 and len({k[0] for k in photos})==100
    for (image,model,path),digest in photos.items():assert photos[image,model,'inplace']==photos[image,model,'to']
    for n,count in [('max_first',603),('p99_first',703)]:
        state=result['capacity'][n];w=state['wide']
        assert w['enabled']==1 and w['format']==16 and w['palette_size']==count and w['input_entries']==2**24
        assert w['table_capacity_bytes']==2**25+4 and w['palette_capacity_bytes']==count*4 and w['guard_bytes']==4 and w['guaranteed_alignment']==2
        assert state['direct']['entries']*4==w['table_capacity_bytes']
    assert result['capacity']['old_best']['wide']['reason']==1 and result['capacity']['old_best']['model_bytes']-result['capacity']['87_old_best']['model_bytes']==144
    assert result['guard_contract']['passed'] and result['guard_contract']['id_max']==65535 and result['guard_contract']['input_address_max']==2**24-1
    assert result['contract']['short_pattern_backend_cases']==729 and result['contract']['diagnostic_rejections']==8
    assert all(v==11 for v in result['outplace_rejections'].values())
    assert [r['wide']['reason'] for r in result['synthetic']]==[1,0,3,2]
    args.output.mkdir(parents=True)
    for target,source in [('results.json',measured/'results.json'),('frozen-v1.json',ROOT/'artifacts/p16-direct-u16-frozen-v1/frozen.json'),
        ('frozen-v2.json',ROOT/'artifacts/p16-direct-u16-frozen-v2/frozen.json'),('plan.md',ROOT/'experiments/p16-direct-u16-plan-v1.md')]:shutil.copyfile(source,args.output/target)
    sources={}
    for name,digest in frozen['sources_sha256'].items():
        data=(ROOT/name).read_bytes();assert sha(data)==digest;sources[name]=data
    # 增补编译器实际依赖中未列在前置文件表的只读基础文件，并逐Git blob验证归档起点。
    extra={};base='a083aeab772455c852425e9d48b5e3d8ce00d128'
    for dep in build.rglob('*.obj.d'):
        for line in dep.read_text(encoding='utf-8').splitlines():
            token=line.strip().rstrip('\\').strip().replace('\\','/')
            if not token.lower().startswith(ROOT.as_posix().lower()+'/'):continue
            path=Path(token).resolve();name=path.relative_to(ROOT).as_posix()
            if name not in sources:
                data=path.read_bytes();old=subprocess.check_output(['git','show',base+':'+name],cwd=ROOT)
                if data!=old:assert data.replace(b'\r\n',b'\n')==old.replace(b'\r\n',b'\n'),name
                sources[name]=data;extra[name]={'actual_sha256':sha(data),'git_blob_sha256':sha(old),'exact_bytes':data==old,'newline_normalized_equal':True}
    sources['scripts/archive_direct_u16_native.py']=Path(__file__).read_bytes()
    with zipfile.ZipFile(args.output/'source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(sources.items()):z.writestr(name,data)
    failed=read(ROOT/'artifacts/p16-direct-u16-frozen-v1/frozen.json');failed_sources={}
    with zipfile.ZipFile(args.output/'failed-source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name,digest in failed['sources_sha256'].items():
            data=(ROOT/name).read_bytes()
            if name=='experiments/p16-direct-u16-runtime/compile_avx2.cpp':
                marker=b'#include "../skylake-domain-isolated-runtime/channel_avx2.cpp"\n'
                data=data.replace(marker,marker+b'#include "direct_u16.hpp"\n',1)
            assert sha(data)==digest,(name,sha(data),digest)
            z.writestr(name,data);failed_sources[name]=digest
    model_sources={}
    for spec in frozen['models'].values():model_sources.update(spec['input_sha256'])
    with zipfile.ZipFile(args.output/'models.zip','w',zipfile.ZIP_DEFLATED) as z:
        model_manifest={}
        for n,(path,digest) in enumerate(sorted(model_sources.items())):
            data=Path(path).read_bytes();assert sha(data)==digest;name=f'{n:02d}-'+Path(path).name;z.writestr(name,data);model_manifest[name]={'original':path,'sha256':digest}
    with zipfile.ZipFile(args.output/'build-evidence.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in ('build.log','build-v2.log','compile_commands.json','CMakeCache.txt'):z.write(build/name,name)
        for path in sorted(build.rglob('*')):
            if path.suffix=='.su' or path.name.endswith('.obj.d'):z.write(path,path.relative_to(build).as_posix())
        for name in ('contracts-stdout.txt','contracts-stderr.txt'):z.write(measured/name,name)
    check={'pass':True,'full_configs':len(seen),'photos':len(photos),'short_groups':729,'guard':True,'performance_calls':0,
        'additional_compiler_dependency_blobs':{'base_commit':base,'files':extra},'failed_source_sha256':failed_sources,'model_zip_members':model_manifest,
        'scope':'独立检查JSON完整性/冻结SHA和矩阵，不重复像素/计时；前置源表未列部分基础C/头文件，实际.d依赖归档逐a083ae Git blob补核（允许记录中的CRLF差异），非事前新增冻结。'}
    (args.output/'independent-check.json').write_text(json.dumps(check,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    manifest={'source_sha256':{name:sha(data) for name,data in sources.items()},'files':{p.name:sha(p.read_bytes()) for p in args.output.iterdir()},
        'scope':'287精确质量全部原件、失败v1和成功v2源码、模型、真实依赖/栈/编译参数；不测速、不改默认。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'pass':True,'files':len(manifest['files']),'source_members':len(sources),'model_members':len(model_manifest),'extra_dependencies':len(extra)}),flush=True)


if __name__=='__main__':main()
