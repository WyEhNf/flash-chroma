"""集中验证地址复用候选的两种包方向、混合链、整数舍入与ABI合同。"""
from __future__ import annotations
import argparse
import ctypes as ct
import json
from pathlib import Path
import sys
import zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'python'));sys.path.insert(0,str(ROOT/'experiments/channel-runtime'))
import numpy as np
from lutlab import channel_coordinates as cc, io, study_provenance
import channel_native
from channel_native import Library,digest
from verify_channel_coordinates import integer_oracle as oracle


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('不覆盖集中合同')
    args.output.mkdir(parents=True)
    lib=Library(args.library,digest(args.library))
    if lib.capabilities!=7:raise ValueError('本轮要求已核实AVX2/OpenMP标量三种能力')
    rng=np.random.default_rng(2026101923);models=[];paths=[];sidecars=[]
    for i,m in enumerate((17,18,25,33)):
        sparse=io.SparseLut(io.uniform_grid(m),rng.integers(0,256,(m,m,m,3),np.uint8))
        path=args.output/f'model{i}.slut';io.save_sparse(path,sparse);paths.append(path)
        expanded=cc.from_sparse(sparse)
        if i in (1,3):
            # 输入位置在各既定单元中保持顺序，制造三个通道不同的Q16权重及端点。
            for c in range(3):
                for axis in range(3):
                    base=expanded.channel_frac[c,axis].astype(np.float64)/65536.0
                    exponent=0.5+0.25*((c*3+axis)%7)
                    base=np.floor(65536*np.power(base,exponent)+0.5).astype(np.int64);base[[0,255]]=[0,65536]
                    for cell in np.unique(expanded.idx[axis]):
                        mask=expanded.idx[axis]==cell;base[mask]=np.maximum.accumulate(base[mask])
                    expanded.channel_frac[c,axis]=base.astype(np.uint32)
            side=args.output/f'fraction{i}.bin';expanded.channel_frac.astype('<u4').tofile(side);sidecars.append(side)
        else:sidecars.append(None)
        cc.validate(expanded);models.append(expanded)
    entries=[]
    with lib.chain(paths,sidecars) as chain:
        for length in (0,1,7,8,9,15,16,17,4095,4096,4097):
            source=rng.integers(0,256,(length,3),np.uint8)
            expected=source.copy()
            for model in models:expected=oracle(model,expected)
            for kernel,threads in (('scalar',1),('scalar',4),('avx2',1),('avx2',4)):
                for offset in (0,1,2,3):
                    buffer=np.full(length*3+offset+17,0xa7,np.uint8);view=buffer[offset:offset+length*3].reshape(length,3)
                    view[:]=source;chain.apply(view,kernel=kernel,threads=threads)
                    np.testing.assert_array_equal(view,expected)
                    if np.any(buffer[:offset]!=0xa7) or np.any(buffer[offset+length*3:]!=0xa7):raise AssertionError('首尾哨兵被改写')
            entries.append({'pixels':length,'backends_threads':4,'byte_offsets':4,'oracle_mismatches':0,'sentinel_mismatches':0})
        memory=chain.model_bytes
        for kernel,threads in [('bad',1),('scalar',0)]:
            try:chain.apply(np.zeros((8,3),np.uint8),kernel=kernel,threads=threads)
            except (ValueError,RuntimeError):pass
            else:raise AssertionError('非法后端/线程未拒绝')
        # ABI直接核不完整RGB长度，Python包装层不会构造这种非法请求。
        data=np.zeros((2,3),np.uint8);error=ct.create_string_buffer(256)
        status=lib.dll.jshc_cc_apply(chain.handle,data.ctypes.data_as(ct.POINTER(ct.c_uint8)),5,0,1,error,len(error))
        if status==0:raise AssertionError('不完整RGB字节数未拒绝')
    shared=args.output/'shared-fractions.bin'
    cc.from_sparse(io.load_sparse(paths[0],competition=True)).channel_frac.astype('<u4').tofile(shared)
    controls=[]
    source=rng.integers(0,256,(4097,3),np.uint8);expected=oracle(models[0],source)
    for label,sides in [('ordinary',[None]),('equal_sidecar',[shared])]:
        with lib.chain([paths[0]],sides) as chain:
            for kernel in ('scalar','avx2'):
                np.testing.assert_array_equal(chain.apply(source.copy(),kernel=kernel,threads=4),expected)
            original=source.copy()
            measured=chain.bench(source,kernel='avx2',threads=4,repeats=2)
            np.testing.assert_array_equal(source,original)
            if any(not np.isfinite(t) or t<=0 for t in measured['apply_seconds']):raise AssertionError('计时接口回执不合法')
            controls.append({'case':label,'oracle_mismatches':0,'source_changed_by_benchmark':False})
    # 显式构造整包方向一致/不一致和端点相等，不能依赖小扰动随机命中分支。
    branch_probes=[]
    for index in (1,3):
        model=models[index];search=rng.integers(0,256,(8192,3),np.uint8)
        search[:2]=[[0,0,0],[255,255,255]]
        directions=[]
        for c in range(3):
            x,y,z=(model.channel_frac[c,a,search[:,a]].astype(np.int64) for a in range(3))
            first=np.where(z>np.maximum(x,y),2,np.where(y>x,1,0))
            last=np.where(np.minimum(x,y)>z,2,np.where(x>y,1,0))
            directions.append(first|(last<<2))
        common=(directions[0]==directions[1])&(directions[0]==directions[2])
        if not np.any(common) or not np.any(~common):raise AssertionError('缺少方向一致/不一致探针')
        probes=np.concatenate([np.repeat(search[common][:32],8,axis=0),
            np.repeat(search[~common][:32],8,axis=0),np.repeat(search[:2],8,axis=0)])
        expected=oracle(model,probes)
        with lib.chain([paths[index]],[sidecars[index]]) as chain:
            for kernel,threads in [('scalar',1),('avx2',1),('avx2',4)]:
                np.testing.assert_array_equal(chain.apply(probes.copy(),kernel=kernel,threads=threads),expected)
        branch_probes.append({'m':model.m,'common_packets':32,'fallback_packets':32,'endpoint_tie_packets':2,
            'pixels':len(probes),'backends_threads':3,'oracle_mismatches':0})
    for values in [np.zeros(2303,np.uint32),np.full(2304,65537,np.uint32)]:
        p=args.output/f'invalid-{len(values)}.bin';values.tofile(p)
        try:
            with lib.chain([paths[0]],[p]):pass
        except RuntimeError:pass
        else:raise AssertionError('损坏/越界侧表未拒绝')
    original_digest,original_destroy=channel_native.digest,lib.dll.jshc_cc_destroy
    destroyed=[]
    def failed_hash(path):raise OSError('合同注入：create成功后的来源读取失败')
    def counted_destroy(handle):
        destroyed.append(bool(handle.value));original_destroy(handle)
    try:
        channel_native.digest=failed_hash;lib.dll.jshc_cc_destroy=counted_destroy
        try:lib.chain([paths[0]])
        except OSError:pass
        else:raise AssertionError('注入的构造后异常没有传播')
        if destroyed!=[True]:raise AssertionError('构造失败时原生句柄没有恰好清理一次')
    finally:
        channel_native.digest=original_digest;lib.dll.jshc_cc_destroy=original_destroy
    names=['scripts/verify_channel_reuse.py','scripts/verify_channel_coordinates.py','python/lutlab/channel_coordinates.py',
        'experiments/channel-runtime/channel_native.py','experiments/channel-runtime/channel_runtime.h',
        'experiments/channel-runtime/channel_views.hpp','experiments/channel-runtime/channel_runtime.cpp',
        'experiments/channel-runtime-reuse/channel_avx2.cpp','scripts/build_channel_reuse.py',
        'experiments/channel-runtime-reuse-policy-v1.json','CMakeLists.txt']
    sources={n:digest(ROOT/n) for n in names}
    result={'pass':True,'purpose':'内点地址复用两个包分支、有限混合m与4级、逐级整数舍入/未对齐/向量尾部及ABI输入正确性，非真实精度/性能验收',
        'environment':study_provenance.environment_fingerprint(),'library_sha256':lib.sha256,'abi':1,'revision':lib.revision,'capabilities':lib.capabilities,
        'source_sha256':sources,'mixed_m':[17,18,25,33],'cases':entries,'shared_controls':controls,'branch_probes':branch_probes,
        'constructor_exception_cleanup_count':len(destroyed),'model_accounting_bytes':memory,
        'limits':'有限合成合同；未在本合同中运行真实完整域/100图，未验证C99或其他ISA'}
    with zipfile.ZipFile(args.output/'measured-source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for n,h in sources.items():
            if digest(ROOT/n)!=h:raise ValueError('集中合同期间源码变化')
            z.write(ROOT/n,n)
    (args.output/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'pass':True,'cases':len(entries),'capabilities':lib.capabilities,'library_sha256':lib.sha256},ensure_ascii=False))


if __name__=='__main__':main()
