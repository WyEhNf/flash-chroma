"""独立重建全部精确字节索引，核验四包交错、非对齐gather尾保护与只读ABI；不测速。"""
import argparse,ctypes as ct,hashlib
from pathlib import Path
import numpy as np
from skylake_support import ROOT,build_libraries,checked,claim,digest,read,save,unchanged
from palette_support import metadata_bytes, tables as palette_tables
from direct16_support import info,table,storage,DirectInfo

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('plan','build','contract','output'):p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args();plan,build,libraries,loaded=build_libraries(args.plan,args.build)
    prior=read(args.contract)
    if not prior['pass'] or prior['build_sha256']!=digest(args.build/'build.json'):raise ValueError('须先通过同构建基础合同')
    names=[*plan['source_sha256'],'scripts/verify_skylake_byteindex.py','scripts/direct16_support.py','scripts/exception_support.py','scripts/palette_support.py']
    lengths=[0,1,7,8,9,15,16,17,31,32,33,4095,4096,4097]
    out,identity=claim(args.output,args.plan,names,{'purpose':__doc__,'build_sha256':digest(args.build/'build.json'),'loaded_libraries':loaded,
        'seed':2026102024,'lengths':lengths,'patterns':['random','endpoints','same_pair','alternating_parity'],'offsets':[0,1,2,3],
        'backends':[['scalar',1],['avx2',1],['avx2',4]]})
    first=checked(plan['fixed_inputs']['base']);side=checked(plan['fixed_inputs']['sidecar']);models=[first,*[checked(s) for s in plan['suffix_models']]]
    extra=metadata_bytes(libraries,first,side);handles={n:l.chain(models,[side,None,None,None]) for n,l in libraries.items()}
    try:
        cand=handles['candidate'];state=info(cand);words=table(cand)
        assert state['enabled']==1 and state['format']==8 and len(words)==2**22+1 and state['table_capacity_bytes']==2**24+4
        assert cand.model_bytes-handles['reference'].model_bytes==extra+storage(cand)-storage(handles['reference'])
        expected=np.memmap(checked(plan['fixed_inputs']['cube']),np.uint8,'r',shape=(256**3,3))
        _,palette=palette_tables(cand)
        assert words[-1]==0
        for start in range(0,256**3,65536):
            w=words[start//4:(start+65536)//4]
            ids=((w[:,None]>>np.array([0,8,16,24],np.uint32))&255).ravel()
            actual=palette[ids]
            x=np.asarray(expected[start:start+65536])
            truth=x[:,0].astype(np.uint32)|(x[:,1].astype(np.uint32)<<8)|(x[:,2].astype(np.uint32)<<16)
            np.testing.assert_array_equal(actual,truth)
        rng=np.random.default_rng(2026102024);cases=[]
        for pattern in ('random','endpoints','same_pair','alternating_parity'):
            for length in lengths:
                codes=rng.integers(0,2**24,length,dtype=np.uint32)
                if pattern=='endpoints':codes[:]=np.resize(np.array([0,1,2,3,2**24-2,2**24-1,255,256,65535,65536],np.uint32),length)
                elif pattern=='same_pair':codes[:]=(codes[0]&np.uint32(0xfffffe) if length else 0)+(np.arange(length,dtype=np.uint32)&1)
                elif pattern=='alternating_parity':codes=(codes&np.uint32(0xfffffe))+(np.arange(length,dtype=np.uint32)&1)
                source=np.column_stack((codes>>16,(codes>>8)&255,codes&255)).astype(np.uint8);truth=np.asarray(expected[codes]);count=0
                for role,h in handles.items():
                    for kernel,threads in (('scalar',1),('avx2',1),('avx2',4)):
                        for offset in (0,1,2,3):
                            guard=np.full(source.nbytes+offset+17,0xa7,np.uint8);actual=guard[offset:offset+source.nbytes].reshape(-1,3);actual[:]=source
                            h.apply(actual,kernel=kernel,threads=threads);np.testing.assert_array_equal(actual,truth)
                            assert np.all(guard[:offset]==0xa7) and np.all(guard[offset+source.nbytes:]==0xa7);count+=1
                cases.append({'pattern':pattern,'length':length,'comparisons':count,'byte_mismatches':0})
        d=cand.library.dll;f=d.jshc_cc_get_direct_info;raw=DirectInfo();ct.memset(ct.byref(raw),0xa7,ct.sizeof(raw));before=bytes(raw);negative=0
        for handle,output,size in [(None,ct.byref(raw),ct.sizeof(raw)),(cand.handle,None,ct.sizeof(raw)),(cand.handle,ct.byref(raw),ct.sizeof(raw)-1)]:
            assert f(handle,output,size)==1 and bytes(raw)==before;negative+=1
        f=d.jshc_cc_copy_direct;guard=np.full(8,0xa7a7a7a7,np.uint32);ptr=guard.ctypes.data_as(ct.POINTER(ct.c_uint32))
        for handle,pointer,length in [(None,ptr,len(words)),(cand.handle,ptr,len(words)-1),(cand.handle,None,len(words))]:
            assert f(handle,pointer,length)==1 and np.all(guard==0xa7a7a7a7);negative+=1
        save(out/'results.json',{'pass':True,'purpose':__doc__,'plan_sha256':digest(args.plan),'build_sha256':digest(args.build/'build.json'),'libraries':build['libraries'],
            'direct_info':state,'metadata_delta':extra,'table_sha256':hashlib.sha256(words.tobytes()).hexdigest(),'full_oracle_colors':256**3,
            'cases':cases,'finite_comparisons':sum(x['comparisons'] for x in cases),'negative_checks':negative,'byte_mismatches':0,'new_fits':0,'performance_calls':0})
        unchanged(identity);print('字节直索引重建通过：16M颜色，',sum(x['comparisons'] for x in cases),'比较，',negative,'拒绝')
    finally:
        for h in handles.values():h.close()
if __name__=='__main__':main()
