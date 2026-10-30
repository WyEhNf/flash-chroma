"""293/294 V2独立Fraction/Decimal静态审计草稿；不加载DLL或图像。"""
import argparse
from decimal import Decimal,getcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path

def read(path):return json.loads(path.read_text(encoding='utf-8'),parse_float=Decimal)
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def median(values):
    values=sorted(values);count=len(values)
    return values[count//2] if count%2 else (values[count//2-1]+values[count//2])/2
def fraction(value):return Fraction(value)
def pack(value):return [value.numerator,value.denominator]

def check_representation(plan,role,value,reference=None):
    # 独立实现稳定投影，不导入driver/support；allocator模64及计时不进入身份。
    projected={}
    for section,row in value.items():
        projected[section]={k:v for k,v in row.items() if k!='prepare_seconds' and k!='data_mod_64'} if isinstance(row,dict) else row
    assert projected==plan['expected_states'][role]
    if reference is not None:
        prior={section:({k:v for k,v in row.items() if k not in ('prepare_seconds','data_mod_64')}
            if isinstance(row,dict) else row) for section,row in reference.items()}
        assert projected==prior
    assert value['cache']['enabled']==value['domain']['cache_enabled']==value['domain']['eligible']==value['direct']['enabled']==1
    assert value['domain']['unproven_cells']==0 and value['domain']['reachable_cells']==32768 and value['domain']['fast_path_enabled']==1
    if role.endswith('max41'):
        wide=value['wide'];u16=role=='293-max41'
        assert value['palette']['enabled']==0 and value['palette']['palette_size']==613
        assert wide['enabled']==1 and wide['format']==value['direct']['format']==(16 if u16 else 18)
        assert wide['guard_bytes']==4 and wide['id_bytes']==(2 if u16 else 3) and wide['input_entries']==16777216
        assert wide['palette_size']==(613 if u16 else 0) and wide['palette_capacity_bytes']==(2452 if u16 else 0)
        assert wide['table_capacity_bytes']==value['direct']['table_capacity_bytes']==(33554436 if u16 else 50331652)
        assert wide['raw_words']==value['direct']['entries']==(8388609 if u16 else 12582913)
    else:
        assert value['palette']['enabled']==1 and value['palette']['palette_size']==(230 if role=='87-a399' else 234)
        assert value['direct']['format']==9 and value['direct']['entries']==4194304 and value['direct']['table_capacity_bytes']==16777216
        if value['wide'] is not None:
            assert value['wide']['enabled']==0 and value['wide']['reason']==1
            assert value['wide']['table_capacity_bytes']==value['wide']['palette_capacity_bytes']==0
    if value['wide'] is not None:
        wide=value['wide'];assert 0<=wide['data_mod_64']<64 and wide['data_mod_64']%wide['guaranteed_alignment']==0

def check_modules(plan,states):
    for label,groups in states.items():
        assert set(groups)==set(plan['gcc_dependencies'])
        for name,rows in groups.items():
            assert len(rows) in ((0,1) if label=='before_native' else (1,))
            expected=plan['gcc_dependencies'][name]
            for row in rows:
                assert Path(row['path']).resolve()==Path(expected['path']).resolve() and row['sha256']==expected['sha256'] and row['base']>0

def check_pool(profile,pool,expected_calls):
    assert pool['healthy'] and len(set(pool['tids']))==4 and len(pool['snapshots'])==expected_calls
    actions=[row['action'] for row in pool['snapshots']]
    if profile=='U':assert all(action==0 for action in actions)
    else:assert actions.count(1)==actions.count(2)==1
    for snapshot in pool['snapshots']:
        assert snapshot['return_code']==0 and [v['os_tid'] for v in snapshot['members']]==pool['tids']
        for t,row in enumerate(snapshot['members']):
            assert row['version']==1 and row['omp_tid']==t and row['team_size']==4
            assert row['query_before_ok'] and row['query_after_ok'] and row['group_before']==row['group_after']==0
            wanted=1<<(2*t) if snapshot['policy']=='P' else 0x55
            assert row['mask_after']==wanted and row['cpu_after'] in (0,2,4,6)
            if snapshot['action']==0:
                assert not row['set_attempted'] and row['mask_before']==wanted
                if snapshot['policy']=='P':assert row['cpu_before']==row['cpu_after']==2*t
            elif snapshot['action']==1:
                assert row['set_attempted'] and row['previous_mask']==0x55 and not row['set_error'] and row['cpu_after']==2*t
            else:
                assert row['set_attempted'] and row['mask_before']==1<<(2*t) and row['previous_mask']==1<<(2*t) and not row['set_error']
    if profile=='P':assert pool['snapshots'][-2]['action']==2 and pool['snapshots'][-1]['policy']=='U'

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source',type=Path);args=parser.parse_args()
    getcontext().prec=50;folder=args.source;plan=read(folder/'executed-plan.json');overall=read(folder/'results.json');float_stats=read(folder/'statistics.json')
    output=folder/'fraction-audit.json'
    if output.exists():raise FileExistsError('V2独立原始审计不覆盖')
    assert overall['passed'] and overall['sha_checks']==2688 and overall['image_apply_calls']==5568 and overall['rss_processes']==12
    # 独立从原始组建立索引，不导入driver的summary函数。
    float_hot={(v['profile'],v['worker'],v['pair'],tuple(v['mode'])):v for v in float_stats['hot']}
    float_cold={(v['profile'],v['worker'],v['images'],v['pair'],v['metric']):v for v in float_stats['cold']}
    assert len(float_hot)==len(float_stats['hot'])==288 and len(float_cold)==len(float_stats['cold'])==288
    hot=[];cold=[];checks=0;apply_calls=0;errors=[];rss_rows=[]
    def compare(raw,expected):
        value=Decimal(expected.numerator)/Decimal(expected.denominator)
        error=abs(Decimal(raw)-value);assert error<Decimal('1e-13'),(str(raw),str(value));errors.append(error)
    for profile in ('U','P'):
        for number in range(4):
            path=folder/f'{profile}-worker{number}.json';worker=read(path)
            assert overall['worker_sha256'][f'{profile}-{number}']==digest(path)
            assert worker['passed'] and worker['profile']==profile and worker['worker']==number
            assert worker['counters']==plan['per_worker_expected'] and worker['source_sha256']==plan['source_sha256']
            assert worker['successful_creates']==126 and len(worker['hot'])==36 and len(worker['cold'])==120
            assert len(set(worker['addresses'].values()))==3
            assert worker['environment']['python']==plan['expected_python'] and worker['environment']['numpy']==plan['expected_numpy']
            assert worker['environment']['thread_environment']==plan['required_environment']
            assert set(worker['hot_states'])==set(plan['role_names'])
            for role,value in worker['hot_states'].items():check_representation(plan,role,value)
            check_modules(plan,worker['module_states']);check_pool(profile,worker['pool'],676 if profile=='U' else 680)
            assert worker['helper_calls']==len(worker['pool']['snapshots'])
            def endpoint(group):
                before,after=group['before_pool'],group['after_pool'];assert after==before+1
                for index in (before,after):assert worker['pool']['snapshots'][index]['policy']==profile and worker['pool']['snapshots'][index]['action']==0
            expected_cells={(pair,tuple(mode)) for pair in plan['pair_orders'][number] for mode in plan['mode_orders'][number]}
            assert {(c['pair'],tuple(c['mode'])) for c in worker['hot']}==expected_cells
            for cell in worker['hot']:
                pair=plan['pairs'][cell['pair']];roles=(pair['candidate'],pair['denominator'])
                assert len(cell['warm'])==2 and {g['role'] for g in cell['warm']}==set(roles) and len(cell['groups'])==4
                assert [g['role'] for g in cell['groups']]==[roles[0] if token=='A' else roles[1] for token in plan['palindromes'][number]]
                for warm,groups in ((True,cell['warm']),(False,cell['groups'])):
                    for group in groups:
                        repeats=2 if warm else 3;assert group['repeats']==repeats and len(group['apply_seconds'])==repeats
                        assert all(t>0 for t in group['apply_seconds']);endpoint(group)
                        model=plan['roles'][group['role']]['model'];assert group['actual_output_sha256']==plan['expected'][model]['100']
                        if cell['mode'][0]=='inplace':
                            assert len(group['copy_apply_seconds'])==repeats and all(a>=b for a,b in zip(group['copy_apply_seconds'],group['apply_seconds']))
                        checks+=1;apply_calls+=repeats
                metrics=('apply_seconds','copy_apply_seconds') if cell['mode'][0]=='inplace' else ('apply_seconds',)
                indexed={(r['role'],r['phase']):r for r in cell['groups']};aa={};ratios={}
                for role in roles:
                    for metric in metrics:aa[f'{role}/{metric}']=median([fraction(x) for x in indexed[role,2][metric]])/median([fraction(x) for x in indexed[role,1][metric]])
                valid=all(Fraction(85,100)<=v<=Fraction(115,100) for v in aa.values())
                for metric in metrics:
                    ratios[metric]=[median([fraction(x) for x in indexed[roles[1],p][metric]])/median([fraction(x) for x in indexed[roles[0],p][metric]]) for p in (1,2)]
                worst=min(v for values in ratios.values() for v in values);tiers={str(g):valid and worst>=Fraction(g,100) for g in plan['tiers']}
                actual=float_hot[profile,number,cell['pair'],tuple(cell['mode'])]
                assert actual['control_valid']==valid and actual['tiers']==tiers
                for k,v in aa.items():compare(actual['aa'][k],v)
                for k,values in ratios.items():
                    for a,v in zip(actual['retained_by_phase'][k],values):compare(a,v)
                compare(actual['worst_retained'],worst)
                hot.append({'profile':profile,'worker':number,'pair':cell['pair'],'main':pair['main'],'candidate':pair['candidate'],
                    'mode':cell['mode'],'valid':valid,'aa':{k:pack(v) for k,v in aa.items()},'retained_by_phase':{k:[pack(v) for v in values] for k,values in ratios.items()},
                    'worst':pack(worst),'valid_below50':valid and worst<Fraction(1,2),'tiers':tiers})
            expected_cold={(role,n,p,r) for role in plan['role_names'] for n in (1,100) for p in (1,2) for r in range(5)}
            assert {(r['role'],r['images'],r['phase'],r['repeat']) for r in worker['cold']}==expected_cold
            for row in worker['cold']:
                assert row['destroyed_before_next'] and 0<row['create_ns']<row['wall_ns'] and 0<row['first_apply_seconds']*1000000000<row['wall_ns']
                model=plan['roles'][row['role']]['model'];assert row['actual_output_sha256']==plan['expected'][model][str(row['images'])]
                check_representation(plan,row['role'],row['state'],worker['hot_states'][row['role']])
                endpoint(row);checks+=1;apply_calls+=1
            for n in (1,100):
                for pair in [p for p in plan['pairs'] if p['main']]:
                    roles=(pair['candidate'],pair['denominator'])
                    for metric in ('create_ns','first_apply_seconds','wall_ns'):
                        med={(role,p):median([fraction(r[metric]) for r in worker['cold'] if r['role']==role and r['images']==n and r['phase']==p]) for role in roles for p in (1,2)}
                        aa={r:med[r,2]/med[r,1] for r in roles};valid=all(Fraction(85,100)<=v<=Fraction(115,100) for v in aa.values())
                        retained=[med[roles[1],p]/med[roles[0],p] for p in (1,2)];worst=min(retained);tiers={str(g):valid and worst>=Fraction(g,100) for g in plan['tiers']}
                        actual=float_cold[profile,number,n,pair['id'],metric];assert actual['control_valid']==valid and actual['tiers']==tiers
                        for role,value in aa.items():compare(actual['aa'][role],value)
                        for a,v in zip(actual['retained_by_phase'],retained):compare(a,v)
                        compare(actual['worst_retained'],worst)
                        cold.append({'profile':profile,'worker':number,'images':n,'pair':pair['id'],'candidate':pair['candidate'],'metric':metric,
                            'valid':valid,'worst':pack(worst),'retained_by_phase':[pack(v) for v in retained],
                            'aa':{k:pack(v) for k,v in aa.items()},'valid_below50':valid and worst<Fraction(1,2),'tiers':tiers})
        for role in plan['role_names']:
            row=read(folder/f'{profile}-rss-{role}.json');assert row['passed'] and row['successful_creates']==1 and not row['images_loaded'] and row['image_apply_calls']==0
            assert row['python']==plan['expected_python'] and row['numpy']==plan['expected_numpy']
            check_representation(plan,role,row['state'])
            check_modules(plan,row['module_states']);check_pool(profile,row['pool'],5 if profile=='U' else 9)
            for snapshot in ('before','after','after_close'):
                value=row[snapshot];assert value['WorkingSetSize']>0 and value['PrivateUsage']>=0 and value['PeakWorkingSetSize']>=value['WorkingSetSize']
            rss_rows.append({'profile':profile,'role':role,'before':row['before'],'after':row['after'],'after_close':row['after_close'],'model_bytes':row['state']['model_bytes']})
    assert checks==2688 and apply_calls==5568 and len(hot)==288 and len(cold)==288 and len(rss_rows)==12
    verdicts=[]
    for profile in ('U','P'):
        for candidate in ('293-max41','294-max41'):
            selections={'hot':[r for r in hot if r['profile']==profile and r['candidate']==candidate and r['main']]}
            for n in (1,100):selections[f'cold{n}_wall']=[r for r in cold if r['profile']==profile and r['candidate']==candidate and r['images']==n and r['metric']=='wall_ns']
            gates={}
            for scope,rows in selections.items():
                gates[scope]={'required_cells':len(rows),'aa_invalid':sum(not r['valid'] for r in rows),'valid_below50':sum(r['valid_below50'] for r in rows),
                    'tiers':{str(g):all(r['tiers'][str(g)] for r in rows) for g in plan['tiers']}}
            verdicts.append({'profile':profile,'candidate':candidate,'scopes':gates,
                'all_scope_tiers':{str(g):all(v['tiers'][str(g)] for v in gates.values()) for g in plan['tiers']}})
    save={'passed':True,'plan_sha256':digest(folder/'executed-plan.json'),'actual_sha_checks':checks,'actual_image_apply_calls':apply_calls,
        'rss_processes':12,'hot_cells':len(hot),'cold_metric_sets':len(cold),'hot':hot,'cold':cold,'verdicts':verdicts,'rss':rss_rows,
        'float_scalar_checks':len(errors),'max_float_absolute_difference':str(max(errors)),'fraction_exact':True,'decimal_digits':50,
        'scope':'U主/P辅独立授档，P/局部正例不能恢复U或N1；所有AA失败和有效低50保留，冷只用连续wall主门。'}
    output.write_text(json.dumps(save,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':True,'sha_checks':checks,'image_apply_calls':apply_calls,'verdicts':verdicts},ensure_ascii=False))

if __name__=='__main__':main()
