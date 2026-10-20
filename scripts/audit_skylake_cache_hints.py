"""标准库独立核对38—42、失败容量断言与五组配对PMU画像；不加载库或重新计时。"""
import argparse,hashlib,json,math
from pathlib import Path
from statistics import median
ROOT=Path(__file__).resolve().parents[1]
CASES=[('sourcehint',38,1),('tablehint',39,1),('batchspan',40,1),('skew',41,1),('wordload',42,1)]
EXPECTED='f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def local(p):
    p=str(p)
    if p.startswith('/mnt/f/'):p='F:/'+p[7:]
    path=Path(p);return path if path.is_absolute() else ROOT/path
def check_source(run):
    for name,digest in run['source_sha256'].items():assert sha(local(name))==digest,name
def tasks(rows):
    assert rows and all(len(x['allowed_cpus'])==1 for x in rows)
    assert {x['allowed_cpus'][0] for x in rows}=={0,2,4,6}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('不得覆盖审计')
    cases=[];rounds=0
    for name,revision,version in CASES:
        folder=ROOT/f'artifacts/skylake-{name}-linux-perf-v{version}';run=read(folder/'run.json');policy=run['policy'];check_source(run)
        for spec in policy.values():
            if isinstance(spec,dict) and 'path' in spec and 'sha256' in spec:assert sha(local(spec['path']))==spec['sha256']
        build=read(local(policy['build']['path']));full=read(local(policy['full_acceptance']['path']))
        assert full['pass'] and full['build_sha256']==policy['build']['sha256'] and full['libraries']==build['libraries']
        assert build['revisions']=={'reference':23,'candidate':revision}
        assert len(full['outplace_full_pixels'])==12 and all(n==2**24 for n in full['outplace_full_pixels'].values())
        assert full['outplace_negative_checks']==44
        if revision>=34:assert full['guarded_page_comparisons']>=320
        assert full['stream_alignment_comparisons']==1280
        assert full['independent_table_colors']==2**24
        if revision in (40,42):assert full['full_input_chunk_pixels']==262144
        result=read(folder/('offline-results-v1.json' if revision==34 else 'results.json'));workers=[]
        for index in range(4):
            path=folder/f'worker{index}.json';assert sha(path)==result['worker_sha256'][index];w=read(path);workers.append(w)
            assert w['worker_index']==index and w['order']==policy['orders'][index] and w['thread_order']==policy['thread_orders'][index]
            assert w['build_sha256']==policy['build']['sha256'] and len(w['records'])==4
            assert w['actual_affinity']==([0] if revision>=34 else [0,2,4,6])
            for r in w['records']:
                t=r['requested_threads'];assert r['library_revision']==build['revisions'][r['variant']] and r['library_sha256']==build['libraries'][r['variant']]['sha256']
                assert r['actual_team']['actual']==t and len(set(r['actual_team']['cpus']))==t
                assert set(r['actual_team']['cpus'])<={0,2,4,6}
                if revision>=34:
                    assert r['actual_team']['cpus']==[0,2,4,6][:t];tasks(r['actual_team']['task_affinities']);tasks(r['task_affinities_after_rounds'])
                for key in ('per_round_output_sha256','outplace_output_sha256'):assert r[key]==[EXPECTED]*5
                for key in ('apply_seconds','legacy_copy_apply_seconds','outplace_seconds'):assert len(r[key])==5 and all(math.isfinite(x) and x>0 for x in r[key])
                assert all(x<=y for x,y in zip(r['apply_seconds'],r['legacy_copy_apply_seconds']))
                assert r['mode_orders']==[(['legacy','outplace'] if (index+j)%2==0 else ['outplace','legacy']) for j in range(5)]
                if r['variant']=='candidate':
                    payload=2**23 if revision==42 else 2**24
                    for key in ('paged_info','paged_info_after_rounds'):assert r[key]['aligned_2m'] and r[key]['anon_huge_bytes']>=payload
                rounds+=5
        stats=[]
        for threads in (1,4):
            pairs=[{r['variant']:r for r in w['records'] if r['requested_threads']==threads} for w in workers];original=next(r for r in result['paired'] if r['requested_threads']==threads);row={'requested_threads':threads}
            for key,label in [('apply_seconds','apply'),('legacy_copy_apply_seconds','legacy_copy_apply'),('outplace_seconds','outplace')]:
                ratios=[median(m['candidate'][key])/median(m['reference'][key]) for m in pairs]
                assert original['process_'+label+'_ratios']==ratios and original['median_'+label+'_ratio']==median(ratios)
                row[label+'_ratio']=median(ratios);row[label+'_throughput_multiple']=1/median(ratios)
            prep=[m['candidate']['prepare_plus_first_100_outplace_seconds']/m['reference']['prepare_plus_first_100_outplace_seconds'] for m in pairs]
            assert original['median_prepare_plus_100_outplace_ratio']==median(prep);row['prepare_plus_100_outplace_ratio']=median(prep);stats.append(row)
        assert not result['accepted_on_this_host']
        cases.append({'revision':revision,'performance_directory':folder.relative_to(ROOT).as_posix(),'pinned_protocol':revision>=34,'original_aggregation_completed':revision!=34,'paired':stats,'full_finite_comparisons':full['finite_backend_offset_comparisons'],'full_guarded_comparisons':full.get('guarded_page_comparisons',0)})
    failed=ROOT/'artifacts/skylake-wordload-linux-full-v1'
    assert not (failed/'results.json').exists() and read(failed/'failure-note.json')['exit_code']==1
    check_source(read(failed/'run.json'))
    pmustats=[]
    for name,_,_ in CASES:
        folder=ROOT/f'artifacts/skylake-{name}-pmu-v1';pmurun=read(folder/'run.json');pmu=read(folder/'results.json');check_source(pmurun)
        assert pmu['profile_completed'] and len(pmu['records'])==4 and pmu['candidate_wallclock_timing_calls']==0
        assert pmu['candidate_counted_calls']==4 and pmu['candidate_warmup_calls']==4
        for r in pmu['records']:
            assert r['output_sha256']==EXPECTED and r['multiplexing_acceptable'];tasks(r['tasks_before']);tasks(r['tasks_after'])
            assert {x['tid'] for x in r['tasks_before']}=={x['tid'] for x in r['tasks_after']}
            sums={key:sum(x['counts'][key] for x in r['thread_counters']) for key in r['sum_counts']};assert sums==r['sum_counts']
            assert r['cycles_per_pixel']==sums['cycles']/78643200 and r['instructions_per_pixel']==sums['instructions']/78643200
            pmustats.append({'profile':name,**{k:r[k] for k in ('variant','requested_threads','cycles_per_pixel','instructions_per_pixel','generic_cache_misses_per_pixel','multiplexing_acceptable')}})
    assert rounds==400
    a.output.parent.mkdir(parents=True,exist_ok=True);save={'pass':True,'purpose':__doc__,'cases':cases,'valid_mode_rounds':{'legacy':rounds,'outplace':rounds},'preserved_validation_failure':True,'pmu_sanity':pmustats,'new_native_calls':0,'new_performance_calls':0,'script_sha256':sha(__file__),'threefold_goal_completed':False}
    a.output.write_text(json.dumps(save,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('38—42独立复核通过，完整模式轮次',2*rounds,'PMU画像',len(pmustats),'容量断言失败保留')
if __name__=='__main__':main()
