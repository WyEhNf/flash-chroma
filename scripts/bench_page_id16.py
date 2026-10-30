"""六模型全驻留、四模式完整百图与精确AA；每次native调用全输出SHA。"""
import argparse
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import time
import numpy as np
from study_memory_rom import ROOT,U8,Model as LinearModel,native,create,sha,read,save,env
from win_readonly_rom import API,FileView,library as linear_library,snapshot
from page_id16_common import PageModel,Borrowed,library as page_library
PLAN=ROOT/'experiments/page-id16-performance-v1.json'
K32=ct.WinDLL('kernel32',use_last_error=True)
SET_AFFINITY=K32.SetProcessAffinityMask;SET_AFFINITY.argtypes=[ct.c_void_p,ct.c_size_t];SET_AFFINITY.restype=ct.c_int
GET_AFFINITY=K32.GetProcessAffinityMask;GET_AFFINITY.argtypes=[ct.c_void_p,ct.POINTER(ct.c_size_t),ct.POINTER(ct.c_size_t)];GET_AFFINITY.restype=ct.c_int
GET_CPU=K32.GetCurrentProcessorNumber;GET_CPU.restype=ct.c_uint32
def checked():
    plan=read(PLAN)
    if any(sha(ROOT/name)!=value for name,value in plan['source_sha256'].items()) or any(sha(name)!=value for name,value in plan['input_sha256'].items()):raise AssertionError('性能启动前身份不同')
    return plan
def affinity():
    process=API.process();allowed=ct.c_size_t();system=ct.c_size_t()
    if not GET_AFFINITY(process,ct.byref(allowed),ct.byref(system)) or system.value&0x55!=0x55 or not SET_AFFINITY(process,0x55):raise RuntimeError('预定0x55允许集不可设置，STOP')
    if not GET_AFFINITY(process,ct.byref(allowed),ct.byref(system)) or allowed.value!=0x55:raise AssertionError('0x55读回不同')
    return dict(allowed=allowed.value,system=system.value,allowed_logical_cpus=[0,2,4,6],scope='进程允许集，非逐OMP绑定/锁频或旧漂移因果证明。')
