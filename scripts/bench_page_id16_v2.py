"""P4六角色双阶段、1232调用协议；v1仅借用准备/身份辅助，不执行旧协议。"""
import argparse
import ctypes as ct
import hashlib
from pathlib import Path
import time
import numpy as np
import bench_page_id16 as base

ROOT=base.ROOT
PLAN=ROOT/'experiments/page-id16-performance-v2.json'
base.PLAN=PLAN

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--worker',type=int)
    parser.add_argument('--rss')
    args=parser.parse_args()
    plan=base.checked()
    control=base.affinity()
    args.output.mkdir(parents=True,exist_ok=False)
    if args.rss:
        if args.rss not in plan['roles']:raise ValueError('未知RSS角色')
        before=base.snapshot()
        operation,close,metadata=base.setup(args.rss,plan)
        try:prepared=base.snapshot()
        finally:close()
        closed=base.snapshot()
        value=dict(role=args.rss,plan_sha256=base.sha(PLAN),before=before,prepared=prepared,closed=closed,identity=metadata,affinity=control,environment=base.env(),scope='同v2 imports与流式身份预检的独立fresh，无图片数组；峰值包含Python/依赖库/准备，不称纯模型RAM或prepare专属峰值。')
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
        for role in plan['roles']:operators[role]=base.setup(role,plan)
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
    result=dict(worker=args.worker,passed=failure is None,plan_sha256=base.sha(PLAN),environment=base.env(),affinity=control,roles=list(plan['roles']),phase_orders={str(phase):value for phase,value in orders.items()},thread_order=thread_order,mode_order=mode_order,identities={role:value[2] for role,value in operators.items()},original_source_address=int(source.ctypes.data),target_address=int(target.ctypes.data),rows=rows,scope='v2每角色两阶段各五次，四fresh共1232调用之一；所有角色同址/全驻留，不因稳定性失效补跑。')
    if failure:result['failure']=dict(type=type(failure).__name__,message=str(failure))
    base.save(args.output/'results.json',result)
    print(dict(worker=args.worker,passed=result['passed'],calls=len(rows)),flush=True)
    if failure:raise failure

if __name__=='__main__':main()
