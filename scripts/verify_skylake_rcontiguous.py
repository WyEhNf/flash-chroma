"""在集中基础/缓存合同后，独立核对R连续的真实存储置换及只读导出失败不写；不测性能。"""
from __future__ import annotations
import argparse
import ctypes as ct
from pathlib import Path
import numpy as np
from skylake_support import build_libraries,claim,digest,read,save,unchanged,checked
from suffix_cache_support import cache_info,cache_table


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('plan','build','contract','cache-contract','output'):p.add_argument('--'+n,type=Path,required=True)
    args=p.parse_args();plan,build,libraries,loaded=build_libraries(args.plan,args.build)
    for path in (args.contract,args.cache_contract):
        v=read(path)
        if not v['pass'] or v['build_sha256']!=digest(args.build/'build.json') or v['libraries']!=build['libraries']:
            raise ValueError('需要同构建的基础及缓存集中合同')
    out,identity=claim(args.output,args.plan,[*plan['source_sha256'],'scripts/verify_skylake_rcontiguous.py'],
        {'purpose':__doc__,'build_sha256':digest(args.build/'build.json'),'loaded_libraries':loaded})
    folder=args.cache_contract.parent;paths=[folder/f'model{i}.slut' for i in range(4)];sides=[folder/f'side{i}.bin' for i in range(4)]
    cases=[('shared_shared',paths,[None]*4),('unshared_shared',paths,[sides[0],None,None,None]),
        ('shared_mixed',paths,[None,sides[1],None,sides[3]]),('unshared_mixed',paths,sides),
        ('equal_changed_shared',paths,[folder/'equal-changed.bin',None,None,None]),
        ('actual_a399',[checked(plan['fixed_inputs']['base']),*[checked(s) for s in plan['suffix_models']]],
            [checked(plan['fixed_inputs']['sidecar']),None,None,None]),('disabled_single',paths[:1],[None])]
    results=[];negatives=0
    for label,model_paths,side_paths in cases:
        handles={name:lib.chain(model_paths,side_paths) for name,lib in libraries.items()}
        try:
            h=handles['candidate'];info=cache_info(h);canonical=cache_table(h,info)
            reference=cache_table(handles['reference'],cache_info(handles['reference']))
            np.testing.assert_array_equal(canonical,reference)
            assert h.model_bytes==handles['reference'].model_bytes
            d=h.library.dll;d.jshc_cc_copy_cache_storage.argtypes=[ct.c_void_p,ct.POINTER(ct.c_uint32),ct.c_size_t];d.jshc_cc_copy_cache_storage.restype=ct.c_int
            guard=np.full(len(canonical)+2,0xa7a7a7a7,np.uint32);raw=guard[1:-1]
            pointer=raw.ctypes.data_as(ct.POINTER(ct.c_uint32));before=guard.copy()
            assert d.jshc_cc_copy_cache_storage(h.handle,pointer,len(raw)+1)==1;np.testing.assert_array_equal(guard,before)
            assert d.jshc_cc_copy_cache_storage(None,pointer,len(raw))==1;np.testing.assert_array_equal(guard,before);negatives+=2
            if len(raw):
                assert d.jshc_cc_copy_cache_storage(h.handle,None,len(raw))==1;negatives+=1
                nr=info['r_max']-info['r_min']+1;ng=info['dg_max']-info['dg_min']+1;nb=info['db_max']-info['db_min']+1
                expected=canonical.reshape(nr,ng,nb).transpose(2,1,0).reshape(-1)
            else:
                assert d.jshc_cc_copy_cache_storage(h.handle,None,0)==0;expected=canonical
            assert d.jshc_cc_copy_cache_storage(h.handle,pointer,len(raw))==0
            np.testing.assert_array_equal(raw,expected);assert guard[0]==guard[-1]==0xa7a7a7a7
            if label=='actual_a399':
                gold=checked(plan['r_contiguous_policy']['cache_gold']);np.testing.assert_array_equal(canonical,np.fromfile(gold,dtype='<u4'))
            results.append({'fixture':label,'entries':len(raw),'canonical_sha256':__import__('hashlib').sha256(canonical.tobytes()).hexdigest(),
                'storage_sha256':__import__('hashlib').sha256(raw.tobytes()).hexdigest(),'storage_byte_mismatches':0,'sentinel_mismatches':0,
                'reference_model_bytes':handles['reference'].model_bytes,'candidate_model_bytes':h.model_bytes,'cache_info':info})
        finally:
            for h in handles.values():h.close()
    unchanged(identity);save(out/'results.json',{'pass':True,'purpose':__doc__,'plan_sha256':digest(args.plan),'build_sha256':digest(args.build/'build.json'),
        'libraries':build['libraries'],'base_contract_sha256':digest(args.contract),'cache_contract_sha256':digest(args.cache_contract),
        'cases':results,'storage_words_checked':sum(r['entries'] for r in results),'diagnostic_negative_checks':negatives,'performance_calls':0,'new_fits':0,
        'scope':'独立声明置换、全部槽及失败不写，不替代完整实际输出或Skylake性能；不重复运行已有像素合同。'})
    print('实际缓存排列独立验证完成：',sum(r['entries'] for r in results),'槽，',negatives,'条负例',flush=True)


if __name__=='__main__':main()
