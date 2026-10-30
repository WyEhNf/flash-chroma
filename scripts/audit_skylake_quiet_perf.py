"""离线复算空闲协议原始CPU字段及既有配对结果；不调用原生库或重新计时。"""
import argparse,json,hashlib
from pathlib import Path
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def quiet(path,policy,settle):
    r=read(path);assert r['pass'] and r['policy']==policy and r['actual_settle_min_seconds']==settle
    samples=r['samples'];assert len(samples)==len(r['intervals'])+1
    for sample in samples:
        assert sample['pid1_age_seconds']==sample['uptime_seconds']-sample['pid1_start_ticks']/sample['ticks_per_second']
        assert 0<=sample['pid1_age_seconds']<=sample['uptime_seconds']
        assert set(sample['cpu_ticks'])=={'cpu','cpu0','cpu2','cpu4','cpu6'}
        for row in sample['cpu_ticks'].values():assert row['total']==sum(row['raw_ticks'][:8]) and row['idle']==row['raw_ticks'][3]
    passes=[]
    for old,new,interval in zip(samples,samples[1:],r['intervals']):
        assert new['monotonic']-old['monotonic']>=policy['sample_interval_seconds']-0.01
        assert abs((new['monotonic']-r['start_monotonic'])-interval['elapsed_seconds'])<0.05
        busy={}
        for cpu,row in new['cpu_ticks'].items():
            previous=old['cpu_ticks'][cpu];total=sum(row['raw_ticks'][:8])-sum(previous['raw_ticks'][:8]);idle=row['raw_ticks'][3]-previous['raw_ticks'][3]
            assert total>0 and 0<=idle<=total;busy[cpu]=100*(total-idle)/total
        assert busy==interval['busy_percent']
        settled=interval['elapsed_seconds']>=settle and new['pid1_age_seconds']>=policy['minimum_pid1_age_seconds']
        passed=settled and all(value<=policy['busy_percent_max'] for value in busy.values())
        assert interval['settled']==settled and interval['pass']==passed;passes.append(passed)
    assert all(passes[-policy['consecutive_good_intervals']:]) and len(passes)>=policy['consecutive_good_intervals']
    assert r['elapsed_seconds']>=settle and samples[-1]['pid1_age_seconds']>=policy['minimum_pid1_age_seconds']
    return {'path':str(path),'sha256':sha(path),'elapsed_seconds':r['elapsed_seconds'],'last_busy_percent':r['intervals'][-1]['busy_percent'],'pid1_age_seconds':samples[-1]['pid1_age_seconds'],'raw_intervals':len(r['intervals'])}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--performance',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('不得覆盖旧复算')
    run=read(a.performance/'run.json');policy=run['policy'];q=policy['quiet_protocol'];assert policy['protocol_revision']=='guest-quiet-v1'
    assert q['minimum_parent_settle_seconds']==120 and q['minimum_pid1_age_seconds']==180 and q['sample_interval_seconds']==5 and q['consecutive_good_intervals']==2 and q['busy_percent_max']==10 and q['iowait_is_nonidle']
    rows=[quiet(a.performance/'quiet-parent.json',q,120)]+[quiet(a.performance/f'quiet-worker{i}.json',q,0) for i in range(4)]
    result=read(a.performance/'results.json');offline=read(a.performance/'offline-audit-v1.json');assert offline['pass'] and result['accepted_on_this_host']==offline['accepted_on_this_host']
    for old,new in zip(result['paired'],offline['paired']):
        for key,value in old.items():assert new[key]==value,key
    receipt={'pass':True,'purpose':__doc__,'quiet_checks':rows,'accepted_on_this_host':result['accepted_on_this_host'],'offline_performance_sha256':sha(a.performance/'offline-audit-v1.json'),'script_sha256':sha(__file__),'new_native_calls':0,'new_performance_calls':0,'limitation':'来宾前置空闲不代表宿主独占、锁频控温或Skylake实测'}
    a.output.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('空闲原始字段和配对复算通过，整体门槛',receipt['accepted_on_this_host'])
if __name__=='__main__':main()
