"""独立60位Decimal核1232调用、六角色双阶段控制及6RSS，任何cell失效全部清档。"""
import argparse
from decimal import Decimal,localcontext
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'experiments/page-id16-performance-v2.json'

def read(path):return json.loads(path.read_text(encoding='utf-8'))

def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def median(values):
    ordered=sorted(Decimal(value) for value in values)
    n=len(ordered)
    return ordered[n//2] if n%2 else (ordered[n//2-1]+ordered[n//2])/2

def tier(value):return next((threshold for threshold in (100,90,80,70,60,50) if value>=Decimal(threshold)/100),None)

def valid_ratio(value):return Decimal('0.8')<=value<=Decimal('1.25')

def check_identity(value,role,plan):
    identity=value['identities'][role] if 'identities' in value else value['identity']
    library_key=role if role in ('ref78','ref80') else 'linear' if role.startswith('linear') else 'p4'
    if identity['role']!=role or identity['capacity']!=plan['capacities'][role] or identity['library']!=plan['libraries'][library_key] or identity['library_sha256']!=plan['input_sha256'][plan['libraries'][library_key]]:raise AssertionError('角色实际DLL/容量不同')
    if role.startswith('linear') and (identity['model_bytes']!=1056 or identity['rom_sha256']!=plan['input_sha256'][plan['original_rom']]):raise AssertionError('linear实际ROM/ABI不同')
    if role.startswith('p4') and (identity['model_bytes']!=40 or identity['rom_sha256']!=plan['input_sha256'][plan['page_rom']]):raise AssertionError('P4实际ROM/ABI不同')

def compute(directory,plan):
    with localcontext() as context:
        context.prec=60
        workers=[]
        cell_valid={}
        measured={}
        total=0
        plan_digest=sha(PLAN)
        for index in range(4):
            value=read(directory/('worker'+str(index))/'results.json')
            roles=plan['roles']
            order=roles[index%len(roles):]+roles[:index%len(roles)]
            if index%2:order=list(reversed(order))
            orders={'1':order,'2':list(reversed(order))}
            threads=[1,4] if index%2==0 else [4,1]
            modes=['in','out'] if index%2==0 else ['out','in']
            expected=[]
            for thread_count in threads:
                for mode in modes:
                    expected.append(('ref80',thread_count,mode,'aa_warm',0,0))
                    expected.extend(('ref80',thread_count,mode,'aa_before',0,round_index) for round_index in range(2))
                    for phase in (1,2):
                        for role in orders[str(phase)]:
                            expected.append((role,thread_count,mode,'role_warm',phase,0))
                            expected.extend((role,thread_count,mode,'measured',phase,round_index) for round_index in range(5))
                    expected.extend(('ref80',thread_count,mode,'aa_after',0,round_index) for round_index in range(2))
            rows=value['rows']
            if not value['passed'] or value['plan_sha256']!=plan_digest or value['worker']!=index or value['roles']!=roles or value['phase_orders']!=orders or value['thread_order']!=threads or value['mode_order']!=modes or value['affinity']['allowed']!=85 or value['affinity']['allowed_logical_cpus']!=[0,2,4,6] or len(rows)!=308 or [(row['role'],row['threads'],row['mode'],row['kind'],row['phase'],row['round']) for row in rows]!=expected:raise AssertionError('预定双阶段镜像顺序/调用数/允许集/计划不同')
            for role in roles:check_identity(value,role,plan)
            for sequence,row in enumerate(rows):
                if row['sequence']!=sequence or type(row['wall_ns']) is not int or row['wall_ns']<=0 or row['returncode'] or row['sha256']!=plan['expected_output_sha256'] or row['cpu_before'] not in (0,2,4,6) or row['cpu_after'] not in (0,2,4,6) or row['target_address']!=value['target_address'] or row['source_address']!=(value['target_address'] if row['mode']=='in' else value['original_source_address']):raise AssertionError('原始调用整数ns/SHA/CPU/同址不同')
            worker_cells=[]
            for thread_count in (1,4):
                for mode in ('in','out'):
                    selected=[row for row in rows if row['threads']==thread_count and row['mode']==mode]
                    before=[row['wall_ns'] for row in selected if row['kind']=='aa_before']
                    after=[row['wall_ns'] for row in selected if row['kind']=='aa_after']
                    if len(before)!=2 or len(after)!=2 or len(selected)!=77:raise AssertionError('外围控制/每cell调用数不同')
                    before_ns=median(before)
                    after_ns=median(after)
                    external_ratio=after_ns/before_ns
                    own=[]
                    for role in roles:
                        for phase in (1,2):
                            samples=[row['wall_ns'] for row in selected if row['kind']=='measured' and row['role']==role and row['phase']==phase]
                            if len(samples)!=5:raise AssertionError('每角色每阶段必须五个原始计时')
                            measured[index,thread_count,mode,role,phase]=median(samples)
                        phase1=measured[index,thread_count,mode,role,1]
                        phase2=measured[index,thread_count,mode,role,2]
                        ratio=phase2/phase1
                        own.append(dict(role=role,phase1_median_ns=str(phase1),phase2_median_ns=str(phase2),phase2_over_phase1=str(ratio),valid=valid_ratio(ratio)))
                    valid=valid_ratio(external_ratio) and all(row['valid'] for row in own)
                    cell_valid[index,thread_count,mode]=valid
                    worker_cells.append(dict(threads=thread_count,mode=mode,all_controls_valid=valid,external=dict(before_mean_ns=str(before_ns),after_mean_ns=str(after_ns),after_over_before=str(external_ratio),valid=valid_ratio(external_ratio)),roles=own))
            workers.append(dict(worker=index,cells=worker_cells,calls=len(rows),cpu_changes=sum(row['cpu_before']!=row['cpu_after'] for row in rows)))
            total+=len(rows)
        cases=[]
        global_rows=[]
        for role in plan['roles']:
            role_cases=[]
            for thread_count in (1,4):
                for mode in ('in','out'):
                    all_valid=all(cell_valid[index,thread_count,mode] for index in range(4))
                    phase_rows=[]
                    for index in range(4):
                        for phase in (1,2):
                            base=min(measured[index,thread_count,mode,'ref78',phase],measured[index,thread_count,mode,'ref80',phase])
                            candidate=measured[index,thread_count,mode,role,phase]
                            row=dict(worker=index,phase=phase,baseline_fastest_ns=str(base),candidate_ns=str(candidate),retention=str(base/candidate),cell_controls_valid=cell_valid[index,thread_count,mode])
                            if role in ('p4_avx','p4_c99'):
                                linear=measured[index,thread_count,mode,'linear_avx' if role=='p4_avx' else 'linear_c99',phase]
                                row['auxiliary_linear_ns']=str(linear)
                                row['auxiliary_vs_linear_retention']=str(linear/candidate)
                            phase_rows.append(row)
                    worst=min(Decimal(row['retention']) for row in phase_rows)
                    case=dict(role=role,threads=thread_count,mode=mode,all_workers_controls_valid=all_valid,worst_raw_retention=str(worst),worst_raw_percent=str(worst*100),tier=tier(worst) if all_valid else None,status='invalid-controls' if not all_valid else 'rejected-below-50' if worst<Decimal('0.5') else 'qualified-mode',phases=phase_rows)
                    if role in ('p4_avx','p4_c99'):
                        case['auxiliary_vs_linear_worst_raw_retention']=str(min(Decimal(row['auxiliary_vs_linear_retention']) for row in phase_rows))
                        case['auxiliary_scope']='同worker/同phase/同kernel linear耗时/P4；沿全部cell控制门，仅辅助不作主分母。'
                    cases.append(case)
                    role_cases.append(case)
            valid_negative=any(row['all_workers_controls_valid'] and Decimal(row['worst_raw_retention'])<Decimal('0.5') for row in role_cases)
            all_valid=all(row['all_workers_controls_valid'] for row in role_cases)
            worst=min(Decimal(row['worst_raw_retention']) for row in role_cases)
            global_rows.append(dict(role=role,all_four_modes_valid=all_valid,worst_raw_retention=str(worst),tier=tier(worst) if all_valid else None,status='valid-negative-below-50' if valid_negative else 'unproven-invalid-mode' if not all_valid else 'qualified-global',precision_retention='1',precision_tier=100,precision_scope='同a399完整输出位等价，非数学误差为0；计时控制失效不改质量事实。'))
        rss=[]
        for role in plan['roles']:
            value=read(directory/('rss-'+role)/'rss.json')
            if value['role']!=role or value['plan_sha256']!=plan_digest or value['affinity']['allowed']!=85:raise AssertionError('RSS角色/计划/允许集不同')
            check_identity(value,role,plan)
            rss.append(value)
        driver=read(directory/'driver.json')
        expected_jobs=['worker'+str(index) for index in range(4)]+['rss-'+role for role in plan['roles']]
        if not driver['passed'] or driver['plan_sha256']!=plan_digest or [row['label'] for row in driver['jobs']]!=expected_jobs or any(row['returncode'] for row in driver['jobs']):raise AssertionError('唯一driver进程集合/状态不同')
        if total!=1232:raise AssertionError('必须保留1232调用')
        return dict(audit_passed=True,plan_sha256=plan_digest,precision_retention='1',precision_tier=100,total_calls=total,measured_calls=960,rss_processes=6,workers=workers,cases=cases,global_roles=global_rows,rss=rss,scope='60位Decimal从全部整数ns独立复算；每角色两阶段控制及外围ref80任一失效则该cell六角色全清档；每phase最快78/80主分母，取全部phase/worker最劣，不合并十样本救线。')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=compute(args.input,read(PLAN))
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(dict(audit_passed=True,total_calls=result['total_calls'],global_roles=result['global_roles']))

if __name__=='__main__':main()
