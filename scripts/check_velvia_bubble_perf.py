"""不导入原汇总器，按原始5次时长的中间值独立重算187三控制与AA。"""
from __future__ import annotations
import argparse
from decimal import Decimal
import json
import math
from pathlib import Path


def close(a,b):
    if not math.isclose(float(a),float(b),rel_tol=1e-12,abs_tol=1e-14):raise AssertionError((a,b))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--measured',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    raw=[json.loads((args.measured/f'worker{n}/results.json').read_text(encoding='utf-8')) for n in range(4)]
    reported=json.loads((args.measured/'results.json').read_text(encoding='utf-8'))
    expected_ratios={(r['worker'],r['dataset'],r['path'],r['threads'],r['phase'],r['comparison'],r['metric']):r for r in reported['comparisons']}
    independent=[];AA=[];checks=0
    for worker in raw:
        if len(worker['groups'])!=48:raise AssertionError('组数不符')
        groups={}
        for row in worker['groups']:
            key=(row['dataset'],row['path'],row['threads'],row['model'],row['phase'])
            if key in groups:raise AssertionError('重复组')
            med={}
            for metric,values in row['seconds'].items():
                if len(values)!=5 or not all(math.isfinite(v) and v>0 for v in values):raise AssertionError('原始时长不符')
                med[metric]=sorted(Decimal(str(v)) for v in values)[2]
                close(med[metric],row['medians'][metric]);checks+=1
            groups[key]=med
            if row['output_sha256']!=worker['expected_output_sha256'][row['dataset']]['on' if row['model']=='187on' else 'off'] or not row['source_readonly']:raise AssertionError('SHA或源可写')
        for dataset,path,t in sorted({key[:3] for key in groups}):
            valid=True
            for model in ('87','187off'):
                for metric in groups[dataset,path,t,model,'A']:
                    ratio=groups[dataset,path,t,model,'B'][metric]/groups[dataset,path,t,model,'A'][metric]
                    passed=Decimal('.85')<=ratio<=Decimal('1.15');valid &= passed
                    AA.append({'worker':worker['worker'],'dataset':dataset,'path':path,'threads':t,'model':model,'metric':metric,'B_over_A':float(ratio),'pass':passed})
            for phase in ('A','B'):
                for left,right in [('87','187off'),('187off','187on'),('87','187on')]:
                    for metric in groups[dataset,path,t,left,phase]:
                        ratio=groups[dataset,path,t,right,phase][metric]/groups[dataset,path,t,left,phase][metric]
                        key=(worker['worker'],dataset,path,t,phase,right+'/'+left,metric);original=expected_ratios.pop(key)
                        close(ratio,original['time_ratio']);close(1/ratio,original['throughput_retention'])
                        if valid!=original['AA_valid']:raise AssertionError('AA有效场判定不同')
                        independent.append({**original,'time_ratio':float(ratio),'throughput_retention':float(1/ratio)});checks+=1
    if expected_ratios:raise AssertionError('存在遗漏比较')
    worst=min((r for r in independent if r['AA_valid']),key=lambda r:r['throughput_retention'])
    close(worst['throughput_retention'],reported['minimum_valid_throughput_retention'])
    failed=[r for r in AA if not r['pass']]
    original_aa={(r['worker'],r['dataset'],r['path'],r['threads'],r['model'],r['metric']):r for r in reported['AA']}
    for row in AA:
        key=tuple(row[n] for n in ('worker','dataset','path','threads','model','metric'))
        previous=original_aa.pop(key);close(row['B_over_A'],previous['B_over_A'])
        if row['pass']!=previous['pass']:raise AssertionError('逐项AA判断不同')
        checks+=1
    if original_aa or bool(failed)==reported['AA_all_passed']:raise AssertionError('全局AA判断不同')
    for percent in (100,90,80,70,60,50):
        if reported['speed_tiers'][str(percent)]!=(worst['throughput_retention']>=percent/100):raise AssertionError('档位错误')
        checks+=1
    breakdown=[]
    for dataset in ('photos','dense'):
        for comparison in ('187off/87','187on/187off','187on/87'):
            for path in ('inplace','true_outplace'):
                for t in (1,4):
                    rows=[r for r in independent if r['dataset']==dataset and r['comparison']==comparison and r['path']==path and r['threads']==t]
                    valid=[r for r in rows if r['AA_valid']]
                    ordered=sorted(r['time_ratio'] for r in valid)
                    breakdown.append({'dataset':dataset,'comparison':comparison,'path':path,'threads':t,'valid_comparisons':len(valid),'invalid_comparisons':len(rows)-len(valid),
                        'minimum_valid_throughput_retention':min((r['throughput_retention'] for r in valid),default=None),
                        'median_valid_time_ratio':float((ordered[(len(ordered)-1)//2]+ordered[len(ordered)//2])/2) if valid else None})
    record={'pass':True,'checks':checks,'raw_groups':sum(len(w['groups']) for w in raw),'AA_checks':len(AA),'AA_failures':failed,
        'minimum_valid_throughput_retention':worst['throughput_retention'],'valid_worst':worst,'breakdown':breakdown,
        'strict_50_floor_rejected':worst['throughput_retention']<.5,
        'scope':'仅独立小JSON重算，不重跑计时/像素；Decimal原始时长排序中值，不导入正式汇总函数；无效场完整列明，不用于挽救有效负例。'}
    args.output.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({n:record[n] for n in ('pass','checks','raw_groups','AA_checks','minimum_valid_throughput_retention','strict_50_floor_rejected')},ensure_ascii=False))
    print(json.dumps({'AA_failures':failed,'breakdown':breakdown},ensure_ascii=False))


if __name__=='__main__':main()
