"""独立复算40首次与一次确认的8进程配对分布；不以最快系列替代确认门槛。"""
import argparse,hashlib,json,math
from pathlib import Path
from statistics import median
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--first',type=Path,required=True);p.add_argument('--confirmation',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('不得覆盖确认复算')
    directories=[a.first,a.confirmation];runs=[read(d/'run.json') for d in directories];policies=[r['policy'] for r in runs];results=[read(d/'results.json') for d in directories]
    for key in ('plan','build','full_acceptance','photos','driver','validation','benchmark_script','pinning_support','pinning_probe','quiet_support','quiet_protocol','adoption_gate','orders','thread_orders','repeats','expected_output_sha256'):
        assert policies[0][key]==policies[1][key],key
    assert policies[1]['confirmation_of']['sha256']==sha(a.first/'results.json') and policies[1]['first_quiet_audit']['sha256']==sha(a.first/'quiet-audit-v1.json')
    rule=policies[1]['confirmation_rule'];assert rule['execute_once'] and '均通过' in rule['series_acceptance']
    workers=[]
    for directory,result in zip(directories,results):
        offline=read(directory/'offline-audit-v1.json');quiet=read(directory/'quiet-audit-v1.json');assert offline['pass'] and quiet['pass'] and len(quiet['quiet_checks'])==5
        assert result['accepted_on_this_host']==offline['accepted_on_this_host']==quiet['accepted_on_this_host']
        for i in range(4):
            path=directory/f'worker{i}.json';assert sha(path)==result['worker_sha256'][i];workers.append(read(path))
    pooled=[];failed=[];gate=policies[0]['adoption_gate']
    for threads in (1,4):
        matches=[{r['variant']:r for r in w['records'] if r['requested_threads']==threads} for w in workers];row={'requested_threads':threads}
        for key,label in [('apply_seconds','apply'),('legacy_copy_apply_seconds','legacy_copy_apply'),('outplace_seconds','outplace')]:
            ratios=[median(m['candidate'][key])/median(m['reference'][key]) for m in matches]
            assert len(ratios)==8 and all(math.isfinite(x) and x>0 for x in ratios)
            row['process_'+label+'_ratios']=ratios;row['median_'+label+'_ratio']=median(ratios);row[label+'_throughput_multiple']=1/median(ratios)
        prep=[m['candidate']['prepare_plus_first_100_outplace_seconds']/m['reference']['prepare_plus_first_100_outplace_seconds'] for m in matches]
        row['process_prepare_plus_100_outplace_ratios']=prep;row['median_prepare_plus_100_outplace_ratio']=median(prep)
        if row['median_apply_ratio']>gate['median_apply_ratio_max']:failed.append(f'{threads}线程8进程纯映射中位未达3倍')
        if row['median_outplace_ratio']>gate['median_outplace_ratio_max']:failed.append(f'{threads}线程8进程真实输出中位未达3倍')
        if max(row['process_apply_ratios'])>gate['any_process_apply_ratio_max']:failed.append(f'{threads}线程某纯映射进程回退超限')
        if median(prep)>gate['median_prepare_plus_100_ratio_max']:failed.append(f'{threads}线程准备加首组中位回退')
        pooled.append(row)
    series=[r['accepted_on_this_host'] for r in results]
    if not all(series):failed.append('两个完整独立系列并非均通过原门槛')
    receipt={'integrity_pass':True,'purpose':__doc__,'threefold_confirmed':not failed,'failed_gates':failed,'series_accepted':series,'pooled':pooled,'series_results_sha256':[sha(d/'results.json') for d in directories],'series_directories':[str(d) for d in directories],'script_sha256':sha(__file__),'new_native_calls':0,'new_performance_calls':0,'scope':'仅当前固定四模型、100图、本机来宾前置空闲协议；完整色域和构建身份另见原验收。旧协议与所有不利进程保留，不代表Skylake实机、官方阈值或含预处理全流程均3倍'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('8进程确认复算完成，3倍确认',receipt['threefold_confirmed'],receipt['failed_gates'])
if __name__=='__main__':main()
