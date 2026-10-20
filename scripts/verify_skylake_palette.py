"""独立解码全部8色/3bit块，核对实际快慢混合包、边界与诊断不写；不测速。"""
from pathlib import Path
import argparse,ctypes as ct
import numpy as np
from skylake_support import ROOT,build_libraries,checked,claim,digest,read,save,unchanged
from palette_support import PaletteInfo,info,tables,metadata_bytes

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('plan','validation','build','contract','output'):p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args();plan,build,libraries,loaded=build_libraries(args.plan,args.build);validation=read(args.validation)
    if validation['base_plan_sha256']!=digest(args.plan):raise ValueError('新增验收计划不是同一构建计划')
    for name,sha in validation['source_sha256'].items():
        if digest(ROOT/name)!=sha:raise ValueError('新增验收源改变：'+name)
    prior=read(args.contract)
    if not prior['pass'] or prior['build_sha256']!=digest(args.build/'build.json'):raise ValueError('基础合同不符')
    out,identity=claim(args.output,args.plan,[*plan['source_sha256'],__file__,'scripts/palette_support.py',args.validation.resolve().relative_to(ROOT).as_posix()],
        {'purpose':__doc__,'build_sha256':digest(args.build/'build.json'),'loaded_libraries':loaded,'validation_sha256':digest(args.validation)})
    first=checked(plan['fixed_inputs']['base']);side=checked(plan['fixed_inputs']['sidecar']);models=[first,*[checked(s) for s in plan['suffix_models']]]
    extra=metadata_bytes(libraries,first,side);handles={n:l.chain(models,[side,None,None,None]) for n,l in libraries.items()}
    try:
        cand=handles['candidate'];state=info(cand)
        if not state['enabled'] or state['palette_size']>255 or state['blocks']!=2**21:raise ValueError('实际模型未启用固定编码')
        words,palette=tables(cand);n=state['palette_size']
        if cand.model_bytes-handles['reference'].model_bytes!=extra+state['table_capacity_bytes']:raise ValueError('资源容量不同')
        expected=np.memmap(checked(plan['fixed_inputs']['cube']),np.uint8,'r',shape=(256**3,3))
        good=(words&255)!=255;good_count=0;decoded=0
        for start in range(0,len(words),65536):
            w=words[start:start+65536];mask=(w&255)!=255;x=np.asarray(expected[start*8:(start+len(w))*8])
            packed=x[:,0].astype(np.uint32)|(x[:,1].astype(np.uint32)<<8)|(x[:,2].astype(np.uint32)<<16)
            ids=np.searchsorted(palette[:n],packed).reshape(-1,8).astype(np.uint32)
            if np.any(ids>=n) or not np.array_equal(palette[ids.ravel()],packed):raise ValueError('独立完整流不在调色板中')
            lo=ids.min(1);span=ids.max(1)-lo;allowed=span<=7
            np.testing.assert_array_equal(mask,allowed)
            if np.any(w[~mask]!=255):raise ValueError('拒绝块不是标准哨兵')
            independent=lo.copy()
            for k in range(8):independent|=(ids[:,k]-lo)<<np.uint32(8+3*k)
            np.testing.assert_array_equal(w[mask],independent[mask])
            decoded_ids=((w[:,None]>>np.arange(8,32,3,dtype=np.uint32))&7)+(w[:,None]&255)
            np.testing.assert_array_equal(palette[decoded_ids[mask].ravel()],packed.reshape(-1,8)[mask].ravel())
            good_count+=int(mask.sum());decoded+=int(mask.sum())*8
        if good_count!=state['fast_blocks'] or not good_count or good_count==len(words):raise ValueError('快慢两路覆盖计数不符')
        fast=np.flatnonzero(good);slow=np.flatnonzero(~good);rng=np.random.default_rng(validation['seed']);records=[]
        for pattern in validation['patterns']:
            for length in validation['actual_lengths']:
                count=(length+7)//8
                if pattern=='fast':groups=rng.choice(fast,count*8)
                elif pattern=='fallback':groups=rng.choice(slow,count*8)
                else:
                    groups=rng.choice(fast,count*8)
                    if pattern=='seven_fast_one_fallback':groups[7::8]=rng.choice(slow,count)
                    elif pattern=='mixed':groups[1::2]=rng.choice(slow,len(groups[1::2]))
                codes=(groups.astype(np.uint32)*8+rng.integers(0,8,len(groups),dtype=np.uint32))[:length]
                if pattern=='endpoints':
                    anchors=np.array([0,1,7,8,255,256,65535,65536,2**24-1],np.uint32)
                    codes[:min(len(codes),len(anchors))]=anchors[:min(len(codes),len(anchors))]
                source=np.column_stack((codes>>16,(codes>>8)&255,codes&255)).astype(np.uint8)
                truth=np.asarray(expected[codes]);comparisons=0
                for role,h in handles.items():
                    for kernel,threads in validation['backends']:
                        for offset in validation['offsets']:
                            storage=np.full(3*length+offset+17,0xa7,np.uint8);actual=storage[offset:offset+3*length].reshape(-1,3);actual[:]=source
                            h.apply(actual,kernel=kernel,threads=threads)
                            np.testing.assert_array_equal(actual,truth)
                            if np.any(storage[:offset]!=0xa7) or np.any(storage[offset+3*length:]!=0xa7):raise AssertionError('越界写')
                            comparisons+=1
                records.append({'pattern':pattern,'length':length,'comparisons':comparisons,'byte_mismatches':0})
        d=cand.library.dll;f=d.jshc_cc_get_palette_info;raw=PaletteInfo();ct.memset(ct.byref(raw),0xa7,ct.sizeof(raw));before=bytes(raw)
        negative=0
        for handle,output,size in [(None,ct.byref(raw),ct.sizeof(raw)),(cand.handle,None,ct.sizeof(raw)),(cand.handle,ct.byref(raw),ct.sizeof(raw)-1)]:
            if f(handle,output,size)!=1 or bytes(raw)!=before:raise ValueError('诊断失败写入')
            negative+=1
        copy=d.jshc_cc_copy_palette;guard=np.full(len(words)+4,0xa7a7a7a7,np.uint32);pg=np.full(260,0xa7a7a7a7,np.uint32);ptr=ct.POINTER(ct.c_uint32)
        for handle,entries,pn,null_words,null_palette in [(None,len(words),256,False,False),(cand.handle,len(words)-1,256,False,False),(cand.handle,len(words),255,False,False),(cand.handle,len(words),256,True,False),(cand.handle,len(words),256,False,True)]:
            if copy(handle,None if null_words else guard.ctypes.data_as(ptr),entries,None if null_palette else pg.ctypes.data_as(ptr),pn)!=1 or np.any(guard!=0xa7a7a7a7) or np.any(pg!=0xa7a7a7a7):raise ValueError('复制拒绝写入')
            negative+=1
        save(out/'results.json',{'pass':True,'purpose':__doc__,'build_sha256':digest(args.build/'build.json'),'libraries':build['libraries'],'plan_sha256':digest(args.plan),'validation_sha256':digest(args.validation),'palette':state,'metadata_extra_bytes':extra,'decoded_fast_pixels':decoded,'complete_oracle_pixels_checked':256**3,'finite_cases':records,'diagnostic_negative_checks':negative,'performance_calls':0,'new_fits':0,'scope':'固定模型全部块及实际新路径有限比较；构造器执行新准备映射，未进行性能计时'})
        unchanged(identity);print('调色板独立解码/哨兵通过：',256**3,'域像素、',len(records),'组、',sum(r['comparisons'] for r in records),'比较、',negative,'拒绝',flush=True)
    finally:
        for h in handles.values():h.close()
if __name__=='__main__':main()
