"""封存完成的测量，发布相对路径模型包与可实际执行的连续目标目录。"""
from __future__ import annotations
import argparse
import copy
import json
import os
from pathlib import Path
import shutil
import struct
import zipfile
import flash_chroma_support as support
import p16_frontier


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--measurement',type=Path,required=True)
    parser.add_argument('--quality',type=Path,required=True)
    parser.add_argument('--model-manifest',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--models-output',type=Path,required=True)
    args=parser.parse_args()
    raw=json.loads((args.measurement/'results.json').read_text(encoding='utf-8'))
    catalog=json.loads((args.measurement/'catalog.json').read_text(encoding='utf-8'))
    quality=json.loads(args.quality.read_text(encoding='utf-8'))
    if raw.get('completed') is not True:
        raise ValueError('测量尚未完成，拒绝发布')
    if (not quality.get('passed') or quality['library']['sha256']!=raw['library']['sha256']
            or quality['manifest']['sha256']!=support.digest(args.model_manifest)):
        raise ValueError('完整域证据与实际库或源模型清单不一致')
    if args.output.exists() or args.models_output.exists():
        raise FileExistsError('发布目录已存在，拒绝覆盖')
    value,models=support.load_models(args.model_manifest)
    root=Path(value.get('path_root',args.model_manifest.resolve().parent))
    if not root.is_absolute(): root=args.model_manifest.resolve().parent/root
    sources=value.get('original_luts',raw['reference_source_luts'])
    source_sha=value.get('source_luts_sha256',[record['sha256'] for record in sources])
    if source_sha!=[record['sha256'] for record in raw['reference_source_luts']]:
        raise ValueError('原始LUT与测量来源不一致')
    if any(model['profile'] not in models for model in catalog['models'].values()):
        raise ValueError('发布模型没有包含全部已测profile')
    args.output.mkdir(parents=True)
    (args.models_output/'objects').mkdir(parents=True)
    manifest={'default_profile':value.get('default_profile',next(iter(models))),'interpolation_basis':'tetra_q16','path_root':'.',
        'source_luts_sha256':source_sha,'original_luts':sources,
        'profiles':{}, 'note':'源LUT身份固定；新LUT重新拟合并整链验证，全批固定参数。'}
    for name,model in models.items():
        profile=copy.deepcopy(model.profile)
        for record in profile['models']+[r for r in profile['sidecars'] if r]:
            source=Path(record['path'])
            if not source.is_absolute(): source=root/source
            payload=source.read_bytes()
            target=args.models_output/'objects'/record['sha256']
            if not target.exists(): target.write_bytes(payload)
            if support.digest(target)!=record['sha256']:
                raise ValueError('发布模型摘要不同')
            record['path']='objects/'+record['sha256']
            record['bytes']=len(payload)
        profile['m']=[struct.unpack_from('<I',(args.models_output/r['path']).read_bytes(),8)[0]
                      for r in profile['models']]
        profile['fixed_for_entire_batch']=True
        profile['interpolation_basis']='tetra_q16'
        profile['source_luts_sha256']=manifest['source_luts_sha256']
        manifest['profiles'][name]=profile
    manifest['licenses']=[]
    for index,record in enumerate(value.get('licenses',[])):
        source=Path(record['path'])
        if not source.is_absolute(): source=root/source
        if support.digest(source)!=record['sha256']: raise ValueError('源许可摘要不符')
        name=source.name
        if name.casefold() in ('manifest.json','objects'):
            name=f'license-{index:02d}-'+name
        destination=args.models_output/name
        if destination.exists() and support.digest(destination)!=record['sha256']:
            name=f'{index:02d}-'+name;destination=args.models_output/name
        if not destination.exists(): shutil.copyfile(source,destination)
        manifest['licenses'].append({'path':name,'sha256':record['sha256']})
    manifest_path=args.models_output/'manifest.json'
    support.write_json(manifest_path,manifest)
    for model in catalog['models'].values():
        model['manifest']=Path(os.path.relpath(manifest_path,args.output)).as_posix()
        model['manifest_sha256']=support.digest(manifest_path)
    for row in catalog['candidates']:
        record_id=row['evidence'].rsplit('#',1)[1]
        row['evidence']='results.json#'+record_id
    p16_frontier.validate_catalog(catalog)
    support.write_json(args.output/'catalog.json',catalog)
    shutil.copyfile(args.measurement/'results.json',args.output/'results.json')
    shutil.copyfile(args.quality,args.output/'quality.json')
    # 原始计划、逐图误差、实际执行字节及中断v1独立归档；不覆盖原值。
    with zipfile.ZipFile(args.output/'raw-evidence.zip','x',compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(args.measurement.rglob('*')):
            if path.is_file(): archive.write(path,'measurement/'+path.relative_to(args.measurement).as_posix())
        partial=args.measurement.parent/'frontier-measure-v1'
        for path in sorted(partial.glob('*.json')):
            archive.write(path,'interrupted-v1/'+path.name)
        for name in ('compact17','compact25','mixed'):
            for path in sorted((args.model_manifest.parent/name).glob('*.json')):
                archive.write(path,'fitting/'+name+'/'+path.name)
        build=args.measurement.parent/'single-header-build'
        for path in (build/'compile_commands.json',build/'libflash_chroma_bridge.dll.build.json',
                     build/'libflash_chroma_bridge.so.build.json'):
            if path.exists(): archive.write(path,'build/'+path.name)
    members={}
    for path in sorted(args.output.iterdir()):
        if path.is_file(): members[path.name]={'sha256':support.digest(path),'bytes':path.stat().st_size}
    support.write_json(args.output/'manifest.json',{'members':members,'model_manifest_sha256':support.digest(manifest_path),
        'models_scope':'同源SLUT和sidecar对象精确去重，包体与运行RAM分开。'})
    print('已发布',len(catalog['candidates']),'个实测点、',len(manifest['profiles']),'套固定模型')


if __name__=='__main__': main()
