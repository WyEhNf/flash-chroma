"""只读复算速度阶段原始JSON；不加载原生库或重跑计时。"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import statistics

def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def audit(path):
    full=read(path/'correctness.json')
    assert full['passed'] and full['full_colors']==1<<24 and full['full_byte_mismatches']==0
    assert len(set(full['output_sha256'].values()))==1
    output={'correctness':True}
    if (path/'performance.json').exists():
        result=read(path/'performance.json');workers=[read(path/f'worker{i}.json') for i in range(4)]
        assert result['worker_sha256']==[sha(path/f'worker{i}.json') for i in range(4)]
        assert len({w['source_sha256'] for w in workers})==1
        assert len({r['output_sha256'] for w in workers for r in w['records']})==1
        controls=[]
        for threads in (1,4):
            pairs=[{r['variant']:r for r in w['records'] if r['threads']==threads} for w in workers]
            summary=next(s for s in result['summary'] if s['threads']==threads)
            for key in ('apply','copy_apply','outplace'):
                ratios=[statistics.median(p['candidate'][key])/statistics.median(p['baseline'][key]) for p in pairs]
                assert ratios==summary[key]['ratios']
                assert statistics.median(ratios)==summary[key]['median_ratio']
            for name in ('baseline','candidate'):
                values=[statistics.median(p[name]['control_apply'])/statistics.median(p[name]['apply']) for p in pairs]
                assert values==summary['same_handle_control'][name]
                controls.extend(values)
            assert summary['prepare_ratios']==[p['candidate']['prepare_seconds']/p['baseline']['prepare_seconds'] for p in pairs]
            assert summary['prepare_plus_cold_first_outplace4_ratios']==[
                (p['candidate']['prepare_seconds']+p['candidate']['cold_first_outplace4_seconds'])/
                (p['baseline']['prepare_seconds']+p['baseline']['cold_first_outplace4_seconds']) for p in pairs]
        output.update({'raw_statistics':True,'any_control_outside_10_percent':any(not .9<=v<=1.1 for v in controls),
                       'control_ratio_min':min(controls),'control_ratio_max':max(controls)})
    return output

def prepare(path):
    result=read(path/'results.json');workers=[read(path/f'worker{i}.json') for i in range(4)]
    assert result['worker_sha256']==[sha(path/f'worker{i}.json') for i in range(4)]
    ratios=[]
    for i,w in enumerate(workers):
        durations={n:[r['create_ns']*1e-9 for r in w['records'] if r['variant']==n] for n in ('baseline','candidate')}
        assert all(len(v)==5 for v in durations.values())
        ratio=statistics.median(durations['candidate'])/statistics.median(durations['baseline'])
        assert ratio==result['processes'][i]['process_median_ratio'];ratios.append(ratio)
    assert statistics.median(ratios)==result['median_ratio']
    assert max(ratios)==result['any_process_max']
    assert result['passed_prepare_gate']==(statistics.median(ratios)<=result['gate']['median_ratio_max'] and max(ratios)<=result['gate']['any_process_ratio_max'])
    validity=read(path/'measurement-validity.json') if (path/'measurement-validity.json').exists() else {'measurement_valid':True}
    return {'raw_statistics':True,'passed_numeric_gate':result['passed_prepare_gate'],
            'measurement_valid':validity['measurement_valid'],
            'accepted_prepare':result['passed_prepare_gate'] and validity['measurement_valid'],
            'median_ratio':result['median_ratio']}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('paths',nargs='+',type=Path);args=p.parse_args()
    result={str(path):prepare(path) if (path/'executed-plan.json').exists() else audit(path) for path in args.paths}
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
