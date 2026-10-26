"""仅检查冻结max_first起点的原60图尾部，决定预注册阈值11是否适用。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'python'))
import numpy as np
from lutlab import study_provenance


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖训练尾部只读诊断')
    cache=Path('F:/Hackathon/projects/16-lut-color/artifacts/cinema-axis-calibration-v1')
    paths={'frequency':cache/'photo-arrival-frequency.npy','reference':cache/'envelope-reference.npy',
        'cube':ROOT/'artifacts/cinema-second-accept-max_first-v1/candidate.rgb',
        'joint':ROOT/'artifacts/cinema-post-second-last-v1/joint-support.npz'}
    expected={'frequency':'1eff7aab15715845bbc3efda68043a62a5c2dd9162f33717cee8bea5d36b756e',
        'reference':'ec79ca618022293b2d2f5c832f1a8647c88e4994ce820664310e09c0f4bf5690',
        'cube':'143e5cc05f4f2635608cd7720b4013a10998d3f7acc8cf35275b38dcfba0792e'}
    inputs={name:{'path':str(path),'sha256':sha(path),'bytes':path.stat().st_size} for name,path in paths.items()}
    for name,digest in expected.items():
        if inputs[name]['sha256']!=digest:raise ValueError('起点输入变更：'+name)
    frequency=np.load(paths['frequency'],mmap_mode='r');reference=np.load(paths['reference'],mmap_mode='r')
    cube=np.memmap(paths['cube'],np.uint8,'r',shape=(256**3,3))
    if frequency.shape!=(256**3,) or frequency.dtype!=np.uint32:raise ValueError('训练计数应为完整原色uint32频数')
    hist=np.zeros(3*255**2+1,np.int64)
    for start in range(0,256**3,1<<18):
        stop=min(start+(1<<18),256**3)
        delta=cube[start:stop].astype(np.int32)-reference[start:stop].astype(np.int32)
        squared=np.sum(delta*delta,axis=1,dtype=np.int32)
        # 每块计数<2^53，因此整数权重的float64 bincount精确，立即还原为int64。
        hist+=np.bincount(squared,weights=frequency[start:stop],minlength=len(hist)).astype(np.int64)
    count=int(hist.sum());cdf=hist.cumsum();rank=(99*count+99)//100
    generalized=int(np.searchsorted(cdf,rank));position=(count-1)*.99;low=int(np.floor(position));high=int(np.ceil(position))
    lo=int(np.searchsorted(cdf,low+1));hi=int(np.searchsorted(cdf,high+1))
    linear=float(np.sqrt(lo)+(position-low)*(np.sqrt(hi)-np.sqrt(lo)))
    with np.load(paths['joint']) as joint:
        mass=joint['mass'];joint_count=np.rint(mass*count).astype(np.int64)
        maximum_integer_residual=float(np.max(np.abs(mass*count-joint_count)))
        if maximum_integer_residual>1e-6 or int(joint_count.sum())!=count:raise AssertionError('联合质量不能还原训练整数频数')
    result={'source_sha256':sha(Path(__file__)),'proposal_sha256':sha(ROOT/'experiments/p16-cinema-training-tail-proposal-v1.md'),
        'environment':study_provenance.environment_fingerprint(),'test_type':'冻结起点的只读原60图频数统计；无拟合、无计时',
        'inputs':inputs,'frequency_dtype':str(frequency.dtype),'training_pixels':count,'expected_60_images_1024x768':count==60*1024*768,
        'histogram_nonzero':{str(i):int(v) for i,v in enumerate(hist) if v},'generalized_cdf_p99_squared':generalized,
        'numpy_linear_equivalent_p99':linear,'squared_11_exceed_count':int(hist[12:].sum()),
        'squared_11_exceed_fraction':float(hist[12:].sum()/count),'joint_integer_residual_max':maximum_integer_residual,
        'fixed_target_11_applicable':bool(generalized>11 and linear>np.sqrt(11)),
        'scope':'100图未参与本次诊断；广义加权CDF与完整像素线性分位数分别报告。阈值11不适用则停止原方案。'}
    if not result['expected_60_images_1024x768']:raise AssertionError('不是冻结60图训练计数')
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('training_pixels','generalized_cdf_p99_squared','numpy_linear_equivalent_p99','squared_11_exceed_fraction','fixed_target_11_applicable')},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
