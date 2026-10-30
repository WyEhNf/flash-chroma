"""copy4发布前以Fraction复核全部真实调用/96门与20档，保留失效和有效低50。"""
import argparse
from decimal import Decimal,localcontext
from fractions import Fraction
from pathlib import Path
from study_memory_rom import ROOT,sha,read,save

def median(values):
    ordered=sorted(values)
    n=len(ordered)
    return Fraction(ordered[n//2]) if n%2 else Fraction(ordered[n//2-1]+ordered[n//2],2)

def tier(value):return next((threshold for threshold in (100,90,80,70,60,50) if value>=Fraction(threshold,100)),None)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quality',type=Path,required=True)
    parser.add_argument('--performance',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    plans=[ROOT/'experiments'/name for name in ('page-id16-copy4-runtime-v1.json','page-id16-copy4-performance-v1.json')]
    for path in plans:
        plan=read(path)
        if any(sha(ROOT/name)!=value for name,value in plan['source_sha256'].items()) or any(sha(name)!=value for name,value in plan['input_sha256'].items()):raise AssertionError('冻结源/输入不同')
    plan=read(plans[1])
    quality=read(args.quality/'quality-audit.json')
    summary=read(args.performance/'summary.json')
    if not quality['audit_passed'] or not summary['audit_passed'] or quality['actual_capacity']!=12633164:raise AssertionError('实际质量/容量不同')
    samples={}
    valid={}
    count=0
    controls=0
    for worker in range(4):
        raw=read(args.performance/('worker'+str(worker))/'results.json')
        if len(raw['rows'])!=260 or not raw['passed'] or raw['plan_sha256']!=sha(plans[1]):raise AssertionError('真实四进程原件不同')
        count+=len(raw['rows'])
        for threads in (1,4):
            for mode in ('in','out'):
                rows=[row for row in raw['rows'] if row['threads']==threads and row['mode']==mode]
                ratio=median([row['wall_ns'] for row in rows if row['kind']=='aa_after'])/median([row['wall_ns'] for row in rows if row['kind']=='aa_before'])
                accepted=Fraction(4,5)<=ratio<=Fraction(5,4)
                controls+=1
                for role in plan['roles']:
                    for phase in (1,2):
                        values=[row['wall_ns'] for row in rows if row['role']==role and row['phase']==phase and row['kind']=='measured']
                        if len(values)!=5:raise AssertionError('真实每阶段不是五次')
                        samples[worker,threads,mode,role,phase]=median(values)
                    own=samples[worker,threads,mode,role,2]/samples[worker,threads,mode,role,1]
                    accepted=accepted and Fraction(4,5)<=own<=Fraction(5,4)
                    controls+=1
                valid[worker,threads,mode]=accepted
    if (count,controls)!=(1040,96):raise AssertionError('真实调用/控制数不同')
    for case in summary['cases']:
        role=case['role'];threads=case['threads'];mode=case['mode']
        ratios=[]
        auxiliary=[]
        for worker in range(4):
            for phase in (1,2):
                candidate=samples[worker,threads,mode,role,phase]
                ratios.append(min(samples[worker,threads,mode,'ref78',phase],samples[worker,threads,mode,'ref80',phase])/candidate)
                if role=='p4_copy4':auxiliary.append(samples[worker,threads,mode,'p4_c99',phase]/candidate)
        worst=min(ratios)
        all_valid=all(valid[worker,threads,mode] for worker in range(4))
        with localcontext() as context:
            context.prec=60
            if str(Decimal(worst.numerator)/Decimal(worst.denominator))!=case['worst_raw_retention']:raise AssertionError('真实Fraction/Decimal最劣不同')
            if auxiliary:
                value=min(auxiliary)
                if str(Decimal(value.numerator)/Decimal(value.denominator))!=case['auxiliary_vs_old_p4_worst_raw_retention']:raise AssertionError('辅助同phase新旧P4比不同')
        if all_valid!=case['all_workers_controls_valid'] or case['tier']!=(tier(worst) if all_valid else None):raise AssertionError('真实控制/档位不同')
    failed=[dict(worker=worker,threads=threads,mode=mode) for (worker,threads,mode),accepted in valid.items() if not accepted]
    save(args.output,dict(audit_passed=True,purpose=__doc__,performance_plan_sha256=sha(plans[1]),quality_plan_sha256=sha(plans[0]),calls=count,controls=controls,valid_cells=sum(valid.values()),invalid_cells=failed,cases=len(summary['cases']),capacity=12633164,scope='全为真实正式raw，另用有理数独立复核；明确1T原地失效清档、1T分离有效低50、4T双模式50限定，不将synthetic预检当测量，不恢复全局资格。'))
    print(dict(audit_passed=True,calls=count,controls=controls,valid_cells=sum(valid.values()),invalid_cells=failed),flush=True)

if __name__=='__main__':main()
