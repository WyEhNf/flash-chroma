"""在构建前冻结原3e5模型、派生87源码及三方正确性/性能对照身份。"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'python'))
from lutlab import io,study_provenance
from run_channel_tail_nodes import load_model,digest,save


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache-root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖构建前冻结身份')
    args.output.mkdir(parents=True)
    path=args.cache_root/'artifacts/velvia-channel-coordinates-v1/channel-coordinates.npz'
    if digest(path)!='3e5f8fd94e8dc9b97dbfea2823896b8dffb6e014b5e6056ab5c10b58a69af3d0':raise ValueError('不是原3e5')
    m=load_model(path)
    io.save_sparse(args.output/'base.slut',io.SparseLut(m.grid,m.nodes,m.idx,m.channel_frac[0]))
    m.channel_frac.astype('<u4').tofile(args.output/'channel-frac.bin')
    sources=list((ROOT/'experiments/velvia-bubble-runtime').glob('*'))
    sources += [Path(__file__),ROOT/'experiments/velvia-bubble-native-plan-v1.md']
    record={'model_sha256':digest(path),'serialized_sha256':{n:digest(args.output/n) for n in ('base.slut','channel-frac.bin')},
        'source_sha256':{p.relative_to(ROOT).as_posix():digest(p) for p in sources},
        'frozen_87_library':'F:/Hackathon/worktrees/p16-speed-20261023/artifacts/p16-speed-direct-build-v1/libjshc_direct_prepare_simd.dll',
        'frozen_87_sha256':'58591a725d367dce3713ff88af4d5549afea5af1ac4f3a39284443586893c158',
        'oracle_baseline_sha256':'945d4b906ae9aa184fdddd7f084da0105fa87b7e756f88ea700ca53f61ed37f0',
        'oracle_candidate_sha256':'f38217d6ab471f58cc794eee23ab02317f4df2d86b0a00eab4f520e2b4ba3875',
        'environment':study_provenance.environment_fingerprint(), 'expected_revision':187,
        'quality_policy':'先核冻结87、187关闭及187开启的全域/100图；scalar1、AVX2的1/4，原地/真分离；短尾/密集/空输入与typed拒绝；本阶段不计时',
        'performance_policy':'另获排他窗后先187关闭对冻结87，再同187关闭/开启；原地与真分离1/4、纯apply与copy+apply，保留所有worker，不用共同固定成本掩盖开销',
        'scope':'非stock SLUT，固定两cell/κ3，不扩拟合；每线程密集命中栈计入容量，不推断50速度底线'}
    save(args.output/'frozen.json',record)
    print(json.dumps(record['serialized_sha256']),flush=True)


if __name__=='__main__':main()
