"""M16T八配置完整域、零pool/256palette/混合tag与图像及ROM双末端保护。"""
import argparse
import ctypes as ct
import hashlib
from pathlib import Path
import struct
import numpy as np
from study_memory_rom import ROOT,Model,U8,romlib,loadrom,sha,read,save,env
from bench_memory_rom import memory

MAPS=4194304
HEADER=1056
FLAG=0x80000000

def fixture(kind):
    """独立合成合法完整map；所有256个palette槽均可被引用。"""
    result=bytearray(HEADER+MAPS+(0 if kind=='constant_zero_pool' else 16))
    result[:4]=b'M16T';struct.pack_into('<7I',result,4,1,4,256,len(result)-HEADER,0,0,0)
    for i in range(256):struct.pack_into('<I',result,32+4*i,i|((255-i)<<8)|((i^85)<<16))
    words=np.frombuffer(result,dtype='<u4',count=1<<20,offset=HEADER)
    if kind=='constant_zero_pool':
        words[:]=FLAG;words[-3:]=[FLAG|0xffffff,FLAG|0xabcdef,FLAG]
    elif kind=='nonconstant_minimum_pool':words[:]=MAPS
    elif kind=='mixed':
        words[::2]=FLAG|0xabcdef;words[1::2]=MAPS
    else:raise ValueError(kind)
    if len(result)>HEADER+MAPS:result[-16:]=bytes((252,253,254,255))*4
    return bytes(result)

