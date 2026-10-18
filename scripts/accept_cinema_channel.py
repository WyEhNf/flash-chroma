"""唯一冻结Cinema候选：四独立原表/逐级整数oracle/实际原生链/百图集中终验。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'python'));sys.path.insert(0,str(ROOT/'experiments/channel-runtime'))
import numba
import numpy as np
from PIL import Image
from lutlab import channel_coordinates as cc,io,study_provenance
from channel_native import Library
from accept_channel_coordinates import aggregate,changes,hist_metrics
from run_channel_coordinates import digest,read,checked
from verify_channel_coordinates import integer_oracle

def keys(rgb):return rgb.astype(np.int64)@np.array([65536,256,1],np.int64)
def squared(a,b):
    delta=a.astype(np.int32)-b.astype(np.int32)
    return np.sum(delta*delta,axis=1,dtype=np.int32)
def histogram(a,b):return np.bincount(squared(a,b),minlength=3*255**2+1)
def save(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.plan=args.plan.resolve();args.output=args.output.resolve()
    if args.output.exists():raise ValueError('不覆盖完整终验')
    plan=read(args.plan);paths={n:checked(s) for n,s in plan['inputs'].items()}
    policy=read(paths['policy']);gates=policy['numeric_gates'];numba.set_num_threads(4)
    run,selection,optimizer=[read(paths[k]) for k in ('fit_run','fit_selection','optimizer')]
    identity=dict(run);identity.pop('identity_sha256')
    if (study_provenance.identity_digest(identity)!=run['identity_sha256']
            or selection['run_identity']!=run['identity_sha256'] or not selection['selected'] or selection['failures']
            or selection['representation_sha256']!=plan['inputs']['candidate']['sha256']
            or any(digest(ROOT/n)!=h for n,h in run['source_sha256'].items())
            or optimizer['training_cap_violations'] or optimizer['coordinate_fresh_mismatches'] or optimizer['node_fresh_mismatches']):
        raise ValueError('拟合身份、固定选择、源码或fresh/cap前置条件不符')
    old,old_run=read(paths['baseline_results']),read(paths['baseline_run'])
    if (old_run['identity_sha256']!=study_provenance.identity_digest(old_run['identity'])
            or old['run_identity']!=old_run['identity_sha256'] or not old['acceptance']['accepted']
            or old['model_sha256']!=run['baseline_chain_model_sha256']
            or old['model_sha256'][0]!=plan['inputs']['baseline_model']['sha256']
            or old['cube']['prediction_sha256']!=plan['inputs']['baseline_stream']['sha256']
            or run['plan']['inputs']['initial']!=plan['inputs']['baseline_model']
            or run['plan']['inputs']['baseline_stream']!=plan['inputs']['baseline_stream']
            or run['plan']['tables']!=plan['tables'] or run['plan']['suffix_models']!=plan['suffix_models']):
        raise ValueError('已验af974基线、四原表或后三模型身份不同')
    for spec in plan['tables']+plan['suffix_models']:checked(spec)
    if [s['sha256'] for s in plan['suffix_models']]!=old['model_sha256'][1:]:raise ValueError('实际后缀模型不同')
    caps_meta=read(paths['cap_metadata'])
    if (caps_meta!=run['derived_cap'] or caps_meta['new_caps_file_sha256']!=plan['inputs']['caps']['sha256']
            or caps_meta['source_stream_sha256']!=plan['inputs']['baseline_stream']['sha256']
            or caps_meta['af974_initial_violations'] or caps_meta['new_greater_than_old_colours']
            or caps_meta['int32_vector_vs_independent_channel_int64_mismatches']):raise ValueError('新锚点约束身份或关系不符')
    data=np.load(paths['candidate']);baseline=io.load_sparse(paths['baseline_model'],competition=True)
    model=cc.ChannelLut(data['grid'],data['nodes'],data['shared_idx'],data['channel_frac']);cc.validate(model)
    if (str(data['format'])!='channel_coordinates_v1_experimental'
            or str(data['source_model_sha256'])!=plan['inputs']['baseline_model']['sha256']
            or str(data['baseline_model_sha256'])!=plan['inputs']['baseline_model']['sha256']
            or str(data['direct_parent_coordinate_checkpoint_sha256'])!=optimizer['coordinate_checkpoint_sha256']
            or data['frozen_suffix_model_sha256'].tolist()!=old['model_sha256'][1:]
            or not np.array_equal(model.grid,baseline.grid) or not np.array_equal(model.idx,baseline.tables()[0])
            or not np.array_equal(model.channel_frac[:,:,[0,255]],cc.from_sparse(baseline).channel_frac[:,:,[0,255]])):
        raise ValueError('候选表示、来源、父阶段、grid/idx或端点不同')
    native_contract=read(paths['native_contract']);lib=Library(paths['library'],plan['inputs']['library']['sha256'])
    if not native_contract['pass'] or native_contract['library_sha256']!=lib.sha256 or lib.capabilities!=7 or lib.revision!=2:
        raise ValueError('packed原生集中合同、DLL或CPU/OS能力不同')
    if any(digest(ROOT/n)!=h for n,h in native_contract['source_sha256'].items()):raise ValueError('原生合同源码变化')
    rows=read(paths['manifest'])['images'];partition=read(paths['partition'])
    groups={'training60':[r['id'] for r in partition['training']['images']],
        'guard20':[r['id'] for r in partition['guard']['images']],'audit20':partition['audit_ids']}
    ids=[v for a in groups.values() for v in a]
    if len(rows)!=100 or [len(v) for v in groups.values()]!=[60,20,20] or len(set(ids))!=100 or set(ids)!={r['id'] for r in rows}:
        raise ValueError('不是原100图互斥60/20/20分组')
    manifest_rows={r['id']:r for r in rows}
    for name in ('training','guard'):
        for r in partition[name]['images']:
            if r['file_sha256']!=manifest_rows[r['id']]['evaluation']['sha256']:raise ValueError('分组图像SHA不同')
    if [r['image'] for r in old['photos']['per_image']]!=[r['id'] for r in rows]:raise ValueError('旧照片顺序不同')
    suffix_models=[io.load_sparse(checked(s),competition=True) for s in plan['suffix_models']]
    suffix_oracle=[cc.from_sparse(s) for s in suffix_models]
    tables=[io.load_full(checked(s),mmap=True).reshape(-1,3) for s in plan['tables']]
    reference=np.load(paths['reference'],mmap_mode='r');cache=np.load(paths['suffix_cache'],mmap_mode='r')
    caps=np.load(paths['caps'],mmap_mode='r');old_cube=np.memmap(paths['baseline_stream'],np.uint8,'r',shape=(256**3,3))
    if reference.shape!=(256**3,3) or reference.dtype!=np.uint8 or cache.shape!=reference.shape or cache.dtype!=np.uint8 or caps.shape!=(256**3,) or caps.dtype!=np.int32:
        raise ValueError('冻结参考/后缀/cap布局不同')
    names=[Path(__file__).relative_to(ROOT).as_posix(),'scripts/accept_channel_coordinates.py',
        'scripts/run_channel_coordinates.py','scripts/verify_channel_coordinates.py','experiments/channel-runtime/channel_native.py',
        'python/lutlab/channel_coordinates.py','python/lutlab/io.py','python/lutlab/study_provenance.py',args.plan.relative_to(ROOT).as_posix()]
    sources={n:digest(ROOT/n) for n in names}|native_contract['source_sha256']
    args.output.mkdir(parents=True)
    base_path=args.output/'candidate-base.slut';side=args.output/'channel-frac.bin'
    io.save_sparse(base_path,io.SparseLut(model.grid,model.nodes,model.idx,baseline.tables()[1]))
    restored=io.load_sparse(base_path,competition=True)
    for a,b in [(restored.grid,model.grid),(restored.nodes,model.nodes),(restored.idx,model.idx)]:np.testing.assert_array_equal(a,b)
    model.channel_frac.astype('<u4').tofile(side)
    info={'purpose':__doc__,'plan':plan,'source_sha256':sources,'fit_identity':run['identity_sha256'],
        'environment':study_provenance.environment_fingerprint(),'numba_threads':4,'library_sha256':lib.sha256,
        'abi':1,'revision':lib.revision,'capabilities':lib.capabilities,'sidecar_sha256':digest(side),'candidate_base_sha256':digest(base_path)}
    info['identity_sha256']=study_provenance.identity_digest(info);save(args.output/'run.json',info)
    with zipfile.ZipFile(args.output/'measured-source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for n,h in sources.items():
            if digest(ROOT/n)!=h:raise ValueError('冻结源码变化')
            z.write(ROOT/n,n)
    hist=np.zeros(3*255**2+1,np.int64);own_hist=np.zeros_like(hist)
    old_hist=np.zeros_like(hist);worst_ids=np.empty(0,np.int64);worst_d2=np.empty(0,np.int32)
    hashes={k:hashlib.sha256() for k in ('reference','single_oracle','chain_oracle','single_scalar','single_avx2','chain_scalar','chain_avx2')}
    violations=0
    with lib.chain([base_path],[side]) as single,lib.chain([base_path,*[checked(s) for s in plan['suffix_models']]],[side,None,None,None]) as chain:
        memory={'single':single.model_bytes,'actual_four':chain.model_bytes}
        print('开始唯一实际四级完整256³：四原表RGB8、独立逐级u64、单级/整链标量1与AVX2请求4',flush=True)
        with (args.output/'cube.rgb').open('wb') as stream:
            for start in range(0,256**3,65536):
                indexes=np.arange(start,start+65536,dtype=np.int64)
                rgb=np.column_stack((indexes>>16,(indexes>>8)&255,indexes&255)).astype(np.uint8)
                truth=rgb
                for table in tables:truth=table[keys(truth)]
                np.testing.assert_array_equal(truth,reference[start:start+len(rgb)])
                own=integer_oracle(model,rgb);np.testing.assert_array_equal(own,cc.predict(model,rgb))
                final=own
                for sparse in suffix_oracle:final=integer_oracle(sparse,final)
                np.testing.assert_array_equal(final,cache[keys(own)])
                for case,operator,expected in [('single',single,own),('chain',chain,final)]:
                    hashes[case+'_oracle'].update(expected.tobytes())
                    for kernel,threads in [('scalar',1),('avx2',4)]:
                        actual=operator.apply(rgb.copy(),kernel=kernel,threads=threads)
                        np.testing.assert_array_equal(actual,expected);hashes[case+'_'+kernel].update(actual.tobytes())
                d2=squared(final,truth);hist+=np.bincount(d2,minlength=len(hist));own_hist+=histogram(own,tables[0][start:start+len(rgb)])
                old_d2=squared(old_cube[start:start+len(rgb)],truth);old_hist+=np.bincount(old_d2,minlength=len(hist))
                np.testing.assert_array_equal(caps[start:start+len(rgb)],np.maximum(49,old_d2))
                violations+=int(np.count_nonzero(d2>caps[start:start+len(rgb)]))
                hashes['reference'].update(truth.tobytes());stream.write(final.tobytes())
                top=np.argsort(-d2,kind='stable')[:128]
                worst_ids=np.r_[worst_ids,indexes[top]];worst_d2=np.r_[worst_d2,d2[top]]
                keep=np.lexsort((worst_ids,-worst_d2))[:128];worst_ids=worst_ids[keep];worst_d2=worst_d2[keep]
        digests={n:h.hexdigest() for n,h in hashes.items()}
        if digests['reference']!=old['cube']['reference_sha256'] or digest(args.output/'cube.rgb')!=digests['chain_oracle']:
            raise AssertionError('完整独立参考/新流SHA不同')
        old_measured=hist_metrics(old_hist)
        for n in ('mean','rms','p99','max','cvar_1pct'):
            if abs(old_measured[n]-old['cube'][n])>1e-12:raise ValueError('旧全域指标无法重现')
        output=np.memmap(args.output/'cube.rgb',np.uint8,'r',shape=reference.shape)
        cube=hist_metrics(hist)|{'prediction_sha256':digests['chain_oracle'],'reference_sha256':digests['reference'],
            'cap_violations':violations,'integer_oracle_channel_mismatches':0,
            'hotspots':[{'rgb':[int(k>>16),int((k>>8)&255),int(k&255)],'squared_distance':int(d),
                'prediction':output[k].tolist(),'reference':reference[k].tolist()} for k,d in zip(worst_ids,worst_d2)]}
        print('完整cube',json.dumps({k:cube[k] for k in ('mean','rms','p99','max','cvar_1pct')},ensure_ascii=False),flush=True)
        image_values=[];native_photo_hash=hashlib.sha256();photo_hist=np.zeros_like(hist);old_photo_hist=np.zeros_like(hist)
        for i,row in enumerate(rows):
            p=checked(row['evaluation'])
            with Image.open(p) as image:
                if image.mode!='RGB' or image.size!=(1024,768):raise ValueError('非1024x768 RGB8照片')
                rgb=np.asarray(image).reshape(-1,3).copy()
            index=keys(rgb);truth=reference[index]
            actual=chain.apply(rgb.copy(),kernel='avx2',threads=4);np.testing.assert_array_equal(actual,output[index])
            h=histogram(actual,truth);photo_hist+=h;old_photo_hist+=histogram(old_cube[index],truth)
            native_photo_hash.update(actual.tobytes())
            group=next(g for g,members in groups.items() if row['id'] in members)
            image_values.append({'image':row['id'],'group':group,'input_file_sha256':row['evaluation']['sha256'],
                'prediction_sha256':hashlib.sha256(actual.tobytes()).hexdigest(),**hist_metrics(h)})
            if (i+1)%20==0:print(f'实际四级原生照片 {i+1}/100',flush=True)
    photos=aggregate(image_values);photos['merged']=hist_metrics(photo_hist);photos['merged_p99']=photos['merged']['p99']
    photos['output_sha256']=native_photo_hash.hexdigest()
    old_photos=dict(old['photos']);old_photos['mean_image_cvar_1pct']=float(np.mean([r['cvar_1pct'] for r in old_photos['per_image']]))
    old_photos['merged']=hist_metrics(old_photo_hist);old_photos['merged_p99']=old_photos['merged']['p99']
    for n in ('mean','rms','worst_image_p99','max'):
        if abs(aggregate(old_photos['per_image'])[n]-old_photos[n])>1e-12:raise ValueError('旧百图汇总不能重现')
    grouped={}
    for name,members in groups.items():
        old_rows=[r for r in old_photos['per_image'] if r['image'] in members];new_rows=[r for r in image_values if r['image'] in members]
        grouped[name]={'baseline':aggregate(old_rows),'candidate':aggregate(new_rows),'changes':changes(old_rows,new_rows)}
    failures=[];tol=gates['tolerance']
    for metric in gates['cube_nonregression']:
        if cube[metric]>old['cube'][metric]+tol:failures.append('cube.'+metric)
    for metric in gates['photos_nonregression']:
        if photos[metric]>old_photos[metric]+tol:failures.append('photos.'+metric)
    if cube['mean']>(1-gates['cube_mean_reduction_min'])*old['cube']['mean']:failures.append('cube.mean_reduction_3pct')
    if photos['mean']>(1-gates['photos_mean_reduction_min'])*old_photos['mean']:failures.append('photos.mean_reduction_3pct')
    if not (cube['p99']<=(1-gates['p99_reduction_in_at_least_one_min'])*old['cube']['p99']
            or photos['worst_image_p99']<=(1-gates['p99_reduction_in_at_least_one_min'])*old_photos['worst_image_p99']):failures.append('p99_reduction_3pct')
    for group in gates['groups']:
        for metric in gates['groups_nonregression']:
            if grouped[group]['candidate'][metric]>grouped[group]['baseline'][metric]+tol:failures.append(group+'.'+metric)
    if violations:failures.append('full_colour_caps')
    if any(digest(ROOT/n)!=h for n,h in sources.items()):raise ValueError('终验源码变化')
    np.savez_compressed(args.output/'histograms.npz',cube=hist,baseline_cube=old_hist,first_stage=own_hist,
        photos=photo_hist,baseline_photos=old_photo_hist,top_keys=worst_ids,top_squared=worst_d2)
    result={'run_identity':info['identity_sha256'],'representation_sha256':plan['inputs']['candidate']['sha256'],
        'cube':cube,'photos':photos,'groups':grouped,'first_stage_vs_independent_T1':hist_metrics(own_hist),
        'baseline':{'cube':old['cube'],'photos':old_photos,'model_sha256':old['model_sha256']},
        'per_image_changes':changes(old_photos['per_image'],image_values),
        'native':{'pass':True,'library_sha256':lib.sha256,'cube_sha256':digests,'model_accounting_bytes':memory,
            'scalar_threads':1,'avx2_requested_threads':4,'cube_pixels':256**3,'photos':100,'byte_mismatches':0,
            'reached_suffix_cache_byte_mismatches':0},
        'candidate_base_sha256':digest(base_path),'sidecar_sha256':digest(side),
        'serialized_four_input_bytes':base_path.stat().st_size+sum(checked(s).stat().st_size for s in plan['suffix_models'])+side.stat().st_size,
        'prototype_sidecar_bytes':side.stat().st_size,'logical_fraction_extra_bytes':6144,
        'acceptance':{'accepted':not failures,'failed':failures},'performance_evaluation_performed':False,
        'default_promoted':False,'scope':policy['limits']}
    save(args.output/'results.json',result)
    print(json.dumps({'acceptance':result['acceptance'],'cube':{k:cube[k] for k in ('mean','rms','p99','max','cvar_1pct')},
        'photos':{k:photos[k] for k in ('mean','rms','worst_image_p99','merged_p99','max','mean_image_cvar_1pct')},
        'per_image_changes':result['per_image_changes']},ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':main()
