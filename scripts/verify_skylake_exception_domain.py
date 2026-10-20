"""在一次基础/缓存合同后，集中核对证明/拒绝/关闭状态、实际独立区间和失败不写，不测速。"""
import argparse,ctypes as ct
from pathlib import Path
from skylake_support import ROOT,build_libraries,checked,claim,digest,read,save,unchanged
from suffix_cache_support import cache_info
from exception_support import info as exception_info, table as exception_table, storage, ExceptionInfo
from palette_support import info as palette_info, metadata_bytes
from domain_cache_support import DomainInfo,info


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('plan','build','contract','cache-contract','output'):p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args();plan,build,libraries,loaded=build_libraries(args.plan,args.build)
    for path in (args.contract,args.cache_contract):
        value=read(path)
        if not value['pass'] or value['build_sha256']!=digest(args.build/'build.json') or value['libraries']!=build['libraries']:
            raise ValueError('必须先完成相同构建的集中基础/缓存合同')
    extra_metadata=metadata_bytes(libraries,checked(plan['fixed_inputs']['base']),checked(plan['fixed_inputs']['sidecar']))
    gold=read(checked(plan['domain_cache_policy']['cell_analysis']))
    if not gold['certificate_eligible']:raise ValueError('独立区间没有证明当前模型')
    out,identity=claim(args.output,args.plan,[*plan['source_sha256'],'scripts/exception_support.py','scripts/palette_support.py','scripts/verify_skylake_exception_domain.py'],
        {'purpose':__doc__,'build_sha256':digest(args.build/'build.json'),'loaded_libraries':loaded})
    folder=args.cache_contract.parent;models=[folder/f'model{i}.slut' for i in range(4)];sides=[folder/f'side{i}.bin' for i in range(4)]
    cases=[('shared_shared',models,[None]*4,True),
        ('unshared_shared',models,[sides[0],None,None,None],False),
        ('shared_mixed',models,[None,sides[1],None,sides[3]],True),
        ('unshared_mixed',models,sides,False),
        ('equal_changed_shared',models,[folder/'equal-changed.bin',None,None,None],True),
        ('actual_a399',[checked(plan['fixed_inputs']['base']),*[checked(s) for s in plan['suffix_models']]],
            [checked(plan['fixed_inputs']['sidecar']),None,None,None],True),
        ('disabled_single',models[:1],[None],False),
        ('disabled_wide',[folder/'wide.slut',*models[1:]],[None]*4,False)]
    records=[];negative=0
    for label,paths,side_paths,expected in cases:
        handles={name:lib.chain(paths,side_paths) for name,lib in libraries.items()}
        try:
            candidate=handles['candidate'];actual=info(candidate);cache=cache_info(candidate)
            if actual is None or bool(actual['eligible'])!=expected or actual['cache_enabled']!=cache['enabled']:
                raise AssertionError('证明/拒绝/关闭路径与预期不同：'+label)
            if plan['domain_cache_policy'].get('isolated_original_fallback') and bool(actual.get('fast_path_enabled'))!=(label=='actual_a399'):
                raise AssertionError('隔离快路径派发与实际共享布局不符：'+label)
            if candidate.model_bytes-handles['reference'].model_bytes!=extra_metadata+storage(candidate)-storage(handles['reference']):raise AssertionError('新增元数据与编译表容量不符')
            if label=='actual_a399':
                lo=gold['proven_global_difference_min_GB'];hi=gold['proven_global_difference_max_GB']
                if [actual['dg_min'],actual['db_min']]!=lo or [actual['dg_max'],actual['db_max']]!=hi or actual['reachable_cells']!=gold['reachable_cells']:
                    raise AssertionError('C++证书不同于独立NumPy逐单元结果')
            d=candidate.library.dll;f=d.jshc_cc_get_domain_info
            raw=DomainInfo();ct.memset(ct.byref(raw),0xa7,ct.sizeof(raw));before=bytes(raw)
            assert f(candidate.handle,ct.byref(raw),ct.sizeof(raw)-1)==1 and bytes(raw)==before
            assert f(None,ct.byref(raw),ct.sizeof(raw))==1 and bytes(raw)==before
            assert f(candidate.handle,None,ct.sizeof(raw))==1 and bytes(raw)==before
            negative+=3
            records.append({'fixture':label,'certificate':actual,'reference_model_bytes':handles['reference'].model_bytes,
                            'candidate_model_bytes':candidate.model_bytes,'cache_info':cache,'exception_info':exception_info(candidate)})
        finally:
            for handle in handles.values():handle.close()
    unchanged(identity);save(out/'results.json',{'pass':True,'purpose':__doc__,'plan_sha256':digest(args.plan),
        'build_sha256':digest(args.build/'build.json'),'libraries':build['libraries'],
        'base_contract_sha256':digest(args.contract),'cache_contract_sha256':digest(args.cache_contract),
        'independent_cell_analysis_sha256':digest(checked(plan['domain_cache_policy']['cell_analysis'])),
        'cases':records,'diagnostic_negative_checks':negative,'extra_metadata_bytes':extra_metadata,'explicit_apply_calls':0,'constructor_may_map_full_domain':True,'performance_calls':0,'new_fits':0,
        'scope':'新域证明的特性合同；八个状态及实际完整单元界，不代替完整实际输出或Skylake性能。'})
    print('域证明合同完成：',len(records),'状态、',negative,'诊断负例',flush=True)


if __name__=='__main__':main()
