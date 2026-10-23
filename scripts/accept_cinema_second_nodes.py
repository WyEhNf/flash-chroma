"""第二级候选的四原表真值、完整四级uint64、两原生配置和历史百图独立验收。"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'python'))
sys.path.insert(0,str(ROOT/'experiments/channel-runtime'))
import numba
import numpy as np
from PIL import Image
from lutlab import channel_coordinates as cc,io,study_provenance
from channel_native import Library
from run_channel_tail_nodes import load_model,digest,save
from verify_channel_coordinates import integer_oracle
from accept_channel_coordinates import hist_metrics,changes


def histogram(prediction,reference):
    delta=prediction.astype(np.int32)-reference.astype(np.int32)
    return np.bincount(np.sum(delta*delta,axis=1,dtype=np.int32),minlength=3*255**2+1)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cache-root',type=Path,required=True)
    p.add_argument('--trial',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--library',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖完整独立终验')
    args.output.mkdir(parents=True);numba.set_num_threads(4);cache=args.cache_root.resolve()
    summary=json.loads((args.trial/'summary.json').read_text(encoding='utf-8'));candidate=args.trial/'candidate'
    if not summary['eligible_for_independent_final_checks']:raise ValueError('拟合门禁未通过')
    suffix_paths=[candidate/'stage2.slut',cache/'artifacts/cinema-envelope-v1/stage4_sweep004/selected-stage3.slut',candidate/'stage4.slut']
    expected={candidate/'model.npz':'0ea0a380b83e3581668654f45a7aa5682515b2dfb6ef7c8aeb96f82f60afa030',
        suffix_paths[0]:summary['stage2_sha256'],suffix_paths[1]:'95cb685e2298c49744cf91502bc06a3f8f20e97d1e654872ba1cfd59a48e7234',
        suffix_paths[2]:'5b8be3d4125b6676eb694749622ff9574b5b79bc18318bee7f504e601a519386',
        candidate/'candidate-base.slut':'73dc15fea4db5fb10a481336e18256cff040ca291a9713dc1c383ad84739b5ad',
        candidate/'channel-frac.bin':'85b045f0247aca016f986b61237302d4f812705d71a390226b8df04189dd7fff',
        args.baseline:'373a2fcbe4fafb73a6daebfd5c71b3308cdb43baf289e37fc564e75dc9033aed',
        args.library:'58591a725d367dce3713ff88af4d5549afea5af1ac4f3a39284443586893c158'}
    for path,value in expected.items():
        if digest(path)!=value:raise ValueError('候选/基线/原生输入身份改变：'+str(path))
    plan=json.loads((ROOT/'experiments/cinema-current-anchor-v1.json').read_text(encoding='utf-8'))
    tables=[]
    for spec in plan['tables']:
        path=cache/spec['path']
        if digest(path)!=spec['sha256']:raise ValueError('独立四原表身份改变')
        tables.append(io.load_full(path,mmap=True).reshape(-1,3))
    reference=np.load(cache/'artifacts/cinema-axis-calibration-v1/envelope-reference.npy',mmap_mode='r')
    baseline=np.memmap(args.baseline,np.uint8,'r',shape=(256**3,3));output=np.memmap(args.output/'candidate.rgb',np.uint8,'w+',shape=(256**3,3))
    first=load_model(candidate/'model.npz');suffix_models=[cc.from_sparse(io.load_sparse(path,competition=True)) for path in suffix_paths]
    toolchain=os.add_dll_directory('E:/mingw64/bin');dll_dir=os.add_dll_directory(str(args.library.resolve().parent))
    library=Library(args.library,expected[args.library]);old_hist=np.zeros(3*255**2+1,np.int64);hist=old_hist.copy()
    hashes={name:hashlib.sha256() for name in ('oracle','scalar','avx2','reference')}
    sources=[Path(__file__),ROOT/'scripts/run_channel_tail_nodes.py',ROOT/'scripts/verify_channel_coordinates.py',
        ROOT/'scripts/accept_channel_coordinates.py',ROOT/'experiments/channel-runtime/channel_native.py',
        *[ROOT/'python/lutlab'/name for name in ('channel_coordinates.py','io.py','interp.py','study_provenance.py')]]
    save(args.output/'identity.json',{'inputs':{str(path):value for path,value in expected.items()},
        'sources':{path.relative_to(ROOT).as_posix():digest(path) for path in sources},'original_tables':plan['tables'],
        'trial_summary_sha256':digest(args.trial/'summary.json'),'environment':study_provenance.environment_fingerprint(),
        'numba_threads':4,'native_configurations':[{'kernel':'scalar','threads':1},{'kernel':'avx2','threads':4}],
        'scope':'完整域四原表真值、独立四级uint64及两原生配置；历史百图只验不调；无性能计时/官方阈值判分。'})
    with library.chain([candidate/'candidate-base.slut',*suffix_paths],[candidate/'channel-frac.bin',None,None,None]) as native:
        for start in range(0,256**3,65536):
            keys=np.arange(start,start+65536,dtype=np.int64)
            rgb=np.column_stack((keys>>16,(keys>>8)&255,keys&255)).astype(np.uint8)
            predicted=integer_oracle(first,rgb)
            for model in suffix_models:predicted=integer_oracle(model,predicted)
            truth=tables[0][keys]
            for table in tables[1:]:truth=table[truth.astype(np.int64)@np.array([65536,256,1],np.int64)]
            np.testing.assert_array_equal(truth,reference[start:start+65536])
            for name,kernel,threads in (('scalar','scalar',1),('avx2','avx2',4)):
                actual=native.apply(rgb.copy(),kernel=kernel,threads=threads)
                np.testing.assert_array_equal(actual,predicted);hashes[name].update(actual.tobytes())
            hashes['oracle'].update(predicted.tobytes());hashes['reference'].update(truth.tobytes())
            output[start:start+65536]=predicted;hist+=histogram(predicted,truth)
            old_hist+=histogram(baseline[start:start+65536],truth)
        output.flush();photo_rows=[];old_rows=[];photo_hist=np.zeros_like(hist);old_photo_hist=np.zeros_like(hist)
        manifest_path=cache/'assets/photos/manifest.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        if digest(manifest_path)!='10893812e0d3cecea7ba8b6bbf4700addd09927feed220149501def03c374f7c':raise ValueError('照片manifest改变')
        for row in manifest['images']:
            path=cache/row['evaluation']['path']
            if digest(path)!=row['evaluation']['sha256']:raise ValueError('照片改变')
            with Image.open(path) as image:rgb=np.asarray(image).reshape(-1,3).copy()
            keys=rgb.astype(np.int64)@np.array([65536,256,1],np.int64)
            actual=native.apply(rgb,kernel='avx2',threads=4);np.testing.assert_array_equal(actual,output[keys])
            h=histogram(actual,reference[keys]);old=histogram(baseline[keys],reference[keys]);photo_hist+=h;old_photo_hist+=old
            photo_rows.append({'image':row['id'],**hist_metrics(h),'prediction_sha256':hashlib.sha256(actual.tobytes()).hexdigest()})
            old_rows.append({'image':row['id'],**hist_metrics(old)})
        memory=native.model_bytes
    dll_dir.close();toolchain.close();before=hist_metrics(old_hist);after=hist_metrics(hist)
    before_photos=hist_metrics(old_photo_hist);after_photos=hist_metrics(photo_hist)
    after_photos.update(per_image=photo_rows,worst_image_p99=max(row['p99'] for row in photo_rows),changes=changes(old_rows,photo_rows))
    passed=all(after[key]<=before[key]+1e-12 and after_photos[key]<=before_photos[key]+1e-12 for key in ('mean','rms','p99','max','cvar_1pct'))
    passed=passed and (after['p99']<before['p99'] or after['max']<before['max'])
    result={'baseline':before,'cube':after,'baseline_photos':{**before_photos,'per_image':old_rows},'photos':after_photos,
        'passed_aggregate':passed,'sha256':{name:h.hexdigest() for name,h in hashes.items()},'model_accounting_bytes':memory,
        'full_native_byte_mismatches':0,'photo_native_byte_mismatches':0,'library_sha256':digest(args.library),
        'scope':'完整域与100历史照片验收，不是四接口性能/盲测/官方得分；逐图恶化在changes与per_image保留。'}
    save(args.output/'results.json',result)
    print({'passed_aggregate':passed,'cube':after,'photos':{key:after_photos[key] for key in ('mean','p99','max')},'capacity':memory},flush=True)


if __name__=='__main__':main()
