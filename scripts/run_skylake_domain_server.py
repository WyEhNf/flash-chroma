"""Linux缓存域证明双库入口：独立正确性、真实整批/逐图调度、逐轮输出校验，正式性能需显式开启。"""
from __future__ import annotations
import argparse
import ctypes as ct
from datetime import datetime,timezone
import hashlib
import itertools
import math
import mmap
import os
from pathlib import Path
import resource
import shutil
import statistics
import subprocess
import sys
import time
import traceback
from skylake_server_support import ROOT,read,save,digest,checked,topology,environment,loaded,bind,create,apply,layouts,cache_details,driver_bind,team,measure
from run_skylake_server import photo_buffers,driver_negative_contract,run_command

ROLES=('cache','domain_isolated')
VERSIONS={'cache':4,'domain_isolated':16}
ORDERS=[['cache','domain_isolated'],['domain_isolated','cache'],['domain_isolated','cache'],['cache','domain_isolated']]
THREADS=[[1,4],[4,1],[1,4],[4,1]];MODES=[[0,1],[1,0],[1,0],[0,1]]
PAIRS=[['cache','domain_isolated']]
GATES={'median_apply_ratio_max':.97,'any_process_apply_ratio_max':1.02,
       'median_copy_apply_ratio_max':1.0,'median_prepare_plus_100_ratio_max':1.0}


class DomainInfo(ct.Structure):
    _fields_=[(n,ct.c_uint32) for n in ('version','eligible','cache_enabled','reserved')]
    _fields_ += [(n,ct.c_uint64) for n in ('reachable_cells','unproven_cells')]
    _fields_ += [(n,ct.c_int32) for n in ('dg_min','dg_max','db_min','db_max')]

def domain_details(d,h,negative=False):
    f=d.jshc_cc_get_domain_info;f.argtypes=[ct.c_void_p,ct.POINTER(DomainInfo),ct.c_size_t];f.restype=ct.c_int
    x=DomainInfo()
    if ct.sizeof(x)!=48 or f(h,ct.byref(x),ct.sizeof(x)) or x.version!=1 or x.reserved:raise ValueError('域证明只读ABI不同')
    fast=d.jshc_cc_domain_fast_enabled;fast.argtypes=[ct.c_void_p];fast.restype=ct.c_uint32
    result={n:getattr(x,n) for n,_ in x._fields_};result['fast_path_enabled']=int(fast(h));checks=0
    if result['fast_path_enabled'] and not result['eligible']:raise ValueError('未证明却启用快路径')
    if negative:
        guard=DomainInfo();ct.memset(ct.byref(guard),0xa7,ct.sizeof(guard));before=bytes(guard)
        for handle,output,size in ((h,ct.byref(guard),ct.sizeof(guard)-1),(None,ct.byref(guard),ct.sizeof(guard)),(h,None,ct.sizeof(guard))):
            if f(handle,output,size)!=1 or bytes(guard)!=before:raise AssertionError('域诊断拒绝保护不同')
            checks+=1
        if fast(None)!=0:raise AssertionError('空句柄快路径诊断不同')
        checks+=1
    result['diagnostic_negative_checks']=checks;return result


def protocol():
    # 在任何计时前验证序位和成对先后均衡；固定两角色，不接受扫描参数。
    for index in range(2):
        if any(sum(row[index]==role for row in ORDERS)!=2 for role in ROLES):raise ValueError('序位不平衡')
    for a,b in itertools.combinations(ROLES,2):
        if sum(row.index(a)<row.index(b) for row in ORDERS)!=2:raise ValueError('成对先后不平衡')
    return {'orders':ORDERS,'thread_orders':THREADS,'mode_orders':MODES,'pairs':PAIRS,'gates':GATES,'repeats':5,'hundred_image_groups':160,'check_every_measured_round':True}
def frozen_sources(bundle):
    for name,sha in bundle['source_sha256'].items():
        if digest(ROOT/name)!=sha:raise ValueError('矩阵源字节变化：'+name)
