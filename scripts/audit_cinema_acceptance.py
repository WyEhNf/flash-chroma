"""审阅后集中补核依赖来源和旧逐图指标；只查旧已验完整流，不重跑模型。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'python'));sys.path.insert(0,str(ROOT/'experiments/channel-runtime'))
import numpy as np
from PIL import Image
from lutlab import study_provenance
from run_channel_coordinates import checked,digest,read
from accept_channel_coordinates import hist_metrics
from native_provenance import verify_dependencies

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',type=Path,required=True);parser.add_argument('--acceptance',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise ValueError('不覆盖补核证据')
    plan=read(args.plan);paths={n:checked(s) for n,s in plan['inputs'].items()}
    full=read(args.acceptance/'results.json');run=read(args.acceptance/'run.json')
    identity=dict(run);identity.pop('identity_sha256')
    if (not full['acceptance']['accepted'] or full['run_identity']!=run['identity_sha256']
            or study_provenance.identity_digest(identity)!=run['identity_sha256'] or run['plan']!=plan):raise ValueError('完整验收状态或身份不同')
    old=read(paths['baseline_results']);old_run=read(paths['baseline_run'])
    old_plan=old_run['identity']['plan']
    if old_plan['photo_manifest']!=plan['inputs']['manifest'] or old_plan['partition']!=plan['inputs']['partition']:
        raise ValueError('历史基线的图片字节清单/60-20-20分组与本轮不同')
    deps=verify_dependencies(paths['library'],read(paths['build']),loaded=False)
    with zipfile.ZipFile(args.acceptance/'measured-source.zip') as z:
        for n,h in run['source_sha256'].items():
            if hashlib.sha256(z.read(n)).hexdigest()!=h:raise ValueError('实测源码ZIP成员SHA不同')
    rows=read(paths['manifest'])['images'];cube=np.memmap(paths['baseline_stream'],np.uint8,'r',shape=(256**3,3))
    reference=np.load(paths['reference'],mmap_mode='r');receipts=[];merged=np.zeros(3*255**2+1,np.int64)
    if [r['id'] for r in rows]!=[r['image'] for r in old['photos']['per_image']]:raise ValueError('旧逐图次序不同')
    for row,previous in zip(rows,old['photos']['per_image']):
        p=checked(row['evaluation'])
        with Image.open(p) as image:
            if image.mode!='RGB' or image.size!=(1024,768):raise ValueError('图片契约不同')
            rgb=np.asarray(image).reshape(-1,3)
        index=rgb.astype(np.int64)@np.array([65536,256,1],np.int64)
        delta=cube[index].astype(np.int32)-reference[index].astype(np.int32)
        d2=np.sum(delta*delta,axis=1,dtype=np.int32);hist=np.bincount(d2,minlength=len(merged));merged+=hist
        measured=hist_metrics(hist)
        for metric in ('mean','rms','p99','max','cvar_1pct'):
            if abs(measured[metric]-previous[metric])>1e-12:raise ValueError('旧逐图实际流与历史指标不同：'+row['id']+'/'+metric)
        receipts.append({'image':row['id'],'input_sha256':row['evaluation']['sha256'],'n':len(rgb),'metric_mismatches':0})
    merged_metrics=hist_metrics(merged)
    for name in ('mean','rms','p99','max','cvar_1pct'):
        if abs(merged_metrics[name]-full['baseline']['photos']['merged'][name])>1e-12:raise ValueError('旧完整合并直方图不能重现')
    names=[Path(__file__).relative_to(ROOT).as_posix(),'experiments/channel-runtime/native_provenance.py',
        'scripts/accept_channel_coordinates.py','scripts/run_channel_coordinates.py','experiments/channel-runtime/channel_native.py']
    sources={n:digest(ROOT/n) for n in names};args.output.mkdir(parents=True)
    with zipfile.ZipFile(args.output/'measured-source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for n in sources:z.write(ROOT/n,n)
    record={'purpose':__doc__,'pass':True,'environment':study_provenance.environment_fingerprint(),
        'acceptance_results_sha256':digest(args.acceptance/'results.json'),'plan_sha256':digest(args.plan),
        'source_sha256':sources,'dependency_files':deps,'old_manifest_and_partition_exactly_equal':True,
        'old_photo_stream_lookup_count':100,'old_photo_metrics':receipts,'metric_mismatches':0,
        'new_model_mappings':0,'native_calls':0,'new_fits':0,'performance_calls':0,
        'scope':'原终验之后审阅发现来源核对可加强；仅一次补核冻结依赖邻接文件与旧完整流的100图直方图。未重跑新模型/原生/完整域或测速。此脚本不采样历史进程实际DLL模块路径；性能worker另核其当前实际已载路径。'}
    (args.output/'results.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'pass':True,'old_photo_lookup_count':100,'metric_mismatches':0,'dependency_files':len(deps)},ensure_ascii=False))

if __name__=='__main__':main()
