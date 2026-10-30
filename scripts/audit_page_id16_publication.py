"""P4发布前另用有理数核双阶段门与六档，核全部冻结身份，不调用native。"""
import argparse
from decimal import Decimal,localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def read(path):return json.loads(path.read_text(encoding='utf-8'))

def median(values):
    ordered=sorted(values)
    n=len(ordered)
    return Fraction(ordered[n//2]) if n%2 else Fraction(ordered[n//2-1]+ordered[n//2],2)

def tier(value):return next((threshold for threshold in (100,90,80,70,60,50) if value>=Fraction(threshold,100)),None)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quality',type=Path,required=True)
    parser.add_argument('--performance',type=Path,required=True)
    parser.add_argument('--modules',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    plans=[ROOT/'experiments'/name for name in ('page-id16-runtime-v1.json','page-id16-performance-v2.json','page-id16-module-observer-v1.json')]
    for path in plans:
        plan=read(path)
        if any(sha(ROOT/name)!=value for name,value in plan['source_sha256'].items()) or any(sha(Path(name))!=value for name,value in plan.get('input_sha256',{}).items()):raise AssertionError('冻结源或输入不同')
    plan=read(plans[1])
    summary=read(args.performance/'summary.json')
    quality=read(args.quality/'quality-audit.json')
    modules=read(args.modules/'results.json')
    if not summary['audit_passed'] or not quality['audit_passed'] or not modules['passed'] or quality['actual_capacity']!=12633164 or modules['performance_plan_sha256']!=sha(plans[1]) or len(modules['observations'])!=8:raise AssertionError('三个原始阶段/模块范围不同')
    measured={}
    valid={}
    controls=0
    count=0
    for worker in range(4):
        raw=read(args.performance/('worker'+str(worker))/'results.json')
        if len(raw['rows'])!=308 or not raw['passed'] or raw['plan_sha256']!=sha(plans[1]):raise AssertionError('四进程原件不同')
        count+=len(raw['rows'])
        for threads in (1,4):
            for mode in ('in','out'):
                rows=[row for row in raw['rows'] if row['threads']==threads and row['mode']==mode]
                before=median([row['wall_ns'] for row in rows if row['kind']=='aa_before'])
                after=median([row['wall_ns'] for row in rows if row['kind']=='aa_after'])
                accepted=Fraction(4,5)<=after/before<=Fraction(5,4)
                controls+=1
                for role in plan['roles']:
                    for phase in (1,2):
                        samples=[row['wall_ns'] for row in rows if row['role']==role and row['phase']==phase and row['kind']=='measured']
                        if len(samples)!=5:raise AssertionError('每阶段不是五次')
                        measured[worker,threads,mode,role,phase]=median(samples)
                    ratio=measured[worker,threads,mode,role,2]/measured[worker,threads,mode,role,1]
                    accepted=accepted and Fraction(4,5)<=ratio<=Fraction(5,4)
                    controls+=1
                valid[worker,threads,mode]=accepted
    if count!=1232 or controls!=112:raise AssertionError('调用或双阶段控制数不同')
    for case in summary['cases']:
        role=case['role'];threads=case['threads'];mode=case['mode']
        ratios=[]
        for worker in range(4):
            for phase in (1,2):
                baseline=min(measured[worker,threads,mode,'ref78',phase],measured[worker,threads,mode,'ref80',phase])
                ratios.append(baseline/measured[worker,threads,mode,role,phase])
        worst=min(ratios)
        all_valid=all(valid[worker,threads,mode] for worker in range(4))
        with localcontext() as context:
            context.prec=60
            decimal_worst=Decimal(worst.numerator)/Decimal(worst.denominator)
            if str(decimal_worst)!=case['worst_raw_retention']:raise AssertionError('有理数与原Decimal最劣不同')
        if all_valid!=case['all_workers_controls_valid'] or case['tier']!=(tier(worst) if all_valid else None):raise AssertionError('有理数档位/控制不同')
    result=dict(audit_passed=True,purpose=__doc__,performance_plan_sha256=sha(plans[1]),quality_plan_sha256=sha(plans[0]),module_plan_sha256=sha(plans[2]),calls=count,controls=controls,valid_cells=sum(valid.values()),cases=len(summary['cases']),model_capacity=quality['actual_capacity'],scope='另用Fraction对全部24模式最劣、112门和Decimal字符串精确复核；不运行native/图片或恢复历史失败。单fresh模块枚举证据不外推六RSS。')
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(result)

if __name__=='__main__':main()
