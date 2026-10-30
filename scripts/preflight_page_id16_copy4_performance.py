"""只用明确标注的模拟整数记录预检冻结审计/阶段门；绝不调用native或计时。"""
import argparse
import ast
import hashlib
from pathlib import Path
from copy import deepcopy
import audit_page_id16_copy4_performance as audit
from study_memory_rom import ROOT,read,save,sha
PLAN=ROOT/'experiments/page-id16-copy4-performance-v1.json'
DEPENDENCIES=('libgcc_s_seh-1.dll','libgomp-1.dll','libstdc++-6.dll','libwinpthread-1.dll')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    plan=read(PLAN)
    if any(sha(ROOT/name)!=value for name,value in plan['source_sha256'].items()) or any(sha(name)!=value for name,value in plan['input_sha256'].items()):raise AssertionError('预检源/输入不同')
    if (len(plan['roles']),plan['calls_per_cell'],plan['calls_per_worker'],plan['calls'],plan['measured_calls'],plan['rss_processes'])!=(5,65,260,1040,800,5):raise AssertionError('冻结计数不同')
    tree=ast.parse((ROOT/'scripts/bench_page_id16_copy4.py').read_text(encoding='utf-8'))
    calls=[node for node in ast.walk(tree) if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='jshc_p4_apply_copy4_parallel']
    if len(calls)!=1 or len(calls[0].args)!=6 or not isinstance(calls[0].args[4],ast.Constant) or calls[0].args[4].value!=0:raise AssertionError('新计时源码未明确新parallel/kernel0')
    digest=sha(PLAN)
    def identity(role):
        key=role if role.startswith('ref') else 'linear' if role=='linear_c99' else 'copy4' if role=='p4_copy4' else 'p4'
        value=dict(role=role,capacity=plan['capacities'][role],library=plan['libraries'][key],library_sha256=plan['input_sha256'][plan['libraries'][key]])
        if role=='linear_c99':value.update(model_bytes=1056,rom_sha256=plan['input_sha256'][plan['original_rom']])
        if role.startswith('p4'):value.update(model_bytes=40,rom_sha256=plan['input_sha256'][plan['page_rom']])
        if role=='p4_copy4':value['entrypoint_receipt']=dict(new_apply_symbol='jshc_p4_apply_copy4',parallel_symbol='jshc_p4_apply_copy4_parallel',old_apply_address=1,new_apply_address=2,selected_kernel=0,scope='纯模拟地址，未加载native')
        return value
    def observations(worker):
        labels=['same-imports-before-setup','after-all-prepare','after-all-close'] if worker else ['same-imports-before-setup','after-prepare','after-close']
        values=[]
        for index,label in enumerate(labels):
            dependencies={}
            for name in DEPENDENCIES:
                path=str(Path(plan['libraries']['ref78']).parent/name)
                dependencies[name]=[] if index==0 else [dict(path=path,sha256=plan['input_sha256'][path],scope='模拟模块元数据，非实际枚举')]
            values.append(dict(label=label,dependencies=dependencies,dependency_counts={name:len(rows) for name,rows in dependencies.items()},synthetic=True))
        return values
    def worker(index,profile):
        roles=plan['roles']
        order=[roles[(index+offset)%len(roles)] for offset in range(len(roles))]
        if index%2:order.reverse()
        threads=[4,1] if index%2 else [1,4]
        modes=['out','in'] if index%2 else ['in','out']
        rows=[]
        medians=dict(ref78=1000000,ref80=1100000,linear_c99=1600000,p4_c99=2500000,p4_copy4=2000000)
        def append(role,thread_count,mode,kind,phase,round_index):
            duration=medians[role]
            if kind=='measured':
                if profile=='own-drift' and index==0 and thread_count==1 and mode=='in' and role=='p4_copy4' and phase==2:duration=2500001
                if profile=='worst-phase' and index==0 and thread_count==1 and mode=='out' and role=='p4_copy4':duration=1900000 if phase==1 else 2100000
                duration+=round_index-2
            if profile=='external-upper-edge' and kind=='aa_after':duration=1375000
            rows.append(dict(sequence=len(rows),role=role,threads=thread_count,mode=mode,kind=kind,phase=phase,round=round_index,wall_ns=duration,returncode=0,sha256=plan['expected_output_sha256'],cpu_before=0,cpu_after=2,source_address=2000 if mode=='in' else 1000,target_address=2000,synthetic=True))
        for thread_count in threads:
            for mode in modes:
                append('ref80',thread_count,mode,'aa_warm',0,0)
                for round_index in range(2):append('ref80',thread_count,mode,'aa_before',0,round_index)
                for phase,phase_order in ((1,order),(2,list(reversed(order)))):
                    for role in phase_order:
                        append(role,thread_count,mode,'role_warm',phase,0)
                        for round_index in range(5):append(role,thread_count,mode,'measured',phase,round_index)
                for round_index in range(2):append('ref80',thread_count,mode,'aa_after',0,round_index)
        return dict(worker=index,passed=True,plan_sha256=digest,roles=roles,phase_orders={'1':order,'2':list(reversed(order))},thread_order=threads,mode_order=modes,affinity=dict(allowed=85,allowed_logical_cpus=[0,2,4,6]),identities={role:identity(role) for role in roles},original_source_address=1000,target_address=2000,rows=rows,module_observations=observations(True),synthetic=True,scope='纯模拟协议记录，不是测量结果')
    reports=[]
    for profile in ('exact-50','external-upper-edge','own-drift','worst-phase'):
        directory=args.output/profile
        directory.mkdir()
        for index in range(4):
            target=directory/('worker'+str(index))
            target.mkdir()
            save(target/'results.json',worker(index,profile))
        for role in plan['roles']:
            target=directory/('rss-'+role)
            target.mkdir()
            save(target/'rss.json',dict(role=role,plan_sha256=digest,identity=identity(role),affinity=dict(allowed=85),module_observations=observations(False),synthetic=True,scope='模拟RSS身份记录，没有实测内存值'))
        save(directory/'driver.json',dict(passed=True,plan_sha256=digest,jobs=[dict(label=label,returncode=0,synthetic=True) for label in ['worker'+str(index) for index in range(4)]+['rss-'+role for role in plan['roles']]],synthetic=True))
        result=audit.compute(directory,plan)
        selected=[row for row in result['global_roles'] if row['role']=='p4_copy4'][0]
        if profile in ('exact-50','external-upper-edge'):
            if selected['tier']!=50 or not selected['all_four_modes_valid']:raise AssertionError('精确50/闭区间1.25应通过')
        elif profile=='own-drift':
            cell=[row for row in result['cases'] if row['threads']==1 and row['mode']=='in']
            if len(cell)!=5 or any(row['tier'] is not None or row['all_workers_controls_valid'] for row in cell) or selected['status']!='unproven-invalid-mode':raise AssertionError('单角色漂移必须清空该cell全部五角色')
        elif selected['status']!='valid-negative-below-50' or selected['tier'] is not None:raise AssertionError('最劣phase不能用合并十样本救线')
        reports.append(dict(profile=profile,passed=True,audit_calls=result['total_calls'],expected_behavior_checked=True,synthetic=True))
    save(args.output/'preflight.json',dict(preflight_passed=True,purpose=__doc__,plan_sha256=digest,source_sha256=sha(Path(__file__)),frozen_sources=len(plan['source_sha256']),frozen_inputs=len(plan['input_sha256']),calls=1040,rss_processes=5,new_parallel_kernel0_ast=True,profiles=reports,scope='仅AST/冻结身份/明确标注的模拟整数审计；没有调用native、映射模型、输出图像、实际模块枚举或测时，不授性能/内存资格。'))
    print(dict(preflight_passed=True,plan_sha256=digest,profiles=4,native_calls=0,actual_rss_processes=0),flush=True)

if __name__=='__main__':main()
