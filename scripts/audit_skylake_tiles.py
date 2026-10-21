"""离线核验47/49默认与回退全域、单次计数及48未执行边界；不加载库或重新计时。"""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def local(p):
    p=str(p)
    if p.startswith('/mnt/f/'):p='F:/'+p[7:]
    q=Path(p);return q if q.is_absolute() else ROOT/q
def sources(d):
    for n,h in d['source_sha256'].items():assert sha(local(n))==h,n
def tasks(rows):assert rows and all(len(x['allowed_cpus'])==1 for x in rows) and {x['allowed_cpus'][0] for x in rows}=={0,2,4,6}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('不得覆盖研究复核')
    outputs={};profiles=[]
    for name,revision in [('tilebmi2',47),('tilemadd',49)]:
        plan=read(ROOT/f'experiments/skylake-{name}-v1.json');sources(plan)
        buildpath=ROOT/f'artifacts/skylake-{name}-linux-build-v1/build.json';build=read(buildpath);sources(build)
        assert build['revisions']=={'reference':23,'candidate':revision}
        assert build['libraries']['reference']['sha256']=='b547cd18aa80d686b39a1c969d8006c04aafb2828ea541bc15cf96ce516dee1e'
        fulls=[]
        for suffix,forced in [('full',False),('fallback-full',True)]:
            folder=ROOT/f'artifacts/skylake-{name}-linux-{suffix}-v1';d=read(folder/'results.json');sources(read(folder/'run.json'))
            assert d['pass'] and d['build_sha256']==sha(buildpath) and d['libraries']==build['libraries']
            assert d['forced_linear_index']==forced and d['direct_info']['format']==(9 if forced else 15)
            assert len(d['full_domain_pixels_per_configuration'])==12 and len(d['outplace_full_pixels'])==12
            assert all(x==2**24 for x in [*d['full_domain_pixels_per_configuration'].values(),*d['outplace_full_pixels'].values()])
            assert d['finite_backend_offset_comparisons']==2208 and d['outplace_finite_comparisons']==4416
            assert d['stream_alignment_comparisons']==1280 and d['guarded_page_comparisons']==736
            assert d['outplace_negative_checks']==44 and d['independent_table_colors']==2**24 and d['full_input_chunk_pixels']==262144
            assert d['model_accounting_bytes']=={'reference':{'single':272835,'chain':11269404},'candidate':{'single':272859,'chain':28046644}}
            assert d['byte_mismatches']==d['sentinel_mismatches']==d['performance_calls']==0
            fulls.append({'directory':folder.relative_to(ROOT).as_posix(),'forced_linear_index':forced,'sha256':sha(folder/'results.json'),'table_sha256':d['direct_table_sha256']})
        outputs[name]=fulls
        static=read(ROOT/f'artifacts/skylake-{name}-linux-static-v{2 if revision==49 else 1}/results.json')
        assert static['pass'] and static['fallback_identical_to_40'] and not static['runtime_has_pext'] and static['build_sha256']==sha(buildpath)
        pmudir=ROOT/f'artifacts/skylake-{name}-pmu-v1';pmu=read(pmudir/'results.json');sources(read(pmudir/'run.json'))
        assert pmu['profile_completed'] and len(pmu['records'])==4 and pmu['candidate_wallclock_timing_calls']==0
        assert pmu['candidate_warmup_calls']==pmu['candidate_counted_calls']==4
        for x in pmu['records']:
            tasks(x['tasks_before']);tasks(x['tasks_after'])
            assert x['output_sha256']=='f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528'
            assert x['multiplexing_acceptable'] and all(c['running_fraction']>=.99 for c in x['thread_counters'])
            counts={k:sum(c['counts'][k] for c in x['thread_counters']) for k in x['sum_counts']};assert counts==x['sum_counts']
            assert x['cycles_per_pixel']==counts['cycles']/78643200 and x['instructions_per_pixel']==counts['instructions']/78643200
            if x['variant']!='reference40':assert x['revision']==revision and x['direct_info']['format']==15
        ratios=[]
        for t in [1,4]:
            group={x['variant']:x for x in pmu['records'] if x['requested_threads']==t};cand=group[name+str(revision)];ref=group['reference40']
            ratios.append(cand['cycles_per_pixel']/ref['cycles_per_pixel'])
        gate=plan['tilebmi2_policy' if revision==47 else 'tilemadd_policy']['pmu_screen']
        passed=ratios[0]<=gate['one_thread_cycle_ratio_max'] and ratios[1]<=gate['four_thread_cycle_ratio_max']
        decision=read(pmudir/'screen-decision.json');assert not passed and not decision['screen_pass'] and decision['full_performance_skipped'] and decision['profile_sha256']==sha(pmudir/'results.json')
        assert [x['cycles_ratio'] for x in decision['rows']]==ratios
        profiles.append({'revision':revision,'cycle_ratios':ratios,'screen_pass':False,'records':pmu['records']})
    assert [x['table_sha256'] for x in outputs['tilebmi2']]==[x['table_sha256'] for x in outputs['tilemadd']]
    build48=read(ROOT/'artifacts/skylake-tilevector-linux-build-v1/build.json');sources(build48);assert build48['revisions']['candidate']==48
    assert not (ROOT/'artifacts/skylake-tilevector-linux-full-v1').exists() and not (ROOT/'artifacts/skylake-tilevector-pmu-v1').exists()
    assert read(ROOT/'artifacts/skylake-tilevector-preflight-v1/decision.json')['pixel_calls']==0
    failure=read(ROOT/'artifacts/skylake-tilemadd-static-failure-v1/failure.json');assert failure['exit_code']==1 and failure['mnemonic_counts']['pext']==failure['mnemonic_counts']['pdep']==failure['mnemonic_counts']['vpgather']==0 and failure['mnemonic_counts']['vpextr']>0
    result={'pass':True,'purpose':__doc__,'script_sha256':sha(__file__),'full_acceptances':outputs,'new_full_domain_api_configurations':96,'independent_table_colors_per_execution':2**24,'pmu_profiles':profiles,'unexecuted_revision':48,'full_wallclock_performance_calls':0,'threefold_goal_completed':False,'new_native_calls':0,'new_performance_calls':0}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('分块研究离线核验通过；96组全域、8项单次画像，两版均不进入墙钟评估')
if __name__=='__main__':main()