def load_native(policy,bundle):
    selected=policy['selected_cpus'];os.sched_setaffinity(0,selected)
    plans={key:read(checked(s)) for key,s in policy['plans'].items()}
    builds={key:read(checked(s)) for key,s in policy['builds'].items()}
    if set(plans)!={'domain'}:raise ValueError('本入口只支持已冻结域证明双库计划')
    libraries={};specs={}
    for pair,p in plans.items():
        b=builds[pair]
        if b['plan_sha256']!=policy['plans'][pair]['sha256'] or b['source_sha256']!=p['source_sha256']:raise ValueError('构建与派生计划不同')
        for name,sha in p['source_sha256'].items():
            if digest(ROOT/name)!=sha:raise ValueError('编译源改变：'+name)
    for role in ROLES:
        setting=bundle['roles'][role];b=builds[setting['pair']];s=b['libraries'][setting['role']]
        d=bind(checked(s));specs[role]=s;libraries[role]=d
        if d.jshc_cc_abi_version()!=1 or d.jshc_cc_revision()!=VERSIONS[role] or d.jshc_cc_capabilities()!=7:
            raise ValueError('实际双库ABI/能力/修订不符：'+role)
    driver=driver_bind(checked(policy['driver']));teams={str(n):team(driver,n,selected) for n in (1,4)}
    maps=loaded([*specs.values(),policy['driver']])
    return plans['domain'],libraries,specs,driver,teams,maps
def actual_chain(plan,d,count=4):
    models=[checked(plan['fixed_inputs']['base']),*[checked(s) for s in plan['suffix_models']]][:count]
    return create(d,models,[checked(plan['fixed_inputs']['sidecar']),None,None,None][:count])

def table_bytes(d,h,entries,negative=False):
    if not 0<=entries<=262144:raise ValueError('缓存超过固定1MiB预算')
    f=d.jshc_cc_copy_cache
    f.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint32),ct.c_size_t];f.restype=ct.c_int
    values=(ct.c_uint32*(entries+2))();ct.memset(values,0xa7,ct.sizeof(values))
    pointer=ct.cast(ct.addressof(values)+4,ct.POINTER(ct.c_uint32));before=bytes(values);failures=0
    if negative:
        for handle,count,output in ((h,entries+1,pointer),(None,entries,pointer)):
            if f(handle,output,count)!=1 or bytes(values)!=before:raise AssertionError('存储快照拒绝保护不同')
            failures+=1
        if entries:
            if f(h,None,entries)!=1 or bytes(values)!=before:raise AssertionError('存储快照空输出未拒绝')
            failures+=1
        elif f(h,None,0)!=0:raise AssertionError('空表只读查询失败')
    if f(h,pointer,entries) or values[0]!=0xa7a7a7a7 or values[-1]!=0xa7a7a7a7:
        raise AssertionError('存储快照写越界或失败')
    return ct.string_at(pointer,entries*4),failures

def check_table(role,d,h,expected,canonical,negative=False):
    info=cache_details(d,h,table_hash=False)
    if info is None or any(info[k]!=v for k,v in expected.items() if k!='bounds'):
        raise ValueError('实际缓存计数/容量与冻结预期不同：'+role)
    if any(info[k]!=v for k,v in expected.get('bounds',{}).items()):raise ValueError('缓存范围不同')
    actual,_=table_bytes(d,h,info['entries'])
    if actual!=canonical:raise AssertionError('独立整数缓存原字典序全表不同')
    checks=0;stored=actual
    if role=='domain_isolated':
        stored,checks=table_bytes(d,h,info['entries'],negative=negative)
        if stored!=canonical:raise AssertionError('独立整数预期与实际原字典序缓存不同')
    return {'role':role,'entries':info['entries'],'canonical_sha256':hashlib.sha256(actual).hexdigest(),
        'copied_sha256':hashlib.sha256(stored).hexdigest(),'canonical_export_checked':True,
        'model_accounting_bytes':d.jshc_cc_model_bytes(h),'diagnostic_negative_checks':checks}

