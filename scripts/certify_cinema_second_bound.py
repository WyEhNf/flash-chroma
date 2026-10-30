"""用完整无损支撑和独立uint64前缀给第二级候选max50下界证书。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'python'))
import numba
import numpy as np
from lutlab import io,channel_coordinates as cc,study_provenance
from lutlab.integer_rgb_ball import intersection
from run_channel_tail_nodes import load_model,digest,save
from verify_channel_coordinates import integer_oracle
from certify_cinema_prefix_bound import key,rgb


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--study',type=Path,required=True)
    p.add_argument('--accept-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖新前缀证书')
    numba.set_num_threads(4);run=json.loads((args.study/'run.json').read_text(encoding='utf-8'))
    for value in run['inputs'].values():
        if digest(value['path'])!=value['sha256']:raise ValueError('原支撑输入变更')
    for name,sha in run['sources'].items():
        if digest(ROOT/name)!=sha:raise ValueError('原拟合执行源变更')
    with np.load(args.study/'joint-support.npz') as data:
        arrivals,gold,frequency,source=[data[name] for name in ('arrivals','reference','frequency','representative_source')]
    assert frequency.dtype==np.int64 and frequency.sum()==256**3 and len(arrivals)==10633
    first=load_model(Path(run['inputs']['first']['path']));source_rgb=rgb(source)
    np.testing.assert_array_equal(integer_oracle(first,source_rgb),arrivals)
    reference=np.load(run['inputs']['reference']['path'],mmap_mode='r');np.testing.assert_array_equal(reference[source],gold)
    records={}
    for mode in ('max_first','p99_first'):
        candidate=args.study/mode/'candidate';accept=args.accept_root/('cinema-second-accept-'+mode+'-v1')
        accepted=json.loads((accept/'results.json').read_text(encoding='utf-8'));cube=accept/'candidate.rgb'
        if digest(cube)!=accepted['sha256']['oracle'] or accepted['cube']['max']**2>50+1e-10:raise ValueError('缺少完整流max50上界')
        complete=np.memmap(cube,np.uint8,'r',shape=(256**3,3));output=complete[source]
        delta=output.astype(np.int32)-gold.astype(np.int32);square=np.sum(delta*delta,axis=1,dtype=np.int32)
        assert square.max()==50
        np.testing.assert_array_equal(np.bincount(square,weights=frequency,minlength=3*255**2+1).astype(np.int64),np.load(args.study/mode/'after-hist.npy'))
        second=cc.from_sparse(io.load_sparse(candidate/'stage2.slut',competition=True))
        third=cc.from_sparse(io.load_sparse(Path(run['inputs']['stage3']['path']),competition=True))
        reached=arrivals;prefix_records=[]
        for prefix,model in ((1,None),(2,second),(3,third)):
            if model is not None:reached=integer_oracle(model,reached)
            codes=key(reached);hot=np.unique(codes[square>49]);groups=[]
            for code in hot:
                selected=np.flatnonzero(codes==code);unique,index=np.unique(gold[selected],axis=0,return_index=True)
                representatives=source[selected[index]];wide=unique.astype(np.int32)
                diameter=-1;pair=None
                for a in range(len(unique)):
                    for b in range(a+1,len(unique)):
                        d=int(np.sum((wide[a]-wide[b])**2,dtype=np.int32))
                        if d>diameter:diameter,pair=d,[a,b]
                ball=intersection(unique,49)
                group={'arrived_rgb':rgb(np.asarray([code],np.uint32))[0].tolist(),'distinct_gold':len(unique),
                    'uniform_frequency':int(frequency[selected].sum()),'integer_ball':ball,'diameter_squared':diameter,
                    'pair_proves_50':diameter>196,'gold':unique.tolist(),'representative_source':representatives.tolist()}
                if pair is not None:group['diameter_pair']={'gold':unique[pair].tolist(),'source_rgb':rgb(representatives[pair]).tolist()}
                if diameter>196 and ball['feasible']:raise AssertionError('整数距离与球交矛盾')
                groups.append(group)
            prefix_records.append({'fixed_prefix_stages':prefix,'all_hot_groups':len(hot),'groups':groups,
                'lower_bound_50_proved':any(not group['integer_ball']['feasible'] for group in groups),
                'current_complete_upper_bound_squared':50})
        records[mode]={'cube_sha256':digest(cube),'stage2_sha256':digest(candidate/'stage2.slut'),'prefixes':prefix_records}
    plan=ROOT/'experiments/p16-cinema-second-bound-v1.json'
    save(args.output,{'records':records,'plan':json.loads(plan.read_text(encoding='utf-8')),'environment':study_provenance.environment_fingerprint(),
        'joint_support_sha256':digest(args.study/'joint-support.npz'),'study_run_sha256':digest(args.study/'run.json'),
        'source_sha256':{path.relative_to(ROOT).as_posix():digest(path) for path in (Path(__file__),plan,
            ROOT/'scripts/verify_channel_coordinates.py',ROOT/'python/lutlab/integer_rgb_ball.py')},
        'scope':'固定前缀的精确整数minimax证书；完整加权支撑，未做新拟合/照片/运行时性能。'})
    print({mode:[{'prefix':value['fixed_prefix_stages'],'hot_groups':value['all_hot_groups'],'lower50':value['lower_bound_50_proved']} for value in record['prefixes']] for mode,record in records.items()},flush=True)


if __name__=='__main__':main()
