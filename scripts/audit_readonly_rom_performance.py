"""RO正式场离线Decimal复算848调用、四AA、三加载身份和独立六档；不补跑。"""
import argparse
from decimal import Decimal,localcontext
import json
from pathlib import Path
from study_memory_rom import ROOT,read,save,sha
D=Decimal
TIERS=(100,90,80,70,60,50)
def median(values):
    ordered=sorted(values);n=len(ordered)
    return ordered[n//2] if n%2 else (ordered[n//2-1]+ordered[n//2])/2
def close(a,b):
    if abs(a-b)>D('1e-15')*max(D(1),abs(a),abs(b)):raise AssertionError('Decimal与原浮点记录不同')
def compute(directory,plan):
    with localcontext() as context:
        context.prec=60
        load=lambda path:json.loads(path.read_bytes(),parse_float=D)
        workers=[load(directory/f'worker-{i}/results.json') for i in range(4)];summary=load(directory/'summary.json');calls=0
        for index,worker in enumerate(workers):
            if worker['worker_index']!=index or worker['affinity_start']['actual']['allowed']!=[0,2,4,6] or worker['affinity_end']['allowed']!=[0,2,4,6] or len(worker['rows'])!=32 or len(worker['controls'])!=4:raise AssertionError('完整角色/允许集不符')
            for row in worker['rows']:
                if len(row['seconds'])!=5 or len(row['cpu_calls'])!=6 or row['seconds']!=[c['seconds'] for c in row['cpu_calls'][1:]]:raise AssertionError('五原轮次不完整')
                close(median(row['seconds']),row['median_seconds'])
            for row in worker['controls']:
                if row['seconds']!=[call['seconds'] for call in row['cpu_calls']] or any(call['phase']!='control' or call['label']!='ref80' for call in row['cpu_calls']):raise AssertionError('AA逐调用原件不符')
            for row in worker['rows']+worker['controls']:
                for call in row['cpu_calls']:
                    if call['cpu_before'] not in (0,2,4,6) or call['cpu_after'] not in (0,2,4,6):raise AssertionError('CPU越允许集')
                    calls+=1
            for label in plan['labels']:
                identity=worker['roles'][label];expected=plan['input_sha256'][plan['reference78'] if label=='ref78' else plan['reference80'] if label=='ref80' else plan['library']]
                if identity['library_sha256']!=expected or identity['capacity']!=(28046644 if label.startswith('ref') else 16779328):raise AssertionError('库/容量身份不同')
                if not label.startswith('ref'):
                    view=worker['views'][label];protection=2 if label.startswith('readonly_') else 8
                    if view['bytes']!=16778272 or any(view[p]['Protect']!=protection or view[p]['Type']!=0x40000 for p in ('first','last')):raise AssertionError('实际映射保护不同')
        if calls!=848 or summary['native_plan_sha256']!=sha(ROOT/'experiments/memory-rom-readonly-performance-v1.json'):raise AssertionError('848调用/计划身份不同')
        result=dict(passed=True,purpose=__doc__,decimal_precision=60,calls=calls,controls={},modes={},auxiliary_pairs=[],rss={})
        for mode in ('inplace','outplace'):
            for threads in (1,4):
                key=f'{mode}_{threads}';times=[];aa=[]
                for worker in workers:
                    current={r['label']:median(r['seconds']) for r in worker['rows'] if r['mode']==mode and r['threads']==threads};times.append(current)
                    row=next(c for c in worker['controls'] if c['mode']==mode and c['threads']==threads)
                    if len(row['seconds'])!=5 or len(row['cpu_calls'])!=5:raise AssertionError('AA五轮不同')
                    value=median(row['seconds'])/current['ref80'];close(value,row['ratio']);aa.append(value)
                valid=all(D('.8')<=v<=D('1.25') for v in aa) and D(1)/D('1.1')<=median(aa)<=D('1.1')
                original=summary['controls'][key]
                if valid!=original['pass_']:raise AssertionError('AA门槛不同')
                for a,b in zip(aa,original['ratios'],strict=True):close(a,b)
                close(median(aa),original['median']);result['controls'][key]=dict(per_worker=[str(v) for v in aa],median=str(median(aa)),pass_=valid)
                rows=[r for r in summary['ratios'] if r['mode']==mode and r['threads']==threads];values={}
                for row in rows:
                    if row['capacity']!=(28046644 if row['label'].startswith('ref') else 16779328):raise AssertionError('摘要容量与角色不同')
                    ratios=[min(t['ref78'],t['ref80'])/t[row['label']] for t in times]
                    for actual,stored in zip(ratios,row['per_worker'],strict=True):close(actual,stored)
                    close(median(ratios),row['speed_retention']);worst=min(ratios)
                    values[row['label']]=dict(accuracy_retention='1',capacity=row['capacity'],per_worker=[str(v) for v in ratios],worst=str(worst),worst_worker=ratios.index(worst),median=str(median(ratios)),control_pass=valid,eligible_speed_tiers=[tier for tier in TIERS if valid and worst>=D(tier)/100])
                result['modes'][key]=values
                for tier in TIERS:
                    eligible=[r for r in rows if valid and D(values[r['label']]['worst'])>=D(tier)/100];selected=min(eligible,key=lambda r:r['capacity'],default=None);stored=summary['tiers'][key][str(tier)]
                    if (selected is None)!=(stored is None) or (selected is not None and selected['label']!=stored['label']):raise AssertionError('最劣六档选择不同')
                for kernel in ('avx','c99'):
                    for control in ('original','cow'):
                        ratios=[t[f'{control}_{kernel}']/t[f'readonly_{kernel}'] for t in times]
                        result['auxiliary_pairs'].append(dict(control=f'{control}_{kernel}',candidate=f'readonly_{kernel}',mode=mode,threads=threads,per_worker=[str(v) for v in ratios],worst=str(min(ratios)),median=str(median(ratios)),control_pass=valid,scope='control耗时/RO耗时，仅辅助，不改变fast78/80主档位。'))
        for label in plan['labels']:
            data=summary['rss'][label]
            if data['affinity_start']['actual']['allowed']!=[0,2,4,6] or data['affinity_end']['allowed']!=[0,2,4,6] or data['model_capacity']!=(28046644 if label.startswith('ref') else 16779328):raise AssertionError('八RSS身份/允许集不符')
            if not label.startswith('ref'):
                protect=2 if label.startswith('readonly_') else 8
                if any(data['view'][p]['Protect']!=protect for p in ('first','last')):raise AssertionError('RSS真实保护不同')
            result['rss'][label]=dict(before=data['before'],prepared=data['prepared'],private_delta=data['prepared']['PrivateUsage']-data['before']['PrivateUsage'],ws_delta=data['prepared']['WorkingSetSize']-data['before']['WorkingSetSize'])
        result['scope']='Windows专属RO loader；模型capacity不变，精度轴独立100%；只读文件保护、提交额度与吞吐分别裁定，AA失败不授档，全部失败保留。'
        return result
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--perf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();plan=read(ROOT/'experiments/memory-rom-readonly-performance-v1.json')
    if any(sha(ROOT/n)!=v for n,v in plan['source_sha256'].items()) or any(sha(n)!=v for n,v in plan['input_sha256'].items()):raise AssertionError('冻结输入/源改变')
    value=compute(a.perf,plan);save(a.output,value);print(dict(passed=True,calls=value['calls']))
if __name__=='__main__':main()
