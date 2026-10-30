"""标准库独立复算24—30全部性能回执、输出身份及冻结源；不加载库或重新计时。"""
import argparse,hashlib,json,math
from pathlib import Path
from statistics import median
ROOT=Path(__file__).resolve().parents[1]
CASES=[('direct16',24,'windows'),('byteindex',25,'windows'),('paged32',26,'linux'),('pageindex',27,'linux'),('fused16',28,'linux'),('load16',29,'linux'),('tileindex',30,'linux')]
EXPECTED='f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def local(p):
    p=str(p)
    if p.startswith('/mnt/f/'):p='F:/'+p[7:]
    path=Path(p);return path if path.is_absolute() else ROOT/path
def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--output',type=Path,required=True);args=a.parse_args()
    if args.output.exists():raise ValueError('不得覆盖既有审计')
    results=[];legacy_rounds=0;out_rounds=0
    for name,revision,system in CASES:
        folder=ROOT/('artifacts/skylake-'+name+('-linux' if system=='linux' else '')+'-perf-v1')
        run=read(folder/'run.json');result=read(folder/'results.json');policy=run['policy']
        assert policy['repeats']==5 and policy['orders']==[['reference','candidate'],['candidate','reference'],['candidate','reference'],['reference','candidate']]
        for spec in policy.values():
            if isinstance(spec,dict) and 'path' in spec and 'sha256' in spec:assert sha(local(spec['path']))==spec['sha256'],spec
        for p,digest in run['source_sha256'].items():assert sha(local(p))==digest,p
        build=read(local(policy['build']['path']));assert build['revisions']=={'reference':23,'candidate':revision}
        workers=[]
        for index in range(4):
            p=folder/f'worker{index}.json';assert sha(p)==result['worker_sha256'][index];w=read(p);workers.append(w)
            assert w['worker_index']==index and w['order']==policy['orders'][index] and w['thread_order']==policy['thread_orders'][index]
            assert w['actual_affinity']==[0,2,4,6] and len(w['records'])==4
            assert w['build_sha256']==policy['build']['sha256']
            for r in w['records']:
                assert r['library_revision']==(revision if r['variant']=='candidate' else 23)
                assert r['library_sha256']==build['libraries'][r['variant']]['sha256']
                assert r['warmup_output_sha256']==EXPECTED and r['per_round_output_sha256']==[EXPECTED]*5
                assert len(r['apply_seconds'])==5 and all(math.isfinite(t) and t>0 for t in r['apply_seconds'])
                copy_key='legacy_copy_apply_seconds' if revision>=28 else 'copy_apply_seconds'
                assert len(r[copy_key])==5 and all(a<=c for a,c in zip(r['apply_seconds'],r[copy_key]));legacy_rounds+=5
                if revision>=28:
                    assert r['outplace_output_sha256']==[EXPECTED]*5 and len(r['outplace_seconds'])==5
                    assert r['mode_orders']==[(['legacy','outplace'] if (index+j)%2==0 else ['outplace','legacy']) for j in range(5)];out_rounds+=5
                if system=='linux' and r['variant']=='candidate':
                    for pk in ('paged_info','paged_info_after_rounds'):
                        assert r[pk]['aligned_2m'] and r[pk]['anon_huge_bytes']>=(2**25 if revision in (28,29) else r[pk]['bytes'])
        paired=[]
        for threads in (1,4):
            matches=[{r['variant']:r for r in w['records'] if r['requested_threads']==threads} for w in workers]
            record=next(r for r in result['paired'] if r['requested_threads']==threads)
            fields=[('apply_seconds','apply'),(copy_key,'legacy_copy_apply' if revision>=28 else 'copy_apply')]
            if revision>=28:fields.append(('outplace_seconds','outplace'))
            stats={'requested_threads':threads}
            for key,label in fields:
                ratios=[median(m['candidate'][key])/median(m['reference'][key]) for m in matches]
                assert ratios==record[f'process_{label}_ratios'] and median(ratios)==record[f'median_{label}_ratio']
                stats[label+'_ratio']=median(ratios);stats[label+'_throughput_multiple']=1/median(ratios)
            paired.append(stats)
        assert result['measurement_completed'] and not result['accepted_on_this_host']
        results.append({'candidate_revision':revision,'environment':system,'performance_directory':folder.relative_to(ROOT).as_posix(),'paired':paired,'threefold_accepted':False})
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps({'pass':True,'purpose':__doc__,'cases':results,'legacy_rounds':legacy_rounds,'outplace_rounds':out_rounds,'new_native_calls':0,'new_performance_calls':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('独立复算通过：',len(results),'候选，旧接口轮次',legacy_rounds,'新增真实输出轮次',out_rounds)
if __name__=='__main__':main()
