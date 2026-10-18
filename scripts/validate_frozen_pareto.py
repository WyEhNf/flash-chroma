"""对已冻结且各选择指标非退化的研究候选做一次完整验收，不改原阶段门禁。"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'python'))
import numba
import numpy as np
from lutlab import error_analysis as ea,io,study_provenance
from lutlab.compatibility import write_json
from run_chain_error_study import cube_evaluate,digest,photos_evaluate
from run_joint_box_study import native_verify


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--executable',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('不覆盖已有研究验收')
    numba.set_num_threads(4)
    parent=ROOT/'artifacts/rounded-fullphotos-v1'
    selected=json.loads((parent/'selection.json').read_text(encoding='utf-8'))
    run=json.loads((parent/'run.json').read_text(encoding='utf-8'))
    if selected['run_identity']!=run['identity_sha256'] or run['identity_sha256']!=study_provenance.identity_digest(run['identity']):
        raise ValueError('父拟合身份不同')
    name='rounded_weighted_iter001'
    expected='dde48aa70bdd4fc51e47e56f5d6b01565f63c46cb81191cb35e806c1c3d4f43c'
    model_path=parent/name/'model.slut'
    if digest(model_path)!=expected or selected['candidates'][name]['model_sha256']!=expected:
        raise ValueError('冻结研究模型不同')
    value,baseline_sample=selected['candidates'][name]['samples'],selected['baseline_samples']
    for group in ('cube','photos','hotspots'):
        for key in ('mean','rms','p99','max','cvar_1pct'):
            if value[group][key]>baseline_sample[group][key]+1e-12:
                raise ValueError('研究候选选择指标退化')
    if value['photos']['worst_image_p99']>baseline_sample['photos']['worst_image_p99']+1e-12:
        raise ValueError('选择图最差p99退化')
    if value['cube']['mean']>.97*baseline_sample['cube']['mean'] or value['cube']['p99']>.97*baseline_sample['cube']['p99']:
        raise ValueError('没有预定的明显色域改善')
    plan=run['identity']['plan']
    if digest(args.executable)!=plan['executable_sha256'] or digest(ROOT/plan['table'])!=plan['table_sha256']:
        raise ValueError('程序或完整参考表不同')
    if digest(ROOT/'assets/photos/manifest.json')!=run['identity']['image_manifest_sha256']:
        raise ValueError('照片清单不同')
    full_path=parent/'historical-full-results.json'
    if digest(full_path)!=selected['historical_full_results_sha256']:
        raise ValueError('完整基线结果不同')
    old=json.loads(full_path.read_text(encoding='utf-8'))
    sources=[Path(__file__),ROOT/'python/lutlab/error_analysis.py',ROOT/'python/lutlab/interp.py',
        ROOT/'python/lutlab/io.py',ROOT/'python/lutlab/study_kernels.py',ROOT/'python/lutlab/runtime.py',
        ROOT/'scripts/run_chain_error_study.py',ROOT/'scripts/run_joint_box_study.py']
    identity={'kind':'frozen_pareto_research_evaluation','parent_run_identity':run['identity_sha256'],
        'model_sha256':expected,'baseline_model_sha256':plan['baseline_sha256'],
        'table_sha256':plan['table_sha256'],'executable_sha256':digest(args.executable),
        'baseline_results_sha256':digest(full_path),'parent_selection_sha256':digest(parent/'selection.json'),
        'image_manifest_sha256':digest(ROOT/'assets/photos/manifest.json'),
        'source_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in sources},
        'environment':study_provenance.environment_fingerprint(),
        'purpose':'原阶段未达到额外两种mean各3%，保留未入围；单独验证选择指标全非退化且色域mean/p99明显下降的冻结研究候选，不升级默认'}
    study_provenance.claim_run(args.output/'run.json',{'identity':identity,'identity_sha256':study_provenance.identity_digest(identity)})
    write_json(args.output/'selection-before-full.json',{'name':name,'model_sha256':expected,
        'original_phase_failures':selected['candidates'][name]['failures'],'sample_metrics':value,
        'new_default_promotion':False,'scope':identity['purpose']})
    with zipfile.ZipFile(args.output/'measured-source.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for path in sources:archive.write(path,str(path.relative_to(ROOT)).replace('\\','/'))
    model=io.load_sparse(model_path,competition=True)
    io.save_sparse(args.output/'model.slut',model)
    table=io.load_full(ROOT/plan['table'],mmap=True)
    print('冻结研究候选：完整256³、独立整数oracle/标量/AVX2',flush=True)
    cube=cube_evaluate([table],ea.Operator([model]),args.output/'cube.rgb',128)
    native=native_verify([model],args.output,cube['prediction_sha256'],args.executable)
    print(f"完整色域mean={cube['mean']:.6f} p99={cube['p99']:.6f} max={cube['max']:.6f}；进入100图",flush=True)
    photos=photos_evaluate([table],{'candidate':ea.Operator([model])})['candidate']
    failed=[]
    for key in ('mean','rms','p99','max','cvar_1pct'):
        if cube[key]>old['cube'][key]+1e-12:failed.append('cube.'+key)
    for key in ('mean','rms','worst_image_p99','max'):
        if photos[key]>old['photos'][key]+1e-12:failed.append('photos.'+key)
    cvar=lambda rows:float(np.mean([r['cvar_1pct'] for r in rows]))
    if cvar(photos['per_image'])>cvar(old['photos']['per_image'])+1e-12:failed.append('photos.mean_image_cvar_1pct')
    changes={}
    for key in ('mean','rms','p99','max','cvar_1pct'):
        counts={'better':0,'equal':0,'worse':0}
        for a,b in zip(old['photos']['per_image'],photos['per_image']):
            if a['image']!=b['image']:raise ValueError('逐图身份不同')
            delta=b[key]-a[key];counts['better' if delta<-1e-12 else 'worse' if delta>1e-12 else 'equal']+=1
        changes[key]=counts
    strict=(not failed and cube['mean']<=.97*old['cube']['mean'] and photos['mean']<=.97*old['photos']['mean']
        and (cube['p99']<=.97*old['cube']['p99'] or photos['worst_image_p99']<=.97*old['photos']['worst_image_p99']))
    result={'run_identity':study_provenance.identity_digest(identity),'model_sha256':expected,'baseline':old,
        'cube':cube,'photos':photos,'native':native,'full_nonregression_failures':failed,
        'original_strict_full_gate_met':strict,'per_image_changes':changes,'default_promoted':False,
        'scope':identity['purpose']+'；单级Velvia、RGB欧氏距离、历史照片已见，无官方Threshold，不是四级成绩'}
    write_json(args.output/'results.json',result)
    print(json.dumps({'cube':{k:cube[k] for k in ('mean','rms','p99','max')},
        'photos':{k:photos[k] for k in ('mean','rms','worst_image_p99','max')},'nonregression_failures':failed,
        'strict_full_gate_met':strict},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
