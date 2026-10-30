"""从八角色全部raw计时独立Decimal复核；不调用原汇总器，不重跑性能。"""
from __future__ import annotations
import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path


def read(path,decimal=False):return json.loads(path.read_text(encoding='utf-8'),parse_float=Decimal if decimal else float)
def close(a,b):return abs(Decimal(str(a))-Decimal(str(b)))<=Decimal('2e-12')*max(Decimal(1),abs(Decimal(str(b))))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--study',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise ValueError('不覆盖独立性能复核')
    identity=read(args.study/'identity.json');plan=identity['plan'];summary=read(args.study/'results.json');comparisons=[];aa=[];checks=0
    lo,hi=map(lambda x:Decimal(str(x)),plan['AA_time_ratio_bounds']);all_source=set()
    for worker in range(plan['workers']):
        raw=read(args.study/f'worker{worker}/results.json',True);all_source.add(raw['source_sha256']);assert raw['worker']==worker and len(raw['groups'])==64
        assert raw['plan_sha256']==identity['plan_sha256'] and raw['driver_sha256']==identity['driver_sha256']
        assert len(raw['prepare'])==8
        for row in raw['prepare']:assert row['output_sha256']==raw['expected_output_sha256'][row['role']];checks+=1
        groups={}
        for row in raw['groups']:
            assert row['output_sha256']==raw['expected_output_sha256'][row['role']] and row['source_readonly']
            key=(row['path'],row['threads'],row['role'],row['phase']);assert key not in groups
            medians={}
            for metric,values in row['seconds'].items():
                assert len(values)==5 and all(v>0 for v in values);middle=sorted(values)[2]
                assert close(row['medians'][metric],middle);medians[metric]=middle;checks+=1
            groups[key]=medians
        for path in plan['paths']:
            for threads in plan['threads']:
                valid={}
                for role in plan['roles']:
                    valid[role]=True
                    for metric,left in groups[path,threads,role,'A'].items():
                        ratio=groups[path,threads,role,'B'][metric]/left;passed=lo<=ratio<=hi;valid[role]&=passed
                        aa.append({'worker':worker,'path':path,'threads':threads,'role':role,'metric':metric,'B_over_A':float(ratio),'pass':passed})
                for left,right in plan['comparisons']:
                    for phase in ('A','B'):
                        for metric,den in groups[path,threads,left,phase].items():
                            ratio=groups[path,threads,right,phase][metric]/den
                            comparisons.append({'worker':worker,'path':path,'threads':threads,'phase':phase,'comparison':right+'/'+left,'metric':metric,
                                'time_ratio':float(ratio),'throughput_retention':float(1/ratio),'AA_valid':valid[left] and valid[right]})
    assert len(all_source)==1 and len(aa)==192 and len(comparisons)==528
    key=lambda r:tuple(r[n] for n in ('worker','path','threads','role','metric'))
    original={key(r):r for r in summary['AA']}
    for row in aa:
        other=original[key(row)];assert row['pass']==other['pass'] and close(row['B_over_A'],other['B_over_A']);checks+=1
    key=lambda r:tuple(r[n] for n in ('worker','path','threads','phase','comparison','metric'))
    original={key(r):r for r in summary['comparisons']}
    for row in comparisons:
        other=original[key(row)];assert row['AA_valid']==other['AA_valid'] and close(row['time_ratio'],other['time_ratio']) and close(row['throughput_retention'],other['throughput_retention']);checks+=1
    pairs={}
    for left,right in plan['comparisons']:
        name=right+'/'+left;rows=[r for r in comparisons if r['comparison']==name];valid=[r for r in rows if r['AA_valid']];worst=min((r['throughput_retention'] for r in valid),default=None)
        original=summary['pairs'][name];assert original['valid_rows']==len(valid)
        assert (worst is None and original['minimum_valid_throughput_retention'] is None) or close(worst,original['minimum_valid_throughput_retention'])
        tiers={str(t):worst is not None and worst>=t/100 for t in (100,90,80,70,60,50)}
        assert tiers==original['tiers'] and original['rejected_by_valid_below_50']==bool(worst is not None and worst<.5)
        assert original['no_obvious_degradation']==bool(worst is not None and worst>=1/plan['no_obvious_time_ratio_cap'])
        assert original['all_AA_passed_for_pair']==all(r['AA_valid'] for r in rows)
        pairs[name]={'minimum_valid_throughput_retention':worst,'tiers':tiers,'AA_all_passed_for_pair':original['all_AA_passed_for_pair']};checks+=5
    assert summary['AA_all_passed']==all(r['pass'] for r in aa)
    for role in ('288max','288p99'):
        names=[role+'/'+base for base in ('87a399','87old','288old')]
        assert summary['candidate_gates'][role]['hard50']==all(pairs[n]['tiers']['50'] and pairs[n]['AA_all_passed_for_pair'] for n in names)
        assert summary['candidate_gates'][role]['rejected_by_valid_below_50']==any(summary['pairs'][n]['rejected_by_valid_below_50'] for n in names);checks+=2
    result={'pass':True,'checks':checks,'raw_groups':256,'AA_checks':len(aa),'AA_failures':[r for r in aa if not r['pass']],
        'comparisons':len(comparisons),'pairs':pairs,'candidate_gates':summary['candidate_gates'],'performance_reruns':0,'discarded_workers':0,
        'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'从所有raw五次值精确Decimal中位数重算；不调用原汇总，不重跑映射/计时。'}
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'pass':True,'checks':checks,'AA_failures':len(result['AA_failures']),'candidate_gates':summary['candidate_gates']}),flush=True)


if __name__=='__main__':main()