def checked_rounds(driver,d,h,source,work,threads,mode,repeats,expected_sha):
    # 每轮只调用计时器一次；完整输出SHA在所有原生计时区间之外核对，不占apply/copy+apply时长。
    result={k:[] for k in ('segment_apply_seconds','segment_copy_apply_seconds','round_apply_seconds','round_copy_apply_seconds','round_wall_seconds')}
    hashes=[]
    for _ in range(repeats):
        value=measure(driver,d,h,source,work,1024*768*3,100,threads,mode,1)
        if any(len(value[k])!=1 for k in ('round_apply_seconds','round_copy_apply_seconds','round_wall_seconds')) or any(len(value[k])!=(100 if mode else 1) for k in ('segment_apply_seconds','segment_copy_apply_seconds')):
            raise ValueError('逐轮计时回执长度与固定调度不同')
        sha=hashlib.sha256(work).hexdigest()
        if sha!=expected_sha:raise AssertionError('某一轮完整100图输出不同，停止且保留已有记录')
        for key in result:result[key].extend(value[key])
        hashes.append(sha)
    return {**result,'round_output_sha256':hashes,'output_hash_scope':'每轮完整100图，核对在原生计时之外；该协议与旧仅核对末轮不同'}
def describe(role,d,h,count,bundle):
    flag=layouts(d,h,count);info=cache_details(d,h,table_hash=True)
    if bundle['roles'][role]['delta16']:
        if flag!=[2]+[1]*(count-1):raise ValueError('实际模型没有启用预期坐标编码：'+role)
    elif flag is not None:raise ValueError('原坐标角色出现非预期布局诊断')
    if bundle['roles'][role]['cache']:
        if info is None:raise ValueError('缺少实际缓存诊断')
        if count==4:
            expected=read(ROOT/bundle['cache_gold_generation'])
            if (not info['enabled'] or info['entries']!=expected['entries'] or info['valid_entries']!=expected['valid_entries']
                or info['table_capacity_bytes']!=expected['bytes'] or info['table_sha256']!=expected['gold_sha256']
                or any(info[k]!=v for k,v in expected['bounds'].items())):raise ValueError('实际缓存与独立整数表不同')
        elif info['enabled'] or info['entries'] or info['reason']!=1:raise ValueError('单级不应启用缓存')
    elif info is not None:raise ValueError('无缓存角色出现派生表')
    certificate=None
    if role=='domain_isolated':
        certificate=domain_details(d,h)
        expected=bundle['domain_expected_actual' if count==4 else 'domain_expected_single']
        if any(certificate[k]!=v for k,v in expected.items()):raise ValueError('实际域证明/快路径状态不同')
    return {'coordinate_layouts':flag,'cache_info':info,'domain_certificate':certificate,'model_accounting_bytes':d.jshc_cc_model_bytes(h)}

