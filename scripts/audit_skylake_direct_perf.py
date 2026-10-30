"""从四个完整绑定进程独立复算；不加载动态库、不重新计时，按冻结格式核验实际容量，允许原汇总层失败。"""
import argparse,math
from pathlib import Path
from statistics import median
from skylake_server_support import ROOT,read,save,digest,checked
EXPECTED='f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528'
def task_state(records,cpus):
    assert records and all(len(r['allowed_cpus'])==1 and r['allowed_cpus'][0] in cpus for r in records)
    assert {r['allowed_cpus'][0] for r in records}==set(cpus)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--performance',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('不得覆盖已有复算')
    run=read(a.performance/'run.json');policy=run['policy'];cpus=policy['affinity_cpus'];assert cpus==[0,2,4,6]
    assert policy['repeats']==5 and policy['affinity_protocol']['OMP_PROC_BIND']=='TRUE'
    assert policy['affinity_protocol']['OMP_PLACES']=='{0},{2},{4},{6}'
    for spec in policy.values():
        if isinstance(spec,dict) and 'path' in spec and 'sha256' in spec:checked(spec)
    build=read(checked(policy['build']));full=read(checked(policy['full_acceptance']));assert full['pass'] and full['build_sha256']==policy['build']['sha256']
    assert full['guarded_page_comparisons']>=320 and all(x==2**24 for x in full['outplace_full_pixels'].values())
    assert read(checked(policy['pinning_probe']))['pass']
    for name,sha in run['source_sha256'].items():assert digest(ROOT/name)==sha,name
    workers=[];rounds=0
    for index in range(4):
        w=read(a.performance/f'worker{index}.json');workers.append(w)
        assert w['worker_index']==index and w['order']==policy['orders'][index] and w['thread_order']==policy['thread_orders'][index]
        assert w['actual_affinity']==[0] and w['selected_cpus']==cpus and w['source_sha256']==policy['photos']['sha256']
        assert w['build_sha256']==policy['build']['sha256'] and w['full_acceptance_sha256']==policy['full_acceptance']['sha256']
        assert w['initial_team']['cpus']==cpus;task_state(w['initial_team']['task_affinities'],cpus)
        assert len(w['records'])==4
        for r in w['records']:
            t=r['requested_threads'];assert r['actual_team']['cpus']==cpus[:t] and r['actual_team']['actual']==t
            assert r['actual_affinity']==[0];task_state(r['actual_team']['task_affinities'],cpus);task_state(r['task_affinities_after_rounds'],cpus)
            assert r['library_revision']==build['revisions'][r['variant']] and r['library_sha256']==build['libraries'][r['variant']]['sha256']
            for key in ('per_round_output_sha256','outplace_output_sha256'):assert r[key]==[EXPECTED]*5
            for key in ('apply_seconds','legacy_copy_apply_seconds','outplace_seconds'):assert len(r[key])==5 and all(math.isfinite(x) and x>0 for x in r[key])
            assert all(x<=y for x,y in zip(r['apply_seconds'],r['legacy_copy_apply_seconds']))
            assert r['mode_orders']==[(['legacy','outplace'] if (index+j)%2==0 else ['outplace','legacy']) for j in range(5)]
            if r['variant']=='candidate':
                sizes={9:(2**22,2**24),10:(2**22,2**24),11:(2**21,2**23),12:(2**24,2**26)}
                state=r['direct_info'];assert state['enabled']==1 and state['format'] in sizes
                entries,capacity=sizes[state['format']]
                assert state['entries']==entries and state['table_capacity_bytes']==capacity
                for key in ('paged_info','paged_info_after_rounds'):assert r[key]['fully_huge'] and r[key]['bytes']==capacity
            rounds+=5
    paired=[];failed=[]
    for threads in (1,4):
        matches=[{r['variant']:r for r in w['records'] if r['requested_threads']==threads} for w in workers]
        stats={'requested_threads':threads}
        for key,label in [('apply_seconds','apply'),('legacy_copy_apply_seconds','legacy_copy_apply'),('outplace_seconds','outplace')]:
            ratios=[median(m['candidate'][key])/median(m['reference'][key]) for m in matches]
            stats['process_'+label+'_ratios']=ratios;stats['median_'+label+'_ratio']=median(ratios);stats[label+'_throughput_multiple']=1/median(ratios)
        prep=[m['candidate']['prepare_plus_first_100_outplace_seconds']/m['reference']['prepare_plus_first_100_outplace_seconds'] for m in matches]
        stats['process_prepare_plus_100_outplace_ratios']=prep;stats['median_prepare_plus_100_outplace_ratio']=median(prep)
        g=policy['adoption_gate']
        if stats['median_apply_ratio']>g['median_apply_ratio_max']:failed.append(f'{threads}线程纯映射未达三倍')
        if stats['median_outplace_ratio']>g['median_outplace_ratio_max']:failed.append(f'{threads}线程真实输出未达三倍')
        if max(stats['process_apply_ratios'])>g['any_process_apply_ratio_max']:failed.append(f'{threads}线程某进程回退超限')
        if median(prep)>g['median_prepare_plus_100_ratio_max']:failed.append(f'{threads}线程准备加首组回退')
        paired.append(stats)
    assert rounds==80
    result={'pass':True,'purpose':__doc__,'worker_measurements_completed':True,'original_aggregation_completed':(a.performance/'results.json').exists(),'accepted_on_this_host':not failed,'legacy_interface_threefold_accepted':all(r['median_legacy_copy_apply_ratio']<=1/3 for r in paired),'failed_gates':failed,'paired':paired,'worker_sha256':[digest(a.performance/f'worker{i}.json') for i in range(4)],'script_sha256':digest(__file__),'new_native_calls':0,'new_performance_calls':0,'mode_rounds':{'legacy':80,'outplace':80},'scope':'独立复算完整四进程，不选取v1失败运行中的部分记录，不将汇总修复伪装为新测量'}
    save(a.output,result);print('绑定记录独立复算完成',result['accepted_on_this_host'],paired)
if __name__=='__main__':main()
