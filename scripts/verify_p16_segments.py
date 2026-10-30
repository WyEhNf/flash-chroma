"""90显式分段入口：完整RGB8、真实非连续照片与拒绝合同，独立于性能脚本。"""
import argparse
import ctypes as ct
import hashlib
import json
from pathlib import Path
import numpy as np
from p16_segment_support import U8,arrays,apply_segments,output_hash,setup,close,run_driver,save,digest,env,source
from direct16_support import info as direct_info

def full(pair):
    count=1<<24;code=np.arange(count,dtype=np.uint32);flat=np.empty((count,3),np.uint8)
    flat[:,0]=code>>16;flat[:,1]=code>>8;flat[:,2]=code;del code
    gold=pair['baseline'].apply(flat.copy(),kernel='scalar',threads=1)
    lengths=[0,1,7,8,9,65535,65536,65537,1048579];lengths.append(count-sum(lengths));src=[];dst=[];at=0
    for n in lengths:src.append(flat[at:at+n].copy() if n else None);dst.append(np.empty((n,3),np.uint8) if n else None);at+=n
    before=output_hash(src);del flat;expected=hashlib.sha256(memoryview(gold).cast('B')).hexdigest();streams={}
    for kernel in (0,1):
        for threads in (1,4):
            apply_segments(pair['candidate'],src,dst,kernel,threads);at=0
            for n,out in zip(lengths,dst):
                if n:assert np.array_equal(out,gold[at:at+n])
                at+=n
            streams[f'k{kernel}-t{threads}']=output_hash(dst)
    assert output_hash(src)==before and set(streams.values())=={expected}
    return {'colors':count,'lengths':lengths,'byte_mismatches':0,'output_sha256':expected,'streams':streams,'source_sha256':before}

