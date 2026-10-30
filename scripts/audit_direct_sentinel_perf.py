"""从291原始pair组以50位Decimal独立复算AA/比例/六档；不重跑计时。"""
from __future__ import annotations
from collections import defaultdict
from decimal import Decimal,localcontext
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'artifacts/p16-direct-sentinel-perf-frozen-v1/plan.json'
OUT=ROOT/'artifacts/p16-direct-sentinel-perf-v1'

def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def read(path):return json.loads(Path(path).read_text(encoding='utf-8'),parse_float=Decimal)

def median(values):
    ordered=sorted(values);middle=len(ordered)//2
    return ordered[middle] if len(ordered)%2 else (ordered[middle-1]+ordered[middle])/2

def serial(value):
    if isinstance(value,Decimal):return str(value)
    if isinstance(value,dict):return {key:serial(item) for key,item in value.items()}
    if isinstance(value,list):return [serial(item) for item in value]
    return value

def main():
    target=OUT/'independent-check.json'
    if target.exists():raise FileExistsError('不覆盖独立性能复算')
    plan=read(PLAN);expected=plan['expected_output_sha256'];rows=[];aa=[];cold=[];native_sha=0;pair_checks=0;raw_identity={}
    for number in range(4):
        path=OUT/f'worker{number}/results.json';record=read(path);raw_identity[str(path.relative_to(OUT))]=sha(path)
        assert record['worker']==number and record['plan_sha256']==sha(PLAN) and record['allowed_cpus']==[0,2,4,6]
        assert len(record['cold'])==9 and len(record['groups'])==208 and len(record['warmup'])==104 and len(record['pair_source_checks'])==52
        assert record['source_sha256']==plan['source_sha256']
        assert {row['role'] for row in record['cold']}==set(plan['roles'])
        for row in record['cold']:
            spec=plan['roles'][row['role']];assert row['output_sha256']==expected[spec['model']]
            assert row['python_chain_create_seconds'].is_finite() and row['python_chain_create_seconds']>0
            assert abs(row['create_plus_first_out4_seconds']-(row['python_chain_create_seconds']+row['first_out4_seconds']['api_total_seconds'][0]))<Decimal('1e-12')
            assert len(row['first_out4_seconds']['api_total_seconds'])==1
            cold.append(dict(row,worker=number));native_sha+=1
        warm_keys=[]
        for row in record['warmup']:
            assert row['output_sha256']==expected[plan['roles'][row['role']]['model']]
            assert row['role'] in (row['left'],row['right']);warm_keys.append((row['left'],row['right'],row['path'],row['threads'],row['role']));native_sha+=1
        assert len(set(warm_keys))==104
        source_keys=[]
        for row in record['pair_source_checks']:
            assert row['source_sha256']==plan['source_sha256'];source_keys.append((row['left'],row['right'],row['path'],row['threads']));pair_checks+=1
        assert len(set(source_keys))==52
        groups=defaultdict(list)
        for group in record['groups']:
            assert group['output_sha256']==expected[plan['roles'][group['role']]['model']]
            wanted={'pure_apply_seconds','copy_apply_seconds'} if group['path']=='inplace' else {'api_total_seconds'}
            assert set(group['seconds'])==wanted
            assert all(len(series)==3 and all(value.is_finite() and value>0 for value in series) for series in group['seconds'].values())
            groups[group['left'],group['right'],group['path'],group['threads']].append(group);native_sha+=1
        for left,right in plan['comparisons']:
            for scene in plan['scenes']:
                path=scene['path'];threads=scene['threads'];batch=groups[left,right,path,threads]
                assert len(batch)==4 and {row['position'] for row in batch}==set(range(4))
                mapping={'L':left,'R':right};order=sorted(batch,key=lambda row:row['position'])
                assert [(row['role'],row['phase']) for row in order]==[(mapping[label[0]],int(label[1])) for label in plan['pair_palindromes'][number]]
                by_key={(row['role'],row['phase']):{metric:median(values) for metric,values in row['seconds'].items()} for row in batch}
                valid={}
                for role in (left,right):
                    qualified=True
                    for metric in by_key[role,1]:
                        ratio=by_key[role,2][metric]/by_key[role,1][metric];passed=Decimal('.85')<=ratio<=Decimal('1.15');qualified &= passed
                        aa.append({'worker':number,'left':left,'right':right,'path':path,'threads':threads,'role':role,'metric':metric,'phase2_over_phase1':ratio,'pass':passed})
                    valid[role]=qualified
                for phase in (1,2):
                    for metric in by_key[left,phase]:
                        ratio=by_key[right,phase][metric]/by_key[left,phase][metric]
                        rows.append({'worker':number,'pair':right+'/'+left,'left':left,'right':right,'path':path,'threads':threads,'phase':phase,'metric':metric,'time_ratio':ratio,'throughput_retention':1/ratio,'AA_valid':valid[left] and valid[right]})
    assert native_sha==1284 and pair_checks==208 and len(rows)==624 and len(aa)==624
    summaries={}
    for left,right in plan['comparisons']:
        name=right+'/'+left;selected=[row for row in rows if row['pair']==name];valid=[row for row in selected if row['AA_valid']];all_valid=len(valid)==len(selected);worst=min((row['throughput_retention'] for row in valid),default=None)
        scenes=[]
        for scene in plan['scenes']:
            for metric in ({'pure_apply_seconds','copy_apply_seconds'} if scene['path']=='inplace' else {'api_total_seconds'}):
                subset=[row for row in selected if row['path']==scene['path'] and row['threads']==scene['threads'] and row['metric']==metric];qualified=[row for row in subset if row['AA_valid']]
                scenes.append({'path':scene['path'],'threads':scene['threads'],'metric':metric,'total_ratio_rows':len(subset),'valid_ratio_rows':len(qualified),'all_AA_valid':len(qualified)==len(subset),'median_time_ratio_all':median([row['time_ratio'] for row in subset]),'minimum_valid_throughput':min((row['throughput_retention'] for row in qualified),default=None)})
        summaries[name]={'total_ratio_rows':len(selected),'valid_ratio_rows':len(valid),'all_AA_valid':all_valid,'minimum_valid_throughput':worst,'worst_valid_row':min(valid,key=lambda row:row['throughput_retention']) if valid else None,'tiers':{str(tier):bool(all_valid and worst is not None and worst>=Decimal(tier)/100) for tier in plan['tiers']},'no_obvious_degradation':bool(all_valid and worst is not None and worst>=1/Decimal('1.10')),'rejected_by_valid_below50':bool(worst is not None and worst<Decimal('.5')),'scenes':scenes}
    gates={}
    for candidate in ('291max','291p99','291max48'):
        required=[summaries[candidate+'/'+base] for base in plan['required_denominators']]
        gates[candidate]={'all_required_AA_valid':all(row['all_AA_valid'] for row in required),'tiers':{str(tier):all(row['tiers'][str(tier)] for row in required) for tier in plan['tiers']},'rejected_by_any_valid_required_below50':any(row['rejected_by_valid_below50'] for row in required),'scope':'仅该固定100图AVX2稳态四模式；冷首无AA不授该范围档，未测所有合成输入最差速度'}
    rss=[]
    for role in plan['roles']:
        path=OUT/'rss'/f'{role}.json';row=read(path);assert row['role']==role and row['plan_sha256']==sha(PLAN) and row['pixels_allocated']==0
        assert row['state']['model_bytes']>0;raw_identity[str(path.relative_to(OUT))]=sha(path);rss.append(row)
    for name,wanted in plan['sources_sha256'].items():
        assert sha(ROOT/name)==wanted, name
    for library in plan['libraries'].values():assert sha(library['path'])==library['sha256']
    result={'passed':True,'purpose':'格式/原SHA与独立Decimal复算通过，不等于候选速度全部达标','decimal_precision':50,'plan_sha256':sha(PLAN),'raw_sha256':raw_identity,'actual_native_output_sha_checks':native_sha,'native_apply_calls_by_frozen_loop_counts':3364,'pair_source_sha_checks':pair_checks,'AA':aa,'comparisons':rows,'pairs':summaries,'candidate_gates':gates,'cold':cold,'rss':rss,'cold_has_AA':False,'no_timing_rerun':True}
    target.write_text(json.dumps(serial(result),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(serial({'passed':True,'actual_native_output_sha_checks':native_sha,'AA_passed':sum(row['pass'] for row in aa),'AA_total':len(aa),'candidate_gates':gates}),ensure_ascii=False))

if __name__=='__main__':
    with localcontext() as context:
        context.prec=50;main()
