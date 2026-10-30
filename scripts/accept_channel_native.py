"""冻结分通道模型的独立原生单级/四级等距控制及完整百图正确性。"""
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
from lutlab import channel_coordinates as cc, io, study_provenance
from channel_native import Library,digest


def checked(spec):
    p=ROOT/spec['path']
    if digest(p)!=spec['sha256']:raise ValueError(f'冻结输入SHA不同：{p}')
    return p


def effect(rgb):
    # cycleGBR -> invertRGB -> swapRG，各级输出仍为RGB8。
    return (255-rgb[:,[2,1,0]]).astype(np.uint8)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.plan=args.plan.resolve();args.output=args.output.resolve()
    if args.output.exists():raise ValueError('不覆盖原生验收')
    plan=json.loads(args.plan.read_text(encoding='utf-8'));paths={n:checked(v) for n,v in plan['inputs'].items()}
    previous=json.loads(paths['full_results'].read_text(encoding='utf-8'))
    selection=json.loads(paths['selection'].read_text(encoding='utf-8'))
    if (not previous['acceptance']['accepted'] or selection['failures'] or not selection['selected']
            or previous['representation_sha256']!=plan['inputs']['representation']['sha256']
            or selection['representation_sha256']!=previous['representation_sha256']
            or previous['cube']['prediction_sha256']!=plan['inputs']['cube']['sha256']):
        raise ValueError('候选尚未通过原固定精度门禁或身份不同')
    contract=json.loads(paths['contract'].read_text(encoding='utf-8'))
    lib=Library(paths['library'],plan['inputs']['library']['sha256'])
    if not contract['pass'] or contract['library_sha256']!=lib.sha256 or lib.capabilities!=7:raise ValueError('原生合同或CPU/OS能力不符')
    for n,h in contract['source_sha256'].items():
        if digest(ROOT/n)!=h:raise ValueError('原生数值源码与集中合同不同')
    base=io.load_sparse(paths['initial'],competition=True);npz=np.load(paths['representation'])
    if (not np.array_equal(base.nodes,npz['nodes']) or not np.array_equal(base.grid,npz['grid'])
            or not np.array_equal(base.idx,npz['shared_idx'])):raise ValueError('侧表的节点/idx/grid与base不对应')
    model=cc.ChannelLut(npz['grid'],npz['nodes'],npz['shared_idx'],npz['channel_frac']);cc.validate(model)
    controls=[checked(s) for s in plan['controls']]
    code=np.arange(256,dtype=np.uint8)
    expected_axes=[[1,2,0],[0,1,2],[1,0,2]]
    proofs=[]
    for index,p in enumerate(controls):
        sparse=io.load_sparse(p,competition=True)
        # 完整节点张量验证为置换/反相单轴依赖，再核256码值曲线。
        for channel,axis in enumerate(expected_axes[index]):
            slicer=[0,0,0,channel];slicer[axis]=slice(None)
            values=sparse.nodes[tuple(slicer)];shape=[1,1,1];shape[axis]=sparse.m
            if not np.array_equal(sparse.nodes[...,channel],np.broadcast_to(values.reshape(shape),(sparse.m,)*3)):raise ValueError('控制节点结构不精确')
            idx,frac=sparse.tables();f=frac[axis].astype(np.int64);cell=idx[axis].astype(np.intp)
            predicted=((values[cell].astype(np.int64)*(65536-f)+values[cell+1].astype(np.int64)*f+32768)>>16).astype(np.uint8)
            if not np.array_equal(predicted,255-code if index==1 else code):raise ValueError('控制并非全域整数精确等距')
        proofs.append({'model_sha256':digest(p),'m':sparse.m,'verified_full_node_values':sparse.nodes.size,'exact_codes':768,'axes':expected_axes[index]})
    args.output.mkdir(parents=True)
    side=args.output/'channel-frac.bin';model.channel_frac.astype('<u4').tofile(side)
    names=[Path(__file__).relative_to(ROOT).as_posix(),'experiments/channel-runtime/channel_native.py',args.plan.relative_to(ROOT).as_posix()]
    sources={n:digest(ROOT/n) for n in names}|contract['source_sha256']
    identity={'plan':plan,'source_sha256':sources,'environment':study_provenance.environment_fingerprint(),'capabilities':lib.capabilities,'sidecar_sha256':digest(side)}
    identity_sha=study_provenance.identity_digest(identity)
    (args.output/'run.json').write_text(json.dumps({'identity':identity,'identity_sha256':identity_sha},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with zipfile.ZipFile(args.output/'measured-source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for n,h in sources.items():
            if digest(ROOT/n)!=h:raise ValueError('冻结期间源码改变')
            z.write(ROOT/n,n)
    expected=np.memmap(paths['cube'],np.uint8,'r',shape=(256**3,3));cube_receipts=[]
    with lib.chain([paths['initial']],[side]) as single,lib.chain([paths['initial'],*controls],[side,None,None,None]) as chain:
        variants=[('single',single,False),('isometric_four',chain,True)]
        hashes={(name,kernel):hashlib.sha256() for name,_,_ in variants for kernel in ['scalar','avx2']}
        control_source_hashes=[hashlib.sha256() for _ in range(3)]
        for start in range(0,256**3,1<<16):
            ids=np.arange(start,start+(1<<16),dtype=np.int64)
            rgb=np.column_stack([ids>>16,(ids>>8)&255,ids&255]).astype(np.uint8)
            for h,values in zip(control_source_hashes,(rgb[:,[1,2,0]],255-rgb,rgb[:,[1,0,2]])):
                h.update(np.ascontiguousarray(values).tobytes())
            for name,operator,four in variants:
                truth=effect(expected[start:start+len(rgb)]) if four else expected[start:start+len(rgb)]
                for kernel,threads in [('scalar',1),('avx2',4)]:
                    actual=operator.apply(rgb.copy(),kernel=kernel,threads=threads)
                    np.testing.assert_array_equal(actual,truth);hashes[name,kernel].update(actual.tobytes())
        if [h.hexdigest() for h in control_source_hashes]!=plan['source_lut_sha256'][1:]:
            raise ValueError('控制原LUT的完整生成字节与历史SHA不同')
        for name,operator,four in variants:
            a,b=(hashes[name,k].hexdigest() for k in ['scalar','avx2'])
            if a!=b:raise AssertionError('两个原生后端全域SHA不同')
            if not four and a!=previous['cube']['prediction_sha256']:raise AssertionError('原生全域与独立u64不同')
            cube_receipts.append({'case':name,'scalar_threads':1,'avx2_threads':4,'prediction_sha256':a,'pixels':256**3,'byte_mismatches':0,'model_accounting_bytes':operator.model_bytes})
            print(name,'标量/AVX2完整色域一致',flush=True)
        photos=json.loads(paths['manifest'].read_text(encoding='utf-8'))['images']
        if len(photos)!=100:raise ValueError('不是冻结100图')
        photos_records=[];photo_hashes={name:hashlib.sha256() for name,_,_ in variants}
        for row in photos:
            p=checked(row['evaluation'])
            with Image.open(p) as image:
                if image.mode!='RGB' or image.size!=(1024,768):raise ValueError('图片不符合比赛RGB8契约')
                rgb=np.asarray(image).reshape(-1,3).copy()
            keys=rgb.astype(np.int64)@np.array([65536,256,1],np.int64)
            entry={'image':row['id'],'file_sha256':row['evaluation']['sha256'],'pixels':len(rgb)}
            for name,operator,four in variants:
                truth=effect(expected[keys]) if four else expected[keys]
                actual=operator.apply(rgb.copy(),kernel='avx2',threads=4);np.testing.assert_array_equal(actual,truth)
                h=hashlib.sha256(actual.tobytes()).hexdigest();entry[name+'_sha256']=h;photo_hashes[name].update(actual.tobytes())
            photos_records.append(entry)
    if any(digest(ROOT/n)!=h for n,h in sources.items()):raise ValueError('验收期间源码改变')
    result={'run_identity':identity_sha,'pass':True,'library_sha256':lib.sha256,'sidecar_sha256':digest(side),
        'cube':cube_receipts,'photos':{'count':100,'per_image':photos_records,'output_sha256':{n:h.hexdigest() for n,h in photo_hashes.items()},'byte_mismatches':0},
        'controls_full_structure_and_codes_proof':proofs,'source_lut_sha256':plan['source_lut_sha256'],
        'logical_fraction_extra_bytes':6144,'prototype_sidecar_bytes':side.stat().st_size,'base_file_bytes':paths['initial'].stat().st_size,
        'scope':plan['limits'],'performance_measured':False}
    (args.output/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'pass':True,'cube':cube_receipts,'photos':100,'sidecar_bytes':side.stat().st_size},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
