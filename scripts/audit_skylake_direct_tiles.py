"""离线复核53—55的冻结源、72组完整色域与12项计数；不调用像素或重计时。"""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def local(p):
    p=str(p).replace('\\','/')
    if p.startswith('/mnt/f/'):p='F:/'+p[7:]
    q=Path(p);return q if q.is_absolute() else ROOT/q
def sources(d):
    for n,h in d['source_sha256'].items():assert sha(local(n))==h,n
def tasks(xs):assert len(xs)==4 and all(len(x['allowed_cpus'])==1 for x in xs) and {x['allowed_cpus'][0] for x in xs}=={0,2,4,6}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('不得覆盖研究审计')
    cases=[]
    for name,revision,fmt,size,memory in [('directtile',53,16,2**26,78378292),('tilexy',54,17,2**24,28046644),('clangload',55,9,2**24,28046644)]:
        planpath=ROOT/f'experiments/skylake-{name}-v1.json';plan=read(planpath);sources(plan)
        validation=read(ROOT/f'experiments/skylake-{name}-validation-v1.json');sources(validation);assert validation['plan_sha256']==sha(planpath)
        buildpath=ROOT/f'artifacts/skylake-{name}-linux-build-v1/build.json';build=read(buildpath);sources(build)
        assert build['plan_sha256']==sha(planpath) and build['revisions']=={'reference':23,'candidate':revision}
        assert build['libraries']['reference']['sha256']=='b547cd18aa80d686b39a1c969d8006c04aafb2828ea541bc15cf96ce516dee1e'
        for spec in build['libraries'].values():assert sha(local(spec['path']))==spec['sha256']
        fullpath=ROOT/f'artifacts/skylake-{name}-linux-full-v1/results.json';d=read(fullpath);sources(read(fullpath.parent/'run.json'))
        assert d['pass'] and d['build_sha256']==sha(buildpath) and d['libraries']==build['libraries']
        assert d['direct_info']['format']==fmt and d['direct_info']['table_capacity_bytes']==size
        if revision==55:
            baseline=read(ROOT/'artifacts/skylake-batchspan-linux-full-v1/results.json')
            assert d['direct_table_sha256']==baseline['direct_table_sha256']
            assert (ROOT/'experiments/skylake-clangload-runtime/channel_avx2.cpp').read_bytes()==(ROOT/'experiments/skylake-batchspan-runtime/channel_avx2.cpp').read_bytes()
            assert build['kernel_compiler']['sha256']==plan['clangload_policy']['compiler']['sha256']
        assert len(d['full_domain_pixels_per_configuration'])==len(d['outplace_full_pixels'])==12
        assert all(x==2**24 for x in [*d['full_domain_pixels_per_configuration'].values(),*d['outplace_full_pixels'].values()])
        assert d['finite_backend_offset_comparisons']==2208 and d['outplace_finite_comparisons']==4416 and d['guarded_page_comparisons']==736 and d['stream_alignment_comparisons']==1280
        assert d['outplace_negative_checks']==44 and d['independent_table_colors']==2**24 and d['full_input_chunk_pixels']==262144
        assert d['model_accounting_bytes']['candidate']=={'single':272859,'chain':memory}
        assert d['byte_mismatches']==d['sentinel_mismatches']==d['performance_calls']==0
        static=read(ROOT/f'artifacts/skylake-{name}-linux-static-v1/results.json');assert static['pass'] and static['script_sha256']==sha(ROOT/f'scripts/inspect_skylake_{name}.py') and static['build_sha256']==sha(buildpath)
        assert static['external_calls']==static['pext_instructions']==0
        folder=ROOT/f'artifacts/skylake-{name}-pmu-v1';pmu=read(folder/'results.json');sources(read(folder/'run.json'))
        assert pmu['profile_completed'] and len(pmu['records'])==4 and pmu['candidate_wallclock_timing_calls']==0 and pmu['candidate_warmup_calls']==pmu['candidate_counted_calls']==4
        for row in pmu['records']:
            tasks(row['tasks_before']);tasks(row['tasks_after']);assert row['multiplexing_acceptable']
            team=row['actual_team'];assert team['actual']==team['requested']==row['requested_threads'] and team['cpus']==[0,2,4,6][:team['actual']]
            assert all(x['running_fraction']>=.99 for x in row['thread_counters'])
            sums={k:sum(x['counts'][k] for x in row['thread_counters']) for k in row['sum_counts']};assert sums==row['sum_counts']
            assert row['cycles_per_pixel']==sums['cycles']/78643200 and row['instructions_per_pixel']==sums['instructions']/78643200
            assert row['output_sha256']=='f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528'
            expected_size=2**24 if row['variant']=='reference40' else size
            expected_fmt=9 if row['variant']=='reference40' else fmt
            assert row['paged_info']['fully_huge'] and row['paged_info']['bytes']==expected_size and row['direct_info']['format']==expected_fmt
        ratios={}
        for t in [1,4]:
            group={x['variant']:x for x in pmu['records'] if x['requested_threads']==t};ratios[str(t)]=group[name+str(revision)]['cycles_per_pixel']/group['reference40']['cycles_per_pixel']
        gate=plan[name+'_policy']['pmu_screen'];accepted=ratios['1']<=gate['one_thread_cycle_ratio_max'] and ratios['4']<=gate['four_thread_cycle_ratio_max']
        decision=read(folder/'screen-decision.json');assert not accepted and not decision['pass'] and decision['pmu_sha256']==sha(folder/'results.json') and decision['ratios']==ratios
        cases.append({'revision':revision,'name':name,'cycle_ratios':ratios,'screen_pass':False,'full_sha256':sha(fullpath),'direct_table_sha256':d['direct_table_sha256'],'pmu_records':pmu['records']})
    result={'pass':True,'purpose':__doc__,'script_sha256':sha(__file__),'cases':cases,'new_full_domain_api_configurations':72,'new_independent_table_checks':3,'pmu_profiles':12,'full_wallclock_performance_calls':0,'threefold_goal_completed':False,'new_native_calls':0,'new_performance_calls':0}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('53—55离线复核通过：72组全域、12项单次计数，均未进入整轮性能')
if __name__=='__main__':main()
