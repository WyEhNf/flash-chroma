"""通用冻结句柄的混合尺寸、共享/分输出轴、单/多级合同及可选完整域。"""
import argparse
import hashlib
from pathlib import Path
import sys
import ctypes as ct
import itertools
import numpy as np
from study_memory_rom import ROOT,sha,read,save,env
sys.path.insert(0,str(ROOT/'python'));sys.path.insert(0,str(ROOT/'experiments/channel-runtime'))
from channel_native import Library
from lutlab import channel_coordinates as cc,io
from verify_channel_coordinates import integer_oracle

def fixture(out):
    rng=np.random.default_rng(2026102405);models=[];extended=[];paths=[];sides=[]
    for stage,m in enumerate((17,18,25,33)):
        sparse=io.SparseLut(io.uniform_grid(m),rng.integers(0,256,(m,m,m,3),dtype=np.uint8));path=out/f'model-{stage}.slut';io.save_sparse(path,sparse);model=cc.from_sparse(io.load_sparse(path,competition=True));other=cc.from_sparse(io.load_sparse(path,competition=True))
        for c in range(3):
            for a in range(3):
                f=np.floor(io.ONE*np.power(other.channel_frac[c,a]/float(io.ONE),.5+.25*((c*3+a)%7))+.5).astype(np.uint32);f[[0,255]]=[0,io.ONE];other.channel_frac[c,a]=f
        cc.validate(other);side=out/f'frac-{stage}.bin';other.channel_frac.astype('<u4').tofile(side)
        paths.append(path);sides.append(side);models.append(model);extended.append(other)
    equal=out/'equal.bin';models[0].channel_frac.astype('<u4').tofile(equal)
    return rng,paths,sides,models,extended,equal

def finite(a,d):
    rng,paths,sides,models,extended,equal=fixture(a.output)
    cases=[('ordinary4',paths,[None]*4,models),('first_extended4',paths,[sides[0],None,None,None],[extended[0],*models[1:]]),('mixed4',paths,[None,sides[1],None,sides[3]],[models[0],extended[1],models[2],extended[3]]),('equal_side4',paths,[equal,None,None,None],models),('ordinary1',paths[:1],[None],models[:1]),('extended2',paths[:2],[sides[0],None],[extended[0],models[1]])]
    reference=Library(a.library.parent/'jshc_channel_specialized.dll',sha(a.library.parent/'jshc_channel_specialized.dll'));records=[];comparisons=0
    for label,names,side,representations in cases:
        with d.chain(names,side) as c,reference.chain(names,side) as r:
            for n in (0,1,7,8,9,15,16,17,4095,4096,4097):
                source=rng.integers(0,256,(n,3),dtype=np.uint8);anchors=np.array(list(itertools.product((0,255),repeat=3)),dtype=np.uint8);source[:min(n,8)]=anchors[:min(n,8)];expected=source.copy()
                for model in representations:expected=integer_oracle(model,expected)
                for chain in (c,r):
                    for kernel,t in (('scalar',1),('avx2',1),('avx2',4)):
                        for offset in (0,1,2,3):
                            data=np.full(3*n+offset+17,0xa7,dtype=np.uint8);view=data[offset:offset+3*n].reshape(n,3);view[:]=source;chain.apply(view,kernel=kernel,threads=t)
                            if not np.array_equal(view,expected) or not np.all(data[:offset]==0xa7) or not np.all(data[offset+3*n:]==0xa7):raise AssertionError('有限合同不同')
                            comparisons+=1
            records.append(dict(case=label,compact_bytes=c.model_bytes,specialized_bytes=r.model_bytes,stages=len(names)))
    # 新创建入口单独核对空输出、坏文件和侧表，不能沿旧句柄声明全部继承通过。
    error=ct.create_string_buffer(1024);h=ct.c_void_p(123);null=None;bad=0
    for count in (0,5):
        if not d.dll.jshc_cc_create(null,null,count,ct.byref(h),error,1024) or h.value is not None:raise AssertionError('无效stage未拒绝')
        bad+=1
    truncated=a.output/'truncated.slut';truncated.write_bytes(paths[0].read_bytes()[:-1]);badside=a.output/'bad-side.bin';badside.write_bytes(b'\0'*12)
    for names,side in (([truncated],[None]),([paths[0]],[badside])):
        try:d.chain(names,side)
        except RuntimeError:bad+=1
        else:raise AssertionError('坏输入未拒绝')
    save(a.output/'finite.json',dict(passed=True,environment=env(),comparisons=comparisons,records=records,refusals=bad,scope='独立u64与原specialized双对照；合成节点覆盖全部RGB8输出，不具Cinema窄调色板假设。'))

