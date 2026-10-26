"""固定当前最优Cinema前缀的完整RGB8不可区分组整数minimax证书。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'python'))
import numba
import numpy as np
from lutlab import channel_coordinates as cc,io,study_provenance
from lutlab.integer_rgb_ball import intersection
from run_channel_tail_nodes import digest,save,load_model
from verify_channel_coordinates import integer_oracle


def key(points):
    return (points[:,0].astype(np.uint32)<<16)|(points[:,1].astype(np.uint32)<<8)|points[:,2]


def rgb(codes):
    return np.stack((codes>>16,(codes>>8)&255,codes&255),axis=1).astype(np.uint8)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache-root',type=Path,required=True)
    p.add_argument('--first-folder',type=Path,required=True)
    p.add_argument('--cube',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖既有证书')
    args.output.mkdir(parents=True)
    numba.set_num_threads(4)
    cache=args.cache_root.resolve();plan=ROOT/'experiments/p16-prefix-bound-v1.json'
    paths={'first':args.first_folder/'model.npz','last':args.first_folder/'stage4.slut',
        'stage2':cache/'artifacts/cinema-envelope-v1/stage4_sweep004/selected-stage2.slut',
        'stage3':cache/'artifacts/cinema-envelope-v1/stage4_sweep004/selected-stage3.slut',
        'reference':cache/'artifacts/cinema-axis-calibration-v1/envelope-reference.npy',
        'points':cache/'artifacts/cinema-axis-calibration-v1/envelope-arrivals.npy','cube':args.cube}
    expected={'first':'0ea0a380b83e3581668654f45a7aa5682515b2dfb6ef7c8aeb96f82f60afa030',
        'last':'fcc15bc8147bc865e534644460ccda3e51f21e8979e21db2fa5bd7e574ffdb67',
        'stage2':'933a4311800dabfafdec534cc149c56aeb7043e5e57df8bef4dd174058b57650',
        'stage3':'95cb685e2298c49744cf91502bc06a3f8f20e97d1e654872ba1cfd59a48e7234',
        'reference':'ec79ca618022293b2d2f5c832f1a8647c88e4994ce820664310e09c0f4bf5690',
        'points':'fac03692667ab8d5220a4a09035b420d96037094c101b91011de303209ccaaea',
        'cube':'150bd55ede2419b3ede748705adad388562137e3144de7aaebb929ee4f066c6a'}
    hashes={k:digest(v) for k,v in paths.items()}
    for k,v in expected.items():
        if hashes[k]!=v:raise ValueError('不是已冻结当前最优模型或流：'+k)
    save(args.output/'run.json',{'inputs':{k:{'path':str(paths[k]),'sha256':v} for k,v in hashes.items()},
        'source_sha256':{str(f.relative_to(ROOT)):digest(f) for f in (Path(__file__),ROOT/'python/lutlab/integer_rgb_ball.py',
            ROOT/'scripts/check_integer_rgb_ball.py',ROOT/'scripts/check_cinema_prefix_certificate.py',
            ROOT/'scripts/run_channel_tail_nodes.py',ROOT/'scripts/verify_channel_coordinates.py',
            ROOT/'python/lutlab/channel_coordinates.py',ROOT/'python/lutlab/io.py',ROOT/'python/lutlab/study_provenance.py',plan)},
        'plan':json.loads(plan.read_text(encoding='utf-8')),'environment':study_provenance.environment_fingerprint(),
        'numba_threads':4,'test_type':'完整域数学下界与数据完整性；无拟合/速度/官方分数'})
    first=load_model(paths['first'])
    rest=[cc.from_sparse(io.load_sparse(paths[name],competition=True)) for name in ('stage2','stage3','last')]
    points=np.load(paths['points'],mmap_mode='r');reference=np.load(paths['reference'],mmap_mode='r')
    if any(v.dtype!=np.uint8 or v.shape!=(256**3,3) for v in (points,reference)):
        raise ValueError('输入或真值不是冻结完整RGB8域')
    baseline=np.memmap(paths['cube'],dtype=np.uint8,mode='r',shape=(256**3,3))
    histogram=np.zeros(3*255**2+1,np.int64);hot=[];started=time.perf_counter()
    for start in range(0,len(points),1<<18):
        stop=min(start+(1<<18),len(points));delta=baseline[start:stop].astype(np.int32)-reference[start:stop].astype(np.int32)
        sq=np.sum(delta*delta,axis=1,dtype=np.int32);histogram+=np.bincount(sq,minlength=len(histogram))
        hot.extend((np.flatnonzero(sq>58)+start).tolist())
    if np.flatnonzero(histogram)[-1]!=59:raise AssertionError('当前完整域max不是59')
    hot=np.asarray(hot,np.int64);hot_prefix=[];reached=points[hot]
    for model in (first,rest[0]):
        reached=cc.predict(model,reached);hot_prefix.append(np.unique(key(reached)))
    groups=[{} for _ in hot_prefix];mismatches=0
    for start in range(0,len(points),1<<18):
        stop=min(start+(1<<18),len(points));reached=points[start:stop]
        if not np.array_equal(key(reached),np.arange(start,stop,dtype=np.uint32)):raise AssertionError('输入顺序不正确')
        for prefix,model in enumerate((first,*rest)):
            reached=cc.predict(model,reached)
            if prefix<2:
                codes=key(reached);targets=hot_prefix[prefix];at=np.searchsorted(targets,codes)
                clipped=np.minimum(at,len(targets)-1);selected=np.flatnonzero((at<len(targets))&(targets[clipped]==codes))
                joint=(codes[selected].astype(np.uint64)<<24)|key(reference[start+selected]).astype(np.uint64)
                unique,index,counts=np.unique(joint,return_index=True,return_counts=True)
                for value,representative,count in zip(unique,index,counts):
                    pair=int(value);old=groups[prefix].get(pair)
                    if old is None:groups[prefix][pair]=[int(count),int(start+selected[representative])]
                    else:old[0]+=int(count)
        mismatches+=int(np.count_nonzero(reached!=baseline[start:stop]))
        if (stop%(1<<22))==0:print(json.dumps({'visited':stop,'seconds':time.perf_counter()-started}),flush=True)
    if mismatches:raise AssertionError('当前四级整链不匹配已验收完整流')
    np.save(args.output/'baseline-squared-hist.npy',histogram)
    reports=[]
    for prefix,targets in enumerate(hot_prefix):
        pair_values=groups[prefix];entries=[]
        for arrived in targets:
            records=sorted((pair&0xffffff,*value) for pair,value in pair_values.items() if pair>>24==int(arrived))
            gold=rgb(np.asarray([v[0] for v in records],np.uint32))
            result=intersection(gold,58)
            source=np.asarray([v[2] for v in records],np.int64)
            independent=integer_oracle(first,points[source])
            if prefix:independent=integer_oracle(rest[0],independent)
            np.testing.assert_array_equal(key(independent),np.full(len(source),arrived,np.uint32))
            np.testing.assert_array_equal(reference[source],gold)
            out=rgb(np.asarray([arrived],np.uint32))
            for model in rest[prefix:]:out=integer_oracle(model,out)
            sq=np.sum((out.astype(np.int32)-gold.astype(np.int32))**2,axis=1)
            if sq.max()!=59:raise AssertionError('被检组缺少旧max59见证')
            entries.append({'arrived_rgb':rgb(np.asarray([arrived],np.uint32))[0].tolist(),
                'reference_rgb':gold.tolist(),'uniform_frequency':[v[1] for v in records],
                'source_rgb_codes':source.tolist(),'current_output':out[0].tolist(),
                'current_group_max_squared':int(sq.max()),'intersection_at_58':result})
        report={'prefix_stages':prefix+1,'hot_original_colours':len(hot),'hot_prefix_groups':len(targets),
            'infeasible_groups':sum(not v['intersection_at_58']['feasible'] for v in entries),'groups':entries}
        report['fixed_prefix_max_squared_lower_bound']=59 if report['infeasible_groups'] else None
        save(args.output/f'prefix-{prefix+1}.json',report);reports.append({k:v for k,v in report.items() if k!='groups'})
    save(args.output/'summary.json',{'reports':reports,'all_rgb_colours':len(points),'pipeline_byte_mismatches':mismatches,
        'baseline_max_squared':59,'seconds':time.perf_counter()-started,'limits':'只固定被检前缀；可改变首级以解除碰撞。可行球交不证明后续稀疏插值表示可达。无官方阈值/评分结论。'})
    print(json.dumps(reports,ensure_ascii=False),flush=True)


if __name__=='__main__':main()
