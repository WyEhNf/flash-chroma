"""验证ROM借用/拒绝/非对齐与Windows保护页边界；不替代完整色域或性能。"""
import argparse
import ctypes as ct
from pathlib import Path
import struct
import numpy as np
from study_memory_rom import Model,U8,romlib,loadrom,save,sha,env

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--library',type=Path,required=True);p.add_argument('--roms',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False);d=romlib(a.library);rng=np.random.default_rng(2026102301);comparisons=0;rejects=0
    raw=bytearray((a.roms/'rom-6.bin').read_bytes())
    def bad(data):
        nonlocal rejects
        buf=(ct.c_uint8*len(data)).from_buffer(data);model=Model()
        if not d.jshc_mem_prepare(ct.byref(model),buf,len(data)):raise AssertionError('畸形未拒绝')
        if any(bytes(model)):raise AssertionError('失败未清零')
        rejects+=1
    for n in (0,1,31,1055,len(raw)-1):bad(bytearray(raw[:n]))
    for offset,value in ((4,2),(8,7),(12,0),(12,257),(16,4),(20,1),(32,0xffffffff),(1056,0),(1056,0xffffffff)):
        data=bytearray(raw);struct.pack_into('<I',data,offset,value);bad(data)
    data=bytearray(raw);data[-1]=255;bad(data)
    for offset in (1,3,7,31):
        storage=bytearray(offset)+raw;buf=(ct.c_uint8*len(storage)).from_buffer(storage);model=Model()
        if d.jshc_mem_prepare(ct.byref(model),ct.addressof(buf)+offset,len(raw)):raise AssertionError('非对齐ROM失败')
        src=rng.integers(0,256,3*4097,dtype=np.uint8);one=np.empty_like(src);two=np.empty_like(src)
        if d.jshc_mem_apply(ct.byref(model),src.ctypes.data_as(U8),one.ctypes.data_as(U8),4097) or d.jshc_mem_apply_parallel(ct.byref(model),src.ctypes.data_as(U8),two.ctypes.data_as(U8),4097,1,4) or not np.array_equal(one,two):raise AssertionError('非对齐ROM不同')
        comparisons+=1
    m,keep=loadrom(d,a.roms/'rom-6.bin');storage=np.full(256,0x5a,dtype=np.uint8);addr=storage.ctypes.data
    def ptr(address):return ct.cast(address,U8)
    for source,target,n in ((0,addr,1),(addr,0,1),(addr,addr+1,16),(addr+1,addr,16),(addr,ct.addressof(m),1),(addr,ct.cast(m.blob,ct.c_void_p).value,1),(addr,addr,(1<<64)//3+1),((1<<64)-2,addr,1)):
        before=bytes(storage)
        if not d.jshc_mem_apply_parallel(ct.byref(m),ptr(source),ptr(target),n,1,1) or bytes(storage)!=before:raise AssertionError('无效IO未无写拒绝')
        rejects+=1
    # 两页之外再设不可访问页，精确覆盖合法源末尾和原地末尾。
    alloc=ct.windll.kernel32.VirtualAlloc;alloc.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32,ct.c_uint32];alloc.restype=ct.c_void_p
    protect=ct.windll.kernel32.VirtualProtect;protect.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32,ct.POINTER(ct.c_uint32)]
    free=ct.windll.kernel32.VirtualFree;free.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32]
    for bits in (0,4,6,8,10):
        model,k=loadrom(d,a.roms/f'rom-{bits}.bin')
        for n in (1,7,8,9,31,32,40,64,72,73,405,406,4096,65536,65537):
            span=((3*n+4095)//4096)*4096;address=alloc(None,span+4096,0x3000,4)
            if not address:raise ct.WinError()
            old=ct.c_uint32();source=address+span-3*n
            if not protect(address+span,4096,1,ct.byref(old)):raise ct.WinError()
            try:
                values=rng.integers(0,256,3*n,dtype=np.uint8);ct.memmove(source,values.ctypes.data,3*n)
                expected=np.empty_like(values)
                if d.jshc_mem_apply(ct.byref(model),values.ctypes.data_as(U8),expected.ctypes.data_as(U8),n):raise AssertionError('C99拒绝')
                for threads in (1,4):
                    output=np.empty_like(values)
                    if d.jshc_mem_apply_parallel(ct.byref(model),ptr(source),output.ctypes.data_as(U8),n,1,threads) or not np.array_equal(output,expected):raise AssertionError('保护页输出不同')
                    ct.memmove(source,values.ctypes.data,3*n)
                    if d.jshc_mem_apply_parallel(ct.byref(model),ptr(source),ptr(source),n,1,threads) or ct.string_at(source,3*n)!=bytes(expected):raise AssertionError('保护页原地不同')
                    ct.memmove(source,values.ctypes.data,3*n);comparisons+=2
            finally:free(address,0,0x8000)
    save(a.output/'results.json',dict(pass_=True,purpose=__doc__,environment=env(),library_sha256=sha(a.library),script_sha256=sha(__file__),comparisons=comparisons,refusals=rejects,scope='Windows x64保护页、非对齐ROM、格式/范围拒绝与借用生命周期；不是跨架构执行。'))
    print(comparisons,rejects)
if __name__=='__main__':main()
