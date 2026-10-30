"""独立Decimal复算P4六角色656调用和6RSS；invalid与有效低50分开。"""
import argparse
from decimal import Decimal,localcontext
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'experiments/page-id16-performance-v1.json'
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def median(values):
    values=sorted(Decimal(value) for value in values);n=len(values)
    return values[n//2] if n%2 else (values[n//2-1]+values[n//2])/2
def tier(value):return next((x for x in (100,90,80,70,60,50) if value>=Decimal(x)/100),None)
def compute(directory,plan):
    with localcontext() as context:
        context.prec=60;workers=[];aa={};measured={};total=0
        for index in range(4):
            value=read(directory/('worker'+str(index))/'results.json');roles=plan['roles'];order=roles[index%len(roles):]+roles[:index%len(roles)]
            if index%2:order=list(reversed(order))
            threads=[1,4] if index%2==0 else [4,1];modes=['in','out'] if index%2==0 else ['out','in'];expected=[]
            for t in threads:
                for mode in modes:
                    expected.append(('ref80',t,mode,'aa_warm',0));expected.extend(('ref80',t,mode,'aa_before',r) for r in range(2))
                    for role in order:
                        expected.append((role,t,mode,'role_warm',0));expected.extend((role,t,mode,'measured',r) for r in range(5))
                    expected.extend(('ref80',t,mode,'aa_after',r) for r in range(2))
            rows=value['rows']
            if not value['passed'] or value['worker']!=index or value['roles']!=roles or value['order']!=order or value['thread_order']!=threads or value['mode_order']!=modes or value['affinity']['allowed']!=85 or len(rows)!=164 or [(r['role'],r['threads'],r['mode'],r['kind'],r['round']) for r in rows]!=expected:raise AssertionError('预定镜像顺序/数量/控制环境不同')
            for role in roles:
                identity=value['identities'][role]
                if identity['capacity']!=plan['capacities'][role] or identity['library_sha256']!=plan['input_sha256'][plan['libraries'][role if role in ('ref78','ref80') else 'linear' if role.startswith('linear') else 'p4']]:raise AssertionError('实际角色身份/容量不同')
            for sequence,row in enumerate(rows):
                if row['sequence']!=sequence or row['wall_ns']<=0 or row['returncode'] or row['sha256']!=plan['expected_output_sha256'] or row['cpu_before'] not in (0,2,4,6) or row['cpu_after'] not in (0,2,4,6) or row['target_address']!=value['target_address'] or row['source_address']!=(value['target_address'] if row['mode']=='in' else value['original_source_address']):raise AssertionError('原始调用SHA/ns/CPU/同址不同')
            worker_aa=[]
            for t in (1,4):
                for mode in ('in','out'):
                    selected=[row for row in rows if row['threads']==t and row['mode']==mode];before=median([row['wall_ns'] for row in selected if row['kind']=='aa_before']);after=median([row['wall_ns'] for row in selected if row['kind']=='aa_after']);ratio=after/before;valid=Decimal('0.8')<=ratio<=Decimal('1.25');aa[index,t,mode]=valid
                    worker_aa.append(dict(threads=t,mode=mode,before_ns=str(before),after_ns=str(after),ratio=str(ratio),valid=valid))
                    for role in roles:
                        samples=[row['wall_ns'] for row in selected if row['kind']=='measured' and row['role']==role]
                        if len(samples)!=5:raise AssertionError('必须五个原始计时')
                        measured[index,t,mode,role]=median(samples)
            workers.append(dict(worker=index,aa=worker_aa,calls=len(rows)));total+=len(rows)
        cases=[];global_rows=[]
        for role in plan['roles']:
            this=[]
            for t in (1,4):
                for mode in ('in','out'):
                    values=[];aux=[];medians=[];valid=all(aa[index,t,mode] for index in range(4))
                    for index in range(4):
                        base=min(measured[index,t,mode,'ref78'],measured[index,t,mode,'ref80']);candidate=measured[index,t,mode,role];values.append(base/candidate);medians.append(dict(worker=index,baseline_fastest_ns=str(base),candidate_ns=str(candidate),retention=str(base/candidate)))
                        if role in ('p4_avx','p4_c99'):aux.append(measured[index,t,mode,'linear_avx' if role=='p4_avx' else 'linear_c99']/candidate)
                    worst=min(values);status='invalid-aa' if not valid else 'rejected-below-50' if worst<Decimal('0.5') else 'qualified-mode';row=dict(role=role,threads=t,mode=mode,all_workers_aa_valid=valid,worst_retention=str(worst),worst_percent=str(worst*100),tier=tier(worst) if valid else None,status=status,workers=medians)
                    if aux:row['auxiliary_vs_linear_worst_retention']=str(min(aux));row['auxiliary_scope']='同场同kernel原linear耗时/P4，辅助不是主速度分母；沿相同AA失效门。'
                    cases.append(row);this.append(row)
            valid_negative=any(row['all_workers_aa_valid'] and Decimal(row['worst_retention'])<Decimal('0.5') for row in this);all_valid=all(row['all_workers_aa_valid'] for row in this);worst=min(Decimal(row['worst_retention']) for row in this)
            global_rows.append(dict(role=role,all_four_modes_valid=all_valid,worst_raw_retention=str(worst),tier=tier(worst) if all_valid else None,status='valid-negative-below-50' if valid_negative else 'unproven-invalid-mode' if not all_valid else 'qualified-global',precision_retention='1',precision_tier=100,precision_scope='同a399完整输出位等价，非数学误差为0；计时invalid不改质量事实。'))
        rss=[]
        for role in plan['roles']:
            value=read(directory/('rss-'+role)/'rss.json')
            if value['role']!=role or value['identity']['capacity']!=plan['capacities'][role] or value['affinity']['allowed']!=85:raise AssertionError('独立RSS角色/实际容量/环境不同')
            rss.append(value)
        if total!=656:raise AssertionError('必须保留656调用')
        return dict(audit_passed=True,precision_retention='1',precision_tier=100,total_calls=total,rss_processes=6,workers=workers,cases=cases,global_roles=global_rows,rss=rss,scope='60位Decimal从全部整数ns独立复算；六档以最劣判定，AA无效清档；不跨场相乘/拼绝对ms或恢复旧3B，辅助linear不作主分母。')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();result=compute(a.input,read(PLAN));a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(dict(audit_passed=True,total_calls=result['total_calls'],global_roles=result['global_roles']))
if __name__=='__main__':main()