def validate(policy,bundle):
    plan,libs,specs,driver,teams,maps=load_native(policy,bundle);fixture=read(ROOT/bundle['fixture_manifest'])
    finite_source=(ROOT/fixture['input']).read_bytes();finite=0;negative=0;memory=[];tables=[];prefixes=[];domains=[]
    for case in fixture['cases']:
        expected=(ROOT/case['expected']).read_bytes();case_source=(ROOT/case['input']).read_bytes() if 'input' in case else finite_source;handles={}
        if len(expected)!=len(case_source) or len(expected)!=4097*3:raise ValueError('有限整数金标准长度不符')
        try:
            for role,d in libs.items():
                handles[role]=create(d,[ROOT/x for x in case['models']],[ROOT/x if x else None for x in case['sidecars']])
                if bundle['roles'][role]['delta16']:
                    if layouts(d,handles[role],len(case['models']))!=case['layouts']:raise ValueError('边界布局不同')
                    f=d.jshc_cc_get_layouts;n=len(case['models']);sentinel=(ct.c_uint32*(n+2))(*([0xa7a7a7a7]*(n+2)))
                    for h,c in ((handles[role],n-1),(handles[role],n+1),(None,n)):
                        before=bytes(sentinel)
                        if f(h,sentinel,c)!=1 or bytes(sentinel)!=before:raise AssertionError('只读布局拒绝保护不同')
                        negative+=1
                    if f(handles[role],None,n)!=1:raise AssertionError('空输出未拒绝')
                    negative+=1
            detail=domain_details(libs['domain_isolated'],handles['domain_isolated'],negative=True)
            expected_domain=case.get('domain_certificate_expected')
            if expected_domain and any(detail[k]!=v for k,v in expected_domain.items()):raise AssertionError('有限域证明不同于已验独立区间')
            domains.append({'case':case['name'],**detail});negative+=detail['diagnostic_negative_checks']
            sizes={role:libs[role].jshc_cc_model_bytes(h) for role,h in handles.items()}
            if sizes['cache']!=sizes['domain_isolated']:
                raise AssertionError('布局改变了有限模型容量')
            memory.append({'case':case['name'],'bytes':sizes,'upstream_coordinate_profile':case['layouts']})
            if 'cache_gold' in case:
                canonical=(ROOT/case['cache_gold']).read_bytes()
                for role,d in libs.items():
                    audit=check_table(role,d,handles[role],case['cache_expected'],canonical,negative=True)
                    audit['case']=case['name'];tables.append(audit);negative+=audit['diagnostic_negative_checks']
                d=libs['cache'];first=create(d,[ROOT/case['models'][0]],[ROOT/case['sidecars'][0] if case['sidecars'][0] else None])
                try:intermediate=apply(d,first,case_source,0,1)
                finally:d.jshc_cc_destroy(first)
                if intermediate!=(ROOT/case['first_expected']).read_bytes():raise AssertionError('缓存覆盖的首级独立预期不同')
                b=case['cache_expected']['bounds'];hits=[]
                for r,g,blue in zip(intermediate[0::3],intermediate[1::3],intermediate[2::3]):
                    hits.append(b['r_min']<=r<=b['r_max'] and b['dg_min']<=g-r<=b['dg_max'] and b['db_min']<=blue-r<=b['db_max'])
                packet_hits=[sum(hits[:8]),sum(hits[8:16])]
                if packet_hits!=case['first_two_packet_hits']:raise AssertionError('没有覆盖冻结的全命中或7命中1未命中')
                prefixes.append({'case':case['name'],'pixels':len(hits),'pixel_hits':sum(hits),'first_two_packet_hits':packet_hits})
            for n in fixture['lengths']:
                for role,d in libs.items():
                    for kernel,threads in fixture['backend_threads']:
                        for offset in fixture['offsets']:
                            if apply(d,handles[role],case_source[:n*3],kernel,threads,offset)!=expected[:n*3]:raise AssertionError('有限独立整数输出不同')
                            finite+=1
        finally:
            for role,h in handles.items():libs[role].jshc_cc_destroy(h)
    handles={};actual={};hashes={};counts={}
    try:
        for role,d in libs.items():
            handles[role]={};actual[role]={}
            for mode,count in (('single',1),('chain',4)):
                h=actual_chain(plan,d,count);handles[role][mode]=h;actual[role][mode]=describe(role,d,h,count,bundle)
                for kernel,threads in ((0,1),(1,1),(1,4)):
                    key=f'{role}_{mode}_{kernel}_{threads}';hashes[key]=hashlib.sha256();counts[key]=0
        mm=[actual[r]['chain']['model_accounting_bytes'] for r in ROLES]
        if mm[0]!=mm[1]:raise AssertionError('实际双模型容量不相同')
        gold=read(ROOT/bundle['cache_gold_generation'])
        expected={'enabled':1,'entries':gold['entries'],'valid_entries':gold['valid_entries'],'table_capacity_bytes':gold['bytes'],'bounds':gold['bounds']}
        for role,d in libs.items():
            audit=check_table(role,d,handles[role]['chain'],expected,(ROOT/bundle['cache_gold']).read_bytes(),negative=True)
            audit['case']='actual_a399';tables.append(audit);negative+=audit['diagnostic_negative_checks']
        d=libs['domain_isolated'];audit=check_table('domain_isolated',d,handles['domain_isolated']['single'],
            {'enabled':0,'entries':0,'table_capacity_bytes':0,'reason':1},b'',negative=True)
        audit['case']='disabled_single';tables.append(audit);negative+=audit['diagnostic_negative_checks']
        with (ROOT/bundle['single_oracle_stream']).open('rb') as sf,checked(plan['fixed_inputs']['cube']).open('rb') as cf:
            single=mmap.mmap(sf.fileno(),0,access=mmap.ACCESS_READ);chain=mmap.mmap(cf.fileno(),0,access=mmap.ACCESS_READ)
            try:
                if len(single)!=256**3*3 or len(chain)!=len(single):raise ValueError('完整预期流长度不同')
                gb=bytes(x for g in range(256) for b in range(256) for x in (g,b))
                for red in range(256):
                    source=bytearray(65536*3);source[0::3]=bytes([red])*65536;source[1::3]=gb[0::2];source[2::3]=gb[1::2];source=bytes(source)
                    start=red*len(source);stop=start+len(source)
                    for role,d in libs.items():
                        for mode,truth in (('single',single[start:stop]),('chain',chain[start:stop])):
                            for kernel,threads in ((0,1),(1,1),(1,4)):
                                output=apply(d,handles[role][mode],source,kernel,threads)
                                if output!=truth:raise AssertionError('完整RGB8直接字节比较失败：'+role+mode)
                                key=f'{role}_{mode}_{kernel}_{threads}';hashes[key].update(output);counts[key]+=65536
            finally:single.close();chain.close()
        print('双库12组完整256³直接字节比较通过',flush=True)
        source,work,source_sha=photo_buffers(bundle);photos=[];driver_contract=[]
        for role,d in libs.items():
            h=handles[role]['chain']
            if not driver_contract:driver_contract=driver_negative_contract(driver,d,h)
            for threads in (1,4):
                for mode in (0,1):
                    rounds=checked_rounds(driver,d,h,source,work,threads,mode,2,bundle['photo_output_sha256'])
                    sha=hashlib.sha256(work).hexdigest()
                    if sha!=bundle['photo_output_sha256']:raise AssertionError('百图调度输出不同')
                    photos.append({'role':role,'threads':threads,'mode':mode,'output_sha256':sha,'round_output_sha256':rounds['round_output_sha256'],'validation_rounds':2})
        if hashlib.sha256(source).hexdigest()!=source_sha:raise AssertionError('只读照片源被修改')
    finally:
        for role,modes in handles.items():
            for h in modes.values():libs[role].jshc_cc_destroy(h)
    if loaded([*specs.values(),policy['driver']])!=maps:raise ValueError('核验中实际库来源改变')
    return {'pass':True,'purpose':'双库集中整数、原字典序缓存全表、完整域与两种逐轮百图调度核验，不作性能结论',
        'policy_sha256':policy['self_sha256'],'libraries':specs,'environment':environment(policy['selected_cpus']),
        'teams':teams,'loaded_libraries':maps,'finite_backend_offset_comparisons':finite,'diagnostic_negative_checks':negative,
        'finite_memory':memory,'actual_models':actual,'full_domain_pixels_per_configuration':counts,
        'cache_table_audits':tables,'first_stage_coverage':prefixes,'domain_diagnostics':domains,
        'full_output_sha256':{k:v.hexdigest() for k,v in hashes.items()},'photos':photos,'photo_source_sha256':source_sha,
        'driver_negative_contract':driver_contract,'driver_callback_failure_aborted':True,
        'byte_mismatches':0,'sentinel_mismatches':0,'performance_comparison_performed':False,'new_fits':0}
