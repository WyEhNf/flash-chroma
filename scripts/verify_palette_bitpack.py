"""实际7bit C99/AVX2完整域、双接口/线程、短尾/保护页及拒绝验收。"""
from __future__ import annotations
import argparse
import ctypes as ct
import hashlib
from pathlib import Path
import json
import os
import numpy as np
from profile_palette_bitpack import sha,save
from study_memory_rom import Model,U8,romlib,loadrom,env


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['library','roms','profile','original-rom','data-root','output']:
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    dlls=os.add_dll_directory('E:/mingw64/bin')
    library=romlib(args.library)
    original=np.frombuffer(args.original_rom.read_bytes(),np.uint8,offset=1056)
    assert sha(args.original_rom)=='146a5f283aaf5d895e4e375990166924b2fe9d6f6f092989f8023b8b8295acc5'
    rng=np.random.default_rng(2026102407)
    rows=[];finite=0;guard_cases=0;refused=0
    alloc=ct.windll.kernel32.VirtualAlloc;alloc.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32,ct.c_uint32];alloc.restype=ct.c_void_p
    protect=ct.windll.kernel32.VirtualProtect;protect.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32,ct.POINTER(ct.c_uint32)]
    free=ct.windll.kernel32.VirtualFree;free.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32]
    ptr=lambda address:ct.cast(address,U8)

    def guarded(size):
        span=(size+4095)//4096*4096
        base=alloc(None,span+4096,0x3000,4)
        if not base:raise ct.WinError()
        old=ct.c_uint32()
        if not protect(base+span,4096,1,ct.byref(old)):raise ct.WinError()
        return base,base+span-size

    for name in ['weighted_ward_centroid7','maximin_original_color7']:
        path=args.roms/(name+'.bin');model,keep=loadrom(library,path)
        fit=np.load(args.profile/(name+'.npz'));palette,mapping=fit['palette'],fit['mapping']

        def oracle(rgb):
            values=rgb.astype(np.uint32)
            code=values[:,0]|(values[:,1]<<8)|(values[:,2]<<16)
            return palette[mapping[original[code]]]

        configs=[(0,1,False),(0,1,True),(1,1,False),(1,1,True),(1,4,False),(1,4,True)]
        hashes=[hashlib.sha256() for _ in configs]
        for start in range(0,256**3,65536):
            code=np.arange(start,start+65536,dtype=np.uint32)
            rgb=np.column_stack((code>>16,(code>>8)&255,code&255)).astype(np.uint8)
            expected=oracle(rgb)
            for digest,(kernel,threads,inplace) in zip(hashes,configs):
                source=rgb.copy();target=source if inplace else np.empty_like(source)
                assert library.jshc_mem_apply_parallel(ct.byref(model),source.ctypes.data_as(U8),target.ctypes.data_as(U8),len(rgb),kernel,threads)==0
                np.testing.assert_array_equal(target,expected);digest.update(target.tobytes())
        assert len({digest.hexdigest() for digest in hashes})==1
        for n in [0,1,7,8,9,31,32,63,64,65,4095,4096,65535,65536,65537]:
            rgb=rng.integers(0,256,(n,3),np.uint8);expected=oracle(rgb)
            for offset in [0,1,7,15,31]:
                for kernel,threads,inplace in configs:
                    source=np.full(3*n+64,0xa5,np.uint8);source[offset:offset+3*n]=rgb.reshape(-1)
                    target=source if inplace else np.full(3*n+64,0x5a,np.uint8)
                    before=target.copy()
                    assert library.jshc_mem_apply_parallel(ct.byref(model),ptr(source.ctypes.data+offset),ptr(target.ctypes.data+offset),n,kernel,threads)==0
                    np.testing.assert_array_equal(target[offset:offset+3*n],expected.reshape(-1))
                    np.testing.assert_array_equal(target[:offset],before[:offset]);np.testing.assert_array_equal(target[offset+3*n:],before[offset+3*n:]);finite+=1
        for n in [1,7,8,9,31,32,63,64,65,4096,65536,65537]:
            rgb=rng.integers(0,256,(n,3),np.uint8);expected=oracle(rgb).tobytes()
            source_owner,source=guarded(3*n);target_owner,target=guarded(3*n)
            try:
                for kernel,threads,inplace in configs:
                    ct.memmove(source,rgb.ctypes.data,3*n)
                    destination=source if inplace else target
                    assert library.jshc_mem_apply_parallel(ct.byref(model),ptr(source),ptr(destination),n,kernel,threads)==0
                    assert ct.string_at(destination,3*n)==expected;guard_cases+=1
            finally:
                free(source_owner,0,0x8000);free(target_owner,0,0x8000)
        raw=path.read_bytes()
        for offset in [1,3,7,31]:
            unaligned=(ct.c_uint8*(len(raw)+offset))();ct.memmove(ct.addressof(unaligned)+offset,raw,len(raw));probe=Model()
            assert library.jshc_mem_prepare(ct.byref(probe),ct.addressof(unaligned)+offset,len(raw))==0
            rgb=rng.integers(0,256,(4097,3),np.uint8);target=np.empty_like(rgb)
            assert library.jshc_mem_apply_parallel(ct.byref(probe),rgb.ctypes.data_as(U8),target.ctypes.data_as(U8),len(rgb),1,4)==0
            np.testing.assert_array_equal(target,oracle(rgb));finite+=1
        # ROM末端紧邻不可访问页，4个guard byte属于真实文件，未借用调用者padding。
        owner,address=guarded(len(raw))
        try:
            ct.memmove(address,raw,len(raw));probe=Model()
            assert library.jshc_mem_prepare(ct.byref(probe),address,len(raw))==0
            rgb=np.array([[255,255,255],[254,255,255],[0,0,0]],np.uint8);target=np.empty_like(rgb)
            for kernel in [0,1]:
                assert library.jshc_mem_apply_parallel(ct.byref(probe),rgb.ctypes.data_as(U8),target.ctypes.data_as(U8),3,kernel,1)==0
                np.testing.assert_array_equal(target,oracle(rgb));guard_cases+=1
        finally:free(owner,0,0x8000)
        for offset in [0,4,8,12,16,20,24,28,32+3,len(raw)-1]:
            bad=bytearray(raw);bad[offset]^=255
            storage=(ct.c_uint8*len(bad)).from_buffer(bad);probe=Model()
            assert library.jshc_mem_prepare(ct.byref(probe),storage,len(bad))!=0 and not any(bytes(probe));refused+=1
        rgb=np.zeros((32,3),np.uint8);addr=rgb.ctypes.data;before=rgb.copy()
        for source,target,n,kernel,threads in [(0,addr,1,1,1),(addr,0,1,1,1),(addr,addr+1,16,1,1),
                (addr+1,addr,16,1,1),(addr,ct.addressof(model),1,1,1),(addr,ct.cast(model.blob,ct.c_void_p).value,1,1,1),
                (addr,addr,2**64//3+1,1,1),(2**64-2,addr,1,1,1),(addr,addr,1,2,1),(addr,addr,1,1,0),(addr,addr,1,1,257)]:
            assert library.jshc_mem_apply_parallel(ct.byref(model),ptr(source),ptr(target),n,kernel,threads)!=0
            np.testing.assert_array_equal(rgb,before);refused+=1
        photo=args.data_root/'artifacts/skylake-server-matrix-v1/server-inputs/photos.rgb'
        assert sha(photo)=='e13278cfc91c3411b3c242232239f9ea6fbda3bf5d18c3f17c41a4dedf57defd'
        images=np.memmap(photo,np.uint8,mode='r').reshape(100,786432,3)
        digest=hashlib.sha256();per_image=[]
        for image in images:
            expected=oracle(image);digest.update(expected.tobytes());per_image.append(hashlib.sha256(expected).hexdigest())
        rows.append(dict(name=name,file_sha256=sha(path),file_bytes=len(raw),resident_capacity=len(raw)+ct.sizeof(Model),
            full_rgb_colors=256**3,configs=[dict(kernel=k,threads=t,inplace=i,sha256=h.hexdigest()) for (k,t,i),h in zip(configs,hashes)],
            photo_oracle_sha256=digest.hexdigest(),photo_oracle_per_image_sha256=per_image,
            scope='native全域6配置精确匹配有损候选；照片此处为全域oracle索引SHA，实际native百图由后续性能首尾核验'))
    save(args.output/'results.json',dict(passed=True,purpose=__doc__,environment=env(),library_sha256=sha(args.library),script_sha256=sha(__file__),
        finite=finite,guard_cases=guard_cases,refusals=refused,models=rows,scope='新格式/映射接口；不是无损原a399输出或新性能结论'))
    print(f'两个7bit候选各6配置全域，{finite}有限/{guard_cases}保护页/{refused}拒绝通过')


if __name__=='__main__':main()
