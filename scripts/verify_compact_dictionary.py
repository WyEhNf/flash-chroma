"""完整域与有限形状验证M16P C99/AVX2原地及分离接口，金标准固定a399。"""
import argparse
import ctypes as ct
import hashlib
from pathlib import Path
import numpy as np
from study_memory_rom import ROOT,Model,U8,romlib,loadrom,read,sha,save,env

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('build','roms','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);plan=read(ROOT/'experiments/compact-dictionary-v1.json')
    if any(sha(ROOT/n)!=v for n,v in plan['source_sha256'].items()):raise ValueError('冻结源码变化')
    desktop=romlib(a.build/'jshc_memory_rom.dll');portable=romlib(a.build/'jshc_dict_c99.dll');rng=np.random.default_rng(2026102407);records=[];comparisons=0;refusals=0
    for mode in (17,24):
        rom=a.roms/f'rom-{mode}.bin';model,keep=loadrom(desktop,rom);scalar,scalar_keep=loadrom(portable,rom)
        for n in (0,1,7,8,9,15,16,17,31,32,33,73,4095,4096,4097):
            src=rng.integers(0,256,(n,3),dtype=np.uint8);expected=np.empty_like(src)
            if portable.jshc_mem_apply(ct.byref(scalar),src.ctypes.data_as(U8),expected.ctypes.data_as(U8),n):raise AssertionError('独立C99失败')
            for kernel,threads in ((0,1),(1,1),(1,4)):
                for same in (False,True):
                    for offset in (0,1,3,7):
                        source=np.full(3*n+offset+17,0xa7,dtype=np.uint8);source[offset:offset+3*n]=src.reshape(-1);target=source if same else np.full_like(source,0xa7);sp=source[offset:offset+3*n].ctypes.data_as(U8);tp=target[offset:offset+3*n].ctypes.data_as(U8)
                        if desktop.jshc_mem_apply_parallel(ct.byref(model),sp,tp,n,kernel,threads) or not np.array_equal(target[offset:offset+3*n],expected.reshape(-1)) or not np.all(target[:offset]==0xa7) or not np.all(target[offset+3*n:]==0xa7):raise AssertionError('有限接口或哨兵不同')
                        comparisons+=1
        hashes={}
        for label,d,m,k,t in [('c99',portable,scalar,0,1),('desktop_scalar',desktop,model,0,1),('avx2_1',desktop,model,1,1),('avx2_4',desktop,model,1,4)]:
            digest=hashlib.sha256()
            for start in range(0,1<<24,1<<18):
                codes=np.arange(start,start+(1<<18),dtype=np.uint32);src=np.empty((len(codes),3),dtype=np.uint8);src[:,0]=codes>>16;src[:,1]=codes>>8;src[:,2]=codes;dst=np.empty_like(src)
                rc=d.jshc_mem_apply(ct.byref(m),src.ctypes.data_as(U8),dst.ctypes.data_as(U8),len(src)) if label=='c99' else d.jshc_mem_apply_parallel(ct.byref(m),src.ctypes.data_as(U8),dst.ctypes.data_as(U8),len(src),k,t)
                if rc:raise AssertionError('完整域调用失败')
                digest.update(dst)
            hashes[label]=digest.hexdigest()
            if hashes[label]!='3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22':raise AssertionError('完整RGB域SHA不同')
        raw=bytearray(rom.read_bytes());buf=(ct.c_uint8*len(raw)).from_buffer(raw);before=bytes(raw);overlap=ct.cast(ct.addressof(buf)+32,ct.POINTER(Model))
        if not desktop.jshc_mem_prepare(overlap,buf,len(raw)) or bytes(raw)!=before:raise AssertionError('prepare重叠未保留ROM')
        refusals+=1
        # 两格式分别破坏首个索引；17bit全1将超出实际107707个块。
        raw[1056:1060]=b'\xff'*4;buf=(ct.c_uint8*len(raw)).from_buffer(raw);bad=Model()
        if not desktop.jshc_mem_prepare(ct.byref(bad),buf,len(raw)) or any(bytes(bad)):raise AssertionError('坏索引未拒绝/清零')
        refusals+=1
        records.append(dict(entry_bits=mode,file_bytes=rom.stat().st_size,model_size=ct.sizeof(Model),resident=rom.stat().st_size+ct.sizeof(Model),rom_sha256=sha(rom),hashes=hashes))
    save(a.output/'results.json',dict(passed=True,purpose=__doc__,environment=env(),source_sha256=plan['source_sha256'],comparisons=comparisons,refusals=refusals,records=records,libraries={x.name:sha(x) for x in (a.build/'jshc_memory_rom.dll',a.build/'jshc_dict_c99.dll')},scope='两种索引宽度的独立C99及桌面scalar/AVX2完整256^3；有限原地/分离和偏移哨兵；额外保护页/通用拒绝另记。'))
    print(comparisons,refusals)
if __name__=='__main__':main()
