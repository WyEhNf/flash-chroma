"""归档六角色287有效低于50%的正式负例；保留全部AA失败，不重跑计时。"""
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
    if args.output.exists():raise ValueError('不覆盖287正式负例归档')
    measured=ROOT/'artifacts/p16-direct-u16-perf-v1';frozen_path=ROOT/'artifacts/p16-direct-u16-perf-frozen-v1.json';frozen=read(frozen_path)
    for name,sha in frozen['frozen_source_sha256'].items():
        if digest(ROOT/name)!=sha:raise ValueError('正式预冻结后源变化：'+name)
    identity=read(measured/'identity.json');result=read(measured/'results.json');check=read(measured/'independent-check.json')
    assert check['pass'] and check['raw_groups']==192 and len(check['AA_failures'])==5
    assert all(result['candidate_gates'][role]['rejected_by_valid_below_50'] for role in ('287max','287p99'))
    assert result['pairs']['287max/87a399']['all_AA_passed_for_pair'] and result['pairs']['287max/287old']['all_AA_passed_for_pair']
    assert identity['driver_sha256']==frozen['frozen_source_sha256']['scripts/run_direct_u16_perf.py']
    assert identity['plan_sha256']==frozen['frozen_source_sha256']['experiments/p16-direct-u16-perf-v1.json']
    args.output.mkdir(parents=True)
    for target,source in [('identity.json',measured/'identity.json'),('results.json',measured/'results.json'),('independent-check.json',measured/'independent-check.json'),
        ('frozen.json',frozen_path),('plan.json',ROOT/'experiments/p16-direct-u16-perf-v1.json'),
        ('quality-manifest.json',ROOT/'report/data/p16-direct-u16-native-20261024-v2/manifest.json')]:shutil.copyfile(source,args.output/target)
    with zipfile.ZipFile(args.output/'raw-workers.zip','w',zipfile.ZIP_DEFLATED) as z:
        for n in range(4):z.write(measured/f'worker{n}/results.json',f'worker{n}/results.json')
        z.write(ROOT/'artifacts/p16-direct-u16-perf-console-v1.txt','console.txt')
    sources=set(frozen['frozen_source_sha256'])|{'scripts/archive_direct_u16_perf.py','scripts/run_channel_tail_nodes.py',
        'scripts/check_velvia_bubble_native.py','scripts/outplace_support.py','python/lutlab/study_provenance.py'}
    with zipfile.ZipFile(args.output/'source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in sorted(sources):z.write(ROOT/name,name)
    manifest={'source_sha256':{name:digest(ROOT/name) for name in sorted(sources)},'files':{p.name:digest(p) for p in args.output.iterdir()},
        'scope':'六角色192组×5及24冷首全部保留；144AA中5失败不删除，937独立检查过；两新模型有效最劣31–34%低50硬拒绝，不切默认，不归因位宽。'}
    (args.output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'files':len(manifest['files']),'source_members':len(sources),'AA_failures':len(check['AA_failures']),'rejected':True}),flush=True)


if __name__=='__main__':main()
