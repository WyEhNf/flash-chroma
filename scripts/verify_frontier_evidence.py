"""核对归档摘要、逐配置统计与模型身份；不把静态复算当作像素或性能重跑。"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics
import zipfile
import p16_frontier


def digest(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream,'sha256').hexdigest()


def verify(folder):
    folder=Path(folder).resolve()
    manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    for name,record in manifest['members'].items():
        path=folder/name
        if not path.is_file() or path.stat().st_size!=record['bytes'] or digest(path)!=record['sha256']:
            raise ValueError('归档成员身份不符：'+name)
    catalog=p16_frontier.validate_catalog(json.loads((folder/'catalog.json').read_text(encoding='utf-8')))
    raw=json.loads((folder/'results.json').read_text(encoding='utf-8'))
    quality=json.loads((folder/'quality.json').read_text(encoding='utf-8'))
    if raw.get('completed') is not True or not quality.get('passed') or quality['library']['sha256']!=raw['library']['sha256']:
        raise ValueError('缺少同一库的完成测量与完整域检查')
    records={row['id']:row for row in raw['records']}
    if len(records)!=20 or len(catalog['candidates'])!=40:
        raise ValueError('本阶段必须覆盖20种预声明配置及两种计时指标')
    model_count=0
    for model in catalog['models'].values():
        path=(folder/model['manifest']).resolve()
        if digest(path)!=model['manifest_sha256']: raise ValueError('模型清单摘要不符')
        values=json.loads(path.read_text(encoding='utf-8'))
        for profile in values['profiles'].values():
            for record in profile['models']+[r for r in profile['sidecars'] if r]:
                if digest(path.parent/record['path'])!=record['sha256']: raise ValueError('模型对象摘要不符')
        for license_record in values.get('licenses',[]):
            if digest(path.parent/license_record['path'])!=license_record['sha256']:
                raise ValueError('模型来源许可摘要不符')
        model_count=len(values['profiles'])
    with zipfile.ZipFile(folder/'raw-evidence.zip') as archive:
        for row in catalog['candidates']:
            name,identity=row['evidence'].rsplit('#',1)
            if name!='results.json' or identity not in records: raise ValueError('实际配置证据引用不符')
            original=records[identity];ctx=catalog['contexts'][row['context']]
            if row['config']!=original['config']: raise ValueError('目录改变了执行参数')
            if ctx['measurement_session']!=original['measurement_session']: raise ValueError('混用了测量场次')
            if ctx['build_id']!=raw['library']['sha256'] or ctx['dataset_sha256']!=raw['source_pixels_sha256']:
                raise ValueError('库或输入身份不符')
            environment=json.dumps(original['measurement_environment'],sort_keys=True,ensure_ascii=False).encode()
            if hashlib.sha256(environment).hexdigest()!=ctx['platform_id']: raise ValueError('平台身份不符')
            resources=original['resources'];metrics=row['metrics']
            if metrics['workspace_bytes']!=resources['arena_bytes'] or metrics['runtime_bytes']!=(
                resources['model_bytes']+resources['arena_bytes']+resources['object_bytes']+2*100*768*1024*3):
                raise ValueError('受控内存账单不符')
            cold='prepare-to-first' in ctx['timing_scope']
            time=original['prepare_to_first_ms'] if cold else statistics.median(original['hot_batch_ms'])
            if time!=metrics['batch_ms']: raise ValueError('时间中位或首批统计不符')
            ratios=[]
            for control in original['aa_controls']:
                observations=control['observations_ms']
                ratio=statistics.mean(observations[1])/statistics.mean(observations[0])
                if not math.isclose(ratio,control['ratio'],rel_tol=1e-12): raise ValueError('A/A比值不符')
                ratios.append(ratio)
            aa=all(.90<=x<=1.10 for x in ratios)
            if aa!=original['aa_pass'] or row['verified']['time_stable']!=(False if cold else aa):
                raise ValueError('A/A资格标记不符')
            prefix='measurement/sessions/'+original['measurement_session']+'/'
            accuracy=json.loads(archive.read(prefix+original['profile']+'-accuracy.json'))
            mean=math.fsum(r['delta_e_sum'] for r in accuracy['per_image'])/accuracy['pixels']
            if not math.isclose(mean,metrics['mean_error'],rel_tol=1e-12): raise ValueError('平均色差复算不符')
            if max(r['mean_delta_e'] for r in accuracy['per_image'])!=metrics['worst_image_mean']:
                raise ValueError('最差单图平均色差不符')
            if any(x!=original['batch_sha256'] for x in original['per_round_sha256']):
                raise ValueError('正式轮次输出不同')
        for session in raw['measurement_sessions']:
            prefix='measurement/sessions/'+session['id']+'/'
            payload=archive.read(prefix+'results.json')
            if hashlib.sha256(payload).hexdigest()!=session['original_results_sha256']:
                raise ValueError('原始场次记录被修改')
            for source,sha in raw['executed_sources'].items():
                if hashlib.sha256(archive.read(prefix+'executed-sources/'+source)).hexdigest()!=sha:
                    raise ValueError('实际执行源码身份不符：'+source)
    return {'passed':True,'configurations':len(records),'catalog_points':len(catalog['candidates']),
        'measurement_sessions':len(raw['measurement_sessions']),'contexts':len(catalog['contexts']),
        'model_profiles':model_count,'aa_pass':sum(row['aa_pass'] for row in records.values()),
        'scope':'成员SHA、模型SHA、场次/平台绑定、实际配置、指标复算与A/A资格；未重新执行像素映射或性能测量。'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(verify(args.evidence),ensure_ascii=False,indent=2))


if __name__=='__main__': main()
