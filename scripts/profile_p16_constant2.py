"""只读筛查2³恒色RGB头：正常包直接RGB，无残差解码，异常包完整精确回退。"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import numpy as np
from PIL import Image
from study_p16_direct_compile import ROOT,Library,digest,save,models,direct,env
from palette_support import tables

def check(row):
    p=Path(row['path']);assert digest(p)==row['sha256'];return p

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    plan=json.loads(a.plan.read_text(encoding='utf-8'));assert digest(Path(__file__))==plan['script_sha256']
    if a.output.exists():raise FileExistsError('保留已有profile，不扫描参数或覆盖')
    a.output.mkdir(parents=True);save(a.output/'executed-plan.json',plan)
    dll_dir=os.add_dll_directory('E:/mingw64/bin') if os.name=='nt' else None
    lib=Library(check(plan['library']),plan['library']['sha256'])
    modelplan=json.loads(check(plan['model_plan']).read_text(encoding='utf-8'));role=modelplan['roles']['baseline']
    paths=[check(r) for r in role['models']];sides=[check(r) if r else None for r in role['sidecars']]
    with lib.chain(paths,sides) as chain:
        ids=direct(chain).view(np.uint8);_,palette=tables(chain)
    blocks=ids.reshape(128,2,128,2,128,2).transpose(0,2,4,1,3,5).reshape(-1,8)
    assert np.array_equal(blocks.reshape(128,128,128,2,2,2).transpose(0,3,1,4,2,5).reshape(-1),ids)
    normal=np.all(blocks==blocks[:,:1],axis=1)
    headers=np.where(normal,palette[blocks[:,0]],np.uint32(0x80000000)).astype(np.uint32)
    assert np.all(headers[normal]<1<<24) and np.all(headers[~normal]==0x80000000)
    assert np.all(palette[blocks[normal]]==headers[normal,None])
    manifest=json.loads(check(modelplan['manifest']).read_text(encoding='utf-8'));rows=[];hist=np.zeros(9,np.uint64);output=hashlib.sha256()
    for row in manifest['images']:
        path=Path(modelplan['data_root'])/row['evaluation']['path'];assert digest(path)==row['evaluation']['sha256']
        with Image.open(path) as image:frame=np.asarray(image)
        assert hashlib.sha256(frame.tobytes()).hexdigest()==row['evaluation']['pixel_sha256']
        red=frame[:,:,0].astype(np.uint32);green=frame[:,:,1].astype(np.uint32);blue=frame[:,:,2].astype(np.uint32)
        code=red|(green<<8)|(blue<<16);q=(red>>1)|((green>>1)<<7)|((blue>>1)<<14)
        counts=np.sum(normal[q].reshape(-1,8),axis=1);h=np.bincount(counts,minlength=9).astype(np.uint64);hist+=h
        expected=palette[ids[code]];all_normal=np.repeat(counts==8,8).reshape(red.shape)
        got=np.where(all_normal,headers[q],expected).astype(np.uint32);assert np.array_equal(got,expected)
        raw=got.view(np.uint8).reshape(*got.shape,4)[:,:,:3].copy().tobytes();output.update(raw)
        rows.append({'id':row['id'],'constant_lanes_histogram':h.tolist(),'all_normal_packages':int(h[8]),'packages':int(h.sum()),'all_normal_fraction':float(h[8]/h.sum())})
    whole=float(hist[8]/hist.sum());passed=whole>=plan['interest_gate']['all_normal_packages_min']
    assert output.hexdigest()=='f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528'
    result={'native_candidate_implemented':False,'performance_claim':False,'constant_blocks':int(normal.sum()),'blocks':normal.size,
        'constant_colors':int(normal.sum())*8,'header_bytes':headers.nbytes,'additional_header_bytes':headers.nbytes,
        'header_sha256':hashlib.sha256(headers.tobytes()).hexdigest(),'all_normal_packages_fraction':whole,
        'constant_lanes_histogram':hist.tolist(),'per_image':rows,'interest_gate_passed':passed,'interest_gate':plan['interest_gate'],
        'simple_logical_header_plus_id_palette_loads_per8':24-16*whole,'baseline_logical_id_palette_loads_per8':16,
        'photos_output_sha256':output.hexdigest(),'full_constant_colors_equal':True,'environment':env(),
        'scope':'固定2³尺寸只读筛查，不是原生实现/性能；兴趣门槛不代表用户50%速度底线，也不证明其它方案不可优化。'}
    save(a.output/'results.json',result);print('恒色块',int(normal.sum()),'整包正常率',whole,'研究兴趣门槛',passed,flush=True)
if __name__=='__main__':main()
