"""293/294唯一V2采样的机械V3封存；保留V2失败，不运行native/计时或重验历史。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[1]
PLAN_SHA='1e3fd982f22675519fe6d578fb54ddaf4766a4e3b7593dd60062d792c7400781'
ROLES=('87-a399','87-best','293-best','294-best','293-max41','294-max41')
MEASURED=('scripts/freeze_direct_cache2_perf_v2.py','scripts/p16_cache2_perf_support_v2.py',
    'scripts/run_direct_cache2_perf_v2.py','scripts/audit_direct_cache2_perf_v2.py',
    'experiments/p16-direct-cache2-performance-protocol-v2.md')
POST=('scripts/archive_direct_cache2_perf_v2.py','scripts/audit_direct_cache2_perf_git_v2.py',
    'scripts/archive_direct_cache2_perf_v3.py','scripts/audit_direct_cache2_perf_git_v3.py')
FAILURE='artifacts/p16-direct-cache2-perf-archive-v1-failure.md'

def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def normalized_sources(plan):
    values={}
    for original,value in plan['sources_sha256'].items():
        name=original.replace('\\','/')
        assert name not in values,('规范化后出现重复路径键',original,name)
        values[name]=value
    return values

def fixed_members():
    frozen=ROOT/'artifacts/p16-direct-cache2-perf-frozen-v2'
    formal=ROOT/'artifacts/p16-direct-cache2-perf-v2'
    launch=ROOT/'artifacts/p16-direct-cache2-perf-launch-v2'
    expected_formal={'executed-plan.json','statistics.json','results.json','fraction-audit.json'}
    for profile in ('U','P'):
        for number in range(4):
            expected_formal.update(f'{profile}-worker{number}{suffix}' for suffix in ('.json','.log','-pending.json','-partial.json'))
        for role in ROLES:expected_formal.update(f'{profile}-rss-{role}{suffix}' for suffix in ('.json','.log'))
    groups=((frozen,{'plan.json','expected-pixels-v2.json'}),(formal,expected_formal),
        (launch,{'process-preflight.json','controller-start.json','controller-end.json','controller.log'}))
    members={}
    for folder,expected in groups:
        actual={p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()}
        assert actual==expected,(str(folder),sorted(actual-expected),sorted(expected-actual))
        for relative in sorted(expected):
            path=folder/relative;assert not path.is_symlink();members[path.relative_to(ROOT).as_posix()]=path
    for name in (*MEASURED,*POST,FAILURE):members[name]=ROOT/name
    return members

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,
        default=ROOT/'report/data/p16-direct-cache2-perf-v3');args=parser.parse_args()
    if args.output.exists():raise FileExistsError('机械V3封存不覆盖')
    plan_path=ROOT/'artifacts/p16-direct-cache2-perf-frozen-v2/plan.json'
    assert sha(plan_path)==PLAN_SHA;plan=read(plan_path)
    sources=normalized_sources(plan)
    for relative in MEASURED:assert sha(ROOT/relative)==sources[relative],relative
    formal=ROOT/'artifacts/p16-direct-cache2-perf-v2';launch=ROOT/'artifacts/p16-direct-cache2-perf-launch-v2'
    result=read(formal/'results.json');audit=read(formal/'fraction-audit.json')
    assert read(formal/'executed-plan.json')==plan
    assert read(plan_path.parent/'expected-pixels-v2.json')['models']==plan['expected']
    assert result['passed'] and audit['passed'] and audit['plan_sha256']==PLAN_SHA
    assert result['sha_checks']==audit['actual_sha_checks']==2688
    assert result['image_apply_calls']==audit['actual_image_apply_calls']==5568
    assert result['rss_processes']==audit['rss_processes']==12
    assert set(result['worker_sha256'])=={f'{p}-{n}' for p in ('U','P') for n in range(4)}
    for profile in ('U','P'):
        for number in range(4):
            path=formal/f'{profile}-worker{number}.json';worker=read(path)
            assert sha(path)==result['worker_sha256'][f'{profile}-{number}']
            assert worker['passed'] and worker['profile']==profile and worker['worker']==number
    started=read(launch/'controller-start.json');assert started['plan_sha256']==PLAN_SHA
    completed=read(launch/'controller-end.json');assert completed['controller_exit_code']==0
    assert completed['started']==started['started'] and completed['output']==started['output']
    # 实际end schema没有plan字段；如后续出现该字段，也不能与冻结身份冲突。
    if 'plan_sha256' in completed:assert completed['plan_sha256']==PLAN_SHA
    members=fixed_members();args.output.mkdir(parents=True)
    rows=[]
    with zipfile.ZipFile(args.output/'evidence.zip','x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for member,path in sorted(members.items()):
            data=path.read_bytes();archive.writestr(member,data)
            rows.append({'member':member,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
    with zipfile.ZipFile(args.output/'evidence.zip') as archive:
        assert archive.testzip() is None and archive.namelist()==[r['member'] for r in rows]
        for row in rows:
            data=archive.read(row['member']);assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
    save(args.output/'members.json',rows)
    copies=((plan_path,'plan.json'),(plan_path.parent/'expected-pixels-v2.json','expected-pixels.json'),
        (formal/'statistics.json','statistics.json'),(formal/'fraction-audit.json','fraction-audit.json'),
        (launch/'controller-end.json','controller-end.json'),(launch/'process-preflight.json','process-preflight.json'))
    for source,name in copies:
        shutil.copyfile(source,args.output/name);assert (args.output/name).read_bytes()==source.read_bytes()
    identity={'plan_sha256':PLAN_SHA,'measured_source_sha256':{p:sources[p] for p in MEASURED},
        'post_source_sha256':{p:sha(ROOT/p) for p in POST},
        'failure_record':{'path':FAILURE,'sha256':sha(ROOT/FAILURE),'scope':'真实工具回执转录，不是现场本地stderr；旧V2源码不改不重跑。'},
        'source_key_normalization':'只将反斜线替换为正斜线，拒绝任何规范化重复键，原SHA及冻结plan原字节不变。',
        'original_member_count':len(rows),'zip_crc_and_member_sha256_passed':True,
        'sha_checks':2688,'image_apply_calls':5568,'rss_processes':12,
        'copy_sources':{name:{'original':source.relative_to(ROOT).as_posix(),'sha256':sha(source)} for source,name in copies},
        'copy_bytes_equal_to_original':True,'archive_script_sha256':sha(Path(__file__)),
        'scope':'只封存唯一V2原始范围，外加旧两post/真实失败转录及新V3两post；222历史源/43外部输入只沿plan身份；不运行native、性能或重新统计。U/P原资格及失败不变。'}
    save(args.output/'identity.json',identity)
    print(json.dumps({'passed':True,'members':len(rows),'sha_checks':2688,'image_apply_calls':5568,'rss_processes':12},ensure_ascii=False))

if __name__=='__main__':main()
