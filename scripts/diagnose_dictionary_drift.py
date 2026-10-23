"""冻结并诊断原3B变动：同进程全驻留，固定ABBA/BAAB，不恢复速度资格。"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]

def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def save(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def freeze(a,path):
    if path.exists():raise FileExistsError(path)
    native=read(ROOT/'experiments/banked-dictionary-native-v1.json');record=read(ROOT/'artifacts/p16-banked-dictionary-perf-v1/worker-0/results.json');export=read(a.roms/'export.json')
    sources=dict(native['source_sha256'])
    for name in ('scripts/diagnose_dictionary_drift.py','experiments/dictionary-drift-diagnostic-design.md'):sources[name]=sha(ROOT/name)
    inputs=dict(native['input_sha256']);inputs[str((a.roms/'rom-4.bin').resolve())]=export['rom_sha256']
    for role in record['roles'].values():inputs[str(Path(role['library']).resolve())]=role['library_sha256']
    save(path,dict(purpose=__doc__,source_sha256=sources,input_sha256=inputs,resident_roles=native['roles'],role_identities=record['roles'],timed_roles={'A':'ref80','B':'avx2_24'},workers=4,groups_per_sequence=16,sequences=['ABBA','BAAB'],calls_per_worker=128,extra_warmup_calls=0,group_hashes_per_worker=32,protocol='每新进程先准备全部七角色保持驻留，只计ref80及原3B。两块各16组；偶数ABBA后BAAB，奇数相反；同一不可变source和同一target地址，实际原地IO均target。每次输入恢复不计时；组内无大IO/整幅SHA，组末核完整输出SHA。不额外预热或追加调用，首组/坏组全部保留。',instrumentation='每call记录perf_counter_ns壁钟、QueryThreadCycleTime、GetThreadTimes用户/内核、CPU前后号及地址；process/thread affinity只读不改。cycle/time计数边界略包围壁钟边界，差异不扣除；CPU时间/壁钟可因粒度超过1，不截断。周期不转换秒/GHz，不是retired指令。',hypotheses={'H1':'单一共同乘性速率足以解释变动：每worker若group A壁钟p90/p10<=1.10，而局部B/A比p90/p10>=1.25，则反驳该简化解释；其它情况只描述相容/不足，不认定调频原因。', 'H2':'>=10%的可重复序列效应：ABBA/BAAB局部B/A中位比若至少3/4worker同向偏离>=10%，记与顺序关联相容；若全部worker偏离<5%，不支持本场>=10%量级效应；其余不足。序列块与时间交互不当作随机因果。','H3':'壁钟/线程CPU时间/周期并列检验仅抢占解释；计时粒度及不同计数器边界可能妨碍辨别。','H4':'记录端点迁移/affinity；端点CPU不同为观察迁移，同CPU不排除中途迁移。不选择核心/样本，不把H1/H2当唯二原因。'},quantile='numpy.quantile(method=linear)，全部32组，不删除控制或异常组。',qualification='此诊断无100..50档、不恢复原3B推荐、不撤销39.8454%有效反例；不补跑/不改门槛/不绑核/不换输入。'))
    print(path,sha(path))

def worker(a,plan,path):
    import ctypes as ct
    import numpy as np
    import bench_banked_dictionary as models
    from study_memory_rom import U8,env
    a.output.mkdir(parents=True,exist_ok=False)
    for name,value in plan['source_sha256'].items():
        if sha(ROOT/name)!=value:raise AssertionError('源身份变化：'+name)
    for name,value in plan['input_sha256'].items():
        if sha(name)!=value:raise AssertionError('输入身份变化：'+name)
    photo=a.data_root/'artifacts/skylake-server-matrix-v1/server-inputs/photos.rgb';src=np.memmap(photo,dtype=np.uint8,mode='r');dst=np.empty(len(src),dtype=np.uint8);source=src.ctypes.data_as(U8);target=dst.ctypes.data_as(U8);n=len(src)//3
    operators={label:models.setup(a,label) for label in plan['resident_roles']};identities={};addresses={}
    for label,item in operators.items():
        if item[4]!=plan['role_identities'][label]['library_sha256']:raise AssertionError('实际DLL身份变化')
        identities[label]=dict(library=item[3],sha256=item[4],capacity=item[2]);keep=item[1]
        if hasattr(keep[1],'table'):addresses[label]=dict(model=ct.addressof(keep[1]),rom=ct.cast(keep[1].blob,ct.c_void_p).value,table=ct.cast(keep[1].table,ct.c_void_p).value,palette=ct.addressof(keep[1].palette))
        else:addresses[label]=dict(opaque_native_handle=keep[1].value)
    k=ct.WinDLL('kernel32',use_last_error=True);k.GetCurrentThread.restype=ct.c_void_p;k.GetCurrentProcess.restype=ct.c_void_p;thread=k.GetCurrentThread();process=k.GetCurrentProcess();k.QueryThreadCycleTime.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint64)];k.GetCurrentProcessorNumber.restype=ct.c_uint32
    class FT(ct.Structure):_fields_=[('lo',ct.c_uint32),('hi',ct.c_uint32)]
    class GA(ct.Structure):_fields_=[('mask',ct.c_size_t),('group',ct.c_uint16),('reserved',ct.c_uint16*3)]
    k.GetThreadTimes.argtypes=[ct.c_void_p,ct.POINTER(FT),ct.POINTER(FT),ct.POINTER(FT),ct.POINTER(FT)];k.GetProcessAffinityMask.argtypes=[ct.c_void_p,ct.POINTER(ct.c_size_t),ct.POINTER(ct.c_size_t)];k.GetThreadGroupAffinity.argtypes=[ct.c_void_p,ct.POINTER(GA)]
    def affinity():
        pm=ct.c_size_t();sm=ct.c_size_t();ga=GA()
        if not k.GetProcessAffinityMask(process,ct.byref(pm),ct.byref(sm)) or not k.GetThreadGroupAffinity(thread,ct.byref(ga)):raise OSError(ct.get_last_error())
        return dict(process_mask=pm.value,system_mask=sm.value,thread_group=ga.group,thread_mask=ga.mask)
    def counters():
        cycles=ct.c_uint64();creation=FT();exit=FT();kernel=FT();user=FT()
        if not k.QueryThreadCycleTime(thread,ct.byref(cycles)) or not k.GetThreadTimes(thread,ct.byref(creation),ct.byref(exit),ct.byref(kernel),ct.byref(user)):raise OSError(ct.get_last_error())
        return cycles.value,(kernel.hi<<32)|kernel.lo,(user.hi<<32)|user.lo
    seqs=plan['sequences'] if a.worker_index%2==0 else list(reversed(plan['sequences']));rows=[];groups=[];affinities=[dict(position='start',value=affinity())]
    for block,sequence in enumerate(seqs):
        affinities.append(dict(position='block-'+str(block)+'-start',value=affinity()))
        for group in range(16):
            ids=[]
            for position,symbol in enumerate(sequence):
                label=plan['timed_roles'][symbol];fn=operators[label][0];np.copyto(dst,src);cpu0=k.GetCurrentProcessorNumber();cy0,kt0,ut0=counters();start=time.perf_counter_ns();rc=fn(source,target,n,1,'inplace');stop=time.perf_counter_ns();cy1,kt1,ut1=counters();cpu1=k.GetCurrentProcessorNumber()
                if rc:raise AssertionError('映射失败')
                row=dict(index=len(rows),block=block,sequence=sequence,group=group,position=position,label=label,wall_ns=stop-start,thread_cycles=cy1-cy0,kernel_ticks100ns=kt1-kt0,user_ticks100ns=ut1-ut0,cpu_execution_over_wall=(kt1-kt0+ut1-ut0)*100/(stop-start),cpu_before=cpu0,cpu_after=cpu1,cpu_endpoint_changed=cpu0!=cpu1,immutable_source_addr=src.ctypes.data,actual_input_addr=dst.ctypes.data,actual_output_addr=dst.ctypes.data)
                ids.append(row['index']);rows.append(row)
            digest=hashlib.sha256(dst).hexdigest()
            if digest!='f3c0d9078bbcf069f33060a45021a28985b70c9616493ba9bea1ac2027858528':raise AssertionError('组末百图SHA不同')
            groups.append(dict(block=block,sequence=sequence,group=group,rows=ids,output_sha256=digest));save(a.output/'partial.json',dict(rows=rows,groups=groups))
        affinities.append(dict(position='block-'+str(block)+'-end',value=affinity()))
    save(a.output/'results.json',dict(purpose=__doc__,plan_sha256=sha(path),environment=env(),worker_index=a.worker_index,identities=identities,addresses=addresses,sequences=seqs,affinities=affinities,rows=rows,groups=groups,scope=plan['qualification']))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('build','roms','ref80','data-root','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--freeze',action='store_true');p.add_argument('--worker-index',type=int);a=p.parse_args();path=ROOT/'experiments/dictionary-drift-diagnostic-v1.json'
    if a.freeze:return freeze(a,path)
    plan=read(path)
    if a.worker_index is not None:return worker(a,plan,path)
    a.output.mkdir(parents=True,exist_ok=False);records=[];common=[sys.executable,'-X','utf8',str(Path(__file__).resolve()),'--build',str(a.build),'--roms',str(a.roms),'--ref80',str(a.ref80),'--data-root',str(a.data_root)]
    for i in range(4):
        command=common+['--worker-index',str(i),'--output',str(a.output/f'worker-{i}')];r=subprocess.run(command,capture_output=True,text=True,encoding='utf-8');records.append(dict(command=command,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));save(a.output/'execution.json',records)
        if r.returncode:raise RuntimeError(r.stderr)
    print(a.output)
if __name__=='__main__':main()