def worker(policy,bundle,index):
    if policy['protocol']!=protocol():raise ValueError('性能协议不是预声明矩阵')
    correctness=read(checked(policy['correctness']))
    if (not correctness['pass'] or correctness['policy_sha256']!=policy['validation_policy_sha256'] or correctness['finite_backend_offset_comparisons']!=3432
        or len(correctness['full_domain_pixels_per_configuration'])!=12
        or set(correctness['full_domain_pixels_per_configuration'].values())!={256**3} or len(correctness['photos'])!=8 or len(correctness['domain_diagnostics'])!=13):
        raise ValueError('需要相同双库的完整正确性')
    plan,libs,specs,driver,teams,maps=load_native(policy,bundle)
    if correctness['libraries']!=specs:raise ValueError('性能库与正确性库不同')
    source,work,source_sha=photo_buffers(bundle);records=[]
    for threads in THREADS[index]:
        for mode in MODES[index]:
            for role in ORDERS[index]:
                d=libs[role];started=time.perf_counter();h=actual_chain(plan,d);prepare=time.perf_counter()-started
                try:
                    description=describe(role,d,h,4,bundle)
                    measure(driver,d,h,source,work,1024*768*3,100,threads,mode,1)
                    if hashlib.sha256(work).hexdigest()!=bundle['photo_output_sha256']:raise AssertionError('预热后输出不同')
                    start={'loadavg':os.getloadavg(),'main_affinity':sorted(os.sched_getaffinity(0))}
                    values=checked_rounds(driver,d,h,source,work,threads,mode,5,bundle['photo_output_sha256'])
                    sha=hashlib.sha256(work).hexdigest()
                    if sha!=bundle['photo_output_sha256']:raise AssertionError('计时后输出不同')
                    records.append({'role':role,'threads':threads,'mode':mode,'images':100,'repeats':5,
                        'library':specs[role],'revision':VERSIONS[role],'prepare_wall_seconds':prepare,
                        'prepare_plus_first_100_copy_apply_seconds':prepare+values['round_copy_apply_seconds'][0],
                        'output_sha256':sha,'start_state':start,'end_loadavg':os.getloadavg(),**description,**values})
                finally:d.jshc_cc_destroy(h)
    if hashlib.sha256(source).hexdigest()!=source_sha:raise AssertionError('计时改变源照片')
    if loaded([*specs.values(),policy['driver']])!=maps:raise ValueError('计时库或依赖改变')
    return {'worker_index':index,'pid':os.getpid(),'policy_sha256':policy['self_sha256'],'environment':environment(policy['selected_cpus']),
        'teams':teams,'libraries':specs,'loaded_libraries':maps,'photo_source_sha256':source_sha,'records':records,
        'whole_process_peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'rss_scope':'整个Linux worker峰值，含450MiB源/工作区及2库；不是模型容量'}
def aggregate(workers):
    comparisons=[];summaries=[]
    for threads in (1,4):
        for mode in (0,1):
            rows=[{r['role']:r for r in w['records'] if r['threads']==threads and r['mode']==mode} for w in workers]
            if any(set(r)!=set(ROLES) for r in rows):raise ValueError('缺少矩阵角色')
            for role in ROLES:
                samples=sorted(x for r in rows for x in r[role]['segment_apply_seconds'])
                process_apply=[statistics.median(r[role]['round_apply_seconds']) for r in rows]
                summaries.append({'role':role,'threads':threads,'mode':mode,'process_apply_medians_seconds_per_100':process_apply,
                    'median_apply_ms_per_image':statistics.median(process_apply)*10,
                    'median_copy_apply_ms_per_image':statistics.median(statistics.median(r[role]['round_copy_apply_seconds']) for r in rows)*10,
                    'median_outer_wall_ms_per_image':statistics.median(statistics.median(r[role]['round_wall_seconds']) for r in rows)*10,
                    'segment_apply_ms_p50':statistics.median(samples)*1000,
                    'segment_apply_ms_p99_nearest_rank':samples[math.ceil(.99*len(samples))-1]*1000,
                    'segment_apply_ms_max':samples[-1]*1000,'model_accounting_bytes':rows[0][role]['model_accounting_bytes'],
                    'prepare_wall_seconds':[r[role]['prepare_wall_seconds'] for r in rows],
                    'segment_scope':'一次100图批调用' if mode==0 else '一次固定照片调用，重复照片/轮次不是独立请求'})
            for a,b in PAIRS:
                ratios={}
                for name,key in (('apply','round_apply_seconds'),('copy_apply','round_copy_apply_seconds'),('wall','round_wall_seconds')):
                    ratios[name]=[statistics.median(r[b][key])/statistics.median(r[a][key]) for r in rows]
                ratios['prepared']=[r[b]['prepare_plus_first_100_copy_apply_seconds']/r[a]['prepare_plus_first_100_copy_apply_seconds'] for r in rows]
                failed=[]
                if statistics.median(ratios['apply'])>GATES['median_apply_ratio_max']:failed.append('apply中位不足3%改善')
                if max(ratios['apply'])>GATES['any_process_apply_ratio_max']:failed.append('某进程apply回退超过2%')
                if statistics.median(ratios['copy_apply'])>GATES['median_copy_apply_ratio_max']:failed.append('copy+apply中位回退')
                if statistics.median(ratios['prepared'])>GATES['median_prepare_plus_100_ratio_max']:failed.append('准备+已预热首100图中位回退')
                comparisons.append({'reference':a,'candidate':b,'threads':threads,'mode':mode,'process_ratios':ratios,
                    'median_ratios':{k:statistics.median(v) for k,v in ratios.items()},'passed_host_gates':not failed,'failed_gates':failed})
    return {'measurement_completed':True,'comparisons':comparisons,'summaries':summaries,
        'adoption_by_comparison':{a+'->'+b:all(x['passed_host_gates'] for x in comparisons if x['reference']==a and x['candidate']==b) for a,b in PAIRS},
        'scope':'本次实际机器、2库和两种逐轮校验调度下的描述性结果；不报告总体显著性或自动认定为Skylake，不混用旧内部bench绝对时间'}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--compiler',default='g++');p.add_argument('--c-compiler',default='gcc');p.add_argument('--cmake',default='cmake')
    p.add_argument('--cpus');p.add_argument('--expected-cpu');p.add_argument('--measure',action='store_true')
    p.add_argument('--child-policy',type=Path);p.add_argument('--validate',action='store_true');p.add_argument('--worker',type=int)
    args=p.parse_args();bundle=read(args.bundle)
    if args.bundle.resolve()!=ROOT/'bundle-manifest.json' or bundle['schema']!=3 or set(bundle['roles'])!=set(ROLES):raise ValueError('请在域证明双库固定包内运行')
    protocol()
    if args.child_policy:
        policy=read(args.child_policy);policy['self_sha256']=digest(args.child_policy);frozen_sources(bundle)
        if policy['bundle_sha256']!=digest(args.bundle):raise ValueError('子进程输入包不同')
        if args.validate:result=validate(policy,bundle)
        elif args.worker in range(4):result=worker(policy,bundle,args.worker)
        else:raise ValueError('内部子进程参数无效')
        frozen_sources(bundle);save(args.output,result);print('域证明子步骤完成',flush=True);return
    top=topology([int(x) for x in args.cpus.split(',')] if args.cpus else None);selected=top['selected_cpus'];env0=environment(selected)
    if any('avx2' not in row.get('flags','').split() for row in env0['selected_cpu_details'].values()):raise ValueError('所选CPU均须支持AVX2')
    if args.expected_cpu and any(row.get('model name')!=args.expected_cpu for row in env0['selected_cpu_details'].values()):raise ValueError('所选CPU型号与约定不一致')
    for s in bundle['files'].values():checked(s)
    out=args.output.resolve()
    if out.exists():raise ValueError('不覆盖已有矩阵输出或自动重试')
    out.mkdir(parents=True);env=os.environ.copy()
    for k in list(env):
        if k.startswith(('OMP_','GOMP_','KMP_')):env.pop(k)
    env.update(OMP_NUM_THREADS='1',OMP_DYNAMIC='FALSE',OMP_THREAD_LIMIT='256',OMP_SCHEDULE='STATIC',OMP_PROC_BIND='CLOSE',
        OMP_PLACES=','.join('{'+str(x)+'}' for x in selected),OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONIOENCODING='utf-8')
    save(out/'run.json',{'purpose':__doc__,'bundle_sha256':digest(args.bundle),'topology':top,'environment':env0,'protocol':protocol(),
        'performance_requested':args.measure,'expected_cpu':args.expected_cpu,'started_utc':datetime.now(timezone.utc).isoformat()})
    try:
        compiler=shutil.which(args.compiler);ccompiler=shutil.which(args.c_compiler);cmake=shutil.which(args.cmake)
        if not compiler or not ccompiler or not cmake:raise ValueError('找不到已安装的CMake/GNU C/C++，不自动安装')
        builds={};plans={}
        for key,name in bundle['plans'].items():
            plan=ROOT/name;folder=out/('backend-'+key)
            run_command([sys.executable,str(ROOT/'scripts/build_skylake_runtime.py'),'--plan',str(plan),'--output',str(folder),
                '--compiler',compiler,'--c-compiler',ccompiler,'--cmake',cmake],out/(key+'-build-command.json'),env)
            plans[key]={'path':str(plan),'sha256':digest(plan)};builds[key]={'path':str(folder/'build.json'),'sha256':digest(folder/'build.json')}
        driver=out/'driver'
        run_command([cmake,'-S',str(ROOT/'experiments/skylake-server-driver'),'-B',str(driver),'-DCMAKE_BUILD_TYPE=Release',
            '-DCMAKE_EXPORT_COMPILE_COMMANDS=ON','-DCMAKE_CXX_COMPILER='+compiler],out/'driver-configure.json',env)
        run_command([cmake,'--build',str(driver),'--parallel','4'],out/'driver-build.json',env)
        for r in read(driver/'compile_commands.json'):
            if any(x in r['command'] for x in ('-march=','-mavx','-mfma','-ffast-math','-Ofast')):raise ValueError('驱动含未允许的ISA或数学选项')
        lib=Path(read(driver/'driver-Release.json')['path'])
        policy={'bundle_sha256':digest(args.bundle),'selected_cpus':selected,'plans':plans,'builds':builds,
            'driver':{'path':str(lib),'sha256':digest(lib)},'protocol':protocol(),
            'compiler':{'path':compiler,'sha256':digest(compiler),'version':subprocess.check_output([compiler,'--version'],text=True)},
            'c_compiler':{'path':ccompiler,'sha256':digest(ccompiler)},'cmake':{'path':cmake,'sha256':digest(cmake)}}
        policy_path=out/'policy.json';save(policy_path,policy)
        run_command([sys.executable,str(Path(__file__).resolve()),'--bundle',str(args.bundle.resolve()),'--output',str(out/'correctness.json'),
            '--child-policy',str(policy_path),'--validate'],out/'correctness-command.json',env)
        correctness=read(out/'correctness.json')
        if not correctness['pass']:raise ValueError('集中正确性未通过')
        if args.measure:
            performance_policy={**policy,'validation_policy_sha256':digest(policy_path),
                'correctness':{'path':str(out/'correctness.json'),'sha256':digest(out/'correctness.json')}}
            pp=out/'performance-policy.json';save(pp,performance_policy);workers=[]
            for index in range(4):
                target=out/f'worker{index}.json'
                run_command([sys.executable,str(Path(__file__).resolve()),'--bundle',str(args.bundle.resolve()),'--output',str(target),
                    '--child-policy',str(pp),'--worker',str(index)],out/f'worker{index}-command.json',env)
                workers.append(read(target));print('完成串行矩阵性能进程',index,flush=True)
            if len({w['photo_source_sha256'] for w in workers})!=1:raise ValueError('各进程源不同')
            measured=aggregate(workers);measured['policy_sha256']=digest(pp);measured['worker_sha256']=[digest(out/f'worker{i}.json') for i in range(4)]
            save(out/'performance.json',measured)
        frozen_sources(bundle)
        for s in bundle['files'].values():checked(s)
        save(out/'results.json',{'pass':True,'correctness_passed':True,'performance_measured':args.measure,
            'correctness_sha256':digest(out/'correctness.json'),'policy_sha256':digest(policy_path),'bundle_sha256':digest(args.bundle),
            'adoption_by_comparison':read(out/'performance.json')['adoption_by_comparison'] if args.measure else None,
            'finished_utc':datetime.now(timezone.utc).isoformat(),'scope':'实际Linux机器见环境记录，不自动标为Skylake或官方成绩；候选通过与否分别报告'})
        print('缓存域证明双库完成，正式计时：',args.measure,flush=True)
    except Exception:
        save(out/'failure.json',{'pass':False,'traceback':traceback.format_exc(),'scope':'保留失败证据，不自动重试或调参'});raise

if __name__=='__main__':main()
