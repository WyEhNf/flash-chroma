"""集中补验获证快路径在四种网格及正负节点斜率下的有限整数正确性，不重跑性能。"""
import argparse
from pathlib import Path
import numpy as np
from skylake_support import ROOT,build_libraries,claim,digest,save,unchanged
from exception_support import info as exception_info, table as exception_table, ExceptionInfo
from direct16_support import info as direct_info, storage
from palette_support import info as palette_info, metadata_bytes
from domain_cache_support import info
from skylake_support import checked
from lutlab import channel_coordinates as cc,io
from verify_channel_coordinates import integer_oracle


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('plan','build','output'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();plan,build,libraries,loaded=build_libraries(args.plan,args.build)
    extra_metadata=metadata_bytes(libraries,checked(plan['fixed_inputs']['base']),checked(plan['fixed_inputs']['sidecar']))
    out,identity=claim(args.output,args.plan,[*plan['source_sha256'],'scripts/direct16_support.py','scripts/exception_support.py','scripts/palette_support.py','scripts/verify_skylake_direct16_signed.py'],
        {'purpose':__doc__,'build_sha256':digest(args.build/'build.json'),'loaded_libraries':loaded,
         'predeclared':{'seed':2026102022,'first_grid_m':[17,18,25,33],'node_grey_range':[120,128],
             'coordinate_powers':[1,1.1,.9],'random_probes':8192,'byte_offsets':[0,1],
             'backend_threads':[['scalar',1],['avx2',1],['avx2',4]]},
         'scope':'只补有限整数覆盖，不拟合或修改冻结候选，不把有限样例称为其他模型的完整色域验收'})
    rng=np.random.default_rng(2026102022);suffix=[];models=[]
    for stage,m in enumerate((17,25,33)):
        path=out/f'suffix{stage}.slut'
        grey=rng.integers(16,240,(m,m,m),np.uint8)
        nodes=np.stack((grey,grey-(stage+1),grey-(stage+3)),axis=-1)
        io.save_sparse(path,io.SparseLut(io.uniform_grid(m),nodes))
        suffix.append(path);models.append(cc.from_sparse(io.load_sparse(path,competition=True)))
    random=rng.integers(0,256,(8192,3),np.uint8)
    corners=np.array([[r,g,b] for r in (0,255) for g in (0,255) for b in (0,255)],np.uint8)
    source=np.concatenate((random,corners,np.array([[1,1,1],[254,254,254],[127,128,129]],np.uint8)))
    rows=[];comparisons=0
    for m in (17,18,25,33):
        grey=rng.integers(120,129,(m,m,m),np.uint8);nodes=np.repeat(grey[...,None],3,axis=3)
        first=out/f'first-m{m}.slut';io.save_sparse(first,io.SparseLut(io.uniform_grid(m),nodes))
        model=cc.from_sparse(io.load_sparse(first,competition=True));slopes=[]
        for axis in range(3):
            d=np.diff(nodes.astype(np.int16),axis=axis);assert d.min()<0 and d.max()>0
            slopes.append([int(d.min()),int(d.max())])
            for cell in np.unique(model.idx[axis]):
                codes=np.flatnonzero(model.idx[axis]==cell);t=np.linspace(0,1,len(codes))
                for channel,power in enumerate((1,1.1,.9)):
                    model.channel_frac[channel,axis,codes]=np.rint(65536*t**power).astype(np.uint32)
        model.channel_frac[:,:,0]=0;model.channel_frac[:,:,255]=65536;cc.validate(model)
        side=out/f'first-m{m}.bin';model.channel_frac.astype('<u4').tofile(side)
        first_truth=integer_oracle(model,source)
        different=int(np.count_nonzero((first_truth[:,0]!=first_truth[:,1])|(first_truth[:,0]!=first_truth[:,2])))
        if not different:raise ValueError('冻结样例没有产生分通道差异，不扫描seed')
        truth=first_truth
        for suffix_model in models:truth=integer_oracle(suffix_model,truth)
        if len(np.unique(truth,axis=0))<2:raise ValueError('后缀把所有探针折叠，拒绝无辨别力样例')
        memory={};certificate=None;payload={};pool={}
        for role,library in libraries.items():
            with library.chain([first,*suffix],[side,None,None,None]) as handle:
                memory[role]=handle.model_bytes;payload[role]=storage(handle);pool[role]=exception_info(handle)
                if role=='candidate':
                    compiled_state=palette_info(handle)
                    direct=direct_info(handle)
                    assert direct['enabled']==1 and direct['table_capacity_bytes']==2**25
                if role=='candidate':
                    certificate=info(handle)
                    assert certificate['eligible']==certificate['fast_path_enabled']==1 and not certificate['unproven_cells']
                for kernel,threads in (('scalar',1),('avx2',1),('avx2',4)):
                    for offset in (0,1):
                        guard=np.full(source.nbytes+offset+17,0xa7,np.uint8)
                        actual=guard[offset:offset+source.nbytes].reshape(-1,3);actual[:]=source
                        handle.apply(actual,kernel=kernel,threads=threads)
                        np.testing.assert_array_equal(actual,truth)
                        assert np.all(guard[:offset]==0xa7) and np.all(guard[offset+source.nbytes:]==0xa7)
                        comparisons+=1
        assert memory['candidate']-memory['reference']==extra_metadata+payload['candidate']-payload['reference']
        rows.append({'m':m,'pixels':len(source),'positive_negative_edge_ranges':slopes,
            'first_outputs_with_channel_difference':different,'certificate':certificate,'model_bytes':memory,'exception_info':pool,
            'direct_info':direct,'first_sha256':digest(first),'sidecar_sha256':digest(side),'byte_mismatches':0,'sentinel_mismatches':0})
    unchanged(identity);save(out/'results.json',{'pass':True,'purpose':__doc__,'plan_sha256':digest(args.plan),
        'build_sha256':digest(args.build/'build.json'),'libraries':build['libraries'],'cases':rows,
        'finite_backend_offset_comparisons':comparisons,'pixels_per_comparison':len(source),
        'byte_mismatches':0,'sentinel_mismatches':0,'new_fits':0,'performance_calls':0,
        'scope':'四个确定性、真正启用获证快路径的有限补验；不代表所有m/任意LUT全域或Skylake实测，不修改既有性能/候选计数'})
    print('正负斜率获证快路径通过：',len(rows),'网格、',comparisons,'比较、每组',len(source),'像素',flush=True)


if __name__=='__main__':main()
