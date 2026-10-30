"""按每个可达网格单元推导有符号斜率/坐标区间证书，不改变缓存范围或执行映射。"""
from __future__ import annotations
import argparse,hashlib,json,platform,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'python'))
from lutlab import io


def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('plan','output'):p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args();plan=read(args.plan);out=args.output.resolve()
    if out.exists():raise ValueError('不覆盖单元证书')
    inputs={name:plan['fixed_inputs'][name] for name in ('base','sidecar')}
    for name,spec in inputs.items():
        if sha(ROOT/spec['path'])!=spec['sha256']:raise ValueError('固定输入不同：'+name)
    model=io.load_sparse(ROOT/inputs['base']['path'],competition=True);m=model.m;idx=model.tables()[0]
    n=model.nodes.astype(np.int64);f=np.fromfile(ROOT/inputs['sidecar']['path'],'<u4').reshape(3,3,256).astype(np.int64)
    if np.any(f<0) or np.any(f>65536):raise ValueError('坐标越界')
    corners=np.stack([n[r:r+m-1,g:g+m-1,b:b+m-1] for r in (0,1) for g in (0,1) for b in (0,1)],axis=3)
    node_difference=corners[...,1:]-corners[...,0,None]
    node_lo=node_difference.min(axis=3);node_hi=node_difference.max(axis=3)
    gradient_lo=[];gradient_hi=[]
    for axis in range(3):
        bit=1<<(2-axis);low=[i for i in range(8) if not i&bit];high=[i|bit for i in low]
        edge=corners[...,high,:]-corners[...,low,:]
        gradient_lo.append(edge.min(axis=3));gradient_hi.append(edge.max(axis=3))
    delta=f-f[0];delta_lo=np.zeros((3,3,m-1),np.int64);delta_hi=delta_lo.copy();counts=np.zeros((3,m-1),np.int64)
    for axis in range(3):
        for cell in range(m-1):
            codes=np.flatnonzero(idx[axis]==cell);counts[axis,cell]=len(codes)
            if len(codes):
                delta_lo[:,axis,cell]=delta[:,axis,codes].min(axis=1)
                delta_hi[:,axis,cell]=delta[:,axis,codes].max(axis=1)
    reachable=(counts[0,:,None,None]>0)&(counts[1,None,:,None]>0)&(counts[2,None,None,:]>0)
    warp_lo=np.zeros((*reachable.shape,2),np.int64);warp_hi=warp_lo.copy()
    for axis in range(3):
        shape=[1,1,1,2];shape[axis]=m-1
        d0=delta_lo[1:,axis,:].T.reshape(shape);d1=delta_hi[1:,axis,:].T.reshape(shape)
        g0=gradient_lo[axis][...,1:];g1=gradient_hi[axis][...,1:]
        products=np.stack((g0*d0,g0*d1,g1*d0,g1*d1))
        warp_lo+=products.min(axis=0);warp_hi+=products.max(axis=0)
    # floor/ceil对有符号分子同样有效；不能以向零截断替代下界floor。
    lower=np.maximum(-255,node_lo+warp_lo//65536)
    upper=np.minimum(255,node_hi-((-warp_hi)//65536))
    existing_lo=np.maximum(-255,(n[...,1:]-n[...,0,None]).min(axis=(0,1,2))-2)
    existing_hi=np.minimum(255,(n[...,1:]-n[...,0,None]).max(axis=(0,1,2))+2)
    bad=reachable&((lower<existing_lo)|(upper>existing_hi)).any(axis=3)
    global_lo=lower[reachable].min(axis=0);global_hi=upper[reachable].max(axis=0);witnesses=[]
    for cell in np.argwhere(bad)[:8]:
        k=tuple(cell);witnesses.append({'cell':cell.tolist(),'node_difference_min_GB':node_lo[k].tolist(),
            'node_difference_max_GB':node_hi[k].tolist(),'warp_lower_numerator_GB':warp_lo[k].tolist(),
            'warp_upper_numerator_GB':warp_hi[k].tolist(),'proven_lower_GB':lower[k].tolist(),'proven_upper_GB':upper[k].tolist()})
    out.mkdir();np.savez_compressed(out/'all-cells.npz',reachable=reachable,node_lo=node_lo,node_hi=node_hi,
        warp_lo=warp_lo,warp_hi=warp_hi,lower=lower,upper=upper,delta_lo=delta_lo,delta_hi=delta_hi,
        gradient_lo=np.stack(gradient_lo),gradient_hi=np.stack(gradient_hi))
    result={'purpose':__doc__,'environment':{'platform':platform.platform(),'python':sys.version,'numpy':np.__version__},
        'inputs':inputs,'source_sha256':sha(__file__),'io_source_sha256':sha(ROOT/'python/lutlab/io.py'),'plan_sha256':sha(args.plan),
        'grid_m':m,'reachable_cells':int(reachable.sum()),'total_cells':int(reachable.size),'unproven_cells':int(bad.sum()),
        'proven_global_difference_min_GB':global_lo.tolist(),'proven_global_difference_max_GB':global_hi.tolist(),
        'existing_cache_difference_min_GB':existing_lo.tolist(),'existing_cache_difference_max_GB':existing_hi.tolist(),
        'certificate_eligible':not bool(bad.any()),'first_unproven_cells':witnesses,'all_cells_sha256':sha(out/'all-cells.npz'),
        'proof':'同单元共同R坐标的节点差凸界，加G/B函数沿三轴从R坐标移到自身坐标的分段线性有符号斜率积分界；每轴对四种斜率端点×偏移端点取完整区间；RGB8差下/上界分别floor/ceil。',
        'policy':'仅一次逐单元有符号细化；未改变原两码边界/缓存预算/模型，若仍不成立则停止省检查方向，不再细分或扫描。',
        'project_native_calls':0,'performance_calls':0,'new_fits':0,
        'scope':'保守数学证书；未证明的单元不是实际miss或输出错误，不代替任何新C++实现正确性/速度。'}
    (out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('reachable_cells','unproven_cells','proven_global_difference_min_GB','proven_global_difference_max_GB','certificate_eligible','first_unproven_cells')},ensure_ascii=False))


if __name__=='__main__':main()
