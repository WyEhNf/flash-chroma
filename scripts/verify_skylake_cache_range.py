"""集中核验范围简化：不对称G/B区间、正R最小值、各自边界内外1码、两半向量及尾部。"""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import zipfile
import numpy as np
from skylake_support import build_libraries,claim,digest,read,save,unchanged
from suffix_cache_support import cache_info,cache_table,hit_mask
from delta16_support import layouts
from lutlab import channel_coordinates as cc,io
from verify_channel_coordinates import integer_oracle
from verify_skylake_delta16 import profile

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('plan','build','interaction-contract','output'):p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args();plan,build,libraries,loaded=build_libraries(args.plan,args.build)
    previous=read(args.interaction_contract)
    if not previous['pass'] or previous['build_sha256']!=digest(args.build/'build.json') or previous['libraries']!=build['libraries']:
        raise ValueError('先通过相同构建的编码/缓存交互合同')
    out,identity=claim(args.output,args.plan,[*plan['source_sha256'],'scripts/verify_skylake_cache_range.py'],
        {'purpose':__doc__,'build_sha256':digest(args.build/'build.json'),'loaded_libraries':loaded})
    paths=[];ordinary=[]
    for s,m in enumerate((17,18,25,33)):
        if s==0:
            r=np.rint(np.linspace(32,223,m)).astype(np.uint8);g=r.astype(np.int32)+3+4*(np.arange(m)%2)
            line=np.column_stack((r,g,r)).astype(np.uint8)
            nodes=np.broadcast_to(line[:,None,None,:],(m,m,m,3)).copy();grid=io.uniform_grid(m)
        else:
            grid=np.tile(np.rint(np.linspace(0,255,m)),(3,1))
            rr,gg,bb=np.meshgrid(*grid,indexing='ij')
            # 整数轴上的仿射置换/反相保持RGB8可逆，错误缓存索引不能被后缀偶合的相同颜色掩盖。
            values=((rr,gg,bb) if s==1 else ((255-rr,255-gg,255-bb) if s==2 else (gg,bb,rr)))
            nodes=np.stack(values,axis=-1).astype(np.uint8)
        path=out/f'model{s}.slut';io.save_sparse(path,io.SparseLut(grid,nodes))
        paths.append(path);ordinary.append(cc.from_sparse(io.load_sparse(path,competition=True)))
    targets=[('g_lower_out',[38,38,38],False),('g_lower_in',[38,39,38],True),
             ('g_upper_in',[38,47,38],True),('g_upper_out',[38,48,38],False),
             ('b_lower_out',[38,41,35],False),('b_lower_in',[38,41,36],True),
             ('b_upper_in',[38,41,40],True),('b_upper_out',[38,41,41],False)]
    records=[];fixture_paths=[*paths];canonical=None;table_slots=0
    for label,target,expected_hit in targets:
        first=profile(io.load_sparse(paths[0],competition=True),'bounds')
        first.channel_frac[:]=first.channel_frac[0].copy()
        middle=first.channel_frac[0,0]==32768
        first.channel_frac[1,0,middle]=int(round((target[1]-35)*65536/16))
        first.channel_frac[2,0,middle]=int(round((target[2]-32)*65536/12))
        cc.validate(first);side=out/(label+'.bin');first.channel_frac.astype('<u4').tofile(side);fixture_paths.append(side)
        chain_models=[first,*ordinary[1:]];handles={name:lib.chain(paths,[side,None,None,None]) for name,lib in libraries.items()}
        try:
            infos={name:cache_info(h) for name,h in handles.items()}
            for name,h in handles.items():
                assert layouts(h)==[2,1,1,1]
                info=infos[name]
                assert info['enabled'] and (info['r_min'],info['r_max'],info['dg_min'],info['dg_max'],info['db_min'],info['db_max'])==(32,223,1,9,-2,2)
                table=cache_table(h,info)
                if canonical is None:
                    r,dg,db=np.meshgrid(np.arange(32,224),np.arange(1,10),np.arange(-2,3),indexing='ij')
                    colours=np.column_stack((r.ravel(),(r+dg).ravel(),(r+db).ravel())).astype(np.uint8)
                    truth=colours
                    for model in ordinary[1:]:truth=integer_oracle(model,truth)
                    canonical=truth[:,0].astype(np.uint32)|(truth[:,1].astype(np.uint32)<<8)|(truth[:,2].astype(np.uint32)<<16)
                    assert len(canonical)==8640
                np.testing.assert_array_equal(table,canonical);table_slots+=len(table)
            assert handles['reference'].model_bytes==handles['candidate'].model_bytes
            probe=np.array([[6,0,0]],np.uint8);prefix=integer_oracle(first,probe)
            np.testing.assert_array_equal(prefix,np.array([target],np.uint8))
            assert bool(hit_mask(prefix,infos['candidate'])[0])==expected_hit
            for position in plan['range_policy']['packet_positions']:
                packet=np.tile(np.array([[0,0,0],[255,255,255]],np.uint8),(4,1));packet[position]=probe[0]
                hits=int(hit_mask(integer_oracle(first,packet),infos['candidate']).sum())
                assert hits==(8 if expected_hit else 7)
                for length in plan['range_policy']['fence_lengths']:
                    source=np.resize(packet,(length,3)).astype(np.uint8);truth=source.copy()
                    for model in chain_models:truth=integer_oracle(model,truth)
                    for name,h in handles.items():
                        for kernel,threads in plan['contract']['backend_threads']:
                            for offset in plan['contract']['byte_offsets']:
                                storage=np.full(offset+length*3+17,0xa7,np.uint8)
                                actual=storage[offset:offset+length*3].reshape(length,3);actual[:]=source
                                h.apply(actual,kernel=kernel,threads=threads);np.testing.assert_array_equal(actual,truth)
                                assert np.all(storage[:offset]==0xa7) and np.all(storage[offset+length*3:]==0xa7)
                    records.append({'case':label,'first_output':target,'packet_probe_position':position,'packet_hits':hits,
                        'pixels':length,'byte_mismatches':0,'sentinel_mismatches':0})
        finally:
            for h in handles.values():h.close()
    shutil.copyfile(args.interaction_contract,out/'prior-interaction-results.json')
    for source in args.interaction_contract.parent.glob('prior-*.json'):shutil.copyfile(source,out/source.name)
    with zipfile.ZipFile(out/'fixtures.zip','w',zipfile.ZIP_DEFLATED) as z:
        for path in fixture_paths:z.write(path,path.name)
    unchanged(identity)
    save(out/'results.json',{'pass':True,'purpose':__doc__,'plan_sha256':digest(args.plan),'build_sha256':digest(args.build/'build.json'),
        'libraries':build['libraries'],'prior_interaction_contract_sha256':digest(args.interaction_contract),
        'fence_packet_length_cases':len(records),'cases':records,'independent_table_slots_per_profile_library':8640,
        'total_table_slots_compared':table_slots,'fixture_sha256':{p.name:digest(p) for p in fixture_paths},
        'cache_bounds':{'r':[32,223],'dg':[1,9],'db':[-2,2]},'new_fits':0,'performance_calls':0,
        'scope':'范围检查及未命中恢复的集中整数合同；不替代实际完整色域、100图或Skylake性能。'})
    print('范围边界合同通过：',len(records),'组；两库/8配置表槽累计：',table_slots,flush=True)

if __name__=='__main__':main()
