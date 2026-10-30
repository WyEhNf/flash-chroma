"""只读固定模型，以全节点轴向差分和坐标偏移推导完整输入域的后缀缓存范围证书。"""
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
    if out.exists():raise ValueError('不覆盖数学证书')
    inputs={name:plan['fixed_inputs'][name] for name in ('base','sidecar')}
    for name,spec in inputs.items():
        if sha(ROOT/spec['path'])!=spec['sha256']:raise ValueError('固定输入不同：'+name)
    model=io.load_sparse(ROOT/inputs['base']['path'],competition=True)
    n=model.nodes.astype(np.int64)
    f=np.fromfile(ROOT/inputs['sidecar']['path'],'<u4').reshape(3,3,256).astype(np.int64)
    if np.any(f<0) or np.any(f>65536):raise ValueError('坐标越界')
    # 任一四面体中沿单轴的斜率是该轴某条立方体边的节点差；取全节点边的绝对最大值。
    gradient=np.stack([np.abs(np.diff(n,axis=a)).max(axis=(0,1,2)) for a in range(3)],axis=1)
    delta=np.abs(f-f[0]).max(axis=2)
    numerator=(gradient*delta).sum(axis=1);padding=(numerator+65535)//65536
    diffs=n[...,1:]-n[...,0,None]
    node_min=diffs.min(axis=(0,1,2));node_max=diffs.max(axis=(0,1,2))
    lower=np.maximum(-255,node_min-padding[1:]);upper=np.minimum(255,node_max+padding[1:])
    original_lower=np.maximum(-255,node_min-2);original_upper=np.minimum(255,node_max+2)
    eligible=bool(np.all(lower>=original_lower) and np.all(upper<=original_upper))
    result={'purpose':__doc__,'environment':{'platform':platform.platform(),'python':sys.version,'numpy':np.__version__},
        'inputs':inputs,'source_sha256':sha(__file__),'io_source_sha256':sha(ROOT/'python/lutlab/io.py'),
        'plan_sha256':sha(args.plan),'gradient_max_channel_axis':gradient.tolist(),'fraction_delta_max_channel_axis':delta.tolist(),
        'warp_numerator_channel':numerator.tolist(),'denominator':65536,'required_integer_padding_channel':padding.tolist(),
        'node_difference_min_GB':node_min.tolist(),'node_difference_max_GB':node_max.tolist(),
        'proven_output_difference_min_GB':lower.tolist(),'proven_output_difference_max_GB':upper.tolist(),
        'existing_cache_difference_min_GB':original_lower.tolist(),'existing_cache_difference_max_GB':original_upper.tolist(),
        'certificate_eligible':eligible,
        'proof':['同一共享idx下每个通道为单位立方体上连续分段仿射四面体函数T_c。',
                 '沿轴a的绝对斜率不超过所有该轴相邻节点差最大值L_ca；坐标改变引起的输出差不超过sum(L_ca*abs(df_ca))/65536。',
                 '先把G/B坐标移动到R坐标；共同权重时G-R/B-R是对应节点差的凸组合。',
                 '整数half-up满足round(A)-round(B)<=ceil(A-B)，故节点差界加ceil(sum(L*df)/65536)覆盖最终RGB8差。',
                 'R本身始终在全节点R整数最小/最大内；证明范围必须被现有缓存界完整包含，且缓存已经成功创建。'],
        'decision':'数学资格成立；仍需新实现的全部路径静态成本，不能直接测速' if eligible else '保守界不能证明当前缓存完整覆盖，不实现省检查路径',
        'project_native_calls':0,'performance_calls':0,'new_fits':0,
        'scope':'仅固定输入的小型整数界推导；不是新C++实现、完整色域输出或性能证明，未调整缓存预算/两码边界。'}
    out.mkdir();(out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('gradient_max_channel_axis','fraction_delta_max_channel_axis','required_integer_padding_channel','certificate_eligible','decision')},ensure_ascii=False))


if __name__=='__main__':main()
