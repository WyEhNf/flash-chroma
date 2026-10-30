"""只导出已验模型的独立uint64后缀表预期，供无NumPy服务器逐字节核验；不调用原生后端或拟合。"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
import platform
import sys
import numpy as np
from skylake_support import ROOT,read,checked,digest,save
from lutlab import channel_coordinates as cc,io
from verify_channel_coordinates import integer_oracle

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan',type=Path,required=True);p.add_argument('--full',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();plan=read(args.plan);full=read(args.full)
    if not full['pass'] or full['plan_sha256']!=digest(args.plan):raise ValueError('先有相同模型的完整验收')
    for name in ('scripts/verify_channel_coordinates.py','python/lutlab/channel_coordinates.py','python/lutlab/io.py'):
        if digest(ROOT/name)!=plan['source_sha256'][name]:raise ValueError('独立oracle及输入转换源不同：'+name)
    out=args.output.resolve()
    if out.exists():raise ValueError('不覆盖已导出金标准')
    base=checked(plan['fixed_inputs']['base']);suffix=[checked(s) for s in plan['suffix_models']]
    nodes=io.load_sparse(base,competition=True).nodes.reshape(-1,3).astype(np.int32)
    dg=nodes[:,1]-nodes[:,0];db=nodes[:,2]-nodes[:,0];margin=plan['cache_policy']['node_difference_margin']
    bounds={'r_min':int(nodes[:,0].min()),'r_max':int(nodes[:,0].max()),'dg_min':max(-255,int(dg.min())-margin),
        'dg_max':min(255,int(dg.max())+margin),'db_min':max(-255,int(db.min())-margin),'db_max':min(255,int(db.max())+margin)}
    if any(full['suffix_cache']['info'][k]!=v for k,v in bounds.items()):raise ValueError('独立节点范围与既有缓存不同')
    r,g,b=np.meshgrid(*[np.arange(bounds[a],bounds[z]+1,dtype=np.int32) for a,z in
        [('r_min','r_max'),('dg_min','dg_max'),('db_min','db_max')]],indexing='ij')
    colours=np.column_stack((r.ravel(),(r+g).ravel(),(r+b).ravel()));valid=((colours>=0)&(colours<=255)).all(axis=1)
    truth=colours[valid].astype(np.uint8)
    for path in suffix:truth=integer_oracle(cc.from_sparse(io.load_sparse(path,competition=True)),truth)
    values=np.zeros(len(colours),dtype='<u4');values[valid]=truth[:,0].astype(np.uint32)|(truth[:,1].astype(np.uint32)<<8)|(truth[:,2].astype(np.uint32)<<16)
    if values.nbytes>plan['cache_policy']['budget_bytes']:raise ValueError('超过既有预算')
    out.mkdir(parents=True);values.tofile(out/'cache-gold.u32')
    save(out/'generation.json',{'purpose':__doc__,'generation_completed':True,'plan_sha256':digest(args.plan),'prior_full_sha256':digest(args.full),
        'inputs':{'base':plan['fixed_inputs']['base'],'suffix':plan['suffix_models']},'bounds':bounds,'entries':len(values),
        'valid_entries':int(valid.sum()),'invalid_entries_zero':int((~valid).sum()),'bytes':values.nbytes,
        'gold_sha256':digest(out/'cache-gold.u32'),'format':'little-endian uint32, R|(G<<8)|(B<<16), R/dG/dB字典序',
        'environment':{'platform':platform.platform(),'python':sys.version,'numpy':np.__version__},
        'source_sha256':{'scripts/export_skylake_cache_gold.py':digest(__file__),'scripts/verify_channel_coordinates.py':digest(ROOT/'scripts/verify_channel_coordinates.py')},
        'native_calls':0,'new_fits':0,'performance_calls':0})
    print('缓存整数金标准导出完成：',len(values),'槽；SHA',digest(out/'cache-gold.u32'),flush=True)

if __name__=='__main__':main()