def independent(content,values):
    """按序列化字节独立解释；常量分支不构造或读取pool索引。"""
    output=bytearray()
    for red,green,blue in values.reshape(-1,3):
        code=int(red)|(int(green)<<8)|(int(blue)<<16)
        word=struct.unpack_from('<I',content,HEADER+4*(code>>4))[0]
        if word&FLAG:value=word&0xffffff
        else:value=struct.unpack_from('<I',content,32+4*content[HEADER+word+(code&15)])[0]
        output.extend((value&255,(value>>8)&255,(value>>16)&255))
    return bytes(output)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('build','roms','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);planpath=ROOT/'experiments/tagged-block16-native-v1.json';plan=read(planpath);before_memory=memory()
    if any(sha(ROOT/n)!=v for n,v in plan['source_sha256'].items()):raise AssertionError('冻结源变化')
    library=a.build/'jshc_memory_tag16.dll';pure=a.build/'jshc_tag16_c99.dll';d=romlib(library);c=romlib(pure)
    for lib in (d,c):
        lib.jshc_mem_model_size.restype=ct.c_size_t
        if lib.jshc_mem_model_size()!=ct.sizeof(Model):raise AssertionError('实际ABI非1056B')
    path=a.roms/'rom-4.bin';m,keep=loadrom(d,path);portable,pk=loadrom(c,path);raw=path.read_bytes();rng=np.random.default_rng(2026102443);finite=0;rejects=0;image_guards=0;rom_guards=0
    configs=[('c99',c,portable,0,1),('desktop_scalar',d,m,0,1),('avx2_1',d,m,1,1),('avx2_4',d,m,1,4)]
    def call(lib,model,source,target,n,kernel=1,threads=1):
        source=ct.cast(source,U8);target=ct.cast(target,U8)
        return lib.jshc_mem_apply(ct.byref(model),source,target,n) if lib is c else lib.jshc_mem_apply_parallel(ct.byref(model),source,target,n,kernel,threads)
    def expected(values):
        target=np.empty_like(values)
        if call(c,portable,values.ctypes.data,target.ctypes.data,len(values)//3):raise AssertionError('纯C99失败')
        return target
    for n in (0,1,7,8,9,15,16,17,31,32,33,73,1023,1024,1025,4095,4096,4097):
        values=rng.integers(0,256,3*n,dtype=np.uint8);gold=expected(values)
        for label,lib,model,k,t in configs:
            for same in (False,True):
                for offset in (0,1,3,7):
                    source=np.full(3*n+offset+17,0xa7,dtype=np.uint8);source[offset:offset+3*n]=values;target=source if same else np.full_like(source,0xa7)
                    if call(lib,model,source.ctypes.data+offset,target.ctypes.data+offset,n,k,t) or not np.array_equal(target[offset:offset+3*n],gold) or not np.all(target[:offset]==0xa7) or not np.all(target[offset+3*n:]==0xa7):raise AssertionError('有限/尾哨兵不同：'+label)
                    finite+=1
    for label,lib,model,k,t in configs:
        if call(lib,model,0,0,0,k,t):raise AssertionError('空指针零长度被拒绝')
        finite+=1
    hashes={}
    for label,lib,model,k,t in configs:
        for same in (False,True):
            digest=hashlib.sha256()
            for start in range(0,1<<24,1<<18):
                codes=np.arange(start,start+(1<<18),dtype=np.uint32);source=np.empty((len(codes),3),dtype=np.uint8);source[:,0]=codes>>16;source[:,1]=codes>>8;source[:,2]=codes;target=source if same else np.empty_like(source)
                if call(lib,model,source.ctypes.data,target.ctypes.data,len(source),k,t):raise AssertionError('完整域调用失败')
                digest.update(target)
            key=label+('_inplace' if same else '_outplace');hashes[key]=digest.hexdigest()
            if hashes[key]!='3c9ce8d98d8db454ce9337c50c2ecadb8ba59485d6bc3e6a42e3cc1dfe307c22':raise AssertionError('完整域SHA不同：'+key)
    def bad(data):
        nonlocal rejects
        buffer=(ct.c_uint8*len(data)).from_buffer(data);model=Model()
        for lib in (d,c):
            if not lib.jshc_mem_prepare(ct.byref(model),buffer,len(data)) or any(bytes(model)):raise AssertionError('非法ROM未拒绝并清零')
            rejects+=1
    for n in (0,1,31,1055,len(raw)-1):bad(bytearray(raw[:n]))
    for offset,value in ((4,2),(8,3),(8,5),(12,0),(12,257),(16,4),(20,1),(24,1),(28,1),(32,0xffffffff)):
        data=bytearray(raw);struct.pack_into('<I',data,offset,value);bad(data)
    data=bytearray(raw);data[:4]=b'M16D';bad(data)
    for word in (0,MAPS+1,len(raw)-HEADER-15,0x81000000,0xffabcdef):
        data=bytearray(raw);struct.pack_into('<I',data,HEADER,word);bad(data)
    data=bytearray(raw);data[-1]=255;bad(data)
    zero=fixture('constant_zero_pool');data=bytearray(zero);struct.pack_into('<I',data,HEADER,MAPS);bad(data)
    for offset in (1,3,7,31):
        storage=bytearray(offset)+raw;buffer=(ct.c_uint8*len(storage)).from_buffer(storage);model=Model()
        if d.jshc_mem_prepare(ct.byref(model),ct.addressof(buffer)+offset,len(raw)):raise AssertionError('非对齐ROM失败')
        values=rng.integers(0,256,3*4097,dtype=np.uint8);target=np.empty_like(values)
        if call(d,model,values.ctypes.data,target.ctypes.data,4097,1,4) or not np.array_equal(target,expected(values)):raise AssertionError('非对齐ROM输出不同')
        finite+=1
    data=bytearray(raw);buffer=(ct.c_uint8*len(data)).from_buffer(data);original=bytes(data);overlap=ct.cast(ct.addressof(buffer)+32,ct.POINTER(Model))
    for lib in (d,c):
        if not lib.jshc_mem_prepare(overlap,buffer,len(data)) or bytes(data)!=original:raise AssertionError('prepare重叠不是无写拒绝')
        rejects+=1
    storage=np.full(256,0x5a,dtype=np.uint8);addr=storage.ctypes.data;ptrmax=(1<<(8*ct.sizeof(ct.c_void_p)))-1
    for lib,model in ((d,m),(c,portable)):
        for source,target,n in ((0,addr,1),(addr,0,1),(addr,addr+1,16),(addr+1,addr,16),(addr,ct.addressof(model),1),(addr,ct.cast(model.blob,ct.c_void_p).value,1),(addr,addr,ptrmax//3+1),(ptrmax-1,addr,1)):
            original=bytes(storage)
            if not call(lib,model,source,target,n) or bytes(storage)!=original:raise AssertionError('非法IO未无写拒绝')
            rejects+=1
    k32=ct.WinDLL('kernel32',use_last_error=True);alloc=k32.VirtualAlloc;alloc.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32,ct.c_uint32];alloc.restype=ct.c_void_p;protect=k32.VirtualProtect;protect.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32,ct.POINTER(ct.c_uint32)];free=k32.VirtualFree;free.argtypes=[ct.c_void_p,ct.c_size_t,ct.c_uint32]
    for n in (1,7,8,9,31,32,40,64,72,73,405,406,1023,1024,1025,4096,65536,65537):
        span=((3*n+4095)//4096)*4096;address=alloc(None,span+4096,0x3000,4);output_address=alloc(None,span+4096,0x3000,4)
        if not address or not output_address:raise OSError(ct.get_last_error())
        try:
            old=ct.c_uint32()
            if not protect(address+span,4096,1,ct.byref(old)) or not protect(output_address+span,4096,1,ct.byref(old)):raise OSError(ct.get_last_error())
            source=address+span-3*n;target=output_address+span-3*n;values=rng.integers(0,256,3*n,dtype=np.uint8);gold=expected(values)
            for label,lib,model,k,t in configs:
                ct.memmove(source,values.ctypes.data,3*n);ct.memset(target,0xa7,3*n)
                if call(lib,model,source,target,n,k,t) or ct.string_at(target,3*n)!=bytes(gold):raise AssertionError('双图像保护页分离不同：'+label)
                if call(lib,model,source,source,n,k,t) or ct.string_at(source,3*n)!=bytes(gold):raise AssertionError('图像保护页原地不同：'+label)
                image_guards+=2
        finally:
            if not free(address,0,0x8000) or not free(output_address,0,0x8000):raise OSError(ct.get_last_error())
    forced=bytearray(raw);struct.pack_into('<I',forced,HEADER+MAPS-4,len(raw)-HEADER-16)
    fixtures=[('original',raw),('last_map_to_last_pool',bytes(forced)),('constant_zero_pool',zero),('nonconstant_minimum_pool',fixture('nonconstant_minimum_pool')),('mixed',fixture('mixed'))];fixture_records={}
    for label,content in fixtures:
        pages=(len(content)+4095)//4096;address=alloc(None,(pages+1)*4096,0x3000,4)
        if not address:raise OSError(ct.get_last_error())
        try:
            old=ct.c_uint32()
            if not protect(address+pages*4096,4096,1,ct.byref(old)):raise OSError(ct.get_last_error())
            start=address+pages*4096-len(content);ct.memmove(start,content,len(content));model=Model()
            if not protect(address,pages*4096,2,ct.byref(old)):raise OSError(ct.get_last_error())
            for lib in (d,c):
                if lib.jshc_mem_prepare(ct.byref(model),start,len(content)):raise AssertionError('ROM末端/正向夹具准备失败：'+label)
            # 包括最后map、倒数三个map、混合tag lane及palette最高四ID。
            codes=np.resize(np.array([0xffffff,0xffffef,0xffffdf,0xfffffc,0xfffffd,0xfffffe,0xffffff,0xffffe0],dtype=np.uint32),73);values=np.empty((73,3),dtype=np.uint8);values[:,0]=codes;values[:,1]=codes>>8;values[:,2]=codes>>16;values=values.reshape(-1);gold=independent(content,values)
            for backend,lib,unused,k,t in configs:
                for same in (False,True):
                    target=values.copy() if same else np.empty_like(values)
                    if call(lib,model,target.ctypes.data if same else values.ctypes.data,target.ctypes.data,73,k,t) or bytes(target)!=gold:raise AssertionError('ROM末端/独立期望不同：'+label+'/'+backend)
                    rom_guards+=1
            fixture_records[label]=dict(bytes=len(content),sha256=hashlib.sha256(content).hexdigest(),pool_bytes=len(content)-HEADER-MAPS,expected_sha256=hashlib.sha256(gold).hexdigest())
        finally:
            if not free(address,0,0x8000):raise OSError(ct.get_last_error())
    save(a.output/'results.json',dict(passed=True,purpose=__doc__,environment=env(),plan_sha256=sha(planpath),libraries={str(x):sha(x) for x in (library,pure)},rom_sha256=sha(path),rom_bytes=len(raw),model_size=ct.sizeof(Model),resident=len(raw)+ct.sizeof(Model),finite=finite,refusals=rejects,image_guards=image_guards,rom_guards=rom_guards,fixtures=fixture_records,hashes=hashes,quality_memory_before=before_memory,quality_memory_after=memory(),scope='Windows x64/GCC15.2；C99/scalar/AVX1/4各原地与分离8完整256^3。零pool全常量、256palette最高ID、全非恒定最小pool、混合lane、实际/强制最后pool均以独立序列化解释及ROM尾保护页验证。质量可与tail质量并行，无性能结论；峰值包括Python/NumPy/库/合成夹具，不是核心RAM；未执行WASM或实板。'))
    print(finite,rejects,image_guards,rom_guards)
if __name__=='__main__':main()
