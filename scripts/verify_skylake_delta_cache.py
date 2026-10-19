"""集中验证差值编码与缓存的交互：打包后建表、全命中、7命中1未命中及混合后缀；不测性能。"""
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
    for name in ('plan','build','contract','cache-contract','layout-contract','output'):
        p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args();plan,build,libraries,loaded=build_libraries(args.plan,args.build)
    priors={name:read(getattr(args,name.replace('-','_'))) for name in ('contract','cache-contract','layout-contract')}
    for value in priors.values():
        if not value['pass'] or value['build_sha256']!=digest(args.build/'build.json') or value['libraries']!=build['libraries']:
            raise ValueError('组合合同需要同次构建的三份前置合同通过')
    out,identity=claim(args.output,args.plan,[*plan['source_sha256'],'scripts/verify_skylake_delta_cache.py'],
        {'purpose':__doc__,'build_sha256':digest(args.build/'build.json'),'loaded_libraries':loaded})
    rng=np.random.default_rng(plan['combination_policy']['contract_seed']);paths=[];ordinary=[];bounded=[];sides=[]
    for s,m in enumerate((17,18,25,33)):
        if s==0:
            # R轴灰度坡道的节点差为零，缓存dg/db范围固定±2；独立通道坐标可产生可解释的越界。
            grey=np.rint(np.linspace(0,255,m)).astype(np.uint8)
            nodes=np.broadcast_to(grey[:,None,None,None],(m,m,m,3)).copy()
        else:nodes=rng.integers(0,256,(m,m,m,3),np.uint8)
        path=out/f'model{s}.slut';io.save_sparse(path,io.SparseLut(io.uniform_grid(m),nodes))
        model=io.load_sparse(path,competition=True);b=profile(model,'bounds');side=out/f'bounds{s}.bin'
        b.channel_frac.astype('<u4').tofile(side)
        paths.append(path);ordinary.append(cc.from_sparse(model));bounded.append(b);sides.append(side)
    over=profile(io.load_sparse(paths[1],competition=True),'over_positive')
    over_path=out/'over-positive1.bin';over.channel_frac.astype('<u4').tofile(over_path)
    cases=[('packed_shared', [sides[0],None,None,None],[bounded[0],*ordinary[1:]],[2,1,1,1],True),
        ('all_packed',sides,bounded,[2,2,2,2],True),
        ('packed_unpacked_mixed',[sides[0],over_path,None,sides[3]],[bounded[0],over,ordinary[2],bounded[3]],[2,0,1,2],True),
        ('shared_packed_mixed',[None,sides[1],None,sides[3]],[ordinary[0],bounded[1],ordinary[2],bounded[3]],[1,2,1,2],False)]
    records=[];entries=[]
    for label,side_paths,models,flags,mixed in cases:
        handles={name:lib.chain(paths,side_paths) for name,lib in libraries.items()}
        try:
            if layouts(handles['candidate'])!=flags:raise AssertionError('组合样例没有使用冻结布局')
            tables={};infos={}
            for name,h in handles.items():
                info=cache_info(h);infos[name]=info
                if not info or not info['enabled'] or info['table_capacity_bytes']>plan['cache_policy']['budget_bytes']:
                    raise AssertionError('组合缓存未启用或超过原预算')
                if (info['entries'],info['r_min'],info['r_max'],info['dg_min'],info['dg_max'],info['db_min'],info['db_max'])!=(6400,0,255,-2,2,-2,2):
                    raise AssertionError('固定灰度样例的缓存形状不同')
                tables[name]=cache_table(h,info)
            r,dg,db=np.meshgrid(np.arange(256),np.arange(-2,3),np.arange(-2,3),indexing='ij')
            colours=np.column_stack((r.ravel(),(r+dg).ravel(),(r+db).ravel()))
            valid=((colours>=0)&(colours<=255)).all(axis=1);truth=colours[valid].astype(np.uint8)
            for model in models[1:]:truth=integer_oracle(model,truth)
            packed=truth[:,0].astype(np.uint32)|(truth[:,1].astype(np.uint32)<<8)|(truth[:,2].astype(np.uint32)<<16)
            for name,table in tables.items():
                np.testing.assert_array_equal(table[valid],packed)
                assert np.all(table[~valid]==0) and infos[name]['valid_entries']==int(valid.sum())
            np.testing.assert_array_equal(tables['reference'],tables['candidate'])
            assert handles['reference'].model_bytes-handles['candidate'].model_bytes==3072*flags.count(2)
            entries.append({'fixture':label,'layouts':flags,'cache_entries':6400,'legal_slots_per_library':int(valid.sum()),
                'invalid_slots_zero_per_library':int((~valid).sum()),'two_tables_byte_mismatches':0,
                'reference_cache_info':infos['reference'],'candidate_cache_info':infos['candidate']})
            good=np.array([[0,0,0],[255,255,255]],np.uint8)
            packet=np.tile(good,(4,1));bad=np.array([[6,0,0]],np.uint8)
            if not hit_mask(integer_oracle(models[0],packet),infos['candidate']).all():raise AssertionError('全命中样例不成立')
            packets=[('all_hit',packet,8)]
            if mixed:
                first=integer_oracle(models[0],bad)
                np.testing.assert_array_equal(first,np.array([[8,0,16]],np.uint8))
                if hit_mask(first,infos['candidate']).any():raise AssertionError('固定反例未触发范围回退')
                mixed_packet=packet.copy();mixed_packet[-1]=bad[0];packets.append(('seven_hit_one_miss',mixed_packet,7))
            for packet_name,packet,hits in packets:
                assert int(hit_mask(integer_oracle(models[0],packet),infos['candidate']).sum())==hits
                for length in plan['contract']['lengths']:
                    source=np.resize(packet,(length,3)).astype(np.uint8);truth=source.copy()
                    for model in models:truth=integer_oracle(model,truth)
                    for name,handle in handles.items():
                        for kernel,threads in plan['contract']['backend_threads']:
                            for offset in plan['contract']['byte_offsets']:
                                storage=np.full(offset+length*3+17,0xa7,np.uint8)
                                actual=storage[offset:offset+length*3].reshape(length,3);actual[:]=source
                                handle.apply(actual,kernel=kernel,threads=threads)
                                np.testing.assert_array_equal(actual,truth)
                                assert np.all(storage[:offset]==0xa7) and np.all(storage[offset+length*3:]==0xa7)
                    records.append({'fixture':label,'packet':packet_name,'packet_hits':hits,'pixels':length,
                                    'layouts':flags,'byte_mismatches':0,'sentinel_mismatches':0})
        finally:
            for h in handles.values():h.close()
    for name in ('contract','cache-contract','layout-contract'):
        shutil.copyfile(getattr(args,name.replace('-','_')),out/('prior-'+name+'.json'))
    files=[*paths,*sides,over_path]
    with zipfile.ZipFile(out/'fixtures.zip','w',zipfile.ZIP_DEFLATED) as z:
        for path in files:z.write(path,path.name)
    unchanged(identity)
    save(out/'results.json',{'pass':True,'purpose':__doc__,'plan_sha256':digest(args.plan),
        'build_sha256':digest(args.build/'build.json'),'libraries':build['libraries'],
        'prior_contracts':{name:digest(getattr(args,name.replace('-','_'))) for name in priors},
        'layout_packet_length_cases':len(records),'cases':records,'cache_entry_audits':entries,
        'fixture_sha256':{p.name:digest(p) for p in files},'new_fits':0,'performance_calls':0,
        'scope':'编码与缓存交互的集中整数合同，不替代实际完整色域/百图或Skylake性能。'})
    print('组合交互合同通过：',len(records),'组；两库每份合法槽：',sum(x['legal_slots_per_library'] for x in entries),flush=True)

if __name__=='__main__':main()
