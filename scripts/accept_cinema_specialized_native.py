"""同一a399模型的专门化内核：复用已验oracle流，一次完整原生字节终验。"""
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
from lutlab import channel_coordinates as cc,study_provenance
from channel_native import Library
from native_provenance import verify_dependencies
from run_channel_coordinates import read,checked,digest
from verify_channel_coordinates import integer_oracle

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.plan=args.plan.resolve()
    if args.output.exists():raise ValueError('不覆盖原生等价证据')
    plan=read(args.plan);paths={k:checked(v) for k,v in plan['inputs'].items()}
    prior=read(paths['prior_full']);contract=read(paths['contract']);build=read(paths['build'])
    if (not prior['acceptance']['accepted'] or prior['acceptance']['failed'] or not prior['native']['pass']
            or prior['representation_sha256']!=plan['inputs']['model']['sha256']
            or prior['candidate_base_sha256']!=plan['inputs']['base']['sha256']
            or prior['sidecar_sha256']!=plan['inputs']['sidecar']['sha256']
            or prior['cube']['prediction_sha256']!=plan['inputs']['cube']['sha256']):raise ValueError('既有完整准确性/模型/输出身份不符')
    lib=Library(paths['library'],plan['inputs']['library']['sha256'])
    if not contract['pass'] or contract['library_sha256']!=lib.sha256 or lib.capabilities!=7:raise ValueError('新集中合同或实际能力不符')
    for n,h in contract['source_sha256'].items():
        if digest(ROOT/n)!=h:raise ValueError('数值源码与新合同不同')
    dependencies=verify_dependencies(paths['library'],build,loaded=True)
    data=np.load(paths['model']);model=cc.ChannelLut(data['grid'],data['nodes'],data['shared_idx'],data['channel_frac']);cc.validate(model)
    suffix=[checked(s) for s in plan['suffix_models']]
    prior_plan=read(paths['prior_run'])['plan']
    if plan['suffix_models']!=prior_plan['suffix_models']:raise ValueError('实际后三模型不同')
    expected=np.memmap(paths['cube'],np.uint8,'r',shape=(256**3,3))
    args.output.mkdir(parents=True)
    names=[Path(__file__).relative_to(ROOT).as_posix(),args.plan.relative_to(ROOT).as_posix(),
        'experiments/channel-runtime/native_provenance.py','experiments/channel-runtime/channel_native.py',
        'scripts/verify_channel_coordinates.py','python/lutlab/channel_coordinates.py']
    sources={n:digest(ROOT/n) for n in names}|contract['source_sha256']
    identity={'plan':plan,'source_sha256':sources,'environment':study_provenance.environment_fingerprint(),
        'loaded_dependencies':dependencies,'purpose':__doc__};identity['identity_sha256']=study_provenance.identity_digest(identity)
    (args.output/'run.json').write_text(json.dumps(identity,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with zipfile.ZipFile(args.output/'measured-source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for n in sources:z.write(ROOT/n,n)
    hashes={n:hashlib.sha256() for n in ('single_oracle','single_scalar','single_avx2','chain_scalar','chain_avx2')}
    photo_hash=hashlib.sha256();photos=[]
    with lib.chain([paths['base']],[paths['sidecar']]) as single,lib.chain([paths['base'],*suffix],[paths['sidecar'],None,None,None]) as chain:
        for start in range(0,256**3,65536):
            ids=np.arange(start,start+65536,dtype=np.int64)
            rgb=np.column_stack((ids>>16,(ids>>8)&255,ids&255)).astype(np.uint8)
            own=integer_oracle(model,rgb);hashes['single_oracle'].update(own.tobytes())
            for name,operator,truth in [('single',single,own),('chain',chain,expected[start:start+len(rgb)])]:
                for kernel,threads in [('scalar',1),('avx2',4)]:
                    actual=operator.apply(rgb.copy(),kernel=kernel,threads=threads)
                    np.testing.assert_array_equal(actual,truth);hashes[name+'_'+kernel].update(actual.tobytes())
        values={k:h.hexdigest() for k,h in hashes.items()}
        for name,h in values.items():
            target=prior['native']['cube_sha256']['single_oracle'] if name.startswith('single') else prior['cube']['prediction_sha256']
            if h!=target:raise AssertionError('完整域输出SHA与已有独立oracle不同')
        print('专门化单级/实际四级完整域标量1/AVX2请求4逐字节一致',flush=True)
        rows=read(paths['manifest'])['images'];previous=prior['photos']['per_image']
        if len(rows)!=100 or [r['id'] for r in rows]!=[r['image'] for r in previous]:raise ValueError('不是同顺序100图')
        for row,old in zip(rows,previous):
            with Image.open(checked(row['evaluation'])) as image:
                if image.mode!='RGB' or image.size!=(1024,768):raise ValueError('图片契约不同')
                rgb=np.asarray(image).reshape(-1,3).copy()
            key=rgb.astype(np.int64)@np.array([65536,256,1],np.int64)
            actual=chain.apply(rgb.copy(),kernel='avx2',threads=4);np.testing.assert_array_equal(actual,expected[key])
            h=hashlib.sha256(actual.tobytes()).hexdigest()
            if h!=old['prediction_sha256']:raise ValueError('实际照片字节与完整终验不同')
            photo_hash.update(actual.tobytes());photos.append({'image':row['id'],'prediction_sha256':h,'byte_mismatches':0})
        memory={'single':single.model_bytes,'actual_four':chain.model_bytes}
    if photo_hash.hexdigest()!=prior['photos']['output_sha256']:raise AssertionError('100图聚合SHA不同')
    if any(digest(ROOT/n)!=h for n,h in sources.items()):raise ValueError('终验期间源码变化')
    result={'pass':True,'run_identity':identity['identity_sha256'],'library_sha256':lib.sha256,
        'prior_full_results_sha256':plan['inputs']['prior_full']['sha256'],'representation_sha256':plan['inputs']['model']['sha256'],
        'cube':{'pixels':256**3,'sha256':values,'byte_mismatches':0},
        'photos':{'count':100,'output_sha256':photo_hash.hexdigest(),'per_image':photos,'byte_mismatches':0},
        'model_accounting_bytes':memory,'performance_calls':0,'new_fits':0,
        'scope':'同一模型与oracle完整流的后端等价，不新增精度选型/原表参考/全域拟合或性能；首次实际四级正确性完整来源在prior_full中。'}
    (args.output/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'pass':True,'cube_sha256':values,'photos':100,'model_accounting_bytes':memory},ensure_ascii=False))

if __name__=='__main__':main()
