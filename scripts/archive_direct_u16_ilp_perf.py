"""保留288八角色有效子集改善、整体AA未证的完整正式证据与阻断映射。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
ROOT=Path(__file__).resolve().parents[1]


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖288正式证据')
    measured=ROOT/'artifacts/p16-direct-u16-ilp-perf-v1';frozen_path=ROOT/'artifacts/p16-direct-u16-ilp-perf-frozen-v1.json';frozen=read(frozen_path)
    for name,sha in frozen['frozen_source_sha256'].items():
        if digest(ROOT/name)!=sha:raise ValueError('预冻结源改变：'+name)
    identity=read(measured/'identity.json');result=read(measured/'results.json');check=read(measured/'independent-check.json');failures=check['AA_failures']
    assert check['pass'] and check['raw_groups']==256 and len(failures)==22
    assert all(not result['candidate_gates'][role]['hard50'] and not result['candidate_gates'][role]['rejected_by_valid_below_50'] for role in ('288max','288p99'))
    assert identity['driver_sha256']==frozen['frozen_source_sha256']['scripts/run_direct_u16_ilp_perf.py']
    assert identity['plan_sha256']==frozen['frozen_source_sha256']['experiments/p16-direct-u16-ilp-perf-v1.json']
    blocked={}
    for left,right in identity['plan']['comparisons']:
        rows=[r for r in failures if r['role'] in (left,right)];scenes={}
        for row in rows:scenes.setdefault((row['worker'],row['path'],row['threads']),[]).append(row)
        pair=right+'/'+left
        invalid_rows=sum(2*(2 if path=='inplace' else 1) for worker,path,threads in scenes)
        assert result['pairs'][pair]['valid_rows']==48-invalid_rows
        assert result['pairs'][pair]['all_AA_passed_for_pair']==(not scenes)
        blocked[pair]={'all_AA_passed':not scenes,'valid_rows':48-invalid_rows,'invalid_rows':invalid_rows,
            'blocking_roles':sorted({r['role'] for r in rows}),'blocking_scenes':[{'worker':w,'path':p,'threads':t,'AA_failures':v} for (w,p,t),v in sorted(scenes.items())]}
    args.output.mkdir(parents=True)
    for target,source in [('identity.json',measured/'identity.json'),('results.json',measured/'results.json'),('independent-check.json',measured/'independent-check.json'),
        ('frozen.json',frozen_path),('plan.json',ROOT/'experiments/p16-direct-u16-ilp-perf-v1.json'),('quality-manifest.json',ROOT/'report/data/p16-direct-u16-ilp-native-20261024/manifest.json'),
        ('host-memory-before.json',ROOT/'artifacts/p16-direct-u16-ilp-perf-memory-before-v1.json')]:shutil.copyfile(source,args.output/target)
    mapping={'AA_failures':failures,'pair_blocking':blocked,'scope':'只按冻结AA规则定位阻断角色/场景，不推测未测CPU频率、温度、系统或进程原因；不重跑或放宽门槛。'}
    (args.output/'AA-blocking.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with zipfile.ZipFile(args.output/'raw-workers.zip','w',zipfile.ZIP_DEFLATED) as z:
        for n in range(4):z.write(measured/f'worker{n}/results.json',f'worker{n}/results.json')
        z.write(ROOT/'artifacts/p16-direct-u16-ilp-perf-console-v1.txt','console.txt')
    sources=set(frozen['frozen_source_sha256'])|{'scripts/archive_direct_u16_ilp_perf.py','scripts/run_channel_tail_nodes.py',
        'scripts/check_velvia_bubble_native.py','scripts/outplace_support.py','python/lutlab/study_provenance.py'}
    with zipfile.ZipFile(args.output/'source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in sorted(sources):z.write(ROOT/name,name)
    manifest={'source_sha256':{name:digest(ROOT/name) for name in sorted(sources)},'files':{p.name:digest(p) for p in args.output.iterdir()},
        'scope':'八角色全部256组×5、32冷首及22/192 AA失败保留；1195独立检查过，有效子集60/70但整体未证50，旧综合best保留，不补跑。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'files':len(manifest['files']),'source_members':len(sources),'AA_failures':len(failures),'pairs':len(blocked),'overall_qualified':False}),flush=True)


if __name__=='__main__':main()
