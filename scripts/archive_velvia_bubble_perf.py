"""完整归档187主集80档、dense有效低于50%的负例，保留AA失败场。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
ROOT=Path(__file__).resolve().parents[1]


def digest(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖187正式性能归档')
    args.output.mkdir(parents=True)
    measured=ROOT/'artifacts/velvia-bubble-perf-v1';identity=read(measured/'identity.json')
    driver=ROOT/'scripts/run_velvia_bubble_perf.py';plan=ROOT/'experiments/velvia-bubble-perf-v1.json'
    if digest(driver)!=identity['driver_sha256'] or digest(plan)!=identity['plan_sha256']:raise ValueError('正式计时源码或计划改变')
    quality=ROOT/'report/data/velvia-bubble-native-20261024'
    for target,source in [('identity.json',measured/'identity.json'),('results.json',measured/'results.json'),
        ('independent-check.json',measured/'independent-check-v3.json'),('derived-first-check.json',measured/'independent-check.json'),
        ('plan.json',plan),('quality-stage-manifest.json',quality/'manifest.json'),('frozen-model.json',quality/'frozen-v2.json')]:
        shutil.copyfile(source,args.output/target)
    with zipfile.ZipFile(args.output/'raw-workers.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for n in range(4):archive.write(measured/f'worker{n}/results.json',f'worker{n}/results.json')
    sources=['scripts/'+n for n in ('run_velvia_bubble_perf.py','check_velvia_bubble_perf.py','archive_velvia_bubble_perf.py',
        'check_velvia_bubble_native.py','run_channel_tail_nodes.py')]+['experiments/velvia-bubble-perf-v1.json',
        'experiments/channel-runtime/channel_native.py','experiments/skylake-andn-normal-runtime/outplace_bench.cpp',
        'python/lutlab/study_provenance.py']
    with zipfile.ZipFile(args.output/'source.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for name in sources:archive.write(ROOT/name,name)
    result=read(measured/'results.json');check=read(measured/'independent-check-v3.json')
    if not check['pass'] or not result['rejected_by_valid_below_50']:raise ValueError('必须保持已观察的有效负例')
    note={'independent_auxiliary_table_repair':'初版独立分表把偶数样本中位数写成上中位数；辅助表已修为中间二值均值。正式计时raw和原summary正确，50%判定不受影响，未重跑性能。',
        'performance_reruns':0,'discarded_workers':0,'AA_failed_checks':len(check['AA_failures'])}
    (args.output/'audit-note.json').write_text(json.dumps(note,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    manifest={'source_sha256':{name:digest(ROOT/name) for name in sources},'files':{p.name:digest(p) for p in args.output.iterdir()},
        'numeric_or_performance_calls_during_archive':0,'scope':'全部192组×5计时及组末SHA保留；照片最低80档，dense有效18.4527%使整体低50拒绝；AA无效场不救结论，不切默认'}
    (args.output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'files':len(manifest['files']),'AA_failed_checks':len(check['AA_failures']),'rejected':True}),flush=True)


if __name__=='__main__':main()
