"""独立复算最终模型同87库性能原始数组，不执行颜色内核或重新计时。"""
import argparse
import hashlib
import json
from pathlib import Path
import statistics as st

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('directory',type=Path);a=p.parse_args();d=a.directory
    result=read(d/'results.json');plan=read(d/'executed-plan.json');pre=read(d/'preflight.json')
    workers=[read(d/f'worker{i}.json') for i in range(4)]
    assert result['worker_sha256']==[sha(d/f'worker{i}.json') for i in range(4)]
    assert all(w['source_sha256']==pre['source_sha256'] for w in workers)
    controls=[];retained=[]
    for threads in (1,4):
        pairs=[{r['role']:r for r in w['records'] if r['threads']==threads} for w in workers]
        row=next(r for r in result['summary'] if r['threads']==threads)
        for key in ('apply','copy_apply','outplace'):
            ratios=[st.median(p['candidate'][key])/st.median(p['baseline'][key]) for p in pairs]
            assert row[key]['time_ratios']==ratios and row[key]['median_time_ratio']==st.median(ratios)
            assert row[key]['worst_throughput_retained']==1/max(ratios)
            if key in ('apply','outplace'):retained.extend(1/r for r in ratios)
        for name in ('baseline','candidate'):
            assert all(p[name]['output_sha256']==pre['oracle_photo_outputs'][name]['whole_sha256'] for p in pairs)
            values=[st.median(p[name]['control_apply'])/st.median(p[name]['apply']) for p in pairs]
            assert row['controls'][name]==values;controls.extend(values)
        assert row['prepare_time_ratios']==[p['candidate']['prepare_seconds']/p['baseline']['prepare_seconds'] for p in pairs]
        assert row['prepare_plus_cold_outplace4_ratios']==[(p['candidate']['prepare_seconds']+p['candidate']['cold_outplace4_seconds'])/(p['baseline']['prepare_seconds']+p['baseline']['cold_outplace4_seconds']) for p in pairs]
    valid=all(plan['gates']['control_any_min']<=v<=plan['gates']['control_any_max'] for v in controls)
    assert valid==result['control_valid'] and min(retained)==result['worst_throughput_retained']
    assert result['grades']=={str(v):valid and min(retained)>=v/100 for v in (100,90,80,70,60,50)}
    assert result['meets_50_percent_speed_floor']==(valid and min(retained)>=.5)
    no_obvious=valid and all(r[k]['median_time_ratio']<=1.05 and max(r[k]['time_ratios'])<=1.1 for r in result['summary'] for k in ('apply','outplace'))
    assert no_obvious==result['no_obvious_slowdown']
    print(json.dumps({'raw_statistics_verified':True,'control_valid':valid,'control_min':min(controls),'control_max':max(controls),
        'worst_throughput_retained':min(retained),'grades':result['grades'],'no_obvious_slowdown':no_obvious},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