def setup(role,plan):
    paths=plan['libraries'];err=ct.create_string_buffer(1024)
    if role in ('ref78','ref80'):
        d=native(Path(paths[role]));h=create(d,Path(plan['data_root']));d.jshc_cc_apply_to.argtypes=[ct.c_void_p,U8,U8,ct.c_size_t,ct.c_int,ct.c_int,ct.POINTER(ct.c_char),ct.c_size_t];capacity=int(d.jshc_cc_model_bytes(h))
        def apply(src,dst,n,threads,mode):
            return d.jshc_cc_apply(h,dst,3*n,1,threads,err,1024) if mode=='in' else d.jshc_cc_apply_to(h,src,dst,3*n,1,threads,err,1024)
        close=lambda:d.jshc_cc_destroy(h)
        metadata=dict(role=role,capacity=capacity,library=paths[role],library_sha256=sha(paths[role]),model_kind='a399快编译句柄')
        if capacity!=28046644:close();raise AssertionError('fast78/80真实capacity不同')
    elif role.startswith('linear_'):
        d=linear_library(paths['linear']);owner=FileView(plan['original_rom'],'readonly');model=owner.prepare(d);capacity=owner.length+ct.sizeof(LinearModel);kernel=1 if role.endswith('avx') else 0
        def apply(src,dst,n,threads,mode):return d.jshc_mem_apply_parallel(ct.byref(model),src,dst,n,kernel,threads)
        close=owner.close;metadata=dict(role=role,capacity=capacity,library=paths['linear'],library_sha256=sha(paths['linear']),rom_sha256=sha(plan['original_rom']),model_bytes=ct.sizeof(model),blob_address=owner.address)
    else:
        d=page_library(paths['p4'],True);owner=Borrowed(plan['page_rom'],d);model=owner.model;capacity=owner.view.length+ct.sizeof(PageModel);kernel=1 if role.endswith('avx') else 0
        def apply(src,dst,n,threads,mode):return d.jshc_p4_apply_parallel(ct.byref(model),src,dst,n,kernel,threads)
        close=owner.close;metadata=dict(role=role,capacity=capacity,library=paths['p4'],library_sha256=sha(paths['p4']),rom_sha256=sha(plan['page_rom']),model_bytes=ct.sizeof(model),blob_address=model.blob)
    if capacity!=plan['capacities'][role]:close();raise AssertionError('真实角色capacity与冻结不同')
    return apply,close,metadata
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--worker',type=int);p.add_argument('--rss');a=p.parse_args();plan=checked();control=affinity();a.output.mkdir(parents=True,exist_ok=False)
    if a.rss:
        if a.rss not in plan['roles']:raise ValueError('未知RSS角色')
        before=snapshot();fn,close,metadata=setup(a.rss,plan);prepared=snapshot();close();closed=snapshot();save(a.output/'rss.json',dict(role=a.rss,plan_sha256=sha(PLAN),before=before,prepared=prepared,closed=closed,identity=metadata,affinity=control,environment=env(),scope='同imports独立fresh，无图片数组；准备/库/进程全成本包含，非纯模型RAM。'));print(dict(rss=a.rss,capacity=metadata['capacity']),flush=True);return
    if a.worker not in range(4):raise ValueError('固定4worker编号')
    source=np.memmap(plan['photos'],dtype=np.uint8,mode='r');target=np.empty(len(source),dtype=np.uint8);n=len(source)//3
    if len(source)!=235929600:raise AssertionError('完整百图长度不同')
    src=source.ctypes.data_as(U8);dst=target.ctypes.data_as(U8);operators={};rows=[];failure=None
    def measure(role,threads,mode,kind,round_index):
        np.copyto(target,source);actual_src=dst if mode=='in' else src;cpu_before=int(GET_CPU());started=time.perf_counter_ns();result=int(operators[role][0](actual_src,dst,n,threads,mode));elapsed=time.perf_counter_ns()-started;cpu_after=int(GET_CPU());digest=hashlib.sha256(target).hexdigest();row=dict(sequence=len(rows),role=role,threads=threads,mode=mode,kind=kind,round=round_index,wall_ns=elapsed,cpu_before=cpu_before,cpu_after=cpu_after,source_address=int(ct.cast(actual_src,ct.c_void_p).value),target_address=int(target.ctypes.data),returncode=result,sha256=digest);rows.append(row)
        if result or digest!=plan['expected_output_sha256'] or cpu_before not in (0,2,4,6) or cpu_after not in (0,2,4,6):raise AssertionError('native/输出/允许集失败，首失败STOP')
    order=list(plan['roles']);shift=a.worker%len(order);order=order[shift:]+order[:shift]
    if a.worker%2:order.reverse()
    thread_order=(1,4) if a.worker%2==0 else (4,1);mode_order=('in','out') if a.worker%2==0 else ('out','in')
    try:
        for role in plan['roles']:operators[role]=setup(role,plan)
        for threads in thread_order:
            for mode in mode_order:
                measure('ref80',threads,mode,'aa_warm',0)
                for r in range(2):measure('ref80',threads,mode,'aa_before',r)
                for role in order:
                    measure(role,threads,mode,'role_warm',0)
                    for r in range(5):measure(role,threads,mode,'measured',r)
                for r in range(2):measure('ref80',threads,mode,'aa_after',r)
                save(a.output/'partial.json',dict(worker=a.worker,rows=rows))
    except BaseException as error:failure=error
    finally:
        for role,value in reversed(list(operators.items())):value[1]()
    data=dict(worker=a.worker,passed=failure is None,plan_sha256=sha(PLAN),environment=env(),affinity=control,roles=list(plan['roles']),order=order,thread_order=thread_order,mode_order=mode_order,identities={role:value[2] for role,value in operators.items()},original_source_address=int(source.ctypes.data),target_address=int(target.ctypes.data),rows=rows,scope='656协议中的一个fresh；所有角色同址/全驻留，原始ns/SHA/CPU全保留，不因AA无效补跑。')
    if failure:data['failure']=dict(type=type(failure).__name__,message=str(failure))
    save(a.output/'results.json',data);print(dict(worker=a.worker,passed=data['passed'],calls=len(rows)),flush=True)
    if failure:raise failure
if __name__=='__main__':main()
