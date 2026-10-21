"""83按冻结首次/唯一确认规则作决定；仅读取原始结果，不执行原生。"""
import hashlib
import json
from pathlib import Path
import statistics
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def spec(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def pooled(first,second):
    workers=[read(base/f'worker{i}.json') for base in (first,second) for i in range(4)]
    rows=[]
    for threads in (1,4):
        ratios={k:[] for k in ('apply','outplace','prepare')};controls=[]
        for w in workers:
            by={r['variant']:r for r in w['records'] if r['requested_threads']==threads}
            for key,array in (('apply','apply_seconds'),('outplace','outplace_seconds')):
                ratios[key].append(statistics.mean(by['candidate'][array])/statistics.mean(by['reference'][array]))
            ratios['prepare'].append(by['candidate']['prepare_plus_first_100_outplace_seconds']/by['reference']['prepare_plus_first_100_outplace_seconds'])
            aa={r['label']:r for r in w['control_records'] if r['requested_threads']==threads}
            controls.append(statistics.mean(aa['B']['apply_seconds'])/statistics.mean(aa['A']['apply_seconds']))
        med={k:statistics.median(v) for k,v in ratios.items()}
        ok=med['apply']<=1/3 and med['outplace']<=1/3 and med['prepare']<=1 and max(ratios['apply'])<=.9
        valid=min(controls)>=.8 and max(controls)<=1.25 and 1/1.10<=statistics.median(controls)<=1.10
        rows.append({'threads':threads,'ratios':ratios,'median_ratios':med,'aa_ratios':controls,'control_valid':valid,'performance_pass':ok})
    return {'pairs':8,'rows':rows,'accepted':all(r['control_valid'] and r['performance_pass'] for r in rows)}
policy_path=ROOT/'experiments/skylake-input256-ordered-long-perf-v1.json';policy=read(policy_path)
first_path=ROOT/'artifacts/skylake-input256-ordered-long-perf-v1/results.json';first=read(first_path)
assert first['measurement_completed']
confirmation=ROOT/policy['confirmation']['output']
output=ROOT/'artifacts/skylake-input256-ordered-confirmation-decision-v1.json'
assert not output.exists(),'不覆盖确认决定'
if first['accepted_on_this_host'] and not confirmation.exists():
    print(json.dumps({'confirmation_permitted':True,'only_once':True,'output':confirmation.relative_to(ROOT).as_posix()},ensure_ascii=False))
else:
    decision={'purpose':__doc__,'first_result':spec(first_path),'policy':spec(policy_path),
        'first_accepted':first['accepted_on_this_host'],'first_control_valid':first['measurement_control_valid'],
        'first_failed_gates':first['failed_gates'],'confirmation_executed':first['accepted_on_this_host'],
        'no_retry_or_sample_selection':True}
    if first['accepted_on_this_host']:
        assert (confirmation/'results.json').exists(),'保留未完成确认，不重试或产生通过结论'
        second=read(confirmation/'results.json');assert second['measurement_completed']
        decision.update(confirmation_result=spec(confirmation/'results.json'),confirmation_accepted=second['accepted_on_this_host'],
            pooled8=pooled(first_path.parent,confirmation),additional_series=1)
        decision['overall_accepted']=first['accepted_on_this_host'] and second['accepted_on_this_host'] and decision['pooled8']['accepted']
    else:decision.update(reason='首次失败，跳过确认，新增系列/原生调用0',additional_series=0,additional_native_calls=0,overall_accepted=False)
    with output.open('x',encoding='utf-8') as stream:json.dump(decision,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps(decision,ensure_ascii=False))