def full(a,d):
    plan=read(ROOT/'experiments/skylake-andn-split-v1.json');models=[a.data_root/plan['fixed_inputs']['base']['path'],*[a.data_root/x['path'] for x in plan['suffix_models']]];sides=[a.data_root/plan['fixed_inputs']['sidecar']['path'],None,None,None]
    cases=[('single',models[:1],sides[:1],a.data_root/'artifacts/skylake-domain-isolated-full-v1/first-stage.rgb'),('chain',models,sides,a.data_root/'artifacts/cinema-current-anchor-accept-v1/cube.rgb')];hashes={};capacities={}
    for label,paths,side,gold in cases:
        expected_sha='7837c93f7b177a93e4bfb9afe8381e22eb24bdcca16009d6042e5f5b840ff146' if label=='single' else '3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22'
        if sha(gold)!=expected_sha:raise ValueError('固定完整域真值身份不同')
        expected=np.memmap(gold,dtype=np.uint8,mode='r').reshape(-1,3)
        with d.chain(paths,side) as chain:
            capacities[label]=chain.model_bytes
            for kernel,t in (('scalar',1),('avx2',1),('avx2',4)):
                h=hashlib.sha256()
                for start in range(0,1<<24,1<<18):
                    codes=np.arange(start,start+(1<<18),dtype=np.uint32);rgb=np.empty((len(codes),3),dtype=np.uint8);rgb[:,0]=codes>>16;rgb[:,1]=codes>>8;rgb[:,2]=codes;chain.apply(rgb,kernel=kernel,threads=t)
                    if not np.array_equal(rgb,expected[start:start+len(codes)]):raise AssertionError('完整域不符')
                    h.update(rgb)
                hashes[f'{label}_{kernel}_{t}']=h.hexdigest()
    # 一般随机节点/混合尺寸四级另与原specialized AVX2完整域对照，不借Cinema的窄域证明。
    rng,paths,side,models,extended,equal=fixture(a.output)
    ref=Library(a.library.parent/'jshc_channel_specialized.dll',sha(a.library.parent/'jshc_channel_specialized.dll'))
    with d.chain(paths,[side[0],None,None,None]) as chain,ref.chain(paths,[side[0],None,None,None]) as original:
        capacities['general4']=chain.model_bytes;h=hashlib.sha256()
        for start in range(0,1<<24,1<<18):
            codes=np.arange(start,start+(1<<18),dtype=np.uint32);rgb=np.empty((len(codes),3),dtype=np.uint8);rgb[:,0]=codes>>16;rgb[:,1]=codes>>8;rgb[:,2]=codes;expected=rgb.copy();original.apply(expected,kernel='avx2',threads=1);chain.apply(rgb,kernel='avx2',threads=4)
            if not np.array_equal(rgb,expected):raise AssertionError('一般四级完整域不同')
            h.update(rgb)
        hashes['general4_avx2_4']=h.hexdigest()
    save(a.output/'full.json',dict(passed=True,environment=env(),library_sha256=sha(a.library),hashes=hashes,capacities=capacities,scope='a399单级及实际四级各标量1/AVX2 1/4全256^3；一般随机节点/混合尺寸四级另与原specialized AVX2全域对照。输出逐字节不变，无相对原滤镜零误差声明。'))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--library',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--data-root',type=Path,required=True);p.add_argument('--full',action='store_true');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    plan=ROOT/'experiments/compact-sparse-v1.json'
    if any(sha(ROOT/n)!=v for n,v in read(plan)['source_sha256'].items()):raise ValueError('冻结源变化')
    d=Library(a.library,sha(a.library))
    if d.revision!=1001 or d.capabilities!=7:raise AssertionError('实际ABI/指令集不符')
    if a.full:full(a,d)
    else:finite(a,d)
    save(a.output/'driver.json',dict(script_sha256=sha(__file__),plan_sha256=sha(plan),library_sha256=sha(a.library)))
    print(a.output)
if __name__=='__main__':main()
