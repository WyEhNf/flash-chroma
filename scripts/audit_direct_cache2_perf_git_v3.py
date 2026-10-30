"""293/294唯一V2采样的机械V3封存独立Git核对，不执行native或重算统计。"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'report/data/p16-direct-cache2-perf-v3'
DOC='docs/stages/2026-10-24-p16-direct-cache2-performance-v2.md'
MEASURED=('scripts/freeze_direct_cache2_perf_v2.py','scripts/p16_cache2_perf_support_v2.py',
    'scripts/run_direct_cache2_perf_v2.py','scripts/audit_direct_cache2_perf_v2.py',
    'experiments/p16-direct-cache2-performance-protocol-v2.md')
POST=('scripts/archive_direct_cache2_perf_v2.py','scripts/audit_direct_cache2_perf_git_v2.py',
    'scripts/archive_direct_cache2_perf_v3.py','scripts/audit_direct_cache2_perf_git_v3.py')
FAILURE='artifacts/p16-direct-cache2-perf-archive-v1-failure.md'
PLAN_SHA='1e3fd982f22675519fe6d578fb54ddaf4766a4e3b7593dd60062d792c7400781'

def sha(data):return hashlib.sha256(data).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--ref',choices=('index','HEAD'),required=True)
    parser.add_argument('--receipt',type=Path,required=True);args=parser.parse_args()
    if args.receipt.exists():raise FileExistsError('独立Git核对回执不覆盖')
    assert not args.receipt.resolve().is_relative_to(FOLDER.resolve()),'审计回执必须在封存目录外'
    identity=read(FOLDER/'identity.json');assert identity['plan_sha256']==PLAN_SHA and identity['zip_crc_and_member_sha256_passed']
    assert sha((FOLDER/'plan.json').read_bytes())==PLAN_SHA
    assert identity['sha_checks']==2688 and identity['image_apply_calls']==5568 and identity['rss_processes']==12
    rows=read(FOLDER/'members.json');assert len(rows)==identity['original_member_count']
    # 独立列出固定原件集合，不导入归档器，也不扩展到222份历史源闭包。
    raw_expected={'artifacts/p16-direct-cache2-perf-frozen-v2/'+v for v in ('plan.json','expected-pixels-v2.json')}
    raw_expected.update('artifacts/p16-direct-cache2-perf-launch-v2/'+v for v in
        ('process-preflight.json','controller-start.json','controller-end.json','controller.log'))
    formal={'executed-plan.json','statistics.json','results.json','fraction-audit.json'}
    roles=('87-a399','87-best','293-best','294-best','293-max41','294-max41')
    for profile in ('U','P'):
        for number in range(4):formal.update(f'{profile}-worker{number}{suffix}' for suffix in ('.json','.log','-pending.json','-partial.json'))
        for role in roles:formal.update(f'{profile}-rss-{role}{suffix}' for suffix in ('.json','.log'))
    raw_expected.update('artifacts/p16-direct-cache2-perf-v2/'+v for v in formal)
    raw_expected.update(MEASURED);raw_expected.update(POST);raw_expected.add(FAILURE)
    assert {r['member'] for r in rows}==raw_expected and len(rows)==len(raw_expected)
    with zipfile.ZipFile(FOLDER/'evidence.zip') as archive:
        assert archive.testzip() is None and len(archive.namelist())==len(rows)
        assert set(archive.namelist())==raw_expected
        for row in rows:
            raw=archive.read(row['member']);assert len(raw)==row['bytes'] and sha(raw)==row['sha256']
            assert sha((ROOT/row['member']).read_bytes())==row['sha256'],row['member']
        # 从ZIP独立核证据链接，不能只认可每个成员各自的manifest SHA。
        prefix='artifacts/p16-direct-cache2-perf-v2/'
        frozen_prefix='artifacts/p16-direct-cache2-perf-frozen-v2/'
        frozen_bytes=archive.read(frozen_prefix+'plan.json');assert sha(frozen_bytes)==PLAN_SHA
        plan=json.loads(frozen_bytes)
        # 独立建立无重复规范键映射，不能借归档器的映射或改写原计划SHA。
        normalized={}
        for original,value in plan['sources_sha256'].items():
            canonical=original.replace('\\','/');assert canonical not in normalized,(original,canonical)
            normalized[canonical]=value
        assert identity['measured_source_sha256']=={p:normalized[p] for p in MEASURED}
        for relative in MEASURED:assert sha(archive.read(relative))==normalized[relative]
        assert json.loads(archive.read(prefix+'executed-plan.json'))==plan
        assert json.loads(archive.read(frozen_prefix+'expected-pixels-v2.json'))['models']==plan['expected']
        formal_results=json.loads(archive.read(prefix+'results.json'));assert formal_results['passed']
        assert set(formal_results['worker_sha256'])=={f'{p}-{n}' for p in ('U','P') for n in range(4)}
        for profile in ('U','P'):
            for number in range(4):
                worker_bytes=archive.read(prefix+f'{profile}-worker{number}.json')
                assert sha(worker_bytes)==formal_results['worker_sha256'][f'{profile}-{number}']
                worker=json.loads(worker_bytes)
                assert worker['passed'] and worker['profile']==profile and worker['worker']==number
        copy_expected={'plan.json':frozen_prefix+'plan.json','expected-pixels.json':frozen_prefix+'expected-pixels-v2.json',
            'statistics.json':prefix+'statistics.json','fraction-audit.json':prefix+'fraction-audit.json',
            'controller-end.json':'artifacts/p16-direct-cache2-perf-launch-v2/controller-end.json',
            'process-preflight.json':'artifacts/p16-direct-cache2-perf-launch-v2/process-preflight.json'}
        assert set(identity['copy_sources'])==set(copy_expected)
        for name,original in copy_expected.items():
            assert identity['copy_sources'][name]['original']==original
            assert (FOLDER/name).read_bytes()==archive.read(original),name
        started=json.loads(archive.read('artifacts/p16-direct-cache2-perf-launch-v2/controller-start.json'))
        completed=json.loads(archive.read('artifacts/p16-direct-cache2-perf-launch-v2/controller-end.json'))
        assert started['plan_sha256']==PLAN_SHA and completed['controller_exit_code']==0
        assert completed['started']==started['started'] and completed['output']==started['output']
        if 'plan_sha256' in completed:assert completed['plan_sha256']==PLAN_SHA
    for relative in MEASURED:
        assert sha((ROOT/relative).read_bytes())==identity['measured_source_sha256'][relative]
    assert set(identity['post_source_sha256'])==set(POST)
    for relative in POST:assert sha((ROOT/relative).read_bytes())==identity['post_source_sha256'][relative]
    assert identity['failure_record']['path']==FAILURE and sha((ROOT/FAILURE).read_bytes())==identity['failure_record']['sha256']
    assert sha((ROOT/POST[2]).read_bytes())==identity['archive_script_sha256'] and identity['copy_bytes_equal_to_original']
    for name,spec in identity['copy_sources'].items():assert sha((FOLDER/name).read_bytes())==spec['sha256']
    own=['.gitattributes',DOC,*MEASURED,*POST]
    own += [p.relative_to(ROOT).as_posix() for p in sorted(FOLDER.rglob('*')) if p.is_file()]
    assert len(own)==len(set(own));text_paths={'.gitattributes',DOC};expected={}
    for relative in own:
        raw=(ROOT/relative).read_bytes();expected[relative]=sha(raw.replace(b'\r\n',b'\n') if relative in text_paths else raw)
    prefix=':' if args.ref=='index' else 'HEAD:'
    result=subprocess.run(['git','cat-file','--batch'],cwd=ROOT,input=''.join(prefix+p+'\n' for p in expected).encode(),capture_output=True,check=True)
    blobs=result.stdout;position=0
    for relative,value in expected.items():
        end=blobs.index(b'\n',position);header=blobs[position:end].split()
        assert len(header)==3 and header[1]==b'blob',relative
        size=int(header[2]);assert sha(blobs[end+1:end+1+size])==value,relative;position=end+size+2
    assert position==len(blobs)
    if args.ref=='index':
        staged=subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ROOT).decode().split('\0')
        assert set(staged)-{''}<=set(own),staged
    receipt={'ref':args.ref,'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'all_sha256_passed':True,'explicit_whitelist_paths':len(own),'zip_members_verified':len(rows),
        'text_normalization_only':sorted(text_paths),'checker_sha256':sha(Path(__file__).read_bytes()),'expected':expected,
        'scope':'本阶段白名单/ZIP/原始字节增量核对；不复跑计时、native或Fraction统计，不恢复任何旧资格。'}
    args.receipt.parent.mkdir(parents=True,exist_ok=True)
    args.receipt.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k!='expected'},ensure_ascii=False))

if __name__=='__main__':main()
