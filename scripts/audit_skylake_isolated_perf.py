"""离线核对32个独立配置进程、原始空闲字段及4对配对公式；不重新计时。"""
import argparse,math,statistics
from pathlib import Path
from skylake_server_support import ROOT,read,save,digest,checked
from audit_skylake_quiet_perf import quiet
EXPECTED='f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528'
def tasks(rows,cpus,pid):
    assert rows and all(len(r['allowed_cpus'])==1 and r['allowed_cpus'][0] in cpus for r in rows)
    assert {r['allowed_cpus'][0] for r in rows}==set(cpus) and any(r['tid']==pid for r in rows)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--performance',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('不得覆盖隔离复算')
    run=read(a.performance/'run.json');policy=run['policy'];result=read(a.performance/'results.json');cpus=policy['affinity_cpus'];assert cpus==[0,2,4,6]
    assert policy['protocol_revision']=='isolated-config-v1' and policy['process_isolation']['dimensions']==['role','threads','api_mode']
    assert policy['process_isolation']['children_per_series']==32 and policy['repeats']==5
    for spec in policy.values():
        if isinstance(spec,dict) and 'path' in spec and 'sha256' in spec:checked(spec)
    for name,sha in run['source_sha256'].items():assert digest(ROOT/name)==sha,name
    build=read(checked(policy['build']));full=read(checked(policy['full_acceptance']));assert full['pass'] and full['libraries']==build['libraries'] and full['build_sha256']==policy['build']['sha256']
    assert build['revisions']=={'reference':23,'candidate':40} and full['byte_mismatches']==full['sentinel_mismatches']==0
    for key in ('full_domain_pixels_per_configuration','outplace_full_pixels'):assert len(full[key])==12 and all(x==2**24 for x in full[key].values())
    q=policy['quiet_protocol'];assert q['minimum_parent_settle_seconds']==120 and q['minimum_pid1_age_seconds']==180 and q['busy_percent_max']==10
    quiet_rows=[quiet(a.performance/'quiet-parent.json',q,120)];children={};pids=[];rounds={'legacy':0,'outplace':0};pairs=[]
    for index in range(4):
        for threads in policy['thread_orders'][index]:
            for role in policy['orders'][index]:
                for mode in policy['mode_orders'][index]:
                    key=f'p{index}-t{threads}-{role}-{mode}';path=a.performance/(key+'.json');assert digest(path)==result['child_sha256'][key]
                    quiet_rows.append(quiet(a.performance/('quiet-'+key+'.json'),q,0));w=read(path);children[(index,threads,role,mode)]=w;pids.append(w['pid'])
                    assert w['worker_index']==index and w['role']==role and w['api_mode']==mode and w['order']==[role] and w['thread_order']==[threads]
                    assert w['primary_library_isolated'] and w['actual_affinity']==[0] and w['selected_cpus']==cpus
                    assert w['source_sha256']==policy['photos']['sha256'] and w['source_bytes']==235929600 and w['build_sha256']==policy['build']['sha256']
                    assert w['libraries']=={role:build['libraries'][role]} and len(w['records'])==1
                    tasks(w['initial_team']['task_affinities'],cpus,w['pid'])
                    r=w['records'][0];assert r['variant']==role and r['requested_threads']==threads and r['actual_team']['actual']==threads and r['actual_team']['cpus']==cpus[:threads]
                    assert r['actual_affinity']==[0] and r['library_revision']==build['revisions'][role] and r['library_sha256']==build['libraries'][role]['sha256']
                    tasks(r['actual_team']['task_affinities'],cpus,w['pid']);tasks(r['task_affinities_after_rounds'],cpus,w['pid'])
                    assert r['warmup_output_sha256']==EXPECTED and r['mode_orders']==[[mode]]*5
                    for name in ('apply_seconds','legacy_copy_apply_seconds','outplace_seconds'):
                        expected_count=5 if (name=='outplace_seconds')==(mode=='outplace') else 0
                        assert len(r[name])==expected_count and all(math.isfinite(x) and x>0 for x in r[name])
                    assert r['per_round_output_sha256']==([EXPECTED]*5 if mode=='legacy' else []) and r['outplace_output_sha256']==([EXPECTED]*5 if mode=='outplace' else [])
                    if mode=='legacy':assert all(x<=y for x,y in zip(r['apply_seconds'],r['legacy_copy_apply_seconds'])) and r['prepare_plus_first_100_outplace_seconds'] is None
                    else:assert r['prepare_plus_first_100_outplace_seconds']==r['prepare_wall_seconds']+r['outplace_seconds'][0] and r['prepare_plus_first_100_apply_seconds'] is None and r['prepare_plus_first_100_copy_apply_seconds'] is None
                    if role=='candidate':
                        assert r['direct_info']['format']==9 and r['direct_info']['table_capacity_bytes']==2**24 and r['model_accounting_bytes']==28046644
                        for key_page in ('paged_info','paged_info_after_rounds'):assert r[key_page]['fully_huge'] and r[key_page]['bytes']==2**24 and r[key_page]['aligned_2m']
                    else:assert r['model_accounting_bytes']==11269404
                    selected=build['libraries'][role];assert any(x['sha256']==selected['sha256'] for x in w['loaded_libraries'])
                    other='reference' if role=='candidate' else 'candidate';assert all(x['sha256']!=build['libraries'][other]['sha256'] for x in w['loaded_libraries'])
                    rounds[mode]+=5
        path=a.performance/f'pair{index}.json';assert digest(path)==result['pair_sha256'][index];pair=read(path);pairs.append(pair)
        assert pair['kind']=='derived_pair_of_independent_configuration_processes' and pair['pair_index']==index and len(pair['records'])==4
        for r in pair['records']:
            threads=r['requested_threads'];role=r['variant'];legacy=children[(index,threads,role,'legacy')]['records'][0];out=children[(index,threads,role,'outplace')]['records'][0]
            for field in ('apply_seconds','legacy_copy_apply_seconds'):assert r[field]==legacy[field]
            for field in ('outplace_seconds','prepare_wall_seconds','prepare_plus_first_100_outplace_seconds','model_accounting_bytes'):assert r[field]==out[field]
            for mode,spec in r['measurement_sources'].items():
                child=children[(index,threads,role,mode)];assert spec['pid']==child['pid'] and spec['sha256']==digest(a.performance/spec['file'])
    assert len(children)==len(set(pids))==32 and len(quiet_rows)==33 and rounds=={'legacy':80,'outplace':80} and result['unique_pids']==pids
    stats=[];failed=[];gate=policy['adoption_gate']
    for threads in (1,4):
        matches=[{r['variant']:r for r in pair['records'] if r['requested_threads']==threads} for pair in pairs];row={'requested_threads':threads};original=next(r for r in result['paired'] if r['requested_threads']==threads)
        for name,label in [('apply_seconds','apply'),('legacy_copy_apply_seconds','legacy_copy_apply'),('outplace_seconds','outplace')]:
            ratios=[statistics.median(m['candidate'][name])/statistics.median(m['reference'][name]) for m in matches]
            assert ratios==original['pair_'+label+'_ratios'] and statistics.median(ratios)==original['median_'+label+'_ratio']
            row['pair_'+label+'_ratios']=ratios;row['median_'+label+'_ratio']=statistics.median(ratios);row[label+'_throughput_multiple']=1/statistics.median(ratios)
        prep=[m['candidate']['prepare_plus_first_100_outplace_seconds']/m['reference']['prepare_plus_first_100_outplace_seconds'] for m in matches]
        assert prep==original['pair_prepare_plus_100_outplace_ratios'] and statistics.median(prep)==original['median_prepare_plus_100_outplace_ratio']
        row['pair_prepare_plus_100_outplace_ratios']=prep;row['median_prepare_plus_100_outplace_ratio']=statistics.median(prep)
        if row['median_apply_ratio']>gate['median_apply_ratio_max']:failed.append(f'{threads}线程纯映射未达3倍')
        if row['median_outplace_ratio']>gate['median_outplace_ratio_max']:failed.append(f'{threads}线程真实输出未达3倍')
        if max(row['pair_apply_ratios'])>gate['any_process_apply_ratio_max']:failed.append(f'{threads}线程某配对回退超限')
        if statistics.median(prep)>gate['median_prepare_plus_100_ratio_max']:failed.append(f'{threads}线程准备加首组回退')
        stats.append(row)
    assert result['accepted_on_this_host']==(not failed) and result['failed_gates']==failed
    save(a.output,{'pass':True,'purpose':__doc__,'accepted_on_this_host':not failed,'failed_gates':failed,'paired':stats,'quiet_checks':quiet_rows,'independent_child_processes':32,'mode_rounds':rounds,'script_sha256':digest(__file__),'new_native_calls':0,'new_performance_calls':0,'scope':'原始独立子进程复算通过不等于性能门槛通过，目标机和宿主锁频控温未验证'})
    print('32配置进程及33项空闲核对完成，原门槛',not failed,flush=True)
if __name__=='__main__':main()
