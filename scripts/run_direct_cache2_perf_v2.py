"""293/294 V2静态驱动草稿；未获root冻结/执行授权不得运行。"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import statistics as st
# 子进程在ctypes/NumPy/产品DLL/OpenMP导入前先设置允许集；父控制器不导入NumPy。
if '--worker' in sys.argv or '--rss-role' in sys.argv:
    import os
    _early_plan=json.loads(Path(sys.argv[sys.argv.index('--plan')+1]).read_text(encoding='utf-8'))
    os.environ.update(_early_plan['required_environment'])
    import psutil
    psutil.Process().cpu_affinity(_early_plan['allowed_cpus'])
import ctypes as ct
from p16_cache2_perf_support_v2 import ROOT,bootstrap,verify,save,digest,pixel_sha,Pool,modules,memory,load_libraries,path_arrays,create,state,check_state

def setup(plan,profile):
    bootstrap(plan)
    assert sys.version==plan['expected_python']
    before=modules(plan,allow_absent=True)
    libraries,directories=load_libraries(plan)
    loaded=modules(plan)
    pool=Pool(plan,profile)
    arrays={name:path_arrays(spec) for name,spec in plan['models'].items()}
    return libraries,directories,pool,arrays,{'before_native':before,'after_load':loaded}

def worker(args,plan):
    import os
    bootstrap(plan)
    assert sys.version==plan['expected_python']
    verify(plan)
    path=args.output/f'{args.profile}-worker{args.worker}.json'
    rows=[];cold=[];handles={};pool=None;pending=None;module_states={};created=0
    u8=ct.POINTER(ct.c_uint8);double=ct.POINTER(ct.c_double)
    def export():
        return {'profile':args.profile,'worker':args.worker,'hot':rows,'cold':cold,'pending':pending,
            'pool':{'tids':pool.tids,'healthy':pool.healthy,'snapshots':pool.snapshots} if pool else None,
            'module_states':module_states,'successful_creates':created}
    try:
        libraries,directories,pool,arrays,module_states=setup(plan,args.profile)
        import numpy as np
        assert np.__version__==plan['expected_numpy']
        pool.initialize()
        source=np.memmap(plan['source'],np.uint8,'r',shape=(100,786432,3))
        work=np.empty(source.shape,np.uint8);target=np.empty(source.shape,np.uint8)
        work.fill(173);target.fill(173);assert pixel_sha(source)==plan['source_sha256']
        addresses={'source':int(source.ctypes.data),'work':int(work.ctypes.data),'target':int(target.ctypes.data)}
        for role in plan['role_orders'][args.worker]:
            spec=plan['roles'][role];library=libraries[spec['library']]
            handles[role]=create(library,arrays[spec['model']]);created+=1
        states={r:state(libraries[plan['roles'][r]['library']],h) for r,h in handles.items()}
        for role,value in states.items():check_state(plan,role,value)
        pool.endpoint('hot_models_ready');module_states['after_hot_prepare']=modules(plan)

        def group(role,boundary,threads,repeats,label):
            nonlocal pending
            spec=plan['roles'][role];library=libraries[spec['library']]
            output=work if boundary=='inplace' else target;output.fill(173)
            values=np.empty(repeats,np.float64);total=np.empty(repeats,np.float64);error=ct.create_string_buffer(1024)
            fields=[handles[role],source.ctypes.data_as(u8),output.ctypes.data_as(u8),source.nbytes,1,threads,repeats,values.ctypes.data_as(double)]
            before=pool.endpoint(label+'_before')
            pending={'label':label,'role':role,'mode':[boundary,threads],'repeats':repeats,'before_pool':before}
            save(args.output/f'{args.profile}-worker{args.worker}-pending.json',export())
            code=(library.dll.jshc_cc_bench(*fields,total.ctypes.data_as(double),error,len(error)) if boundary=='inplace'
                else library.dll.jshc_cc_bench_to(*fields,error,len(error)))
            assert code==0,error.value
            after=pool.endpoint(label+'_after');actual=pixel_sha(output)
            assert actual==plan['expected'][spec['model']]['100']
            result={'role':role,'repeats':repeats,'apply_seconds':values.tolist(),'actual_output_sha256':actual,
                'before_pool':before,'after_pool':after}
            if boundary=='inplace':result['copy_apply_seconds']=total.tolist()
            pending=None;return result

        for boundary,threads in plan['mode_orders'][args.worker]:
            for pair_id in plan['pair_orders'][args.worker]:
                pair=plan['pairs'][pair_id];letters={'A':pair['candidate'],'B':pair['denominator']}
                palindrome=plan['palindromes'][args.worker];cell={'pair':pair_id,'mode':[boundary,threads],'warm':[],'groups':[]}
                for token in palindrome[:2]:cell['warm'].append(group(letters[token],boundary,threads,2,f'hot-{pair_id}-{boundary}-{threads}-warm-{token}'))
                for slot,token in enumerate(palindrome):
                    result=group(letters[token],boundary,threads,3,f'hot-{pair_id}-{boundary}-{threads}-slot{slot}')
                    result.update(phase=1 if slot<2 else 2,slot=slot);cell['groups'].append(result)
                assert pixel_sha(source)==plan['source_sha256'];rows.append(cell)
                save(args.output/f'{args.profile}-worker{args.worker}-partial.json',export())
        # 冷范围不得有额外热模型驻留。
        for role,handle in handles.items():libraries[plan['roles'][role]['library']].dll.jshc_cc_destroy(handle)
        handles.clear();pool.endpoint('all_hot_models_closed')
        for images in plan['cold_images']:
            inputs=source[:images];out=target[:images];scratch=work[:images]
            src,dst=inputs.ctypes.data_as(u8),out.ctypes.data_as(u8)
            for phase in (1,2):
                order=plan['role_orders'][args.worker] if phase==1 else list(reversed(plan['role_orders'][args.worker]))
                for repeat in range(5):
                    for role in order:
                        assert not handles
                        spec=plan['roles'][role];library=libraries[spec['library']]
                        out.fill(173);scratch.fill(173)
                        source_page_touch=int(inputs.reshape(-1)[::4096].sum(dtype=np.uint64))
                        handle=ct.c_void_p();error=ct.create_string_buffer(1024);internal=np.empty(1,np.float64)
                        fields=(arrays[spec['model']][0],arrays[spec['model']][1],4,ct.byref(handle),error,len(error))
                        create_native=library.dll.jshc_cc_create;out_native=library.dll.jshc_cc_bench_to
                        first_fields=(handle,src,dst,inputs.nbytes,1,4,1,internal.ctypes.data_as(double),error,len(error))
                        before=pool.endpoint(f'cold-{images}-{phase}-{repeat}-{role}_before')
                        pending={'cold':True,'images':images,'phase':phase,'repeat':repeat,'role':role,'before_pool':before}
                        save(args.output/f'{args.profile}-worker{args.worker}-pending.json',export())
                        try:
                            started=time.perf_counter_ns()
                            code=create_native(*fields)
                            built=time.perf_counter_ns()
                            if code:raise RuntimeError(error.value.decode('utf-8','replace'))
                            code=out_native(*first_fields)
                            ended=time.perf_counter_ns()
                            assert code==0,error.value
                            after=pool.endpoint(f'cold-{images}-{phase}-{repeat}-{role}_after')
                            current_state=state(library,handle)
                            check_state(plan,role,current_state,states[role])
                            actual=pixel_sha(out);assert actual==plan['expected'][spec['model']][str(images)]
                        finally:
                            if handle.value:library.dll.jshc_cc_destroy(handle)
                        created+=1
                        cold.append({'role':role,'images':images,'phase':phase,'repeat':repeat,'create_ns':built-started,
                            'first_apply_seconds':float(internal[0]),'wall_ns':ended-started,'actual_output_sha256':actual,
                            'before_pool':before,'after_pool':after,'state':current_state,'source_page_touch':source_page_touch,'destroyed_before_next':True})
                        pending=None;save(args.output/f'{args.profile}-worker{args.worker}-partial.json',export())
        assert pixel_sha(source)==plan['source_sha256']
        pool.finish();module_states['end_after_close']=modules(plan);verify(plan)
        result=export();result.update(passed=True,source_sha256=pixel_sha(source),addresses=addresses,hot_states=states,
            counters={'hot_cells':len(rows),'hot_sha':sum(len(c['warm'])+len(c['groups']) for c in rows),
                'cold_sha':len(cold),'sha':sum(len(c['warm'])+len(c['groups']) for c in rows)+len(cold),
                'apply':sum(sum(g['repeats'] for g in c['warm']+c['groups']) for c in rows)+len(cold),
                'hot_create':6,'cold_create':len(cold)},helper_calls=len(pool.snapshots),
            environment={'python':sys.version,'numpy':np.__version__,'thread_environment':{k:os.environ.get(k) for k in plan['required_environment']}},
            scope='所有热句柄关闭后才开始直接native冷create；metadata及SHA均在连续wall外，核SHA后立即destroy。')
        assert result['counters']==plan['per_worker_expected'] and created==126
        save(path,result)
    except BaseException as error:
        result=export();result['failure']=repr(error);save(args.output/f'{args.profile}-worker{args.worker}-failure.json',result)
        raise
    finally:
        for role,handle in handles.items():libraries[plan['roles'][role]['library']].dll.jshc_cc_destroy(handle)

def rss(args,plan):
    bootstrap(plan);assert sys.version==plan['expected_python'];verify(plan)
    handle=None;pending='before_create';pool=None;module_states={}
    try:
        libraries,directories,pool,arrays,module_states=setup(plan,args.profile);pool.initialize()
        role=plan['roles'][args.rss_role];library=libraries[role['library']]
        pool.endpoint('rss_before_create');before=memory()
        started=time.perf_counter_ns();handle=create(library,arrays[role['model']]);ended=time.perf_counter_ns()
        pool.endpoint('rss_after_create');after=memory();current=state(library,handle);module_states['after_prepare']=modules(plan)
        check_state(plan,args.rss_role,current)
        library.dll.jshc_cc_destroy(handle);handle=None;pending='after_close';pool.endpoint('rss_after_close');closed=memory()
        pool.finish();module_states['end_after_close']=modules(plan);verify(plan)
        save(args.output/f'{args.profile}-rss-{args.rss_role}.json',{'passed':True,'profile':args.profile,'role':args.rss_role,
            'before':before,'after':after,'after_close':closed,'state':current,'prepare_descriptive_ns':ended-started,
            'module_states':module_states,'pool':{'tids':pool.tids,'healthy':pool.healthy,'snapshots':pool.snapshots},
            'helper_calls':len(pool.snapshots),'image_apply_calls':0,'images_loaded':False,'successful_creates':1,
            'python':sys.version,'numpy':sys.modules['numpy'].__version__})
    except BaseException as error:
        save(args.output/f'{args.profile}-rss-{args.rss_role}-failure.json',{'failure':repr(error),'pending':pending,
            'module_states':module_states,'pool':{'tids':pool.tids,'healthy':pool.healthy,'snapshots':pool.snapshots} if pool else None})
        raise
    finally:
        if handle is not None:library.dll.jshc_cc_destroy(handle)

def float_statistics(plan,workers):
    result={'hot':[],'cold':[]}
    for worker in workers:
        for cell in worker['hot']:
            pair=plan['pairs'][cell['pair']];roles=(pair['candidate'],pair['denominator'])
            metrics=('apply_seconds','copy_apply_seconds') if cell['mode'][0]=='inplace' else ('apply_seconds',)
            indexed={(r['role'],r['phase']):r for r in cell['groups']}
            aa={f'{role}/{metric}':st.median(indexed[role,2][metric])/st.median(indexed[role,1][metric]) for role in roles for metric in metrics}
            valid=all(.85<=value<=1.15 for value in aa.values());ratios={}
            for metric in metrics:
                ratios[metric]=[st.median(indexed[roles[1],phase][metric])/st.median(indexed[roles[0],phase][metric]) for phase in (1,2)]
            worst=min(v for values in ratios.values() for v in values)
            result['hot'].append({'profile':worker['profile'],'worker':worker['worker'],'pair':cell['pair'],'mode':cell['mode'],
                'aa':aa,'control_valid':valid,'retained_by_phase':ratios,'worst_retained':worst,
                'tiers':{str(g):valid and worst>=g/100 for g in plan['tiers']}})
        for images in (1,100):
            for pair in [p for p in plan['pairs'] if p['main']]:
                roles=(pair['candidate'],pair['denominator'])
                for metric in ('create_ns','first_apply_seconds','wall_ns'):
                    med={(r,p):st.median(v[metric] for v in worker['cold'] if v['role']==r and v['phase']==p and v['images']==images) for r in roles for p in (1,2)}
                    aa={r:med[r,2]/med[r,1] for r in roles};valid=all(.85<=v<=1.15 for v in aa.values())
                    retained=[med[roles[1],p]/med[roles[0],p] for p in (1,2)];worst=min(retained)
                    result['cold'].append({'profile':worker['profile'],'worker':worker['worker'],'images':images,'pair':pair['id'],'metric':metric,
                        'aa':aa,'control_valid':valid,'retained_by_phase':retained,'worst_retained':worst,
                        'tiers':{str(g):valid and worst>=g/100 for g in plan['tiers']}})
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--plan',required=True,type=Path);parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--profile',choices=('U','P'));parser.add_argument('--worker',type=int);parser.add_argument('--rss-role');args=parser.parse_args()
    plan=json.loads(args.plan.read_text(encoding='utf-8'))
    if args.rss_role:return rss(args,plan)
    if args.worker is not None:return worker(args,plan)
    if args.output.exists():raise FileExistsError('V2唯一正式目录不覆盖')
    verify(plan);args.output.mkdir(parents=True);save(args.output/'executed-plan.json',plan);workers=[]
    for profile in ('U','P'):
        for number in range(4):
            command=[sys.executable,'-X','utf8',__file__,'--plan',str(args.plan),'--output',str(args.output),'--profile',profile,'--worker',str(number)]
            with (args.output/f'{profile}-worker{number}.log').open('w',encoding='utf-8') as stream:subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,check=True)
            workers.append(json.loads((args.output/f'{profile}-worker{number}.json').read_text(encoding='utf-8')))
            print('V2独立worker完成',profile,number,flush=True)
        for role in plan['role_names']:
            command=[sys.executable,'-X','utf8',__file__,'--plan',str(args.plan),'--output',str(args.output),'--profile',profile,'--rss-role',role]
            with (args.output/f'{profile}-rss-{role}.log').open('w',encoding='utf-8') as stream:subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,check=True)
    verify(plan);save(args.output/'statistics.json',float_statistics(plan,workers))
    save(args.output/'results.json',{'passed':True,'worker_sha256':{f"{w['profile']}-{w['worker']}":digest(args.output/f"{w['profile']}-worker{w['worker']}.json") for w in workers},
        'sha_checks':2688,'image_apply_calls':5568,'rss_processes':12,'scope':'U主/P辅分开保存，任何P结果不能恢复U资格；独立Fraction审核另执行。'})

if __name__=='__main__':main()
