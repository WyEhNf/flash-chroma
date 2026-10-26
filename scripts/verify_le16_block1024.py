"""M10L八配置完整域、65535合法块ID/256palette及map/pool末端保护。"""
import argparse
import ctypes as ct
import hashlib
from pathlib import Path
import struct
import numpy as np
from study_memory_rom import ROOT,Model,U8,romlib,loadrom,sha,read,save,env
from bench_memory_rom import memory

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('build','roms','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);plan=read(ROOT/'experiments/le16-block1024-v1.json');quality_memory_before=memory()
    if any(sha(ROOT/n)!=v for n,v in plan['source_sha256'].items()):raise AssertionError('冻结源变化')
    library=a.build/'jshc_memory_le16_1024.dll';pure=a.build/'jshc_le16_1024_c99.dll';d=romlib(library);c=romlib(pure)
    for dll in (d,c):
        dll.jshc_mem_model_size.restype=ct.c_size_t
        if dll.jshc_mem_model_size()!=ct.sizeof(Model):raise AssertionError('真实ABI非1056B')
    path=a.roms/'rom-10.bin';m,keep=loadrom(d,path);portable,pk=loadrom(c,path);raw=path.read_bytes();rng=np.random.default_rng(2026102442);finite=0;rejects=0;image_guards=0;rom_guards=0
    def apply(source,target,n,kernel=1,threads=1,model=m):return d.jshc_mem_apply_parallel(ct.byref(model),ct.cast(source,U8),ct.cast(target,U8),n,kernel,threads)
    def expected(src):
        target=np.empty_like(src)
        if c.jshc_mem_apply(ct.byref(portable),src.ctypes.data_as(U8),target.ctypes.data_as(U8),len(src)//3):raise AssertionError('纯C99失败')
        return target
    for n in (0,1,7,8,9,15,16,17,31,32,33,73,1023,1024,1025,4095,4096,4097):
        values=rng.integers(0,256,3*n,dtype=np.uint8);gold=expected(values)
        for kernel,threads in ((0,1),(1,1),(1,4)):
            for same in (False,True):
                for offset in (0,1,3,7):
                    source=np.full(3*n+offset+17,0xa7,dtype=np.uint8);source[offset:offset+3*n]=values;target=source if same else np.full_like(source,0xa7)
                    if apply(source.ctypes.data+offset,target.ctypes.data+offset,n,kernel,threads) or not np.array_equal(target[offset:offset+3*n],gold) or not np.all(target[:offset]==0xa7) or not np.all(target[offset+3*n:]==0xa7):raise AssertionError('有限/尾哨兵不同')
                    finite+=1
    if apply(0,0,0):raise AssertionError('空指针零长度被拒绝')
    finite+=1;hashes={}
    for label,lib,model,k,t in [('c99',c,portable,0,1),('desktop_scalar',d,m,0,1),('avx2_1',d,m,1,1),('avx2_4',d,m,1,4)]:
        for same in (False,True):
            digest=hashlib.sha256()
            for start in range(0,1<<24,1<<18):
                codes=np.arange(start,start+(1<<18),dtype=np.uint32);src=np.empty((len(codes),3),dtype=np.uint8);src[:,0]=codes>>16;src[:,1]=codes>>8;src[:,2]=codes;target=src if same else np.empty_like(src)
                rc=lib.jshc_mem_apply(ct.byref(model),src.ctypes.data_as(U8),target.ctypes.data_as(U8),len(src)) if label=='c99' else apply(src.ctypes.data,target.ctypes.data,len(src),k,t,model)
                if rc:raise AssertionError('完整域调用失败')
                digest.update(target)
            key=label+('_inplace' if same else '_outplace');hashes[key]=digest.hexdigest()
            if hashes[key]!='3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22':raise AssertionError('完整域SHA不同')
    def bad(data):
        nonlocal rejects
        buf=(ct.c_uint8*len(data)).from_buffer(data);model=Model()
        if not d.jshc_mem_prepare(ct.byref(model),buf,len(data)) or any(bytes(model)):raise AssertionError('非法ROM未拒绝并清零')
        rejects+=1
    for n in (0,1,31,1055,len(raw)-1):bad(bytearray(raw[:n]))
    for offset,value in ((4,2),(8,9),(8,11),(12,0),(12,257),(16,4),(20,1),(24,1),(28,1),(32,0xffffffff)):
        data=bytearray(raw);struct.pack_into('<I',data,offset,value);bad(data)
    data=bytearray(raw);data[:4]=b'M16D';bad(data)
    for offset,value in ((1056,65535),(1056+32766,10482)):
        data=bytearray(raw);struct.pack_into('<H',data,offset,value);bad(data)
    data=bytearray(raw);data[-1]=255;bad(data)
    for offset in (1,3,7,31):
        storage=bytearray(offset)+raw;buffer=(ct.c_uint8*len(storage)).from_buffer(storage);model=Model()
        if d.jshc_mem_prepare(ct.byref(model),ct.addressof(buffer)+offset,len(raw)):raise AssertionError('非对齐ROM失败')
        values=rng.integers(0,256,3*4097,dtype=np.uint8);target=np.empty_like(values)
        if apply(values.ctypes.data,target.ctypes.data,4097,1,4,model) or not np.array_equal(target,expected(values)):raise AssertionError('非对齐输出不同')
        finite+=1
    data=bytearray(raw);buffer=(ct.c_uint8*len(data)).from_buffer(data);before=bytes(data);overlap=ct.cast(ct.addressof(buffer)+32,ct.POINTER(Model))
    if not d.jshc_mem_prepare(overlap,buffer,len(data)) or bytes(data)!=before:raise AssertionError('prepare重叠不是无写拒绝')
    rejects+=1;storage=np.full(256,0x5a,dtype=np.uint8);addr=storage.ctypes.data;ptrmax=(1<<(8*ct.sizeof(ct.c_void_p)))-1
    for source,target,n in ((0,addr,1),(addr,0,1),(addr,addr+1,16),(addr+1,addr,16),(addr,ct.addressof(m),1),(addr,ct.cast(m.blob,ct.c_void_p).value,1),(addr,addr,ptrmax//3+1),(ptrmax-1,addr,1)):
        before=bytes(storage)
        if not apply(source,target,n) or bytes(storage)!=before:raise AssertionError('非法IO未无写拒绝')
        rejects+=1
    k32=ct.WinDLL('kernel32',use_last_error=True);alloc=k32.VirtualAlloc;alloc.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32,ct.c_uint32];alloc.restype=ct.c_void_p;protect=k32.VirtualProtect;protect.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32,ct.POINTER(ct.c_uint32)];free=k32.VirtualFree;free.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32]
    for n in (1,7,8,9,31,32,40,64,72,73,405,406,1023,1024,1025,4096,65536,65537):
        span=((3*n+4095)//4096)*4096;address=alloc(None,span+4096,0x3000,4);output_address=alloc(None,span+4096,0x3000,4)
        if not address or not output_address:raise OSError(ct.get_last_error())
        try:
            old=ct.c_uint32()
            if not protect(address+span,4096,1,ct.byref(old)):raise OSError(ct.get_last_error())
            if not protect(output_address+span,4096,1,ct.byref(old)):raise OSError(ct.get_last_error())
            source=address+span-3*n;target=output_address+span-3*n;values=rng.integers(0,256,3*n,dtype=np.uint8);gold=expected(values)
            for kernel,threads in ((0,1),(1,1),(1,4)):
                ct.memmove(source,values.ctypes.data,3*n);ct.memset(target,0xa7,3*n)
                if apply(source,target,n,kernel,threads) or ct.string_at(target,3*n)!=bytes(gold):raise AssertionError('图像输入/分离输出双保护页不同')
                if apply(source,source,n,kernel,threads) or ct.string_at(source,3*n)!=bytes(gold):raise AssertionError('图像保护页原地不同')
                image_guards+=2
        finally:
            if not free(address,0,0x8000):raise OSError(ct.get_last_error())
            if not free(output_address,0,0x8000):raise OSError(ct.get_last_error())
    forced=bytearray(raw);last_id=(len(raw)-1056-32768)//1024-1;struct.pack_into('<H',forced,1056+32766,last_id)
    expanded=bytearray(1056+32768+65536*1024);expanded[:4]=b'M10L';struct.pack_into('<7I',expanded,4,1,10,256,len(expanded)-1056,0,0,0)
    for i in range(256):struct.pack_into('<I',expanded,32+4*i,i|((255-i)<<8)|((i^85)<<16))
    struct.pack_into('<H',expanded,1056+32766,65535);expanded[-1024:]=bytes((252,253,254,255))*256
    for label,content in (('original',raw),('last_map_to_last_pool',bytes(forced)),('id65535_palette256',bytes(expanded))):
        pages=(len(content)+4095)//4096;address=alloc(None,(pages+1)*4096,0x3000,4)
        if not address:raise OSError(ct.get_last_error())
        try:
            old=ct.c_uint32()
            if not protect(address+pages*4096,4096,1,ct.byref(old)):raise OSError(ct.get_last_error())
            start=address+pages*4096-len(content);ct.memmove(start,content,len(content));model=Model()
            if d.jshc_mem_prepare(ct.byref(model),start,len(content)):raise AssertionError('ROM guard/65535合法准备失败')
            values=np.full(3*73,255,dtype=np.uint8)
            if label=='id65535_palette256':values.reshape(-1,3)[:,0]=np.tile(np.array([252,253,254,255],dtype=np.uint8),19)[:73]
            gold=np.empty_like(values)
            if c.jshc_mem_apply(ct.byref(model),values.ctypes.data_as(U8),gold.ctypes.data_as(U8),73):raise AssertionError('ROM guard C99失败')
            if label=='last_map_to_last_pool' and bytes(gold)!=content[32+4*content[-1]:35+4*content[-1]]*73:raise AssertionError('末pool独立金标准不同')
            if label=='id65535_palette256':
                independent=bytes(v for red in values.reshape(-1,3)[:,0] for v in (int(red),255-int(red),int(red)^85))
                if bytes(gold)!=independent:raise AssertionError('65535与252..255独立期望不同')
            for kernel,threads in ((0,1),(1,1),(1,4)):
                for same in (False,True):
                    target=values.copy() if same else np.empty_like(values)
                    if apply(target.ctypes.data if same else values.ctypes.data,target.ctypes.data,73,kernel,threads,model) or not np.array_equal(target,gold):raise AssertionError('ROM guard输出不同')
                    rom_guards+=1
        finally:
            if not free(address,0,0x8000):raise OSError(ct.get_last_error())
    save(a.output/'results.json',dict(passed=True,purpose=__doc__,environment=env(),plan_sha256=sha(ROOT/'experiments/le16-block1024-v1.json'),libraries={str(x):sha(x) for x in (library,pure)},rom_sha256=sha(path),rom_bytes=len(raw),model_size=ct.sizeof(Model),resident=len(raw)+ct.sizeof(Model),finite=finite,refusals=rejects,image_guards=image_guards,rom_guards=rom_guards,forced_last_id=last_id,positive_maximum_id=65535,positive_palette_count=256,positive_fixture_bytes=len(expanded),positive_fixture_sha256=hashlib.sha256(expanded).hexdigest(),hashes=hashes,quality_memory_before=quality_memory_before,quality_memory_after=memory(),scope='Windows x64/GCC15.2；四后端原地/分离共8完整256^3。ID65535的65536块与全部256合法palette，真实/强制末map末pool图像与ROM保护页通过；质量与tail并行非计时，峰值含Python/NumPy及67MiB正向夹具，不是核心RAM；无WASM/实板或速度结论。'))
    print(finite,rejects,image_guards,rom_guards)
if __name__=='__main__':main()
