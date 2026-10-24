"""P4 copy4五角色双阶段1040调用；每进程实际模块观察，明确新C99入口。"""
import argparse
import ctypes as ct
import hashlib
from pathlib import Path
import time
import numpy as np
import bench_page_id16 as base
import observe_page_id16_modules as module_observer
from page_id16_copy4_common import PageModel,Borrowed,library as copy_library

ROOT=base.ROOT
PLAN=ROOT/'experiments/page-id16-copy4-performance-v1.json'
base.PLAN=PLAN
MODULE_FAILURE_OUTPUT=None

def setup(role,plan):
    if role!='p4_copy4':return base.setup(role,plan)
    d=copy_library(plan['libraries']['copy4'],True)
    owner=Borrowed(plan['page_rom'],d)
    model=owner.model
    capacity=owner.view.length+ct.sizeof(PageModel)
    if capacity!=plan['capacities'][role]:
        owner.close()
        raise AssertionError('copy4真实capacity不同')
    def apply(src,dst,pixels,threads,mode):
        return d.jshc_p4_apply_copy4_parallel(ct.byref(model),src,dst,pixels,0,threads)
    entrypoint={name:value for name,value in d.copy4_receipt.items() if name not in ('calls','scope')}
    entrypoint['selected_kernel']=0
    entrypoint['scope']='计时直接调用新parallel/kernel0；不走质量Python计数包装，地址不是执行次数。'
    metadata=dict(role=role,capacity=capacity,library=plan['libraries']['copy4'],library_sha256=base.sha(plan['libraries']['copy4']),rom_sha256=base.sha(plan['page_rom']),model_bytes=ct.sizeof(model),blob_address=model.blob,entrypoint_receipt=entrypoint)
    return apply,owner.close,metadata

def checked_modules(label,plan):
    observation=module_observer.snapshot(label)
    if label!='same-imports-before-setup':
        known={str(Path(path)).casefold():value for path,value in plan['input_sha256'].items()}
        for name,rows in observation['dependencies'].items():
            if len(rows)!=1 or known.get(str(Path(rows[0]['path'])).casefold())!=rows[0]['sha256']:
                if MODULE_FAILURE_OUTPUT is not None and not MODULE_FAILURE_OUTPUT.exists():base.save(MODULE_FAILURE_OUTPUT,observation)
                raise AssertionError('实际依赖模块路径/数量/SHA不属于冻结输入：'+name)
    return observation

def main():
    global MODULE_FAILURE_OUTPUT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--worker',type=int)
    parser.add_argument('--rss')
    args=parser.parse_args()
    plan=base.checked()
    control=base.affinity()
    args.output.mkdir(parents=True,exist_ok=False)
    MODULE_FAILURE_OUTPUT=args.output/'module-identity-failure.json'
    if args.rss:
        if args.rss not in plan['roles']:raise ValueError('未知RSS角色')
        before_modules=checked_modules('same-imports-before-setup',plan)
        before=base.snapshot()
        operation,close,metadata=setup(args.rss,plan)
        try:
            prepared_modules=checked_modules('after-prepare',plan)
            prepared=base.snapshot()
        finally:close()
        closed=base.snapshot()
        value=dict(module_observations=[before_modules,prepared_modules,checked_modules('after-close',plan)],role=args.rss,plan_sha256=base.sha(PLAN),before=before,prepared=prepared,closed=closed,identity=metadata,affinity=control,environment=base.env(),scope='同copy4 imports/流式身份SHA/实际模块观察的独立fresh，无图片；峰值含Python/依赖/准备/模块元数据，不称纯模型RAM或prepare专属峰值。')
        base.save(args.output/'rss.json',value)
        print(dict(rss=args.rss,capacity=metadata['capacity']),flush=True)
        return
    if args.worker not in range(4):raise ValueError('固定四worker编号')
    source=np.memmap(plan['photos'],dtype=np.uint8,mode='r')
    target=np.empty(len(source),dtype=np.uint8)
    if len(source)!=235929600:raise AssertionError('完整百图长度不同')
    n=len(source)//3
    src=source.ctypes.data_as(base.U8)
    dst=target.ctypes.data_as(base.U8)
    operators={}
    rows=[]
    module_observations=[]
    failure=None
    order=list(plan['roles'])
    shift=args.worker%len(order)
    order=order[shift:]+order[:shift]
    if args.worker%2:order.reverse()
    orders={1:order,2:list(reversed(order))}
    thread_order=(1,4) if args.worker%2==0 else (4,1)
    mode_order=('in','out') if args.worker%2==0 else ('out','in')

    def measure(role,threads,mode,kind,phase,round_index):
        np.copyto(target,source)
        actual_src=dst if mode=='in' else src
        cpu_before=int(base.GET_CPU())
        started=time.perf_counter_ns()
        result=int(operators[role][0](actual_src,dst,n,threads,mode))
        elapsed=time.perf_counter_ns()-started
        cpu_after=int(base.GET_CPU())
        digest=hashlib.sha256(target).hexdigest()
        rows.append(dict(sequence=len(rows),role=role,threads=threads,mode=mode,kind=kind,phase=phase,round=round_index,wall_ns=elapsed,cpu_before=cpu_before,cpu_after=cpu_after,source_address=int(ct.cast(actual_src,ct.c_void_p).value),target_address=int(target.ctypes.data),returncode=result,sha256=digest))
        if result or digest!=plan['expected_output_sha256'] or cpu_before not in (0,2,4,6) or cpu_after not in (0,2,4,6):raise AssertionError('native/输出/允许集失败，首失败STOP')

    try:
        module_observations.append(checked_modules('same-imports-before-setup',plan))
        for role in plan['roles']:operators[role]=setup(role,plan)
        module_observations.append(checked_modules('after-all-prepare',plan))
        for threads in thread_order:
            for mode in mode_order:
                measure('ref80',threads,mode,'aa_warm',0,0)
                for index in range(2):measure('ref80',threads,mode,'aa_before',0,index)
                for phase in (1,2):
                    for role in orders[phase]:
                        measure(role,threads,mode,'role_warm',phase,0)
                        for index in range(5):measure(role,threads,mode,'measured',phase,index)
                for index in range(2):measure('ref80',threads,mode,'aa_after',0,index)
                base.save(args.output/'partial.json',dict(worker=args.worker,rows=rows))
    except BaseException as error:failure=error
    finally:
        for role,value in reversed(list(operators.items())):value[1]()
    try:module_observations.append(checked_modules('after-all-close',plan))
    except BaseException as error:
        if failure is None:failure=error
    result=dict(module_observations=module_observations,worker=args.worker,passed=failure is None,plan_sha256=base.sha(PLAN),environment=base.env(),affinity=control,roles=list(plan['roles']),phase_orders={str(phase):value for phase,value in orders.items()},thread_order=thread_order,mode_order=mode_order,identities={role:value[2] for role,value in operators.items()},original_source_address=int(source.ctypes.data),target_address=int(target.ctypes.data),rows=rows,scope='copy4每角色两阶段各五次，四fresh共1040调用之一；实际模块同进程观察，所有角色同址/全驻留，不因失效补跑。')
    if failure:result['failure']=dict(type=type(failure).__name__,message=str(failure))
    base.save(args.output/'results.json',result)
    print(dict(worker=args.worker,passed=result['passed'],calls=len(rows)),flush=True)
    if failure:raise failure

if __name__=='__main__':main()