def contracts(pair):
    rng=np.random.default_rng(902);cases=0
    for lengths in ([0],[0]*100,[1,7,8,9,65535,65536,65537], [7]*100):
        storages=[];src=[];dst=[];gold=[]
        for i,n in enumerate(lengths):
            if not n:src.append(None);dst.append(None);gold.append(None);continue
            s=np.full(n*3+126,0xa7,np.uint8);d=np.full(n*3+126,0xc7,np.uint8)
            sa=np.ndarray((n,3),np.uint8,buffer=s,offset=63);da=np.ndarray((n,3),np.uint8,buffer=d,offset=63)
            sa[:]=rng.integers(0,256,sa.shape,np.uint8);src.append(sa);dst.append(da);storages.append((s,d));gold.append(pair['baseline'].apply(sa.copy(),kernel='scalar',threads=1))
        before=output_hash(src)
        for kernel in (0,1):
            for threads in (1,4):
                apply_segments(pair['candidate'],src,dst,kernel,threads)
                for actual,expected in zip(dst,gold):
                    if actual is not None:assert np.array_equal(actual,expected)
                for s,d in storages:assert np.all(s[:63]==0xa7) and np.all(s[-63:]==0xa7) and np.all(d[:63]==0xc7) and np.all(d[-63:]==0xc7)
                cases+=1
        assert output_hash(src)==before
    # 共享只读输入允许，两个目标独立；空批仍验证kernel/threads。
    sample=np.arange(21,dtype=np.uint8).reshape(7,3);outputs=[np.empty_like(sample),np.empty_like(sample)]
    apply_segments(pair['candidate'],[sample,sample],outputs,1,4);assert np.array_equal(outputs[0],outputs[1]);cases+=1
    for k in (0,1):
        for t in (1,4):apply_segments(pair['candidate'],[],[],k,t);cases+=1
    c=pair['candidate'];f=c.library.dll.jshc_cc_apply_to_segments;sources=[np.zeros((7,3),np.uint8),np.ones((7,3),np.uint8)];targets=[np.full((7,3),0xc7,np.uint8) for _ in range(2)]
    s,d,n=arrays(sources,targets);error=ct.create_string_buffer(1024);base=[c.handle,s,d,n,2,1,4,error,len(error)]
    bad=[{0:None},{1:None},{2:None},{3:None},{4:101},{5:2},{6:0},{6:257}]
    # 每个非法数组单独快照，验证最后一段非法时首目标也未写。
    variants=[]
    for kind in ('bytes','null-source','null-destination','same','partial','cross-source','cross-destination','source-overflow','destination-overflow'):
        ss,dd,nn=arrays(sources,targets)
        if kind=='bytes':nn[1]=1
        if kind=='null-source':ss[1]=None
        if kind=='null-destination':dd[1]=None
        if kind=='same':dd[1]=ss[1]
        if kind=='partial':dd[1]=ct.cast(ct.addressof(sources[1].ctypes.data_as(U8).contents)+1,U8)
        if kind=='cross-source':dd[1]=ss[0]
        if kind=='cross-destination':dd[1]=dd[0]
        if kind=='source-overflow':ss[1]=ct.cast(ct.c_void_p((1<<(ct.sizeof(ct.c_void_p)*8))-2),U8)
        if kind=='destination-overflow':dd[1]=ct.cast(ct.c_void_p((1<<(ct.sizeof(ct.c_void_p)*8))-2),U8)
        variants.append({1:ss,2:dd,3:nn})
    bad.extend(variants);before=output_hash(sources)
    for replacement in bad:
        args=base.copy()
        for index,value in replacement.items():args[index]=value
        assert f(*args)==1 and all(np.all(a==0xc7) for a in targets) and output_hash(sources)==before
    return {'finite_groups':cases,'rejections':len(bad),'all_rejections_before_any_write':True,'empty_batch_and_segments':True,'shared_readonly_source':True}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    plan=json.loads(a.plan.read_text(encoding='utf-8'));assert digest(Path(__file__))==plan['script_sha256']
    for n,h in plan['support_sha256'].items():assert digest(Path(n))==h
    if a.output.exists():raise FileExistsError('保留已有质量原件')
    a.output.mkdir(parents=True);libs,chains,frames,f,mp,directory,driver=setup(plan,False);fullproof={};contract={}
    try:
        for role,pair in chains.items():
            fullproof[role]=full(pair);contract[role]=contracts(pair)
            if role=='direct':assert fullproof[role]['output_sha256']=='3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22'
        frames,manifest=source(mp);diag=json.loads(Path(plan['diagnostic_proof']['path']).read_text(encoding='utf-8'));assert digest(Path(plan['diagnostic_proof']['path']))==plan['diagnostic_proof']['sha256']
        expected={(r['role'],r['scale'],r['images']):r['output_sha256'] for r in diag['photos']};photos=[];driver_checks=0
        for role,pair in chains.items():
            for scale in plan['role_scales'][role]:
                for n in (1,10,100):
                    src=[frames[i,::scale,::scale].copy() for i in range(n)];dst=[np.empty_like(x) for x in src];before=output_hash(src)
                    for threads in (1,4):
                        apply_segments(pair['candidate'],src,dst,1,threads);assert output_hash(dst)==expected[role,scale,n]
                    photos.append({'role':role,'scale':scale,'images':n,'output_sha256':output_hash(dst),'noncontiguous_caller_owned':True})
                    assert output_hash(src)==before
                    if n<=10:
                        flat=frames[:n,::scale,::scale].copy();work=np.empty_like(flat)
                        for layout in (0,1):
                            s=[flat[i] for i in range(n)] if not layout else src;d=[work[i] for i in range(n)] if not layout else dst
                            for variant in (0,1,2):
                                for threads in (1,4):
                                    for out in d:out.fill(0xc7)
                                    if layout and variant==1:flat.fill(0xde);work.fill(0xc7)
                                    run_driver(f,pair,s,d,flat,work,layout,variant,threads,1);assert output_hash(d)==expected[role,scale,n];driver_checks+=1
                        del flat,work
                    assert output_hash(src)==before
                    del src,dst
        assert hashlib.sha256(memoryview(frames).cast('B')).hexdigest()=='e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd'
        save(a.output/'correctness.json',{'passed':True,'full':fullproof,'contracts':contract,'photos':photos,'driver_contract_checks':driver_checks,
            'driver_full100_boundary':'质量预检N1/10；正式100三角色每组必须先预热并核caller-owned末work，异常则不计时。',
            'states':{role:{v:{'bytes':c.model_bytes,'direct':direct_info(c)} for v,c in pair.items()} for role,pair in chains.items()},'environment':env()})
        save(a.output/'executed-quality-plan.json',plan);print('90两模型完整RGB8/非连续照片/合同与driver小批验证通过',flush=True)
    finally:close(chains)
if __name__=='__main__':main()
